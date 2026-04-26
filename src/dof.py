"""Depth-of-focus metrics for Phase 3 focus-stack analysis."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

import numpy as np

from . import constants as C
from .aerial import WaferGrid, aerial_image, contrast
from .mask import MaskGrid
from .pupil import PupilSpec


@dataclass(frozen=True)
class FocusSample:
    """Single focus-stack contrast sample."""

    defocus_m: float
    contrast: float
    normalized_contrast: float


@dataclass(frozen=True)
class DOFMetrics:
    """Nominal-focus DOF window derived from a focus stack."""

    samples: tuple[FocusSample, ...]
    reference_defocus_m: float
    reference_contrast: float
    threshold_fraction: float
    threshold_contrast: float
    lower_defocus_m: float | None
    upper_defocus_m: float | None
    dof_m: float | None


@dataclass(frozen=True)
class K2FitCase:
    """Single Rayleigh DOF fit case."""

    na: float
    dof_m: float
    k2: float
    pitch_m: float | None = None


@dataclass(frozen=True)
class K2FitResult:
    """Aggregate `DOF = k2 * lambda / NA^2` fit result."""

    cases: tuple[K2FitCase, ...]
    mean_k2: float
    std_k2: float
    target_k2: float
    relative_error: float
    tolerance_fraction: float
    passed: bool


def focus_stack_contrast(
    mask_field: np.ndarray,
    mask_grid: MaskGrid,
    defocus_values_m: Iterable[float],
    pupil_spec: PupilSpec | None = None,
    *,
    anamorphic: bool = True,
) -> tuple[FocusSample, ...]:
    """Evaluate center-line contrast over a constant-defocus stack."""
    if pupil_spec is None:
        pupil_spec = PupilSpec(grid_size=max(mask_grid.nx, mask_grid.ny))

    raw_samples: list[tuple[float, float]] = []
    for defocus_m in sorted(float(value) for value in defocus_values_m):
        spec = replace(pupil_spec, defocus_m=defocus_m)
        intensity, wafer = aerial_image(
            mask_field,
            mask_grid,
            pupil_spec=spec,
            anamorphic=anamorphic,
        )
        line = intensity[wafer.ny // 2, :]
        raw_samples.append((defocus_m, contrast(line)))

    if not raw_samples:
        raise ValueError("defocus_values_m must contain at least one value")

    reference_contrast = max(value for _, value in raw_samples)
    if reference_contrast <= 0.0:
        return tuple(FocusSample(dz, c, 0.0) for dz, c in raw_samples)
    return tuple(
        FocusSample(dz, c, c / reference_contrast) for dz, c in raw_samples
    )


def nominal_depth_of_focus(
    samples: Iterable[FocusSample],
    threshold_fraction: float = 0.8,
    reference_defocus_m: float = 0.0,
) -> DOFMetrics:
    """Estimate the contiguous DOF window around nominal best focus.

    The metric deliberately uses the sample nearest `reference_defocus_m`
    instead of a global maximum because coherent focus stacks can show remote
    contrast revivals. Phase 3 Part 02 tracks the nominal process window first.
    """
    ordered = tuple(sorted(samples, key=lambda sample: sample.defocus_m))
    if not ordered:
        raise ValueError("samples must contain at least one FocusSample")
    if not 0.0 < threshold_fraction <= 1.0:
        raise ValueError("threshold_fraction must be in (0, 1]")

    contrasts = np.array([sample.contrast for sample in ordered], dtype=np.float64)
    defocus = np.array([sample.defocus_m for sample in ordered], dtype=np.float64)
    ref_index = int(np.argmin(np.abs(defocus - reference_defocus_m)))
    reference_contrast = float(contrasts[ref_index])
    threshold_contrast = threshold_fraction * reference_contrast

    lower = _crossing_from_reference(defocus, contrasts, ref_index, threshold_contrast, -1)
    upper = _crossing_from_reference(defocus, contrasts, ref_index, threshold_contrast, 1)
    dof = None if lower is None or upper is None else upper - lower

    normalized = tuple(
        FocusSample(
            sample.defocus_m,
            sample.contrast,
            0.0 if reference_contrast <= 0.0 else sample.contrast / reference_contrast,
        )
        for sample in ordered
    )
    return DOFMetrics(
        samples=normalized,
        reference_defocus_m=float(defocus[ref_index]),
        reference_contrast=reference_contrast,
        threshold_fraction=threshold_fraction,
        threshold_contrast=threshold_contrast,
        lower_defocus_m=lower,
        upper_defocus_m=upper,
        dof_m=dof,
    )


def k2_from_dof(
    dof_m: float,
    na: float,
    wavelength: float = C.LAMBDA_EUV,
) -> float:
    """Invert the Rayleigh DOF expression into a fitted `k2` value."""
    if not np.isfinite(dof_m) or dof_m <= 0.0:
        raise ValueError("dof_m must be a positive finite value")
    if not np.isfinite(na) or na <= 0.0:
        raise ValueError("na must be a positive finite value")
    if not np.isfinite(wavelength) or wavelength <= 0.0:
        raise ValueError("wavelength must be a positive finite value")
    return float(dof_m * na * na / wavelength)


def fit_k2_from_dof_cases(
    dof_cases: Iterable[Iterable[float]],
    *,
    wavelength: float = C.LAMBDA_EUV,
    target_k2: float = C.K2_TYPICAL,
    tolerance_fraction: float = 0.30,
) -> K2FitResult:
    """Fit `k2` across an NA/pitch sweep of measured DOF values.

    Each input row must be `(na, dof_m)` or `(na, dof_m, pitch_m)`.
    `passed` is true when the mean fitted `k2` is within the requested
    relative tolerance of `target_k2`.
    """
    if not np.isfinite(target_k2) or target_k2 <= 0.0:
        raise ValueError("target_k2 must be a positive finite value")
    if not np.isfinite(tolerance_fraction) or tolerance_fraction < 0.0:
        raise ValueError("tolerance_fraction must be a non-negative finite value")

    cases: list[K2FitCase] = []
    for row in dof_cases:
        values = tuple(float(value) for value in row)
        if len(values) not in {2, 3}:
            raise ValueError("each DOF case must be (na, dof_m) or (na, dof_m, pitch_m)")

        na, dof_m = values[0], values[1]
        pitch_m = values[2] if len(values) == 3 else None
        if pitch_m is not None and (not np.isfinite(pitch_m) or pitch_m <= 0.0):
            raise ValueError("pitch_m must be positive and finite when provided")

        cases.append(
            K2FitCase(
                na=na,
                dof_m=dof_m,
                k2=k2_from_dof(dof_m, na, wavelength=wavelength),
                pitch_m=pitch_m,
            )
        )

    if not cases:
        raise ValueError("dof_cases must contain at least one case")

    k2_values = np.array([case.k2 for case in cases], dtype=np.float64)
    mean_k2 = float(np.mean(k2_values))
    relative_error = abs(mean_k2 - target_k2) / target_k2
    return K2FitResult(
        cases=tuple(cases),
        mean_k2=mean_k2,
        std_k2=float(np.std(k2_values)),
        target_k2=target_k2,
        relative_error=float(relative_error),
        tolerance_fraction=float(tolerance_fraction),
        passed=relative_error <= tolerance_fraction,
    )


def fit_k2_from_metrics(
    measurements: Iterable[tuple[float, DOFMetrics]],
    *,
    wavelength: float = C.LAMBDA_EUV,
    target_k2: float = C.K2_TYPICAL,
    tolerance_fraction: float = 0.30,
) -> K2FitResult:
    """Fit `k2` from already-computed nominal DOF metrics."""
    dof_cases: list[tuple[float, float]] = []
    for na, metrics in measurements:
        if metrics.dof_m is None:
            raise ValueError("all DOF metrics must have a closed dof_m window")
        dof_cases.append((na, metrics.dof_m))
    return fit_k2_from_dof_cases(
        dof_cases,
        wavelength=wavelength,
        target_k2=target_k2,
        tolerance_fraction=tolerance_fraction,
    )


def focus_drilling_average(
    mask_field: np.ndarray,
    mask_grid: MaskGrid,
    defocus_values_m: Iterable[float],
    pupil_spec: PupilSpec | None = None,
    *,
    weights: Iterable[float] | None = None,
    anamorphic: bool = True,
) -> tuple[np.ndarray, WaferGrid]:
    """Average aerial images across depth slices for micro focus-drilling."""
    if pupil_spec is None:
        pupil_spec = PupilSpec(grid_size=max(mask_grid.nx, mask_grid.ny))

    defocus_values = tuple(float(value) for value in defocus_values_m)
    if not defocus_values:
        raise ValueError("defocus_values_m must contain at least one value")
    if not all(np.isfinite(value) for value in defocus_values):
        raise ValueError("defocus_values_m must contain finite values")

    if weights is None:
        weights_array = np.full(
            len(defocus_values),
            1.0 / len(defocus_values),
            dtype=np.float64,
        )
    else:
        weights_array = np.array(tuple(float(value) for value in weights))
        if weights_array.size != len(defocus_values):
            raise ValueError("weights must match defocus_values_m length")
        if not np.all(np.isfinite(weights_array)):
            raise ValueError("weights must be finite")
        if np.any(weights_array < 0.0):
            raise ValueError("weights must be non-negative")
        total_weight = float(np.sum(weights_array))
        if total_weight <= 0.0:
            raise ValueError("weights must sum to a positive value")
        weights_array = weights_array / total_weight

    accumulated: np.ndarray | None = None
    wafer_grid: WaferGrid | None = None
    for defocus_m, weight in zip(defocus_values, weights_array, strict=True):
        intensity, wafer = aerial_image(
            mask_field,
            mask_grid,
            pupil_spec=replace(pupil_spec, defocus_m=defocus_m),
            anamorphic=anamorphic,
        )
        weighted = intensity * float(weight)
        accumulated = weighted if accumulated is None else accumulated + weighted
        if wafer_grid is None:
            wafer_grid = wafer

    if accumulated is None or wafer_grid is None:
        raise RuntimeError("focus drilling produced no aerial slices")
    return accumulated.astype(np.float64), wafer_grid


def _crossing_from_reference(
    defocus: np.ndarray,
    contrasts: np.ndarray,
    ref_index: int,
    threshold: float,
    direction: int,
) -> float | None:
    """Interpolate the first threshold crossing from the reference sample."""
    idx = ref_index
    if contrasts[idx] < threshold:
        return float(defocus[idx])

    while 0 <= idx + direction < contrasts.size:
        next_idx = idx + direction
        if contrasts[next_idx] < threshold:
            return _linear_crossing(
                defocus[idx],
                contrasts[idx],
                defocus[next_idx],
                contrasts[next_idx],
                threshold,
            )
        idx = next_idx
    return None


def _linear_crossing(
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    threshold: float,
) -> float:
    """Return x where the segment between two samples crosses threshold."""
    if y1 == y0:
        return float(x1)
    fraction = (threshold - y0) / (y1 - y0)
    return float(x0 + fraction * (x1 - x0))
