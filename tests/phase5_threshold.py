"""Phase 5 MVP tests for threshold resist and lithography metrics."""

from __future__ import annotations

import numpy as np
import pytest

from src import constants as C
from src.aerial import aerial_image
from src.mask import MaskGrid, kirchhoff_mask, line_space_pattern
from src.metrics import (
    critical_dimension,
    dose_cd_curve,
    edge_positions,
    mean_absolute_epe,
)
from src.pupil import PupilSpec
from src.resist_threshold import dose_to_clear, threshold_resist


def test_threshold_resist_applies_dose_threshold():
    """Exposure is exactly `dose * I > threshold`."""
    aerial = np.array([[0.1, 0.3, 0.6], [0.2, 0.5, 0.9]])
    exposed = threshold_resist(aerial, dose=2.0, threshold=0.8)

    expected = np.array([[False, False, True], [False, True, True]])
    assert exposed.dtype == np.bool_
    assert np.array_equal(exposed, expected)
    assert dose_to_clear(0.5, threshold=0.8) == pytest.approx(1.6)


def test_threshold_resist_rejects_invalid_inputs():
    """The MVP model should fail early on non-physical dose/intensity."""
    with pytest.raises(ValueError, match="non-negative"):
        threshold_resist(np.array([-0.1, 0.2]))
    with pytest.raises(ValueError, match="dose"):
        threshold_resist(np.array([0.1, 0.2]), dose=0.0)
    with pytest.raises(ValueError, match="threshold"):
        threshold_resist(np.array([0.1, 0.2]), threshold=0.0)


def test_critical_dimension_measures_mean_interior_runs():
    """CD is the mean width of full foreground runs in a printed line."""
    line = np.array(
        [False, False, True, True, True, False, True, True, False],
        dtype=bool,
    )

    assert critical_dimension(line, 2e-9) == pytest.approx(5e-9)


def test_edge_placement_error_matches_binary_edges():
    """EPE compares printed and target transition locations."""
    target = np.array([False, False, True, True, False, False])
    printed = np.array([False, True, True, True, False, False])

    target_edges = edge_positions(target, 1e-9)
    printed_edges = edge_positions(printed, 1e-9)

    assert np.allclose(target_edges, [2e-9, 4e-9])
    assert np.allclose(printed_edges, [1e-9, 4e-9])
    assert mean_absolute_epe(target_edges, printed_edges) == pytest.approx(0.5e-9)


def test_dose_cd_curve_is_monotonic_for_exposed_cd():
    """Higher dose must not shrink the exposed CD in threshold resist."""
    aerial_line = np.array([0.0, 0.2, 0.5, 0.8, 1.0, 0.8, 0.5, 0.2, 0.0])
    curve = dose_cd_curve(aerial_line, 1e-9, [0.8, 1.0, 1.5], threshold=0.45)
    cds = [point.cd_m for point in curve]

    assert [point.dose for point in curve] == [0.8, 1.0, 1.5]
    assert cds == sorted(cds)
    assert cds[0] < cds[-1]


def test_line_space_target_cd_within_ten_percent():
    """A resolved line/space aerial image prints the target clear CD."""
    pitch_m = 80e-9
    grid = MaskGrid(nx=512, ny=64, pixel_size=1e-9)
    pattern = line_space_pattern(grid, pitch_m=pitch_m, duty_cycle=0.5)
    intensity, wafer = aerial_image(
        kirchhoff_mask(pattern),
        grid,
        pupil_spec=PupilSpec(grid_size=512, na=C.NA_HIGH, obscuration_ratio=0.0),
        anamorphic=False,
    )

    cy = wafer.ny // 2
    target_clear = pattern[cy, :] == 0.0
    printed = threshold_resist(intensity, dose=1.0, threshold=0.2)

    target_cd = critical_dimension(target_clear, grid.pixel_size)
    printed_cd = critical_dimension(printed[cy, :], wafer.pixel_x_m)

    assert target_cd == pytest.approx(0.5 * pitch_m)
    assert abs(printed_cd - target_cd) / target_cd <= 0.10
