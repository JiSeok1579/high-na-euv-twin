# High-NA EUV Paper Search Handoff

Status: normalized English handoff summary
Last updated: 2026-04-28

This file explains how to continue the paper-search and reference-maintenance
work for the simulator.

## Goals

- Keep the 21-paper reference set mapped to simulator phases.
- Add missing links, DOIs, and formulas when papers are read in detail.
- Keep notes in English for GitHub readability.
- Avoid committing PDFs unless licensing permits it.

## Priority Topics

1. Anamorphic High-NA projection and central obscuration.
2. Partial coherence, source shape, and relay/facet matching.
3. Wafer focus, DOF, and micro focus-drilling.
4. Reduced mask 3D effects and absorber optimization.
5. Resist threshold, blur, depth absorption, and stochastic LWR.
6. SMO, PMWO, OPC, and ILT optimization objectives.

## Maintenance Rules

- Update `references/papers/INDEX.md` when a paper is added or remapped.
- Update `references/papers/KNOWLEDGE.md` when a paper changes a model choice.
- Add formulas only when the original source supports them clearly.
- Mark access status as open, free, partial, or paywalled.
- Link implementation changes back to `src/`, `tests/`, or notebooks.

## Next Paper Work

- Verify paper #13 mapping to resist sidewall angle and focus-depth coupling.
- Add DOI fields to paper notes where missing.
- Add public formula snippets for Phase 4 M3D effects where available.
- Add public quantitative DOF references only if the units and setup are clear.
