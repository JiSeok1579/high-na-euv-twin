# INST-003 - Notebook Correctness Fixes

Status: implemented and archived
Last updated: 2026-04-28

This instruction tracked notebook correctness fixes that have since been
absorbed into the active validation workflow.

## Current Standard

- Notebook imports should work from the repository root.
- Headless execution should work with `MPLBACKEND=Agg`.
- Plots should include explicit units.
- Validation notebooks should print sanity checks before plotting.
- Demo-only 3D views should appear after the 2D validation views.

## Validation Command

```bash
MPLBACKEND=Agg jupyter nbconvert --to notebook --execute \
  notebooks/3d_focus_stack.ipynb \
  notebooks/3d_resist_depth.ipynb \
  --output-dir /tmp/high_na_euv_nbcheck \
  --ExecutePreprocessor.timeout=120
```
