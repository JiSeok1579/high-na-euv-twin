# Phase 5 - Resist Models

## 1. Scope

Phase 5 closes the first full mask-to-print pipeline and then refines the
resist model by levels:

```text
line/space mask -> aerial image -> focus slice -> threshold resist -> CD/EPE
```

Level 0 is threshold resist. A pixel is exposed when:

```text
dose * I(x, y) > threshold
```

Level 1 adds a Gaussian chemical blur approximation before thresholding.
Level 2 adds depth-resolved dose attenuation, focus-depth coupling, and a
deterministic profile/SWA proxy. Stochastic LWR remains deferred to Phase 5 L3.

## 2. Implemented Functions

| Function | Role |
|----------|------|
| `threshold_resist(...)` | Converts a normalized aerial image into a boolean exposed map. |
| `dose_to_clear(...)` | Computes the scalar dose needed to clear a pixel at a given intensity. |
| `gaussian_kernel_1d(...)` | Builds a normalized 1-D Gaussian blur kernel from sigma and pixel size. |
| `gaussian_blur(...)` | Applies separable Gaussian blur to a 1-D line or 2-D aerial image. |
| `blurred_threshold_resist(...)` | Applies Level 1 blur before threshold resist. |
| `blur_dose_sweep(...)` | Evaluates CD, EPE, transition width, and deterministic LWR proxy over sigma-dose grids. |
| `transition_width(...)` | Measures deterministic edge-spread width between two normalized intensity levels. |
| `depth_defocus_values(...)` | Maps top-to-bottom resist depths onto signed focus offsets. |
| `depth_attenuation_factors(...)` | Computes Beer-Lambert top-to-bottom dose factors. |
| `depth_resolved_dose_stack(...)` | Builds a 3-D dose stack from 2-D/3-D aerial intensity. |
| `depth_resolved_threshold_resist(...)` | Thresholds each depth slice into an exposure stack. |
| `top_bottom_dose_asymmetry(...)` | Reports top-vs-bottom mean dose asymmetry. |
| `depth_cd_profile(...)` | Extracts center-line CD and exposed fraction for each resist depth. |
| `sidewall_angle_proxy(...)` | Converts through-resist CD taper into a deterministic SWA proxy. |
| `focus_depth_resolved_resist(...)` | Runs focus-coupled aerial slices and depth-resolved thresholding. |
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

The Phase 5 L1 tests cover:

- Gaussian kernel normalization and symmetry
- constant-dose preservation after blur
- larger sigma broadening deterministic edge spread
- sigma `0` reducing exactly to Level 0 threshold resist
- blurred end-to-end CD staying within the MVP 10% tolerance
- sigma-dose sweep grid output
- LWR proxy increasing with sigma at fixed dose
- LWR proxy decreasing with dose at fixed sigma

The Phase 5 L2 Part 01 tests cover:

- deeper slices mapping to negative defocus
- Beer-Lambert attenuation decay from top to bottom
- top-vs-bottom dose asymmetry in a depth stack
- depth threshold stack shape and boolean exposure behavior
- consistency with Phase 3 `focus_drilling_average(...)` when absorption is zero
- focus-depth summary reporting lower bottom dose under absorption

The Phase 5 L2 Part 02 tests cover:

- center-line CD extraction per depth slice
- constant through-resist CD mapping to a 90 degree vertical wall proxy
- tapered through-resist CD mapping to non-zero edge tilt and lower SWA
- profile metadata validation for stack/depth/line-index consistency
- `focus_depth_resolved_resist(...)` output feeding the profile/SWA proxy path

Current targets:

| Case | Target | Result |
|------|--------|--------|
| 80 nm pitch, 50% duty | 40 nm clear CD | <= 10% CD error |
| Dose sweep | exposed CD monotonic with dose | PASS |
| End-to-end L0 | mask -> printed pattern | PASS |
| End-to-end L1 | mask -> Gaussian blur -> printed pattern | PASS |
| Edge spread | larger sigma -> wider transition band | PASS |
| L1 sweep | sigma-dose -> CD/EPE/LWR proxy table | PASS |
| L2 depth | focus-depth slices -> dose/exposure stack | PASS |
| L2 profile | depth exposure stack -> CD/SWA proxy | PASS |

## 4. Limitations

| ID | Limitation | Deferred To |
|----|------------|-------------|
| P5-L1 | Gaussian blur is deterministic and isotropic; no separate acid/quencher diffusion chemistry. | Phase 5 L1 calibration |
| P5-L5 | LWR proxy is deterministic `transition_width / sqrt(dose)`, not Monte Carlo LWR. | Phase 5 L3 |
| P5-L2 | SWA is a deterministic CD-taper proxy, not a calibrated dissolution/profile simulator. | Phase 5 L2 calibration |
| P5-L3 | No stochastic photon/chemistry Monte Carlo or LWR distribution. | Phase 5 L3 |
| P5-L4 | Printed output is a boolean exposed map plus profile metrics, not a developed 3-D resist volume. | Phase 5 L2-L3 |

## 5. Exit Status

KPI K1 is complete for the MVP pipeline. The simulator can now propagate a
line/space mask through aerial imaging, Phase 3 focus handling, threshold
resist, Gaussian blur, depth-resolved dose, and CD/EPE metrics. Phase 5 L2
Part 02 adds a deterministic through-resist CD profile and SWA proxy; calibrated
dissolution geometry and stochastic LWR remain later targets.
