# Software Engineer Expert Opinion — Phase 1 Post-Audit Fixes (PR #4)

## 메타
- 감사 ID: EXT-AUD-2026-04-26-002
- 감사 단계: Stage 1 / Individual
- 전문가 시각: **Software (코드 품질·아키텍처·CI/CD·유지보수성)**
- 감사 날짜: 2026-04-26
- 대상: PR #4 squash merge `ee30c04` — MT-001~MT-005 처리

---

## 1. 발견사항 (Findings)

### 1.1 P0 처리 — `.github/CLAUDE.md` v2.0 sync (MT-001) ★

#### F-SW-01 — REVIEWER_DIRECTIVE.md v2.0 완전 인용
- 새 `CLAUDE.md` 가 v2.0 의 핵심 모두 반영:
  - "Role" 섹션이 외부 감사자 명시
  - "Required References" 에 REVIEWER_DIRECTIVE.md 최우선
  - "PR Audit Procedure" 가 4-md 폴더 구조 (`A1`/`A2`/`A3`/`00_FINAL`) 명시
  - "Verdict Rules" 5단계 일관 (PASS / CAUTION / MAJOR RISK / PHYSICAL VIOLATION / UNVERIFIED)
- **GitHub Action 이 이제 v2.0 외부 감사 자동화 작동 가능**

#### F-SW-02 — PR title 명명 규칙 명문화
- `phase<N>-part<NN>-<kind>: <summary>` + `<scope>-<kind>: <summary>` + `build(deps): bump ...` 3 패턴
- `kind`: add/update/fix/refactor/docs/test/audit/chore — 의미론 일관
- `pr-title.yml` workflow 가 본 규칙 자동 강제

### 1.2 아키텍처 개선 (MT-003)

#### F-SW-03 — `src/optics/` 모듈 신설로 의존 그래프 정리
```
constants ─┐
           ├─→ pupil  ─┐
optics ────┤            ├─→ aerial  ─┐
           ├─→ aerial   │             ├─→ tests
           └─→ (Phase 4 mask_3d 미래)
mask ──────────────────┴─→ aerial   ┘
```
- 더 이상 `aerial.py` 가 `pupil._wavefront` 를 lazy import 하지 않음
- top-level `from .optics import wavefront` (aerial.py:37, pupil.py:29)

#### F-SW-04 — `src/optics/__init__.py` 의 `__all__` 명시
- `["ZernikeCoeffs", "wavefront", "zernike_polynomial"]` 3개 export
- public API 가 import 시점에 명확

#### F-SW-05 — Phase 4 진입 준비도
- `src/mask_3d.py` 가 Phase 4 에서 absorber 위상 계산 시 같은 `wavefront()` 재사용 가능
- 추가 코드 작성 없이 import 만으로 활용

### 1.3 테스트 인프라 강화 (MT-004)

#### F-SW-06 — `tests/audits/` 서브폴더 신설
- `__init__.py` + `test_fft_invariants.py`
- `pytest.ini` 의 `python_files = phase*_*.py test_*.py` 와 호환
- 4개 테스트 자동 발견 + 통과

#### F-SW-07 — 테스트 명명 spec 역할 유지
- `test_fft_parseval_round_trip` — 무엇을 검증하는지 자명
- `test_fftshift_ifftshift_round_trip`
- `test_pupil_cutoff_frequency_matches_na_scaling`
- `test_grid_refinement_converges_for_resolved_pitch`
- 4개 모두 회귀 테스트가 아닌 invariant 테스트

### 1.4 Pre-commit 도입 (MT-005)

#### F-SW-08 — `.pre-commit-config.yaml` 합리적 baseline
- pre-commit-hooks v5.0.0:
  - check-yaml (workflow YAML 검증)
  - end-of-file-fixer
  - trailing-whitespace
- ruff-pre-commit v0.8.6:
  - ruff check --fix
  - ruff-format
- **개발자가 push 전에 자동 점검** → CI 사이클 단축

### 1.5 문서 동기화 (MT-002)

#### F-SW-09 — `진행계획서.md §5.1` 정확히 갱신
- Phase 1 코드 4개 항목 (`constants`, `pupil`, `mask`, `aerial`) → ✅ 완료
- `src/optics/zernike.py` 신규 항목 추가 ("1+ / cross")
- §5.2 테스트 표에 `tests/audits/test_fft_invariants.py` 추가
- §13 변경 이력 v1.1 entry (작성자: Codex)

#### F-SW-10 — `audits/AUDIT_LOG.md` 완료 task 분리 표 추가
- "미해결 mitigation task" + "완료된 mitigation task" 두 개 표
- MT-001~005 가 완료 표로 이동, MT-006 만 미해결로 남음
- **task tracking 정직**

---

## 2. 위험 (Risks)

### R-SW-01 — `__pycache__/` 가 git tracking 되는지 확인 필요 (낮음)
- 워크스페이스에 `__pycache__/` 다수 존재
- `.gitignore` 에 포함되어 있어야 함 (Python 표준)
- `git diff --check` 통과는 보고되었으나 `.gitignore` 직접 확인 필요
- **현재 영향**: PR #4 가 squash merge 되었으므로 main 에 누출 가능성

### R-SW-02 — `pre-commit install` 가 실제 실행되었는지 미확인 (낮음)
- `.pre-commit-config.yaml` 만으로는 hook 활성화 안 됨
- 개발자가 `pre-commit install` 한 번 실행 필요
- README 또는 CONTRIBUTING.md 에 명시 권고
- **현재 영향**: 다음 commit 부터 hook 미적용 가능

### R-SW-03 — `tests/audits/` 와 `audits/` 폴더의 명명 충돌 가능성 (낮음)
- `tests/audits/` = pytest invariant 테스트
- `audits/` = 감사 보고서 + INSTRUCTIONS
- 의미는 다르나 같은 단어 — 외부 contributor 가 혼동 가능
- **권고**: `tests/audits/` → `tests/invariants/` 같은 명명 고려 (P3)

### R-SW-04 — mypy strict 도입 timeline 여전히 미정 (중간, 의도된 deferred)
- EXT-AUD-001 R-SW-07 그대로
- `.github/workflows/ci.yml` 의 `continue-on-error: true` 유지
- pre-commit 에 mypy 미추가
- **권고**: 다음 PR 에 mypy 모듈별 strict 시작 (constants.py)

### R-SW-05 — `CONTRIBUTING.md` / `CHANGELOG.md` 부재 유지
- EXT-AUD-001 R-SW-06 그대로
- pre-commit 도입을 외부 contributor 가 알 방법이 없음
- **권고**: CONTRIBUTING.md 1-pager 추가 (P2)

---

## 3. 권고 (개별 권고 — 우선순위 시도)

### REC-SW-01 (P1) — `.gitignore` 확인 + `__pycache__/`, `.pytest_cache/`, `*.pyc` 명시 등록
- 작업량: 5분
- 효과: 향후 모든 PR 에서 캐시 파일 자동 제외

### REC-SW-02 (P2) — `CONTRIBUTING.md` 추가 (pre-commit 설치 가이드 포함)
- 내용:
  - 로컬 환경 셋업 (`pip install -r requirements-dev.txt`)
  - `pre-commit install` 1회 실행 안내
  - 본 프로젝트의 4-역할 self-audit + 3-전문가 외부 감사 흐름 요약
  - PR title 명명 규칙 인용
- 작업량: 1시간

### REC-SW-03 (P2) — pre-commit 에 mypy 추가 (R-AI-02 와 consensus)
- `.pre-commit-config.yaml` 에 `mirrors-mypy` repo 추가
- 처음에는 `--ignore-missing-imports` 등 관대한 설정
- 작업량: 30분

### REC-SW-04 (P3) — `tests/audits/` → `tests/invariants/` 또는 `tests/regressions/` 로 명명 변경 검토
- 현재 충돌 없으나 외부 인지 향상 목적
- 작업량: 10분 (rename + import path update)

---

## 4. 본 전문가가 답하지 않는 영역

- **EUV 전문가**: 리팩터의 물리적 의미 평가
- **AI 전문가**: 신규 invariant 테스트의 수치 적정성
- **Data Scientist**: EXT-AUD-001 → 002 메트릭 변화 정량화

---

## 5. 한 줄 요약 판정

**🟢 PASS (clean)** — MT-001~005 5건 모두 권고와 정확히 일치하게 처리됨. 특히 MT-001 (CLAUDE.md v2.0 sync) 은 외부 감사 자동화의 결정적 enabler 였으며 결과물 품질 우수. 미세 권고 (`.gitignore` 확인, CONTRIBUTING.md 추가) 만 P1/P2 backlog 에 추가. 본 PR 자체에 P0 없음.
