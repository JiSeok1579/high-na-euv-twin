"""End-to-end MVP test: mask -> aerial/DOF -> threshold resist -> metrics."""

from __future__ import annotations

import pytest

from src import constants as C
from src.dof import focus_drilling_average
from src.mask import MaskGrid, kirchhoff_mask, line_space_pattern
from src.metrics import (
    critical_dimension,
    edge_positions,
    mean_absolute_epe,
    michelson_contrast,
    normalized_image_log_slope,
)
from src.pupil import PupilSpec
from src.resist_threshold import threshold_resist


def test_phase1_phase3_phase5_mvp_end_to_end_pipeline():
    """The MVP pipeline prints a resolved line/space target within 10% CD."""
    pitch_m = 80e-9
    grid = MaskGrid(nx=512, ny=64, pixel_size=1e-9)
    pattern = line_space_pattern(grid, pitch_m=pitch_m, duty_cycle=0.5)
    mask = kirchhoff_mask(pattern)

    aerial, wafer = focus_drilling_average(
        mask,
        grid,
        [0.0],
        pupil_spec=PupilSpec(grid_size=512, na=C.NA_HIGH, obscuration_ratio=0.0),
        anamorphic=False,
    )
    printed = threshold_resist(aerial, dose=1.0, threshold=0.2)

    cy = wafer.ny // 2
    target_clear = pattern[cy, :] == 0.0
    target_cd = critical_dimension(target_clear, grid.pixel_size)
    printed_cd = critical_dimension(printed[cy, :], wafer.pixel_x_m)
    target_edges = edge_positions(target_clear, grid.pixel_size)
    printed_edges = edge_positions(printed[cy, :], wafer.pixel_x_m)

    assert aerial.shape == printed.shape == pattern.shape
    assert target_cd == pytest.approx(0.5 * pitch_m)
    assert abs(printed_cd - target_cd) / target_cd <= 0.10
    assert mean_absolute_epe(target_edges, printed_edges) <= 0.10 * target_cd
    assert michelson_contrast(aerial[cy, :]) > 0.90
    assert normalized_image_log_slope(
        aerial[cy, :],
        wafer.pixel_x_m,
        target_cd,
        threshold=0.2,
    ) > 1.0
