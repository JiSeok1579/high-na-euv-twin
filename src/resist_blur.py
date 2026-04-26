"""Gaussian chemical blur approximation for Phase 5 Level 1."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np

from .metrics import critical_dimension, edge_positions, mean_absolute_epe
from .resist_threshold import threshold_resist


@dataclass(frozen=True)
class BlurDoseSweepPoint:
    """One deterministic point in a Gaussian-blur/dose sweep."""

    sigma_m: float
    dose: float
    cd_m: float
    mean_abs_epe_m: float | None
    transition_width_m: float
    lwr_proxy_m: float


@dataclass(frozen=True)
class CalibratedLWRPoint:
    """One measured-vs-calibrated LWR proxy point."""

    sigma_m: float
    dose: float
    lwr_proxy_m: float
    measured_lwr_m: float
    calibrated_lwr_m: float
    residual_m: float


@dataclass(frozen=True)
class BlurLWRCalibration:
    """Scale calibration from Level 1 LWR proxy to measured LWR."""

    scale: float
    rms_error_m: float
    max_abs_error_m: float
    points: tuple[CalibratedLWRPoint, ...]


def gaussian_kernel_1d(
    sigma_m: float,
    pixel_size_m: float,
    *,
    truncate: float = 3.0,
) -> np.ndarray:
    """Return a normalized 1-D Gaussian kernel sampled in pixel units."""
    _validate_blur_inputs(sigma_m, pixel_size_m, truncate)
    if sigma_m == 0.0:
        return np.array([1.0], dtype=np.float64)

    sigma_px = sigma_m / pixel_size_m
    radius = max(1, int(math.ceil(truncate * sigma_px)))
    coords = np.arange(-radius, radius + 1, dtype=np.float64)
    kernel = np.exp(-0.5 * (coords / sigma_px) ** 2)
    kernel_sum = float(np.sum(kernel))
    if kernel_sum <= 0.0:
        raise ValueError("Gaussian kernel sum must be positive")
    return (kernel / kernel_sum).astype(np.float64)


def gaussian_blur(
    aerial: np.ndarray,
    pixel_size_m: float,
    sigma_m: float,
    *,
    truncate: float = 3.0,
) -> np.ndarray:
    """Apply separable Gaussian blur to a 1-D or 2-D aerial intensity array."""
    image = np.asarray(aerial, dtype=np.float64)
    if image.ndim not in {1, 2}:
        raise ValueError("aerial must be a 1-D line or 2-D image")
    if image.size == 0:
        raise ValueError("aerial must contain at least one pixel")
    if not np.all(np.isfinite(image)):
        raise ValueError("aerial must contain finite values")
    if np.any(image < 0.0):
        raise ValueError("aerial intensity must be non-negative")

    kernel = gaussian_kernel_1d(sigma_m, pixel_size_m, truncate=truncate)
    if kernel.size == 1:
        return image.copy()

    blurred = _convolve_along_axis(image, kernel, axis=0)
    if image.ndim == 2:
        blurred = _convolve_along_axis(blurred, kernel, axis=1)
    return blurred.astype(np.float64)


def blurred_threshold_resist(
    aerial: np.ndarray,
    pixel_size_m: float,
    sigma_m: float,
    *,
    dose: float = 1.0,
    threshold: float = 0.3,
    truncate: float = 3.0,
) -> np.ndarray:
    """Blur aerial intensity before applying the Phase 5 threshold resist."""
    blurred = gaussian_blur(
        aerial,
        pixel_size_m,
        sigma_m,
        truncate=truncate,
    )
    return threshold_resist(blurred, dose=dose, threshold=threshold)


def blur_dose_sweep(
    aerial_line: np.ndarray,
    target_line: np.ndarray,
    pixel_size_m: float,
    sigma_values_m: Iterable[float],
    doses: Iterable[float],
    *,
    threshold: float = 0.3,
    truncate: float = 3.0,
) -> tuple[BlurDoseSweepPoint, ...]:
    """Evaluate CD/EPE and a deterministic LWR proxy over sigma and dose.

    `lwr_proxy_m` is `transition_width_m / sqrt(dose)`. It is not stochastic
    LWR; it is a Level 1 monotonic proxy used before Monte Carlo is introduced.
    """
    line = _as_aerial_line(aerial_line)
    target = _as_target_line(target_line, expected_size=line.size)
    _validate_pixel_size(pixel_size_m)

    sigmas = tuple(float(sigma) for sigma in sigma_values_m)
    dose_values = tuple(float(dose) for dose in doses)
    if not sigmas:
        raise ValueError("sigma_values_m must contain at least one value")
    if not dose_values:
        raise ValueError("doses must contain at least one value")
    if any(not np.isfinite(dose) or dose <= 0.0 for dose in dose_values):
        raise ValueError("doses must contain positive finite values")

    target_edges = edge_positions(target, pixel_size_m)
    points: list[BlurDoseSweepPoint] = []
    for sigma_m in sigmas:
        blurred = gaussian_blur(
            line,
            pixel_size_m,
            sigma_m,
            truncate=truncate,
        )
        width_m = transition_width(blurred, pixel_size_m)
        for dose in dose_values:
            printed = threshold_resist(blurred, dose=dose, threshold=threshold)
            printed_edges = edge_positions(printed, pixel_size_m)
            points.append(
                BlurDoseSweepPoint(
                    sigma_m=sigma_m,
                    dose=dose,
                    cd_m=critical_dimension(printed, pixel_size_m),
                    mean_abs_epe_m=_mean_epe_or_none(target_edges, printed_edges),
                    transition_width_m=width_m,
                    lwr_proxy_m=width_m / math.sqrt(dose),
                )
            )
    return tuple(points)


def calibrate_blur_lwr_proxy(
    sweep_points: Iterable[BlurDoseSweepPoint],
    measured_lwr_m: Iterable[float],
) -> BlurLWRCalibration:
    """Fit a scalar calibration from deterministic LWR proxy to measured LWR."""
    points = tuple(sweep_points)
    measured = np.array(tuple(float(value) for value in measured_lwr_m), dtype=np.float64)
    if not points:
        raise ValueError("sweep_points must contain at least one point")
    if measured.size != len(points):
        raise ValueError("measured_lwr_m must match sweep_points length")
    if not np.all(np.isfinite(measured)) or np.any(measured < 0.0):
        raise ValueError("measured_lwr_m must contain non-negative finite values")

    proxy = np.array([point.lwr_proxy_m for point in points], dtype=np.float64)
    if not np.all(np.isfinite(proxy)) or np.any(proxy < 0.0):
        raise ValueError("sweep point LWR proxies must be non-negative finite values")
    denominator = float(np.dot(proxy, proxy))
    if denominator <= 0.0:
        raise ValueError("at least one sweep point must have positive LWR proxy")

    scale = float(np.dot(proxy, measured) / denominator)
    calibrated = scale * proxy
    residuals = calibrated - measured
    calibrated_points = tuple(
        CalibratedLWRPoint(
            sigma_m=point.sigma_m,
            dose=point.dose,
            lwr_proxy_m=point.lwr_proxy_m,
            measured_lwr_m=float(target),
            calibrated_lwr_m=float(predicted),
            residual_m=float(residual),
        )
        for point, target, predicted, residual in zip(
            points,
            measured,
            calibrated,
            residuals,
            strict=True,
        )
    )

    return BlurLWRCalibration(
        scale=scale,
        rms_error_m=float(np.sqrt(np.mean(residuals**2))),
        max_abs_error_m=float(np.max(np.abs(residuals))),
        points=calibrated_points,
    )


def transition_width(
    intensity_line: np.ndarray,
    pixel_size_m: float,
    *,
    low: float = 0.1,
    high: float = 0.9,
) -> float:
    """Estimate edge-spread width between low and high normalized intensities."""
    line = np.asarray(intensity_line, dtype=np.float64)
    if line.ndim != 1:
        raise ValueError("intensity_line must be 1-D")
    if line.size == 0:
        raise ValueError("intensity_line must contain at least one pixel")
    if not np.all(np.isfinite(line)):
        raise ValueError("intensity_line must contain finite values")
    if not 0.0 <= low < high <= 1.0:
        raise ValueError("low and high must satisfy 0 <= low < high <= 1")
    if not np.isfinite(pixel_size_m) or pixel_size_m <= 0.0:
        raise ValueError("pixel_size_m must be a positive finite value")

    normalized = line.copy()
    line_min = float(np.min(normalized))
    line_max = float(np.max(normalized))
    span = line_max - line_min
    if span <= 0.0:
        return 0.0
    normalized = (normalized - line_min) / span
    transition = (normalized > low) & (normalized < high)
    return float(np.count_nonzero(transition) * pixel_size_m)


def _as_aerial_line(aerial_line: np.ndarray) -> np.ndarray:
    line = np.asarray(aerial_line, dtype=np.float64)
    if line.ndim != 1:
        raise ValueError("aerial_line must be 1-D")
    if line.size == 0:
        raise ValueError("aerial_line must contain at least one pixel")
    if not np.all(np.isfinite(line)):
        raise ValueError("aerial_line must contain finite values")
    if np.any(line < 0.0):
        raise ValueError("aerial_line intensity must be non-negative")
    return line


def _as_target_line(target_line: np.ndarray, *, expected_size: int) -> np.ndarray:
    target = np.asarray(target_line, dtype=bool)
    if target.ndim != 1:
        raise ValueError("target_line must be 1-D")
    if target.size != expected_size:
        raise ValueError("target_line must match aerial_line size")
    return target


def _mean_epe_or_none(
    target_edges_m: np.ndarray,
    printed_edges_m: np.ndarray,
) -> float | None:
    if target_edges_m.size == 0 or target_edges_m.shape != printed_edges_m.shape:
        return None
    return mean_absolute_epe(target_edges_m, printed_edges_m)


def _convolve_along_axis(
    image: np.ndarray,
    kernel: np.ndarray,
    axis: int,
) -> np.ndarray:
    radius = kernel.size // 2
    pad_width = [(0, 0)] * image.ndim
    pad_width[axis] = (radius, radius)
    padded = np.pad(image, pad_width, mode="edge")
    return np.apply_along_axis(
        lambda line: np.convolve(line, kernel, mode="valid"),
        axis,
        padded,
    )


def _validate_blur_inputs(
    sigma_m: float,
    pixel_size_m: float,
    truncate: float,
) -> None:
    if not np.isfinite(sigma_m) or sigma_m < 0.0:
        raise ValueError("sigma_m must be a non-negative finite value")
    if not np.isfinite(pixel_size_m) or pixel_size_m <= 0.0:
        raise ValueError("pixel_size_m must be a positive finite value")
    if not np.isfinite(truncate) or truncate <= 0.0:
        raise ValueError("truncate must be a positive finite value")


def _validate_pixel_size(pixel_size_m: float) -> None:
    if not np.isfinite(pixel_size_m) or pixel_size_m <= 0.0:
        raise ValueError("pixel_size_m must be a positive finite value")
