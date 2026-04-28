# INST-002 - 3D Visualization Upgrade

Status: superseded and archived
Last updated: 2026-04-28

This instruction requested Tier 1 Matplotlib 3D notebooks. It is superseded by
the validation-first plotting rule documented in `docs/3d_implementation_guide.md`.

## Current Policy

- Use 2D heatmaps and 2D line plots for physical validation.
- Keep 3D surfaces as demo-only views unless the data is genuinely resolved
  across the plotted dimensions.
- Print shape, min/max, finite status, and sample counts in validation
  notebooks.
- Label reduced models explicitly.

## Implemented Notebooks

- `notebooks/3d_focus_stack.ipynb`
- `notebooks/3d_pupil_wavefront.ipynb`
- `notebooks/3d_resist_depth.ipynb`
