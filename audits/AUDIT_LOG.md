# Audit Log — 감사 이력

> 모든 감사의 한 줄 요약을 시간 순으로 기록한다.
> 상세 보고서는 각 역할 폴더의 `reports/` 에 저장된다.

---

## 사용법

새 감사 완료 시 아래 표 가장 위에 한 줄 추가:

```
| YYYY-MM-DD | Phase | 역할 | 주제 | 판정 | 보고서 파일 | 비고 |
```

---

## 감사 기록

| 날짜 | Phase | 역할 | 주제 | 판정 | 보고서 | 비고 |
|------|-------|------|------|------|--------|------|
| 2026-04-26 | meta | mitigation | EXT-AUD-001 P0/P1 후속 조치 | 🟢 PASS | [REVIEWER_DIRECTIVE.md](../REVIEWER_DIRECTIVE.md) | MT-001~005 처리: CLAUDE.md v2 sync, 진행계획서 §5.1 갱신, Zernike 공용화, FFT invariant test, pre-commit 도입 |
| 2026-04-26 | meta | external (DS) | EXT-AUD-001 Phase 1 첫 외부 감사 (4-md) | 🟡 PASS w/ 1 P0 | [00_FINAL_audit.md](external/reports/EXT-AUD-2026-04-26-001_phase1_initial_review/00_FINAL_audit.md) | REVIEWER_DIRECTIVE v2.0 발효 후 첫 시연. P0 1건: .github/CLAUDE.md sync 필요 |
| 2026-04-26 | Phase 1 | sim (간접) | aerial image MVP 완료 | 🟢 PASS | [docs/phase1_design.md](../docs/phase1_design.md) | 5/5 unit tests PASS, KPI K1·K2 합격, 7 단순화 4중 기록 100% |
| 2026-04-26 | meta | system | REVIEWER_DIRECTIVE v2.0 + audits/external/ 신설 | 🟢 PASS | [REVIEWER_DIRECTIVE.md](../REVIEWER_DIRECTIVE.md) | 3 전문가 + Data Scientist 통합자 2-stage 구조 |
| 2026-04-25 | meta | system | 감사 시스템 초기 구축 | 🟢 PASS | (본 폴더 자체) | 4개 INSTRUCTIONS + 템플릿 작성 완료 |

---

## 통계 (자동 갱신 대상)

```
총 감사 수:           5
PASS:                4
PASS WITH P0:        1
CAUTION:             0
MAJOR RISK:          0
PHYSICAL VIOLATION:  0
UNVERIFIED:          0
```

---

## 미해결 mitigation task

> P0/P1/CAUTION 판정에 따라 생성된 task 중 미완료 항목.

| ID | 생성일 | 등급 | 내용 | 데드라인 | 출처 |
|----|--------|------|------|----------|------|
| MT-006 | 2026-04-26 | P1 | Phase 3 entry 전 defocus 부호 컨벤션 fix + 테스트 | Phase 3 entry 전 | EXT-AUD-001 §4.3 P1-06 |

---

## 완료된 mitigation task

| ID | 완료일 | 등급 | 내용 | 반영 파일 |
|----|--------|------|------|-----------|
| MT-001 | 2026-04-26 | **P0** | `.github/CLAUDE.md` 를 REVIEWER_DIRECTIVE.md v2.0 으로 sync | `.github/CLAUDE.md` |
| MT-002 | 2026-04-26 | P1 | `진행계획서.md §5.1` 상태표를 ✅로 갱신 | `진행계획서.md` |
| MT-003 | 2026-04-26 | P1 | `_wavefront` → `src/optics/zernike.py` 추출 | `src/optics/zernike.py`, `src/pupil.py`, `src/aerial.py` |
| MT-004 | 2026-04-26 | P1 | FFT invariant tests 신설 | `tests/audits/test_fft_invariants.py` |
| MT-005 | 2026-04-26 | P1 | pre-commit hook 도입 | `.pre-commit-config.yaml`, `requirements-dev.txt` |

---

## 차단 이력 (Block History)

> MAJOR RISK 또는 PHYSICAL VIOLATION으로 차단된 PR / Phase Gate 기록.

| 날짜 | 대상 | 차단 사유 | 해결 방법 | 해결 날짜 |
|------|------|-----------|-----------|-----------|
| (없음) | | | | |
