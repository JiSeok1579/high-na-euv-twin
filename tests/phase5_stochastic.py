"""Phase 5 Level 3 tests for stochastic resist LWR MVP."""

from __future__ import annotations

import numpy as np
import pytest

from src.resist_stochastic import (
    StochasticResistParams,
    calibrate_stochastic_lwr_budget,
    lwr_decomposition_budget,
    monte_carlo_convergence_gate,
    monte_carlo_lwr_curve,
    stochastic_lwr_m,
    stochastic_resist,
)


def test_stochastic_resist_chain_tracks_aerial_dose_response():
    """Photon/acid/deprotection means should rise with aerial intensity."""
    aerial = np.concatenate(
        [
            np.full(256, 0.10),
            np.full(256, 0.80),
        ]
    )
    exposure = stochastic_resist(
        aerial,
        dose=1.0,
        params=StochasticResistParams(
            photon_density_per_unit=600.0,
            material_threshold_sigma=0.0,
        ),
        rng=np.random.default_rng(20260426),
    )

    low = slice(0, 256)
    high = slice(256, 512)
    assert exposure.photon_count.shape == aerial.shape
    assert exposure.printed.dtype == np.bool_
    assert float(np.mean(exposure.photon_count[high])) > float(
        np.mean(exposure.photon_count[low])
    )
    assert float(np.mean(exposure.acid_count[high])) > float(
        np.mean(exposure.acid_count[low])
    )
    assert float(np.mean(exposure.deprotection_fraction[high])) > float(
        np.mean(exposure.deprotection_fraction[low])
    )
    assert np.any(exposure.printed[high])


def test_zero_material_sigma_uses_constant_clearing_threshold():
    """Turning off material variability should leave only chain shot noise."""
    params = StochasticResistParams(material_threshold_sigma=0.0)
    exposure = stochastic_resist(
        np.full((4, 5), 0.5),
        params=params,
        rng=np.random.default_rng(7),
    )

    assert np.allclose(exposure.clearing_threshold_map, params.clearing_threshold)


def test_monte_carlo_lwr_curve_is_reproducible_with_seed():
    """Seeded trials should emit stable CD/LWR samples for regression use."""
    params = StochasticResistParams(
        photon_density_per_unit=500.0,
        material_threshold_sigma=0.01,
    )
    first = monte_carlo_lwr_curve(
        _soft_line(),
        pixel_size_m=1e-9,
        doses=[0.8, 1.0],
        trials=24,
        params=params,
        seed=1234,
    )
    second = monte_carlo_lwr_curve(
        _soft_line(),
        pixel_size_m=1e-9,
        doses=[0.8, 1.0],
        trials=24,
        params=params,
        seed=1234,
    )

    assert first == second
    assert [point.dose for point in first] == [0.8, 1.0]
    assert all(point.trials == 24 for point in first)
    assert all(point.mean_cd_m > 0.0 for point in first)
    assert all(point.lwr_m >= 0.0 for point in first)
    assert first[0].lwr_m == pytest.approx(
        stochastic_lwr_m(first[0].cd_samples_m)
    )


def test_monte_carlo_convergence_gate_accepts_1000_trial_stable_lwr():
    """The L3 Part 02 gate should pass after the 1000-trial LWR stabilizes."""
    params = StochasticResistParams(
        photon_density_per_unit=800.0,
        material_threshold_sigma=0.005,
    )
    gate = monte_carlo_convergence_gate(
        _soft_line(),
        pixel_size_m=1e-9,
        dose=1.0,
        trial_counts=[100, 300, 1000],
        tolerance_fraction=0.10,
        params=params,
        seed=1,
    )

    assert [point.trials for point in gate.trial_results] == [100, 300, 1000]
    assert gate.min_trials == 1000
    assert gate.final_lwr_m == pytest.approx(gate.trial_results[-1].lwr_m)
    assert gate.relative_lwr_change <= gate.tolerance_fraction
    assert gate.converged


def test_monte_carlo_convergence_gate_fails_tight_tolerance():
    """The same MC trace should fail when the convergence tolerance is too tight."""
    gate = monte_carlo_convergence_gate(
        _soft_line(),
        pixel_size_m=1e-9,
        dose=1.0,
        trial_counts=[100, 300, 1000],
        tolerance_fraction=0.01,
        params=StochasticResistParams(
            photon_density_per_unit=800.0,
            material_threshold_sigma=0.005,
        ),
        seed=1,
    )

    assert gate.relative_lwr_change > gate.tolerance_fraction
    assert not gate.converged


def test_lwr_budget_reproduces_optical_material_smile_shape():
    """Optical LWR falls with dose while material LWR grows at high dose."""
    low = lwr_decomposition_budget(0.5, cd_m=36e-9)
    nominal = lwr_decomposition_budget(1.0, cd_m=36e-9)
    high = lwr_decomposition_budget(2.0, cd_m=36e-9)

    assert low.optical_lwr_m > nominal.optical_lwr_m > high.optical_lwr_m
    assert low.material_lwr_m < nominal.material_lwr_m < high.material_lwr_m
    assert low.cross_term_m2 < 0.0
    assert nominal.total_lwr_m < low.total_lwr_m
    assert nominal.total_lwr_m < high.total_lwr_m


def test_calibrate_stochastic_lwr_budget_recovers_reference_coefficients():
    """Level 3 calibration fits optical/material LWR coefficients to data."""
    true_params = StochasticResistParams(
        optical_lwr_coeff_m=2.0e-9,
        material_lwr_coeff_m=4.0e-9,
        cross_compensation=0.2,
    )
    doses = [0.5, 1.0, 2.0]
    cds = [36e-9, 36e-9, 36e-9]
    measured = [
        lwr_decomposition_budget(dose, cd_m=cd_m, params=true_params).total_lwr_m
        for dose, cd_m in zip(doses, cds, strict=True)
    ]

    calibration = calibrate_stochastic_lwr_budget(
        doses,
        cds,
        measured,
        params=StochasticResistParams(cross_compensation=0.2),
        optical_coeff_grid_m=[2.0e-9, 3.0e-9],
        material_coeff_grid_m=[3.0e-9, 4.0e-9],
    )

    assert calibration.params.optical_lwr_coeff_m == pytest.approx(2.0e-9)
    assert calibration.params.material_lwr_coeff_m == pytest.approx(4.0e-9)
    assert calibration.rms_error_m == pytest.approx(0.0, abs=1e-18)


def test_stochastic_lwr_uses_three_sigma_sample_width():
    """The exported helper should match the explicit 3-sigma convention."""
    samples = [20e-9, 21e-9, 19e-9, 22e-9]

    assert stochastic_lwr_m(samples) == pytest.approx(
        3.0 * float(np.std(samples, ddof=1))
    )


def test_stochastic_resist_rejects_invalid_inputs():
    """Invalid physical parameters should fail before Monte Carlo execution."""
    with pytest.raises(ValueError, match="non-negative"):
        stochastic_resist(np.array([-0.1, 0.2]))
    with pytest.raises(ValueError, match="dose"):
        stochastic_resist(np.ones(4), dose=0.0)
    with pytest.raises(ValueError, match="photon_density_per_unit"):
        stochastic_resist(
            np.ones(4),
            params=StochasticResistParams(photon_density_per_unit=0.0),
        )
    with pytest.raises(ValueError, match="trials"):
        monte_carlo_lwr_curve(np.ones(8), 1e-9, [1.0], trials=1)
    with pytest.raises(ValueError, match="1-D"):
        monte_carlo_lwr_curve(np.ones((2, 2)), 1e-9, [1.0], trials=2)
    with pytest.raises(ValueError, match="at least two"):
        stochastic_lwr_m([20e-9])


def test_monte_carlo_convergence_gate_rejects_invalid_gate_inputs():
    """Convergence gates need increasing counts and a final 1000-trial sample."""
    with pytest.raises(ValueError, match="at least two"):
        monte_carlo_convergence_gate(np.ones(8), 1e-9, trial_counts=[1000])
    with pytest.raises(ValueError, match="strictly increasing"):
        monte_carlo_convergence_gate(np.ones(8), 1e-9, trial_counts=[100, 100])
    with pytest.raises(ValueError, match="at least min_trials"):
        monte_carlo_convergence_gate(
            np.ones(8),
            1e-9,
            trial_counts=[100, 300],
            min_trials=1000,
        )
    with pytest.raises(ValueError, match="tolerance_fraction"):
        monte_carlo_convergence_gate(
            np.ones(8),
            1e-9,
            tolerance_fraction=-0.1,
        )
    with pytest.raises(ValueError, match="must match length"):
        calibrate_stochastic_lwr_budget(
            [1.0],
            [36e-9, 40e-9],
            [4e-9],
        )


def _soft_line() -> np.ndarray:
    line = np.full(160, 0.05, dtype=np.float64)
    line[50:60] = np.linspace(0.05, 0.85, 10)
    line[60:100] = 0.85
    line[100:110] = np.linspace(0.85, 0.05, 10)
    return line
