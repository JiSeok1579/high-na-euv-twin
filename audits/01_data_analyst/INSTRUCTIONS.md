# Data Analyst Audit Instructions

Status: active
Last updated: 2026-04-28

Review data flow, input assumptions, and trend interpretation.

## Checkpoints

- Inputs have documented units and expected ranges.
- Arrays have explicit shapes and finite-value checks.
- Sweeps use enough samples for the claimed trend.
- Metrics are not overinterpreted beyond the study-grade model.
- Plots expose the relevant dimensions directly.
- README and notebooks describe the same data path.

## Red Flags

- A sparse sweep is presented as a smooth physical surface.
- A scalar metric is replicated across an axis and treated as local data.
- A plot title implies full process validation when only a reduced model is
  implemented.
- A documentation table claims a status that is not present in code.

## Output

Record findings with:

- Severity: P0, P1, P2, or P3.
- Evidence file and line or notebook cell.
- Impact on interpretation.
- Recommended next action.
