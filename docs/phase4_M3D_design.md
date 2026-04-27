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

`load_absorber_materials_json(...)` reads the same schema from disk, accepting
either `thickness_m` or `thickness_nm`. This keeps the starter data replaceable
by measured 13.5 nm n,k rows without changing the simulator API.

Part 03 adds provenance fields to `AbsorberMaterial`:

- `source`: where the row came from, such as starter, paper table, metrology, or
  vendor data.
- `reference`: human-readable citation or transfer note.
- `measured`: boolean flag that separates real measured rows from qualitative
  starter rows.

## Part 02 Field-Level Boundary Correction

`boundary_corrected_mask(...)` upgrades the Part 01 scalar checklist into a
complex mask field that can feed the existing aerial-image solver. It returns a
`BoundaryCorrectionResult` with:

- `baseline_field`: the Phase 1 Kirchhoff thin-mask field.
- `corrected_field`: the reduced Mask 3D corrected complex field.
- `shadow_map`: incident-side boundary attenuation from oblique CRA.
- `phase_map_radians`: absorber phase perturbation localized to clear boundary
  pixels.
- `secondary_field`: shifted weak ghost field from absorber top reflection.
- `summary`: the same six-effect scalar checklist for traceability.

The correction remains local to absorber/clear boundaries. Zero CRA still
collapses to the Kirchhoff baseline, which is the explicit in-line projector
mitigation smoke test.

## Part 03 Lookup-Table Refinement

`Mask3DLookupTable` and `Mask3DLookupEntry` provide the hook for future rigorous
Mask 3D data. A lookup row stores the same six-effect metrics as
`Mask3DEffectSummary` at one material, pitch, chief-ray angle, and orientation.
`lookup_mask3d_six_effects(...)` linearly interpolates between pitch rows and
falls back to the reduced model when no matching row exists.

`screen_absorber_materials(...)` ranks absorber candidates using either reduced
model summaries or lookup-refined summaries. The score is a qualitative penalty
that combines shadowing, contrast loss, secondary-image strength, telecentricity
error, best-focus shift, and orientation CD bias. It is meant for candidate
ordering and workflow tests, not product qualification.

The repository includes:

- `data/absorber_nk/materials.json`: starter absorber rows with provenance
  fields. All current rows are marked `measured=false`.
- `data/mask3d_lookup/qualitative_example.json`: schema example only, explicitly
  not rigorous data.
- `data/mask3d_lookup/rigorous_import_template.csv`: header-only CSV template
  for RCWA/DDM/measured rows.

## Part 04 Rigorous-Data Import and Aerial Regression

Part 04 does not add fake rigorous numbers. It adds the plumbing needed to
replace qualitative rows safely once RCWA, DDM, or measured mask data exists.

`load_mask3d_lookup_csv(...)` imports external solver rows using explicit unit
columns. Pitch, orientation CD bias, and best-focus shift may be supplied in
meters or nanometers. Empty files fail closed.

`lookup_boundary_corrected_mask(...)` drives the Part 02 complex-field boundary
correction from imported lookup rows. This makes the field path data-driven:
when a matching rigorous row exists, it overrides the reduced CRA proxy; when it
does not, the caller can choose reduced-model fallback or fail.

`compare_mask3d_aerial_images(...)` and `lookup_mask3d_aerial_regression(...)`
provide the first aerial-image regression gate. They normalize predicted and
reference aerial images, compute RMSE, mean absolute error, and max absolute
error, and expose a boolean pass/fail status against explicit tolerances.

## Simplifications

| ID | Simplification | Consequence | Future replacement |
|---|---|---|---|
| P4-L1 | Boundary-correction field model instead of RCWA/Maxwell. | Correct sign/trend only, not quantitative CD or NILS prediction. | RCWA or imported rigorous mask lookup tables. |
| P4-L2 | Material optical constants are starter qualitative values unless loaded from JSON. | Absorber ranking is a smoke test before measured rows are supplied. | Measured n,k data at 13.5 nm. |
| P4-L3 | Every effect scales to zero at zero CRA. | Useful for paper #3 in-line mitigation check but incomplete for phase-only stack effects. | Separate angle and stack-cavity terms. |
| P4-L4 | Secondary images use a shifted top-reflectivity proxy. | Ghost images are field-level but not physically propagated reflected paths. | Field-level reflected-path model. |
| P4-L5 | Lookup-table example rows are qualitative placeholders. | Demonstrates schema and interpolation only. | Replace with DDM, RCWA, or measured Mask 3D table rows. |
| P4-L6 | Aerial regression currently compares imported references but does not generate them. | Quantitative accuracy depends entirely on supplied external rigorous images. | Add RCWA/DDM export fixtures or measured actinic aerial references. |

## Verification

`tests/phase4_m3d_6effects.py` maps the paper #12 checklist to qualitative
unit tests:

- CRA zero baseline removes all six effects.
- Shadowing grows with chief-ray angle.
- H/V CD bias changes sign.
- Telecentricity error is pitch dependent.
- High-k near-n=1 absorber reduces contrast loss and best-focus shift proxies.
- Secondary image proxy scales with top reflectivity.
- Boundary-corrected zero-CRA field equals the Kirchhoff baseline.
- Boundary shadow maps move with CRA sign.
- Boundary phase maps track absorber phase strength.
- JSON absorber loading accepts measured-row replacement data.
- Lookup rows interpolate by pitch and fall back to the reduced model when
  missing.
- Absorber screening prefers candidates with lower lookup-refined penalties.
- CSV lookup imports accept explicit nanometer columns.
- Lookup-driven boundary correction can override the reduced CRA proxy.
- Aerial-image regression gates imported references with RMSE and max-error
  tolerances.

## Exit State

Part 04 adds the import and regression path needed for later quantitative
refinement. KPI K4 remains a reduced-model pass until real RCWA/DDM/measured
rows are supplied, but the simulator now has a closed path for importing those
rows, applying them to the field model, and gating aerial-image agreement.
