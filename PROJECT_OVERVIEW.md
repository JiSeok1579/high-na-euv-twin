# High-NA EUV Lithography Simulator - Project Overview

Created: 2026-04-25
Last updated: 2026-04-28
Status: study-grade simulator, active development
Primary entry point: README.md

This repository is a research and education simulator for High-NA EUV
lithography. It approximates the path from a 13.5 nm EUV source through
illumination, reflective mask imaging, projection optics, wafer focus, resist
response, and source-mask optimization.

The project is intentionally study-grade. It is not a reproduction of a
commercial scanner, a reverse-engineering effort, or a quantitative process
recipe. Public papers are used to build qualitative models, sanity checks, and
visual notebooks.

## Current State

The repository has an end-to-end qualitative simulator path:

1. Source and illumination sampling.
2. Reflective mask and Fourier aerial imaging.
3. Defocus, depth of focus, and focus-stack metrics.
4. Reduced mask 3D effects.
5. Threshold, blur, depth, and stochastic resist models.
6. SMO / PMWO demonstration loop.

The visualization workflow is validation-first:

- `notebooks/3d_focus_stack.ipynb` uses a 2D x-defocus heatmap and a 2D
  contrast-through-focus curve as the primary physical validation views.
- `notebooks/3d_resist_depth.ipynb` uses a 2D x-depth dose heatmap as the
  primary resist-depth validation view.
- 3D surfaces are retained only as demo views, not as the physical validation
  authority.

## Repository Map

```text
.
├── README.md
├── PROJECT_OVERVIEW.md
├── PROJECT_PLAN.md
├── REVIEWER_DIRECTIVE.md
├── high_na_euv_physics_considerations.md
├── high_na_euv_deep_research_report.docx
├── src/
├── tests/
├── notebooks/
├── docs/
├── audits/
├── data/
├── references/
│   ├── high_na_euv_reference_paper_list.txt
│   ├── high_na_euv_paper_search_handoff.md
│   └── papers/
└── .github/
```

All tracked path names are normalized to English ASCII. The former Korean paper
folder is now `references/`, the former Korean plan file is now
`PROJECT_PLAN.md`, and the long Korean report filename is now
`high_na_euv_deep_research_report.docx`.

## Scope

In scope:

- Scalar Fourier aerial image simulation.
- Annular, dipole, quadrupole, and freeform source sampling.
- Study-grade partial coherence.
- Wafer defocus and DOF metrics.
- Reduced mask 3D effects and mitigation hooks.
- Threshold, blur, depth-resolved, and stochastic resist models.
- Qualitative SMO / PMWO / OPC / ILT style optimization.
- Documentation and notebooks that explain how to run the models locally.

Out of scope:

- Commercial scanner prescription reconstruction.
- Rigorous industrial process matching.
- Full Maxwell mask EM simulation as a default path.
- Plasma source hardware simulation.
- Proprietary process recipe extraction.

## Phase Status

| Phase | Area | Status | Main Files |
| --- | --- | --- | --- |
| 1 | Scalar Fourier optics | Implemented | `src/aerial.py`, `src/mask.py`, `src/pupil.py` |
| 2 | Source and partial coherence | Implemented | `src/illuminator.py`, `src/partial_coherence.py` |
| 3 | DOF and wafer focus | Implemented baseline | `src/dof.py`, `src/wafer_topo.py` |
| 4 | Reduced mask 3D | Implemented baseline | `src/mask3d.py` |
| 5 | Resist models | Implemented baseline | `src/resist.py`, `src/resist_depth.py`, `src/resist_stochastic.py` |
| 6 | SMO / PMWO loop | Implemented MVP | `src/smo.py`, `src/pipeline.py` |

## Validation Policy

The project treats simple, reproducible sanity checks as the main guardrail.
Each phase should provide:

- Unit tests for shape, units, finite values, and monotonic trends.
- Notebook validation plots that expose physical behavior in 2D first.
- Clear model limitations in titles, docstrings, and documentation.
- Audit log entries for cross-cutting changes.

Notebook plots should not overclaim. 3D plots are useful for inspection and
presentation, but physical validation must be based on 2D heatmaps, 2D line
plots, scalar metrics, and automated tests.

## Local Usage

Use the README first. The short path is:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/
```

Run the validation notebooks headlessly with:

```bash
MPLBACKEND=Agg jupyter nbconvert --to notebook --execute \
  notebooks/3d_focus_stack.ipynb \
  notebooks/3d_resist_depth.ipynb \
  --output-dir /tmp/high_na_euv_nbcheck \
  --ExecutePreprocessor.timeout=120
```

For the browser-oriented notebook guide, start at `docs/getting_started.md`.
For the 3D implementation notes and validation-first plotting rules, read
`docs/3d_implementation_guide.md`.

## Reference Material

- `references/papers/README.md` explains the paper-note structure.
- `references/papers/INDEX.md` maps papers to phases and modules.
- `references/papers/KNOWLEDGE.md` is the integrated study summary.
- `high_na_euv_physics_considerations.md` is the main implementation handbook.
- `high_na_euv_deep_research_report.docx` is a supporting research report.

## Audit Trail

The audit system lives under `audits/`. Current working guidance is in:

- `audits/AUDIT_LOG.md`
- `REVIEWER_DIRECTIVE.md`
- `audits/templates/`
- `.github/PULL_REQUEST_TEMPLATE.md`

Archived external audit reports are kept for traceability. They may preserve
historical phrasing from the review process, but current entry-point documents,
paths, and templates should stay English and match the implemented code.

## Change History

| Date | Change |
| --- | --- |
| 2026-04-28 | Repository polish: English path normalization, residue cleanup, and validation-first documentation sync. |
| 2026-04-28 | 2D focus/resist validation notebooks aligned with README claims. |
| 2026-04-27 | SMO MVP connected to source variables and resist penalties. |
| 2026-04-26 | Phase 3, Phase 4, and Phase 5 baseline modules integrated. |
