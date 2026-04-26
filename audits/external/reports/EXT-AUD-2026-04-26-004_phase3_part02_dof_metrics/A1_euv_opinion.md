# EUV Expert Opinion — Phase 3 Part 02: DOF Metrics

## 메타
- 감사 ID: EXT-AUD-2026-04-26-004
- 감사 단계: Stage 1 / Individual
- 전문가 시각: **EUV (물리 + 도메인)**
- 감사 날짜: 2026-04-26
- 대상: 자동 트리거 — Phase 3 Part 02 (MT-008~010 + DOF metrics)
- 트리거: REVIEWER_DIRECTIVE v2.1 §10.5 (자동 외부감사)

---

## 1. 발견사항 (Findings)

### F-EUV-01 — Paraxial vs Angular OPL 비교 옵션 정확 (MT-008)
- `wafer_topo.py:53-92` 의 `defocus_phase_radians(approximation: "paraxial" | "angular")`
- Paraxial 식 (Part 01 그대로): `φ = π · z · NA² / λ · ρ²`
- Angular 식 (신규): `φ = 2π · z / λ · (1 - cos θ)`, `sin θ = NA · ρ`
- **물리적 의미**:
  - paraxial: 작은 각도 근사, `1 - cos θ ≈ θ²/2 ≈ (NA·ρ)²/2`
  - angular: 정확한 wavefront sphere geometric path
  - 0.55 NA pupil edge: paraxial ~9% 과소평가 (EXT-AUD-003 R-EUV-01 와 일치)
- `test_full_angular_defocus_matches_paraxial_small_angle_limit` 가 ρ → 0 에서 두 식 일치 자동 검증 ★

### F-EUV-02 — `validate_defocus_sampling` (MT-009) 가 물리적 sampling 한계 강제
- `wafer_topo.py:136-158` 의 가드:
  - `max_defocus_phase_step_radians()` 가 인접 ρ 샘플 사이 위상 변화 추정
  - Threshold: `max_phase_step_rad = π / 2` (default)
  - 위반 시 ValueError + 권고: "Increase grid_size or reduce defocus_m"
- **물리적 의미**: 큰 defocus + 작은 grid → pupil phase 의 ρ² 항이 fast oscillation → grid 가 표현 불가 → aliasing → 비물리적 결과
- `test_defocus_sampling_guard_rejects_under_sampled_phase` 가 자동 검증

### F-EUV-03 — DOF Metric 정직 — Nominal process window 한정
- `dof.py` 의 `nominal_depth_of_focus()` 가 명시적 단순화:
  - 전체 max contrast 가 아닌 **`reference_defocus_m = 0` 근방의 sample 을 reference 로 사용**
  - 이유: coherent scalar 시뮬에서 remote contrast revival 가능 → 비연속 process window 위험
- `docs/phase3_DOF_analysis.md §2` 명시:
  > "in coherent scalar simulations, remote contrast revivals can occur, but they are not part of the contiguous nominal process window."
- **물리적 정직**: 실제 산업 process window 정의 (k₃ 같은 coherent revival 무시) 와 일치

### F-EUV-04 — KPI K3 정직 보고 — measurable but not complete
- `docs/phase3_DOF_analysis.md §4` 가 KPI K3 의 현 상태를 명확히:
  > "KPI K3 is now measurable but not complete. Completion still requires a broader focus sweep and reported `k2` estimate"
- **과대주장 차단**: focus stack metrics 추가 = K3 enabler, K3 정량 진척은 다음 increment

### F-EUV-05 — Conjugacy 대칭성 자동 검증
- `test_focus_stack_contrast_is_symmetric_for_opposite_defocus` (신규)
- 광학 시스템의 시간 반전 대칭성 (Hermitian wavefront) 검증
- ±dz 에서 contrast 가 동일해야 함 → 식의 부호 정확성 + 수치 안정성 동시 검증

### F-EUV-06 — `DefocusConvention` dataclass 확장
- `wafer_topo.py:35` 에 `angular_phase_equation: str = "+2pi * defocus_m / wavelength * (1 - cos(theta))"` 필드 추가
- **EXT-AUD-003 의 dataclass 패턴 일관 유지** — 컨벤션의 객체화 모범 사례 강화

---

## 2. 위험 (Risks)

### R-EUV-01 — k₂ fitting 미구현 (낮음, 의도된 deferred)
- `docs/phase3_DOF_analysis.md §4` 가 명시: 다음 increment 의 작업
- KPI K3 는 measurable 만, 정량 진척 (k₂ 값 보고) 까지가 합격선
- **현재 영향**: 본 PR 의 책임 외, Phase 3 다음 part 에서 처리

### R-EUV-02 — `nominal_depth_of_focus` 가 80% threshold 단일 사용 (낮음)
- `threshold_fraction: float = 0.8` default
- 산업 표준은 process window 정의에 따라 다름 (보통 5-10% CD 변화 기준)
- **현재 영향**: contrast threshold 와 CD-based DOF 의 1:1 매핑 미명시
- **권고**: docs/ 에 contrast 0.8 ↔ CD 변화 정량 매핑 추가 (P3)

### R-EUV-03 — 0.55 NA 에서 paraxial 의 ~9% 오차가 default (낮음, 옵션 제공됨)
- `defocus_phase_radians()` default = "paraxial"
- 0.55 NA 에서 paraxial 부정확성 알려져 있음 (EXT-AUD-003)
- 그러나 `approximation="angular"` 옵션으로 우회 가능
- **권고**: Phase 3 part 03 진입 시 default 를 `"angular"` 로 전환 검토 (P2)

---

## 3. 권고 (개별 권고 — 우선순위 시도)

### REC-EUV-01 (P1-신규) — Phase 3 part 03 또는 다음 increment 에서 k₂ fitting 보고
- 위치: `docs/phase3_DOF_analysis.md §4` 표 갱신 + `notebooks/2_DOF_topography.ipynb`
- 내용: NA 0.33 vs 0.55, pitch 32-50 nm 범위 sweep → k₂ 측정값 ± 오차
- 효과: KPI K3 정량 진척 (33% → 50%)
- 작업량: 2-3시간

### REC-EUV-02 (P2-신규) — angular 를 default approximation 으로 전환
- 0.55 NA 에서 paraxial 의 ~9% 한계 회피
- backward compat: `approximation: DefocusApproximation = "paraxial"` 가 사용자 명시 시 유지
- 작업량: 30분

### REC-EUV-03 (P3-신규) — contrast threshold ↔ CD 변화 매핑 명시
- 80% contrast threshold 가 어떤 CD 오차에 대응하는지 docs/ 에 표
- 작업량: 1시간

### REC-EUV-04 (P3) — Paper #14 의 LCDU 18-42% 향상 정성 재현
- 0.33 vs 0.55 NA 에서 simulator의 contrast vs defocus 비교
- 작업량: 1-2시간

---

## 4. 본 전문가가 답하지 않는 영역

- **AI 전문가**: `validate_defocus_sampling` 의 π/2 threshold 합리성, focus_stack_contrast 의 numerical stability
- **Software 전문가**: `dof.py` 의 dataclass 설계, helper 함수 분리
- **Data Scientist**: KPI K3 진척률 정량화, MT-008~010 처리 품질, 4-point 추세

---

## 5. 한 줄 요약 판정

**🟢 PASS (clean, with P1 follow-up)** — Phase 3 Part 02 가 paraxial vs angular 옵션 + sampling guard + DOF metric 을 모두 물리적으로 정직하게 구현. KPI K3 의 현 상태를 "measurable but not complete" 로 정직 보고. k₂ fitting 은 다음 increment 의 명확한 책임 (P1-신규 REC-EUV-01).
