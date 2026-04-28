"""Physical constants for the High-NA EUV simulator.

All units are SI unless noted. Length in meters, energy in joules.
Reference: PROJECT_OVERVIEW.md and PROJECT_PLAN.md.
"""

LAMBDA_EUV: float = 13.5e-9
NA_HIGH: float = 0.55
NA_STANDARD: float = 0.33

ANAMORPHIC_MAG_X: float = 4.0
ANAMORPHIC_MAG_Y: float = 8.0

DEFAULT_OBSCURATION_RATIO: float = 0.20

K1_LOW: float = 0.25
K1_TYPICAL: float = 0.30
K1_HIGH: float = 0.40

K2_TYPICAL: float = 0.50

C_LIGHT: float = 2.99792458e8
H_PLANCK: float = 6.62607015e-34


def euv_photon_energy_eV() -> float:
    """Photon energy of 13.5 nm EUV in electron-volts."""
    e_joules = H_PLANCK * C_LIGHT / LAMBDA_EUV
    return e_joules / 1.602176634e-19


def rayleigh_resolution(
    k1: float = K1_TYPICAL,
    wavelength: float = LAMBDA_EUV,
    na: float = NA_HIGH,
) -> float:
    """R = k1 · lambda / NA. Returns half-pitch in meters."""
    return k1 * wavelength / na


def depth_of_focus(
    k2: float = K2_TYPICAL,
    wavelength: float = LAMBDA_EUV,
    na: float = NA_HIGH,
) -> float:
    """DOF = k2 · lambda / NA²."""
    return k2 * wavelength / (na * na)
