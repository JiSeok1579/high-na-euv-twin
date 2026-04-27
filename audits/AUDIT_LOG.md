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
| 2026-04-27 | Phase 4 | implementation | Phase 4 Part 04 rigorous-data import + aerial regression hooks | 🟢 PASS | [docs/phase4_M3D_design.md](../docs/phase4_M3D_design.md) | `load_mask3d_lookup_csv`, `lookup_boundary_corrected_mask`, `compare_mask3d_aerial_images`, `lookup_mask3d_aerial_regression`, and a rigorous import CSV template added. 89/89 tests PASS |
| 2026-04-27 | Phase 4 | implementation | Phase 4 Part 03 absorber provenance + lookup-table hooks | 🟢 PASS | [docs/phase4_M3D_design.md](../docs/phase4_M3D_design.md) | `Mask3DLookupEntry`, `Mask3DLookupTable`, `AbsorberScreeningRow`, lookup JSON loading, pitch interpolation, reduced fallback, and candidate screening added. Absorber provenance fields added. 84/84 tests PASS |
| 2026-04-27 | Phase 4 | implementation | Phase 4 Part 02 boundary-corrected Mask 3D field | 🟢 PASS | [docs/phase4_M3D_design.md](../docs/phase4_M3D_design.md) | `boundary_corrected_mask`, `BoundaryCorrectionResult`, and `load_absorber_materials_json` added. Zero-CRA Kirchhoff preservation, asymmetric shadowing, phase map, secondary field, and measured-row JSON loader tests added. 79/79 tests PASS |
| 2026-04-27 | Phase 4 + meta | implementation | MT-015/016 closure + Phase 4 paper #12 six-effect stub | 🟢 PASS | [docs/phase4_M3D_design.md](../docs/phase4_M3D_design.md) | Simulator rebrand, `.github/CLAUDE.md` v2.1 English-first sync, Tier 1 matplotlib 3D notebooks, `src/mask_3d.py`, absorber starter data, and 9 Phase 4 Mask 3D tests. 73/73 tests PASS |
| 2026-04-26 | Phase 5 | external (DS) | EXT-AUD-005 Full Resist Chain (자동 트리거 v2.1) | 🟡 PASS w/ 1 P0 (rebrand) | [00_FINAL_audit.md](external/reports/EXT-AUD-2026-04-26-005_phase5_full_resist_chain/00_FINAL_audit.md) | **본 프로젝트 단일 최대 진척 외부 검증**: 4-level resist + KPI K1 진정 100% + K6 70% + k₂ fitting closed. 64/64 tests PASS. user-directed legacy-name-to-Simulator rebrand + 3D 시각화 Tier 1 권고 instruction sheet 포함. MT-015~018 등록 |
| 2026-04-26 | Phase 5 | implementation | Phase 5 complete calibration + K6 exit | 🟢 PASS | [docs/phase5_resist_models.md](../docs/phase5_resist_models.md) | L1 LWR, L2 SWA, L3 stochastic LWR measured-input calibration hooks 추가. K6 exit 상태 반영. 64/64 tests PASS |
| 2026-04-26 | Phase 5 | implementation | Phase 5 L3 Part 02 MC convergence gate | 🟢 PASS | [docs/phase5_resist_models.md](../docs/phase5_resist_models.md) | `monte_carlo_convergence_gate` 추가. 100/300/1000 trial LWR stability, tight tolerance fail, gate input validation 검증. 61/61 tests PASS |
| 2026-04-26 | Phase 5 | implementation | Phase 5 L3 Part 01 stochastic LWR MVP | 🟢 PASS | [docs/phase5_resist_models.md](../docs/phase5_resist_models.md) | `resist_stochastic.py`, `tests/phase5_stochastic.py` 추가. stochastic chain, seeded MC CD/LWR/LCDU, optical/material/cross budget 검증. 58/58 tests PASS |
| 2026-04-26 | Phase 5 | implementation | Phase 5 L2 Part 02 profile/SWA proxy | 🟢 PASS | [docs/phase5_resist_models.md](../docs/phase5_resist_models.md) | `depth_cd_profile`, `sidewall_angle_proxy` 추가. depth별 CD profile, top-bottom CD taper, vertical/tapered SWA proxy 검증. 52/52 tests PASS |
| 2026-04-26 | Phase 5 | implementation | Phase 5 L2 Part 01 depth-resolved resist | 🟢 PASS | [docs/phase5_resist_models.md](../docs/phase5_resist_models.md) | `resist_depth.py`, `tests/phase5_depth.py` 추가. depth defocus, Beer-Lambert attenuation, top/bottom asymmetry, focus-drilling consistency 검증. 48/48 tests PASS |
| 2026-04-26 | Phase 5 | implementation | Phase 5 L1 Part 02 blur sigma-dose sweep | 🟢 PASS | [docs/phase5_resist_models.md](../docs/phase5_resist_models.md) | `blur_dose_sweep` 추가. CD/EPE/transition width/LWR proxy table, sigma/dose 방향성 회귀, 4b notebook sweep 추가. 42/42 tests PASS |
| 2026-04-26 | Phase 5 | implementation | Phase 5 L1 Part 01 Gaussian blur resist | 🟢 PASS | [docs/phase5_resist_models.md](../docs/phase5_resist_models.md) | `resist_blur.py`, `tests/phase5_blur.py`, `4b_resist_levels.ipynb` 추가. Gaussian blur kernel/edge-spread/end-to-end CD 검증. 38/38 tests PASS |
| 2026-04-26 | Phase 5 | implementation | Phase 5 MVP threshold resist + end-to-end pipeline | 🟢 PASS | [docs/phase5_resist_models.md](../docs/phase5_resist_models.md) | KPI K1 end-to-end MVP 합격. `resist_threshold.py`, `metrics.py`, notebook, 7개 신규 테스트 추가. 32/32 tests PASS |
| 2026-04-26 | Phase 3 | mitigation | MT-012 Phase 3 Part 03 k₂ fitting + focus-drilling MVP | 🟢 PASS | [docs/phase3_DOF_analysis.md](../docs/phase3_DOF_analysis.md) | K3 formula gate 50%→100%. `fit_k2_from_dof_cases`, `fit_k2_from_metrics`, `focus_drilling_average` 추가. 25/25 tests PASS |
| 2026-04-26 | meta | housekeeping | MT-011/013/014 v2.1 sync + 문서 drift 정리 | 🟢 PASS | [REVIEWER_DIRECTIVE.md](../REVIEWER_DIRECTIVE.md) | `.github/CLAUDE.md` v2.1 자동 트리거 sync, 진행계획서 §13 v1.2/v1.3, phase3_design P3-L2 갱신 |
| 2026-04-26 | Phase 3 | external (DS) | EXT-AUD-004 Phase 3 Part 02 (DOF metrics + MT-008~010, 자동 트리거) | 🟡 PASS w/ 1 P0 | [00_FINAL_audit.md](external/reports/EXT-AUD-2026-04-26-004_phase3_part02_dof_metrics/00_FINAL_audit.md) | REVIEWER_DIRECTIVE v2.1 §10.5 자동 트리거 첫 적용. KPI K3 첫 정량 진척 (0%→50%). 메타 sync P0 1건 (CLAUDE.md v2.1) |
| 2026-04-26 | meta | system | REVIEWER_DIRECTIVE v2.1 — 자동 외부감사 트리거 신설 | 🟢 PASS | [REVIEWER_DIRECTIVE.md](../REVIEWER_DIRECTIVE.md) | §10.5 신설: 코드 수정 + 다음지시 요청 시 4-md 폴더 자동 작성 |
| 2026-04-26 | Phase 3 | mitigation | MT-008~010 DOF metric 후속 조치 | 🟢 PASS | [docs/phase3_DOF_analysis.md](../docs/phase3_DOF_analysis.md) | full angular defocus option, defocus-aware sampling guard, focus-stack DOF metric, defocus invariants 추가. 20/20 tests PASS |
| 2026-04-26 | Phase 3 | external (DS) | EXT-AUD-003 Phase 3 Part 01 (PR #5 9ee22bb) | 🟢 PASS (clean) | [00_FINAL_audit.md](external/reports/EXT-AUD-2026-04-26-003_phase3_part01_defocus_sign/00_FINAL_audit.md) | MT-006/007 closure 검증. 위험 지수 7.2→5.5 (누적 -83%). 14/14 tests PASS. DefocusConvention dataclass 모범 사례. P2-NEW MT-008~010 등록 |
| 2026-04-26 | Phase 3 | mitigation | MT-006 defocus 부호 컨벤션 + MT-007 gitignore | 🟢 PASS | [docs/phase3_design.md](../docs/phase3_design.md) | `src/wafer_topo.py`, `PupilSpec.defocus_m`, `tests/phase3_DOF.py` 추가. Phase 3 Part 01 진입 |
| 2026-04-26 | Phase 1 | external (DS) | EXT-AUD-002 Post-Audit Fixes (PR #4 ee30c04) | 🟢 PASS (clean) | [00_FINAL_audit.md](external/reports/EXT-AUD-2026-04-26-002_phase1_post_audit_fixes/00_FINAL_audit.md) | MT-001~005 100%/83% 처리. 위험 지수 32.9→7.2 (-78%). 9/9 tests PASS. 자동 squash merge 검증 |
| 2026-04-26 | meta | mitigation | EXT-AUD-001 P0/P1 후속 조치 | 🟢 PASS | [REVIEWER_DIRECTIVE.md](../REVIEWER_DIRECTIVE.md) | MT-001~005 처리: CLAUDE.md v2 sync, 진행계획서 §5.1 갱신, Zernike 공용화, FFT invariant test, pre-commit 도입 |
| 2026-04-26 | meta | external (DS) | EXT-AUD-001 Phase 1 첫 외부 감사 (4-md) | 🟡 PASS w/ 1 P0 | [00_FINAL_audit.md](external/reports/EXT-AUD-2026-04-26-001_phase1_initial_review/00_FINAL_audit.md) | REVIEWER_DIRECTIVE v2.0 발효 후 첫 시연. P0 1건: .github/CLAUDE.md sync 필요 |
| 2026-04-26 | Phase 1 | sim (간접) | aerial image MVP 완료 | 🟢 PASS | [docs/phase1_design.md](../docs/phase1_design.md) | 5/5 unit tests PASS, KPI K1·K2 합격, 7 단순화 4중 기록 100% |
| 2026-04-26 | meta | system | REVIEWER_DIRECTIVE v2.0 + audits/external/ 신설 | 🟢 PASS | [REVIEWER_DIRECTIVE.md](../REVIEWER_DIRECTIVE.md) | 3 전문가 + Data Scientist 통합자 2-stage 구조 |
| 2026-04-25 | meta | system | 감사 시스템 초기 구축 | 🟢 PASS | (본 폴더 자체) | 4개 INSTRUCTIONS + 템플릿 작성 완료 |

---

## 통계 (자동 갱신 대상)

```
총 감사 수:           26
PASS:                23
PASS WITH P0:        3 (EXT-AUD-001/004/005)
CAUTION:             0
MAJOR RISK:          0
PHYSICAL VIOLATION:  0
UNVERIFIED:          0

본 PR (EXT-AUD-005) 단일 최대 진척:
  Phase 5 4-level 완성 + KPI K1 진정 100% + K6 70% + k₂ fitting (MT-012)
  paper #1 smile + paper #21 chain 정확 재현
  tests 20→64 (+220% 단일 PR), KPI 평균 +15%
  사용자 명시 지시 (rebrand + 3D) instruction sheet 제공

추세 (5-point established: EXT-AUD-001 → 002 → 003 → 004 → 005):
  위험 지수 가중 합계:  32.9 → 7.2 → 5.5 → 20.2 (메타 sync 시 spike 패턴)
  P0 개수:             1 → 0 → 0 → 1 → 0 (MT-011 처리)
  P1 개수:             6 → 2 → 0 → 3 → 1 → 0 (MT-012 처리)
  Mitigation 처리율 (누적): — → 86% → 100% → 100% → 93% → 100% (14/14)
  단위 테스트 수:       5 → 9 → 14 → 20 → 25 → 32 → 38 → 42 → 48 → 52 → 58 → 61 → 64 → 73 → 79 → 84 → 89 (+1680% 누적) ★
  Test pass rate:      5/5 → 9/9 → 14/14 → 20/20 → 25/25 → 32/32 → 38/38 → 42/42 → 48/48 → 52/52 → 58/58 → 61/61 → 64/64 → 73/73 → 79/79 → 84/84 → 89/89 (100% 유지)
  KPI K3 (DOF 정량):   0% → 0% → enabled → 50% → 100% ★
  KPI K4 (M3D 6):      0% → reduced six-effect + field boundary evidence ★
  KPI K1 (end-to-end): optical only → full MVP ★
  KPI 평균 진척률:      33% → 33% → 33%+ → 42% → 50% → 58% → 61% → 63% → 65% → 67% → 70% → 72% → 75%
  누적 단순화:          7 → 7 → 11 → 14 (P4-L6 신규)
  단순화 4중 기록률:    100% → 100% → 100% → 85% (drift 시작 — P3-L5/L6 명시 필요)

식별된 시스템 패턴:
  "Meta-sync drift" — REVIEWER_DIRECTIVE 변경 시 .github/CLAUDE.md sync 가 항상 P0
  → 권고: 메타 변경 PR 안에 CLAUDE.md 동시 갱신 자동화 (P3 backlog)
```

---

## 미해결 mitigation task

> P0/P1/CAUTION 판정에 따라 생성된 task 중 미완료 항목.

| ID | 생성일 | 등급 | 내용 | 데드라인 | 출처 |
|----|--------|------|------|----------|------|
| MT-019 | 2026-04-26 | P2 | `_validate_*` helper 통합 → `src/utils.py` 또는 `src/_validation.py` (DRY) | Phase 4 entry 전 | EXT-AUD-005 §4.5 (REC-AI-01 + REC-SW-04 consensus) |
| MT-020 | 2026-04-26 | P2 | `resist_stochastic.py` 539줄 모듈 분할 검토 (chain/budget/calibration) | 다음 정밀화 PR | EXT-AUD-005 §4.5 (REC-SW-05) |
| MT-021 | 2026-04-26 | P2 | docs/phase5 에 threshold 0.25 (acid) vs 0.3 (intensity) 의미 차이 명시. depth absorption paper #20 정량 비교 | 다음 PR | EXT-AUD-005 §4.5 (REC-EUV-01/02) |

---

## 완료된 mitigation task

| ID | 완료일 | 등급 | 내용 | 반영 파일 |
|----|--------|------|------|-----------|
| MT-001 | 2026-04-26 | **P0** | `.github/CLAUDE.md` 를 REVIEWER_DIRECTIVE.md v2.0 으로 sync | `.github/CLAUDE.md` |
| MT-002 | 2026-04-26 | P1 | `진행계획서.md §5.1` 상태표를 ✅로 갱신 | `진행계획서.md` |
| MT-003 | 2026-04-26 | P1 | `_wavefront` → `src/optics/zernike.py` 추출 | `src/optics/zernike.py`, `src/pupil.py`, `src/aerial.py` |
| MT-004 | 2026-04-26 | P1 | FFT invariant tests 신설 | `tests/audits/test_fft_invariants.py` |
| MT-005 | 2026-04-26 | P1 | pre-commit hook 도입 | `.pre-commit-config.yaml`, `requirements-dev.txt` |
| MT-006 | 2026-04-26 | P1 | Phase 3 defocus 부호 컨벤션 fix + 테스트 | `docs/phase3_design.md`, `src/wafer_topo.py`, `tests/phase3_DOF.py` |
| MT-007 | 2026-04-26 | P1 | Python cache ignore pattern 명시 확인 | `.gitignore` |
| MT-008 | 2026-04-26 | P2 | paraxial vs full angular OPL 비교 옵션 | `src/wafer_topo.py`, `tests/phase3_DOF.py` |
| MT-009 | 2026-04-26 | P2 | defocus-aware pupil sampling sanity check | `src/wafer_topo.py`, `src/pupil.py`, `src/aerial.py` |
| MT-010 | 2026-04-26 | P2 | defocus invariant tests 추가 | `tests/audits/test_fft_invariants.py` |
| **MT-011** | 2026-04-26 | P0 | `.github/CLAUDE.md` v2.1 sync — **MT-015 로 통합** | (재할당) |
| **MT-012** | 2026-04-26 | P1 | k₂ fitting (3 신규 tests in Phase 5 PR) | `tests/phase3_DOF.py::test_k2_fit_*` (3 tests) |
| MT-011 | 2026-04-26 | **P0** | `.github/CLAUDE.md` 를 REVIEWER_DIRECTIVE v2.1 자동 트리거 절차로 sync | `.github/CLAUDE.md` |
| MT-012 | 2026-04-26 | P1 | k₂ fitting 보고 (NA/pitch sweep + DOF = k₂·λ/NA² 정량 검증, KPI K3 100% 합격선) | `src/dof.py`, `tests/phase3_DOF.py`, `docs/phase3_DOF_analysis.md` |
| MT-013 | 2026-04-26 | P1 | `진행계획서.md §13` v1.2 + v1.3 변경 이력 추가 | `진행계획서.md` |
| MT-014 | 2026-04-26 | P1 | `docs/phase3_design.md §4` P3-L2 문구 갱신 | `docs/phase3_design.md` |
| **MT-015** | 2026-04-27 | **P0** | Legacy project-name rebrand to High-NA EUV Lithography Simulator + `.github/CLAUDE.md` v2.1 English-first sync | `.github/CLAUDE.md`, `README.md`, docs, audit files, source docstrings |
| **MT-016** | 2026-04-27 | P1 | Tier 1 matplotlib 3D notebooks for focus stack, pupil wavefront, resist depth dose, and Mask 3D effect bars | `notebooks/3d_focus_stack.ipynb`, `notebooks/3d_pupil_wavefront.ipynb`, `notebooks/3d_resist_depth.ipynb`, `notebooks/3_M3D_effects.ipynb` |

---

## 차단 이력 (Block History)

> MAJOR RISK 또는 PHYSICAL VIOLATION으로 차단된 PR / Phase Gate 기록.

| 날짜 | 대상 | 차단 사유 | 해결 방법 | 해결 날짜 |
|------|------|-----------|-----------|-----------|
| (없음) | | | | |
