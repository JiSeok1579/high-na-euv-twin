# Phase 3 — Defocus And DOF Groundwork

## 1. Scope

This document fixes the Phase 3 defocus sign convention and records the first
nominal-focus DOF metric. The current implementation covers constant focus
offset in the pupil phase, focus-stack contrast metrics, `k2` fitting, and a
micro focus-drilling depth-slice average. Spatially varying height maps and
focus-exposure matrices remain later Phase 3 work.

## 2. Defocus Sign Convention

| Quantity | Convention |
|----------|------------|
| `z = 0` | Nominal best-focus wafer plane |
| `defocus_m > 0` | Wafer surface is above best focus, toward projection optics |
| `defocus_m < 0` | Wafer surface is below best focus, away from projection optics |
| Pupil radius | `rho = 1` maps to the coherent cutoff `NA / lambda` |
| Paraxial phase equation | `phi_defocus(rho) = + pi * defocus_m * NA^2 / lambda * rho^2` |
| Angular phase equation | `phi_defocus(rho) = + 2pi * defocus_m / lambda * (1 - cos(theta))` |
| Pupil multiplier | `P -> P * exp(i * phi_defocus)` |

This is a project convention. It is chosen so that the sign is explicit and
testable before downstream resist, CD, and focus-exposure modules depend on it.
Changing it later requires a migration note and updated tests.

## 3. Numerical Invariants

- `defocus_m = 0` must preserve the Phase 1 aerial image exactly.
- `+defocus_m` and `-defocus_m` must produce complex-conjugate pupil phases.
- At `rho = 1`, the phase must equal `pi * defocus_m * NA^2 / lambda`.
- The angular optical-path option must reduce to the paraxial expression in
  the small-angle limit.
- The defocus phase multiplier must be unitary and zero defocus must be the
  identity multiplier.
- Large defocus values must pass the defocus-aware pupil sampling guard before
  FFT use.
- The phase term is applied after the annular pupil aperture and composes with
  Zernike wavefront phase by multiplication.
- Nominal DOF is measured around `defocus_m = 0`; remote coherent contrast
  revivals are not treated as process-window continuity.

## 4. Current Limitations

| ID | Limitation | Deferred To |
|----|------------|-------------|
| P3-L1 | Only constant defocus is implemented; spatial `z(x, y)` maps are not yet propagated locally. | Phase 3 topography map |
| P3-L2 | `k2` fitting exists for nominal DOF cases; paper #14 LCDU/process-window matching is not yet implemented. | Phase 3 paper #14 validation |
| P3-L3 | Micro focus-drilling supports depth-slice image averaging; depth-resolved resist coupling is not yet implemented. | Phase 5 depth resist |
| P3-L4 | Scalar coherent optics remains inherited from Phase 1. | Phase 2/4 |

## 5. Files

- `src/wafer_topo.py` — sign convention, height-to-defocus mapping, pupil phase helper
- `src/dof.py` — focus-stack contrast, nominal DOF window metrics, `k2` fit, focus-drilling average
- `src/pupil.py` — `PupilSpec.defocus_m` integration
- `src/aerial.py` — aerial-plane pupil defocus integration
- `tests/phase3_DOF.py` — sign, conjugacy, sampling, focus-stack, `k2`, focus-drilling, and zero-defocus regression tests
- `tests/audits/test_fft_invariants.py` — defocus unitary and zero-identity invariants

## 6. Exit Status

MT-006 through MT-012 are resolved by this design and the matching tests. Phase
3 now has a nominal focus-stack metric, a Rayleigh `k2` formula fit, and a
micro focus-drilling average. KPI K3 is complete for the project-level DOF
formula gate; broader LCDU/process-window validation remains future paper #14
work.
