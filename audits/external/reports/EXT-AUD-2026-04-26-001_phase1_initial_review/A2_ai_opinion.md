# AI / Numerical Expert Opinion — Phase 1 Initial Review

## 메타
- 감사 ID: EXT-AUD-2026-04-26-001
- 감사 단계: Stage 1 / Individual
- 전문가 시각: **AI / Numerical**
- 감사 날짜: 2026-04-26
- 대상: `src/`, `tests/`, `docs/phase1_design.md` 의 수치·sampling·optimization 측면

---

## 1. 발견사항 (Findings)

### F-AI-01 — Even-grid 강제 + 입력 검증
- `PupilSpec.__post_init__` (`pupil.py:46-54`) 가 grid_size 짝수, NA ∈ (0,1], obscuration ∈ [0,1), λ > 0 모두 강제
- ValueError 명확하게 발생 → silent error 차단

### F-AI-02 — Nyquist sanity guard (★)
- `aerial.py:146-153` 에서 aerial-plane Nyquist `1/(2·dx_w)` 가 pupil cutoff `NA/λ` 미만이면 ValueError
- 잘못된 mask grid 해상도로 high-frequency가 잘리는 silent failure 차단
- **수치 정직성의 모범 사례**

### F-AI-03 — fftshift 컨벤션 일관
- spectrum에 `fftshift`, inverse에 `ifftshift` 일관 적용 (`aerial.py:163-165`)
- pupil grid도 `np.fft.fftshift(np.fft.fftfreq(...))` 로 동일 컨벤션 (`aerial.py:85-86`)
- 모듈 간 origin 위치 일치

### F-AI-04 — np.fft.fftfreq 사용 (정확)
- 수동 frequency grid 계산이 아닌 numpy 표준 함수 사용
- pixel_x_m, pixel_y_m 비대칭 (anamorphic) 도 자연스럽게 처리

### F-AI-05 — Noise floor 보호 (★ 디버깅 결과 반영)
- `aerial.py:170-181`: bright-field reference 미만의 noise는 0으로 floor
- sub-resolution + central obscuration 조합에서 division-by-noise → 잘못된 contrast=1 차단
- **`docs/phase1_design.md §4` 에 디버깅 trace 정직하게 기록**

### F-AI-06 — Type hints + frozen dataclasses
- 모든 public 함수 type hint
- `PupilSpec`, `MaskGrid`, `WaferGrid` 모두 frozen dataclass (immutability)
- mutation으로 인한 silent state 오류 차단

### F-AI-07 — Pixel quantization 처리 + 명시
- `mask.py:99-104` 가 pitch_m을 정수 픽셀로 양자화
- 부동소수점 누적 오차로 인한 non-periodic pattern → spectral leakage 차단
- 디버깅 trace가 `docs/phase1_design.md §3` 에 정직하게 기록

### F-AI-08 — Reproducibility 보장 (현재 범위 내)
- Phase 1은 stochastic 요소 없음 → seed 불필요
- 모든 결과 deterministic
- Phase 5 L3 진입 시 seed 정책 별도 필요 (R-AI-04 참고)

### F-AI-09 — Algorithmic complexity
- FFT: O(N²·log N²) per call — 적절
- 2048² grid 기준 단일 aerial image < 100ms 추정 (M4 Air에서)
- Phase 6 SMO iterative loop 시점에 병목 평가 필요

---

## 2. 위험 (Risks)

### R-AI-01 — `aerial.py` 가 `pupil._wavefront` 를 lazy import (중간, 미해결)
- `aerial.py:98` 에서 `from .pupil import _wavefront` 함수 안에서 import
- 작동은 하지만 architectural smell
- Phase 4 mask_3d 추가 시 같은 패턴이 누적되면 순환 참조 위험
- **권고**: `src/optics/zernike.py` 모듈로 _wavefront 추출

### R-AI-02 — Pixel quantization 제약 (낮음, 기록됨)
- pitch가 grid 총 길이의 정확한 약수여야 함
- 노트북 sweep의 parameter space 제약
- **현재 영향: 노트북에서 divisor list 명시로 우회**

### R-AI-03 — Intensity normalization to peak loses absolute scale (중간, 기록됨)
- `aerial.py:179` 가 `intensity / peak` 로 [0,1] 정규화
- dose 계산 (Phase 5) 시 절대 scale 필요
- **권고**: optional `normalize=True/False` 파라미터 추가 (Phase 5 entry 시)

### R-AI-04 — Phase 5 L3 stochastic MC seed 정책 미정 (낮음, 미정)
- Phase 1 범위 외이지만 미리 정책 결정 필요
- **권고**: Phase 5 진입 전 `tests/conftest.py` 에 `RANDOM_SEED = 42` global fixture 추가

### R-AI-05 — Parseval / fftshift round-trip 자동 테스트 부재 (낮음)
- 현재 5개 테스트가 모두 EUV 거동 위주
- FFT normalization 또는 shift 컨벤션 오류를 자동 검출하는 smoke test 없음
- **권고**: `tests/audits/test_fft_invariants.py` 신설 — Parseval, fftshift round-trip, NA scaling

### R-AI-06 — mypy `continue-on-error: true` (중간, 의도된 점진적)
- `.github/workflows/ci.yml:159` 가 mypy 실패를 차단하지 않음
- 의도: 초기에는 경고만, 점차 강제 — `docs/phase1_design.md`에는 명시 X
- **위험**: 시간이 지나면서 type error 누적, "점차 강제" 시점이 지연
- **권고**: 모듈별 `# mypy: strict` 마크로 점진적 enforce

---

## 3. 권고 (개별 권고 — 우선순위 시도)

### REC-AI-01 (P1) — `_wavefront` 를 `src/optics/zernike.py` 로 추출
- 현재: `pupil.py:64-107` 의 `_zernike_polynomial`, `_wavefront` 가 같은 파일에 있고 `aerial.py` 가 lazy import
- 변경: `src/optics/__init__.py`, `src/optics/zernike.py` 신설 → 두 함수 이동
- 효과: Phase 4 mask_3d.py 가 같은 zernike 함수 공유 가능, 순환 참조 위험 제거
- 작업량: 1시간 (이동 + import 수정 + 5개 테스트 다시 통과 확인)

### REC-AI-02 (P1) — `tests/audits/` 자동 수치 invariant 테스트 신설
- 위치: `tests/audits/test_fft_invariants.py`
- 내용:
  - `test_parseval_round_trip()` — `sum(|M|²) ≈ sum(|FFT(M)|²) / N`
  - `test_fftshift_idempotent()` — `ifftshift(fftshift(A)) == A`
  - `test_NA_scaling()` — NA 변화 시 cutoff frequency 정확
  - `test_grid_refinement()` — N=512, 1024, 2048에서 contrast 수렴
- 효과: 향후 모든 PR이 이 자동 검증 통과해야 함
- 작업량: 2시간

### REC-AI-03 (P2) — mypy strict 점진적 도입
- 우선 `src/constants.py` 에 `# mypy: strict` 추가 (가장 단순)
- 차례로 `pupil.py`, `mask.py`, `aerial.py`
- CI에서 `continue-on-error` 제거는 모든 모듈 strict 통과 후
- 작업량: 1-2주에 걸쳐 점진적

### REC-AI-04 (P2) — Phase 5 진입 전 `RANDOM_SEED` global fixture 추가
- 위치: `tests/conftest.py`
- 효과: stochastic MC reproducibility 보장
- 작업량: 30분

### REC-AI-05 (P3) — Optional 절대 intensity scale 보존
- `aerial_image()` 에 `normalize: bool = True` 파라미터 추가
- `False` 시 dose 계산용 절대 scale 보존
- 작업량: 1시간 + 단위 테스트

---

## 4. 본 전문가가 답하지 않는 영역

- **EUV 전문가**: 물리식의 정확성 (defocus phase 부호, M3D 효과)
- **Software 전문가**: 모듈 구조의 더 큰 아키텍처 결정 (e.g., `src/optics/` vs `src/`)
- **Data Scientist**: 7 simplification 의 누적 위험, 시간에 따른 quality drift trajectory

---

## 5. 한 줄 요약 판정

**PASS (with notable rigor)** — Phase 1 의 수치 구현은 매우 정직하다. Nyquist 가드 + noise floor + pixel quantization 처리 + 디버깅 trace 의 정직한 기록은 모범 사례. 단 lazy import 1건 + 자동 수치 invariant 테스트 부재가 다음 Phase 진입 전 정리 권고 (P1).
