"""Kirchhoff thin-mask model for the EUV reticle.

The Kirchhoff (thin-mask) approximation treats the reflective EUV mask as
an infinitely thin amplitude/phase modulator: the absorber stops the field
(amplitude 0), the multilayer reflects with amplitude 1 and phase 0. This
is the Phase 1 baseline. Phase 4 will introduce boundary corrections to
capture the dominant Mask 3D effects (paper #12).

Conventions
-----------
- pattern is a 2-D ndarray with values in {0, 1}: 1 = absorber present
  (opaque), 0 = clear multilayer.
- The returned complex amplitude follows transmission convention:
  field = (1 - pattern), i.e. amplitude 0 where pattern is 1.
- All spatial dimensions are in meters at the *mask plane*. The
  anamorphic 4×/8× demagnification is applied later in aerial.py.

References
----------
- physics_considerations.md Part L (Mask)
- PROJECT_PLAN.md Phase 1
- Paper #12 (M3D, future Phase 4)
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class MaskGrid:
    """Pixel grid of the mask plane."""

    nx: int
    ny: int
    pixel_size: float

    def shape(self) -> tuple[int, int]:
        return (self.ny, self.nx)

    def extent_m(self) -> tuple[float, float]:
        return (self.nx * self.pixel_size, self.ny * self.pixel_size)


def kirchhoff_mask(pattern: np.ndarray) -> np.ndarray:
    """Return the complex transmission of a binary absorber pattern.

    Parameters
    ----------
    pattern : ndarray of {0, 1}
        Binary array marking absorber (1) vs clear multilayer (0).

    Returns
    -------
    field : complex ndarray, same shape as pattern
        Complex amplitude after Kirchhoff thin-mask: (1 - pattern).
    """
    arr = np.asarray(pattern)
    if arr.ndim != 2:
        raise ValueError("pattern must be a 2-D array")
    if not np.issubdtype(arr.dtype, np.number):
        raise TypeError("pattern must be numeric")
    if not np.all((arr == 0) | (arr == 1)):
        raise ValueError("pattern must contain only 0 or 1")
    return (1.0 - arr.astype(np.float64)).astype(np.complex128)


def line_space_pattern(
    grid: MaskGrid,
    pitch_m: float,
    duty_cycle: float = 0.5,
    orientation: str = "vertical",
) -> np.ndarray:
    """Generate a line/space pattern at the *mask plane*.

    The pitch is measured at the mask. To compare with wafer-plane pitches
    (e.g. 32 nm), multiply by the anamorphic demagnification (×4 or ×8).

    Parameters
    ----------
    pitch_m : float
        Line+space pitch in meters at the mask plane.
    duty_cycle : float in (0, 1)
        Fraction of pitch occupied by the absorber (line).
    orientation : {"vertical", "horizontal"}
        Direction of the lines.
    """
    if pitch_m <= 0.0:
        raise ValueError("pitch_m must be positive")
    if not 0.0 < duty_cycle < 1.0:
        raise ValueError("duty_cycle must be in (0, 1)")
    if orientation not in {"vertical", "horizontal"}:
        raise ValueError("orientation must be 'vertical' or 'horizontal'")

    pitch_px_float = pitch_m / grid.pixel_size
    if pitch_px_float < 2.0:
        raise ValueError(
            "pitch is undersampled: need at least 2 pixels per pitch (got "
            f"{pitch_px_float:.2f}). Increase grid.nx/ny or decrease pixel_size."
        )
    # Round to integer pixels to keep the period exact and avoid float drift.
    pitch_px = max(2, int(round(pitch_px_float)))
    duty_px = max(1, min(pitch_px - 1, int(round(duty_cycle * pitch_px))))

    pattern = np.zeros(grid.shape(), dtype=np.float64)
    if orientation == "vertical":
        coord = np.arange(grid.nx)
        line = ((coord % pitch_px) < duty_px).astype(np.float64)
        pattern[:, :] = line[np.newaxis, :]
    else:
        coord = np.arange(grid.ny)
        line = ((coord % pitch_px) < duty_px).astype(np.float64)
        pattern[:, :] = line[:, np.newaxis]
    return pattern


def pinhole_pattern(grid: MaskGrid, radius_m: float | None = None) -> np.ndarray:
    """Single clear pinhole on an opaque mask. Used for PSF tests."""
    pattern = np.ones(grid.shape(), dtype=np.float64)
    cy, cx = grid.ny // 2, grid.nx // 2
    if radius_m is None:
        pattern[cy, cx] = 0.0
        return pattern
    yy, xx = np.indices(grid.shape())
    r2 = ((yy - cy) * grid.pixel_size) ** 2 + ((xx - cx) * grid.pixel_size) ** 2
    pattern[r2 <= radius_m * radius_m] = 0.0
    return pattern
