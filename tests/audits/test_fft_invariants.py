"""Numerical invariants for FFT-based optical imaging."""

from __future__ import annotations

import numpy as np
import pytest

from src import constants as C
from src.aerial import aerial_image, contrast
from src.mask import MaskGrid, kirchhoff_mask, line_space_pattern


def test_fft_parseval_round_trip():
    """NumPy FFT normalization should satisfy Parseval's theorem."""
    rng = np.random.default_rng(42)
    field = rng.normal(size=(32, 32)) + 1j * rng.normal(size=(32, 32))

    spectrum = np.fft.fft2(field)
    spatial_energy = float(np.sum(np.abs(field) ** 2))
    spectral_energy = float(np.sum(np.abs(spectrum) ** 2) / field.size)

    assert spectral_energy == pytest.approx(spatial_energy, rel=1e-12)


def test_fftshift_ifftshift_round_trip():
    """Frequency-origin shifts must be exactly reversible."""
    array = np.arange(33 * 34).reshape(33, 34)
    assert np.array_equal(np.fft.ifftshift(np.fft.fftshift(array)), array)


def test_pupil_cutoff_frequency_matches_na_scaling():
    """The coherent cutoff frequency scales linearly with NA."""
    na_low = 0.33
    na_high = 0.55
    cutoff_low = na_low / C.LAMBDA_EUV
    cutoff_high = na_high / C.LAMBDA_EUV

    assert cutoff_high / cutoff_low == pytest.approx(na_high / na_low)


def test_grid_refinement_converges_for_resolved_pitch():
    """Resolved line-space contrast should be stable under grid refinement."""
    contrasts = []
    for nx in (256, 512):
        grid = MaskGrid(nx=nx, ny=64, pixel_size=2e-9)
        pattern = line_space_pattern(grid, pitch_m=40e-9)
        intensity, wafer = aerial_image(
            kirchhoff_mask(pattern),
            grid,
            anamorphic=False,
        )
        contrasts.append(contrast(intensity[wafer.ny // 2, :]))

    assert contrasts[0] > 0.3
    assert contrasts[1] > 0.3
    assert abs(contrasts[1] - contrasts[0]) < 0.15
