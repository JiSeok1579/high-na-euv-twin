# Phase 4 Mask 3D Design

## Scope

Phase 4 starts from paper #12 as a six-effect checklist for high-NA EUV mask
3D behavior. The first implementation is a reduced qualitative model in
`src/mask_3d.py`. It is intended to make the six effects visible, testable, and
available to later SMO loops. It is not a rigorous electromagnetic mask solver.

## Six-Effect Stub

| Paper #12 effect | Reduced metric | Current behavior |
|---|---|---|
| Asymmetric shadowing | `shadowing_loss_fraction` | Increases with chief-ray angle, absorber thickness, and dense pitch. |
| H/V CD bias | `orientation_cd_bias_m` | Changes sign between vertical and horizontal line orientation. |
| Telecentricity error | `telecentricity_error_mrad` | Grows for smaller pitch and larger absorber phase strength. |
| Contrast loss | `contrast_loss_fraction` | Tracks destructive-interference proxy from absorber phase and CRA. |
| Pitch-dependent best-focus shift | `best_focus_shift_m` | Decreases for the high-k near-n=1 candidate relative to TaBN. |
| Secondary images | `secondary_image_fraction` | Scales with absorber top-reflection proxy. |

The in-line projector mitigation is encoded explicitly: `chief_ray_angle_deg=0`
collapses all six paper #12 metrics to the Kirchhoff thin-mask baseline.

## Absorber Library

The starter material list is duplicated in code and data:

- `TABN_REFERENCE`: baseline absorber.
- `NI_HIGH_K`: high-k near-n=1 mitigation candidate.
- `RUTA_LOW_N_PSM`: low-n attenuated phase-shift candidate.
- `data/absorber_nk/materials.json`: editable starter data for future measured
  optical constants.

The numbers are qualitative defaults. They should not be used as measured
material data.

## Simplifications

| ID | Simplification | Consequence | Future replacement |
|---|---|---|---|
| P4-L1 | Boundary-correction scalar model instead of RCWA/Maxwell. | Correct sign/trend only, not quantitative CD or NILS prediction. | RCWA or imported rigorous mask lookup tables. |
| P4-L2 | Material optical constants are starter qualitative values. | Absorber ranking is a smoke test. | Measured n,k data at 13.5 nm. |
| P4-L3 | Every effect scales to zero at zero CRA. | Useful for paper #3 in-line mitigation check but incomplete for phase-only stack effects. | Separate angle and stack-cavity terms. |
| P4-L4 | Secondary images use a top-reflectivity proxy. | Ghost images are tracked as a scalar fraction only. | Field-level reflected-path model. |

## Verification

`tests/phase4_m3d_6effects.py` maps the paper #12 checklist to qualitative
unit tests:

- CRA zero baseline removes all six effects.
- Shadowing grows with chief-ray angle.
- H/V CD bias changes sign.
- Telecentricity error is pitch dependent.
- High-k near-n=1 absorber reduces contrast loss and best-focus shift proxies.
- Secondary image proxy scales with top reflectivity.

## Exit State

This PR opens Phase 4 Part 01. KPI K4 is not complete yet; the current status is
six-effect stub coverage, not validated Mask 3D accuracy.
