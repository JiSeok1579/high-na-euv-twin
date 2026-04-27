"""Phase 2 tests for source-shape and partial-coherence illumination."""

from __future__ import annotations

import json

import numpy as np
import pytest

from src import constants as C
from src.aerial import aerial_image
from src.illuminator import (
    SourcePoint,
    annular_source,
    dipole_source,
    freeform_source,
    load_source_shape_json,
    load_source_shape_library_json,
    partial_coherent_aerial_image,
    point_source,
    quadrupole_source,
)
from src.mask import MaskGrid, kirchhoff_mask, line_space_pattern
from src.pupil import PupilSpec


def test_point_source_matches_phase1_coherent_aerial():
    """The on-axis Phase 2 wrapper preserves the Phase 1 coherent baseline."""
    grid = MaskGrid(nx=256, ny=64, pixel_size=2e-9)
    field = kirchhoff_mask(line_space_pattern(grid, pitch_m=40e-9))
    pupil = PupilSpec(grid_size=256, na=C.NA_HIGH, obscuration_ratio=0.0)

    coherent, wafer = aerial_image(field, grid, pupil, anamorphic=False)
    result = partial_coherent_aerial_image(
        field,
        grid,
        point_source(),
        pupil,
        anamorphic=False,
    )

    assert result.wafer_grid == wafer
    assert result.normalized_weights == pytest.approx((1.0,))
    assert np.allclose(result.intensity, coherent, atol=1e-12)


def test_freeform_source_normalizes_weights_and_parses_angle_points():
    """Freeform input supports tuples and sigma/angle mapping rows."""
    source = freeform_source(
        (
            (0.0, 0.0, 2.0),
            {"sigma": 0.5, "angle_deg": 90.0, "weight": 1.0},
        ),
        name="weighted_freeform",
    )

    assert source.name == "weighted_freeform"
    assert source.normalized_weights() == pytest.approx((2.0 / 3.0, 1.0 / 3.0))
    assert source.points[1].sigma_x == pytest.approx(0.0, abs=1e-15)
    assert source.points[1].sigma_y == pytest.approx(0.5)


def test_dipole_and_quadrupole_source_geometry():
    """Built-in source shapes place poles at deterministic sigma positions."""
    dipole = dipole_source(0.65, orientation="x")
    quadrupole = quadrupole_source(0.5)
    diagonal = quadrupole_source(0.6, diagonal=True)

    assert [(p.sigma_x, p.sigma_y) for p in dipole.points] == pytest.approx(
        [(-0.65, 0.0), (0.65, 0.0)]
    )
    assert [point.radius for point in quadrupole.points] == pytest.approx([0.5] * 4)
    assert all(point.radius == pytest.approx(0.6) for point in diagonal.points)


def test_annular_source_samples_requested_sigma_band():
    """Annular sampling stays inside the requested band and uses positive weights."""
    source = annular_source(0.3, 0.8, num_radial=2, num_azimuthal=8)
    radii = np.array([point.radius for point in source.points])
    weights = np.array([point.weight for point in source.points])

    assert len(source.points) == 16
    assert float(np.min(radii)) >= 0.3
    assert float(np.max(radii)) <= 0.8
    assert np.all(weights > 0.0)
    assert sum(source.normalized_weights()) == pytest.approx(1.0)


def test_off_axis_source_changes_resolved_line_image():
    """A nonzero source point must exercise a distinct aerial-image branch."""
    grid = MaskGrid(nx=256, ny=64, pixel_size=2e-9)
    field = kirchhoff_mask(line_space_pattern(grid, pitch_m=40e-9))
    pupil = PupilSpec(grid_size=256, na=C.NA_HIGH, obscuration_ratio=0.0)

    on_axis, _ = aerial_image(field, grid, pupil, anamorphic=False)
    off_axis, _ = aerial_image(
        field,
        grid,
        pupil,
        anamorphic=False,
        source_sigma_x=0.4,
    )

    assert not np.allclose(off_axis, on_axis)
    assert np.max(np.abs(off_axis - on_axis)) > 0.05


def test_partial_coherence_annular_returns_normalized_finite_image():
    """Annular partial coherence returns finite normalized summed intensity."""
    grid = MaskGrid(nx=256, ny=64, pixel_size=2e-9)
    field = kirchhoff_mask(line_space_pattern(grid, pitch_m=40e-9))
    pupil = PupilSpec(grid_size=256, na=C.NA_HIGH, obscuration_ratio=0.0)

    point = partial_coherent_aerial_image(
        field,
        grid,
        point_source(),
        pupil,
        anamorphic=False,
    )
    annular = partial_coherent_aerial_image(
        field,
        grid,
        annular_source(0.2, 0.7, num_radial=1, num_azimuthal=4),
        pupil,
        anamorphic=False,
        return_point_images=True,
    )

    assert annular.intensity.shape == grid.shape()
    assert np.all(np.isfinite(annular.intensity))
    assert float(np.max(annular.intensity)) == pytest.approx(1.0)
    assert len(annular.point_images) == 4
    assert not np.allclose(annular.intensity, point.intensity)


def test_load_source_shape_json_accepts_single_shape(tmp_path):
    """Measured or hand-authored source shapes can enter through JSON."""
    source_path = tmp_path / "source.json"
    source_path.write_text(
        json.dumps(
            {
                "name": "json_dipole_x",
                "points": [
                    {"sigma_x": -0.55, "sigma_y": 0.0, "weight": 1.0},
                    {"sigma_x": 0.55, "sigma_y": 0.0, "weight": 1.0},
                ],
            }
        ),
        encoding="utf-8",
    )

    source = load_source_shape_json(source_path)

    assert source.name == "json_dipole_x"
    assert len(source.points) == 2
    assert source.normalized_weights() == pytest.approx((0.5, 0.5))


def test_load_source_shape_library_json_accepts_multiple_shapes(tmp_path):
    """A source-shape library file can feed notebooks and future SMO sweeps."""
    library_path = tmp_path / "sources.json"
    library_path.write_text(
        json.dumps(
            {
                "source_shapes": [
                    {"name": "point", "points": [{"sigma_x": 0.0, "sigma_y": 0.0}]},
                    {
                        "name": "quad",
                        "points": [
                            {"sigma_x": -0.4, "sigma_y": 0.0},
                            {"sigma_x": 0.4, "sigma_y": 0.0},
                            {"sigma_x": 0.0, "sigma_y": -0.4},
                            {"sigma_x": 0.0, "sigma_y": 0.4},
                        ],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    shapes = load_source_shape_library_json(library_path)

    assert [shape.name for shape in shapes] == ["point", "quad"]
    assert [len(shape.points) for shape in shapes] == [1, 4]


def test_source_shape_input_validation():
    """Invalid source data fails before it can enter image integration."""
    with pytest.raises(ValueError, match="at least one"):
        freeform_source(())
    with pytest.raises(ValueError, match="radius"):
        SourcePoint(0.8, 0.8)
    with pytest.raises(ValueError, match="weight"):
        SourcePoint(0.0, 0.0, 0.0)
    with pytest.raises(ValueError, match="orientation"):
        dipole_source(0.5, orientation="diagonal")
    with pytest.raises(ValueError, match="inner_sigma"):
        annular_source(0.8, 0.4)
