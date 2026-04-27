"""Phase 6 Part 02 tests for PMWO/OPC and 2-D EPE maps."""

from __future__ import annotations

import numpy as np
import pytest

from src import constants as C
from src.illuminator import annular_source
from src.mask import MaskGrid, line_space_pattern
from src.pmwo import (
    edge_placement_error_map_2d,
    opc_bias_mask_candidates,
    pmwo_grid_search,
    pupil_obscuration_candidates,
    wavefront_zernike_candidates,
)
from src.pupil import PupilSpec
from src.smo import SMOObjectiveWeights


def _pmwo_fixture():
    grid = MaskGrid(nx=256, ny=64, pixel_size=2e-9)
    pitch_m = 40e-9
    target_pattern = line_space_pattern(grid, pitch_m=pitch_m, duty_cycle=0.5)
    target_printed = target_pattern == 0.0
    pupil = PupilSpec(grid_size=256, na=C.NA_HIGH, obscuration_ratio=0.0)
    source = annular_source(0.2, 0.7, num_radial=1, num_azimuthal=4, name="annular")
    return grid, pitch_m, target_printed, pupil, source


def test_opc_bias_mask_candidates_shift_line_space_duty():
    """OPC bias candidates expose a mask-family axis for Phase 6 sweeps."""
    grid, pitch_m, _, _, _ = _pmwo_fixture()
    candidates = opc_bias_mask_candidates(grid, pitch_m, [-4e-9, 0.0, 4e-9])

    assert [candidate.name for candidate in candidates] == [
        "opc_bias_-4.0nm",
        "opc_bias_+0.0nm",
        "opc_bias_+4.0nm",
    ]
    absorber_fractions = [float(np.mean(candidate.pattern)) for candidate in candidates]
    assert absorber_fractions == sorted(absorber_fractions)
    assert absorber_fractions[1] == pytest.approx(0.5, abs=0.02)


def test_edge_placement_error_map_is_zero_for_identical_prints():
    """The 2-D EPE map is a true zero map for identical target/print images."""
    grid, _, target_printed, _, _ = _pmwo_fixture()

    epe_map = edge_placement_error_map_2d(
        target_printed,
        target_printed.copy(),
        grid.pixel_size,
    )

    assert epe_map.edge_error_m.shape[0] == grid.ny
    assert epe_map.edges_per_row > 0
    assert epe_map.mean_abs_epe_m == pytest.approx(0.0)
    assert epe_map.max_abs_epe_m == pytest.approx(0.0)
    assert epe_map.edge_count_mismatch_fraction == pytest.approx(0.0)


def test_wavefront_and_pupil_candidate_builders_preserve_base_spec():
    """PMWO candidate builders create explicit pupil and wavefront options."""
    _, _, _, pupil, _ = _pmwo_fixture()

    wavefronts = wavefront_zernike_candidates(pupil, (2, 0), [0.0, 0.05])
    pupils = pupil_obscuration_candidates(pupil, [0.0, 0.4])

    assert [candidate.name for candidate in wavefronts] == [
        "wavefront_clear",
        "zernike_2_0_+0.050waves",
    ]
    assert wavefronts[0].pupil_spec.zernike == {}
    assert wavefronts[1].pupil_spec.zernike[(2, 0)] == pytest.approx(0.05)
    assert [candidate.pupil_spec.obscuration_ratio for candidate in pupils] == [
        0.0,
        0.4,
    ]
    assert all(candidate.pupil_spec.na == pytest.approx(C.NA_HIGH) for candidate in pupils)


def test_pmwo_grid_search_improves_bad_initial_pupil_and_opc_candidate():
    """PMWO chooses the unbiased mask and clear pupil over a bad initial point."""
    grid, pitch_m, target_printed, pupil, source = _pmwo_fixture()
    masks = opc_bias_mask_candidates(grid, pitch_m, [-4e-9, 0.0, 4e-9])
    pupils = pupil_obscuration_candidates(pupil, [0.8, 0.0])

    result = pmwo_grid_search(
        target_printed,
        grid,
        masks,
        [source],
        pupils,
        [1.0],
        weights=SMOObjectiveWeights(cd=2.0, epe=1.0, lwr=0.0),
    )

    assert result.converged
    assert result.improvement_fraction > 0.95
    assert result.best.mask_candidate.name == "opc_bias_+0.0nm"
    assert result.best.pupil_candidate.name == "obscuration_0.00"
    assert result.best.epe_map.mean_abs_epe_m < result.initial.epe_map.mean_abs_epe_m
    assert len(result.history) == len(masks) * len(pupils)


def test_pmwo_rejects_invalid_inputs():
    """Invalid PMWO grids fail before they enter expensive image evaluation."""
    grid, pitch_m, target_printed, pupil, source = _pmwo_fixture()
    masks = opc_bias_mask_candidates(grid, pitch_m, [0.0])
    pupils = pupil_obscuration_candidates(pupil, [0.0])

    with pytest.raises(ValueError, match="pupil_candidates"):
        pmwo_grid_search(target_printed, grid, masks, [source], (), [1.0])
    with pytest.raises(ValueError, match="dose_grid"):
        pmwo_grid_search(target_printed, grid, masks, [source], pupils, [0.0])
    with pytest.raises(ValueError, match="outside"):
        opc_bias_mask_candidates(grid, pitch_m, [30e-9])
