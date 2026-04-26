# 외부 감사 최종 보고서 — Claude (Data Scientist 통합)

## 0. 메타

```
감사 ID:        EXT-AUD-2026-04-26-001
감사 단계:      Stage 2 / Final Synthesis
작성자:         Claude (Data Scientist 시각)
감사 날짜:      2026-04-26
대상:           Phase 1 Initial Review
                - src/ (constants, pupil, mask, aerial)
                - tests/phase1_aerial_image.py (5 tests)
                - docs/phase1_design.md
                - notebooks/0_first_aerial_image.ipynb
받은 보고서:    코드 작성자 self-audit 미작성
                .pytest_cache 로그 (5/5 PASS) 직접 확인
Stage 1 입력:   A1_euv_opinion.md (PASS)
                A2_ai_opinion.md (PASS with rigor)
                A3_software_opinion.md (PASS with 1 P0)
참조 문서:      REVIEWER_DIRECTIVE.md v2.0
                진행계획서.md §4.1, §9.2
                PROJECT_OVERVIEW.md §0.3, §6
```

---

## 1. 종합 판정

> **🟡 PASS WITH 1 P0** — Phase 1 코드 자체는 모든 시각에서 PASS. 단 `.github/CLAUDE.md` 가 본 지침 v2.0 과 mismatch 라는 1건의 P0 issue가 다음 PR 전 차단 조건.

| 시각 | 판정 | 핵심 |
|------|------|------|
| EUV 전문가 | 🟢 PASS | 물리·좌표·단순화 모두 정직 |
| AI 전문가 | 🟢 PASS (with rigor) | Nyquist guard + noise floor + 디버깅 trace 정직 |
| Software 전문가 | 🟡 PASS with 1 P0 | CLAUDE.md sync 필요 |
| **Data Scientist 통합** | **🟡 PASS WITH 1 P0** | 다음 PR 전 P0 1건 처리 → 그 후 자유 진행 |

---

## 2. 3 전문가 의견 통합

### 2.1 Consensus (3/3 일치)

| 항목 | EUV | AI | Software |
|------|-----|----|----|
| 코드 품질 우수 | F-EUV-* 전반 | F-AI-06 | F-SW-01 ~ 04 |
| 테스트 충분 (Phase 1 범위) | F-EUV-07 | (전제) | F-SW-08 ~ 10 |
| 단순화 4중 기록 충실 | F-EUV-05 | F-AI-07 | F-SW-14 |
| Phase 1 KPI K1, K2 합격 | F-EUV-08 | (확인) | (확인) |
| 디버깅 trace 정직 | (인정) | F-AI-05, F-AI-07 | F-SW-15 |

**통합 결론**: Phase 1 구현 자체는 3 시각 모두 통과. **이의 없음**.

### 2.2 Conflict (충돌 지점) + Data Scientist 중재

| 항목 | EUV | AI | Software | DS 중재 결정 |
|------|-----|----|----|-------------|
| `aerial.py` lazy import | 미언급 (영역 외) | R-AI-01 / REC-AI-01 P1 | R-SW-04 / REC-SW-04 P1 | **P1 채택 (consensus)** |
| mypy continue-on-error | 미언급 | R-AI-06 / REC-AI-03 P2 | R-SW-07 / REC-SW-07 P2 | **P2 채택 (consensus)** |
| 노트북 reproducibility | 미언급 | F-AI-08 (현재 OK) | R-SW-08 / REC-SW-08 P3 | **P3 채택 (Phase 1 영향 없음)** |
| `_wavefront` 모듈 분리 | 미언급 | REC-AI-01: optics/zernike.py | REC-SW-04: 같음 | **REC-AI-01 채택 (구체적 위치 명시)** |

**실질적 충돌은 없음.** 모두 우선순위 일치.

### 2.3 Gap (3 전문가 모두 누락한 영역, DS 보강)

| Gap | DS 평가 | 권고 |
|-----|---------|------|
| `.github/CLAUDE.md` v1 vs REVIEWER_DIRECTIVE v2 mismatch | Software 가 R-SW-01 로 캐치 | **P0 — 다른 두 전문가는 이 leak 미발견. 영역 한계 인지** |
| 데이터 입력 측면 | Phase 1은 합성 패턴만 사용 → N/A 적정 | 변화 없음 |
| Ablation study 부재 | Phase 1은 ablation 의미 없음 (단일 baseline) | Phase 4 entry 시 추가 |
| 추세 분석 baseline | 본 감사가 첫 외부 감사 → baseline 자체 | 본 보고서가 future trend 의 reference |

---

## 3. 메트릭 정량화

### 3.1 코드 변경 메트릭

| 메트릭 | 값 |
|--------|-----|
| LoC (src/) | 556 (constants 49 + pupil 147 + mask 129 + aerial 225 + __init__ 6) |
| LoC (tests/) | 206 (phase1_aerial_image 198 + conftest 8 + __init__ 0) |
| LoC (docs/) | 164 (phase1_design.md) |
| **LoC 총합** | **926 lines** |
| Files added | 4 src + 3 tests + 1 docs + 1 notebook = 9 files |
| Modules touched | constants, pupil, mask, aerial (Phase 1 4모듈) |
| Test count | 5 (4 verification + 1 bonus) |
| Test pass rate | **5/5 = 100%** (.pytest_cache lastfailed = `{}`) |

### 3.2 단순화 가정 추적

| 단순화 | 코드 주석 | docs/phase1_design.md | PROJECT_OVERVIEW | Limitation 섹션 |
|--------|-----------|----------------------|------------------|----------------|
| S1 Single coherent | ✅ | ✅ §5 | ✅ §4.2 | ✅ §10 |
| S2 Kirchhoff thin-mask | ✅ | ✅ §5 | ✅ §4.2 | ✅ §10 |
| S3 Monochromatic | ✅ | ✅ §5 | ✅ §4.2 | ✅ §10 |
| S4 Constant R | ✅ | ✅ §5 | ✅ §4.2 | ✅ §10 |
| S5 Scalar (no polarization) | ✅ | ✅ §5 | (구두 인용) | ✅ §10 |
| S6 Anamorphic 픽셀만 | ✅ | ✅ §5 | (구두 인용) | ✅ §10 |
| S7 Defocus = 0 | ✅ | ✅ §5 | ✅ §4.2 (Phase 3 deferred) | ✅ §10 |

- **신규 도입 단순화: 7개 (S1-S7)**
- **누적 단순화: 7개**
- **4중 기록 완료: 7/7 (100%)** ← 모범 사례

### 3.3 KPI 진척도

| KPI | 목표 | 이전 | 현재 | 진척률 | 비고 |
|-----|------|------|------|--------|------|
| K1 (end-to-end) | mask → printed pattern | 0% | **100%** (광학 파트) | 100% | aerial.py 통과 |
| K2 (회절 정성) | paper #11 정성 패턴 | 0% | **100%** | 100% | pitch sweep cutoff 정확 |
| K3 (DOF 정량) | k₂·λ/NA² 일치 ±30% | 0% | 0% | 0% | Phase 3 시작 시 |
| K4 (M3D 6 효과) | paper #12 6/6 통과 | 0% | 0% | 0% | Phase 4 시작 시 |
| K5 (SMO 수렴) | 1 layout 수렴 | 0% | 0% | 0% | Phase 6 시작 시 |
| K6 (Stochastic LWR) | paper #1 정성 재현 | 0% | 0% | 0% | Phase 5 L3 시작 시 |
| **평균** | | **0%** | **33%** | | 6개 중 2개 100% |

### 3.4 위험 지수

| 등급 | 개수 | 가중치 | 가중 합계 |
|------|------|--------|-----------|
| **P0 — 즉시 수정** | 1 | × 10 | 10 |
| **P1 — 단기 권고** | 6 | × 3 | 18 |
| **P2 — 중기 권고** | 4 | × 1 | 4 |
| **P3 — 장기 권고** | 3 | × 0.3 | 0.9 |
| **합계** | 14 | | **32.9** |

**해석**: P0 1건이 전체 risk index 의 30% 차지. 그 1건만 처리하면 risk index 22.9로 감소 (-30%).

---

## 4. 우선순위 매트릭스 + 최종 권고

### 4.1 매트릭스 적용 결과

```
                        영향도 (Impact)
                  Low      Med      High
              ┌─────────┬─────────┬──────────┐
   확률      Low │  P3   │  P2     │  P1      │
   (Likelihood)   │  REC-04│ REC-AI-05│REC-EUV-02│
              ├─────────┼─────────┼──────────┤
            Med │  P2   │  P1     │  P0      │
                │REC-AI-03│REC-AI-01 │          │
                │REC-SW-07│REC-SW-04 │          │
                ├─────────┼─────────┼──────────┤
           High │  P1   │  P0     │  P0      │
                │REC-SW-02│         │REC-SW-01│
                │REC-SW-03│         │          │
                │REC-SW-05│         │          │
                └─────────┴─────────┴──────────┘
```

### 4.2 P0 — 즉시 수정 (머지 차단)

#### P0-01 — `.github/CLAUDE.md` 를 REVIEWER_DIRECTIVE v2.0 으로 sync
- **출처**: REC-SW-01
- **확률 × 영향**: High × High
- **이유**: 다음 PR 부터 GitHub Action이 stale 지침으로 작동하면 4-md 외부 감사 보고서 생성 자체가 무시됨. 본 외부 감사 시스템 (audits/external/) 의 raison d'être 가 손상.
- **구체 액션**:
  1. `.github/CLAUDE.md` 의 "PR 검토 절차" 섹션을 REVIEWER_DIRECTIVE v2.0 §3, §6 인용으로 갱신
  2. "STAGE 1 — 3 전문가 개별 의견 .md 작성 (audits/external/reports/<EXT-AUD-id>/A{1,2,3}_*.md)"
  3. "STAGE 2 — Data Scientist 통합 보고서 00_FINAL_audit.md 작성"
  4. "PR 코멘트로 00_FINAL 의 cheat sheet 첨부"
- **예상 작업량**: 30분
- **기대 효과**: GitHub Action이 v2.0 지침대로 작동, 외부 감사 layer 가 실제 PR 흐름에 통합

### 4.3 P1 — 단기 권고 (다음 PR / Phase Gate 전)

#### P1-01 — `audits/AUDIT_LOG.md` 에 2 entry 추가
- 출처: REC-SW-03
- 내용: "2026-04-26 | Phase 1 | sim | aerial MVP 완료 | PASS | docs/phase1_design.md"
       + "2026-04-26 | meta | external | EXT-AUD-001 4-md | PASS w/ 1 P0 | audits/external/reports/EXT-AUD-2026-04-26-001_phase1_initial_review/00_FINAL_audit.md"
- 예상 작업량: 5분

#### P1-02 — `진행계획서.md §5.1` 상태표 갱신
- 출처: REC-SW-02
- Phase 1 항목 (constants, pupil, mask, aerial, tests, notebook, docs) 모두 ✅
- 예상 작업량: 10분

#### P1-03 — `_wavefront` 를 `src/optics/zernike.py` 로 추출
- 출처: REC-AI-01 + REC-SW-04 (consensus)
- 예상 작업량: 1시간
- 효과: Phase 4 mask_3d 와 zernike 공유, 순환 참조 위험 제거

#### P1-04 — `tests/audits/test_fft_invariants.py` 신설
- 출처: REC-AI-02
- Parseval, fftshift round-trip, NA scaling, grid refinement
- 예상 작업량: 2시간
- 효과: 향후 모든 PR이 자동 수치 invariant 통과 강제

#### P1-05 — `.pre-commit-config.yaml` 도입
- 출처: REC-SW-05
- ruff + mypy basic + check-yaml + EOF 등
- 예상 작업량: 30분

#### P1-06 — Phase 3 entry 전 defocus 부호 컨벤션 fix + 테스트
- 출처: REC-EUV-02
- 예상 작업량: 1시간
- 효과: Phase 3 코드 전체에 영향. 한 번 정하면 변경 비용 매우 큼 (D5 원칙)

### 4.4 P2 — 중기 권고 (다음 다음 Phase)

- **P2-01** REC-AI-03 / REC-SW-07: mypy strict 점진적 (1-2주)
- **P2-02** REC-EUV-01: Phase 4 진입 전 paper #12 6 효과 test stub (30분)
- **P2-03** REC-AI-04: Phase 5 진입 전 RANDOM_SEED fixture (30분)
- **P2-04** REC-SW-06: CONTRIBUTING.md + CHANGELOG.md (1시간)

### 4.5 P3 — 장기 권고 (프로젝트 전반)

- **P3-01** REC-AI-05: 절대 intensity scale 옵션 (Phase 5 dose 진입 시)
- **P3-02** REC-EUV-03: absorber n,k DB 사전 수집 (Phase 4 시작 직전)
- **P3-03** REC-SW-08: 노트북 reproducibility metadata

---

## 5. 추세 분석

### 5.1 이전 외부 감사와의 비교

**해당 없음** — 본 보고서가 **첫 외부 감사**. 다음 부터는 아래 비교 가능:

| 메트릭 | EXT-AUD-001 (현재) | EXT-AUD-002 (다음) | 추세 |
|--------|--------------------|--------------------|------|
| 종합 판정 | PASS w/ 1 P0 | TBD | TBD |
| P0 개수 | 1 | TBD | |
| 위험 가중 합계 | 32.9 | TBD | |
| KPI 평균 진척률 | 33% | TBD | |
| 누적 단순화 | 7 | TBD | |
| 단순화 4중 기록률 | 100% | TBD | |
| 단위 테스트 수 | 5 | TBD | |

### 5.2 반복되는 패턴 (현재 1회뿐, 후속 추적 시작점)

다음 항목은 future audit 에서 monitor:
- AUDIT_LOG / 진행계획서 stale 의 반복 발생 여부
- `.github/CLAUDE.md` 가 지침 변경 시 자동 sync 되는지
- 단순화 4중 기록률 100% 유지 여부
- mypy continue-on-error 가 실제로 strict 로 전환되는지

### 5.3 개선 / 정체 / 악화 영역

**현재 baseline 설정만**. 후속 감사에서 평가.

---

## 6. 코드 작성자에게 묻는 질문

1. **`.github/CLAUDE.md` v2.0 sync** 를 본 PR 안에 포함하시겠습니까, 별도 PR 로 분리하시겠습니까? (권장: 별도 P0 hotfix PR)

2. **다음 진행 방향**:
   - (A) Phase 3 (Wafer topography & DOF) 진입
   - (B) Phase 5 MVP (threshold resist) 진입 → end-to-end pipeline 빨리 닫기
   - (C) Phase 1 정밀화 (P1 권고들 처리 후 다음 Phase)
   - (D) GitHub 첫 push + smoke test PR

3. **mypy strict 로 전환 일정** 을 명시할까요? (현재 continue-on-error 무기한)

4. **paper #13 매핑 확인** (resist SWA — 정확한 SPIE 13686 paper 인지 확인 요청, 직전 점검에서 미해결)

---

## 7. 다음 단계 (Action Items)

```
[ ] P0-01: .github/CLAUDE.md v2.0 sync                    ★ 차단 항목
[ ] P1-01: AUDIT_LOG.md 갱신
[ ] P1-02: 진행계획서.md §5.1 상태표 갱신
[ ] P1-03: _wavefront → src/optics/zernike.py 추출
[ ] P1-04: tests/audits/test_fft_invariants.py 신설
[ ] P1-05: .pre-commit-config.yaml 도입
[ ] P1-06: Phase 3 entry 전 defocus 부호 컨벤션 fix
[ ] (선택) P2/P3 항목들은 backlog로
```

### Phase Gate 판정

- **본 PR 머지 가능 여부**: **P0-01 처리 후 가능**
- **Phase 1 → 다음 Phase 진입 가능 여부**: ✅ **가능** (Phase 1 자체는 통과)
- **권장 다음 Phase**: Phase 3 (Wafer topography) 또는 Phase 5 MVP (threshold resist) — 진행계획서 §2.2 Phase 진행 모델 따라 둘 다 가능

---

## 8. 한 페이지 요약 (cheat sheet)

```
═══════════════════════════════════════════════════════════════
  EXT-AUD-2026-04-26-001 — Phase 1 Initial Review — FINAL
═══════════════════════════════════════════════════════════════

판정          🟡 PASS WITH 1 P0

P0 수         1     (CLAUDE.md ↔ REVIEWER_DIRECTIVE v2.0 sync)
P1 수         6     (housekeeping + lazy import + pre-commit + ...)
P2 수         4     (mypy strict, M3D test stub, ...)
P3 수         3     (intensity scale, absorber DB, notebook meta)

KPI 진척률    K1=100% K2=100% K3=0% K4=0% K5=0% K6=0% (평균 33%)

단순화        7개 신규 (S1-S7), 4중 기록률 100% ✓
LoC          926 lines (src 556 + tests 206 + docs 164)
테스트        5/5 PASS

가장 중요한 권고 1개:
  → .github/CLAUDE.md 를 REVIEWER_DIRECTIVE.md v2.0 으로 sync
    (30분 작업, 다음 PR 부터 외부 감사 자동화 작동)

다음 단계:
  P0-01 처리 → Phase 3 또는 Phase 5 MVP 자유 진입 가능
═══════════════════════════════════════════════════════════════
```

---

## 9. 부록

### 9.1 Stage 1 개별 의견 (참조)
- `A1_euv_opinion.md` — EUV 전문가 (PASS)
- `A2_ai_opinion.md` — AI 전문가 (PASS with rigor)
- `A3_software_opinion.md` — Software 전문가 (PASS w/ 1 P0)

### 9.2 코드 작성자 self-audit
- **상태**: 미작성
- **참고**: 본 외부 감사가 self-audit 의 부재를 일부 보강했으나, 다음 PR부터는 4-역할 self-audit 보고서가 `audits/01-04/reports/` 에 함께 제출되어야 함

### 9.3 본 감사가 사용한 evidence
- `.pytest_cache/v/cache/lastfailed` 직접 확인 (5/5 PASS)
- `.pytest_cache/v/cache/nodeids` 5개 테스트 등록 확인
- `src/`, `tests/`, `docs/`, `.github/` 모든 파일 직접 read
- REVIEWER_DIRECTIVE.md v2.0, 진행계획서 §4.1, §9.2 참조

### 9.4 본 감사의 limitation
- 코드 작성자 self-audit 보고서 없는 상태에서 진행 → 작성자 의도 추론에 일부 의존
- mypy / ruff 실제 실행 결과 미확인 (sandbox에 도구 미설치)
- 노트북은 cell 구조만 검토, 실행 결과 시각적 평가 못함
- 위 limitation 은 EXT-AUD-002 부터 self-audit 동반 제출로 해소 권고
