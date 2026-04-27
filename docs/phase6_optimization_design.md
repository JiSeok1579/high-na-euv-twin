# Phase 6 Optimization Design

## Scope

Phase 6 Part 01 added a study-grade source-mask optimization (SMO) MVP. Phase 6
Part 02 extends that loop with PMWO/OPC candidate families and row-wise 2-D EPE
maps. The implementation closes the simulator loop by evaluating:

- mask candidates,
- Phase 2 source shapes,
- OPC bias candidates,
- pupil and wavefront candidates,
- dose candidates,
- Phase 5 stochastic LWR budget penalties.

The optimizer is deterministic grid search. This is intentionally simpler than
industrial SMO, PMWO, OPC, or ILT, but it gives the project a complete
target-to-candidate optimization loop with measurable loss components.

## Objective

The MVP objective is:

```text
loss = w_cd * CD_error
     + w_epe * EPE_error
     + w_lwr * LWR_fraction
     + w_dose * dose_error
```

Definitions:

- `CD_error = abs(printed_cd - target_cd) / target_cd`
- `EPE_error = mean_abs_edge_error / target_cd`
- `LWR_fraction = phase5_lwr_budget / target_cd`
- `dose_error = (dose - 1)^2`

The LWR term calls `lwr_decomposition_budget()` from `src/resist_stochastic.py`,
so Phase 6 directly reuses the Phase 5 stochastic resist model.

## Source Variable Connection

Each candidate evaluation runs:

```text
mask candidate -> Kirchhoff field
source shape -> partial_coherent_aerial_image()
dose -> threshold_resist()
printed line -> CD/EPE/LWR objective
```

This connects the Phase 2 source-shape API to the Phase 6 objective. The current
MVP supports point and sampled source shapes such as annular, dipole, quadrupole,
or freeform JSON-loaded sources.

## PMWO / OPC Extension

Phase 6 Part 02 adds `src/pmwo.py`:

- `opc_bias_mask_candidates()` converts mask-bias values into binary line-space
  mask candidates.
- `wavefront_zernike_candidates()` sweeps one Zernike coefficient in waves.
- `pupil_obscuration_candidates()` sweeps central-obscuration ratio.
- `edge_placement_error_map_2d()` returns row-wise target-vs-print EPE maps.
- `pmwo_grid_search()` evaluates mask, source, pupil/wavefront, and dose
  combinations with the same weighted objective.

The PMWO loss uses the same CD/LWR/dose terms as Part 01, but replaces the
center-line EPE term with the mean absolute value from the 2-D EPE map.

## Implemented APIs

- `SMOObjectiveWeights`
- `MaskCandidate`
- `SMOCandidateMetrics`
- `SMOCandidateEvaluation`
- `SMOResult`
- `weighted_smo_loss()`
- `line_space_mask_candidates()`
- `evaluate_smo_candidate()`
- `fast_smo_grid_search()`
- `opc_bias_mask_candidates()`
- `wavefront_zernike_candidates()`
- `pupil_obscuration_candidates()`
- `edge_placement_error_map_2d()`
- `pmwo_grid_search()`

## Simplifications

| ID | Simplification | Reason |
|---|---|---|
| P6-L1 | Deterministic grid search instead of gradient descent | Keeps the first SMO loop inspectable and stable. |
| P6-L2 | Line-space mask helper for the MVP demo | Enough to verify target-to-mask optimization before contact-array and ILT work. |
| P6-L3 | Threshold resist print check inside the objective | Reuses the existing end-to-end MVP path without adding a new resist abstraction. |
| P6-L4 | Scalar CD/LWR plus row-wise 2-D EPE objective | Enough to expose PMWO/OPC trends before full layout contour extraction. |
| P6-L5 | OPC represented as line-space mask bias | Keeps candidate generation deterministic while preserving the mask-bias control axis. |
| P6-L6 | Pupil/wavefront candidates are discrete sweeps | Replaces autograd PMWO with inspectable grid search for the study-grade gate. |

## Verification

The Phase 6 test suite checks:

- line-space mask candidate generation,
- improvement from a poor initial mask/source candidate,
- direct Phase 5 LWR budget connection,
- LWR weight influence on candidate ranking,
- OPC bias candidate generation,
- pupil and Zernike wavefront candidate generation,
- 2-D EPE zero-map and candidate ranking,
- input validation before optimization.

Current implementation files:

- `src/smo.py`
- `tests/phase6_smo.py`
- `src/pmwo.py`
- `tests/phase6_pmwo.py`
- `notebooks/5_SMO_PMWO.ipynb`
- `docs/phase6_optimization_design.md`
