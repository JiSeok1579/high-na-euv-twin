"""Phase 4 qualitative Mask 3D six-effect tests."""

from __future__ import annotations

import pytest

from src.mask_3d import (
    NI_HIGH_K,
    TABN_REFERENCE,
    AbsorberMaterial,
    compare_absorber_materials,
    default_absorber_materials,
    mask3d_six_effects,
)


def test_cra_zero_collapses_to_thin_mask_baseline():
    """The paper #12 in-line projector mitigation removes all six effects."""
    summary = mask3d_six_effects(
        32e-9,
        chief_ray_angle_deg=0.0,
        orientation="vertical",
    )

    assert summary.as_effect_vector() == pytest.approx((0.0,) * 6)
    assert summary.phase_error_waves == pytest.approx(0.0)


def test_asymmetric_shadowing_increases_with_chief_ray_angle():
    """Effect 1: oblique incidence increases absorber shadowing."""
    low = mask3d_six_effects(32e-9, chief_ray_angle_deg=3.0)
    high = mask3d_six_effects(32e-9, chief_ray_angle_deg=6.0)

    assert high.shadowing_loss_fraction > low.shadowing_loss_fraction > 0.0


def test_orientation_dependent_cd_bias_changes_sign():
    """Effect 2: horizontal and vertical features carry opposite CD bias signs."""
    vertical = mask3d_six_effects(32e-9, orientation="vertical")
    horizontal = mask3d_six_effects(32e-9, orientation="horizontal")

    assert vertical.orientation_cd_bias_m > 0.0
    assert horizontal.orientation_cd_bias_m < 0.0
    assert abs(vertical.orientation_cd_bias_m) == pytest.approx(
        abs(horizontal.orientation_cd_bias_m)
    )


def test_telecentricity_error_is_pitch_dependent():
    """Effect 3: smaller pitches receive a larger qualitative CRA error."""
    dense = mask3d_six_effects(28e-9)
    relaxed = mask3d_six_effects(64e-9)

    assert dense.telecentricity_error_mrad > relaxed.telecentricity_error_mrad > 0.0


def test_contrast_loss_tracks_absorber_phase_strength():
    """Effect 4: near-n=1 high-k absorbers reduce destructive interference."""
    tabn = mask3d_six_effects(32e-9, material=TABN_REFERENCE)
    high_k = mask3d_six_effects(32e-9, material=NI_HIGH_K)

    assert tabn.contrast_loss_fraction > high_k.contrast_loss_fraction > 0.0


def test_best_focus_shift_reduces_for_high_k_material():
    """Effect 5: high-k near-n=1 absorber lowers the BF shift proxy."""
    tabn = mask3d_six_effects(32e-9, material=TABN_REFERENCE)
    high_k = mask3d_six_effects(32e-9, material=NI_HIGH_K)

    assert tabn.best_focus_shift_m > high_k.best_focus_shift_m > 0.0


def test_secondary_images_scale_with_top_reflection():
    """Effect 6: absorber top reflection creates a ghost-image proxy."""
    reflective = AbsorberMaterial(
        name="reflective test absorber",
        n=TABN_REFERENCE.n,
        k=TABN_REFERENCE.k,
        thickness_m=TABN_REFERENCE.thickness_m,
        top_reflectivity=0.04,
    )
    muted = AbsorberMaterial(
        name="muted test absorber",
        n=TABN_REFERENCE.n,
        k=TABN_REFERENCE.k,
        thickness_m=TABN_REFERENCE.thickness_m,
        top_reflectivity=0.005,
    )

    assert (
        mask3d_six_effects(32e-9, material=reflective).secondary_image_fraction
        > mask3d_six_effects(32e-9, material=muted).secondary_image_fraction
        > 0.0
    )


def test_absorber_library_comparison_is_stable():
    """The starter material library provides deterministic Phase 4 rows."""
    materials = default_absorber_materials()
    rows = compare_absorber_materials(32e-9, materials)

    assert [row.material.name for row in rows] == [material.name for material in materials]
    assert len(rows) == 3


def test_mask3d_input_validation():
    """Invalid Phase 4 parameters fail before they feed SMO loops."""
    with pytest.raises(ValueError, match="pitch_m"):
        mask3d_six_effects(0.0)
    with pytest.raises(ValueError, match="orientation"):
        mask3d_six_effects(32e-9, orientation="diagonal")
    with pytest.raises(ValueError, match="materials"):
        compare_absorber_materials(32e-9, ())
