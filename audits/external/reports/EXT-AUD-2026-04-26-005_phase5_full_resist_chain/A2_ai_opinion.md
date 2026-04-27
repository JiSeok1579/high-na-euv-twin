# AI / Numerical Expert Opinion — Phase 5 Full Resist Chain

## 메타
- 감사 ID: EXT-AUD-2026-04-26-005
- 감사 단계: Stage 1 / Individual
- 전문가 시각: **AI / Numerical**
- 감사 날짜: 2026-04-26

---

## 1. 발견사항 (Findings)

### F-AI-01 — `np.random.Generator` 모던 API + seed 제어
- `resist_stochastic.py:115`: `np.random.default_rng()` 사용 — legacy `np.random.seed` 회피
- `monte_carlo_lwr_curve(seed=...)` 로 reproducibility 보장
- `test_monte_carlo_lwr_curve_is_reproducible_with_seed` 자동 검증

### F-AI-02 — Poisson sampling at each stochastic stage ★
- 4-stage chain 의 각 단계가 `generator.poisson(λ)` 사용
- **이론적 근거**: photon arrival, secondary electron generation, acid generation 모두 독립 Poisson process
- 합리적 Markov chain MC 모델

### F-AI-03 — Convergence Gate 견고
`monte_carlo_convergence_gate(trial_counts=(100, 300, 1000), tolerance=0.10, min_trials=1000)`:
- **3-point progressive**: 100 → 300 → 1000 trials
- **Relative LWR change** < 10% → converged
- **min_trials gate**: 1000 미만이면 자동 fail
- `test_monte_carlo_convergence_gate_accepts_1000_trial_stable_lwr` + `_fails_tight_tolerance` + `_rejects_invalid_gate_inputs` 3가지 자동 검증

### F-AI-04 — Bessel correction (`ddof=1`) 정확 사용
- `np.std(cd_array, ddof=1)` (line 197) — 표본 분산 (N-1 분모)
- `lwr_m = 3.0 * std_cd_m` — 3σ multiplier 명시적
- **수치적**: small-N MC 에서 표본 분산 편향 회피

### F-AI-05 — `acid_normalizer` 가 계산 stable
`resist_stochastic.py:127-131`:
```python
acid_normalizer = (
    photon_density · SE_yield · acid_yield
)
chemical_signal = acid_count / acid_normalizer
```
- division-by-zero 방지: 모든 yield 가 `_validate_positive_finite()` 통과 후
- normalize 가 chain 전체 amplification 의 평균 → 신호의 dimensionless ratio

### F-AI-06 — Material threshold sampling 의 physical bound 강제
`_sample_material_thresholds()`:
```python
thresholds = generator.normal(loc=clearing_threshold, scale=sigma)
return np.clip(thresholds, 0.0, 1.0)
```
- 정규분포 → [0, 1] clip — 비물리적 음수/초과 1 차단
- **σ = 0** 시 deterministic constant — backward compat

### F-AI-07 — Grid search calibration의 합리성
`calibrate_stochastic_lwr_budget()`:
- 2D parameter space (optical_coeff × material_coeff)
- 기본 grid: `center * np.linspace(0.25, 2.5, 46)` — 46×46 = 2116 points
- 합리적 brute force (gradient-free, 매끄러운 loss surface)
- RMS + max abs 동시 보고

### F-AI-08 — Robust 입력 검증 (Phase 1-3 패턴 일관)
모든 public 함수에 `_validate_*` helper:
- `_validate_positive_finite(value, name)` — NaN/Inf/zero/negative 차단
- `_validate_pixel_size(pixel_size_m)` — 양수 유한 강제
- `_as_nonnegative_image()` — aerial intensity ≥ 0 강제
- `_as_positive_vector()`, `_as_nonnegative_vector()` — vector 변환 + 검증

EXT-AUD-001~004 의 검증 패턴 그대로 일관 — robust 시스템 수렴.

### F-AI-09 — 64/64 tests PASS — `lastfailed = {}`
- 이전 20 → 현재 64 (+220% 증가) ★
- Phase 5: threshold 6 + blur 10 + depth 10 + stochastic 9 = 35
- Phase 3 추가: focus drilling 2 + k₂ fitting 3 = 5
- audits: 6
- integration: 2 (KPI K1)

### F-AI-10 — Stochastic chain 의 Numerical stability
`deprotection_fraction = 1 - exp(-gain · chemical_signal)`:
- `exp(-x)` 가 x ≥ 0 → [0, 1] bound
- `gain` 이 매우 클 경우에도 deprotection ≤ 1 보장
- saturation behavior — 물리적

---

## 2. 위험 (Risks)

### R-AI-01 — `monte_carlo_convergence_gate` 의 (100, 300, 1000) hardcoded default (낮음)
- 사용자가 `trial_counts` 인자로 override 가능하지만 default 가 fix
- 실제 calibration 시 더 큰 trial 필요 가능 (예: 5000+)
- **권고**: docs 에 default rationale 명시 (P2)

### R-AI-02 — Calibration grid 의 중심값 하드코딩
- `_coefficient_grid(values_m=None)` 시 `center * linspace(0.25, 2.5, 46)`
- 측정값이 default coefficient 와 매우 멀면 grid 가 cover 못 함
- **권고**: 사용자가 명시적 grid 제공할 때 warning 또는 expansion (P3)

### R-AI-03 — Float precision in `_linear_crossing` (Phase 3 dof.py 와 동일, 변경 없음)
- EXT-AUD-003 의 R-AI-* 그대로

### R-AI-04 — Stochastic chain 의 large-array memory
- 4-stage chain 이 각 stage 별 array 저장 (`StochasticExposure` dataclass 의 6 fields)
- 큰 grid (e.g., 4096²) × 1000 trials = 16 GB 추정 → memory pressure
- 현재 테스트는 작은 grid (e.g., 512×64) 라 무관
- **권고**: production-scale 사용 시 dataclass 의 field 선택적 storage (P3)

### R-AI-05 — Validate 함수의 코드 중복
- `resist_stochastic.py` 와 `metrics.py` 에 유사한 `_validate_pixel_size` 등 중복
- DRY 위배 (Software 시각과 consensus)
- **권고**: `src/_validation.py` 또는 `src/utils.py` 모듈로 추출 (P2)

---

## 3. 권고 (개별 권고)

### REC-AI-01 (P2-신규) — `_validate_*` helper 를 `src/utils.py` 로 통합
- 코드 중복 제거 + Phase 4-6 진입 시 재사용 baseline
- 작업량: 1시간

### REC-AI-02 (P2-신규) — Convergence gate default 의 docs 설명
- (100, 300, 1000) trial counts + 10% tolerance 의 rationale
- 작업량: 20분

### REC-AI-03 (P3-신규) — Calibration grid 의 user-provided grid validation
- 사용자가 너무 좁은 grid 제공 시 warning
- 작업량: 30분

### REC-AI-04 (P3-신규) — Large-array memory 모니터링
- production scale 시 PaaS 사용 mode (selective storage)
- 작업량: 2시간

---

## 4. 본 전문가가 답하지 않는 영역

- **EUV 전문가**: paper #1 smile shape 의 물리적 정확성, paper #21 chain 의 도메인 적정성
- **Software 전문가**: 모듈 539줄의 분리 가능성, dataclass 7개의 구조
- **Data Scientist**: 5-point 추세, KPI 진척, 3D 시각화 권고

---

## 5. 한 줄 요약 판정

**🟢 PASS (clean)** — `np.random.Generator` 사용 + Poisson sampling + Bessel correction + convergence gate 모두 모범 사례. 64/64 tests PASS, lastfailed `{}`. 견고한 입력 검증 패턴이 EXT-AUD-001-004 의 일관 패턴과 수렴. validate helper 중복 (P2 권고) 외 즉시 차단 항목 없음.
