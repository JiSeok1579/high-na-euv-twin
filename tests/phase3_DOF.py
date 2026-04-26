"""Phase 3 smoke tests for defocus sign convention and pupil integration."""

from __future__ import annotations

import numpy as np
import pytest

from src import constants as C
from src.aerial import aerial_image
from src.dof import (
    FocusSample,
    fit_k2_from_dof_cases,
    fit_k2_from_metrics,
    focus_drilling_average,
    focus_stack_contrast,
    k2_from_dof,
    nominal_depth_of_focus,
)
from src.mask import MaskGrid, kirchhoff_mask, line_space_pattern
from src.pupil import PupilSpec, build_pupil
from src.wafer_topo import (
    defocus_phase_radians,
    defocus_pupil_phase,
    height_to_defocus_m,
    max_defocus_phase_step_radians,
    validate_defocus_sampling,
)


def test_defocus_phase_sign_convention_is_fixed():
    """Positive z maps to positive phase at the pupil edge."""
    rho = np.array([0.0, 0.5, 1.0])
    dz = 20e-9

    plus = defocus_phase_radians(rho, dz, na=C.NA_HIGH, wavelength=C.LAMBDA_EUV)
    minus = defocus_phase_radians(rho, -dz, na=C.NA_HIGH, wavelength=C.LAMBDA_EUV)

    expected_edge = np.pi * dz * C.NA_HIGH**2 / C.LAMBDA_EUV
    assert plus[-1] == pytest.approx(expected_edge)
    assert plus[0] == pytest.approx(0.0)
    assert np.allclose(minus, -plus)


def test_full_angular_defocus_matches_paraxial_small_angle_limit():
    """The angular OPL option must reduce to the paraxial Phase 3 formula."""
    rho = np.linspace(0.0, 1.0, 9)
    dz = 20e-9
    na = 0.10

    paraxial = defocus_phase_radians(
        rho,
        dz,
        na=na,
        wavelength=C.LAMBDA_EUV,
        approximation="paraxial",
    )
    angular = defocus_phase_radians(
        rho,
        dz,
        na=na,
        wavelength=C.LAMBDA_EUV,
        approximation="angular",
    )

    assert np.allclose(angular, paraxial, rtol=3e-3, atol=1e-12)


def test_height_to_defocus_uses_focus_plane_reference():
    """Wafer height above focus is positive signed defocus."""
    heights = np.array([15e-9, 10e-9, 5e-9])
    expected = np.array([5e-9, 0.0, -5e-9])
    assert np.allclose(height_to_defocus_m(heights, focus_plane_m=10e-9), expected)


def test_defocus_pupil_phase_conjugates_for_opposite_signs():
    """The opposite defocus sign must produce the conjugate pupil phase."""
    rho = np.linspace(0.0, 1.0, 9)
    dz = 30e-9

    plus = defocus_pupil_phase(rho, dz)
    minus = defocus_pupil_phase(rho, -dz)
    zero = defocus_pupil_phase(rho, 0.0)

    assert np.allclose(plus, np.conjugate(minus))
    assert np.allclose(zero, np.ones_like(zero))


def test_defocus_sampling_guard_rejects_under_sampled_phase():
    """Large defocus on a tiny grid should be rejected before FFT use."""
    assert max_defocus_phase_step_radians(256, 50e-9) < np.pi / 2.0
    with pytest.raises(ValueError, match="defocus phase step"):
        validate_defocus_sampling(8, 10e-6, max_phase_step_rad=np.pi / 2.0)


def test_build_pupil_applies_expected_edge_phase():
    """PupilSpec.defocus_m is wired into the sampled pupil phase."""
    dz = 20e-9
    pupil = build_pupil(
        PupilSpec(
            grid_size=64,
            na=C.NA_HIGH,
            obscuration_ratio=0.0,
            defocus_m=dz,
        )
    )

    center = pupil[32, 32]
    edge = pupil[32, 0]
    expected_edge_phase = np.exp(1j * np.pi * dz * C.NA_HIGH**2 / C.LAMBDA_EUV)

    assert center == pytest.approx(1.0 + 0.0j)
    assert edge / abs(edge) == pytest.approx(expected_edge_phase)


def test_nominal_dof_metric_interpolates_threshold_crossings():
    """Synthetic stack verifies the nominal DOF interpolation independent of optics."""
    samples = [
        FocusSample(-80e-9, 0.70, 0.70),
        FocusSample(-40e-9, 0.90, 0.90),
        FocusSample(0.0, 1.00, 1.00),
        FocusSample(40e-9, 0.90, 0.90),
        FocusSample(80e-9, 0.70, 0.70),
    ]
    metrics = nominal_depth_of_focus(samples, threshold_fraction=0.8)

    assert metrics.reference_defocus_m == pytest.approx(0.0)
    assert metrics.lower_defocus_m == pytest.approx(-60e-9)
    assert metrics.upper_defocus_m == pytest.approx(60e-9)
    assert metrics.dof_m == pytest.approx(120e-9)


def test_focus_stack_contrast_is_symmetric_for_opposite_defocus():
    """A real coherent line-space stack should respect +/- defocus symmetry."""
    grid = MaskGrid(nx=512, ny=64, pixel_size=1e-9)
    mask = kirchhoff_mask(line_space_pattern(grid, pitch_m=30e-9))
    samples = focus_stack_contrast(
        mask,
        grid,
        [-80e-9, -40e-9, 0.0, 40e-9, 80e-9],
        pupil_spec=PupilSpec(grid_size=512, na=C.NA_HIGH, obscuration_ratio=0.0),
        anamorphic=False,
    )
    by_focus = {sample.defocus_m: sample.contrast for sample in samples}

    assert by_focus[-80e-9] == pytest.approx(by_focus[80e-9])
    assert by_focus[-40e-9] == pytest.approx(by_focus[40e-9])
    assert by_focus[0.0] > 0.9


def test_zero_defocus_preserves_phase1_aerial_image():
    """Explicit zero defocus must be identical to the Phase 1 focus plane."""
    grid = MaskGrid(nx=256, ny=64, pixel_size=2e-9)
    mask = kirchhoff_mask(line_space_pattern(grid, pitch_m=40e-9))
    focused_spec = PupilSpec(grid_size=256, na=C.NA_HIGH, obscuration_ratio=0.2)
    zero_defocus_spec = PupilSpec(
        grid_size=256,
        na=C.NA_HIGH,
        obscuration_ratio=0.2,
        defocus_m=0.0,
    )

    focused, _ = aerial_image(mask, grid, pupil_spec=focused_spec, anamorphic=False)
    zero_defocus, _ = aerial_image(
        mask,
        grid,
        pupil_spec=zero_defocus_spec,
        anamorphic=False,
    )

    assert np.allclose(zero_defocus, focused)


def test_k2_fit_matches_rayleigh_depth_of_focus_sweep():
    """Part 03 verifies the `DOF = k2 * lambda / NA^2` fit gate."""
    cases = [
        (C.NA_STANDARD, C.depth_of_focus(na=C.NA_STANDARD), 64e-9),
        (C.NA_HIGH, C.depth_of_focus(na=C.NA_HIGH), 36e-9),
    ]
    result = fit_k2_from_dof_cases(cases)

    assert [case.pitch_m for case in result.cases] == [64e-9, 36e-9]
    assert result.mean_k2 == pytest.approx(C.K2_TYPICAL)
    assert result.std_k2 == pytest.approx(0.0)
    assert result.relative_error == pytest.approx(0.0)
    assert result.passed
    assert k2_from_dof(C.depth_of_focus(), C.NA_HIGH) == pytest.approx(C.K2_TYPICAL)


def test_k2_fit_rejects_large_rayleigh_error():
    """The K3 gate must fail if fitted k2 is outside the tolerance band."""
    result = fit_k2_from_dof_cases(
        [(C.NA_HIGH, 2.0 * C.depth_of_focus(na=C.NA_HIGH))],
        tolerance_fraction=0.30,
    )

    assert result.mean_k2 == pytest.approx(1.0)
    assert not result.passed


def test_k2_fit_from_nominal_dof_metrics():
    """Already-computed DOFMetrics can feed the same k2 fitter."""
    dof_m = C.depth_of_focus(na=C.NA_HIGH)
    samples = [
        FocusSample(-0.75 * dof_m, 0.70, 0.70),
        FocusSample(-0.50 * dof_m, 0.80, 0.80),
        FocusSample(0.0, 1.00, 1.00),
        FocusSample(0.50 * dof_m, 0.80, 0.80),
        FocusSample(0.75 * dof_m, 0.70, 0.70),
    ]
    metrics = nominal_depth_of_focus(samples, threshold_fraction=0.8)
    result = fit_k2_from_metrics([(C.NA_HIGH, metrics)])

    assert metrics.dof_m == pytest.approx(dof_m)
    assert result.mean_k2 == pytest.approx(C.K2_TYPICAL)
    assert result.passed


def test_focus_drilling_single_slice_matches_aerial_image():
    """A one-slice focus-drilling pass is exactly the baseline aerial image."""
    grid = MaskGrid(nx=256, ny=64, pixel_size=2e-9)
    mask = kirchhoff_mask(line_space_pattern(grid, pitch_m=40e-9))
    pupil_spec = PupilSpec(grid_size=256, na=C.NA_HIGH, obscuration_ratio=0.0)

    focused, wafer = aerial_image(mask, grid, pupil_spec=pupil_spec, anamorphic=False)
    drilled, drilled_wafer = focus_drilling_average(
        mask,
        grid,
        [0.0],
        pupil_spec=pupil_spec,
        anamorphic=False,
    )

    assert drilled_wafer == wafer
    assert np.allclose(drilled, focused)


def test_focus_drilling_weighted_average_is_normalized_and_finite():
    """Depth-slice averaging keeps a bounded finite intensity plane."""
    grid = MaskGrid(nx=256, ny=64, pixel_size=2e-9)
    mask = kirchhoff_mask(line_space_pattern(grid, pitch_m=40e-9))
    drilled, wafer = focus_drilling_average(
        mask,
        grid,
        [-20e-9, 0.0, 20e-9],
        pupil_spec=PupilSpec(grid_size=256, na=C.NA_HIGH, obscuration_ratio=0.0),
        weights=[1.0, 2.0, 1.0],
        anamorphic=False,
    )

    assert drilled.shape == wafer.shape()
    assert np.all(np.isfinite(drilled))
    assert float(np.min(drilled)) >= 0.0
    assert float(np.max(drilled)) <= 1.0 + 1e-12
