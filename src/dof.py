"""Depth-of-focus metrics for Phase 3 focus-stack analysis."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

import numpy as np

from .aerial import aerial_image, contrast
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
