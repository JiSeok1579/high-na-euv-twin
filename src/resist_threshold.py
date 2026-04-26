"""Threshold photoresist model for Phase 5 MVP.

This module intentionally implements the simplest resist transfer function:
an aerial-image pixel is exposed when `dose * intensity > threshold`.
Chemical blur, depth coupling, and stochastic development remain later Phase 5
levels.
"""

from __future__ import annotations

import numpy as np


def threshold_resist(
    aerial: np.ndarray,
    dose: float = 1.0,
    threshold: float = 0.3,
) -> np.ndarray:
    """Return the exposed resist map from an aerial image.

    Parameters
    ----------
    aerial:
        Non-negative aerial image intensity. Any dimensionality is accepted and
        preserved in the returned boolean array.
    dose:
        Scalar exposure dose multiplier.
    threshold:
        Clearing threshold in the same normalized dose-intensity units.
    """
    aerial_array = np.asarray(aerial, dtype=np.float64)
    if aerial_array.size == 0:
        raise ValueError("aerial must contain at least one pixel")
    if not np.all(np.isfinite(aerial_array)):
        raise ValueError("aerial must contain finite values")
    if np.any(aerial_array < 0.0):
        raise ValueError("aerial intensity must be non-negative")
    if not np.isfinite(dose) or dose <= 0.0:
        raise ValueError("dose must be a positive finite value")
    if not np.isfinite(threshold) or threshold <= 0.0:
        raise ValueError("threshold must be a positive finite value")

    return dose * aerial_array > threshold


def dose_to_clear(intensity: float, threshold: float = 0.3) -> float:
    """Dose required to expose a pixel with the given normalized intensity."""
    if not np.isfinite(intensity) or intensity <= 0.0:
        raise ValueError("intensity must be a positive finite value")
    if not np.isfinite(threshold) or threshold <= 0.0:
        raise ValueError("threshold must be a positive finite value")
    return float(threshold / intensity)
