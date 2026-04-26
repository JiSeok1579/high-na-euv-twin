"""Zernike wavefront helpers shared by pupil and imaging modules."""

from __future__ import annotations

from math import factorial
from typing import Mapping

import numpy as np


ZernikeCoeffs = Mapping[tuple[int, int], float]


def zernike_polynomial(
    n: int,
    m: int,
    rho: np.ndarray,
    theta: np.ndarray,
) -> np.ndarray:
    """Compute a single Noll-style Zernike polynomial on `(rho, theta)`.

    Parameters
    ----------
    n, m : int
        Zernike radial and azimuthal indices.
    rho, theta : ndarray
        Normalized pupil radius and azimuth coordinates.

    Returns
    -------
    ndarray
        Zernike polynomial values, zeroed outside `rho > 1`.
    """
    abs_m = abs(m)
    if (n - abs_m) % 2 != 0 or n < abs_m:
        raise ValueError(f"invalid Zernike index n={n}, m={m}")

    radial = np.zeros_like(rho)
    for k in range((n - abs_m) // 2 + 1):
        coeff = (-1) ** k
        coeff *= factorial(n - k)
        coeff /= (
            factorial(k)
            * factorial((n + abs_m) // 2 - k)
            * factorial((n - abs_m) // 2 - k)
        )
        radial += coeff * rho ** (n - 2 * k)

    if m > 0:
        z = radial * np.cos(m * theta)
    elif m < 0:
        z = radial * np.sin(abs_m * theta)
    else:
        z = radial

    z[rho > 1.0] = 0.0
    return z


def wavefront(
    rho: np.ndarray,
    theta: np.ndarray,
    zernike: ZernikeCoeffs,
) -> np.ndarray:
    """Sum Zernike contributions into optical path difference in waves."""
    if not zernike:
        return np.zeros_like(rho)
    w = np.zeros_like(rho)
    for (n, m), coeff in zernike.items():
        w += coeff * zernike_polynomial(n, m, rho, theta)
    return w
