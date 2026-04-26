"""MVP lithography metrics shared by Phase 1 and Phase 5 tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .aerial import contrast as _contrast
from .aerial import nils as _nils
from .resist_threshold import threshold_resist


@dataclass(frozen=True)
class LineRun:
    """Contiguous foreground segment on a 1-D printed line."""

    start_m: float
    stop_m: float
    width_m: float


@dataclass(frozen=True)
class DoseCDPoint:
    """One point on a CD-dose curve."""

    dose: float
    cd_m: float


def binary_line_runs(
    binary_line: np.ndarray,
    pixel_size_m: float,
    *,
    foreground: bool = True,
    include_boundary: bool = False,
) -> tuple[LineRun, ...]:
    """Return contiguous foreground runs from a 1-D binary printed line."""
    line = _as_bool_line(binary_line)
    _validate_pixel_size(pixel_size_m)

    starts = np.concatenate(
        (
            np.array([0], dtype=np.int64),
            np.flatnonzero(line[1:] != line[:-1]).astype(np.int64) + 1,
        )
    )
    stops = np.concatenate((starts[1:], np.array([line.size], dtype=np.int64)))

    runs: list[LineRun] = []
    for start, stop in zip(starts, stops, strict=True):
        if bool(line[start]) != foreground:
            continue
        if not include_boundary and (start == 0 or stop == line.size):
            continue
        runs.append(
            LineRun(
                start_m=float(start * pixel_size_m),
                stop_m=float(stop * pixel_size_m),
                width_m=float((stop - start) * pixel_size_m),
            )
        )
    return tuple(runs)


def critical_dimension(
    binary_line: np.ndarray,
    pixel_size_m: float,
    *,
    foreground: bool = True,
    include_boundary: bool = False,
) -> float:
    """Return mean foreground run width as the printed CD."""
    runs = binary_line_runs(
        binary_line,
        pixel_size_m,
        foreground=foreground,
        include_boundary=include_boundary,
    )
    if not runs:
        return 0.0
    return float(np.mean([run.width_m for run in runs]))


def edge_positions(binary_line: np.ndarray, pixel_size_m: float) -> np.ndarray:
    """Return transition edge positions for a 1-D binary printed line."""
    line = _as_bool_line(binary_line)
    _validate_pixel_size(pixel_size_m)
    transition_indices = np.flatnonzero(line[1:] != line[:-1]) + 1
    return transition_indices.astype(np.float64) * pixel_size_m


def edge_placement_errors(
    target_edges_m: Iterable[float],
    printed_edges_m: Iterable[float],
) -> np.ndarray:
    """Return signed printed-minus-target edge placement errors."""
    target = _as_finite_vector(target_edges_m, "target_edges_m")
    printed = _as_finite_vector(printed_edges_m, "printed_edges_m")
    if target.size == 0:
        raise ValueError("edge vectors must contain at least one edge")
    if target.shape != printed.shape:
        raise ValueError("target_edges_m and printed_edges_m must have the same shape")
    return printed - target


def mean_absolute_epe(
    target_edges_m: Iterable[float],
    printed_edges_m: Iterable[float],
) -> float:
    """Return mean absolute edge placement error."""
    return float(np.mean(np.abs(edge_placement_errors(target_edges_m, printed_edges_m))))


def dose_cd_curve(
    aerial_line: np.ndarray,
    pixel_size_m: float,
    doses: Iterable[float],
    *,
    threshold: float = 0.3,
    foreground: bool = True,
) -> tuple[DoseCDPoint, ...]:
    """Evaluate printed CD over a dose sweep."""
    dose_values = tuple(float(dose) for dose in doses)
    if not dose_values:
        raise ValueError("doses must contain at least one value")

    points: list[DoseCDPoint] = []
    for dose in dose_values:
        printed_line = threshold_resist(aerial_line, dose=dose, threshold=threshold)
        points.append(
            DoseCDPoint(
                dose=dose,
                cd_m=critical_dimension(
                    printed_line,
                    pixel_size_m,
                    foreground=foreground,
                ),
            )
        )
    return tuple(points)


def michelson_contrast(intensity: np.ndarray) -> float:
    """Return Michelson contrast for an intensity profile or image."""
    return _contrast(np.asarray(intensity, dtype=np.float64))


def normalized_image_log_slope(
    intensity_line: np.ndarray,
    pixel_size_m: float,
    cd_target_m: float,
    threshold: float = 0.3,
) -> float:
    """Return NILS at the threshold crossing nearest the pattern edge."""
    return _nils(
        np.asarray(intensity_line, dtype=np.float64),
        pixel_size_m,
        cd_target_m,
        threshold=threshold,
    )


def _as_bool_line(binary_line: np.ndarray) -> np.ndarray:
    line = np.asarray(binary_line, dtype=bool)
    if line.ndim != 1:
        raise ValueError("binary_line must be 1-D")
    if line.size == 0:
        raise ValueError("binary_line must contain at least one pixel")
    return line


def _as_finite_vector(values: Iterable[float], name: str) -> np.ndarray:
    vector = np.array(tuple(float(value) for value in values), dtype=np.float64)
    if vector.ndim != 1:
        raise ValueError(f"{name} must be a 1-D iterable")
    if not np.all(np.isfinite(vector)):
        raise ValueError(f"{name} must contain finite values")
    return vector


def _validate_pixel_size(pixel_size_m: float) -> None:
    if not np.isfinite(pixel_size_m) or pixel_size_m <= 0.0:
        raise ValueError("pixel_size_m must be a positive finite value")
