"""Phase 5 Level 1 tests for Gaussian resist blur."""

from __future__ import annotations

import numpy as np
import pytest

from src.resist_blur import (
    blurred_threshold_resist,
    blur_dose_sweep,
    gaussian_blur,
    gaussian_kernel_1d,
    transition_width,
)
from src.resist_threshold import threshold_resist


def test_gaussian_kernel_is_normalized_and_symmetric():
    """The sampled chemical blur kernel must preserve total dose."""
    kernel = gaussian_kernel_1d(sigma_m=2e-9, pixel_size_m=1e-9)

    assert kernel.size % 2 == 1
    assert np.sum(kernel) == pytest.approx(1.0)
    assert np.allclose(kernel, kernel[::-1])
    assert kernel[kernel.size // 2] == pytest.approx(float(np.max(kernel)))


def test_gaussian_blur_preserves_constant_intensity():
    """A constant aerial dose should remain constant after blur."""
    aerial = np.full((9, 11), 0.42)
    blurred = gaussian_blur(aerial, pixel_size_m=1e-9, sigma_m=3e-9)

    assert blurred.shape == aerial.shape
    assert np.allclose(blurred, aerial)


def test_gaussian_blur_broadens_edge_transition_with_sigma():
    """Larger sigma should widen the deterministic edge-spread band."""
    aerial_line = np.zeros(201, dtype=np.float64)
    aerial_line[101:] = 1.0

    narrow = gaussian_blur(aerial_line, pixel_size_m=1e-9, sigma_m=2e-9)
    wide = gaussian_blur(aerial_line, pixel_size_m=1e-9, sigma_m=4e-9)

    assert transition_width(narrow, 1e-9) > 0.0
    assert transition_width(wide, 1e-9) > transition_width(narrow, 1e-9)


def test_zero_sigma_blurred_threshold_matches_threshold_resist():
    """Level 1 must reduce to the Phase 5 MVP model when sigma is zero."""
    aerial = np.array([[0.1, 0.4, 0.7], [0.2, 0.5, 0.9]])

    baseline = threshold_resist(aerial, dose=1.2, threshold=0.5)
    blurred = blurred_threshold_resist(
        aerial,
        pixel_size_m=1e-9,
        sigma_m=0.0,
        dose=1.2,
        threshold=0.5,
    )

    assert np.array_equal(blurred, baseline)


def test_blur_rejects_invalid_inputs():
    """Negative sigma, bad dimensionality, and negative intensity are invalid."""
    with pytest.raises(ValueError, match="sigma_m"):
        gaussian_kernel_1d(sigma_m=-1e-9, pixel_size_m=1e-9)
    with pytest.raises(ValueError, match="1-D line or 2-D image"):
        gaussian_blur(np.zeros((2, 2, 2)), pixel_size_m=1e-9, sigma_m=1e-9)
    with pytest.raises(ValueError, match="non-negative"):
        gaussian_blur(np.array([-0.1, 0.2]), pixel_size_m=1e-9, sigma_m=1e-9)


def test_blur_dose_sweep_returns_cd_epe_grid():
    """The L1 sweep should emit one CD/EPE point per sigma-dose pair."""
    target = _two_line_target()
    points = blur_dose_sweep(
        target.astype(float),
        target,
        pixel_size_m=1e-9,
        sigma_values_m=[2e-9, 4e-9],
        doses=[1.0, 2.0],
        threshold=0.5,
    )

    assert len(points) == 4
    assert {(point.sigma_m, point.dose) for point in points} == {
        (2e-9, 1.0),
        (2e-9, 2.0),
        (4e-9, 1.0),
        (4e-9, 2.0),
    }
    assert all(point.cd_m > 0.0 for point in points)
    assert all(point.mean_abs_epe_m is not None for point in points)


def test_blur_sweep_lwr_proxy_increases_with_sigma():
    """At fixed dose, the deterministic LWR proxy follows blur width."""
    target = _two_line_target()
    points = blur_dose_sweep(
        target.astype(float),
        target,
        pixel_size_m=1e-9,
        sigma_values_m=[2e-9, 4e-9],
        doses=[1.0],
        threshold=0.5,
    )

    assert points[1].transition_width_m > points[0].transition_width_m
    assert points[1].lwr_proxy_m > points[0].lwr_proxy_m


def test_blur_sweep_lwr_proxy_decreases_with_dose():
    """At fixed blur, the exposure-normalized proxy falls with dose."""
    target = _two_line_target()
    points = blur_dose_sweep(
        target.astype(float),
        target,
        pixel_size_m=1e-9,
        sigma_values_m=[4e-9],
        doses=[1.0, 4.0],
        threshold=0.5,
    )

    assert points[1].transition_width_m == pytest.approx(points[0].transition_width_m)
    assert points[1].lwr_proxy_m == pytest.approx(0.5 * points[0].lwr_proxy_m)


def test_blur_sweep_rejects_bad_target_shape():
    """Sweep inputs must preserve one target pixel per aerial sample."""
    with pytest.raises(ValueError, match="target_line"):
        blur_dose_sweep(
            np.ones(8),
            np.ones(7, dtype=bool),
            pixel_size_m=1e-9,
            sigma_values_m=[2e-9],
            doses=[1.0],
        )


def _two_line_target() -> np.ndarray:
    target = np.zeros(120, dtype=bool)
    target[20:40] = True
    target[70:90] = True
    return target
