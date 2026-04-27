# EUV Expert Opinion — Phase 5 Full Resist Chain + KPI K1 진척

## 메타
- 감사 ID: EXT-AUD-2026-04-26-005
- 감사 단계: Stage 1 / Individual
- 전문가 시각: **EUV (물리 + 도메인)**
- 감사 날짜: 2026-04-26
- 트리거: REVIEWER_DIRECTIVE v2.1 §10.5 자동 외부감사

---

## 1. 발견사항 (Findings)

### F-EUV-01 — Phase 5 4-level 완성 (★ 진행계획서 P1 원칙 모범)
| Level | 모듈 | 책임 |
|-------|------|------|
| L0 | `resist_threshold.py` | `dose * I > threshold` 단순 binary |
| L1 | `resist_blur.py` | Gaussian chemical blur (σ ≈ 2-4 nm, paper #4 PSCAR/CAR) |
| L2 | `resist_depth.py` | depth-resolved absorption, top vs bottom 비대칭 (paper #20, #13) |
| L3 | `resist_stochastic.py` | 4-stage Markov chain MC (paper #21) + LWR decomposition (paper #1) |

진행계획서 §4.5 의 4 level 진행이 1:1 매핑.

### F-EUV-02 — Paper #21 의 4-stage Markov chain 정확 구현 ★
`resist_stochastic.py:117-145`:
```
photon_count = Poisson(dose · I · photon_density)
secondary_electron_count = Poisson(photon_count · SE_yield)
acid_count = Poisson(secondary_electron · acid_yield)
deprotection = 1 - exp(-gain · acid / normalizer)
printed = deprotection > threshold_map
```
- 각 단계 Poisson sampling — paper #21 의 stochastic chain 정확 구현
- threshold_map 이 material_threshold_sigma 기반 spatial randomness — material stochastics 분리

### F-EUV-03 — Paper #1 의 "Smile" LWR Decomposition 정확 구현 ★
`resist_stochastic.py:382-396`:
```
optical_lwr_m  = optical_coeff / sqrt(dose · cd_ratio)    # 저전류 dominant
material_lwr_m = material_coeff * sqrt(dose · cd_ratio)   # 고전류 dominant
cross_term_m2  = -cross_compensation * optical * material  # negative (smile!)
total_variance = optical² + material² + cross_term
```
- **paper #1 의 핵심 발견 정확 재현**: 저전류 optical 지배, 고전류 material 지배, 두 효과 partial compensation
- `test_lwr_budget_reproduces_optical_material_smile_shape` 가 자동 검증
- KPI K6 합격선 도달

### F-EUV-04 — KPI K1 (End-to-end) 100% 합격
`tests/integration_end_to_end.py:test_phase1_phase3_phase5_mvp_end_to_end_pipeline`:
```
80 nm pitch L/S mask
  → aerial_image (NA 0.55, focus drilling)
  → threshold_resist (dose=1.0, threshold=0.2)
  → printed CD within 10% of target_cd
  → mean_abs_epe ≤ 10% target_cd
  → contrast > 0.90
  → NILS > 1.0
```
- **mask → printed pattern 전체 pipeline 자동 검증** ★
- L1 blur version 도 동일 통과 (`test_phase5_l1_blurred_pipeline_keeps_resolved_cd_within_tolerance`)

### F-EUV-05 — KPI K3 추가 진척 — k₂ Fitting 구현
`tests/phase3_DOF.py` 신규:
- `test_k2_fit_from_nominal_dof_metrics` — DOF metric 으로부터 k₂ 추출
- `test_k2_fit_matches_rayleigh_depth_of_focus_sweep` — Rayleigh DOF 식 검증
- `test_k2_fit_rejects_large_rayleigh_error` — 한계 오차 거부

진행계획서 K3 합격선 (`오차 ≤ 30 %`) 적용 가능.

### F-EUV-06 — Phase 3+5 통합: focus drilling
- `dof.py:focus_drilling_average()` 신규 (단일 슬라이스 + weighted average)
- Phase 5 depth-resolved (L2) 와 자연 결합 가능
- `test_focus_drilling_single_slice_matches_aerial_image` 가 회귀 차단

### F-EUV-07 — Material threshold sigma → spatial randomness
`_sample_material_thresholds()` 가 정규분포 + clip(0, 1)
- 물리적 의미: 분자 수준 acid 임계값의 stochastic distribution
- threshold_sigma = 0 시 deterministic 으로 회귀 — backward compat

### F-EUV-08 — Calibration framework 완비
`calibrate_stochastic_lwr_budget()`:
- 측정값 → optical/material coeff 그리드 서치
- RMS error + max abs error 보고
- **paper #1 의 측정값과 비교 가능한 framework**

---

## 2. 위험 (Risks)

### R-EUV-01 — `cd_ratio = max(cd_m / reference_cd_m, 0.25)` 의 floor 0.25 (낮음, P3)
- 매우 작은 CD 에서 LWR 식이 폭발하지 않도록 floor
- **잠재 영향**: cd 가 reference의 25% 미만 (예: 9 nm @ ref 36 nm) 이면 floor 작동, smile 식의 정확성 손상
- 0.55 NA 에서 9 nm 미만은 비현실적이므로 영향 미미
- **권고**: P3 — 0.25 floor 의 정량 영향 측정

### R-EUV-02 — Threshold 0.25 vs Phase 1/3 의 0.3 (낮음, 의도된 분리)
- Phase 1/3 metrics 는 threshold 0.3 default
- Phase 5 stochastic 은 clearing_threshold 0.25 default
- **의도**: stochastic 모델은 acid distribution 의 cumulative 임계값, threshold metric 과 다른 의미론
- **권고**: docs/phase5_resist_models.md 에 두 threshold 의 의미 차이 명시 (P2)

### R-EUV-03 — paper #20 depth absorption 의 정량 calibration 부재 (낮음, P2)
- L2 `resist_depth.py` 의 attenuation factor 가 합리적이나 paper #20 측정값 비교 부재
- KPI K6 100% 합격은 LWR 진척 — depth 측면은 진척 미정의
- **권고**: docs 에 depth 정량 검증 follow-up 명시

### R-EUV-04 — Paper #18 의 OOB radiation, Paper #8 LPP spectrum 미연계 (S3 변함없음)
- 단순화 S3 (monochromatic) 그대로
- 본 PR 은 resist 측면, 광원 측면은 변함 없음
- **현재 영향**: 없음

---

## 3. 권고 (개별 권고 — 우선순위 시도)

### REC-EUV-01 (P2-신규) — depth absorption paper #20 정량 비교
- `resist_depth.py` 의 attenuation 식과 paper #20 의 측정값 비교
- `docs/phase5_resist_models.md` 에 정량 표 추가
- 작업량: 1-2시간

### REC-EUV-02 (P2-신규) — Threshold 의미 차이 명시
- Phase 1/3 의 threshold 0.3 (intensity threshold) vs Phase 5 stochastic 0.25 (acid threshold) 의 의미 분리 docs 명시
- 작업량: 30분

### REC-EUV-03 (P3) — `cd_ratio` floor 0.25 정량 영향 측정
- 변경 전후 비교 시뮬레이션 + docs 보고
- 작업량: 1시간

### REC-EUV-04 (P3) — paper #14 LCDU 18-42% 향상 정성 재현 (이전 권고 유지)

---

## 4. 본 전문가가 답하지 않는 영역

- **AI 전문가**: Monte Carlo convergence gate, Poisson 샘플링 정확성, calibration grid search 효율
- **Software 전문가**: 7-dataclass 구조, 539-line 모듈 분리, integration test 통합
- **Data Scientist**: KPI K1, K6 진척률 정량화, 5-point 추세, rebrand instruction

---

## 5. 한 줄 요약 판정

**🟢 PASS (clean, exemplary)** — Phase 5 4-level 모두 진행계획서 § P1 원칙대로 정확히 구현. **paper #21 의 4-stage chain + paper #1 의 smile decomposition** 정확 재현. KPI K1 100% (end-to-end) + K6 (LWR smile) 도달 + K3 k₂ fitting 진행. 본 PR 은 본 프로젝트의 **단일 최대 진척** 이며 EUV 도메인 측면 추가 P0/P1 없음. P2/P3 권고는 정밀화 backlog.
