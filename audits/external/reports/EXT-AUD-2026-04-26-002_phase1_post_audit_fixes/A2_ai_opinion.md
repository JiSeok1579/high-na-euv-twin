# AI / Numerical Expert Opinion — Phase 1 Post-Audit Fixes (PR #4)

## 메타
- 감사 ID: EXT-AUD-2026-04-26-002
- 감사 단계: Stage 1 / Individual
- 전문가 시각: **AI / Numerical**
- 감사 날짜: 2026-04-26
- 대상: PR #4 squash merge `ee30c04` — MT-001~MT-005 5건 반영

---

## 1. 발견사항 (Findings)

### F-AI-01 — `_wavefront` 추출이 lazy import 제거 + 깨끗한 의존 그래프
- 이전: `aerial.py:98` 에서 함수 내부 `from .pupil import _wavefront` (architectural smell)
- 현재: `aerial.py:37` `from .optics import wavefront` — top-level, 명시적
- `pupil.py:29` 도 동일하게 `from .optics import ZernikeCoeffs, wavefront`
- **순환 참조 위험 0**: aerial → pupil → optics, pupil → optics 의 acyclic DAG
- **Phase 4 mask_3d.py 진입 시 이미 깨끗한 import 경로 확보**

### F-AI-02 — public API 명명 변경 (`_wavefront` → `wavefront`)
- 단일 파일 private 에서 공유 모듈 public 으로 승격
- `_zernike_polynomial` → `zernike_polynomial` 도 동일
- **명명 일관성**: 공유 helper 가 public 인 것은 적절
- `src/optics/__init__.py` 에 `__all__ = ["ZernikeCoeffs", "wavefront", "zernike_polynomial"]` 명시 export

### F-AI-03 — `tests/audits/test_fft_invariants.py` 4 테스트가 핵심 invariant 자동 검증
| 테스트 | 검증 대상 | 평가 |
|--------|-----------|------|
| `test_fft_parseval_round_trip` | `sum(|spectrum|²) / N == sum(|field|²)` | ✓ 정확. NumPy 의 unitary scaling 식 일치 |
| `test_fftshift_ifftshift_round_trip` | `ifftshift(fftshift(A)) == A` | ✓ 33×34 비대칭 grid 로 odd-size 보장 |
| `test_pupil_cutoff_frequency_matches_na_scaling` | `cutoff = NA/λ` 의 NA 선형성 | ✓ 0.33 vs 0.55 비교 |
| `test_grid_refinement_converges_for_resolved_pitch` | 256 vs 512 grid 의 contrast 차 < 0.15 | ✓ discretization 안정성 |

- **모범 사례**: random seed 42 고정 (reproducibility)
- **모범 사례**: `pytest.approx(rel=1e-12)` 정밀도 명시

### F-AI-04 — 9개 테스트 전부 통과 + lastfailed = `{}`
- pytest cache 직접 확인 (`{}` = 모든 등록 테스트 PASS)
- coder report 의 "pytest 9개 통과" 와 일치

### F-AI-05 — Numerical artifacts 회귀 없음
- `aerial.py` 의 Nyquist guard, noise floor, fftshift 컨벤션 모두 그대로 유지
- pixel quantization 워크어라운드도 변경 없음 (mask.py:99-104)

### F-AI-06 — 33×34 odd-size grid 테스트는 이상적
- `test_fftshift_ifftshift_round_trip` 가 33 (odd) × 34 (even) 사용
- numpy `fftshift` 가 odd 차원에서 N/2 의 floor/ceil 처리하는 미묘한 케이스 자동 검증
- **AI 전문가 시각에서 추가 권고는 없음** — 이미 견고

---

## 2. 위험 (Risks)

### R-AI-01 — `mypy continue-on-error: true` 여전히 (중간, 의도된 점진적)
- `.github/workflows/ci.yml:159` 변경 없음
- EXT-AUD-001 R-AI-06 와 동일
- **현재 영향**: 본 PR 의 신규 코드는 type hint 일관 → 단기 영향 없음
- **권고**: P2 timeline 그대로

### R-AI-02 — `tests/audits/__init__.py` 빈 파일 인식
- `__init__.py` 가 38 bytes 로 거의 비어 있음 — pytest discovery 만 위함
- **위험 없음** — pytest 설정 (`pytest.ini` 의 `python_files = phase*_*.py test_*.py`) 와 호환

### R-AI-03 — 새 invariant 테스트가 4개로 충분한가
- Parseval, fftshift, NA scaling, grid refinement 4개로 핵심 invariant cover
- **잠재 gap**: random init mask 로 Parseval 검증은 했지만 *imaged* result 의 power conservation (sum I = pupil throughput · |M|² mean) 은 미커버
- **권고**: Phase 5 dose 진입 전 추가

---

## 3. 권고 (개별 권고 — 우선순위 시도)

### REC-AI-01 (P2) — Phase 5 dose 진입 전 power conservation 테스트 추가
- 위치: `tests/audits/test_fft_invariants.py` 또는 신규 `test_imaging_invariants.py`
- 내용: clear mask + open pupil → aerial image 의 적분이 입사 power 와 일치
- 효과: Phase 5 dose 계산 정확성 보장
- 작업량: 1시간

### REC-AI-02 (P2) — `mypy --strict` 단계적 도입 (MT-005 의 다음 단계)
- pre-commit hook 에 mypy 추가 (현재는 ruff 만)
- 한 번에 strict 보다는 모듈별 점진적 (constants.py 부터)
- 작업량: 2시간

### REC-AI-03 (P3) — random seed 정책 명문화
- `tests/audits/test_fft_invariants.py:15` 에서 `np.random.default_rng(42)` 사용
- Phase 5 L3 stochastic MC 진입 시 동일 seed 정책 필요
- `tests/conftest.py` 에 `RANDOM_SEED = 42` global fixture 추가
- 작업량: 30분

---

## 4. 본 전문가가 답하지 않는 영역

- **EUV 전문가**: 물리식 정확성, Zernike 다항식의 광학적 의미
- **Software 전문가**: 모듈 구조 평가, pre-commit 도입의 운영 효과
- **Data Scientist**: 4개 invariant 테스트의 종합 coverage 평가, 이전 감사 대비 위험 지수 변화

---

## 5. 한 줄 요약 판정

**🟢 PASS (clean)** — `_wavefront` 추출은 architectural smell 1건을 깔끔히 해소했고, `tests/audits/` 4개 invariant 테스트는 향후 모든 PR에서 FFT/sampling 회귀를 자동 차단할 견고한 안전망. EXT-AUD-001 의 AI 시각 P1 권고 (REC-AI-01, REC-AI-02) 모두 정확히 반영됨. 추가 P0/P1 없음.
