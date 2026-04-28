# AI and Numerical Audit Instructions

Status: active
Last updated: 2026-04-28

Review numerical stability, sampling, stochastic behavior, and optimization
claims.

## Checkpoints

- FFT sampling and grid spacing are adequate for the claimed frequency content.
- Arrays are finite and have deterministic shapes.
- Random paths use explicit seeds where reproducibility matters.
- Loss functions are finite and decomposed into interpretable terms.
- Optimization variables stay bounded.
- Notebook sweeps print sample counts and min/max values.

## Red Flags

- Contrast is constant across a sweep without explanation.
- Best focus is pinned to a sweep edge in a symmetric baseline.
- Dose or intensity contains NaN, Inf, or unexpected negative values.
- A stochastic result is shown without seed or repeated-sample context.
- An optimizer result is judged only by visual appearance.

## Output

Provide severity, evidence, numerical risk, and a minimal validation command.
