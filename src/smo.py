"""Phase 6 study-grade source-mask optimization MVP.

This module closes the simulator loop with a conservative grid-search SMO
baseline. It is not a production inverse lithography solver; it is a small,
deterministic optimizer that evaluates mask candidates, Phase 2 source shapes,
and dose values against a target printed pattern.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np

from . import constants as C
from .aerial import WaferGrid
from .illuminator import SourceShape, partial_coherent_aerial_image
from .mask import MaskGrid, kirchhoff_mask, line_space_pattern
from .metrics import critical_dimension, edge_positions
from .pupil import PupilSpec
from .resist_stochastic import StochasticResistParams, lwr_decomposition_budget
from .resist_threshold import threshold_resist


@dataclass(frozen=True)
class SMOObjectiveWeights:
    """Weights for the Phase 6 MVP objective."""

    cd: float = 1.0
    epe: float = 1.0
    lwr: float = 0.25
    dose: float = 0.0

    def __post_init__(self) -> None:
        for name, value in (
            ("cd", self.cd),
            ("epe", self.epe),
            ("lwr", self.lwr),
            ("dose", self.dose),
        ):
            if not np.isfinite(value) or value < 0.0:
                raise ValueError(f"{name} weight must be non-negative and finite")
        if self.cd + self.epe + self.lwr + self.dose <= 0.0:
            raise ValueError("at least one objective weight must be positive")


@dataclass(frozen=True)
class MaskCandidate:
    """One binary mask candidate for source-mask optimization."""

    name: str
    pattern: np.ndarray

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("mask candidate name must be a non-empty string")
        pattern = np.asarray(self.pattern, dtype=np.float64)
        if pattern.ndim != 2:
            raise ValueError("mask candidate pattern must be 2-D")
        if not np.all((pattern == 0.0) | (pattern == 1.0)):
            raise ValueError("mask candidate pattern must contain only 0 or 1")
        object.__setattr__(self, "name", self.name.strip())
        object.__setattr__(self, "pattern", pattern)


@dataclass(frozen=True)
class SMOCandidateMetrics:
    """Scalar metrics used by the Phase 6 MVP objective."""

    target_cd_m: float
    printed_cd_m: float
    mean_epe_m: float
    lwr_m: float
    cd_error_fraction: float
    epe_error_fraction: float
    lwr_fraction: float
    dose_error_fraction: float
    loss: float


@dataclass(frozen=True)
class SMOCandidateEvaluation:
    """Evaluation result for one mask/source/dose candidate."""

    mask_candidate: MaskCandidate
    source_shape: SourceShape
    dose: float
    metrics: SMOCandidateMetrics
    wafer_grid: WaferGrid
    aerial: np.ndarray
    printed: np.ndarray


@dataclass(frozen=True)
class SMOResult:
    """Grid-search SMO result bundle."""

    initial: SMOCandidateEvaluation
    best: SMOCandidateEvaluation
    history: tuple[SMOCandidateEvaluation, ...]
    weights: SMOObjectiveWeights
    improvement_fraction: float

    @property
    def converged(self) -> bool:
        """Return True when the best candidate is no worse than the initial one."""
        return self.best.metrics.loss <= self.initial.metrics.loss


def weighted_smo_loss(
    *,
    cd_error_fraction: float,
    epe_error_fraction: float,
    lwr_fraction: float,
    dose_error_fraction: float,
    weights: SMOObjectiveWeights | None = None,
) -> float:
    """Return the weighted Phase 6 MVP objective."""
    if weights is None:
        weights = SMOObjectiveWeights()
    values = (
        cd_error_fraction,
        epe_error_fraction,
        lwr_fraction,
        dose_error_fraction,
    )
    if any(not np.isfinite(value) or value < 0.0 for value in values):
        raise ValueError("objective components must be non-negative and finite")
    return float(
        weights.cd * cd_error_fraction
        + weights.epe * epe_error_fraction
        + weights.lwr * lwr_fraction
        + weights.dose * dose_error_fraction
    )


def line_space_mask_candidates(
    mask_grid: MaskGrid,
    pitch_m: float,
    duty_cycles: Iterable[float],
    *,
    orientation: str = "vertical",
) -> tuple[MaskCandidate, ...]:
    """Build binary line-space mask candidates over a duty-cycle grid."""
    duty_values = tuple(float(value) for value in duty_cycles)
    if not duty_values:
        raise ValueError("duty_cycles must contain at least one value")
    candidates = []
    for duty_cycle in duty_values:
        pattern = line_space_pattern(
            mask_grid,
            pitch_m=pitch_m,
            duty_cycle=duty_cycle,
            orientation=orientation,
        )
        candidates.append(
            MaskCandidate(
                name=f"line_space_duty_{duty_cycle:.3f}",
                pattern=pattern,
            )
        )
    return tuple(candidates)


def evaluate_smo_candidate(
    target_printed: np.ndarray,
    mask_grid: MaskGrid,
    mask_candidate: MaskCandidate,
    source_shape: SourceShape,
    *,
    dose: float = 1.0,
    pupil_spec: PupilSpec | None = None,
    weights: SMOObjectiveWeights | None = None,
    stochastic_params: StochasticResistParams | None = None,
    threshold: float = 0.3,
    anamorphic: bool = False,
    mag_x: float = C.ANAMORPHIC_MAG_X,
    mag_y: float = C.ANAMORPHIC_MAG_Y,
    line_index: int | None = None,
    edge_mismatch_penalty_m: float | None = None,
) -> SMOCandidateEvaluation:
    """Evaluate one mask/source/dose candidate against a target printed image."""
    target = _as_bool_image(target_printed, "target_printed")
    if target.shape != mask_grid.shape():
        raise ValueError("target_printed shape must match mask_grid")
    if mask_candidate.pattern.shape != mask_grid.shape():
        raise ValueError("mask candidate shape must match mask_grid")
    _validate_positive_finite(dose, "dose")
    _validate_positive_finite(threshold, "threshold")
    if threshold >= 1.0:
        raise ValueError("threshold must be less than one")

    if pupil_spec is None:
        pupil_spec = PupilSpec(grid_size=max(mask_grid.nx, mask_grid.ny))
    if weights is None:
        weights = SMOObjectiveWeights()
    if stochastic_params is None:
        stochastic_params = StochasticResistParams()

    partial = partial_coherent_aerial_image(
        kirchhoff_mask(mask_candidate.pattern),
        mask_grid,
        source_shape,
        pupil_spec=pupil_spec,
        anamorphic=anamorphic,
        mag_x=mag_x,
        mag_y=mag_y,
    )
    printed = threshold_resist(partial.intensity, dose=dose, threshold=threshold)

    cy = _line_index(line_index, partial.wafer_grid.ny)
    target_line = target[cy, :]
    printed_line = printed[cy, :]
    target_cd_m = critical_dimension(
        target_line,
        partial.wafer_grid.pixel_x_m,
    )
    if target_cd_m <= 0.0:
        raise ValueError("target center line must contain at least one interior run")
    printed_cd_m = critical_dimension(
        printed_line,
        partial.wafer_grid.pixel_x_m,
    )
    mean_epe_m = _mean_edge_error_with_penalty(
        edge_positions(target_line, partial.wafer_grid.pixel_x_m),
        edge_positions(printed_line, partial.wafer_grid.pixel_x_m),
        penalty_m=edge_mismatch_penalty_m or target_cd_m,
    )
    lwr_m = lwr_decomposition_budget(
        dose,
        cd_m=max(printed_cd_m, partial.wafer_grid.pixel_x_m),
        params=stochastic_params,
    ).total_lwr_m

    cd_error_fraction = abs(printed_cd_m - target_cd_m) / target_cd_m
    epe_error_fraction = mean_epe_m / target_cd_m
    lwr_fraction = lwr_m / target_cd_m
    dose_error_fraction = (dose - 1.0) ** 2
    loss = weighted_smo_loss(
        cd_error_fraction=cd_error_fraction,
        epe_error_fraction=epe_error_fraction,
        lwr_fraction=lwr_fraction,
        dose_error_fraction=dose_error_fraction,
        weights=weights,
    )

    return SMOCandidateEvaluation(
        mask_candidate=mask_candidate,
        source_shape=source_shape,
        dose=float(dose),
        metrics=SMOCandidateMetrics(
            target_cd_m=float(target_cd_m),
            printed_cd_m=float(printed_cd_m),
            mean_epe_m=float(mean_epe_m),
            lwr_m=float(lwr_m),
            cd_error_fraction=float(cd_error_fraction),
            epe_error_fraction=float(epe_error_fraction),
            lwr_fraction=float(lwr_fraction),
            dose_error_fraction=float(dose_error_fraction),
            loss=loss,
        ),
        wafer_grid=partial.wafer_grid,
        aerial=partial.intensity,
        printed=printed,
    )


def fast_smo_grid_search(
    target_printed: np.ndarray,
    mask_grid: MaskGrid,
    mask_candidates: Iterable[MaskCandidate],
    source_shapes: Iterable[SourceShape],
    dose_grid: Iterable[float],
    *,
    pupil_spec: PupilSpec | None = None,
    weights: SMOObjectiveWeights | None = None,
    stochastic_params: StochasticResistParams | None = None,
    threshold: float = 0.3,
    anamorphic: bool = False,
    line_index: int | None = None,
) -> SMOResult:
    """Run deterministic grid-search SMO over mask, source, and dose choices."""
    masks = tuple(mask_candidates)
    sources = tuple(source_shapes)
    doses = tuple(float(value) for value in dose_grid)
    if not masks:
        raise ValueError("mask_candidates must contain at least one candidate")
    if not sources:
        raise ValueError("source_shapes must contain at least one source")
    if not doses:
        raise ValueError("dose_grid must contain at least one dose")
    if any(not np.isfinite(dose) or dose <= 0.0 for dose in doses):
        raise ValueError("dose_grid must contain positive finite values")
    if weights is None:
        weights = SMOObjectiveWeights()

    history = tuple(
        evaluate_smo_candidate(
            target_printed,
            mask_grid,
            mask_candidate,
            source_shape,
            dose=dose,
            pupil_spec=pupil_spec,
            weights=weights,
            stochastic_params=stochastic_params,
            threshold=threshold,
            anamorphic=anamorphic,
            line_index=line_index,
        )
        for mask_candidate in masks
        for source_shape in sources
        for dose in doses
    )
    initial = history[0]
    best = min(history, key=lambda item: item.metrics.loss)
    denominator = max(abs(initial.metrics.loss), float(np.finfo(np.float64).eps))
    improvement = (initial.metrics.loss - best.metrics.loss) / denominator

    return SMOResult(
        initial=initial,
        best=best,
        history=history,
        weights=weights,
        improvement_fraction=float(improvement),
    )


def _mean_edge_error_with_penalty(
    target_edges_m: np.ndarray,
    printed_edges_m: np.ndarray,
    *,
    penalty_m: float,
) -> float:
    _validate_positive_finite(penalty_m, "penalty_m")
    target = np.asarray(target_edges_m, dtype=np.float64)
    printed = np.asarray(printed_edges_m, dtype=np.float64)
    if target.size == 0:
        raise ValueError("target line must contain at least one edge")
    if printed.size == 0:
        return float(penalty_m)

    matched = min(target.size, printed.size)
    edge_error_sum = float(np.sum(np.abs(printed[:matched] - target[:matched])))
    unmatched = abs(target.size - printed.size)
    return float((edge_error_sum + unmatched * penalty_m) / max(target.size, 1))


def _as_bool_image(image: np.ndarray, name: str) -> np.ndarray:
    arr = np.asarray(image)
    if arr.ndim != 2:
        raise ValueError(f"{name} must be 2-D")
    if arr.size == 0:
        raise ValueError(f"{name} must contain at least one pixel")
    return arr.astype(bool)


def _line_index(line_index: int | None, ny: int) -> int:
    if line_index is None:
        return ny // 2
    index = int(line_index)
    if not 0 <= index < ny:
        raise ValueError("line_index must be inside the image height")
    return index


def _validate_positive_finite(value: float, name: str) -> None:
    if not np.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be a positive finite value")
