# High-NA EUV Lithography Simulator - Project Plan

Created: 2026-04-25
Last updated: 2026-04-28
Version: v3.6 repository polish
Status: active

This plan defines the phase sequence, acceptance checks, and operating rules
for the study-grade High-NA EUV lithography simulator.

## 1. Goal

Build a qualitative simulator that connects:

```text
source -> illuminator -> reflective mask -> projection optics -> wafer focus
       -> aerial image -> resist response -> correction / optimization
```

The simulator is designed for learning, visualization, exploration, and paper
traceability. It is not intended to match an industrial scanner or process
recipe quantitatively.

## 2. Success Criteria

| ID | Criterion | Study-grade target |
| --- | --- | --- |
| K1 | End-to-end flow | Mask input produces a printed-pattern output. |
| K2 | Diffraction behavior | Line-space contrast changes qualitatively with pitch and NA. |
| K3 | DOF behavior | Contrast follows the expected DOF trend around best focus. |
| K4 | Mask 3D behavior | Reduced models expose the six major paper #12 effects. |
| K5 | Resist behavior | Threshold, blur, depth, and stochastic paths are testable. |
| K6 | Optimization loop | Source-mask variables can reduce a simple loss. |
| K7 | Documentation | New users can run tests and notebooks from README-linked docs. |

## 3. Operating Rules

1. Keep all public path names in English ASCII.
2. Keep README and project documents synchronized with notebook behavior.
3. Prefer 2D validation plots for physical checks; keep 3D surfaces as demo
   views only.
4. Record simplifications in code, docs, tests, and audit logs when they affect
   interpretation.
5. Treat broken tests, unit drift, invalid signs, and false audit status as
   P0/P1 issues.
6. Treat missing industrial calibration as expected study-grade backlog unless
   a module claims quantitative accuracy.
7. Commit and PR titles must be clear enough to explain the phase, part, and
   update type.

## 4. Phase Plan

| Phase | Area | Main Objective | Status |
| --- | --- | --- | --- |
| Phase 1 | Scalar Fourier optics | Create mask, pupil, and aerial-image baseline. | Implemented |
| Phase 2 | Source and coherence | Add source-shape sampling and partial coherence. | Implemented |
| Phase 3 | Wafer focus and DOF | Add defocus sign convention, focus stacks, and DOF metrics. | Implemented baseline |
| Phase 4 | Mask 3D | Add reduced M3D effects and mitigation hooks. | Implemented baseline |
| Phase 5 | Resist | Add threshold, blur, depth, and stochastic resist models. | Implemented baseline |
| Phase 6 | SMO / PMWO | Close the source-mask optimization MVP loop. | Implemented MVP |

## 5. Phase Acceptance

### Phase 1 - Scalar Fourier Optics

Required outputs:

- Binary line-space mask generation.
- Annular pupil support.
- Aerial image solver.
- Anamorphic coordinate support.

Acceptance checks:

- Output arrays are finite and non-negative.
- Pitch and NA sweeps show plausible contrast changes.
- Regression tests cover basic shapes and energy behavior.

### Phase 2 - Source and Partial Coherence

Required outputs:

- Annular, dipole, quadrupole, and freeform source definitions.
- Source-point sampling.
- Incoherent intensity summation.

Acceptance checks:

- Source weights are normalized.
- Symmetric sources preserve expected symmetry.
- Different source shapes change contrast qualitatively.

### Phase 3 - Wafer Focus and DOF

Required outputs:

- Fixed defocus sign convention.
- Focus-stack computation.
- Contrast-through-focus metric.
- Nominal DOF metric.

Acceptance checks:

- Best focus is near zero for a symmetric flat setup.
- Defocus sweeps are finite and reproducible.
- Validation notebooks use a 2D x-defocus heatmap and a 2D contrast curve.

### Phase 4 - Reduced Mask 3D

Required outputs:

- Reduced M3D parameter model.
- Shadowing, best-focus shift, telecentricity, NILS, bossung tilt, and
  absorber-sensitivity hooks.
- M3D-aware loss terms for later optimization.

Acceptance checks:

- The six named effects are individually testable.
- Model limitations are stated as reduced / qualitative.
- No notebook or doc presents reduced M3D as rigorous EM simulation.

### Phase 5 - Resist Models

Required outputs:

- Threshold resist.
- Gaussian blur.
- Depth-resolved Beer-Lambert dose stack.
- Focus-depth coupled comparison path.
- Stochastic LWR helper.

Acceptance checks:

- Bottom mean dose decreases when absorption is positive.
- Depth heatmaps are x-depth 2D validation plots.
- Full resist development, acid diffusion, and sidewall prediction are not
  claimed.

### Phase 6 - SMO / PMWO

Required outputs:

- Source variables connected to the objective.
- Resist and LWR penalties connected to the loss.
- A simple source-mask optimization loop.
- Reproducible notebook demonstration.

Acceptance checks:

- The objective is finite and decreases in a simple scenario.
- Source variables remain bounded and interpretable.
- Results are documented as qualitative optimization.

## 6. Documentation Checklist

For each meaningful implementation change:

- Update README if the user path changes.
- Update `docs/getting_started.md` if run commands or notebooks change.
- Update relevant phase docs when model assumptions change.
- Update `audits/AUDIT_LOG.md` for audit-relevant changes.
- Keep archived instruction files marked as archived, superseded, or
  implemented when they are no longer active.

## 7. Repository Hygiene Checklist

Before merging:

- `git ls-files` contains no non-English or non-ASCII tracked path names.
- Untracked files are either intentionally added or removed.
- Generated residues such as `.DS_Store`, caches, and notebook checkpoints are
  absent or ignored.
- Notebook output residue is cleared unless a committed output is intentional.
- README-linked documents point to current paths.
- Stale references to renamed paths are removed.

## 8. Validation Commands

Recommended local checks:

```bash
pytest tests/
python3 -m ruff check src tests
python3 -m mypy src --ignore-missing-imports
```

Recommended notebook validation:

```bash
MPLBACKEND=Agg jupyter nbconvert --to notebook --execute \
  notebooks/3d_focus_stack.ipynb \
  notebooks/3d_resist_depth.ipynb \
  --output-dir /tmp/high_na_euv_nbcheck \
  --ExecutePreprocessor.timeout=120
```

## 9. Current Priority Queue

1. Keep repository documents aligned with the validation-first 2D notebook
   workflow.
2. Maintain clean English path names and clear README navigation.
3. Strengthen Phase 4 M3D validation stubs.
4. Extend Phase 6 optimization examples beyond the MVP case.
5. Add stronger quantitative comparisons only where public data is adequate.

## 10. Change Log

| Version | Date | Change |
| --- | --- | --- |
| v3.6 | 2026-04-28 | Repository polish: English path normalization, active-doc rewrite, residue cleanup, and 2D validation sync. |
| v3.5 | 2026-04-28 | Phase 6 SMO MVP connected to source variables and resist penalties. |
| v3.4 | 2026-04-28 | README and local usage documentation expanded for first-time users. |
| v3.3 | 2026-04-27 | Phase 5 resist chain closed the end-to-end MVP. |
| v3.2 | 2026-04-26 | Phase 3 DOF metrics and defocus convention stabilized. |
| v3.1 | 2026-04-26 | Phase 1 scalar Fourier optics baseline established. |
