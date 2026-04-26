# Software Engineer Expert Opinion — Phase 3 Part 02

## 메타
- 감사 ID: EXT-AUD-2026-04-26-004
- 감사 단계: Stage 1 / Individual
- 전문가 시각: **Software**
- 감사 날짜: 2026-04-26

---

## 1. 발견사항 (Findings)

### 1.1 아키텍처

#### F-SW-01 — `src/dof.py` 단일 책임 명확
- DOF metric 전용 모듈 — focus stack 평가 + nominal DOF window 추정
- `aerial`, `mask`, `pupil` 의존만 (acyclic)
- 향후 Phase 3 part 03 (focus drilling) 도 같은 모듈 확장 가능

#### F-SW-02 — Public dataclass 2개 명료
| dataclass | 역할 |
|-----------|------|
| `FocusSample` | 단일 focus point (defocus, contrast, normalized_contrast) |
| `DOFMetrics` | 전체 focus stack + threshold 결과 + DOF 값 |

- `frozen=True` immutability
- 필드명 명시적 (`reference_defocus_m`, `threshold_contrast`, `lower_defocus_m`, `upper_defocus_m`)

#### F-SW-03 — Helper 함수 private (`_crossing_from_reference`, `_linear_crossing`)
- `_` prefix 로 내부 헬퍼 명시
- public API = `focus_stack_contrast` + `nominal_depth_of_focus` 두 개만

### 1.2 코드 품질

#### F-SW-04 — Type hints 일관 적용
```python
def focus_stack_contrast(
    mask_field: np.ndarray,
    mask_grid: MaskGrid,
    defocus_values_m: Iterable[float],
    pupil_spec: PupilSpec | None = None,
    *,
    anamorphic: bool = True,
) -> tuple[FocusSample, ...]:
```
- 모든 인자 type hint
- `Iterable[float]` 로 다양한 입력 (list, tuple, generator) 수용
- keyword-only 인자 (`*,`) 로 명확한 호출 강제

#### F-SW-05 — `Literal["paraxial", "angular"]` 타입 alias
- `wafer_topo.py:25`: `DefocusApproximation = Literal["paraxial", "angular"]`
- mypy strict 가능 — 잘못된 문자열 입력 즉시 type error
- IDE 자동완성 지원

#### F-SW-06 — Docstring 일관성
- 모든 public 함수 NumPy-style docstring
- 단위 명시 (m, radians)
- 단순화/한계 inline 명시 (e.g., "Phase 3 Part 02 tracks the nominal process window first")

### 1.3 테스트

#### F-SW-07 — 6 신규 테스트 모두 spec 역할
| 테스트 | spec 검증 |
|--------|-----------|
| `test_full_angular_defocus_matches_paraxial_small_angle_limit` | 두 옵션의 일관성 |
| `test_focus_stack_contrast_is_symmetric_for_opposite_defocus` | 광학 대칭성 |
| `test_nominal_dof_metric_interpolates_threshold_crossings` | DOF 측정 정확성 |
| `test_defocus_sampling_guard_rejects_under_sampled_phase` | 가드 작동 |
| `test_defocus_phase_is_unitary` | 광학 invariant 1 |
| `test_zero_defocus_phase_is_identity` | 광학 invariant 2 |

#### F-SW-08 — Test 명명 패턴 일관 유지
- `test_<noun>_<verb_phrase>` 형태
- `assert` not just regression but spec
- EXT-AUD-001/002/003 의 모범 사례 패턴 그대로 적용 ★

### 1.4 문서

#### F-SW-09 — `docs/phase3_DOF_analysis.md` 단순화 4중 기록 충실
- §1 Purpose — scope 명확
- §2 Implemented Metrics — 4 함수 표
- §3 Smoke Evidence — 8 테스트 항목 명시
- §4 K3 Status — measurable vs complete 정직 분리
- 코드 docstring (`dof.py:80-83`) + docs §2 + 테스트 명명 + AUDIT_LOG = 4중 기록 ★

#### F-SW-10 — `docs/phase3_design.md` 의 P3-L1~L4 limitation 갱신 가능 상태
- Part 01 docs 가 P3-L1 (constant defocus) 명시
- Part 02 가 처리한 항목: 부분적으로 P3-L2 (DOF metric) — measurable 까지 진척
- **권고**: `docs/phase3_design.md §4` 의 P3-L2 entry 를 "measurable, k₂ fitting 다음 part" 로 갱신 (P1-신규)

### 1.5 CI/CD

#### F-SW-11 — 코더 자체 보고
- pytest --cov 20 passed
- ruff passed
- mypy passed
- 단, **본 PR 의 git/GitHub merge 정보 미제공** — 자체 보고만으로 진행 추정

#### F-SW-12 — `.github/CLAUDE.md` v2.1 sync 미완 (잠재 위험)
- 본 지침이 v2.0 → v2.1 로 격상 (자동 트리거 추가)
- `.github/CLAUDE.md` 는 여전히 v2.0 기준
- **현재 영향**: GitHub Action 이 v2.0 prompt 사용 — 자동 트리거 절차 미적용 가능

---

## 2. 위험 (Risks)

### R-SW-01 — `진행계획서.md §13` v1.2 entry 누락 (낮음, drift 시작)
- v1.0 → v1.1 (Phase 1 완료) 이후 갱신 없음
- Phase 3 Part 01 + Part 02 의 변경 이력 누락
- **권고**: 다음 PR 에서 v1.2 (Phase 3 Part 01) + v1.3 (Phase 3 Part 02) 동반 추가 (P1-신규)

### R-SW-02 — `.github/CLAUDE.md` v2.1 sync 필요 (P0-신규)
- 본 지침 v2.1 신설 (자동 외부감사 트리거)
- GitHub Action 이 같은 절차로 작동하려면 sync 필요
- EXT-AUD-001 의 P0 (CLAUDE.md sync) 와 동일 패턴

### R-SW-03 — `진행계획서.md §5.1` 상태표 stale 가능
- `src/dof.py`, `src/optics/zernike.py` 추가 후 §5.1 갱신 여부 미확인
- **권고**: 직접 검증 필요

### R-SW-04 — pre-commit / mypy strict 도입 timeline 여전히 deferred
- EXT-AUD-001/002/003 와 동일

### R-SW-05 — `CONTRIBUTING.md` 부재 4회 deferred
- 외부 contributor 이 합류할 경우 진입 장벽

---

## 3. 권고 (개별 권고)

### REC-SW-01 (P0-신규) — `.github/CLAUDE.md` 를 REVIEWER_DIRECTIVE v2.1 로 sync
- v2.1 §10.5 자동 외부감사 트리거 절차 명시
- "코드 변경 + @claude 멘션 자체가 자동 EXT-AUD 4-md 작성 트리거" 추가
- 작업량: 30분

### REC-SW-02 (P1-신규) — `진행계획서.md §13` 변경 이력 v1.2/v1.3 추가
- v1.2: Phase 3 Part 01 (defocus sign convention)
- v1.3: Phase 3 Part 02 (DOF metrics + MT-008~010)
- 작업량: 10분

### REC-SW-03 (P1-신규) — `docs/phase3_design.md §4` P3-L2 갱신
- 현재: "DOF metric / k₂ fitting 없음 | Phase 3 part 2"
- 갱신: "DOF metric measurable, k₂ fitting | Phase 3 part 3 또는 다음 increment"
- 작업량: 5분

### REC-SW-04 (P2) — `진행계획서.md §5.1` Phase 3 항목 갱신
- `src/wafer_topo.py`, `src/dof.py` 둘 다 ✅ 표기
- 작업량: 5분

### REC-SW-05 (P2) — Pre-commit 에 mypy strict 모듈별 도입 (deferred 누적)
- EXT-AUD-001/002/003 와 동일

### REC-SW-06 (P3) — CONTRIBUTING.md 추가
- EXT-AUD-001/002/003 와 동일

---

## 4. 본 전문가가 답하지 않는 영역

- **EUV / AI 전문가**: 물리·수치 정확성
- **Data Scientist**: 4-point 추세, KPI K3 진척률 정량화

---

## 5. 한 줄 요약 판정

**🟡 PASS WITH 1 P0** — Phase 3 Part 02 코드/테스트/문서 자체는 모두 깨끗하나, **REVIEWER_DIRECTIVE v2.1 신설로 인한 `.github/CLAUDE.md` sync 가 새 P0** (EXT-AUD-001 의 패턴 반복). 추가로 `진행계획서.md §13` v1.2/v1.3 entry stale + §5.1 갱신 여부 미확인이 P1-신규 2건. 자체 코드 품질에는 P0/P1 없음.
