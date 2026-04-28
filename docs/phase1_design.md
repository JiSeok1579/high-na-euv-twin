# Phase 1 Design - Scalar Fourier Optics

Status: implemented baseline
Last updated: 2026-04-28

Phase 1 establishes the minimum optical path needed by later phases.

## Modules

- `src/constants.py` defines common physical constants.
- `src/mask.py` builds simple binary mask patterns.
- `src/pupil.py` builds annular pupil functions.
- `src/aerial.py` computes scalar Fourier aerial images.

## Model

The baseline model uses scalar Fourier optics:

```text
mask field -> FFT -> pupil filter -> inverse FFT -> intensity
```

The implementation supports a study-grade anamorphic projection option. It does
not claim full vector EM, scanner calibration, or rigorous mask 3D physics.

## Acceptance

- A line-space mask can produce a finite aerial image.
- The pupil is bounded and normalized.
- Intensity is non-negative.
- Anamorphic coordinate scaling is explicit.
- Tests cover shape, finite values, and basic qualitative behavior.

## Downstream Dependencies

- Phase 3 uses aerial images for focus-stack and DOF studies.
- Phase 5 uses aerial images as the resist exposure input.
- Phase 6 uses the forward path inside the optimization objective.
