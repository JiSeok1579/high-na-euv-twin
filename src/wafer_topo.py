"""Wafer topography and defocus helpers for Phase 3.

Sign convention
---------------
`defocus_m > 0` means the wafer surface is above the nominal best-focus
plane, toward the projection optics. Positive defocus maps to a positive
pupil phase:

    phi_defocus(rho) = + pi * defocus_m * NA^2 / wavelength * rho^2

The opposite defocus value must produce the complex-conjugate pupil phase.
This convention is fixed before adding spatially varying topography so that
later resist and focus-exposure models share the same z direction.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

from . import constants as C

DefocusApproximation = Literal["paraxial", "angular"]


@dataclass(frozen=True)
class DefocusConvention:
    """Human-readable record of the signed defocus convention."""

    positive_z: str = "wafer surface above nominal best focus"
    positive_z_direction: str = "toward projection optics"
    phase_equation: str = "+pi * defocus_m * NA^2 / wavelength * rho^2"
    angular_phase_equation: str = "+2pi * defocus_m / wavelength * (1 - cos(theta))"


DEFOCUS_CONVENTION = DefocusConvention()


def height_to_defocus_m(
    wafer_height_m: np.ndarray | float,
    focus_plane_m: float = 0.0,
) -> np.ndarray:
    """Convert wafer height into signed defocus relative to best focus.

    Positive output means the wafer surface is above the nominal best-focus
    plane, using the project-wide Phase 3 convention.
    """
    return np.asarray(wafer_height_m, dtype=np.float64) - float(focus_plane_m)


def defocus_phase_radians(
    rho: np.ndarray,
    defocus_m: float,
    na: float = C.NA_HIGH,
    wavelength: float = C.LAMBDA_EUV,
    approximation: DefocusApproximation = "paraxial",
) -> np.ndarray:
    """Return the Fresnel defocus phase in radians on a normalized pupil.

    Parameters
    ----------
    rho : ndarray
        Normalized pupil radius where rho = 1 maps to the system NA.
    defocus_m : float
        Signed defocus in meters. Positive means wafer above best focus.
    na : float
        Numerical aperture.
    wavelength : float
        Exposure wavelength in meters.
    approximation : {"paraxial", "angular"}
        `paraxial` uses the Phase 3 Part 01 expression. `angular` uses the
        full angular optical-path expression and removes piston so that both
        options agree at rho = 0.
    """
    if not np.isfinite(defocus_m):
        raise ValueError("defocus_m must be finite")
    if not 0.0 < na <= 1.0:
        raise ValueError("na must be in (0, 1]")
    if wavelength <= 0.0:
        raise ValueError("wavelength must be positive")
    if approximation not in ("paraxial", "angular"):
        raise ValueError("approximation must be 'paraxial' or 'angular'")

    rho_arr = np.clip(np.asarray(rho, dtype=np.float64), 0.0, 1.0)
    if approximation == "paraxial":
        return np.pi * float(defocus_m) * na * na / wavelength * rho_arr**2

    sin_theta = np.clip(na * rho_arr, 0.0, 1.0)
    cos_theta = np.sqrt(1.0 - sin_theta**2)
    return 2.0 * np.pi * float(defocus_m) / wavelength * (1.0 - cos_theta)


def defocus_pupil_phase(
    rho: np.ndarray,
    defocus_m: float,
    na: float = C.NA_HIGH,
    wavelength: float = C.LAMBDA_EUV,
    approximation: DefocusApproximation = "paraxial",
) -> np.ndarray:
    """Return complex pupil multiplier exp(i * phi_defocus)."""
    phase = defocus_phase_radians(
        rho,
        defocus_m,
        na=na,
        wavelength=wavelength,
        approximation=approximation,
    )
    return np.exp(1j * phase).astype(np.complex128)


def max_defocus_phase_step_radians(
    grid_size: int,
    defocus_m: float,
    na: float = C.NA_HIGH,
    wavelength: float = C.LAMBDA_EUV,
    approximation: DefocusApproximation = "paraxial",
) -> float:
    """Estimate the largest radial defocus phase step on a pupil grid."""
    if grid_size < 2:
        raise ValueError("grid_size must be at least 2")
    rho = np.linspace(0.0, 1.0, grid_size // 2 + 1)
    phase = defocus_phase_radians(
        rho,
        defocus_m,
        na=na,
        wavelength=wavelength,
        approximation=approximation,
    )
    if phase.size < 2:
        return 0.0
    return float(np.max(np.abs(np.diff(phase))))


def validate_defocus_sampling(
    grid_size: int,
    defocus_m: float,
    na: float = C.NA_HIGH,
    wavelength: float = C.LAMBDA_EUV,
    approximation: DefocusApproximation = "paraxial",
    max_phase_step_rad: float = np.pi / 2.0,
) -> None:
    """Raise if the defocus phase is under-sampled on the pupil grid."""
    if max_phase_step_rad <= 0.0:
        raise ValueError("max_phase_step_rad must be positive")
    step = max_defocus_phase_step_radians(
        grid_size,
        defocus_m,
        na=na,
        wavelength=wavelength,
        approximation=approximation,
    )
    if step > max_phase_step_rad:
        raise ValueError(
            f"defocus phase step {step:.3f} rad exceeds sampling limit "
            f"{max_phase_step_rad:.3f} rad. Increase grid_size or reduce defocus_m."
        )
