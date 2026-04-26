"""Stochastic resist Monte Carlo MVP for Phase 5 Level 3."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .metrics import critical_dimension


@dataclass(frozen=True)
class StochasticResistParams:
    """Reduced stochastic-chain parameters for EUV resist exposure."""

    photon_density_per_unit: float = 80.0
    secondary_electron_yield: float = 1.0
    acid_yield: float = 1.0
    deprotection_gain: float = 1.0
    clearing_threshold: float = 0.25
    material_threshold_sigma: float = 0.03
    optical_lwr_coeff_m: float = 3.0e-9
    material_lwr_coeff_m: float = 3.0e-9
    cross_compensation: float = 0.30
    reference_cd_m: float = 36.0e-9


@dataclass(frozen=True)
class StochasticExposure:
    """One stochastic resist exposure trial."""

    photon_count: np.ndarray
    secondary_electron_count: np.ndarray
    acid_count: np.ndarray
    deprotection_fraction: np.ndarray
    clearing_threshold_map: np.ndarray
    printed: np.ndarray


@dataclass(frozen=True)
class LWRBudget:
    """Dose-dependent optical/material LWR variance decomposition."""

    dose: float
    cd_m: float
    optical_lwr_m: float
    material_lwr_m: float
    cross_term_m2: float
    total_lwr_m: float


@dataclass(frozen=True)
class StochasticDoseResult:
    """Monte Carlo CD/LWR/LCDU summary at one dose."""

    dose: float
    trials: int
    mean_cd_m: float
    std_cd_m: float
    lwr_m: float
    lcdu_m: float
    missing_fraction: float
    budget: LWRBudget
    cd_samples_m: tuple[float, ...]


@dataclass(frozen=True)
class MonteCarloConvergenceResult:
    """Trial-count convergence gate for stochastic LWR estimates."""

    dose: float
    trial_results: tuple[StochasticDoseResult, ...]
    previous_lwr_m: float
    final_lwr_m: float
    relative_lwr_change: float
    tolerance_fraction: float
    min_trials: int
    converged: bool


def stochastic_resist(
    aerial: np.ndarray,
    *,
    dose: float = 1.0,
    params: StochasticResistParams | None = None,
    rng: np.random.Generator | None = None,
) -> StochasticExposure:
    """Run one photon-to-dissolution stochastic resist trial."""
    if params is None:
        params = StochasticResistParams()
    _validate_params(params)
    _validate_positive_finite(dose, "dose")
    generator = np.random.default_rng() if rng is None else rng

    image = _as_nonnegative_image(aerial)
    photon_lambda = dose * image * params.photon_density_per_unit
    photon_count = generator.poisson(photon_lambda).astype(np.float64)
    secondary_electron_count = generator.poisson(
        photon_count * params.secondary_electron_yield
    ).astype(np.float64)
    acid_count = generator.poisson(
        secondary_electron_count * params.acid_yield
    ).astype(np.float64)

    acid_normalizer = (
        params.photon_density_per_unit
        * params.secondary_electron_yield
        * params.acid_yield
    )
    chemical_signal = acid_count / acid_normalizer
    deprotection_fraction = (
        1.0 - np.exp(-params.deprotection_gain * chemical_signal)
    ).astype(np.float64)

    threshold_map = _sample_material_thresholds(image.shape, params, generator)
    printed = deprotection_fraction > threshold_map
    return StochasticExposure(
        photon_count=photon_count,
        secondary_electron_count=secondary_electron_count,
        acid_count=acid_count,
        deprotection_fraction=deprotection_fraction,
        clearing_threshold_map=threshold_map,
        printed=printed,
    )


def monte_carlo_lwr_curve(
    aerial_line: np.ndarray,
    pixel_size_m: float,
    doses: Iterable[float],
    *,
    trials: int = 100,
    params: StochasticResistParams | None = None,
    seed: int | None = None,
    foreground: bool = True,
    include_boundary: bool = False,
) -> tuple[StochasticDoseResult, ...]:
    """Return CD, LWR, LCDU, and variance-budget summaries over a dose sweep."""
    if params is None:
        params = StochasticResistParams()
    _validate_params(params)
    _validate_pixel_size(pixel_size_m)
    if trials <= 1:
        raise ValueError("trials must be greater than one")

    line = _as_nonnegative_line(aerial_line)
    dose_values = tuple(float(value) for value in doses)
    if not dose_values:
        raise ValueError("doses must contain at least one value")
    if any(not np.isfinite(value) or value <= 0.0 for value in dose_values):
        raise ValueError("doses must contain positive finite values")

    generator = np.random.default_rng(seed)
    results: list[StochasticDoseResult] = []
    for dose in dose_values:
        cd_samples = []
        for _ in range(trials):
            exposure = stochastic_resist(
                line,
                dose=dose,
                params=params,
                rng=generator,
            )
            cd_samples.append(
                critical_dimension(
                    exposure.printed,
                    pixel_size_m,
                    foreground=foreground,
                    include_boundary=include_boundary,
                )
            )

        cd_array = np.array(cd_samples, dtype=np.float64)
        mean_cd_m = float(np.mean(cd_array))
        std_cd_m = float(np.std(cd_array, ddof=1))
        lwr_m = 3.0 * std_cd_m
        budget = lwr_decomposition_budget(
            dose,
            cd_m=max(mean_cd_m, pixel_size_m),
            params=params,
        )
        results.append(
            StochasticDoseResult(
                dose=dose,
                trials=trials,
                mean_cd_m=mean_cd_m,
                std_cd_m=std_cd_m,
                lwr_m=lwr_m,
                lcdu_m=lwr_m,
                missing_fraction=float(np.mean(cd_array <= 0.0)),
                budget=budget,
                cd_samples_m=tuple(float(value) for value in cd_array),
            )
        )

    return tuple(results)


def monte_carlo_convergence_gate(
    aerial_line: np.ndarray,
    pixel_size_m: float,
    *,
    dose: float = 1.0,
    trial_counts: Iterable[int] = (100, 300, 1000),
    tolerance_fraction: float = 0.10,
    min_trials: int = 1000,
    params: StochasticResistParams | None = None,
    seed: int | None = None,
    foreground: bool = True,
    include_boundary: bool = False,
) -> MonteCarloConvergenceResult:
    """Evaluate whether stochastic LWR has stabilized by the final trial count."""
    _validate_positive_finite(dose, "dose")
    counts = _validate_convergence_inputs(
        trial_counts,
        tolerance_fraction,
        min_trials,
    )

    results = tuple(
        monte_carlo_lwr_curve(
            aerial_line,
            pixel_size_m,
            [dose],
            trials=count,
            params=params,
            seed=seed,
            foreground=foreground,
            include_boundary=include_boundary,
        )[0]
        for count in counts
    )
    previous = results[-2]
    final = results[-1]
    denominator = max(abs(final.lwr_m), float(np.finfo(np.float64).eps))
    relative_change = abs(final.lwr_m - previous.lwr_m) / denominator
    converged = (
        final.trials >= min_trials and relative_change <= tolerance_fraction
    )

    return MonteCarloConvergenceResult(
        dose=float(dose),
        trial_results=results,
        previous_lwr_m=previous.lwr_m,
        final_lwr_m=final.lwr_m,
        relative_lwr_change=float(relative_change),
        tolerance_fraction=float(tolerance_fraction),
        min_trials=int(min_trials),
        converged=bool(converged),
    )


def lwr_decomposition_budget(
    dose: float,
    *,
    cd_m: float,
    params: StochasticResistParams | None = None,
) -> LWRBudget:
    """Return paper-1-style optical/material/cross stochastic LWR budget."""
    if params is None:
        params = StochasticResistParams()
    _validate_params(params)
    _validate_positive_finite(dose, "dose")
    _validate_positive_finite(cd_m, "cd_m")

    cd_ratio = max(cd_m / params.reference_cd_m, 0.25)
    optical_lwr_m = params.optical_lwr_coeff_m / np.sqrt(dose * cd_ratio)
    material_lwr_m = params.material_lwr_coeff_m * np.sqrt(dose * cd_ratio)
    cross_term_m2 = -params.cross_compensation * optical_lwr_m * material_lwr_m
    total_variance = optical_lwr_m**2 + material_lwr_m**2 + cross_term_m2
    total_lwr_m = float(np.sqrt(max(total_variance, 0.0)))

    return LWRBudget(
        dose=float(dose),
        cd_m=float(cd_m),
        optical_lwr_m=float(optical_lwr_m),
        material_lwr_m=float(material_lwr_m),
        cross_term_m2=float(cross_term_m2),
        total_lwr_m=total_lwr_m,
    )


def stochastic_lwr_m(
    cd_samples_m: Iterable[float],
    *,
    sigma_multiplier: float = 3.0,
) -> float:
    """Return a sigma-multiplied LWR estimate from Monte Carlo CD samples."""
    samples = np.array(tuple(float(value) for value in cd_samples_m), dtype=np.float64)
    if samples.size <= 1:
        raise ValueError("cd_samples_m must contain at least two values")
    if not np.all(np.isfinite(samples)):
        raise ValueError("cd_samples_m must contain finite values")
    if not np.isfinite(sigma_multiplier) or sigma_multiplier <= 0.0:
        raise ValueError("sigma_multiplier must be a positive finite value")
    return float(sigma_multiplier * np.std(samples, ddof=1))


def _sample_material_thresholds(
    shape: tuple[int, ...],
    params: StochasticResistParams,
    generator: np.random.Generator,
) -> np.ndarray:
    if params.material_threshold_sigma == 0.0:
        return np.full(shape, params.clearing_threshold, dtype=np.float64)

    thresholds = generator.normal(
        loc=params.clearing_threshold,
        scale=params.material_threshold_sigma,
        size=shape,
    )
    return np.clip(thresholds, 0.0, 1.0).astype(np.float64)


def _as_nonnegative_image(aerial: np.ndarray) -> np.ndarray:
    image = np.asarray(aerial, dtype=np.float64)
    if image.size == 0:
        raise ValueError("aerial must contain at least one pixel")
    if not np.all(np.isfinite(image)):
        raise ValueError("aerial must contain finite values")
    if np.any(image < 0.0):
        raise ValueError("aerial intensity must be non-negative")
    return image


def _as_nonnegative_line(aerial_line: np.ndarray) -> np.ndarray:
    line = _as_nonnegative_image(aerial_line)
    if line.ndim != 1:
        raise ValueError("aerial_line must be 1-D")
    return line


def _validate_params(params: StochasticResistParams) -> None:
    _validate_positive_finite(
        params.photon_density_per_unit,
        "photon_density_per_unit",
    )
    _validate_positive_finite(
        params.secondary_electron_yield,
        "secondary_electron_yield",
    )
    _validate_positive_finite(params.acid_yield, "acid_yield")
    _validate_positive_finite(params.deprotection_gain, "deprotection_gain")
    _validate_positive_finite(params.clearing_threshold, "clearing_threshold")
    if params.clearing_threshold >= 1.0:
        raise ValueError("clearing_threshold must be less than one")
    if (
        not np.isfinite(params.material_threshold_sigma)
        or params.material_threshold_sigma < 0.0
    ):
        raise ValueError("material_threshold_sigma must be non-negative and finite")
    _validate_positive_finite(params.optical_lwr_coeff_m, "optical_lwr_coeff_m")
    _validate_positive_finite(params.material_lwr_coeff_m, "material_lwr_coeff_m")
    _validate_positive_finite(params.reference_cd_m, "reference_cd_m")
    if (
        not np.isfinite(params.cross_compensation)
        or not 0.0 <= params.cross_compensation < 1.0
    ):
        raise ValueError("cross_compensation must satisfy 0 <= value < 1")


def _validate_convergence_inputs(
    trial_counts: Iterable[int],
    tolerance_fraction: float,
    min_trials: int,
) -> tuple[int, ...]:
    counts = tuple(int(value) for value in trial_counts)
    if len(counts) < 2:
        raise ValueError("trial_counts must contain at least two values")
    if any(value <= 1 for value in counts):
        raise ValueError("trial_counts must contain values greater than one")
    if any(next_value <= value for value, next_value in zip(counts, counts[1:])):
        raise ValueError("trial_counts must be strictly increasing")
    if not np.isfinite(tolerance_fraction) or tolerance_fraction < 0.0:
        raise ValueError("tolerance_fraction must be non-negative and finite")
    if min_trials <= 1:
        raise ValueError("min_trials must be greater than one")
    if counts[-1] < min_trials:
        raise ValueError("final trial count must be at least min_trials")
    return counts


def _validate_positive_finite(value: float, name: str) -> None:
    if not np.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be a positive finite value")


def _validate_pixel_size(pixel_size_m: float) -> None:
    if not np.isfinite(pixel_size_m) or pixel_size_m <= 0.0:
        raise ValueError("pixel_size_m must be a positive finite value")
