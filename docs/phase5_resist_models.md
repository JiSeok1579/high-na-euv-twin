# Phase 5 - Threshold Resist MVP

## 1. Scope

Phase 5 MVP closes the first full mask-to-print pipeline:

```text
line/space mask -> aerial image -> focus slice -> threshold resist -> CD/EPE
```

The resist model is deliberately Level 0. A pixel is exposed when:

```text
dose * I(x, y) > threshold
```

Chemical blur, depth-resolved development, and stochastic LWR are deferred to
Phase 5 L1-L3.

## 2. Implemented Functions

| Function | Role |
|----------|------|
| `threshold_resist(...)` | Converts a normalized aerial image into a boolean exposed map. |
| `dose_to_clear(...)` | Computes the scalar dose needed to clear a pixel at a given intensity. |
| `critical_dimension(...)` | Measures mean foreground run width on a 1-D printed line. |
| `edge_positions(...)` | Extracts binary transition edges for EPE measurement. |
| `mean_absolute_epe(...)` | Compares printed and target edge positions. |
| `dose_cd_curve(...)` | Generates an MVP CD-dose curve from a 1-D aerial profile. |
| `michelson_contrast(...)` | Reuses the Phase 1 image contrast metric. |
| `normalized_image_log_slope(...)` | Reuses the Phase 1 NILS metric. |

## 3. Verification

The Phase 5 MVP tests cover:

- exact `dose * intensity > threshold` behavior
- invalid dose, threshold, and negative intensity rejection
- CD extraction from binary printed runs
- EPE extraction from target and printed edges
- monotonic exposed CD growth with dose
- resolved line/space target CD within 10%
- Phase 1 + Phase 3 + Phase 5 end-to-end pipeline

Current MVP target:

| Case | Target | Result |
|------|--------|--------|
| 80 nm pitch, 50% duty | 40 nm clear CD | <= 10% CD error |
| Dose sweep | exposed CD monotonic with dose | PASS |
| End-to-end | mask -> printed pattern | PASS |

## 4. Limitations

| ID | Limitation | Deferred To |
|----|------------|-------------|
| P5-L1 | No acid/quencher diffusion or post-exposure bake blur. | Phase 5 L1 |
| P5-L2 | No depth-resolved resist stack or focus-depth coupling. | Phase 5 L2 |
| P5-L3 | No stochastic photon/chemistry Monte Carlo or LWR distribution. | Phase 5 L3 |
| P5-L4 | Printed output is a boolean exposed map, not a developed 3-D resist profile. | Phase 5 L2-L3 |

## 5. Exit Status

KPI K1 is complete for the MVP pipeline. The simulator can now propagate a
line/space mask through aerial imaging, Phase 3 focus handling, threshold
resist, and CD/EPE metrics.
