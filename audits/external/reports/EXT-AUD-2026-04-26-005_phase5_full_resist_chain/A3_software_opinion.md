# Software Engineer Expert Opinion — Phase 5 Full Resist Chain

## 메타
- 감사 ID: EXT-AUD-2026-04-26-005
- 감사 단계: Stage 1 / Individual
- 전문가 시각: **Software**
- 감사 날짜: 2026-04-26

---

## 1. 발견사항 (Findings)

### 1.1 아키텍처

#### F-SW-01 — Phase 5 4-level 4 모듈 분리 ★
```
src/resist_threshold.py   ( 53 lines)  Level 0 MVP
src/resist_blur.py        (~ 250 lines)  Level 1 Gaussian blur
src/resist_depth.py       (~ 350 lines)  Level 2 depth-resolved
src/resist_stochastic.py  (539 lines)  Level 3 Markov chain MC
src/metrics.py            (186 lines)  Cross-cutting metrics
```
- **단일 책임 명확**: 각 level 별 독립 모듈
- **점진적 정밀화 (P1 원칙) 그대로 매핑**
- `resist_stochastic.py` 가 가장 큼 (Markov chain + LWR budget + calibration 통합)

#### F-SW-02 — `metrics.py` 가 Phase 1-5 cross-cutting
- `binary_line_runs`, `critical_dimension`, `edge_positions`, `edge_placement_errors`, `mean_absolute_epe`, `dose_cd_curve`, `michelson_contrast`, `normalized_image_log_slope`
- Phase 5 stochastic 이 `from .metrics import critical_dimension` 으로 재사용
- DRY 충실

#### F-SW-03 — 7개 Public Dataclass — 결과 구조화의 모범
`resist_stochastic.py` 의 dataclass:
| 클래스 | 역할 |
|--------|------|
| `StochasticResistParams` | 입력 파라미터 |
| `StochasticExposure` | 단일 trial 출력 |
| `LWRBudget` | paper #1 분해 |
| `StochasticDoseResult` | 단일 dose summary |
| `MonteCarloConvergenceResult` | 수렴 게이트 |
| `CalibratedStochasticLWRPoint` | 측정/캘리브레이션 |
| `StochasticLWRCalibration` | 캘리브레이션 출력 |

- 모두 `frozen=True` immutable
- 각 필드 명시적 + 단위 (`_m` suffix)
- **dict 반환 대신 dataclass — IDE/mypy strict 친화** ★

### 1.2 코드 품질

#### F-SW-04 — Type hints 일관 적용 (모든 public + 대부분 private)
- `Iterable[float]` 로 다양한 입력 수용 (list/tuple/generator)
- `np.random.Generator | None`
- `tuple[int, ...]` 로 trial counts

#### F-SW-05 — `*` keyword-only 구분
- 모든 public 함수가 `*,` 로 keyword 인자 명시
- 호출 명확성 + future-proof (positional 추가 시 깨지지 않음)

#### F-SW-06 — 공통 패턴: `_validate_positive_finite`, `_as_*`
- 모든 모듈에 같은 검증 패턴
- 단점: 코드 중복 (AI 시각 R-AI-05 와 consensus)
- 장점: 각 모듈 self-contained

### 1.3 테스트

#### F-SW-07 — 64 tests, 일관 명명 ★
- `test_<topic>_<verb_phrase>` 패턴
- spec 역할: `test_threshold_resist_applies_dose_threshold`, `test_lwr_budget_reproduces_optical_material_smile_shape`
- 부정 케이스: `test_threshold_resist_rejects_invalid_inputs`, `test_blur_rejects_invalid_inputs`

#### F-SW-08 — `tests/integration_end_to_end.py` ★ KPI K1
- **본 프로젝트의 첫 통합 테스트** (단위 테스트와 분리)
- Phase 1+3+5 MVP 의 mask → printed pattern pipeline 자동 검증
- 보조 테스트 (`test_phase5_l1_blurred_pipeline_keeps_resolved_cd_within_tolerance`) 가 L1 blur 통합 검증

#### F-SW-09 — Phase 3 k₂ fitting 추가 발견
- `tests/phase3_DOF.py` 가 EXT-AUD-004 이후 5 신규 추가:
  - `test_focus_drilling_*` (2)
  - `test_k2_fit_from_nominal_dof_metrics`
  - `test_k2_fit_matches_rayleigh_depth_of_focus_sweep`
  - `test_k2_fit_rejects_large_rayleigh_error`
- **MT-012 (k₂ fitting) 도 본 PR 에서 처리됨!** (mitigation 추가 closure)

### 1.4 문서

#### F-SW-10 — `docs/phase5_resist_models.md`
- §1 Scope, §2 Implemented Functions, §3 Verification, §4 Limitations, §5 Exit Status
- Phase 1/3 design doc 패턴 그대로 일관
- **단순화 4중 기록** 충실

---

## 2. 위험 (Risks)

### R-SW-01 (★ P0-신규) — "Simulator" 용어 12개 파일 잔존 (사용자 명시 제거 지시 미반영)
- 사용자가 EXT-AUD-005 직전에 명시적 지시: "시뮬레이터이라는 단어는 뺄것"
- 현재 `src/__init__.py`, `README.md`, `PROJECT_OVERVIEW.md`, `진행계획서.md` 등 12개 파일에 잔존
- **권고: 코드 작성자에게 rebrand 지시서 작성 (DS 통합 §6)**
- **현재 영향**: 프로젝트 정체성 혼선

### R-SW-02 (P0-신규, 누적) — `.github/CLAUDE.md` v2.1 sync 미완 + rebrand 적용 필요
- EXT-AUD-004 P0 (MT-011) 가 미해결 누적
- 추가로 v2.1 자동 트리거 + rebrand 까지 한 번에 sync 필요
- **단일 P0**: `.github/CLAUDE.md` 갱신 (v2.1 트리거 + "Simulator" naming)

### R-SW-03 — `resist_stochastic.py` 539줄 — 모듈 분할 검토 필요 (낮음, P2)
- 한 모듈에 chain + LWR budget + calibration + helpers
- 분할 후보:
  - `resist_stochastic_chain.py` (chain MC)
  - `resist_lwr_budget.py` (paper #1 decomposition)
  - `resist_calibration.py` (grid search)
- **현재 영향**: 가독성 약간 부담, 기능 정상

### R-SW-04 (deferred 누적) — mypy strict, CONTRIBUTING.md, pre-commit + mypy
- EXT-AUD-001/002/003/004 와 동일

### R-SW-05 — 진행계획서 §5.1 / §5.2 / §13 stale 가능성
- Phase 5 4 module + 5 test file + 1 docs + 2 notebook 추가
- §5 산출물 표 갱신 여부 + §13 v1.4 entry 추가 여부 확인 필요
- **권고**: P1-신규 (코드 작성자 갱신)

### R-SW-06 — 노트북 reproducibility (4a, 4b 신규) — 메타데이터 미확인
- `notebooks/4a_threshold_resist.ipynb`, `4b_resist_levels.ipynb` 신규
- 첫 셀에 dependency version, seed, code commit hash 기록 여부 미확인
- **권고**: P3 backlog (이전 권고 그대로)

---

## 3. 권고 (개별 권고)

### REC-SW-01 (P0-신규, 통합) — `.github/CLAUDE.md` 한 번에 sync (v2.1 + rebrand)
- v2.1 자동 트리거 절차 (EXT-AUD-004 의 MT-011)
- "Simulator" → "Simulator" 명칭 (사용자 신규 지시)
- 작업량: 30분
- **DS 통합에서 단일 P0 으로 통합**

### REC-SW-02 (P0-신규) — Rebrand 일괄 처리 — 12개 파일 + workspace 폴더명
- 코드 작성자 task — 별도 PR 권고 (`docs-update: rename legacy project name to simulator`)
- 본 감사가 instruction sheet 제공 (DS §6 참고)

### REC-SW-03 (P1-신규) — `진행계획서.md §5/§13` 갱신
- §5.1: 4 resist 모듈 ✅, §5.2: 5 신규 test ✅
- §13 v1.4 entry: Phase 5 4-level + KPI K1 + k₂ fitting

### REC-SW-04 (P2-신규) — `_validation.py` 또는 `src/utils.py` 추출
- AI 시각 REC-AI-01 와 consensus
- 작업량: 1시간

### REC-SW-05 (P2) — `resist_stochastic.py` 모듈 분할 검토
- 작업량: 1-2시간

### REC-SW-06 (deferred) — mypy strict, CONTRIBUTING.md, pre-commit mypy

---

## 4. 본 전문가가 답하지 않는 영역

- **EUV / AI 전문가**: 물리·수치 정확성
- **Data Scientist**: 5-point 추세, rebrand instruction sheet, 3D 시각화 권고

---

## 5. 한 줄 요약 판정

**🟡 PASS WITH 1 P0** — Phase 5 코드 자체 매우 깨끗 (4-level 분리 + 7-dataclass 구조 + KPI K1 통합 테스트). 단 사용자 명시 rebrand 지시 미반영 ★ + EXT-AUD-004 의 CLAUDE.md sync 누적 = 단일 P0. 코드 작성자가 다음 PR 에서 둘 다 처리.
