# Physics Audit Instructions

Status: active
Last updated: 2026-04-28

Review whether the EUV lithography behavior is physically plausible for a
study-grade simulator.

## Checkpoints

- Units are consistent: m, nm, radians, waves, dose, and pixels are not mixed.
- Defocus, anamorphic axes, CRA, and phase signs are stated and tested.
- Energy or intensity behavior is finite and non-negative where required.
- Simplified models state their limits.
- Paper claims are qualitative unless quantitative calibration exists.
- Validation plots use the right dimensionality.

## Focus and DOF Rules

- Use 2D x-defocus heatmaps and contrast-through-focus curves for validation.
- Best focus should be near zero for a symmetric flat baseline.
- Sparse 3D focus surfaces are demo views only.

## Resist Rules

- Beer-Lambert depth stacks should show lower bottom mean dose when absorption
  is positive.
- Focus-depth coupled resist views must be separated from simple attenuation
  baselines.
- Do not claim full resist development, sidewall, or acid diffusion behavior
  unless that model exists.

## Output

State whether the result is physically plausible, what assumptions limit the
claim, and which follow-up would most improve trust.
