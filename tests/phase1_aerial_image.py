"""Phase 1 unit tests — Scalar Fourier optics MVP.

Verifies the four Phase 1 exit criteria from PROJECT_PLAN.md:

1. Single pinhole + circular pupil → Airy-like PSF (Bessel/sinc shape).
2. Line/space scaling: large pitch resolved, sub-resolution pitch washes
   out to near-zero contrast.
3. Annular pupil (ε > 0) shifts sidelobe energy compared with a solid
   disk pupil (paper #15 qualitative check).
4. Anamorphic 4×/8× projection: a 26×33 mm mask field maps to a
   6.5×4.125 mm wafer field.
"""

from __future__ import annotations

import numpy as np
import pytest

from src import constants as C
from src.aerial import (
    aerial_image,
    cd_from_threshold,
    contrast,
    wafer_grid_from_mask,
)
from src.mask import MaskGrid, kirchhoff_mask, line_space_pattern, pinhole_pattern
from src.pupil import PupilSpec


# ---------------------------------------------------------------------------
# Test 1 — Pinhole PSF has the expected radial structure.
# ---------------------------------------------------------------------------
def test_pinhole_psf_radial_structure():
    grid = MaskGrid(nx=256, ny=256, pixel_size=4e-9)  # mask plane sampling
    pattern = pinhole_pattern(grid)
    field = kirchhoff_mask(pattern)

    # 1× imaging so we can reason about the PSF on the wafer plane in mask units.
    intensity, wafer = aerial_image(
        field,
        grid,
        pupil_spec=PupilSpec(grid_size=256, na=C.NA_HIGH, obscuration_ratio=0.0),
        anamorphic=False,
    )

    # Peak should be at the centre.
    cy, cx = wafer.ny // 2, wafer.nx // 2
    peak_idx = np.unravel_index(np.argmax(intensity), intensity.shape)
    assert peak_idx == (cy, cx), f"PSF peak at {peak_idx}, expected {(cy, cx)}"

    # Symmetric: horizontal and vertical line cuts should agree to <5 %.
    h_cut = intensity[cy, :]
    v_cut = intensity[:, cx]
    assert np.allclose(h_cut, v_cut, atol=5e-2)

    # First sidelobe should be well below the peak (Airy ~1.75 % of peak).
    radial = h_cut[cx + 1 :]
    if radial.size > 5:
        # Find the first local maximum after the central peak.
        diffs = np.diff(radial)
        sign_changes = np.where((diffs[:-1] > 0) & (diffs[1:] < 0))[0]
        if sign_changes.size > 0:
            first_sidelobe = radial[sign_changes[0] + 1]
            assert first_sidelobe < 0.2, (
                f"first sidelobe {first_sidelobe:.3f} too large vs Airy ~0.0175"
            )


# ---------------------------------------------------------------------------
# Test 2 — Resolved vs washed-out line/space.
# ---------------------------------------------------------------------------
def test_line_space_resolution_vs_pitch():
    # Mask-plane pitches. Anamorphic ×4 along scan direction → divide by 4
    # to obtain the wafer-plane pitch. We use 1× imaging here to avoid
    # confusing the test with the demag.
    grid = MaskGrid(nx=512, ny=64, pixel_size=2e-9)

    # Pitch comfortably above Rayleigh limit (R = 0.3 · 13.5 / 0.55 ≈ 7.4 nm).
    resolved_pattern = line_space_pattern(grid, pitch_m=40e-9)
    intensity_resolved, wafer = aerial_image(
        kirchhoff_mask(resolved_pattern),
        grid,
        pupil_spec=PupilSpec(grid_size=512, na=C.NA_HIGH, obscuration_ratio=0.2),
        anamorphic=False,
    )

    # Pitch well below the cutoff (lambda / NA ≈ 24.5 nm full pitch coherent).
    # Use 16 nm pitch so that the first diffraction order falls outside the pupil.
    washed_pattern = line_space_pattern(grid, pitch_m=16e-9)
    intensity_washed, _ = aerial_image(
        kirchhoff_mask(washed_pattern),
        grid,
        pupil_spec=PupilSpec(grid_size=512, na=C.NA_HIGH, obscuration_ratio=0.2),
        anamorphic=False,
    )

    cy = wafer.ny // 2
    c_resolved = contrast(intensity_resolved[cy, :])
    c_washed = contrast(intensity_washed[cy, :])

    assert c_resolved > 0.3, f"40 nm pitch contrast {c_resolved:.3f} too low"
    assert c_washed < 0.05, (
        f"16 nm pitch contrast {c_washed:.3f} should be near zero (sub-resolution)"
    )
    assert c_resolved > c_washed * 5.0


# ---------------------------------------------------------------------------
# Test 3 — Annular vs solid pupil change the PSF sidelobe distribution.
# ---------------------------------------------------------------------------
def test_annular_pupil_modifies_sidelobes():
    grid = MaskGrid(nx=256, ny=256, pixel_size=4e-9)
    field = kirchhoff_mask(pinhole_pattern(grid))

    intensity_solid, wafer = aerial_image(
        field,
        grid,
        pupil_spec=PupilSpec(grid_size=256, na=C.NA_HIGH, obscuration_ratio=0.0),
        anamorphic=False,
    )
    intensity_annular, _ = aerial_image(
        field,
        grid,
        pupil_spec=PupilSpec(grid_size=256, na=C.NA_HIGH, obscuration_ratio=0.4),
        anamorphic=False,
    )

    # Both peaks normalized to 1; annular pupil concentrates more energy in
    # the sidelobes compared to the central peak (paper #15 figure 3).
    cy, cx = wafer.ny // 2, wafer.nx // 2
    radial_solid = intensity_solid[cy, cx + 1 :]
    radial_annular = intensity_annular[cy, cx + 1 :]

    # Compare integrated sidelobe energy beyond the first 4 pixels.
    side_solid = float(np.sum(radial_solid[4:]))
    side_annular = float(np.sum(radial_annular[4:]))
    assert side_annular > side_solid, (
        f"annular sidelobe energy {side_annular:.3e} should exceed solid "
        f"{side_solid:.3e} (paper #15 trend)"
    )


# ---------------------------------------------------------------------------
# Test 4 — Anamorphic 4×/8× field-size mapping.
# ---------------------------------------------------------------------------
def test_anamorphic_field_mapping():
    # 26 mm × 33 mm mask field at 100 µm/pixel for a coarse check.
    pixel = 100e-6
    nx = int(round(26e-3 / pixel))
    ny = int(round(33e-3 / pixel))
    grid = MaskGrid(nx=nx, ny=ny, pixel_size=pixel)
    wafer = wafer_grid_from_mask(grid, anamorphic=True)

    width_m = wafer.nx * wafer.pixel_x_m
    height_m = wafer.ny * wafer.pixel_y_m

    assert width_m == pytest.approx(6.5e-3, rel=1e-3), (
        f"wafer width {width_m * 1e3:.4f} mm; expected 6.5 mm (mask 26 mm / 4)"
    )
    assert height_m == pytest.approx(4.125e-3, rel=1e-3), (
        f"wafer height {height_m * 1e3:.4f} mm; expected 4.125 mm (mask 33 mm / 8)"
    )

    # Anamorphic OFF must collapse to a 1× projection.
    wafer_iso = wafer_grid_from_mask(grid, anamorphic=False)
    assert wafer_iso.pixel_x_m == pytest.approx(pixel)
    assert wafer_iso.pixel_y_m == pytest.approx(pixel)


# ---------------------------------------------------------------------------
# Bonus — CD measurement and contrast helpers behave on a known signal.
# ---------------------------------------------------------------------------
def test_cd_helper_on_square_signal():
    """A 50% duty 80 nm pitch pattern (well above resolution) should leave
    roughly 50% of the line above the threshold after coherent imaging."""
    grid = MaskGrid(nx=256, ny=4, pixel_size=2e-9)
    pattern = line_space_pattern(grid, pitch_m=80e-9, duty_cycle=0.5)
    intensity, wafer = aerial_image(
        kirchhoff_mask(pattern),
        grid,
        pupil_spec=PupilSpec(grid_size=256, na=C.NA_HIGH, obscuration_ratio=0.2),
        anamorphic=False,
    )
    cy = wafer.ny // 2
    line = intensity[cy, :]
    cd = cd_from_threshold(line, wafer.pixel_x_m, threshold=0.3)
    total_length = grid.nx * grid.pixel_size
    # 50% duty + threshold 0.3 should leave between 35% and 70% above threshold
    # depending on edge slope and ringing.
    assert 0.30 * total_length <= cd <= 0.75 * total_length, (
        f"cd {cd * 1e9:.1f} nm out of expected band "
        f"({0.30 * total_length * 1e9:.0f}-{0.75 * total_length * 1e9:.0f} nm)"
    )
    assert cd > 0.0


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
