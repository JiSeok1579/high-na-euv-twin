# 3D Implementation Guide

This guide explains how the existing visualization notebooks are implemented and
how to add a new 3D demo without breaking the study-grade validation workflow.

The current stack uses Matplotlib. It does not require a browser, WebGL, or
Three.js. Physical validation now starts with 2D heatmaps and 2D line plots; 3D
surfaces are presentation/demo views only because sparse sweep surfaces can hide
or exaggerate artifacts.

## Existing 3D Notebooks

| Notebook | Physical object | Main module inputs | Validation plot |
|----------|-----------------|--------------------|-----------|
| `notebooks/3d_focus_stack.ipynb` | Aerial image through defocus | `src.mask`, `src.pupil`, `src.aerial`, `src.dof` | 2D x-defocus heatmap plus contrast curve |
| `notebooks/3d_pupil_wavefront.ipynb` | Zernike pupil wavefront | `src.optics.zernike` | pupil x/y OPD surface |
| `notebooks/3d_resist_depth.ipynb` | Resist dose through depth | `src.aerial`, `src.resist_depth` | 2D x-depth heatmaps for Beer-Lambert and focus-depth coupled dose |

## Common Pattern

Each validation notebook follows the same shape:

1. Import the repository root and scientific stack.
2. Build a grid or pupil coordinate system.
3. Compute a 2D surface or a small stack of 2D arrays.
4. Convert axes to readable units, usually nanometers.
5. Print sanity checks: shape, min/max, finite status, and sample counts.
6. Plot the validation view as a 2D heatmap or line plot.
7. Add a 3D surface only after the 2D validation plot, and label it demo-only.
8. Validate with both interactive Jupyter and headless `nbconvert`.

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
defocus_values = np.linspace(-80e-9, 80e-9, 41)
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

The validation outputs are:

- 2D x-defocus heatmap: x axis is wafer x coordinate in nm, y axis is defocus
  in nm, and color is normalized aerial intensity.
- 2D contrast curve: x axis is defocus in nm and y axis is normalized
  center-line contrast.
- demo-only 3D surface: x vs defocus vs normalized intensity.

Do not plot the scalar defocus contrast as a replicated 3D x surface. It is a
single scalar per defocus slice, so the validation view must be a line plot.

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
depths = np.linspace(0.0, 60e-9, 31)
dose_stack = depth_resolved_dose_stack(
    aerial,
    depths,
    dose=1.0,
    absorption_coefficient_m_inv=2.0e6,
)
```

The validation outputs are:

- 2D x-depth dose heatmap for the Beer-Lambert attenuation-only model.
- 2D x-depth dose heatmap for `focus_depth_resolved_resist`, which recomputes
  aerial images at depth-coupled defocus slices.
- demo-only 3D surface using the Beer-Lambert stack.

For `absorption_coefficient_m_inv=2.0e6` and a 60 nm thickness, the bottom/top
mean dose ratio should be close to `exp(-0.12)`, about 0.887, for the
Beer-Lambert-only model. Larger absorption coefficients should reduce that ratio.

## How To Add a New 3D Notebook

1. Copy the import/path setup from an existing 3D notebook.
2. Choose the validation plot first. Prefer a 2D heatmap for a stack or a line
   plot for one scalar per sweep point.
3. Keep the initial grid small enough for fast interactive use.
4. Convert SI units to plot labels, usually nm for space and waves for OPD.
5. Print shape, min/max, finite status, and the sweep sample count before the
   plot.
6. Normalize only when it helps comparison. Keep raw units when absolute scale
   matters.
7. Add a 3D surface only as a downstream demo if it communicates the already
   validated result.
8. Validate it headlessly before committing.
9. Add the notebook to `README.md` and update this guide if it introduces a new
   plotting pattern.

## Good Defaults

| Setting | Recommended starting value |
|---------|----------------------------|
| Mask grid | `MaskGrid(nx=256, ny=64, pixel_size=2e-9)` |
| Line-space pitch | `40e-9` |
| Defocus sweep | `np.linspace(-80e-9, 80e-9, 41)` |
| Resist depth sweep | `np.linspace(0.0, 60e-9, 31)` |
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

## Validation Criteria

| Plot | Expected result | Red flag |
|------|-----------------|----------|
| Focus heatmap | Periodic x pattern, strongest nominal-focus contrast, finite non-negative intensity | Identical rows for every defocus, NaN/Inf, negative intensity, or random x noise |
| Contrast curve | Normalized maximum equals 1 and best focus is near 0 nm for the nominal window | Constant contrast, endpoint-only best focus, negative or NaN contrast |
| Resist depth heatmap | Bottom mean dose is lower than top mean dose and tracks attenuation coefficient | Bottom dose exceeds top dose, absorption coefficient has no effect, or dose becomes negative |

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
- [ ] The first validation plot is a 2D heatmap or line plot, not a 3D surface.
- [ ] Each validation plot prints shape, min/max, finite status, and sample
  counts or mean-dose checks.
- [ ] Any 3D surface is labeled as demo-only.
- [ ] At least one parameter sweep is included when the plot demonstrates a
  tunable effect.
- [ ] Any new reusable calculation has a test in `tests/`.
- [ ] `README.md` links to the notebook or guide.
- [ ] `nbconvert` execution passes with `MPLBACKEND=Agg`.
