# EUV Expert Opinion — Phase 1 Initial Review

## 메타
- 감사 ID: EXT-AUD-2026-04-26-001
- 감사 단계: Stage 1 / Individual
- 전문가 시각: **EUV (물리 + 도메인)**
- 감사 날짜: 2026-04-26
- 대상:
  - `src/constants.py`, `src/pupil.py`, `src/mask.py`, `src/aerial.py`
  - `tests/phase1_aerial_image.py` (5 tests)
  - `docs/phase1_design.md`
  - `notebooks/0_first_aerial_image.ipynb`
- 받은 보고서: 코드 작성자 self-audit 미작성 상태 (직접 코드 + design doc 검토)

---

## 1. 발견사항 (Findings)

### F-EUV-01 — 광학 상수 정확
- λ = 13.5e-9 m (`constants.py` line 9), NA = 0.55 default
- EUV photon energy helper도 명시 (h·c/λ, eV 변환 정확)
- Rayleigh / DOF 헬퍼: `R = k₁·λ/NA`, `DOF = k₂·λ/NA²` 식 그대로 구현

### F-EUV-02 — Anamorphic 4×/8× 정확 모델링
- `(x_w, y_w) = (x_m/4, y_m/8)` (`aerial.py:65-66`)
- scan vs cross-scan 비대칭 명시 (paper #19 Migura 2015 fig.3 인용)
- `wafer_grid_from_mask()` 가 `anamorphic=False` 옵션도 제공해 1× 테스트 모드 분리

### F-EUV-03 — Annular pupil + central obscuration 정확
- `P = (ρ ≤ 1) ∧ (ρ ≥ ε)` (`pupil.py:124-126`, `aerial.py:93-95`)
- 0.55 NA EUV 시스템의 obscuration ratio 0.20 default (`constants.py:16`)
- paper #15 Beck Optronic 정성 식과 일치

### F-EUV-04 — Hopkins coherent imaging step 정확
- `I = |IFFT(FFT(M)·P)|²` (`aerial.py:163-166`)
- fftshift / ifftshift 컨벤션 일관 (spectrum에 fftshift, inverse에 ifftshift)
- partial coherence는 Phase 2로 명시적 deferred (S1)

### F-EUV-05 — Kirchhoff thin-mask + 명시적 한계
- `field = 1 - pattern` (absorber=1 → field=0) (`mask.py:67`)
- M3D 6 효과 (paper #12) 모두 무시됨이 docs §5 S2 + mask.py docstring 양쪽에 명시
- Phase 4에서 다루어질 것임을 forward reference

### F-EUV-06 — 좌표·부호 컨벤션 fix + 명시
- D5 결정 (anamorphic 컨벤션 한 번 정하면 변경 금지) 가 `docs/phase1_design.md §1` 에 표 + 도식으로 기록
- numpy `meshgrid(..., indexing='xy')` 명시 — fx 가로축, fy 세로축
- 6개월 후 재검토 시 모호함 없음

### F-EUV-07 — 단위 테스트 4가지가 핵심 EUV 거동 모두 커버
- Airy PSF (T1) — 회절 정성
- Line/space resolution (T2) — λ/NA cutoff = 24.5 nm 정량 검증
- Annular vs solid sidelobe (T3) — central obscuration 효과 (paper #15)
- Anamorphic field 26×33 → 6.5×4.125 mm (T4) — paper #19 정량 매핑

### F-EUV-08 — KPI K1, K2 이미 합격
- K1 (end-to-end 광학): mask → aerial image 통과
- K2 (정성적 회절 재현): pitch sweep cutoff 24.5 nm 정확 일치

---

## 2. 위험 (Risks)

### R-EUV-01 — Kirchhoff thin-mask의 0.55 NA 정량 한계 (낮음, 기록됨)
- paper #12, #17 이 명시적으로 부정량
- Phase 4 entry 시 boundary correction 필요
- **현재 영향: 없음** — Phase 1 범위 한정. 4중 기록 (S2) 완료

### R-EUV-02 — Monochromatic 가정의 OOB radiation 영향 (낮음, 기록됨)
- paper #8 LPP source spectrum
- ~몇 % dose 오차 가능
- **현재 영향: 없음** — S3 기록. Phase 1+ 옵션으로 명시

### R-EUV-03 — Constant mirror reflectivity (낮음, 기록됨)
- 다층막 angle/polarization 의존성 무시
- **현재 영향: 없음** — S4 기록. 미래 확장

### R-EUV-04 — Defocus phase 부호 컨벤션이 아직 fix되지 않음 (중간, 미기록)
- Phase 1에서는 z=0 가정이라 defocus 항이 없음
- Phase 3 wafer_topo.py 진입 시 `φ = π·z·NA²/λ` 의 z 부호 (z>0 = above focus or below?) 결정 필요
- **현재 영향: 없음** — Phase 3 entry criteria 에 추가 필요

### R-EUV-05 — Pixel quantization 제약 (낮음, 기록됨)
- pitch가 grid 총 길이의 정확한 약수일 때만 깨끗한 sub-resolution 거동
- `mask.py:99-104` 의 양자화 + `docs/phase1_design.md §3` 에 디버깅 trace 기록
- **현재 영향: 노트북 sweep에서 divisor list 명시로 회피 가능**

---

## 3. 권고 (개별 권고 — 우선순위 시도)

### REC-EUV-01 (P1) — Phase 4 진입 전 paper #12 6 효과 test stub 작성
- 위치: `tests/phase4_m3d_6effects.py` (현재는 미존재)
- 내용: 6개 빈 함수 + skip mark + 각 함수 docstring에 paper #12 정확한 figure/section 인용
- 효과: Phase 4 entry 시 verification 항목이 명확
- 작업량: 30분

### REC-EUV-02 (P1) — Phase 3 진입 전 defocus 부호 컨벤션 결정 + 단위 테스트
- 위치: `docs/phase3_design.md` 에 부호 컨벤션 표 + `tests/phase3_DOF.py` 에 부호 검증 테스트
- 효과: Phase 3 코드 전체에 영향. 한 번 정하면 변경 비용 매우 큼 (D5 원칙 적용)
- 작업량: 1시간

### REC-EUV-03 (P2) — paper #17 absorber n,k 후보 데이터 수집
- 위치: `data/absorber_nk/` 폴더 + JSON 파일 (TaBN, Ni, RuTa, PtMo, PtTe)
- 효과: Phase 4 진입 시 즉시 ablation 가능
- 작업량: 2시간 (CXRO database 또는 paper 표에서 추출)

---

## 4. 본 전문가가 답하지 않는 영역

다음은 EUV 시각 외부 → 다른 전문가에게 위임:

- **AI 전문가**: FFT sampling 정확성, gradient 안정성 (Phase 1에서는 N/A이나 일반 점검), numerical stability
- **Software 전문가**: 코드 아키텍처, CI/CD 정합성, test naming, refactor 후보
- **Data Scientist**: 7 simplification 누적의 누적 위험 정량화, KPI trajectory, 추세 분석

---

## 5. 한 줄 요약 판정

**PASS** — Phase 1의 EUV 도메인 측면은 물리적으로 정직하고 수식·좌표·단순화가 명시화되어 있다. 0.55 NA EUV 의 핵심 광학 거동 (회절·anamorphic·annular pupil) 이 정성·정량 모두 합리적으로 재현됨. Phase 3, 4 진입 전 defocus 부호 + M3D 6효과 stub 만 미리 준비하면 EUV 측면 risk 낮음.
