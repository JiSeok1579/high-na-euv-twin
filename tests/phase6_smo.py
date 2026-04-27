"""Phase 6 tests for the study-grade SMO MVP."""

from __future__ import annotations

import numpy as np
import pytest

from src import constants as C
from src.illuminator import annular_source, point_source
from src.mask import MaskGrid, line_space_pattern
from src.pupil import PupilSpec
from src.smo import (
    SMOObjectiveWeights,
    evaluate_smo_candidate,
    fast_smo_grid_search,
    line_space_mask_candidates,
    weighted_smo_loss,
)


def _phase6_fixture():
    grid = MaskGrid(nx=256, ny=64, pixel_size=2e-9)
    pitch_m = 40e-9
    target_mask = line_space_pattern(grid, pitch_m=pitch_m, duty_cycle=0.5)
    target_printed = target_mask == 0.0
    pupil = PupilSpec(grid_size=256, na=C.NA_HIGH, obscuration_ratio=0.0)
    return grid, pitch_m, target_printed, pupil


def test_line_space_mask_candidates_build_binary_grid():
    """The Phase 6 MVP starts from explicit binary mask candidates."""
    grid, pitch_m, _, _ = _phase6_fixture()
    candidates = line_space_mask_candidates(grid, pitch_m, [0.35, 0.5, 0.65])

    assert [candidate.name for candidate in candidates] == [
        "line_space_duty_0.350",
        "line_space_duty_0.500",
        "line_space_duty_0.650",
    ]
    assert all(candidate.pattern.shape == grid.shape() for candidate in candidates)
    assert all(set(np.unique(candidate.pattern)) <= {0.0, 1.0} for candidate in candidates)


def test_fast_smo_grid_search_improves_initial_candidate():
    """Grid-search SMO improves a poor initial mask/source candidate."""
    grid, pitch_m, target_printed, pupil = _phase6_fixture()
    candidates = line_space_mask_candidates(grid, pitch_m, [0.35, 0.5, 0.65])
    sources = (
        point_source(name="point"),
        annular_source(0.2, 0.7, num_radial=1, num_azimuthal=4, name="annular"),
    )

    result = fast_smo_grid_search(
        target_printed,
        grid,
        candidates,
        sources,
        [1.0],
        pupil_spec=pupil,
        weights=SMOObjectiveWeights(cd=2.0, epe=1.0, lwr=0.0),
    )

    assert result.converged
    assert result.improvement_fraction > 0.9
    assert result.best.metrics.loss < result.initial.metrics.loss
    assert result.best.mask_candidate.name == "line_space_duty_0.500"
    assert result.best.source_shape.name == "annular"
    assert len(result.history) == len(candidates) * len(sources)


def test_evaluate_smo_candidate_connects_phase5_lwr_budget():
    """Candidate metrics include the Phase 5 stochastic LWR penalty term."""
    grid, pitch_m, target_printed, pupil = _phase6_fixture()
    candidate = line_space_mask_candidates(grid, pitch_m, [0.5])[0]

    evaluation = evaluate_smo_candidate(
        target_printed,
        grid,
        candidate,
        annular_source(0.2, 0.7, num_radial=1, num_azimuthal=4, name="annular"),
        dose=1.0,
        pupil_spec=pupil,
        weights=SMOObjectiveWeights(cd=0.0, epe=0.0, lwr=1.0),
    )

    assert evaluation.metrics.printed_cd_m == pytest.approx(
        evaluation.metrics.target_cd_m
    )
    assert evaluation.metrics.mean_epe_m == pytest.approx(0.0)
    assert evaluation.metrics.lwr_m > 0.0
    assert evaluation.metrics.loss == pytest.approx(evaluation.metrics.lwr_fraction)


def test_lwr_weight_changes_candidate_ranking():
    """The weighted objective can trade CD/EPE error against LWR."""
    no_lwr = SMOObjectiveWeights(cd=1.0, epe=1.0, lwr=0.0)
    high_lwr = SMOObjectiveWeights(cd=1.0, epe=1.0, lwr=5.0)

    sharper_but_noisy = dict(
        cd_error_fraction=0.01,
        epe_error_fraction=0.01,
        lwr_fraction=0.40,
        dose_error_fraction=0.0,
    )
    smoother_but_biased = dict(
        cd_error_fraction=0.08,
        epe_error_fraction=0.07,
        lwr_fraction=0.02,
        dose_error_fraction=0.0,
    )

    assert weighted_smo_loss(**sharper_but_noisy, weights=no_lwr) < weighted_smo_loss(
        **smoother_but_biased,
        weights=no_lwr,
    )
    assert weighted_smo_loss(**smoother_but_biased, weights=high_lwr) < weighted_smo_loss(
        **sharper_but_noisy,
        weights=high_lwr,
    )


def test_smo_rejects_invalid_inputs():
    """SMO fails before invalid candidates enter optimization loops."""
    grid, pitch_m, target_printed, pupil = _phase6_fixture()
    candidates = line_space_mask_candidates(grid, pitch_m, [0.5])

    with pytest.raises(ValueError, match="source_shapes"):
        fast_smo_grid_search(target_printed, grid, candidates, (), [1.0], pupil_spec=pupil)
    with pytest.raises(ValueError, match="dose_grid"):
        fast_smo_grid_search(
            target_printed,
            grid,
            candidates,
            [point_source()],
            [0.0],
            pupil_spec=pupil,
        )
    with pytest.raises(ValueError, match="target_printed shape"):
        evaluate_smo_candidate(
            target_printed[:, :-1],
            grid,
            candidates[0],
            point_source(),
            pupil_spec=pupil,
        )
