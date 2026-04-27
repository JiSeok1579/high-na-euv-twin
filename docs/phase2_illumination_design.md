# Phase 2 Illumination Design

## Scope

Phase 2 adds a study-grade partial-coherence layer on top of the Phase 1
coherent aerial solver. The model supports on-axis point, dipole, quadrupole,
annular, and JSON/freeform source shapes.

The goal is not a rigorous Hopkins transmission cross coefficient model. The
goal is to expose the source-shape control surface needed for qualitative
contrast studies, notebook visualization, and future Phase 6 SMO/PMWO loops.

## Coordinate Convention

Source points are represented in normalized pupil coordinates:

```text
sigma = sqrt(sigma_x^2 + sigma_y^2), 0 <= sigma <= 1
```

Each source point applies a wafer-plane phase tilt before coherent imaging:

```text
fx_source = sigma_x * NA / wavelength
fy_source = sigma_y * NA / wavelength
M_tilted = M * exp(i * 2pi * (fx_source * x + fy_source * y))
```

`src/aerial.py` still computes one coherent image at a time. `src/illuminator.py`
performs partial coherence by summing source-point intensities incoherently:

```text
I_partial = sum_k normalized_weight_k * I_coherent(source_k)
```

The final partial-coherence image is normalized to peak 1 by default so it
remains compatible with Phase 5 resist threshold and stochastic workflows.

## Source Shapes

Implemented source constructors:

- `point_source()` keeps the Phase 1 on-axis coherent baseline.
- `dipole_source()` builds x/y dipoles.
- `quadrupole_source()` builds cardinal or diagonal quadrupoles.
- `annular_source()` samples an annular band with area-proportional ring
  weights.
- `freeform_source()` accepts explicit tuples or JSON-style dictionaries.

Data entry points:

- `data/source_shapes/basic_sources.json` stores starter source libraries.
- `load_source_shape_json()` loads one source shape.
- `load_source_shape_library_json()` loads multiple named shapes.

## Simplifications

| ID | Simplification | Study-grade effect |
|---|---|---|
| P2-L1 | Finite source-point sampling instead of continuous integration | Source-shape trends are available; dense sampling remains a runtime/accuracy knob. |
| P2-L2 | Off-axis source modeled as a scalar phase tilt | Captures qualitative diffraction-order shifts; not a rigorous vector/TCC solver. |
| P2-L3 | No polarization-dependent source weighting | Acceptable until Phase 6 needs polarization-aware optimization penalties. |
| P2-L4 | No measured illuminator pupil-fill data | JSON loader allows measured or externally generated source rows to replace starter shapes later. |

These are acceptable under `docs/study_grade_relaxation.md` because they do not
break the intended learning workflow and are explicitly documented.

## Verification

The Phase 2 test suite checks:

- On-axis point source reproduces the Phase 1 coherent aerial image.
- Dipole, quadrupole, and annular geometry stays inside the unit pupil.
- Freeform and JSON source shapes normalize weights deterministically.
- Off-axis source points change the resolved line-space aerial image.
- Annular partial coherence returns finite normalized intensity and optional
  per-source-point images.

Current implementation files:

- `src/illuminator.py`
- `src/aerial.py`
- `tests/phase2_illumination.py`
- `notebooks/1_partial_coherence.ipynb`
- `data/source_shapes/basic_sources.json`
