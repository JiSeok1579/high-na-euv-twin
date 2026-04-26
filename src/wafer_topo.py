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

import numpy as np

from . import constants as C


@dataclass(frozen=True)
class DefocusConvention:
    """Human-readable record of the signed defocus convention."""

    positive_z: str = "wafer surface above nominal best focus"
    positive_z_direction: str = "toward projection optics"
    phase_equation: str = "+pi * defocus_m * NA^2 / wavelength * rho^2"


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
    """
    if not np.isfinite(defocus_m):
        raise ValueError("defocus_m must be finite")
    if not 0.0 < na <= 1.0:
        raise ValueError("na must be in (0, 1]")
    if wavelength <= 0.0:
        raise ValueError("wavelength must be positive")

    rho_arr = np.asarray(rho, dtype=np.float64)
    return np.pi * float(defocus_m) * na * na / wavelength * rho_arr**2


def defocus_pupil_phase(
    rho: np.ndarray,
    defocus_m: float,
    na: float = C.NA_HIGH,
    wavelength: float = C.LAMBDA_EUV,
) -> np.ndarray:
    """Return complex pupil multiplier exp(i * phi_defocus)."""
    phase = defocus_phase_radians(rho, defocus_m, na=na, wavelength=wavelength)
    return np.exp(1j * phase).astype(np.complex128)
