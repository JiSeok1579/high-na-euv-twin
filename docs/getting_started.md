# Getting Started

This guide is for a first-time GitHub visitor who wants to run the simulator,
open the notebooks, and understand where to go next.

## What This Repository Does

The simulator follows a reduced High-NA EUV lithography pipeline:

```text
source -> illuminator -> reflective mask -> projection optics -> wafer -> resist -> correction
```

It is study-grade. The goal is to learn how the physics modules connect and how
parameters affect the printed pattern. The project intentionally avoids claims
of industrial scanner accuracy.

## Requirements

Use Python 3.11 or newer if possible. The tested dependency set is intentionally
small:

```text
numpy
scipy
matplotlib
pytest
pytest-cov
mypy
pre-commit
ruff
```

Install with:

```bash
python3 -m pip install -r requirements-dev.txt
```

If your system has multiple Python installs, use the same Python executable for
installation, testing, and Jupyter kernel registration.

## First Run

From the repository root:

```bash
python3 -m pytest tests/integration_end_to_end.py -v
```

This checks the basic mask -> aerial image -> threshold resist -> printed
pattern path. Then run the full suite:

```bash
python3 -m pytest tests/ -v
```

The expected current suite size is 118 tests.

## Open the First Notebook

```bash
jupyter lab notebooks/0_first_aerial_image.ipynb
```

Run all cells. The notebook builds a binary line-space mask, applies the
Kirchhoff thin-mask model, propagates through the pupil, and displays the aerial
image. This is the best first visual check.

## Suggested Notebook Order

| Step | Notebook | Why |
|------|----------|-----|
| 1 | `notebooks/0_first_aerial_image.ipynb` | First coherent aerial-image result |
| 2 | `notebooks/1_partial_coherence.ipynb` | Source-shape and partial-coherence behavior |
| 3 | `notebooks/4a_threshold_resist.ipynb` | Threshold resist and printed pattern |
| 4 | `notebooks/4b_resist_levels.ipynb` | Blur, depth, stochastic, and calibration hooks |
| 5 | `notebooks/3d_focus_stack.ipynb` | 2D focus validation heatmap, contrast curve, and demo-only 3D surface |
| 6 | `notebooks/3d_pupil_wavefront.ipynb` | 3D Zernike wavefront visualization |
| 7 | `notebooks/3d_resist_depth.ipynb` | 2D x-depth dose validation and demo-only 3D surface |
| 8 | `notebooks/5_SMO_PMWO.ipynb` | SMO/PMWO/OPC/ILT optimization flow |

## Core Modules

| File | Role |
|------|------|
| `src/constants.py` | Shared wavelength, NA, and anamorphic constants |
| `src/mask.py` | Mask grid, line-space patterns, Kirchhoff mask field |
| `src/pupil.py` | Pupil specification and obscuration/defocus inputs |
| `src/aerial.py` | Coherent aerial-image solver |
| `src/illuminator.py` | Point, annular, dipole, quadrupole, freeform sources and partial coherence |
| `src/wafer_topo.py`, `src/dof.py` | Defocus sign convention, DOF metrics, focus stack |
| `src/mask_3d.py` | Reduced Mask 3D metrics, boundary correction, lookup-table import |
| `src/resist_*.py` | Threshold, blur, depth, stochastic resist models |
| `src/metrics.py` | CD, EPE, NILS, contrast, and helper metrics |
| `src/smo.py` | Source-mask-dose grid search |
| `src/pmwo.py` | PMWO/OPC bias candidates and 2D EPE maps |
| `src/ilt.py` | Full-layout contour EPE and finite-difference ILT refinement |
| `src/opc.py` | Assist-feature OPC and pixel-level ILT refinement |

## Run a Minimal Script

```python
from src.mask import MaskGrid, kirchhoff_mask, line_space_pattern
from src.pupil import PupilSpec
from src.aerial import aerial_image

grid = MaskGrid(nx=256, ny=64, pixel_size=2e-9)
pattern = line_space_pattern(grid, pitch_m=40e-9, duty_cycle=0.5)
mask = kirchhoff_mask(pattern)
image, wafer = aerial_image(mask, grid, pupil_spec=PupilSpec(grid_size=256))

print(image.shape)
print(wafer.pixel_x_m, wafer.pixel_y_m)
```

Save it as `scratch_run.py` if you want a quick local experiment, then run:

```bash
python3 scratch_run.py
```

Do not commit scratch files unless they become a documented example.

## Validation Commands

```bash
python3 -m ruff check src tests
python3 -m mypy src --ignore-missing-imports
python3 -m pytest tests/ -v --tb=short --cov=src --cov-report=term-missing
```

For notebook validation:

```bash
MPLBACKEND=Agg jupyter nbconvert \
  --to notebook \
  --execute notebooks/5_SMO_PMWO.ipynb \
  --output-dir /tmp/high_na_euv_nbcheck \
  --ExecutePreprocessor.timeout=120
```

## Where To Read Next

- `README.md` gives the shortest route through the repository.
- `PROJECT_OVERVIEW.md` is the broad project inventory and remaining-work map.
- `docs/3d_implementation_guide.md` explains the validation-first notebook
  pattern and demo-only 3D views.
- `docs/phase6_optimization_design.md` explains the SMO/PMWO/OPC/ILT objective.
- `audits/AUDIT_LOG.md` records what was implemented and how it was validated.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `ModuleNotFoundError: src` in a notebook | Notebook kernel started from a different working directory | Run from repo root or add the repo path to `sys.path` as existing notebooks do |
| `ModuleNotFoundError: matplotlib` | Jupyter kernel uses a different Python than `pip install` | Install dependencies in that kernel environment or register the correct kernel |
| Notebook execution fails in a sandbox | Jupyter needs local kernel ports | Run locally, or execute with the same unrestricted environment used for normal Jupyter |
| Tests pass but plots look blank | Axis scaling or all-NaN surface mask | Check nan masks, `set_zlim`, and normalized intensity ranges |
| Very slow notebook | Grid size too large for exploratory plotting | Start with `nx=256`, `ny=64`, then scale up after the plot is correct |
