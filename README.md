# High-NA EUV Lithography Simulator

Research and education simulator for 0.55 NA EUV lithography. The code follows
the source -> illumination -> reflective mask -> anamorphic projection -> wafer
-> resist path with reduced Fourier optics, depth-of-focus, Mask 3D, and
photoresist models.

## Quick Start

```bash
python -m pip install -r requirements-dev.txt
pytest tests/ -v
jupyter lab notebooks/0_first_aerial_image.ipynb
```

## Current Status

| Phase | Scope | Status |
|---|---|---|
| 1 | Scalar Fourier optics MVP: pupil, mask, aerial image | Complete |
| 2 | Partial coherence / illuminator | Pending |
| 3 | Wafer topography and DOF | Complete through k2 fitting |
| 4 | Mask 3D effects | Started: paper #12 six-effect stub |
| 5 | Photoresist: threshold, blur, depth, stochastic | Complete through calibration exit gates |
| 6 | SMO / PMWO / OPC / ILT | Pending |

## Notebook Demos

- `notebooks/0_first_aerial_image.ipynb`
- `notebooks/3d_focus_stack.ipynb`
- `notebooks/3d_pupil_wavefront.ipynb`
- `notebooks/3d_resist_depth.ipynb`
- `notebooks/3_M3D_effects.ipynb`
- `notebooks/4a_threshold_resist.ipynb`
- `notebooks/4b_resist_levels.ipynb`

## Main References

- `PROJECT_OVERVIEW.md` - project inventory, roadmap, and operating context.
- `진행계획서.md` - phase plan, KPIs, WBS, and risk register.
- `docs/phase4_M3D_design.md` - Phase 4 reduced Mask 3D model.
- `docs/phase5_resist_models.md` - Phase 5 resist model stack.
- `docs/github_claude_automerge_setup.md` - GitHub automation setup.
- `audits/AUDIT_LOG.md` - audit and mitigation task tracking.

## License

Research and education use. Commercial use requires separate agreement.
