# AI / Numerical Expert Opinion — Phase 3 Part 02

## 메타
- 감사 ID: EXT-AUD-2026-04-26-004
- 감사 단계: Stage 1 / Individual
- 전문가 시각: **AI / Numerical**
- 감사 날짜: 2026-04-26

---

## 1. 발견사항 (Findings)

### F-AI-01 — `validate_defocus_sampling` 합리적 Nyquist-style 가드 (MT-009)
- `wafer_topo.py:113-158` 의 두 함수:
  - `max_defocus_phase_step_radians()`: 인접 ρ 샘플 위상차의 max
  - `validate_defocus_sampling()`: π/2 default threshold 강제
- **이론적 근거**: phase step > π → discrete 표현 시 sign ambiguity → numerical instability
- π/2 default 는 conservative — 실제 위험은 π 까지지만 안전 여유 확보
- 위반 시 actionable error message: "Increase grid_size or reduce defocus_m"

### F-AI-02 — `np.clip(rho, 0, 1)` 안전 처리 ★
- `wafer_topo.py:86`, `:90` 에서 ρ 입력 boundary clipping
- 사용자가 ρ > 1 (outside pupil) 또는 ρ < 0 (invalid) 전달 시:
  - paraxial 식: ρ² 가 monotonic increase → 큰 값 폭발 가능
  - angular 식: `sin θ = NA · ρ > 1` → `sqrt(1 - sin²θ)` 가 NaN
  - **clipping 으로 NaN 방지 + ρ ∈ [0, 1] 정상 도메인 강제**

### F-AI-03 — Defocus invariant 자동 검증 (MT-010, 2 신규)
| 테스트 | 검증 |
|--------|------|
| `test_defocus_phase_is_unitary` | `|exp(iφ)| = 1` 모든 ρ, 모든 defocus 에서 |
| `test_zero_defocus_phase_is_identity` | `defocus_pupil_phase(rho, 0) == 1+0j` 모든 ρ |

- **이전 conjugacy 테스트 (Part 01) 와 합쳐 4-property 완전성**:
  - unitary (modulus = 1)
  - identity (zero defocus → identity)
  - conjugacy (opposite signs)
  - sign convention (ρ=1 edge phase value)
- FFT optical chain 의 Hermitian preservation 자동 검증

### F-AI-04 — DOF Metric의 Numerical Robustness
- `nominal_depth_of_focus()` 가 다음 case 모두 처리:
  - reference_contrast ≤ 0 → normalized = 0 (division by zero 회피)
  - reference 부터 한쪽 끝까지 threshold 미만 부재 → `lower_defocus_m = None`
  - 양쪽 모두 부재 → `dof_m = None`
- `_linear_crossing()` 가 `y0 == y1` 케이스 (flat region) 정확 처리

### F-AI-05 — `replace(pupil_spec, defocus_m=...)` 패턴
- `dof.py:52` 가 `dataclasses.replace` 사용
- frozen dataclass 의 정상 mutation 패턴 — immutability 유지하며 새 인스턴스 생성
- focus stack 의 각 sample 이 독립 PupilSpec 가짐 → 부작용 없음

### F-AI-06 — 20개 테스트 PASS (lastfailed = `{}`)
- `.pytest_cache/v/cache/lastfailed = {}` 직접 확인
- 14 → 20 (+6 신규)
- Phase 1: 5 (회귀 보호), Phase 3: 9 (sign + sampling + dof + symmetry), audits: 6 (FFT + defocus invariants)

### F-AI-07 — `int(np.argmin(np.abs(defocus - reference_defocus_m)))`
- `dof.py:92` 가 reference sample 선정
- defocus 배열에서 0 (또는 사용자 지정) 에 가장 가까운 sample
- **수치적**: float 비교 대신 거리 최소화 → robust

---

## 2. 위험 (Risks)

### R-AI-01 — π/2 sampling threshold 의 conservativeness 측정 부재 (낮음, P3)
- π/2 가 안전하지만 실제 시뮬에서 얼마나 보수적인지 정량 평가 부재
- 일부 정상 case 가 false-rejected 가능
- **권고**: P3 backlog — empirical false-rejection rate 측정

### R-AI-02 — focus_stack 의 grid_size auto-resolution
- `dof.py:48`: `pupil_spec is None` 시 `PupilSpec(grid_size=max(mask_grid.nx, mask_grid.ny))`
- **잠재 issue**: 큰 defocus + auto grid_size 가 sampling validation 을 violate 가능
- 그러나 `aerial_image()` 가 이미 Nyquist + sampling 검증 → silent failure 위험 낮음

### R-AI-03 — `tuple(sorted(...))` 의 비교 안정성
- `dof.py:84`: `sorted(samples, key=lambda sample: sample.defocus_m)`
- 사용자가 동일 defocus 값을 중복 입력 시 순서 결정성 불확실
- **현재 영향**: 매우 드문 케이스, 영향 미미

### R-AI-04 — Angular approximation 의 piston 처리
- `wafer_topo.py:92`: `2π · z / λ · (1 - cos θ)` — `(1 - cos)` 가 자연스럽게 ρ=0 에서 0
- piston (ρ=0 phase) 가 0 → paraxial 과 일치
- 별도 piston 제거 로직 불필요 — 식 자체로 처리됨 ★

---

## 3. 권고 (개별 권고 — 우선순위 시도)

### REC-AI-01 (P2-신규) — `dof.py` 에 grid resolution 자동 검증 통합
- `focus_stack_contrast()` 가 큰 defocus 입력 시 자동 `validate_defocus_sampling()` 호출
- 작업량: 30분

### REC-AI-02 (P3-신규) — Sampling threshold (π/2) empirical tuning
- 다양한 defocus + grid 조합에서 false rejection rate 측정
- π/2 → 더 큰 값 (예: 0.8π) 으로 완화 검토
- 작업량: 1-2시간

### REC-AI-03 (P3) — `_linear_crossing()` 의 monotonicity assumption 명시
- 현재 두 sample 사이 contrast 가 monotonic decrease 를 가정
- non-monotonic case (revival) 에서 first crossing 만 사용
- docs/ 또는 docstring 에 명시
- 작업량: 30분

---

## 4. 본 전문가가 답하지 않는 영역

- **EUV 전문가**: 80% threshold 의 산업 적합성, k₂ fitting 의 광학적 의미
- **Software 전문가**: `dof.py` 의 모듈 분리 정당성, helper 명명
- **Data Scientist**: 4-point 추세, KPI K3 정량 진척률, mitigation 처리 누적

---

## 5. 한 줄 요약 판정

**🟢 PASS (clean)** — MT-008/009/010 모두 깨끗하게 처리. `validate_defocus_sampling` 가 conservative π/2 threshold 로 numerical robustness 확보. 4-property 자동 검증 (unitary + identity + conjugacy + sign) 으로 광학 chain Hermitian preservation 보장. ρ clipping + np.clip 안전 처리 모범. 20/20 tests PASS.
