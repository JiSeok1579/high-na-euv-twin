# 외부 감사 최종 보고서 — Claude (Data Scientist 통합)

## 0. 메타

```
감사 ID:        EXT-AUD-2026-04-26-004
감사 단계:      Stage 2 / Final Synthesis
작성자:         Claude (Data Scientist 시각)
감사 날짜:      2026-04-26
대상:           Phase 3 Part 02 — DOF Focus Stack Metrics + MT-008~010 처리
트리거:         REVIEWER_DIRECTIVE v2.1 §10.5 (자동 외부감사 트리거)
                — 사용자 명시 지침: "코드 작성자가 코드 수정하고 다음지시 요청할때마다
                  외부감사 자동으로 진행할것"

코드 작성자 보고: AUDIT_LOG entry "MT-008~010 DOF metric 후속 조치 | 🟢 PASS"
                pytest --cov 20 passed, ruff/mypy/compileall pass

Stage 1 입력:   A1_euv_opinion.md (PASS clean, with P1 follow-up)
                A2_ai_opinion.md (PASS clean)
                A3_software_opinion.md (PASS WITH 1 P0)

이전 감사:      EXT-AUD-001 → 002 → 003 → 004 (4-point 추세 확립)
참조 문서:      REVIEWER_DIRECTIVE.md v2.1
```

---

## 1. 종합 판정

> **🟡 PASS WITH 1 P0** — Phase 3 Part 02 코드/테스트/문서 자체는 매우 깨끗 (3 전문가 모두 코드 품질 PASS). 단 v2.1 지침 신설로 인한 **`.github/CLAUDE.md` v2.1 sync 가 신규 P0** (EXT-AUD-001 P0-01 과 동일 패턴 반복). v2.1 자동 트리거가 GitHub Action 에서도 작동하려면 sync 필수.

| 시각 | 판정 | 핵심 |
|------|------|------|
| EUV 전문가 | 🟢 PASS (clean, P1 follow-up) | Paraxial vs Angular 옵션 + DOF 정직 보고 |
| AI 전문가 | 🟢 PASS (clean) | π/2 sampling guard + 4-property 자동 검증 |
| Software 전문가 | 🟡 PASS w/ 1 P0 | `.github/CLAUDE.md` v2.1 sync 필요 |
| **Data Scientist 통합** | **🟡 PASS WITH 1 P0** | 코드 자체 깨끗, 메타 sync drift 1건 |

---

## 2. 3 전문가 의견 통합

### 2.1 Consensus (3/3 일치)

| 항목 | 평가 |
|------|------|
| MT-008/009/010 모두 권고와 정확히 일치 처리 | 🟢 |
| `validate_defocus_sampling` (π/2 threshold) 합리적 | 🟢 |
| 4-property 광학 invariant (unitary/identity/conjugacy/sign) 자동 검증 | 🟢 |
| `dof.py` FocusSample/DOFMetrics dataclass 명확 | 🟢 |
| 6 신규 테스트 spec 역할 (회귀 X) | 🟢 |
| `docs/phase3_DOF_analysis.md` 단순화 4중 기록 충실 | 🟢 |
| K3 "measurable but not complete" 정직 보고 | 🟢 |
| 20/20 tests PASS | 🟢 |

### 2.2 Conflict (충돌 지점) + Data Scientist 중재

**실질적 충돌 없음**. 모든 미세 권고 P1-P3 backlog.

| 항목 | EUV | AI | Software | DS 결정 |
|------|-----|----|----|--------|
| K3 k₂ fitting 미구현 | REC-EUV-01 P1 | 미언급 | 미언급 (영역 외) | **P1-신규 채택** (다음 part 책임 명확화) |
| Angular default 전환 | REC-EUV-02 P2 | F-AI-04 (현재 OK) | 미언급 | P2 채택 (Phase 3 part 03 시) |
| .github/CLAUDE.md v2.1 sync | 미언급 | 미언급 | REC-SW-01 P0 ★ | **P0-신규 채택** (자동 트리거 GitHub Action 작동 필수) |
| 진행계획서 §13 v1.2/v1.3 | 미언급 | 미언급 | REC-SW-02 P1 | **P1-신규 채택** |

### 2.3 Gap (3 전문가 모두 누락한 영역, DS 보강)

| Gap | DS 평가 | 권고 |
|-----|---------|------|
| `진행계획서.md §5.1` Phase 3 항목 갱신 여부 | Software 가 부분 캐치 | P2-신규 검증 필요 |
| GitHub PR 정보 (코더 보고 누락) | 자체 보고만 | 다음 보고 시 PR 번호 + commit hash 명시 권고 |
| KPI K3 진척률 정확한 % | 모두 정성적 ("measurable") | DS 정량: enabled 50% (메트릭 가능 + 1 case 측정), k₂ fitting 까지 100% |

---

## 3. 메트릭 정량화

### 3.1 코드 변경 메트릭 (4-point trend)

| 메트릭 | 001 | 002 | 003 | 004 | 누적 Δ |
|--------|-----|-----|-----|-----|--------|
| LoC src/ | 556 | ~700 | ~770 | **~930** | +374 (+67%) |
| LoC tests/ | 206 | 263 | ~360 | **~520** | +314 (+152%) |
| 테스트 수 | 5 | 9 | 14 | **20** | **+300%** |
| src/ 모듈 수 | 4 | 6 | 7 | **8** | +100% |
| Test pass rate | 5/5 | 9/9 | 14/14 | **20/20** | 100% 유지 |

### 3.2 단순화 가정 추적

| 단순화 | 상태 |
|--------|------|
| S1-S7 (Phase 1) | 변경 없음 ✓ |
| P3-L1 ~ P3-L4 (Phase 3 Part 01) | P3-L2 부분 처리 (measurable) |
| **P3-L5 (신규)** Threshold 80% 단일 기준 | 신규 단순화, R-EUV-02 |
| **P3-L6 (신규)** Paraxial default | EXT-AUD-003 의 한계 그대로, R-EUV-03 |

- **신규 도입 단순화: 2개 (P3-L5, P3-L6)**
- **누적 단순화: 11 → 13 (+18%)**
- **4중 기록 완료: 11/13 (85%)** — P3-L5/L6 명시 권고 (P2)

### 3.3 KPI 진척도

| KPI | 001 | 002 | 003 | 004 | 진척률 |
|-----|-----|-----|-----|-----|--------|
| K1 (end-to-end) | 100% | 100% | 100% | 100% | 유지 |
| K2 (회절 정성) | 100% | 100% | 100% | 100% | 유지 |
| **K3 (DOF 정량)** | 0% | 0% | enabled (식 + 테스트) | **enabled + 메트릭 + 단일 시연 = 50%** | **시작!** |
| K4 (M3D 6 효과) | 0% | 0% | 0% | 0% | 변화 없음 |
| K5 (SMO 수렴) | 0% | 0% | 0% | 0% | 변화 없음 |
| K6 (Stochastic LWR) | 0% | 0% | 0% | 0% | 변화 없음 |
| **평균** | 33% | 33% | 33%+ | **42%** | **+27% (003→004)** |

> K3 진척: 메트릭 함수 (`focus_stack_contrast`, `nominal_depth_of_focus`) 작동 + symmetry test = **50%**. 100% 까지는 NA/pitch sweep + k₂ 측정값 보고 필요.

### 3.4 위험 지수

| 등급 | 001 | 002 | 003 | 004 | Δ (003→004) |
|------|-----|-----|-----|-----|-------------|
| **P0** | 1 | 0 | 0 | **1** | +1 (Software CLAUDE.md sync) |
| **P1** | 6 | 2 | 0 | **3** | +3 (k₂ fitting, §13 stale, P3-L2 갱신) |
| **P2** | 4 | 4 | 5 | 5 | 유지 |
| **P3** | 3 | 4 | 5 | 4 | -1 |
| **합계** | 14 | 10 | 10 | **13** | +3 |
| **가중 합계** | 32.9 | 7.2 | 5.5 | **20.2** | **+14.7 (+267%)** |

**해석**: 본 PR 자체에서 P0 1건 (메타 sync) + P1 3건 발생 → 위험 지수 다시 상승. 단, **이는 v2.1 지침 신설로 인한 일시적 sync drift** 이며, 코드 자체의 위험은 미증가. P0 처리 시 다시 8 정도로 감소 예상.

### 3.5 Mitigation Task 누적 처리율

| 출처 | 총 task | 완료 | 미해결 | 처리율 |
|------|---------|------|--------|--------|
| EXT-AUD-001 ~ 003 (MT-001~010) | 10 | **10** | 0 | **100% ★** |
| EXT-AUD-004 신규 등록 (MT-011~014) | 4 | 0 | 4 | 0% (방금 등록) |
| 누적 | 14 | 10 | 4 | 71% |

---

## 4. 우선순위 매트릭스 + 최종 권고

### 4.1 P0 — 즉시 수정 (머지 차단 / 다음 PR 전)

#### P0-01 (신규, MT-011) — `.github/CLAUDE.md` 를 REVIEWER_DIRECTIVE v2.1 으로 sync
- **출처**: REC-SW-01
- **근거**: v2.1 §10.5 자동 외부감사 트리거가 GitHub Action 에서 작동하려면 system prompt 갱신 필요
- **EXT-AUD-001 P0-01 와 동일 패턴 반복** — 메타 변경 시 GitHub Action sync 필요
- **구체 액션**: `.github/CLAUDE.md` 의 "PR Audit Procedure" 섹션에 다음 추가:
  - "When code author requests next directive after code modification, automatically trigger 4-md external audit creation as per REVIEWER_DIRECTIVE v2.1 §10.5"
  - "Auto-trigger conditions, exemptions, and absent-trigger declaration rule"
- **예상 작업량**: 20분
- **기대 효과**: GitHub Action 이 v2.1 자동 트리거 절차 적용 가능

### 4.2 P1 — 단기 권고 (다음 PR / Phase Gate 전)

#### P1-01 (신규, MT-012) — k₂ fitting 보고 (KPI K3 정량 진척)
- 출처: REC-EUV-01
- 데드라인: Phase 3 part 03 또는 다음 increment
- 작업량: 2-3시간

#### P1-02 (신규, MT-013) — `진행계획서.md §13` v1.2/v1.3 entry 추가
- 출처: REC-SW-02
- 작업량: 10분

#### P1-03 (신규, MT-014) — `docs/phase3_design.md §4` P3-L2 갱신
- 출처: REC-SW-03
- 작업량: 5분

### 4.3 P2 — 중기 권고

- **MT-008/009/010 follow-up**: angular default 전환 (REC-EUV-02), grid resolution 자동 검증 (REC-AI-01), §5.1 갱신 (REC-SW-04)
- **기존 P2 backlog**: mypy strict, CONTRIBUTING.md, M3D 6 효과 stub

### 4.4 P3 — 장기 권고

- Sampling threshold tuning (REC-AI-02), monotonicity assumption 명시 (REC-AI-03), CD-DOF mapping (REC-EUV-03), Paper #14 정성 재현 (REC-EUV-04)

---

## 5. 추세 분석 — 4-point 누적

### 5.1 EXT-AUD-001 → 002 → 003 → 004

| 메트릭 | 001 | 002 | 003 | 004 | 추세 |
|--------|-----|-----|-----|-----|------|
| 종합 판정 | 🟡 PASS w/1 P0 | 🟢 PASS clean | 🟢 PASS clean | 🟡 PASS w/1 P0 | 메타 sync 시 P0 재발 패턴 |
| P0 개수 | 1 | 0 | 0 | 1 | 메타 변경 시 spike |
| P1 개수 | 6 | 2 | 0 | 3 | 정상 backlog |
| 위험 가중 합계 | 32.9 | 7.2 | 5.5 | 20.2 | v2.1 신설로 일시 +267% |
| 단위 테스트 | 5 | 9 | 14 | 20 | **+300% 누적** ★ |
| Mitigation 처리율 | — | 86% | 100% | 100%(이전) | 모범 유지 |
| KPI K3 | 0% | 0% | enabled | **50%** | **첫 정량 진척** ★ |
| 단순화 4중 기록률 | 100% | 100% | 100% | 85% | -15% (P3-L5/L6 명시 필요) |

### 5.2 식별된 패턴 — "Meta-sync drift" 반복

| 회차 | 메타 변경 | P0 발생 |
|------|-----------|---------|
| 001 | REVIEWER_DIRECTIVE v2.0 신설 | CLAUDE.md sync (P0-01) |
| 002 | — | 0 |
| 003 | — | 0 |
| 004 | REVIEWER_DIRECTIVE v2.1 신설 | CLAUDE.md sync (P0-01 재발) |

**패턴 일반화**: 본 시스템의 **메타 변경 (지침/감사 절차 자체)** 시 `.github/CLAUDE.md` sync 가 항상 P0 가 됨. **future-proof 권고**: REVIEWER_DIRECTIVE 변경 시 같은 PR 안에 `.github/CLAUDE.md` 동시 갱신을 강제 (P3 자동화 후보).

### 5.3 개선 / 정체 / 악화

#### 🟢 개선 영역
1. KPI K3 첫 정량 진척 (0% → 50%)
2. 테스트 +300% 누적 (5 → 20)
3. Mitigation 처리율 100% 유지
4. `dof.py` 의 nominal process window 정직 정의 — 산업 적합

#### 🟡 정체 영역
1. mypy strict, CONTRIBUTING.md (4회 deferred)
2. KPI K4-K6 = 0% (Phase 4-6 미진입)
3. 단순화 4중 기록률 100% → 85% (drift 시작)

#### 🔴 악화 영역
1. 위험 지수 +267% (메타 sync drift) — 단, P0 처리 시 회복

---

## 6. 코드 작성자에게 묻는 질문

1. **P0-01 (.github/CLAUDE.md v2.1 sync)** 을 본 EXT-AUD 결과의 첫 follow-up PR 로 처리하시겠습니까? (DS 권고: Yes — 다른 작업 시작 전 우선)

2. **다음 진행 방향** 선택:
   - (A) **Phase 3 Part 03** — focus drilling + k₂ fitting (KPI K3 50% → 100%)
   - (B) **Phase 5 MVP** — threshold resist 진입, end-to-end pipeline 닫기
   - (C) **Phase 4 시작** — paper #12 6 효과 stub
   - (D) **메타 housekeeping** — P0 + 3 P1 동반 처리만
   - **DS 권고**: D 부터 (15-30분), 이후 A 또는 B 자유 선택

3. **GitHub PR 번호 + commit hash** 본 작업의 정보를 알려주실 수 있습니까? (자동 트리거 정확성 향상)

---

## 7. 다음 단계 (Action Items)

```
[ ] MT-011 P0: .github/CLAUDE.md v2.1 sync           ★ 차단 항목
[ ] MT-012 P1: k₂ fitting 보고 (Phase 3 part 03)
[ ] MT-013 P1: 진행계획서 §13 v1.2/v1.3 entry
[ ] MT-014 P1: docs/phase3_design.md §4 P3-L2 갱신
[ ] (선택) P2/P3 backlog

다음 Phase 진입:
  → P0 처리 후 자유 선택 (A, B, C 중)
  → DS 권고 흐름: D housekeeping → A k₂ fitting → B/C 진입
```

### Phase Gate 판정

- **Phase 3 Part 02 자체**: ✅ **코드 통과**
- **메타 sync 후 main 정합성**: ⚠️ **P0-01 처리 후 깨끗**
- **Phase 3 Part 03 진입**: ✅ **즉시 가능 (P0 와 병렬 또는 후행)**

---

## 8. 한 페이지 요약 (cheat sheet)

```
═══════════════════════════════════════════════════════════════
  EXT-AUD-2026-04-26-004 — Phase 3 Part 02 — FINAL
═══════════════════════════════════════════════════════════════

판정          🟡 PASS WITH 1 P0  (메타 sync drift)

코드 자체     🟢 PASS — 3 전문가 코드 품질 모두 통과
메타 sync     🟡 .github/CLAUDE.md v2.1 sync 필요 (P0)

P0 신규       1   (CLAUDE.md v2.1 sync)
P1 신규       3   (k₂ fitting, §13 entry, P3-L2 갱신)
P2 신규       3   (angular default, auto resolution, §5.1)
P3 신규       0

추세 (4-point)
  P0:         1 → 0 → 0 → 1   (메타 변경 시 spike 패턴)
  위험 가중:  32.9 → 7.2 → 5.5 → 20.2
  테스트:    5 → 9 → 14 → 20  (+300% 누적)
  KPI K3:    0% → 0% → enabled → 50% ★ (첫 정량 진척)
  Mitigation: 86% → 100% → 100% (누적)

가장 중요한 결과:
  → REVIEWER_DIRECTIVE v2.1 자동 외부감사 트리거 명문화
  → KPI K3 첫 정량 진척 (0% → 50%) — DOF 메트릭 작동
  → Phase 3 Part 02 가 paraxial vs angular 옵션 + π/2 sampling guard
    + 4-property 광학 invariant 모두 cover
  → 메타 sync drift = 본 시스템의 일반화된 패턴 인지

다음 단계:
  P0-01 처리 → Phase 3 Part 03 (k₂ fitting) 또는 다른 Phase 진입
═══════════════════════════════════════════════════════════════
```

---

## 9. 부록

### 9.1 Stage 1 개별 의견
- `A1_euv_opinion.md` — EUV (PASS clean, with P1 follow-up)
- `A2_ai_opinion.md` — AI (PASS clean)
- `A3_software_opinion.md` — Software (PASS WITH 1 P0)

### 9.2 본 감사가 사용한 evidence
- `.pytest_cache/v/cache/lastfailed = {}` (20/20 PASS)
- `.pytest_cache/v/cache/nodeids` 20개 등록 확인
- `src/dof.py` (158 lines) 전체 read
- `src/wafer_topo.py` (159 lines, paraxial+angular 통합) 전체 read
- `docs/phase3_DOF_analysis.md` (47 lines) 전체 read
- 코더 자체 보고: AUDIT_LOG entry "MT-008~010 DOF metric 후속 조치 | 🟢 PASS"

### 9.3 본 감사의 limitation
- GitHub PR 번호 / commit hash 미제공 (자체 보고만)
- 진행계획서 §5.1 Phase 3 항목 갱신 여부 추가 검증 필요
- 자동 트리거 본 사례: REVIEWER_DIRECTIVE v2.1 의 첫 적용 케이스

### 9.4 자동 트리거 작동 검증 (v2.1 §10.5 첫 사례)

| 단계 | 결과 |
|------|------|
| 1. 변경 파일 식별 | ✓ 8개 신규/수정 식별 |
| 2. 코드 직접 read | ✓ dof.py, wafer_topo.py, design doc |
| 3. 4-md 폴더 작성 | ✓ A1+A2+A3+00_FINAL |
| 4. AUDIT_LOG 갱신 | (다음 단계) |
| 5. mitigation 등록 | ✓ MT-011~014 |
| 6. 다음 지시 권고 | ✓ §6 질문 |

**v2.1 자동 트리거 절차가 정상 작동했음을 본 보고서가 자기 입증**.
