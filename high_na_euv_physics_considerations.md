# High-NA EUV Lithography Simulator - Physics Considerations

Status: active implementation handbook
Last updated: 2026-04-28

This document summarizes the physics and modeling assumptions used by the
study-grade High-NA EUV lithography simulator. It is not a scanner design
document and does not attempt to reproduce a commercial tool.

## 1. System Chain

```text
EUV source -> illuminator -> reflective mask -> projection optics
           -> wafer focus -> aerial image -> resist -> correction
```

The simulator focuses on qualitative behavior:

- Resolution improves as NA increases.
- Depth of focus decreases as NA increases.
- Mask 3D effects become more visible at high chief-ray angle.
- Resist stochasticity becomes important because EUV photon counts are limited.
- Source, mask, focus, and resist choices are coupled.

## 2. Core Equations

### Wavelength and Frequency

```text
c = lambda * f
lambda_EUV = 13.5 nm
```

### Numerical Aperture

```text
NA = n * sin(theta)
```

For EUV in vacuum, use `n ~= 1`.

### Rayleigh Resolution

```text
R = k1 * lambda / NA
```

### Depth of Focus

```text
DOF = k2 * lambda / NA^2
```

This relationship is the main reason High-NA systems need careful focus and
wafer-topography handling.

### Defocus Pupil Phase

The study-grade paraxial form is:

```text
phi(rho) = pi * defocus_m * NA^2 / lambda * rho^2
```

The angular form can be used when the approximation error matters:

```text
phi(rho) = 2*pi/lambda * defocus_m * (1 - cos(theta))
sin(theta) = NA * rho
```

## 3. Fourier Aerial Imaging

The baseline scalar model is:

```text
mask field -> FFT -> pupil filter -> inverse FFT -> intensity
```

Implementation files:

- `src/mask.py`
- `src/pupil.py`
- `src/aerial.py`

Assumptions:

- Scalar optics.
- Thin-mask baseline unless Phase 4 reduced M3D terms are enabled.
- No rigorous RCWA / FDTD by default.
- No industrial scanner prescription.

## 4. Source and Partial Coherence

The illuminator is represented by sampled source points and weights. Coherent
images are computed per source point and summed incoherently.

Supported study-grade source types:

- Annular.
- Dipole.
- Quadrupole.
- Freeform.

Implementation files:

- `src/illuminator.py`
- `src/partial_coherence.py`

## 5. Reflective Mask and Mask 3D

EUV masks are reflective, not transmissive. At High-NA, absorber thickness and
oblique incidence can create:

- Asymmetric shadowing.
- Horizontal / vertical CD bias.
- Telecentricity error.
- Contrast loss.
- Best-focus shift.
- Secondary-image artifacts.

The current project uses reduced, qualitative M3D hooks. These are useful for
learning and sensitivity studies but should not be presented as rigorous EM
simulation.

Implementation file:

- `src/mask3d.py`

## 6. Wafer Focus and DOF

Wafer height maps are interpreted as local focus errors. Defocus is converted
into pupil phase. The sign convention is fixed in code and tests.

Validation rules:

- Symmetric flat baselines should have best focus near zero.
- Focus validation should use a 2D x-defocus heatmap.
- Contrast validation should use a 2D contrast-through-focus curve.
- Sparse 3D focus surfaces are demo-only.

Implementation files:

- `src/wafer_topo.py`
- `src/dof.py`

## 7. Resist Models

The resist chain is intentionally layered:

| Level | Model | Purpose |
| --- | --- | --- |
| 0 | Threshold | First printed-pattern MVP. |
| 1 | Blur | Chemical blur proxy. |
| 2 | Depth attenuation | Beer-Lambert x-depth dose stack. |
| 2b | Focus-depth coupling | Depth slices re-evaluate aerial image with local defocus. |
| 3 | Stochastic | Photon and material variability study hooks. |

Validation rules:

- Beer-Lambert depth stacks should show lower bottom mean dose when absorption
  is positive.
- Depth validation should use a 2D x-depth heatmap.
- Do not claim sidewall, development, or acid-diffusion prediction unless the
  corresponding model exists.

Implementation files:

- `src/resist.py`
- `src/resist_depth.py`
- `src/resist_stochastic.py`

## 8. Correction and Optimization

The correction path uses study-grade OPC, ILT, SMO, and PMWO concepts. The goal
is to expose the optimization structure, not to reproduce industrial correction
quality.

Typical objective terms:

```text
loss = image_error
     + resist_penalty
     + LWR_penalty
     + source_regularization
     + mask_regularization
```

Implementation files:

- `src/smo.py`
- `src/pipeline.py`
- `src/metrics.py`

## 9. Numerical Rules

Use these rules when adding or auditing code:

- Keep grid spacing and units explicit.
- Check arrays for finite values.
- Print shape, min/max, and sample counts in validation notebooks.
- Use deterministic seeds for stochastic demos.
- Avoid interpreting a sparse sweep as a continuous physical surface.
- Do not replicate scalar metrics across an axis and call the result a local
  field.

## 10. Validation Plot Policy

Primary validation views:

- Focus: 2D x-defocus heatmap.
- Contrast: 2D contrast-through-focus curve.
- Resist depth: 2D x-depth dose heatmap.
- Pupil wavefront: x/y OPD map or surface.

Demo views:

- 3D focus surface.
- 3D resist surface.
- 3D pupil surface.

Demo views must be labeled as demo-only unless the plotted dimensions are
physically resolved and adequately sampled.

## 11. What This Simulator Can Teach

Strong learning targets:

- Fourier optics flow.
- Pupil cutoff and central obscuration.
- Anamorphic coordinate scaling.
- Source-shape effects.
- Defocus sign and DOF trends.
- Threshold, blur, and depth-resolved resist behavior.
- The structure of SMO / PMWO objectives.

Limited learning targets:

- Industrial CD / LCDU / LWR matching.
- Full vector polarization.
- Rigorous mask EM.
- Real resist chemistry.
- Plasma source hardware.
- Proprietary scanner prescription.

## 12. Implementation Priority

1. Keep the end-to-end path runnable.
2. Keep README and notebook descriptions synchronized.
3. Prefer honest 2D validation over visually impressive but ambiguous 3D plots.
4. Add stronger physical models only when their assumptions and evidence are
   clear.
5. Keep all public path names and active docs in English.
