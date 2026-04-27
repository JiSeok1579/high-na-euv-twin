# High-NA EUV Lithography Simulator

Research and education simulator for 0.55 NA EUV lithography. The code follows
the source -> illumination -> reflective mask -> anamorphic projection -> wafer
-> resist path with reduced Fourier optics, depth-of-focus, Mask 3D, and
photoresist models.

## Study Purpose

This is a **study-purpose simulator**, not a paper, report, or industry
deployment tool. Goals:

1. **Build** a working simulation of 0.55 NA EUV lithography.
2. **Visualize** results in 3D: focus stack, pupil wavefront, and resist depth.
3. **Understand qualitatively**:
   - the structural pipeline: source -> mask -> optics -> wafer -> resist
   - what a good result looks like at each stage
   - which input parameters can be fine-tuned and how the output responds

**This is not**:

- Paper or report writing.
- Real-equipment 1:1 replication or reverse engineering.
- Industry-grade quantitative validation. Data and paper sources are
  inconsistent, so strict industrial validation is out of scope.

Strict industrial quantitative validation is intentionally not pursued. The
primary workflow is implementation, result inspection, parameter tuning, and
qualitative learning.

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
| 2 | Partial coherence / illuminator | Part 01: source-shape and partial-coherence MVP |
| 3 | Wafer topography and DOF | Complete through k2 fitting |
| 4 | Mask 3D effects | Part 04: rigorous-data import and aerial regression hooks |
| 5 | Photoresist: threshold, blur, depth, stochastic | Complete through calibration exit gates |
| 6 | SMO / PMWO / OPC / ILT | Part 01: SMO grid-search MVP with source and LWR objective |

## Notebook Demos

- `notebooks/0_first_aerial_image.ipynb`
- `notebooks/1_partial_coherence.ipynb`
- `notebooks/3d_focus_stack.ipynb` - 3D focus and contrast sweeps.
- `notebooks/3d_pupil_wavefront.ipynb` - 3D Zernike mode comparison.
- `notebooks/3d_resist_depth.ipynb` - 3D dose-depth absorption sweep.
- `notebooks/3_M3D_effects.ipynb`
- `notebooks/4a_threshold_resist.ipynb`
- `notebooks/4b_resist_levels.ipynb`
- `notebooks/5_SMO_PMWO.ipynb`

## Main References

- `PROJECT_OVERVIEW.md` - project inventory, roadmap, and operating context.
- Project execution plan - phase plan, KPIs, WBS, and risk register.
- `docs/phase2_illumination_design.md` - Phase 2 source-shape and partial-coherence model.
- `docs/phase4_M3D_design.md` - Phase 4 Mask 3D boundary, lookup import, and aerial-regression model.
- `docs/phase5_resist_models.md` - Phase 5 resist model stack.
- `docs/phase6_optimization_design.md` - Phase 6 SMO objective and grid-search MVP.
- `docs/study_grade_relaxation.md` - study-purpose strictness and audit severity policy.
- `docs/github_claude_automerge_setup.md` - GitHub automation setup.
- `audits/AUDIT_LOG.md` - audit and mitigation task tracking.

## License

Research and education use. Commercial use requires separate agreement.
