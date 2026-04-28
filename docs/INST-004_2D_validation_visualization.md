# INST-004 - 2D Validation Visualization

Status: implemented and archived
Last updated: 2026-04-28

This instruction required the focus and resist notebooks to use 2D validation
plots before any 3D demo view. The implementation is now part of the active
notebook workflow.

## Implemented Requirements

- `notebooks/3d_focus_stack.ipynb` uses at least 41 defocus samples.
- Focus validation uses a 2D x-defocus heatmap.
- Contrast validation uses a 2D contrast-through-focus curve.
- `notebooks/3d_resist_depth.ipynb` uses at least 31 depth samples.
- Resist-depth validation uses a 2D x-depth dose heatmap.
- Beer-Lambert attenuation and focus-depth coupling are labeled separately.
- 3D surfaces are demo-only.

## Acceptance Checks

- Focus stack prints shape, min/max, and sample counts.
- Contrast curve prints min/max and best-focus information.
- Resist dose stack prints shape, min/max, top mean dose, and bottom mean dose.
- Bottom mean dose is lower than top mean dose when absorption is positive.
- Notebook execution succeeds with `nbconvert`.
