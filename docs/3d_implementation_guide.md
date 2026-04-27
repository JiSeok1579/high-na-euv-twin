# 3D Implementation Guide

This guide explains how the existing 3D notebooks are implemented and how to add
a new 3D visualization without breaking the study-grade workflow.

The current 3D stack uses Matplotlib's `mplot3d`. It does not require a browser,
WebGL, or Three.js. The goal is reliable scientific visualization that can run
inside Jupyter and headless `nbconvert`.

## Existing 3D Notebooks

| Notebook | Physical object | Main module inputs | Main plot |
|----------|-----------------|--------------------|-----------|
| `notebooks/3d_focus_stack.ipynb` | Aerial image through defocus | `src.mask`, `src.pupil`, `src.aerial`, `src.dof` | `x` vs defocus vs normalized intensity |
| `notebooks/3d_pupil_wavefront.ipynb` | Zernike pupil wavefront | `src.optics.zernike` | pupil x/y vs OPD in waves |
| `notebooks/3d_resist_depth.ipynb` | Resist dose through depth | `src.aerial`, `src.resist_depth` | `x` vs resist depth vs dose |

## Common Pattern

Each 3D notebook follows the same shape:

1. Import the repository root and scientific stack.
2. Build a grid or pupil coordinate system.
3. Compute a 2D surface or a small stack of 2D arrays.
4. Convert axes to readable units, usually nanometers.
5. Use `fig.add_subplot(..., projection="3d")`.
6. Plot with `ax.plot_surface(...)`.
7. Add labels, title, colorbar if useful, and `fig.tight_layout()`.
8. Add one small parameter sweep cell.
9. Validate with both interactive Jupyter and headless `nbconvert`.

## Minimal 3D Surface Template

```python
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.abspath(".."))

x_nm = np.linspace(-100.0, 100.0, 128)
z_nm = np.linspace(-50.0, 50.0, 21)
X, Z = np.meshgrid(x_nm, z_nm)
Y = np.exp(-(X / 40.0) ** 2) * np.cos(Z / 30.0)

fig = plt.figure(figsize=(9, 5))
ax = fig.add_subplot(111, projection="3d")
surface = ax.plot_surface(
    X,
    Z,
    Y,
    cmap="viridis",
    linewidth=0,
    antialiased=True,
    alpha=0.9,
)
ax.set_xlabel("x [nm]")
ax.set_ylabel("sweep axis [nm]")
ax.set_zlabel("normalized response")
ax.set_title("Example 3D response surface")
fig.colorbar(surface, ax=ax, shrink=0.6, pad=0.1)
fig.tight_layout()
plt.show()
```

## Focus Stack Implementation

File: `notebooks/3d_focus_stack.ipynb`

The notebook builds a line-space mask and evaluates aerial images across
defocus:

```python
grid = MaskGrid(nx=256, ny=64, pixel_size=2e-9)
mask = kirchhoff_mask(line_space_pattern(grid, pitch_m=40e-9))
defocus_values = np.linspace(-80e-9, 80e-9, 9)
```

For each defocus value, it creates a `PupilSpec` with `defocus_m`, computes the
aerial image, and stores the center line:

```python
image, wafer = aerial_image(
    mask,
    grid,
    pupil_spec=PupilSpec(grid_size=256, na=C.NA_HIGH, defocus_m=float(dz)),
    anamorphic=False,
)
line = image[wafer.ny // 2, :]
```

The plotted axes are:

- x axis: wafer x coordinate in nm,
- y axis: defocus in nm,
- z axis: normalized aerial intensity.

Use this notebook when you want to study depth-of-focus behavior, contrast loss,
or the effect of a new pupil option.

## Pupil Wavefront Implementation

File: `notebooks/3d_pupil_wavefront.ipynb`

The notebook builds a normalized pupil disk:

```python
axis = np.linspace(-1.0, 1.0, grid)
X, Y = np.meshgrid(axis, axis)
rho = np.sqrt(X**2 + Y**2)
theta = np.arctan2(Y, X)
```

It then calls:

```python
W = wavefront(rho, theta, coeffs)
W = np.where(rho <= 1.0, W, np.nan)
```

Outside-pupil values are masked with `np.nan` so the plotted surface is a disk,
not a square sheet.

Use this notebook when adding or tuning Zernike terms that later feed
`PupilSpec.zernike` and Phase 6 PMWO/ILT experiments.

## Resist Depth Implementation

File: `notebooks/3d_resist_depth.ipynb`

The notebook computes one aerial image, then expands it through resist depth:

```python
depths = np.linspace(0.0, 60e-9, 7)
dose_stack = depth_resolved_dose_stack(
    aerial,
    depths,
    dose=1.0,
    absorption_coefficient_m_inv=2.0e6,
)
```

The surface uses:

- x axis: wafer x coordinate in nm,
- y axis: resist depth in nm,
- z axis: dose.

The parameter sweep repeats the dose-depth calculation for low, nominal, and
high absorption coefficients. This is the recommended pattern for any new 3D
notebook: first show one baseline surface, then add one compact sensitivity
sweep.

## How To Add a New 3D Notebook

1. Copy the import/path setup from an existing 3D notebook.
2. Choose one physical quantity for the z axis. Avoid mixing unrelated metrics
   in the same surface.
3. Keep the initial grid small enough for fast interactive use.
4. Convert SI units to plot labels, usually nm for space and waves for OPD.
5. Normalize only when it helps comparison. Keep raw units when absolute scale
   matters.
6. Add a small parameter sweep cell with 3 to 6 cases.
7. Validate it headlessly before committing.
8. Add the notebook to `README.md` and update this guide if it introduces a new
   plotting pattern.

## Good Defaults

| Setting | Recommended starting value |
|---------|----------------------------|
| Mask grid | `MaskGrid(nx=256, ny=64, pixel_size=2e-9)` |
| Line-space pitch | `40e-9` |
| Defocus sweep | `np.linspace(-80e-9, 80e-9, 9)` |
| Resist depth sweep | `np.linspace(0.0, 60e-9, 7)` |
| Pupil grid for wavefronts | 160 to 256 |
| Figure size | `(9, 5)` for one surface, `(13, 7)` for 2x3 comparison |
| Colormaps | `viridis` for intensity, `plasma` for contrast, `coolwarm` for signed wavefronts, `magma` for dose |

## Headless Validation

Run one notebook:

```bash
MPLBACKEND=Agg jupyter nbconvert \
  --to notebook \
  --execute notebooks/3d_focus_stack.ipynb \
  --output-dir /tmp/high_na_euv_nbcheck \
  --ExecutePreprocessor.timeout=120
```

Run all current 3D notebooks:

```bash
MPLBACKEND=Agg jupyter nbconvert \
  --to notebook \
  --execute \
  notebooks/3d_focus_stack.ipynb \
  notebooks/3d_pupil_wavefront.ipynb \
  notebooks/3d_resist_depth.ipynb \
  --output-dir /tmp/high_na_euv_nbcheck \
  --ExecutePreprocessor.timeout=120
```

## Common Failure Modes

| Problem | Cause | Fix |
|---------|-------|-----|
| Blank surface | The z array is all zero, all NaN, or clipped by `set_zlim` | Print min/max and check masks before plotting |
| Jagged surface | Grid too coarse or sweep axis too sparse | Increase samples only after the plot works |
| Memory blow-up | Full 3D volume plotted at high resolution | Plot a center-line surface first, then add selected slices |
| Wrong units | SI meters plotted directly without conversion | Convert to nm with `* 1e9` for plot axes |
| Notebook works interactively but fails in CI | Kernel or Matplotlib backend mismatch | Use `MPLBACKEND=Agg` and keep dependency imports explicit |

## When To Use a New Module Instead of Notebook-Only Code

Move code into `src/` when:

- the calculation is used by more than one notebook,
- the behavior needs a regression test,
- the calculation defines a project metric,
- or a later phase depends on it.

Keep code in the notebook when:

- it only reshapes arrays for plotting,
- it only changes labels or colormaps,
- or it is a one-off visual comparison.

## Checklist Before Committing a 3D Update

- [ ] The notebook runs top to bottom from the repository root.
- [ ] Axes have physical units in the labels.
- [ ] The first surface is visually interpretable without reading code.
- [ ] At least one parameter sweep is included when the plot demonstrates a
  tunable effect.
- [ ] Any new reusable calculation has a test in `tests/`.
- [ ] `README.md` links to the notebook or guide.
- [ ] `nbconvert` execution passes with `MPLBACKEND=Agg`.
