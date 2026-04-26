# Phase 3 — Defocus And DOF Groundwork

## 1. Scope

This document fixes the Phase 3 defocus sign convention before adding full
wafer topography and DOF sweeps. The current implementation covers constant
focus offset in the pupil phase. Spatially varying height maps, focus-exposure
matrices, and micro focus-drilling remain later Phase 3 work.

## 2. Defocus Sign Convention

| Quantity | Convention |
|----------|------------|
| `z = 0` | Nominal best-focus wafer plane |
| `defocus_m > 0` | Wafer surface is above best focus, toward projection optics |
| `defocus_m < 0` | Wafer surface is below best focus, away from projection optics |
| Pupil radius | `rho = 1` maps to the coherent cutoff `NA / lambda` |
| Phase equation | `phi_defocus(rho) = + pi * defocus_m * NA^2 / lambda * rho^2` |
| Pupil multiplier | `P -> P * exp(i * phi_defocus)` |

This is a project convention. It is chosen so that the sign is explicit and
testable before downstream resist, CD, and focus-exposure modules depend on it.
Changing it later requires a migration note and updated tests.

## 3. Numerical Invariants

- `defocus_m = 0` must preserve the Phase 1 aerial image exactly.
- `+defocus_m` and `-defocus_m` must produce complex-conjugate pupil phases.
- At `rho = 1`, the phase must equal `pi * defocus_m * NA^2 / lambda`.
- The phase term is applied after the annular pupil aperture and composes with
  Zernike wavefront phase by multiplication.

## 4. Current Limitations

| ID | Limitation | Deferred To |
|----|------------|-------------|
| P3-L1 | Only constant defocus is implemented; spatial `z(x, y)` maps are not yet propagated locally. | Phase 3 focus stack |
| P3-L2 | No DOF metric or `k2` fitting yet. | Phase 3 part 2 |
| P3-L3 | No micro focus-drilling depth slices. | Phase 3 part 3 |
| P3-L4 | Scalar coherent optics remains inherited from Phase 1. | Phase 2/4 |

## 5. Files

- `src/wafer_topo.py` — sign convention, height-to-defocus mapping, pupil phase helper
- `src/pupil.py` — `PupilSpec.defocus_m` integration
- `src/aerial.py` — aerial-plane pupil defocus integration
- `tests/phase3_DOF.py` — sign, conjugacy, edge phase, and zero-defocus regression tests

## 6. Exit Status

MT-006 is resolved by this design and the matching tests. Phase 3 is now open
for DOF focus-stack metrics, but KPI K3 is not complete until the simulated DOF
is compared against `k2 * lambda / NA^2`.
