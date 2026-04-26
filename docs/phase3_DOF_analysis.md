# Phase 3 — DOF Focus Stack Metrics

## 1. Purpose

Phase 3 Part 02 adds the first reproducible depth-of-focus metric. It is a
nominal process-window metric around `defocus_m = 0`, not a full process-window
study. The goal is to make future `k2 * lambda / NA^2` validation measurable
without changing the Phase 3 defocus sign convention.

## 2. Implemented Metrics

| Function | Role |
|----------|------|
| `focus_stack_contrast(...)` | Runs `aerial_image(...)` over signed constant-defocus values and records center-line Michelson contrast. |
| `nominal_depth_of_focus(...)` | Interpolates the contiguous threshold window around nominal focus. |
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
- real aerial line-space focus-stack symmetry
- zero-defocus Phase 1 regression

## 4. K3 Status

KPI K3 is now measurable but not complete. Completion still requires a broader
focus sweep and reported `k2` estimate against:

```text
DOF = k2 * lambda / NA^2
```

The next Phase 3 increment should run a controlled NA/pitch sweep and record
the fitted `k2` table here.
