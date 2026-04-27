"""Phase 6 Part 02 PMWO/OPC candidate helpers.

The functions here extend the Phase 6 SMO MVP with study-grade pupil,
mask, and wavefront candidate families plus row-wise 2-D EPE maps. The
implementation remains deterministic grid search so the optimization loop stays
inspectable for education and design-space exploration.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np

from .illuminator import SourceShape
from .mask import MaskGrid, line_space_pattern
from .metrics import edge_positions
from .pupil import PupilSpec
from .smo import (
    MaskCandidate,
    SMOCandidateMetrics,
    SMOObjectiveWeights,
    evaluate_smo_candidate,
    weighted_smo_loss,
)


@dataclass(frozen=True)
class PupilWavefrontCandidate:
    """One pupil/wavefront candidate for PMWO sweeps."""

    name: str
    pupil_spec: PupilSpec

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("pupil candidate name must be a non-empty string")
        if not isinstance(self.pupil_spec, PupilSpec):
            raise TypeError("pupil_spec must be a PupilSpec")
        object.__setattr__(self, "name", self.name.strip())


@dataclass(frozen=True)
class EPEMap2D:
    """Row-wise edge-placement-error map in meters."""

    edge_error_m: np.ndarray
    mean_abs_epe_m: float
    max_abs_epe_m: float
    edge_count_mismatch_fraction: float
    rows_evaluated: int
    edges_per_row: int


@dataclass(frozen=True)
class PMWOCandidateEvaluation:
    """Evaluation for one pupil/mask/wavefront/source/dose candidate."""

    mask_candidate: MaskCandidate
    source_shape: SourceShape
    pupil_candidate: PupilWavefrontCandidate
    dose: float
    metrics: SMOCandidateMetrics
    epe_map: EPEMap2D
    aerial: np.ndarray
    printed: np.ndarray


@dataclass(frozen=True)
class PMWOResult:
    """PMWO grid-search result bundle."""

    initial: PMWOCandidateEvaluation
    best: PMWOCandidateEvaluation
    history: tuple[PMWOCandidateEvaluation, ...]
    weights: SMOObjectiveWeights
    improvement_fraction: float

    @property
    def converged(self) -> bool:
        """Return True when the best candidate is no worse than the initial one."""
        return self.best.metrics.loss <= self.initial.metrics.loss


def opc_bias_mask_candidates(
    mask_grid: MaskGrid,
    pitch_m: float,
    bias_values_m: Iterable[float],
    *,
    target_duty_cycle: float = 0.5,
    orientation: str = "vertical",
) -> tuple[MaskCandidate, ...]:
    """Build line-space OPC candidates by biasing absorber duty cycle."""
    _validate_positive_finite(pitch_m, "pitch_m")
    if not 0.0 < target_duty_cycle < 1.0:
        raise ValueError("target_duty_cycle must be in (0, 1)")
    biases = tuple(float(value) for value in bias_values_m)
    if not biases:
        raise ValueError("bias_values_m must contain at least one value")
    if any(not np.isfinite(value) for value in biases):
        raise ValueError("bias_values_m must contain finite values")

    candidates: list[MaskCandidate] = []
    for bias_m in biases:
        duty_cycle = target_duty_cycle + 2.0 * bias_m / pitch_m
        if not 0.0 < duty_cycle < 1.0:
            raise ValueError("OPC bias produces duty cycle outside (0, 1)")
        pattern = line_space_pattern(
            mask_grid,
            pitch_m=pitch_m,
            duty_cycle=duty_cycle,
            orientation=orientation,
        )
        candidates.append(
            MaskCandidate(
                name=f"opc_bias_{bias_m * 1e9:+.1f}nm",
                pattern=pattern,
            )
        )
    return tuple(candidates)


def wavefront_zernike_candidates(
    base_spec: PupilSpec,
    zernike_mode: tuple[int, int],
    amplitudes_waves: Iterable[float],
) -> tuple[PupilWavefrontCandidate, ...]:
    """Build candidates by sweeping one Zernike coefficient in waves."""
    if not isinstance(base_spec, PupilSpec):
        raise TypeError("base_spec must be a PupilSpec")
    n, m = int(zernike_mode[0]), int(zernike_mode[1])
    amplitudes = tuple(float(value) for value in amplitudes_waves)
    if not amplitudes:
        raise ValueError("amplitudes_waves must contain at least one value")
    if any(not np.isfinite(value) for value in amplitudes):
        raise ValueError("amplitudes_waves must contain finite values")

    candidates: list[PupilWavefrontCandidate] = []
    for amplitude in amplitudes:
        zernike = dict(base_spec.zernike)
        if amplitude == 0.0:
            zernike.pop((n, m), None)
            name = "wavefront_clear"
        else:
            zernike[(n, m)] = amplitude
            name = f"zernike_{n}_{m}_{amplitude:+.3f}waves"
        candidates.append(
            PupilWavefrontCandidate(
                name=name,
                pupil_spec=_copy_pupil_spec(base_spec, zernike=zernike),
            )
        )
    return tuple(candidates)


def pupil_obscuration_candidates(
    base_spec: PupilSpec,
    obscuration_ratios: Iterable[float],
) -> tuple[PupilWavefrontCandidate, ...]:
    """Build pupil candidates by sweeping central-obscuration ratio."""
    if not isinstance(base_spec, PupilSpec):
        raise TypeError("base_spec must be a PupilSpec")
    ratios = tuple(float(value) for value in obscuration_ratios)
    if not ratios:
        raise ValueError("obscuration_ratios must contain at least one value")
    candidates: list[PupilWavefrontCandidate] = []
    for ratio in ratios:
        if not np.isfinite(ratio) or not 0.0 <= ratio < 1.0:
            raise ValueError("obscuration ratios must be in [0, 1)")
        candidates.append(
            PupilWavefrontCandidate(
                name=f"obscuration_{ratio:.2f}",
                pupil_spec=_copy_pupil_spec(base_spec, obscuration_ratio=ratio),
            )
        )
    return tuple(candidates)


def edge_placement_error_map_2d(
    target_printed: np.ndarray,
    printed: np.ndarray,
    pixel_size_m: float,
    *,
    penalty_m: float | None = None,
) -> EPEMap2D:
    """Return a row-wise 2-D edge-placement-error map."""
    target = _as_bool_image(target_printed, "target_printed")
    candidate = _as_bool_image(printed, "printed")
    if target.shape != candidate.shape:
        raise ValueError("target_printed and printed must have the same shape")
    _validate_positive_finite(pixel_size_m, "pixel_size_m")
    if penalty_m is not None:
        _validate_positive_finite(penalty_m, "penalty_m")

    target_edges_by_row = tuple(
        edge_positions(target[row, :], pixel_size_m) for row in range(target.shape[0])
    )
    printed_edges_by_row = tuple(
        edge_positions(candidate[row, :], pixel_size_m)
        for row in range(candidate.shape[0])
    )
    max_edges = max((edges.size for edges in target_edges_by_row), default=0)
    if max_edges == 0:
        raise ValueError("target_printed must contain at least one edge")

    fallback_penalty = (
        float(penalty_m)
        if penalty_m is not None
        else float(max(pixel_size_m, target.shape[1] * pixel_size_m / 4.0))
    )
    edge_error = np.full((target.shape[0], max_edges), np.nan, dtype=np.float64)
    total_abs_error = 0.0
    counted_edges = 0
    mismatched_edges = 0
    max_abs_error = 0.0

    for row, (target_edges, printed_edges) in enumerate(
        zip(target_edges_by_row, printed_edges_by_row, strict=True)
    ):
        for edge_idx, target_edge in enumerate(target_edges):
            if edge_idx < printed_edges.size:
                signed_error = float(printed_edges[edge_idx] - target_edge)
            else:
                signed_error = fallback_penalty
                mismatched_edges += 1
            edge_error[row, edge_idx] = signed_error
            abs_error = abs(signed_error)
            total_abs_error += abs_error
            max_abs_error = max(max_abs_error, abs_error)
            counted_edges += 1
        if printed_edges.size > target_edges.size:
            extra_edges = int(printed_edges.size - target_edges.size)
            mismatched_edges += extra_edges
            total_abs_error += extra_edges * fallback_penalty
            max_abs_error = max(max_abs_error, fallback_penalty)
            counted_edges += extra_edges

    return EPEMap2D(
        edge_error_m=edge_error,
        mean_abs_epe_m=float(total_abs_error / max(counted_edges, 1)),
        max_abs_epe_m=float(max_abs_error),
        edge_count_mismatch_fraction=float(mismatched_edges / max(counted_edges, 1)),
        rows_evaluated=int(target.shape[0]),
        edges_per_row=int(max_edges),
    )


def evaluate_pmwo_candidate(
    target_printed: np.ndarray,
    mask_grid: MaskGrid,
    mask_candidate: MaskCandidate,
    source_shape: SourceShape,
    pupil_candidate: PupilWavefrontCandidate,
    *,
    dose: float = 1.0,
    weights: SMOObjectiveWeights | None = None,
    threshold: float = 0.3,
    anamorphic: bool = False,
) -> PMWOCandidateEvaluation:
    """Evaluate one PMWO candidate using 2-D EPE in the objective."""
    if weights is None:
        weights = SMOObjectiveWeights()
    base = evaluate_smo_candidate(
        target_printed,
        mask_grid,
        mask_candidate,
        source_shape,
        dose=dose,
        pupil_spec=pupil_candidate.pupil_spec,
        weights=weights,
        threshold=threshold,
        anamorphic=anamorphic,
    )
    epe_map = edge_placement_error_map_2d(
        target_printed,
        base.printed,
        base.wafer_grid.pixel_x_m,
        penalty_m=base.metrics.target_cd_m,
    )
    epe_error_fraction = epe_map.mean_abs_epe_m / base.metrics.target_cd_m
    loss = weighted_smo_loss(
        cd_error_fraction=base.metrics.cd_error_fraction,
        epe_error_fraction=epe_error_fraction,
        lwr_fraction=base.metrics.lwr_fraction,
        dose_error_fraction=base.metrics.dose_error_fraction,
        weights=weights,
    )
    metrics = SMOCandidateMetrics(
        target_cd_m=base.metrics.target_cd_m,
        printed_cd_m=base.metrics.printed_cd_m,
        mean_epe_m=epe_map.mean_abs_epe_m,
        lwr_m=base.metrics.lwr_m,
        cd_error_fraction=base.metrics.cd_error_fraction,
        epe_error_fraction=float(epe_error_fraction),
        lwr_fraction=base.metrics.lwr_fraction,
        dose_error_fraction=base.metrics.dose_error_fraction,
        loss=loss,
    )
    return PMWOCandidateEvaluation(
        mask_candidate=mask_candidate,
        source_shape=source_shape,
        pupil_candidate=pupil_candidate,
        dose=base.dose,
        metrics=metrics,
        epe_map=epe_map,
        aerial=base.aerial,
        printed=base.printed,
    )


def pmwo_grid_search(
    target_printed: np.ndarray,
    mask_grid: MaskGrid,
    mask_candidates: Iterable[MaskCandidate],
    source_shapes: Iterable[SourceShape],
    pupil_candidates: Iterable[PupilWavefrontCandidate],
    dose_grid: Iterable[float],
    *,
    weights: SMOObjectiveWeights | None = None,
    threshold: float = 0.3,
    anamorphic: bool = False,
) -> PMWOResult:
    """Run PMWO grid search over mask, source, pupil/wavefront, and dose."""
    masks = tuple(mask_candidates)
    sources = tuple(source_shapes)
    pupils = tuple(pupil_candidates)
    doses = tuple(float(value) for value in dose_grid)
    if not masks:
        raise ValueError("mask_candidates must contain at least one candidate")
    if not sources:
        raise ValueError("source_shapes must contain at least one source")
    if not pupils:
        raise ValueError("pupil_candidates must contain at least one candidate")
    if not doses:
        raise ValueError("dose_grid must contain at least one dose")
    if any(not np.isfinite(dose) or dose <= 0.0 for dose in doses):
        raise ValueError("dose_grid must contain positive finite values")
    if weights is None:
        weights = SMOObjectiveWeights()

    history = tuple(
        evaluate_pmwo_candidate(
            target_printed,
            mask_grid,
            mask_candidate,
            source_shape,
            pupil_candidate,
            dose=dose,
            weights=weights,
            threshold=threshold,
            anamorphic=anamorphic,
        )
        for mask_candidate in masks
        for source_shape in sources
        for pupil_candidate in pupils
        for dose in doses
    )
    initial = history[0]
    best = min(history, key=lambda item: item.metrics.loss)
    denominator = max(abs(initial.metrics.loss), float(np.finfo(np.float64).eps))
    improvement = (initial.metrics.loss - best.metrics.loss) / denominator
    return PMWOResult(
        initial=initial,
        best=best,
        history=history,
        weights=weights,
        improvement_fraction=float(improvement),
    )


def _copy_pupil_spec(
    base_spec: PupilSpec,
    *,
    obscuration_ratio: float | None = None,
    zernike: dict[tuple[int, int], float] | None = None,
) -> PupilSpec:
    return PupilSpec(
        grid_size=base_spec.grid_size,
        na=base_spec.na,
        obscuration_ratio=(
            base_spec.obscuration_ratio
            if obscuration_ratio is None
            else float(obscuration_ratio)
        ),
        wavelength=base_spec.wavelength,
        zernike=dict(base_spec.zernike) if zernike is None else zernike,
        defocus_m=base_spec.defocus_m,
        defocus_approximation=base_spec.defocus_approximation,
    )


def _as_bool_image(image: np.ndarray, name: str) -> np.ndarray:
    arr = np.asarray(image)
    if arr.ndim != 2:
        raise ValueError(f"{name} must be 2-D")
    if arr.size == 0:
        raise ValueError(f"{name} must contain at least one pixel")
    return arr.astype(bool)


def _validate_positive_finite(value: float, name: str) -> None:
    if not np.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be a positive finite value")
