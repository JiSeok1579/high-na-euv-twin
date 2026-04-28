# High-NA EUV Lithography Simulator

Research and education simulator for 0.55 NA EUV lithography. The project
models the path

```text
source -> illuminator -> reflective mask -> projection optics -> wafer -> resist -> correction
```

with reduced Fourier optics, partial coherence, wafer defocus, Mask 3D
approximations, resist models, and SMO/PMWO/OPC/ILT optimization helpers.

This repository is designed for study, visualization, parameter sweeps, and
qualitative understanding. It is not an industry-grade scanner replica and does
not claim real-equipment 1:1 validation.

## Start Here

| Goal | Read / Run |
|------|------------|
| Install and run the first simulation | [docs/getting_started.md](docs/getting_started.md) |
| Understand the project scope and remaining work | [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) |
| Learn how the validation and 3D demo notebooks are built | [docs/3d_implementation_guide.md](docs/3d_implementation_guide.md) |
| Inspect the phase-by-phase physics decisions | [docs/phase1_design.md](docs/phase1_design.md), [docs/phase2_illumination_design.md](docs/phase2_illumination_design.md), [docs/phase3_design.md](docs/phase3_design.md), [docs/phase4_M3D_design.md](docs/phase4_M3D_design.md), [docs/phase5_resist_models.md](docs/phase5_resist_models.md), [docs/phase6_optimization_design.md](docs/phase6_optimization_design.md) |
| Run all tests | `python3 -m pytest tests/ -v` |
| Open the first notebook | `jupyter lab notebooks/0_first_aerial_image.ipynb` |

## Quick Start

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pytest tests/ -v
jupyter lab notebooks/0_first_aerial_image.ipynb
```

If you only want to check that the code imports and the most important
simulation path works:

```bash
python3 -m pytest tests/integration_end_to_end.py -v
```

## Recommended Learning Path

1. Run [notebooks/0_first_aerial_image.ipynb](notebooks/0_first_aerial_image.ipynb)
   to see the basic mask -> aerial-image path.
2. Run [notebooks/4a_threshold_resist.ipynb](notebooks/4a_threshold_resist.ipynb)
   to close the aerial image -> printed resist path.
3. Run the validation notebooks. The focus and resist notebooks start with 2D
   heatmaps/line plots for physical checks, then keep 3D surfaces as demo-only
   views:
   - [notebooks/3d_focus_stack.ipynb](notebooks/3d_focus_stack.ipynb)
   - [notebooks/3d_pupil_wavefront.ipynb](notebooks/3d_pupil_wavefront.ipynb)
   - [notebooks/3d_resist_depth.ipynb](notebooks/3d_resist_depth.ipynb)
4. Run [notebooks/5_SMO_PMWO.ipynb](notebooks/5_SMO_PMWO.ipynb) to see the
   SMO/PMWO/OPC/ILT optimization loop.
5. Read [docs/3d_implementation_guide.md](docs/3d_implementation_guide.md) if
   you want to add a new 3D visualization.

## What Is Implemented

| Phase | Scope | Status | Main files |
|---|---|---|---|
| 1 | Scalar Fourier optics MVP | Complete | `src/aerial.py`, `src/pupil.py`, `src/mask.py` |
| 2 | Source shapes and partial coherence | Part 01 complete | `src/illuminator.py`, `data/source_shapes/basic_sources.json` |
| 3 | Wafer topography and DOF | Complete through k2 fitting | `src/wafer_topo.py`, `src/dof.py` |
| 4 | Mask 3D effects | Part 04 complete | `src/mask_3d.py`, `data/mask3d_lookup/` |
| 5 | Threshold, blur, depth, stochastic resist | Complete through calibration gates | `src/resist_threshold.py`, `src/resist_blur.py`, `src/resist_depth.py`, `src/resist_stochastic.py` |
| 6 | SMO / PMWO / OPC / ILT | Part 04 complete | `src/smo.py`, `src/pmwo.py`, `src/ilt.py`, `src/opc.py` |

## Notebook Map

| Notebook | Purpose | Best first question |
|----------|---------|---------------------|
| [0_first_aerial_image.ipynb](notebooks/0_first_aerial_image.ipynb) | Phase 1 coherent aerial image | What does the first image solver output look like? |
| [1_partial_coherence.ipynb](notebooks/1_partial_coherence.ipynb) | Phase 2 source-shape comparison | How do point/annular/etc. sources change contrast? |
| [3d_focus_stack.ipynb](notebooks/3d_focus_stack.ipynb) | 2D focus heatmap, contrast curve, and demo-only 3D surface | How does defocus reshape intensity? |
| [3d_pupil_wavefront.ipynb](notebooks/3d_pupil_wavefront.ipynb) | 3D Zernike wavefront comparison | What do pupil aberration modes look like? |
| [3d_resist_depth.ipynb](notebooks/3d_resist_depth.ipynb) | 2D x-depth dose validation and demo-only 3D surface | How does dose attenuate through resist? |
| [3_M3D_effects.ipynb](notebooks/3_M3D_effects.ipynb) | Reduced Mask 3D effects | What qualitative M3D knobs are modeled? |
| [4a_threshold_resist.ipynb](notebooks/4a_threshold_resist.ipynb) | Threshold resist MVP | How does aerial intensity become printed pattern? |
| [4b_resist_levels.ipynb](notebooks/4b_resist_levels.ipynb) | Blur/depth/stochastic resist | How do resist refinements change CD/EPE/LWR? |
| [5_SMO_PMWO.ipynb](notebooks/5_SMO_PMWO.ipynb) | Optimization demo | How do SMO/PMWO/OPC/ILT candidates improve a target? |

## Common Commands

```bash
# Full local validation
python3 -m ruff check src tests
python3 -m mypy src --ignore-missing-imports
python3 -m pytest tests/ -v --tb=short --cov=src --cov-report=term-missing

# Run one phase
python3 -m pytest tests/phase6_smo.py tests/phase6_pmwo.py tests/phase6_ilt.py tests/phase6_opc.py -q

# Execute a notebook headlessly
MPLBACKEND=Agg jupyter nbconvert \
  --to notebook \
  --execute notebooks/3d_focus_stack.ipynb \
  --output-dir /tmp/high_na_euv_nbcheck \
  --ExecutePreprocessor.timeout=120
```

## Validation And 3D Implementation

The current visualization workflow uses Matplotlib, not a browser rendering
engine. Focus and resist validation should be read from 2D heatmaps and line
plots; 3D surfaces are kept as demo views after the validation cells.

For the full implementation pattern, extension checklist, and validation
commands, read [docs/3d_implementation_guide.md](docs/3d_implementation_guide.md).

## Project Documents

- [docs/getting_started.md](docs/getting_started.md) - installation, first run,
  troubleshooting, and suggested reading path.
- [docs/3d_implementation_guide.md](docs/3d_implementation_guide.md) - how the
  2D validation plots and demo-only 3D notebook views are implemented.
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - inventory, roadmap, remaining
  work checklist, and operating context.
- [PROJECT_PLAN.md](PROJECT_PLAN.md) - phase plan, KPI tracking, deliverables,
  risk register, and change history.
- [references/papers/README.md](references/papers/README.md) - reference-paper
  index and study notes.
- [audits/AUDIT_LOG.md](audits/AUDIT_LOG.md) - audit history and test-count
  progression.
- [docs/study_grade_relaxation.md](docs/study_grade_relaxation.md) - why this
  project uses study-grade gates rather than industrial validation gates.
- [docs/github_claude_automerge_setup.md](docs/github_claude_automerge_setup.md)
  - repository automation and merge policy.

## License

Research and education use. Commercial use requires separate agreement.
