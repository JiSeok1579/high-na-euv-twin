"""Pupil function for the projection optics.

Implements the annular pupil with optional central obscuration and
Zernike-polynomial wavefront aberration plus Phase 3 constant defocus. The
pupil is sampled on a square frequency-domain grid of normalized spatial
frequencies (f_x, f_y) where the unit circle corresponds to the system NA.

Conventions
-----------
- Normalized pupil radius rho = sqrt(f_x^2 + f_y^2) / NA.
- Pupil amplitude is 1 inside the annulus and 0 outside.
- Aberration adds a phase exp(i · 2π · W / lambda), where W is the
  optical path difference produced by the Zernike series at (rho, theta).
- Defocus uses the Phase 3 sign convention from `wafer_topo.py`: positive
  defocus means wafer above best focus and adds +π·z·NA²/λ·rho².

Reference
---------
- physics_considerations.md Part E (Fourier optics)
- 진행계획서.md §4.1 WP1.2
- Paper #15 (central obscuration), #19 (anamorphic)
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from . import constants as C
from .optics import ZernikeCoeffs, wavefront
from .wafer_topo import DefocusApproximation, defocus_pupil_phase, validate_defocus_sampling


@dataclass(frozen=True)
class PupilSpec:
    """Container describing the pupil sampling and physics."""

    grid_size: int
    na: float = C.NA_HIGH
    obscuration_ratio: float = C.DEFAULT_OBSCURATION_RATIO
    wavelength: float = C.LAMBDA_EUV
    zernike: ZernikeCoeffs = field(default_factory=dict)
    defocus_m: float = 0.0
    defocus_approximation: DefocusApproximation = "paraxial"

    def __post_init__(self) -> None:
        if self.grid_size <= 0 or self.grid_size % 2 != 0:
            raise ValueError("grid_size must be a positive even integer")
        if not 0.0 < self.na <= 1.0:
            raise ValueError("na must be in (0, 1]")
        if not 0.0 <= self.obscuration_ratio < 1.0:
            raise ValueError("obscuration_ratio must be in [0, 1)")
        if self.wavelength <= 0.0:
            raise ValueError("wavelength must be positive")
        if not np.isfinite(self.defocus_m):
            raise ValueError("defocus_m must be finite")
        if self.defocus_m != 0.0:
            validate_defocus_sampling(
                self.grid_size,
                self.defocus_m,
                na=self.na,
                wavelength=self.wavelength,
                approximation=self.defocus_approximation,
            )


def _frequency_grid(grid_size: int) -> tuple[np.ndarray, np.ndarray]:
    """Return centered frequency coordinates normalized to [-1, 1]."""
    axis = np.linspace(-1.0, 1.0, grid_size, endpoint=False)
    fx, fy = np.meshgrid(axis, axis, indexing="xy")
    return fx, fy


def build_pupil(spec: PupilSpec) -> np.ndarray:
    """Construct the complex pupil function P(f_x, f_y).

    Returns
    -------
    pupil : (N, N) complex ndarray
        Centered pupil, where pupil[N/2, N/2] is the (0, 0) frequency.
        Magnitude is 1 inside the annulus (NA·ε ≤ rho_phys ≤ NA), 0 outside.
        Phase encodes the Zernike wavefront via exp(i·2π·W).
    """
    fx, fy = _frequency_grid(spec.grid_size)
    rho = np.sqrt(fx**2 + fy**2)
    theta = np.arctan2(fy, fx)

    inside = rho <= 1.0
    outside_obscuration = rho >= spec.obscuration_ratio
    annulus = inside & outside_obscuration

    amplitude = annulus.astype(np.float64)

    phase = np.ones_like(amplitude, dtype=np.complex128)
    if spec.zernike:
        w_waves = wavefront(rho, theta, spec.zernike)
        phase *= np.exp(1j * 2.0 * np.pi * w_waves)
    if spec.defocus_m != 0.0:
        phase *= defocus_pupil_phase(
            rho,
            spec.defocus_m,
            na=spec.na,
            wavelength=spec.wavelength,
            approximation=spec.defocus_approximation,
        )

    return (amplitude * phase).astype(np.complex128)


def pupil_metrics(pupil: np.ndarray) -> dict[str, float]:
    """Quick summary metrics for a pupil array (filling fraction, energy)."""
    mag = np.abs(pupil)
    n_open = float(np.count_nonzero(mag > 0))
    n_total = float(mag.size)
    return {
        "fill_fraction": n_open / n_total,
        "energy": float(np.sum(mag**2)),
    }
