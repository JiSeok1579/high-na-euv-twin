# AI / Numerical Expert Opinion — Phase 3 Part 01 (PR #5)

## 메타
- 감사 ID: EXT-AUD-2026-04-26-003
- 감사 단계: Stage 1 / Individual
- 전문가 시각: **AI / Numerical**
- 감사 날짜: 2026-04-26
- 대상: PR #5 squash merge `9ee22bb`

---

## 1. 발견사항 (Findings)

### F-AI-01 — 입력 검증 robust
- `defocus_phase_radians()`:
  - `np.isfinite(defocus_m)` (NaN/Inf 차단)
  - `0.0 < na <= 1.0` 강제
  - `wavelength > 0.0` 강제
- `PupilSpec.__post_init__` 에서도 `np.isfinite(defocus_m)` 검증 (이중 안전망)

### F-AI-02 — Conjugacy property 자동 검증 ★
- `test_defocus_pupil_phase_conjugates_for_opposite_signs`:
  ```python
  plus = defocus_pupil_phase(rho, dz)
  minus = defocus_pupil_phase(rho, -dz)
  assert np.allclose(plus, np.conjugate(minus))
  ```
- **수치적 reciprocity** 자동 검증 — floating point 정확성 + 식 대칭성 동시 확인
- `np.allclose` 의 default tolerance (`rtol=1e-5, atol=1e-8`) 충분히 정밀

### F-AI-03 — Zero-defocus 효율적 skip path
- `pupil.py:90-96`:
  ```python
  if spec.defocus_m != 0.0:
      phase *= defocus_pupil_phase(...)
  ```
- defocus = 0 시 불필요한 `np.exp(0)` 계산 제거 → Phase 1 backward compat 유지하며 성능 영향 없음
- `test_zero_defocus_preserves_phase1_aerial_image` 가 이 fast path 의 정확성 자동 검증

### F-AI-04 — float comparison `!= 0.0` 적정성
- 일반적으로 float 의 `== 0.0` 은 위험하지만, 본 use case 에서는:
  - 사용자가 명시적으로 `defocus_m=0.0` 로 전달하거나 default 사용 → 정확히 0
  - 비교 대상이 누적 연산 결과가 아니므로 안전
- **권고 없음** — 적정 사용

### F-AI-05 — 14개 테스트 모두 통과 (5 신규 + 9 기존)
- pytest cache: `lastfailed = {}` ★
- 신규 5개:
  - `test_defocus_phase_sign_convention_is_fixed` — `pytest.approx(rel=default)` 명시
  - `test_height_to_defocus_uses_focus_plane_reference` — `np.allclose`
  - `test_defocus_pupil_phase_conjugates_for_opposite_signs` — Hermitian 검증
  - `test_build_pupil_applies_expected_edge_phase` — pupil 통합
  - `test_zero_defocus_preserves_phase1_aerial_image` — 회귀 차단
- 코더 보고: ruff/mypy/compileall 모두 통과

### F-AI-06 — `defocus_phase_radians` 의 dimensional check
- 단위: `[m] · [1]² / [m] = [1]` (dimensionless) → π 곱 → radian ✓
- 모든 입력 단위 명시적 (m for defocus_m, dimensionless ρ, m for λ)

### F-AI-07 — Numerical noise floor / Nyquist guard 무회귀
- `aerial.py` 의 기존 noise floor + Nyquist 체크 모두 유지
- defocus phase 추가가 기존 안전망에 영향 없음 (pupil 곱셈 단계에서 합성)

### F-AI-08 — `defocus_phase_radians` 식의 ρ² 항이 outer product 안전
- `rho_arr = np.asarray(rho, dtype=np.float64)` 후 `rho_arr**2` 적용
- 1D ρ (테스트), 2D meshgrid ρ (실제 pupil) 모두 작동
- broadcasting 안전

---

## 2. 위험 (Risks)

### R-AI-01 — Paraxial vs full angular OPL 의 numerical 차이 (낮음, EUV 영역과 consensus)
- EUV 전문가 R-EUV-01 와 동일
- 수치 관점: 0.55 NA 에서 ~9% 과소평가
- **권고**: Phase 3 part 02 진입 시 정확 식 옵션 추가 (REC-AI-01)

### R-AI-02 — `pupil.py` 가 `wafer_topo.py` 의존성 추가 (낮음)
- 새 import: `from .wafer_topo import defocus_pupil_phase`
- 의존 그래프:
  ```
  constants ──┬─→ wafer_topo ──┬─→ pupil ─┐
              ├─→ optics ──────┴─→ pupil  │
              └─→ wafer_topo ────→ aerial ┤
  pupil ────────────────────────→ aerial ─┤
  mask ────────────────────────→ aerial ──┘
  ```
- **위험**: 순환 참조 없음 — `wafer_topo` 는 `constants` 만 import
- **현재 영향**: 없음, 깨끗한 DAG 유지

### R-AI-03 — `defocus_pupil_phase` 의 `np.exp(1j * phase)` underflow 가능성 (매우 낮음)
- 매우 큰 |defocus_m| (예: 1 mm) 입력 시 phase 가 큰 값
- `np.exp(1j * phase)` 자체는 정상 작동 (단위 원 위)
- 그러나 후속 분석에서 phase wrap 의 의미가 모호해질 수 있음
- **권고**: large defocus 에 대한 sanity warning 추가 검토 (P3)

### R-AI-04 — Nyquist 가드와 defocus 의 상호작용 미검증 (낮음, P2)
- 큰 defocus 에서 pupil phase 의 ρ² 항이 fast oscillation 생성 가능
- 현재 Nyquist guard 는 NA/λ cutoff 만 검증
- 매우 큰 defocus → pupil phase 가 grid 해상도로 표현 불가 가능
- **권고**: Phase 3 part 02 에서 defocus-aware Nyquist 검증 추가

---

## 3. 권고 (개별 권고 — 우선순위 시도)

### REC-AI-01 (P2-신규) — `wafer_topo.py` 에 정확 식 옵션 추가
- 함수 signature 확장: `defocus_phase_radians(..., approximation: str = "paraxial")`
- `paraxial` (현재) vs `full_angular` (`(2π/λ) · z · (1 - cos θ)`)
- 단위 테스트로 ρ → 0 한계에서 두 식이 일치 검증
- 작업량: 1시간

### REC-AI-02 (P2) — Defocus-aware Nyquist sanity check
- 큰 defocus + 작은 grid → pupil phase aliasing 위험
- `aerial.py` 의 Nyquist guard 에 `nyquist_for_defocus = sqrt(N_grid / (4 · |defocus_m| · NA² / λ))` 같은 추가 조건
- 작업량: 1시간

### REC-AI-03 (P2) — `tests/audits/test_fft_invariants.py` 에 defocus invariant 추가
- `test_defocus_pupil_unitary` — `|exp(iφ)| = 1` 모든 ρ 에서
- `test_defocus_zero_identity` — `defocus_pupil_phase(rho, 0)` 가 모든 ρ 에서 1+0j
- 작업량: 30분

### REC-AI-04 (P3) — Large defocus warning
- |defocus_m| > some threshold (e.g., DOF · 5) 시 logging 또는 warning
- 작업량: 30분

---

## 4. 본 전문가가 답하지 않는 영역

- **EUV 전문가**: Fresnel 식의 물리적 의미, 부호 선택의 광학적 합리성
- **Software 전문가**: 모듈 구조, dataclass 설계, 코드 명명
- **Data Scientist**: 14개 테스트의 종합 coverage, 추세 데이터 통합

---

## 5. 한 줄 요약 판정

**🟢 PASS (clean)** — 입력 검증 + conjugacy 자동 검증 + zero-defocus regression test 가 수치 안정성을 robust 하게 보장. 14/14 pytest pass + ruff/mypy 통과. 0.55 NA paraxial 근사의 ~9% 정량 한계는 EUV 시각과 consensus, Phase 3 part 02 에서 정확 식 옵션 추가 권고 (P2-신규).
