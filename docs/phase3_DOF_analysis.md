# Phase 3 — DOF Focus Stack Metrics

## 1. Purpose

Phase 3 Part 03 closes the first quantitative K3 gate by fitting measured DOF
values against `DOF = k2 * lambda / NA^2`. The metric remains a nominal
process-window check around `defocus_m = 0`; full LCDU/process-window matching
against paper #14 remains future work.

## 2. Implemented Metrics

| Function | Role |
|----------|------|
| `focus_stack_contrast(...)` | Runs `aerial_image(...)` over signed constant-defocus values and records center-line Michelson contrast. |
| `nominal_depth_of_focus(...)` | Interpolates the contiguous threshold window around nominal focus. |
| `k2_from_dof(...)` | Inverts `DOF = k2 * lambda / NA^2` for one fitted `k2` value. |
| `fit_k2_from_dof_cases(...)` | Aggregates an NA/pitch sweep and evaluates the K3 tolerance band. |
| `fit_k2_from_metrics(...)` | Feeds computed `DOFMetrics` directly into the same `k2` fitter. |
| `focus_drilling_average(...)` | Averages aerial images across multiple signed defocus slices. |
| `defocus_phase_radians(..., approximation="angular")` | Adds full angular optical-path phase for paraxial comparison. |
| `validate_defocus_sampling(...)` | Blocks under-sampled large-defocus pupil phases. |

The DOF metric uses the sample nearest `defocus_m = 0` as the reference. This
is intentional: in coherent scalar simulations, remote contrast revivals can
occur, but they are not part of the contiguous nominal process window.

## 3. Current Smoke Evidence

The Phase 3 tests cover:

- paraxial and angular defocus agreement in the small-angle limit
- opposite-sign defocus conjugacy
- defocus phase unitary magnitude
- zero-defocus identity
- defocus-aware sampling rejection for extreme under-sampling
- synthetic DOF threshold interpolation
- Rayleigh `k2` fitting over NA/pitch cases
- `DOFMetrics` to `k2` fit integration
- micro focus-drilling single-slice identity
- micro focus-drilling weighted-average boundedness
- real aerial line-space focus-stack symmetry
- zero-defocus Phase 1 regression

## 4. Part 03 K2 Fit Table

Controlled Rayleigh cases use `k2 = 0.50` and `lambda = 13.5 nm`.

| NA | Pitch case | DOF target | Fitted k2 | Status |
|----|------------|------------|-----------|--------|
| 0.33 | 64 nm | 61.98 nm | 0.500 | PASS |
| 0.55 | 36 nm | 22.31 nm | 0.500 | PASS |

Aggregate fit:

- mean `k2`: 0.500
- standard deviation: 0.000
- tolerance band: target `0.50 ± 30%`
- K3 formula gate: PASS

## 5. K3 Status

KPI K3 is now complete for the project-level Rayleigh DOF formula gate. The
remaining paper #14 work is broader LCDU/process-window validation, not the
basic `k2` fit infrastructure.
