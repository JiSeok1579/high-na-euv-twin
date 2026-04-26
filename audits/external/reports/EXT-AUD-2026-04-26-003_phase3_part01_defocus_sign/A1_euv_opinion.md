# EUV Expert Opinion — Phase 3 Part 01: Defocus Sign Convention (PR #5)

## 메타
- 감사 ID: EXT-AUD-2026-04-26-003
- 감사 단계: Stage 1 / Individual
- 전문가 시각: **EUV (물리 + 도메인)**
- 감사 날짜: 2026-04-26
- 대상: PR #5 (squash merge `9ee22bb`) — Phase 3 entry: defocus 부호 컨벤션 fix (MT-006)
- 코더 보고: pytest --cov 14 passed, ruff/mypy/compileall pass, GitHub CI 전체 통과

---

## 1. 발견사항 (Findings)

### F-EUV-01 — 부호 컨벤션 명시·일관·테스트 가능 ★
- `docs/phase3_design.md §2` 표 형식으로 4개 항목 명시:
  - `z = 0` = 명목 best-focus 평면
  - `defocus_m > 0` = wafer 가 best focus 위 (toward projection optics)
  - `defocus_m < 0` = wafer 가 best focus 아래
  - 위상식: `φ_defocus(ρ) = +π · defocus_m · NA² / λ · ρ²`
- **본 프로젝트 D5 결정 원칙 충실 준수**: 한 번 정하면 변경 비용 매우 큰 컨벤션을 코드 작성 전 fix + docs/code/tests 3중 기록

### F-EUV-02 — Fresnel 위상식 수식 정확
- `φ = π · z · NA² / λ · ρ²` 는 paraxial defocus aberration 의 표준 형태
- ρ = 1 (pupil edge) 에서 φ = π · z · NA² / λ
  - 예: z = 20 nm, NA = 0.55, λ = 13.5 nm → φ = π · 0.4485 ≈ 1.41 rad
  - 합리적 범위 (수 라디안 이하), phase wrap 위험 없음
- 부호: `+z` (wafer 가 광원/optics 쪽으로) → `+phase` 추가 — 컨벤션 합리적

### F-EUV-03 — DefocusConvention dataclass 가 문서화 artifact
- `src/wafer_topo.py:25-34` 의 `DefocusConvention` dataclass:
  - `positive_z = "wafer surface above nominal best focus"`
  - `positive_z_direction = "toward projection optics"`
  - `phase_equation = "+pi * defocus_m * NA^2 / wavelength * rho^2"`
- **혁신적 패턴**: 컨벤션을 코드 객체로 표현 → IDE/REPL에서도 조회 가능
- 다른 모듈이 import 시 자동으로 컨벤션 docstring 노출

### F-EUV-04 — 5개 테스트가 핵심 EUV 거동 모두 cover
| 테스트 | EUV 검증 항목 |
|--------|----------------|
| `test_defocus_phase_sign_convention_is_fixed` | 부호 정합성 + ρ=1 edge 위상값 |
| `test_height_to_defocus_uses_focus_plane_reference` | 높이→defocus 변환 |
| `test_defocus_pupil_phase_conjugates_for_opposite_signs` | conjugacy 대칭성 |
| `test_build_pupil_applies_expected_edge_phase` | pupil 통합 정확성 |
| `test_zero_defocus_preserves_phase1_aerial_image` | Phase 1 회귀 차단 |

- 특히 conjugacy 테스트는 **물리적 reciprocity** 검증 (Hermitian 광학계 가정 유효)
- zero-defocus regression test 는 backward compatibility 보장

### F-EUV-05 — 단순화 P3-L1 ~ L4 명시 (`docs/phase3_design.md §4`)
| ID | 단순화 | 다음 작업 |
|----|--------|-----------|
| P3-L1 | 상수 defocus 만, spatial z(x,y) 미반영 | Phase 3 focus stack |
| P3-L2 | DOF metric / k₂ fitting 없음 | Phase 3 part 2 |
| P3-L3 | Micro focus-drilling 없음 | Phase 3 part 3 |
| P3-L4 | Scalar coherent (Phase 2/4 deferred) | Phase 2/4 |

**4중 기록 원칙 충실** — 코드 + docs + Limitation 섹션 + 다음 단계 명시.

### F-EUV-06 — 7 단순화 (S1-S7) 변경 없음 + P3-L1-4 추가
- 본 PR 은 Phase 3 entry 만 — Phase 1 단순화 그대로
- 신규 P3-L1 ~ L4 는 Phase 3 범위 내 deferred 항목
- 누적 단순화: 7 → 7 + 4 = 11 (모두 4중 기록)

---

## 2. 위험 (Risks)

### R-EUV-01 — Paraxial 근사의 0.55 NA 정량 한계 (낮음, P3 권고)
- 현재 식: `φ = π · z · NA² / λ · ρ²` (paraxial Fresnel)
- 정확 식: `φ = (2π/λ) · z · (1 - cos θ)` (각도 의존 OPL)
- 0.55 NA 에서 ρ = 1 (sin θ = 0.55, cos θ ≈ 0.835):
  - paraxial: π · z · 0.55² / λ = π · z · 0.3025 / λ
  - full: 2π · z · 0.165 / λ = π · z · 0.33 / λ
  - **paraxial 이 약 9% 과소평가** (z 가 클수록 차이 누적)
- **현재 영향**: Phase 3 part 1 단순 부호 컨벤션 검증에는 무관
- **권고**: Phase 3 part 2 (DOF 정량) 시 정확 식 도입 검토 (P3 P2-NEW)

### R-EUV-02 — Spatial z(x,y) 미구현 (P3-L1, deferred)
- 현재: 상수 defocus 만 PupilSpec.defocus_m 으로 전달
- Phase 3 part 2 에서 wafer height map → 위치별 defocus 가 필요
- **현재 영향**: 본 PR 범위 외, 의도된 deferred

### R-EUV-03 — 부호 컨벤션 변경 비용 (높음, mitigation 됨)
- 한 번 정한 부호를 후속 Phase 5/Phase 3 part 2/3 에서 변경하면 모든 의존 코드 + 테스트 + docs 수정 필요
- **mitigation**: 본 PR 에서 docs/phase3_design.md §2 에 명시 + 5개 테스트로 강제 + DefocusConvention dataclass 로 객체화 → **변경 시도 시 즉시 실패**

---

## 3. 권고 (개별 권고 — 우선순위 시도)

### REC-EUV-01 (P2-신규) — Phase 3 part 02 진입 시 paraxial vs full angular 비교
- 위치: `tests/phase3_DOF.py` 에 추가 또는 `notebooks/2_DOF_topography.ipynb` 에서 시각화
- 내용: 같은 z 에 대해 paraxial Fresnel vs cos θ-based phase 의 contrast/CD 차이
- 효과: 0.55 NA 의 정량 한계 인지
- 작업량: 1시간

### REC-EUV-02 (P2-신규) — 다음 Part 02 에서 DOF 정량 메트릭 + paper #14 비교
- 진행계획서 §4.2 의 K3 (DOF 정량) 시작
- `dof_from_focus_stack()` 함수 + paper #14 의 LCDU 18-42% 향상 정성 재현
- 작업량: 2-3시간

### REC-EUV-03 (P3) — Phase 4 진입 전 paper #12 6 효과 단위 테스트 stub
- EXT-AUD-001 REC-EUV-01 그대로 유지
- 작업량: 30분

---

## 4. 본 전문가가 답하지 않는 영역

- **AI 전문가**: Fresnel 식의 numerical implementation 안정성, conjugacy property 의 floating-point 정확성
- **Software 전문가**: 새 모듈 `wafer_topo.py` 의 의존 그래프, DefocusConvention dataclass 의 적정성
- **Data Scientist**: 누적 단순화 11개의 추세, 위험 지수 변화

---

## 5. 한 줄 요약 판정

**🟢 PASS (clean, with P2 note)** — Phase 3 entry 의 핵심 부호 컨벤션이 코드/문서/5 테스트 3중 강제 + DefocusConvention dataclass 로 객체화되어 D5 원칙 모범 사례 달성. 5/5 EUV smoke test 통과. Paraxial 근사의 0.55 NA ~9% 정량 한계는 Phase 3 part 02 (DOF 정량) 진입 시 정확 식 비교 권고 (P2-신규).
