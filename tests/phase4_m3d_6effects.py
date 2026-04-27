"""Phase 4 qualitative Mask 3D six-effect tests."""

from __future__ import annotations

import json

import numpy as np
import pytest

from src.aerial import aerial_image
from src.mask import MaskGrid, kirchhoff_mask, line_space_pattern
from src.mask_3d import (
    NI_HIGH_K,
    TABN_REFERENCE,
    AbsorberMaterial,
    Mask3DLookupEntry,
    Mask3DLookupTable,
    boundary_corrected_mask,
    compare_mask3d_aerial_images,
    compare_absorber_materials,
    default_absorber_materials,
    load_absorber_materials_json,
    load_mask3d_lookup_csv,
    load_mask3d_lookup_json,
    lookup_boundary_corrected_mask,
    lookup_mask3d_aerial_regression,
    lookup_mask3d_six_effects,
    mask3d_six_effects,
    screen_absorber_materials,
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


def test_boundary_corrected_mask_zero_cra_matches_kirchhoff():
    """Part 02 preserves the Phase 1 thin-mask field for zero CRA."""
    grid = MaskGrid(nx=64, ny=32, pixel_size=1e-9)
    pattern = line_space_pattern(grid, pitch_m=16e-9)

    result = boundary_corrected_mask(pattern, grid, 16e-9, chief_ray_angle_deg=0.0)

    assert np.allclose(result.corrected_field, kirchhoff_mask(pattern))
    assert np.count_nonzero(result.shadow_map) == 0
    assert np.allclose(result.phase_map_radians, 0.0)
    assert np.allclose(result.secondary_field, 0.0)


def test_boundary_corrected_mask_applies_asymmetric_shadowing():
    """The incident-side boundary attenuation changes with CRA sign."""
    grid = MaskGrid(nx=64, ny=32, pixel_size=1e-9)
    pattern = line_space_pattern(grid, pitch_m=16e-9)

    positive = boundary_corrected_mask(pattern, grid, 16e-9, chief_ray_angle_deg=6.0)
    negative = boundary_corrected_mask(pattern, grid, 16e-9, chief_ray_angle_deg=-6.0)

    assert np.count_nonzero(positive.shadow_map) > 0
    assert np.count_nonzero(negative.shadow_map) > 0
    assert not np.allclose(positive.shadow_map, negative.shadow_map)
    assert not np.allclose(positive.corrected_field, positive.baseline_field)


def test_boundary_phase_map_tracks_absorber_phase_strength():
    """Near-n=1 high-k material has a smaller boundary phase proxy."""
    grid = MaskGrid(nx=64, ny=32, pixel_size=1e-9)
    pattern = line_space_pattern(grid, pitch_m=16e-9)

    tabn = boundary_corrected_mask(pattern, grid, 16e-9, material=TABN_REFERENCE)
    high_k = boundary_corrected_mask(pattern, grid, 16e-9, material=NI_HIGH_K)

    assert np.max(np.abs(tabn.phase_map_radians)) > np.max(
        np.abs(high_k.phase_map_radians)
    )


def test_boundary_secondary_field_tracks_top_reflectivity():
    """The field-level ghost term increases with absorber top reflection."""
    grid = MaskGrid(nx=64, ny=32, pixel_size=1e-9)
    pattern = line_space_pattern(grid, pitch_m=16e-9)
    reflective = AbsorberMaterial("reflective", 0.94, 0.03, 60e-9, 0.05)
    muted = AbsorberMaterial("muted", 0.94, 0.03, 60e-9, 0.002)

    high = boundary_corrected_mask(pattern, grid, 16e-9, material=reflective)
    low = boundary_corrected_mask(pattern, grid, 16e-9, material=muted)

    assert np.linalg.norm(high.secondary_field) > np.linalg.norm(low.secondary_field)


def test_load_absorber_materials_json_accepts_measured_rows(tmp_path):
    """Measured n,k rows can replace starter constants without API changes."""
    material_path = tmp_path / "absorbers.json"
    material_path.write_text(
        json.dumps(
            {
                "materials": [
                    {
                        "name": "measured candidate",
                        "n": 0.97,
                        "k": 0.08,
                        "thickness_nm": 44.0,
                        "top_reflectivity": 0.011,
                        "source": "metrology",
                        "reference": "example measured row",
                        "measured": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    materials = load_absorber_materials_json(material_path)

    assert len(materials) == 1
    assert materials[0].name == "measured candidate"
    assert materials[0].thickness_m == pytest.approx(44e-9)
    assert materials[0].source == "metrology"
    assert materials[0].reference == "example measured row"
    assert materials[0].measured


def test_boundary_corrected_mask_rejects_grid_shape_mismatch():
    """Field-level correction requires explicit grid/mask consistency."""
    grid = MaskGrid(nx=64, ny=32, pixel_size=1e-9)
    pattern = line_space_pattern(grid, pitch_m=16e-9)
    wrong_grid = MaskGrid(nx=32, ny=32, pixel_size=1e-9)

    with pytest.raises(ValueError, match="pattern shape"):
        boundary_corrected_mask(pattern, wrong_grid, 16e-9)


def test_lookup_mask3d_effects_interpolates_pitch_rows():
    """Part 03 can replace reduced proxies with interpolated lookup rows."""
    table = Mask3DLookupTable(
        entries=(
            _lookup_entry("TaBN reference", 32e-9, best_focus_shift_m=4e-9),
            _lookup_entry("TaBN reference", 64e-9, best_focus_shift_m=12e-9),
        ),
        source="unit-test",
    )

    summary = lookup_mask3d_six_effects(
        48e-9,
        table,
        material=TABN_REFERENCE,
    )

    assert summary.best_focus_shift_m == pytest.approx(8e-9)
    assert summary.shadowing_loss_fraction == pytest.approx(0.15)


def test_lookup_mask3d_effects_falls_back_without_matching_rows():
    """Missing lookup rows do not block reduced-model smoke tests by default."""
    table = Mask3DLookupTable(entries=(_lookup_entry("other", 32e-9),))

    summary = lookup_mask3d_six_effects(32e-9, table, material=TABN_REFERENCE)
    reduced = mask3d_six_effects(32e-9, material=TABN_REFERENCE)

    assert summary.best_focus_shift_m == pytest.approx(reduced.best_focus_shift_m)


def test_screen_absorber_materials_prefers_lower_lookup_penalty():
    """Candidate screening uses imported table rows when they are available."""
    table = Mask3DLookupTable(
        entries=(
            _lookup_entry("TaBN reference", 32e-9, best_focus_shift_m=12e-9),
            _lookup_entry("Ni high-k candidate", 32e-9, best_focus_shift_m=2e-9),
        ),
        source="unit-test",
    )

    rows = screen_absorber_materials(
        32e-9,
        [TABN_REFERENCE, NI_HIGH_K],
        lookup_table=table,
    )

    assert rows[0].material.name == "Ni high-k candidate"
    assert rows[0].used_lookup
    assert rows[0].score < rows[1].score


def test_load_mask3d_lookup_json_rejects_empty_entries(tmp_path):
    """Lookup tables must be explicit so silent empty imports do not pass."""
    path = tmp_path / "lookup.json"
    path.write_text(json.dumps({"entries": []}), encoding="utf-8")

    with pytest.raises(ValueError, match="entries"):
        load_mask3d_lookup_json(path)


def test_load_mask3d_lookup_json_reads_pitch_nm_rows(tmp_path):
    """JSON lookup rows accept nm pitch values for paper table transcription."""
    path = tmp_path / "lookup.json"
    path.write_text(
        json.dumps(
            {
                "source": "example",
                "entries": [
                    {
                        "material_name": "TaBN reference",
                        "pitch_nm": 32.0,
                        "chief_ray_angle_deg": 6.0,
                        "orientation": "vertical",
                        "shadowing_loss_fraction": 0.12,
                        "orientation_cd_bias_m": 3e-10,
                        "telecentricity_error_mrad": 8.0,
                        "contrast_loss_fraction": 0.02,
                        "best_focus_shift_m": 6e-9,
                        "secondary_image_fraction": 0.001,
                        "phase_error_waves": 0.02,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    table = load_mask3d_lookup_json(path)

    assert table.source == "example"
    assert table.entries[0].pitch_m == pytest.approx(32e-9)


def test_load_mask3d_lookup_csv_reads_nanometer_columns(tmp_path):
    """Part 04 imports solver-export CSV rows with explicit nm length columns."""
    path = tmp_path / "rigorous_lookup.csv"
    path.write_text(
        "\n".join(
            [
                "material_name,pitch_nm,chief_ray_angle_deg,orientation,"
                "shadowing_loss_fraction,orientation_cd_bias_nm,"
                "telecentricity_error_mrad,contrast_loss_fraction,"
                "best_focus_shift_nm,secondary_image_fraction,phase_error_waves",
                "TaBN reference,32,6,vertical,0.11,0.42,7.5,0.03,5.0,0.002,0.018",
            ]
        ),
        encoding="utf-8",
    )

    table = load_mask3d_lookup_csv(path, source="rcwa-smoke-table")

    assert table.source == "rcwa-smoke-table"
    assert table.entries[0].pitch_m == pytest.approx(32e-9)
    assert table.entries[0].orientation_cd_bias_m == pytest.approx(0.42e-9)
    assert table.entries[0].best_focus_shift_m == pytest.approx(5.0e-9)


def test_lookup_boundary_corrected_mask_uses_imported_zero_effect_row():
    """Imported rigorous rows can override the reduced nonzero CRA proxy."""
    grid = MaskGrid(nx=64, ny=32, pixel_size=1e-9)
    pattern = line_space_pattern(grid, pitch_m=16e-9)
    table = Mask3DLookupTable(
        entries=(
            _lookup_entry(
                "TaBN reference",
                16e-9,
                shadowing_loss_fraction=0.0,
                orientation_cd_bias_m=0.0,
                telecentricity_error_mrad=0.0,
                contrast_loss_fraction=0.0,
                best_focus_shift_m=0.0,
                secondary_image_fraction=0.0,
                phase_error_waves=0.0,
            ),
        )
    )

    result = lookup_boundary_corrected_mask(
        pattern,
        grid,
        16e-9,
        table,
        chief_ray_angle_deg=6.0,
    )

    assert result.summary.as_effect_vector() == pytest.approx((0.0,) * 6)
    assert np.allclose(result.corrected_field, kirchhoff_mask(pattern))


def test_compare_mask3d_aerial_images_passes_normalized_reference():
    """Aerial regression compares normalized solver and reference images."""
    predicted = np.array([[0.0, 0.5, 1.0], [0.1, 0.6, 0.9]])
    reference = 3.0 * predicted

    result = compare_mask3d_aerial_images(predicted, reference)

    assert result.passed
    assert result.rmse == pytest.approx(0.0)
    assert np.max(result.predicted_intensity) == pytest.approx(1.0)


def test_compare_mask3d_aerial_images_fails_large_error():
    """Aerial regression fails when imported reference data is far away."""
    predicted = np.array([[0.0, 1.0], [0.0, 1.0]])
    reference = np.array([[1.0, 0.0], [1.0, 0.0]])

    result = compare_mask3d_aerial_images(
        predicted,
        reference,
        rmse_tolerance=0.1,
        max_abs_tolerance=0.2,
    )

    assert not result.passed
    assert result.max_abs_error == pytest.approx(1.0)


def test_lookup_mask3d_aerial_regression_closes_identical_reference():
    """Lookup-driven Mask 3D fields can be gated against reference aerial data."""
    grid = MaskGrid(nx=64, ny=32, pixel_size=1e-9)
    pattern = line_space_pattern(grid, pitch_m=16e-9)
    table = Mask3DLookupTable(entries=(_lookup_entry("TaBN reference", 16e-9),))
    boundary = lookup_boundary_corrected_mask(pattern, grid, 16e-9, table)
    reference, _ = aerial_image(boundary.corrected_field, grid)

    result = lookup_mask3d_aerial_regression(
        pattern,
        grid,
        16e-9,
        reference,
        table,
        rmse_tolerance=1e-12,
        max_abs_tolerance=1e-12,
    )

    assert result.passed
    assert result.wafer_grid is not None
    assert result.predicted_intensity.shape == reference.shape


def _lookup_entry(
    material_name: str,
    pitch_m: float,
    *,
    best_focus_shift_m: float = 8e-9,
    shadowing_loss_fraction: float = 0.15,
    orientation_cd_bias_m: float = 3e-10,
    telecentricity_error_mrad: float = 8.0,
    contrast_loss_fraction: float = 0.02,
    secondary_image_fraction: float = 0.001,
    phase_error_waves: float = 0.02,
) -> Mask3DLookupEntry:
    return Mask3DLookupEntry(
        material_name=material_name,
        pitch_m=pitch_m,
        chief_ray_angle_deg=6.0,
        orientation="vertical",
        shadowing_loss_fraction=shadowing_loss_fraction,
        orientation_cd_bias_m=orientation_cd_bias_m,
        telecentricity_error_mrad=telecentricity_error_mrad,
        contrast_loss_fraction=contrast_loss_fraction,
        best_focus_shift_m=best_focus_shift_m,
        secondary_image_fraction=secondary_image_fraction,
        phase_error_waves=phase_error_waves,
    )
