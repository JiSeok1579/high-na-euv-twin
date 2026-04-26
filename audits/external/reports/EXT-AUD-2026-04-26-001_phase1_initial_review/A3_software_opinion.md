# Software Engineer Expert Opinion — Phase 1 Initial Review

## 메타
- 감사 ID: EXT-AUD-2026-04-26-001
- 감사 단계: Stage 1 / Individual
- 전문가 시각: **Software (코드 품질·아키텍처·CI/CD·유지보수성)**
- 감사 날짜: 2026-04-26
- 대상: 전체 워크스페이스의 코드 품질·CI/CD·문서·도구 인프라 측면

---

## 1. 발견사항 (Findings)

### 1.1 코드 품질

#### F-SW-01 — Type hints 일관 적용
- 모든 public 함수가 type hint
- `dataclass`, `Mapping`, `tuple` 등 모던 typing 사용
- mypy 통과 가능한 수준

#### F-SW-02 — Frozen dataclasses for config containers
- `PupilSpec`, `MaskGrid`, `WaferGrid` 모두 `@dataclass(frozen=True)`
- immutability 보장 → mutation bug 차단
- `__post_init__` 검증 패턴 일관

#### F-SW-03 — NumPy-style docstrings 일관
- Parameters / Returns 섹션 명시
- physics reference 인용 (paper #N, physics_doc Part X)
- 단위 명시

#### F-SW-04 — 마법 숫자 제거
- λ, NA, K1, K2 모두 `constants.py` 에 단일화
- 헬퍼 함수 (`rayleigh_resolution`, `depth_of_focus`) 제공

### 1.2 아키텍처

#### F-SW-05 — 모듈 분리 합리적
- 4 모듈: `constants` / `pupil` / `mask` / `aerial`
- 단일 책임 (SRP) 준수
- public API vs `_private` 일관

#### F-SW-06 — 가역적 추상화 (REVIEWER_DIRECTIVE P4)
- `MaskGrid.kirchhoff_mask()` → 향후 `Mask3DModel`, `RCWAMaskModel` 가 같은 interface 따를 수 있도록 `complex` field 반환
- pupil도 `PupilSpec` dataclass로 추상화

#### F-SW-07 — Anamorphic option (anamorphic=False) 제공
- 테스트용 1× 모드 분리
- production 코드에서 옵션 노출 시 좋은 패턴

### 1.3 테스트

#### F-SW-08 — 테스트 1:1 매핑
- 5개 테스트 = 4 verification + 1 bonus
- 진행계획서 §4.1 verification 항목과 1:1 대응
- 각 테스트 docstring이 어느 verification 인지 명시

#### F-SW-09 — 테스트 명명 (test = spec)
- `test_pinhole_psf_radial_structure` → 무엇을 검증하는지 자명
- `test_line_space_resolution_vs_pitch`
- 회귀 테스트 아닌 spec 역할

#### F-SW-10 — pytest 인프라 정비
- `pytest.ini` 에 testpaths, naming conventions, addopts
- `tests/conftest.py` 에 sys.path 설정 (project root importable)

### 1.4 CI/CD

#### F-SW-11 — `.github/` 풀 셋업 완료
- `workflows/ci.yml`, `claude.yml`, `pr-title.yml`, `auto-merge.yml`
- `CODEOWNERS`, `PULL_REQUEST_TEMPLATE.md`
- `ISSUE_TEMPLATE/audit_request.md`
- `dependabot.yml`, `labeler.yml`
- `CLAUDE.md` (Claude Action 시스템 프롬프트)

#### F-SW-12 — `requirements-dev.txt` 존재
- numpy, scipy, matplotlib, pytest, pytest-cov, mypy, ruff
- CI workflow와 sync 됨

#### F-SW-13 — PR title 검증 워크플로
- `pr-title.yml` 가 `phase<N>-part<NN>-<kind>: <summary>` 패턴 강제
- squash merge title 품질 보장

### 1.5 문서

#### F-SW-14 — 단순화 4중 기록 충실 (REVIEWER_DIRECTIVE P3)
- 코드 docstring (S2 in mask.py 등)
- `docs/phase1_design.md §5` 표
- `PROJECT_OVERVIEW.md §4.2` Out-of-Scope
- `docs/phase1_design.md §10` Limitation
- ✓ 4-fold record principle 준수

#### F-SW-15 — 디버깅 trace 정직한 기록
- `docs/phase1_design.md §3, §4` 가 pixel quantization, noise floor 디버깅 과정 명시
- 6개월 후 다른 사람이 읽어도 왜 그런 코드인지 이해 가능

---

## 2. 위험 (Risks)

### R-SW-01 (★ 결정적) — `.github/CLAUDE.md` 가 REVIEWER_DIRECTIVE.md v2.0 과 mismatch
- 현재 `.github/CLAUDE.md` 는 4-역할 self-audit 시스템만 인용
- v2.0 (3 전문가 + Data Scientist 통합자) 미반영
- **영향**: GitHub Action에서 Claude가 PR 검토 시 v1.0 4-역할로 작동, 본 외부 감사 시스템 (audits/external/) 무시
- **즉시 수정 필요** (P0)

### R-SW-02 — 진행계획서.md §5.1 상태표 stale
- src/constants.py, pupil.py, mask.py, aerial.py 모두 "미시작" 으로 표기
- 실제는 완료됨
- PROJECT_OVERVIEW.md §6.2 와 모순
- documentation drift

### R-SW-03 — AUDIT_LOG.md Phase 1 entry 누락
- 직전 점검에서 발견했으나 아직 미수정
- CI/CD STAGE 6 housekeeping 불완전

### R-SW-04 — `aerial.py` lazy import (Software 시각, AI 전문가와 consensus)
- `from .pupil import _wavefront` 함수 내부 import
- 단일 instance 시 무해, Phase 4 추가 시 위험

### R-SW-05 — pre-commit hook 부재
- ruff / mypy / black 같은 linter가 push 전 강제되지 않음
- CI에서만 잡으면 PR cycle 길어짐
- **권고**: `.pre-commit-config.yaml` 추가

### R-SW-06 — `CONTRIBUTING.md`, `CHANGELOG.md` 부재
- 외부 contributor 가이드 부재
- 변경 추적이 git log + 진행계획서 §13 에만 의존

### R-SW-07 — mypy `continue-on-error: true` (AI 전문가와 consensus)
- type error 누적 위험
- "점차 강제" 시점 미정

### R-SW-08 — 노트북의 reproducibility metadata 부재
- `notebooks/0_first_aerial_image.ipynb` 가 실행 시점, dependency version 기록 안 함
- 6개월 후 재실행 시 결과 다를 수 있음

---

## 3. 권고 (개별 권고 — 우선순위 시도)

### REC-SW-01 (P0) — `.github/CLAUDE.md` 를 REVIEWER_DIRECTIVE.md v2.0 으로 sync
- 추가할 내용:
  - 본 GitHub Action은 PR 검토 시 4-md 외부 감사 보고서 작성 (A1, A2, A3, 00_FINAL)
  - 저장 위치: `audits/external/reports/<EXT-AUD-id>/`
  - REVIEWER_DIRECTIVE.md §3 양식 준수
- 작업량: 30분
- **블로킹**: 다음 PR 전 필수

### REC-SW-02 (P1) — `진행계획서.md §5.1` 상태표 갱신
- Phase 1 항목 (constants, pupil, mask, aerial, tests, notebook, docs) 모두 ✅ 표기
- 작업량: 10분

### REC-SW-03 (P1) — `audits/AUDIT_LOG.md` 에 Phase 1 + EXT-AUD-001 entry 추가
- 2개 entry: Phase 1 완료 + 본 외부 감사 보고서
- 작업량: 5분

### REC-SW-04 (P1) — `_wavefront` 추출 (AI 전문가 REC-AI-01 와 consensus)
- 작업량: 1시간

### REC-SW-05 (P1) — pre-commit hook 도입
- `.pre-commit-config.yaml` 신설:
  - ruff (lint + format)
  - mypy (basic)
  - check-yaml, end-of-file-fixer, trailing-whitespace
- 작업량: 30분

### REC-SW-06 (P2) — `CONTRIBUTING.md`, `CHANGELOG.md` 추가
- CONTRIBUTING: 본 프로젝트의 4-역할 self-audit + 3-전문가 외부 감사 흐름 안내
- CHANGELOG: keepachangelog.com 양식
- 작업량: 1시간

### REC-SW-07 (P2) — mypy strict 점진적 도입 (AI 전문가 REC-AI-03 와 consensus)
- 작업량: 1-2주 점진적

### REC-SW-08 (P3) — 노트북 reproducibility metadata
- 첫 셀에 `pip freeze | grep -E "numpy|scipy|matplotlib"` 결과 기록
- 또는 `pyproject.toml` 의 dependency lock
- 작업량: 30분

---

## 4. 본 전문가가 답하지 않는 영역

- **EUV 전문가**: 물리·도메인 정확성 판정
- **AI 전문가**: 수치 구현의 정확성·sampling
- **Data Scientist**: 권고들의 우선순위 매트릭스 적용 + 충돌 중재 + 메트릭 정량화

---

## 5. 한 줄 요약 판정

**PASS with 1 P0 (CLAUDE.md sync)** — 코드 품질·테스트 인프라·CI/CD 셋업·문서화 모두 매우 양호. 단 `.github/CLAUDE.md` 가 REVIEWER_DIRECTIVE.md v2.0 과 mismatch 인 결정적 issue 1건 존재 — 다음 PR 전 즉시 sync 필요. 그 외는 housekeeping 정리 + pre-commit 도입 정도의 P1.
