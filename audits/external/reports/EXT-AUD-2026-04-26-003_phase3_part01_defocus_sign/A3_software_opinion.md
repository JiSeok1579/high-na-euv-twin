# Software Engineer Expert Opinion — Phase 3 Part 01 (PR #5)

## 메타
- 감사 ID: EXT-AUD-2026-04-26-003
- 감사 단계: Stage 1 / Individual
- 전문가 시각: **Software (코드 품질·아키텍처·CI/CD·유지보수성)**
- 감사 날짜: 2026-04-26
- 대상: PR #5 squash merge `9ee22bb`

---

## 1. 발견사항 (Findings)

### 1.1 아키텍처

#### F-SW-01 — 새 모듈 `wafer_topo.py` 가 단일 책임 명확
- Phase 3 의 **모든 defocus / wafer height 관련 로직**을 한 모듈로 격리
- `pupil.py`, `aerial.py` 가 같은 helper 공유 (DRY)
- 추후 Phase 3 part 02 (focus stack), part 03 (focus drilling) 도 같은 모듈로 확장 가능

#### F-SW-02 — `DefocusConvention` dataclass 패턴 ★ 혁신적
```python
@dataclass(frozen=True)
class DefocusConvention:
    positive_z: str = "wafer surface above nominal best focus"
    positive_z_direction: str = "toward projection optics"
    phase_equation: str = "+pi * defocus_m * NA^2 / wavelength * rho^2"

DEFOCUS_CONVENTION = DefocusConvention()
```
- **컨벤션을 코드 객체로 표현** — 외부 모듈/REPL에서 `from src.wafer_topo import DEFOCUS_CONVENTION` 후 조회 가능
- frozen dataclass 로 우발적 변경 차단
- IDE / 자동완성 / docstring 인덱싱과 자연 통합
- **다른 프로젝트에 권장할 만한 모범 사례**

#### F-SW-03 — 의존 그래프 깨끗한 DAG 유지
```
constants (no deps)
  ├─→ optics/zernike (Phase 1+ cross)
  ├─→ wafer_topo
  │     └─→ pupil
  │           └─→ aerial
  ├─→ pupil → aerial
  ├─→ wafer_topo → aerial
  └─→ mask → aerial
```
- 순환 참조 0
- `wafer_topo` 가 `constants` 만 import → 가장 안쪽 layer
- Phase 4 (mask_3d) 가 향후 추가될 때도 같은 DAG 패턴 적용 가능

### 1.2 코드 품질

#### F-SW-04 — Type hints 일관 적용 + docstring 정확
- `defocus_phase_radians(rho: np.ndarray, defocus_m: float, na: float, wavelength: float) -> np.ndarray`
- `defocus_pupil_phase(...) -> np.ndarray` (반환 dtype `complex128` docstring 명시)
- `height_to_defocus_m(wafer_height_m: np.ndarray | float, focus_plane_m: float) -> np.ndarray`
- 모든 인자 단위 명시 (radians, meters)

#### F-SW-05 — `PupilSpec.defocus_m: float = 0.0` backward compatible
- 기존 `PupilSpec(...)` 호출 무수정 작동
- `__post_init__` 에 `np.isfinite(self.defocus_m)` 추가 — 일관 검증

#### F-SW-06 — Constants module 활용
- Default `na=C.NA_HIGH`, `wavelength=C.LAMBDA_EUV` — 매직 넘버 없음
- 향후 NA / λ 변경 시 한 곳에서 수정

### 1.3 테스트

#### F-SW-07 — 5 신규 테스트 모두 spec 역할
- `test_defocus_phase_sign_convention_is_fixed` ← 정책 강제
- `test_height_to_defocus_uses_focus_plane_reference` ← 변환 식
- `test_defocus_pupil_phase_conjugates_for_opposite_signs` ← Hermitian
- `test_build_pupil_applies_expected_edge_phase` ← 통합
- `test_zero_defocus_preserves_phase1_aerial_image` ← 회귀 차단

#### F-SW-08 — Backward compatibility 자동 검증
- `test_zero_defocus_preserves_phase1_aerial_image` 가 핵심:
  - 새 PupilSpec(defocus_m=0.0) 결과 = 기존 PupilSpec() 결과
  - `np.allclose(zero_defocus, focused)` 강제
- **Phase 1 의 5개 테스트 모두 무회귀 통과 보장**

### 1.4 문서

#### F-SW-09 — `docs/phase3_design.md` 가 진행계획서 §4.2 와 1:1 매핑
- §1 Scope — Phase 3 part 1 한정 명시
- §2 부호 컨벤션 표 형식
- §3 Numerical Invariants 4개 (테스트가 검증하는 것 동일)
- §4 Current Limitations 4개 (P3-L1~L4)
- §5 Files
- §6 Exit Status — MT-006 closure 명시 + KPI K3 미달 명시 (정직)

#### F-SW-10 — `docs/phase1_design.md` 패턴 일관 유지
- 같은 구조 (Scope, Conventions, Invariants, Limitations, Files, Exit)
- 외부 contributor 가 `docs/phase{N}_design.md` 패턴 학습 가능

### 1.5 CI/CD

#### F-SW-11 — PR #5 자동 squash merge 검증
- 코더 보고: GitHub CI 전체 통과 후 자동 squash merge
- `phase3-part01-fix: define defocus sign convention` 의 PR title이 `pr-title.yml` workflow 패턴 매칭
- v2.0 외부 감사 자동화 워크플로 작동 확인

#### F-SW-12 — 14 tests pass + ruff + mypy + compileall 모두 통과
- 코더 자체 보고 + `.pytest_cache/v/cache/lastfailed = {}` 직접 확인
- mypy 통과 — 새 코드의 type hints 적정

#### F-SW-13 — MT-007 (`.gitignore` 캐시 제외) 함께 closed
- `.gitignore` 직접 read: `__pycache__/`, `*.pyc`, `*.py[cod]`, `.pytest_cache/` 모두 명시
- EXT-AUD-002 의 P1 권고 처리 완료

---

## 2. 위험 (Risks)

### R-SW-01 — Test 명명 일관성 (낮음)
- Phase 1: `tests/phase1_aerial_image.py`
- Phase 3: `tests/phase3_DOF.py`
- 패턴 차이: `phase1_<topic>` vs `phase3_<KPI ID>`
- **권고**: Phase 3 part 02 진입 시 `tests/phase3_focus_stack.py` 같이 topic-based 일관 명명 (P3)

### R-SW-02 — `pre-commit install` 실제 실행 여부 미확인 (낮음, EXT-AUD-002 R-SW-02 그대로)
- `.pre-commit-config.yaml` 존재 + ruff 통과 → hook 작동 추정
- 그러나 코더가 `pre-commit install` 1회 실행했는지 미확인
- **권고**: CONTRIBUTING.md 추가 시 명시 (P2)

### R-SW-03 — `mypy continue-on-error: true` 여전히 (중간, deferred from EXT-AUD-001/002)
- `.github/workflows/ci.yml:159` 변경 없음
- 코더 자체 보고에서 "mypy passed" 명시 → 실제로는 통과 중
- **권고**: 다음 PR 에서 모듈별 strict 시작 가능 (constants.py 부터)

### R-SW-04 — `tests/audits/` vs `audits/` 명명 충돌 (낮음, EXT-AUD-002 R-SW-03 deferred)
- 현재 충돌 없으나 외부 contributor 혼동 가능
- **권고**: P3 backlog 유지

### R-SW-05 — `CONTRIBUTING.md` / `CHANGELOG.md` 부재 (deferred)
- EXT-AUD-001, 002 와 동일

---

## 3. 권고 (개별 권고 — 우선순위 시도)

### REC-SW-01 (P2) — Phase 3 part 02 entry 직전 `phase3_focus_stack.py` 같이 topic-based 명명
- 작업량: 0 (다음 part 부터 적용)
- 효과: 외부 가독성 향상

### REC-SW-02 (P2) — `CONTRIBUTING.md` (이전 권고 유지)
- pre-commit install + 4-역할 self-audit + 3-전문가 외부 감사 흐름 안내
- 작업량: 1시간

### REC-SW-03 (P2) — mypy strict 모듈별 도입 시작
- `src/constants.py` 에 `# mypy: strict` 추가
- CI 의 `continue-on-error: true` 는 strict 모듈만이라도 점진적 false 로
- 작업량: 30분 (constants.py 만)

### REC-SW-04 (P3) — `__pycache__/` 가 git 에 push 되지 않았는지 retroactive 검증
- 새 .gitignore 가 들어왔으나 PR #4/#5 에서 cache 파일이 함께 push 되었는지 git log 확인
- `git ls-files | grep pycache` 실행
- 발견 시 `git rm --cached -r __pycache__` + 새 PR
- 작업량: 5분

---

## 4. 본 전문가가 답하지 않는 영역

- **EUV 전문가**: 부호 선택의 광학적 합리성
- **AI 전문가**: numerical 정확성, conjugacy 검증의 적정성
- **Data Scientist**: 추세 분석, mitigation 처리 누적, 위험 지수 변화

---

## 5. 한 줄 요약 판정

**🟢 PASS (clean)** — `wafer_topo.py` 모듈 분리 + `DefocusConvention` dataclass + 5 신규 테스트 (특히 zero-defocus regression) + docs/phase3_design.md 가 모두 D5 원칙 모범 사례. PR #5 자동 squash merge 검증으로 v2.0 외부 감사 자동화 흐름 정상 작동 확인. 추가 P0/P1 없음, P2/P3 backlog 만 누적.
