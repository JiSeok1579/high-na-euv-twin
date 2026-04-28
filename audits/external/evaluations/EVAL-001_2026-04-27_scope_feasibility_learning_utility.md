# EVAL-001 - Scope, Feasibility, and Learning Utility

Status: archived external evaluation
Date: 2026-04-27
Last normalized: 2026-04-28
Scope: Phase 1 through Phase 6, reference-paper mapping, and notebook
correctness findings

This evaluation is an archived external assessment. It is not the active source
of implementation policy; current policy is in `PROJECT_OVERVIEW.md`,
`PROJECT_PLAN.md`, and `REVIEWER_DIRECTIVE.md`.

## Summary

The project is feasible as a study-grade simulator. The core implementation is
deep enough for learning, but it must avoid implying industrial calibration or
full process accuracy.

Key conclusions:

- The Phase 1 through Phase 6 skeleton is implemented.
- The repository has enough tests and module separation for study-grade use.
- Paywalled papers cannot be quantitatively reproduced without access to their
  data and setup details.
- Reduced Mask 3D, stochastic resist, and SMO / PMWO should stay labeled as
  qualitative unless future evidence supports stronger claims.
- Notebook validation must prefer 2D heatmaps and 2D line plots. Sparse 3D
  surfaces can create false physical intuition.

## Learning Utility

Strong learning areas:

- Anamorphic coordinate scaling.
- Fourier optics aerial image flow.
- Pupil and central obscuration intuition.
- Source-shape effects on contrast.
- Defocus sign conventions and DOF trends.
- Threshold and blur resist behavior.

Limited learning areas:

- Quantitative mask EM behavior.
- Industrial LCDU / LWR matching.
- Full resist chemistry and development.
- Plasma source physics.
- Polarization effects.
- True gradient-based industrial ILT.

## Recommendations

1. Keep the 2D validation-first notebook workflow.
2. Keep README and project documents explicit about study-grade scope.
3. Add stronger Phase 4 M3D validation only when public evidence is available.
4. Add stronger stochastic resist calibration examples only when the assumptions
   are visible to the reader.
5. Keep archived evaluations separate from active implementation instructions.

## Archive Note

The original evaluation contained a longer Korean-language narrative. This file
has been normalized to a compact English archive summary during repository
polish.
