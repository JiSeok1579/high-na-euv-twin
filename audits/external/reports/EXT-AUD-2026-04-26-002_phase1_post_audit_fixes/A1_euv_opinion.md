# EUV Expert Opinion — Phase 1 Post-Audit Fixes (PR #4)

## 메타
- 감사 ID: EXT-AUD-2026-04-26-002
- 감사 단계: Stage 1 / Individual
- 전문가 시각: **EUV (물리 + 도메인)**
- 감사 날짜: 2026-04-26
- 대상: PR #4 (squash merge `ee30c04`) — EXT-AUD-001 의 P0/P1 mitigation 5건 반영
- 받은 보고서: 코드 작성자 (Codex) 의 자체 검증 결과
  - 로컬: pytest 9개 통과, compileall 통과, git diff --check 통과, YAML 파싱 통과
  - GitHub CI: pytest+mypy+ruff, clear-merge-title, claude, auto-merge 모두 통과
  - PR #4 자동 squash merge 완료

---

## 1. 발견사항 (Findings)

### F-EUV-01 — 물리 무회귀 (No Physics Regression)
- **MT-003 `_wavefront` 추출은 순수 리팩터** — 물리식 변경 없음
- `src/optics/zernike.py` 의 Zernike 다항식 계산 로직이 `pupil.py` 원본과 bit-identical
  - radial polynomial: `R_n^|m|(rho)` 정확
  - cos/sin(mθ) 분기 정확
  - `rho > 1` 영역 zero-mask 유지
- `pupil.py:81` 와 `aerial.py:99` 양쪽이 같은 `wavefront(rho, theta, zernike)` 함수를 호출 → **두 모듈의 위상 계산 일치 보장**

### F-EUV-02 — Phase 4 진입 준비도 향상
- 공용 `src/optics/` 모듈은 Phase 4 `mask_3d.py` 가 absorber wavefront 위상 계산 시 동일 Zernike helper 재사용 가능
- 진행계획서 §5.1 의 `src/optics/zernike.py` 항목이 "1+ / cross" 로 표기 — 다중 Phase 공유 의도 명시

### F-EUV-03 — 단위 테스트 EUV 거동 4개 + 신규 4개 모두 통과
- 기존 Phase 1 5개 (Airy PSF, line/space resolution, annular sidelobe, anamorphic field, CD helper) 회귀 없음
- 신규 `tests/audits/test_fft_invariants.py` 의 `test_pupil_cutoff_frequency_matches_na_scaling` 가 NA scaling 식 (`cutoff = NA / λ`) 정확성 자동 검증

### F-EUV-04 — 7개 단순화 가정 변경 없음
- S1–S7 모두 그대로 유효
- 본 PR은 mitigation task 처리만 — 단순화 누적 변화 없음

### F-EUV-05 — MT-006 (defocus 부호 컨벤션) 적절히 deferred
- Phase 3 entry 직전 처리하는 것이 타당
- 현재 z=0 가정 하에서는 EUV 측면 위험 없음

---

## 2. 위험 (Risks)

### R-EUV-01 — `wavefront(rho, theta, zernike)` 의 rho > 1 처리 일관성 (낮음)
- `zernike_polynomial` 함수 내부에서 `z[rho > 1.0] = 0.0` 적용
- 하지만 호출 측 `aerial._build_aerial_pupil` 은 이미 `inside = rho <= 1.0` mask 를 amplitude 에 적용
- **위험**: rho > 1 영역에서도 wavefront 가 계산되어 약간의 불필요 연산 (미세 성능 영향만)
- **현재 영향**: 결과 정확성에는 영향 없음 — amplitude * phase 곱에서 amplitude=0 이 phase 효과 무화

### R-EUV-02 — Phase 3 entry 전 defocus 부호 컨벤션 (MT-006, 미해결)
- EXT-AUD-001 의 REC-EUV-02 그대로 유효
- Phase 3 코드 작성 시작 전 `docs/phase3_design.md` 에 부호 표 + `tests/phase3_DOF.py` 부호 검증 필수
- **현재 영향**: Phase 1 에는 무관. Phase 3 entry 시 차단 항목

---

## 3. 권고 (개별 권고 — 우선순위 시도)

### REC-EUV-01 (P2) — Phase 4 진입 시 absorber n,k 데이터셋 사전 수집
- EXT-AUD-001 REC-EUV-03 그대로 유지
- 작업량: 2시간 (CXRO database)

### REC-EUV-02 (P1) — Phase 3 entry 전 defocus 부호 컨벤션 (MT-006)
- 변경 없음. EXT-AUD-001 권고 유지.
- 작업량: 1시간

### REC-EUV-03 (P3) — Phase 4 진입 시 paper #12 6 효과 단위 테스트 stub 사전 작성
- EXT-AUD-001 REC-EUV-01 그대로 유지
- 작업량: 30분

---

## 4. 본 전문가가 답하지 않는 영역

- **AI 전문가**: refactor 의 import 안전성, 신규 FFT invariant 테스트의 수치 적정성
- **Software 전문가**: pre-commit hook, CI workflow, refactor 의 모듈 구조 평가
- **Data Scientist**: EXT-AUD-001 → 002 추세 정량화, mitigation 처리율, 위험 지수 변화

---

## 5. 한 줄 요약 판정

**🟢 PASS** — Phase 1 의 EUV 물리는 본 PR 에서 무회귀(no regression) 이며, `src/optics/` 공용화는 Phase 4 진입 준비도를 명확히 향상시킨다. 단순화 가정 변경 없음. EUV 측면에서 PR #4 squash merge 완료는 적절했다. 남은 EUV 관련 항목은 MT-006 (defocus 부호) 단 1건, Phase 3 entry 직전 처리.
