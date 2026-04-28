# Simulation Audit Instructions

Status: active
Last updated: 2026-04-28

Review whether the simulator behaves as an integrated, reproducible workflow.

## Phase Gate Checklist

- Inputs, outputs, and units are documented.
- The module can be run from tests or notebooks.
- The result has a physical sanity check.
- Reduced-model limits are stated.
- README or getting-started navigation is updated when needed.
- CI and local checks pass.
- Audit log status matches the actual repository state.
- Next-phase dependencies are explicit.

## Integration Checks

- Phase 1 aerial image output feeds Phase 3 focus and Phase 5 resist.
- Phase 2 source variables can affect Phase 6 optimization.
- Phase 5 resist penalties can affect the SMO objective.
- Phase 4 M3D terms remain reduced and qualitative unless upgraded.

## Output

Classify the change as ready, ready with risks, or blocked. Include the next
recommended phase action.
