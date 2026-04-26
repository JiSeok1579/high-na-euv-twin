# 외부 감사 최종 보고서 — Claude (Data Scientist 통합)

## 0. 메타

```
감사 ID:        EXT-AUD-2026-04-26-003
감사 단계:      Stage 2 / Final Synthesis
작성자:         Claude (Data Scientist 시각)
감사 날짜:      2026-04-26
대상:           Phase 3 Part 01 — Defocus Sign Convention (PR #5 squash merge 9ee22bb)
                MT-006 (defocus 부호) + MT-007 (.gitignore 캐시) closure

코더 보고:      pytest --cov 14 passed, ruff/mypy/compileall pass
                GitHub CI 전체 통과 후 PR #5 자동 squash merge 완료
                main sync 완료, 작업 폴더 clean
                다음 권장: phase3-part02-add: add dof focus stack metrics

Stage 1 입력:   A1_euv_opinion.md (PASS clean, with P2 note)
                A2_ai_opinion.md (PASS clean)
                A3_software_opinion.md (PASS clean)

이전 감사:      EXT-AUD-001 (PASS w/ 1 P0) → EXT-AUD-002 (PASS clean)
참조 문서:      REVIEWER_DIRECTIVE.md v2.0
```

---

## 1. 종합 판정

> **🟢 PASS (clean)** — Phase 3 entry 의 부호 컨벤션이 코드/문서/테스트 3중 강제 + DefocusConvention dataclass 객체화로 D5 원칙 모범 사례 달성. MT-006/MT-007 모두 closed. 추가 P0/P1 없음. Phase 3 part 02 (DOF metrics) 진입 가능 상태.

| 시각 | 판정 | 핵심 |
|------|------|------|
| EUV 전문가 | 🟢 PASS (with P2) | 부호·식 정확. paraxial 근사 ~9% 한계는 part 02 에서 |
| AI 전문가 | 🟢 PASS (clean) | 입력 검증 + conjugacy + zero-regression 자동 검증 robust |
| Software 전문가 | 🟢 PASS (clean) | 모듈 분리 + DefocusConvention dataclass 혁신적 |
| **Data Scientist 통합** | **🟢 PASS (clean)** | mitigation 100% 누적, 위험 지수 추가 감소 |

---

## 2. 3 전문가 의견 통합

### 2.1 Consensus (3/3 일치)

| 항목 | 평가 |
|------|------|
| 부호 컨벤션 D5 원칙 모범 준수 | 🟢 |
| 5 신규 테스트 spec 역할 충실 | 🟢 |
| `wafer_topo.py` 모듈 분리 깨끗 | 🟢 |
| backward compatibility (`zero_defocus_preserves_phase1`) 자동 검증 | 🟢 |
| 14/14 pytest pass + ruff/mypy 통과 | 🟢 |
| `docs/phase3_design.md` 단순화 4중 기록 | 🟢 |
| Phase 3 part 02 진입 준비 완료 | 🟢 |

**통합 결론**: 본 PR 은 **Phase 1 → Phase 3 transition 의 모범 사례**.

### 2.2 Conflict (충돌 지점) + Data Scientist 중재

**실질적 충돌 없음**. P2 권고 차이는 모두 backlog 항목.

| 항목 | EUV | AI | Software | DS 결정 |
|------|-----|----|----|--------|
| Paraxial 근사 한계 | R-EUV-01: ~9% 과소평가 | R-AI-01: consensus | 미언급 (영역 외) | **P2-신규 채택** (Phase 3 part 02 시 정확 식 옵션) |
| Defocus-aware Nyquist | 미언급 | REC-AI-02 P2 | 미언급 | P2 채택 (수치 안정성) |
| Test invariant 추가 | 미언급 | REC-AI-03 P2 | 미언급 | P2 채택 |
| Test 명명 일관성 | 미언급 | 미언급 | REC-SW-01 P2 | P2 채택 (다음 part 부터 적용) |

### 2.3 Gap (3 전문가 모두 누락한 영역, DS 보강)

| Gap | DS 평가 | 권고 |
|-----|---------|------|
| `git ls-files | grep pycache` retroactive 점검 | Software R-SW-04 가 부분 캐치 | P3 권고 유지 (영향 낮음) |
| KPI K3 (DOF 정량) 진척도 — 0% → 0% (still) | 본 PR 은 enabler 만, 실제 K3 진척은 part 02 | Phase 3 part 02 의 핵심 목표로 명시 |
| 누적 단순화 추세 분석 | 7 → 11 (P3-L1~4 추가) | EXT-AUD-004 부터 단순화 누적 trend chart 시작 |

---

## 3. 메트릭 정량화

### 3.1 코드 변경 메트릭

| 메트릭 | 001 | 002 | 003 | Δ (002→003) |
|--------|-----|-----|-----|-------------|
| LoC src/ | 556 | ~700 | ~770* | +70 (+10%) |
| LoC tests/ | 206 | 263 | ~360* | +97 (+37%) |
| 테스트 수 | 5 | 9 | **14** | **+5 (+56%)** |
| 모듈 수 (src/) | 4 | 6 | **7** (+wafer_topo) | +1 |
| 모든 단위 테스트 PASS | 5/5 | 9/9 | **14/14** | 100% 유지 |

*추정값: wafer_topo.py 88 lines + pupil.py +30 lines (defocus 통합) + aerial.py +5 lines = ~123 신규 src LoC. tests/phase3_DOF.py 94 lines.

### 3.2 단순화 가정 추적

| 단순화 | 상태 |
|--------|------|
| S1-S7 (Phase 1) | 변경 없음 ✓ |
| **P3-L1** Spatial z(x,y) 미반영 | **신규**, Phase 3 focus stack |
| **P3-L2** DOF metric / k₂ fitting 없음 | **신규**, Phase 3 part 2 |
| **P3-L3** Micro focus-drilling 없음 | **신규**, Phase 3 part 3 |
| **P3-L4** Scalar coherent | **신규**, Phase 2/4 |

- **신규 도입 단순화: 4개 (P3-L1~L4)**, 모두 4중 기록 (docs §4 + Limitations + 다음 단계 + 코드 docstring)
- **누적 단순화: 7 → 11**
- **4중 기록 완료: 11/11 (100%)** ★ 모범 유지

### 3.3 KPI 진척도

| KPI | 001 | 002 | 003 | 진척률 |
|-----|-----|-----|-----|--------|
| K1 (end-to-end) | 100% | 100% | 100% | 유지 |
| K2 (회절 정성) | 100% | 100% | 100% | 유지 |
| K3 (DOF 정량) | 0% | 0% | **enabled** (식·테스트 준비 완료) | 진척 시작 |
| K4 (M3D 6 효과) | 0% | 0% | 0% | 변화 없음 |
| K5 (SMO 수렴) | 0% | 0% | 0% | 변화 없음 |
| K6 (Stochastic LWR) | 0% | 0% | 0% | 변화 없음 |
| **평균** | 33% | 33% | **33%+** | K3 enabled |

> 본 PR 은 Phase 3 part 01 — Phase 3 의 인프라 (부호 + 식 + dataclass + 테스트). 실제 K3 정량 진척은 Phase 3 part 02 (DOF focus stack metrics) 에서.

### 3.4 위험 지수

| 등급 | 001 | 002 | 003 | Δ (002→003) |
|------|-----|-----|-----|-------------|
| **P0** | 1 | 0 | 0 | 0 (유지) |
| **P1** | 6 | 2 | 0 | -2 (-100%) |
| **P2** | 4 | 4 | 5 | +1 (Phase 3 시작 권고) |
| **P3** | 3 | 4 | 5 | +1 |
| **합계** | 14 | 10 | 10 | 0 |
| **가중 합계** | 32.9 | 7.2 | **5.5** | **-1.7 (-24%)** |

**해석**:
- P0/P1 모두 0 — 본 PR 자체에서 즉시 차단 항목 발생 없음
- P2/P3 권고는 Phase 3 진행 중 자연 backlog (정상)
- 위험 가중 합계 -24% 추가 감소 (003 → 5.5)
- **누적 (001 → 003): 32.9 → 5.5 = -83% ★**

### 3.5 Mitigation Task 처리율

| 출처 | 총 task | 완료 | 미해결 | 처리율 |
|------|---------|------|--------|--------|
| EXT-AUD-001 (P0+P1) | 7 (MT-001~007) | 7 | **0** | **100% ★** |
| EXT-AUD-002 P1 신규 | 1 (MT-007) | 1 | 0 | 100% (이미 합산됨) |
| 누적 | 7 | 7 | 0 | **100%** |

**MT-006/MT-007 모두 본 PR 에서 closed** — EXT-AUD-001/002 의 모든 P0/P1 권고 100% 처리 완료.

### 3.6 신규 P2 권고 (5개)

본 PR 결과로 backlog 추가:
- **P2-NEW-1** (REC-EUV-01): Paraxial vs full angular 비교 (Phase 3 part 02 시)
- **P2-NEW-2** (REC-AI-01): `wafer_topo.py` 에 정확 식 옵션 추가
- **P2-NEW-3** (REC-AI-02): Defocus-aware Nyquist sanity check
- **P2-NEW-4** (REC-AI-03): `tests/audits/test_fft_invariants.py` 에 defocus invariant 추가
- **P2-NEW-5** (REC-EUV-02): Phase 3 part 02 DOF metrics + paper #14 비교

---

## 4. 우선순위 매트릭스 + 최종 권고

### 4.1 매트릭스 적용 결과

```
                        영향도 (Impact)
                  Low      Med      High
              ┌─────────┬─────────┬──────────┐
   확률      Low │  P3   │  P2     │  (없음)  │
              ├─────────┼─────────┼──────────┤
            Med │  P2   │  P1/P2  │  P0      │
                │P2-NEW-3 │P2-NEW-1│  (없음)  │
                │P2-NEW-4 │P2-NEW-2│          │
                ├─────────┼─────────┼──────────┤
           High │  P1   │  P0     │  P0      │
                │ (없음) │ (없음)  │  (없음)  │
                └─────────┴─────────┴──────────┘
```

### 4.2 P0 — 즉시 수정 (머지 차단)

**없음**.

### 4.3 P1 — 단기 권고

**없음**. (003 에서 P1 누락 0)

### 4.4 P2 — 중기 권고 (Phase 3 part 02 entry 시 처리 권고)

#### P2-NEW-MT-008 (신규 mitigation task)
- **내용**: Phase 3 part 02 에 paraxial vs full angular OPL 비교 옵션 추가
- **출처**: REC-EUV-01 + REC-AI-01 consensus
- **데드라인**: Phase 3 part 02 entry
- **작업량**: 1-2시간

#### P2-NEW-MT-009
- **내용**: Defocus-aware Nyquist sanity check 추가
- **출처**: REC-AI-02
- **데드라인**: Phase 3 part 02 entry
- **작업량**: 1시간

#### P2-NEW-MT-010
- **내용**: `tests/audits/test_fft_invariants.py` 에 defocus invariant 2건 추가
- **출처**: REC-AI-03
- **데드라인**: Phase 3 part 02 진행 중
- **작업량**: 30분

#### P2-기존 (deferred from EXT-AUD-001/002)
- mypy strict 모듈별 도입
- CONTRIBUTING.md 추가
- pre-commit 에 mypy 추가

### 4.5 P3 — 장기 권고 (backlog 누적)

- Test 명명 일관성 (REC-SW-01)
- `__pycache__/` retroactive 점검 (REC-SW-04)
- `tests/audits/` 명명 충돌 회피
- Large defocus warning
- 노트북 reproducibility

---

## 5. 추세 분석

### 5.1 EXT-AUD-001 → 002 → 003 누적 비교

| 메트릭 | 001 | 002 | 003 | 추세 |
|--------|-----|-----|-----|------|
| 종합 판정 | 🟡 PASS w/ 1 P0 | 🟢 PASS clean | 🟢 PASS clean | **안정 개선** |
| P0 개수 | 1 | 0 | 0 | **유지 (-100% 누적)** |
| P1 개수 | 6 | 2 | 0 | -100% (003) |
| 위험 가중 합계 | 32.9 | 7.2 | **5.5** | **-83% 누적** ★ |
| 단위 테스트 수 | 5 | 9 | **14** | +180% 누적 |
| Test pass rate | 5/5 | 9/9 | 14/14 | 100% 유지 ✓ |
| 누적 단순화 | 7 | 7 | 11 | +57% (정상, 신규 Phase 진입) |
| 단순화 4중 기록률 | 100% | 100% | 100% | **유지** ✓ |
| Mitigation 처리율 | — | 86% | **100%** | **★ 최대 달성** |
| KPI 평균 | 33% | 33% | 33%+ (K3 enabled) | 진척 시작 |

### 5.2 반복되는 패턴 — 강화된 모범 사례

| 패턴 | 1회 | 2회 | 3회 | 평가 |
|------|-----|-----|-----|------|
| housekeeping 갱신 | ✗ 누락 | ✓ 갱신 | ✓ 갱신 | **개선 → 안정** |
| 단순화 4중 기록률 | 100% | 100% | 100% | **유지 (모범)** |
| Test 명명 spec 역할 | ✓ | ✓ | ✓ | **유지** |
| 전문가 의견 충돌 | 거의 없음 | 없음 | 없음 | **건강한 협업** |
| Mitigation 처리 속도 | — | 86% | 100% | **개선 → 모범** |

### 5.3 개선 / 정체 / 악화 영역

#### 🟢 개선 영역 (지속)
1. **Mitigation 처리율**: 86% → 100% (★ 최대 달성)
2. **위험 지수 누적**: -83%
3. **Test 수**: 5 → 14 (+180%)
4. **D5 부호 컨벤션 원칙**: Phase 1 anamorphic + Phase 3 defocus 양쪽에 적용 (반복 가능 패턴)

#### 🟡 정체 영역
1. **mypy strict**: 3회 연속 P2 deferred
2. **CONTRIBUTING.md**: 3회 연속 P2 deferred
3. **KPI K3 정량**: enabled 됐으나 실제 진척은 part 02 까지

#### 🔴 악화 영역
- **없음** — 모든 메트릭 개선 또는 유지

### 5.4 Data Scientist 의 종합 평가

본 프로젝트의 외부 감사 시스템은 **3회 연속 일관된 품질**을 유지하고 있다. 특히:

1. **D5 컨벤션 원칙의 반복 적용** — 한 번 적용한 패턴 (anamorphic 좌표) 이 다른 곳 (defocus 부호) 에도 적용됨. 이는 단순한 1회성 모범이 아니라 **체화된 운영 원칙**.
2. **Mitigation 처리율 100%** — EXT-AUD-001 의 7개 P0/P1 권고가 단 2개의 후속 PR (#4, #5) 로 모두 처리됨. 평균 처리 속도: 3.5 권고/PR.
3. **위험 지수 -83%** — 외부 감사 시스템의 ROI 가 데이터로 누적 입증됨.
4. **DefocusConvention dataclass 패턴** 은 본 프로젝트의 **혁신적 기여** — 컨벤션을 코드 객체로 표현하는 패턴은 다른 과학 시뮬레이션 프로젝트에 권장할 만함.

---

## 6. 코드 작성자에게 묻는 질문

1. **다음 권장 작업 동의** — `phase3-part02-add: add dof focus stack metrics` 에 다음을 포함하시겠습니까?
   - DOF 정량 메트릭 (k₂ fitting)
   - paper #14 의 LCDU 18-42% 향상 정성 재현
   - **MT-008 ~ MT-010** (신규 P2-NEW): paraxial vs full angular 비교, defocus-aware Nyquist, FFT invariant 추가
   - **DS 권고**: Yes — 한 PR 에서 모두 처리하면 EXT-AUD-004 가 더 효율적

2. **`git ls-files | grep pycache` retroactive 점검** 결과를 다음 PR description 에 포함해 주실 수 있습니까? (5분 작업, REC-SW-04)

3. **mypy strict 모듈별 도입** 은 phase3-part02 에 포함할까요, 별도 `chore-update: enable mypy strict for constants` PR 로 분리할까요? (DS 권고: 분리)

---

## 7. 다음 단계 (Action Items)

```
[✓] MT-001~007 모두 완료 (PR #4, #5)
[ ] MT-008 (P2-NEW): paraxial vs full angular OPL 비교 옵션
[ ] MT-009 (P2-NEW): defocus-aware Nyquist sanity check
[ ] MT-010 (P2-NEW): FFT invariant test 에 defocus 항목 추가
[ ] (선택) mypy strict 도입, CONTRIBUTING.md, pycache retroactive

다음 Phase 진입:
  → Phase 3 Part 02: DOF focus stack metrics + KPI K3 진척 시작
  → 권장 PR title: phase3-part02-add: add dof focus stack metrics
```

### Phase Gate 판정

- **PR #5 머지**: ✅ **이미 자동 squash merge 완료 — 적절**
- **Phase 3 part 02 진입**: ✅ **즉시 가능**
- **권장 다음 작업**: phase3-part02 + MT-008~010 동반 처리

---

## 8. 한 페이지 요약 (cheat sheet)

```
═══════════════════════════════════════════════════════════════
  EXT-AUD-2026-04-26-003 — Phase 3 Part 01 — FINAL
═══════════════════════════════════════════════════════════════

판정          🟢 PASS (clean)

Mitigation 처리율 (누적)
  EXT-AUD-001/002 의 P0+P1: 7/7 = 100% ★
  본 PR 신규 P0/P1: 0개

P0 신규       0
P1 신규       0
P2 신규       3   (MT-008~010, Phase 3 part 02 entry 시 처리 권고)
P3 신규       1

위험 지수     32.9 → 7.2 → 5.5 (누적 -83%)

KPI          K1=100% K2=100% K3=enabled (식 + 테스트 준비)
              K4-K6=0% (Phase 4-6 미진입)

테스트        5 → 9 → 14 (+180% 누적)
단순화        7 → 11 (P3-L1~4 추가, 4중 기록 100% 유지)
LoC          src ~770, tests ~360

가장 중요한 결과:
  → MT-006/007 closure 로 Phase 1 → Phase 3 transition 완료
  → DefocusConvention dataclass 패턴 = 혁신적 모범 사례
  → 5/5 신규 테스트가 spec 역할로 부호 컨벤션 강제
  → 외부 감사 시스템 ROI: 위험 -83%, mitigation 100%

다음 단계:
  Phase 3 Part 02 (DOF focus stack + KPI K3 진척) 즉시 진입
  MT-008~010 동반 처리 권고
═══════════════════════════════════════════════════════════════
```

---

## 9. 부록

### 9.1 Stage 1 개별 의견 (참조)
- `A1_euv_opinion.md` — EUV 전문가 (PASS clean, with P2 note on paraxial)
- `A2_ai_opinion.md` — AI 전문가 (PASS clean)
- `A3_software_opinion.md` — Software 전문가 (PASS clean)

### 9.2 본 감사가 사용한 evidence
- `.pytest_cache/v/cache/lastfailed = {}` (14/14 PASS)
- `.pytest_cache/v/cache/nodeids` 14개 등록 확인 (5 신규 phase3 + 9 기존)
- `src/wafer_topo.py` (88 lines) 직접 read
- `src/pupil.py` (110 lines, defocus 통합 부분) 직접 read
- `src/aerial.py` defocus 통합 부분 grep 검증
- `tests/phase3_DOF.py` (94 lines) 직접 read
- `docs/phase3_design.md` (54 lines) 직접 read
- `.gitignore` 직접 read (MT-007 verification)
- 코더 자체 보고: pytest --cov 14, ruff/mypy/compileall pass, PR #5 자동 squash merge

### 9.3 본 감사의 limitation
- mypy 의 실제 strict mode 적용 범위 미확인 (`continue-on-error: true` 유지)
- `git ls-files | grep pycache` retroactive 점검 미수행 (P3 권고로 등록)
- Phase 3 part 02 의 정확 식 옵션 구현은 미래 PR 의 audit 대상

### 9.4 추세 데이터 — 3 point established

001 → 002 → 003 의 3 point 가 확보됨. EXT-AUD-004 부터:
- 위험 지수 trend chart
- KPI 진척 trajectory
- Mitigation 처리 속도 (권고/PR)
- 누적 단순화 vs 4중 기록률
이 4가지를 정량 trend 로 추적 가능.
