# High-NA EUV 참고 논문 — 마스터 인덱스

> 0.55 NA EUV Lithography Simulator 프로젝트의 21편 reference paper 정리
> 폴더: `/논문/papers/`

---

## 0. PDF 다운로드 안내

이 환경에서는 외부 도메인 네트워크가 차단되어 PDF 자동 다운로드가 불가능합니다.
각 논문 페이지에서 직접 다운로드하셔야 합니다. **Open Access** 논문(★)은 무료로 받을 수 있고, **Paywalled** 논문은 SPIE Digital Library 구독 또는 기관 액세스가 필요합니다.

---

## 1. 21편 전체 리스트

| #  | 단축 제목 | 연도 | Venue | Priority | OA여부 | .md 파일 |
|----|-----------|------|-------|----------|--------|----------|
| 01 | Material vs optical stochastic LWR decomposition | 2025 | Sci. Reports | A | ★ OA | [01_stochastic_effects_LWR.md](01_stochastic_effects_LWR.md) |
| 02 | SHARP actinic mask microscope | 2013 | SPIE 8880 | B | preprint | [02_SHARP_actinic_microscope.md](02_SHARP_actinic_microscope.md) |
| 03 | In-Line (coaxial) Projector for EUV | 2025 | arXiv | B | ★ OA | [03_inline_projector_OIST.md](03_inline_projector_OIST.md) |
| 04 | PSCAR / CAR fundamentals | 2017 | EUVL Workshop | A | ★ free | [04_PSCAR_CAR_fundamentals.md](04_PSCAR_CAR_fundamentals.md) |
| 05 | 0.55 NA EUV: Imaging & Overlay (van Schoot) | 2024 | EUVL Workshop | A | ★ free | [05_055NA_imaging_overlay.md](05_055NA_imaging_overlay.md) |
| 06 | Contrast / dose for High-NA DRAM (PMWO) | 2025 | SPIE 13979 | A | paywall | [06_contrast_dose_DRAM.md](06_contrast_dose_DRAM.md) |
| 07 | Novel high-k mask, M3D & focus | 2023 | EUVL Workshop | A | ★ free | [07_high_k_mask_M3D.md](07_high_k_mask_M3D.md) |
| 08 | EUV spectrum of high-power LPP | 2025 | SPIE 13686 | B | paywall | [08_LPP_source_spectrum.md](08_LPP_source_spectrum.md) |
| 09 | Fast SMO for High-NA EUV (gradient + CS) | 2024 | OEA | A | ★ OA | [09_fast_SMO_high_NA.md](09_fast_SMO_high_NA.md) |
| 10 | PMWO: LWR + overlay | 2025 | SPIE 13686 | A | paywall | [10_PMWO_LWR_overlay.md](10_PMWO_LWR_overlay.md) |
| 11 | Moore's Law: High-NA First Imaging | 2024 | EUVL Workshop + SPIE 12953 | A | ★ free | [11_Moore_Law_first_imaging.md](11_Moore_Law_first_imaging.md) |
| 12 | M3D Characterization & Mitigation (Erdmann) | 2017 | Adv. Opt. Tech. | A | partial | [12_M3D_characterization_mitigation.md](12_M3D_characterization_mitigation.md) |
| 13 | Resist SWA / SMO for resist profile | 2025 | SPIE 13686 | B | paywall | [13_resist_SWA_measurement.md](13_resist_SWA_measurement.md) |
| 14 | High-NA DOF challenge & LCDU | 2025 | SPIE 13686 | A | paywall | [14_high_NA_DOF_LCDU.md](14_high_NA_DOF_LCDU.md) |
| 15 | Central obscuration PSF/MTF | ~2018 | Beck technote | B | ★ free | [15_central_obscuration_optics.md](15_central_obscuration_optics.md) |
| 16 | Deep RL illumination relay (anamorphic) | 2025 | Optics Express | A | ★ OA likely | [16_deep_RL_relay_facets.md](16_deep_RL_relay_facets.md) |
| 17 | Best focus shift via optical constant screening | 2025 | SPIE 13686 | A | paywall | [17_best_focus_optical_constant.md](17_best_focus_optical_constant.md) |
| 18 | Tin plasma physics review (Versolato) | 2019 | PSST topical review | A | ★ OA | [18_tin_plasma_physics_review.md](18_tin_plasma_physics_review.md) |
| 19 | Anamorphic High-NA EUV optics (Migura, Zeiss) | 2015 | SPIE 9661 | A | paywall | [19_anamorphic_high_NA_optics.md](19_anamorphic_high_NA_optics.md) |
| 20 | EUV photon absorption distribution at 0.55 NA | 2025 | SPIE 13686 | A | paywall | [20_photon_absorption_distribution.md](20_photon_absorption_distribution.md) |
| 21 | Statistics of EUV nanopatterns (Fukuda) | 2025 | J. Appl. Phys. | A | paywall | [21_statistics_EUV_nanopatterns.md](21_statistics_EUV_nanopatterns.md) |

★ = Open Access / Free (즉시 다운로드 가능)

---

## 2. 분야별 분류

### 2.1 High-NA Overview (시스템/광학 아키텍처)
- **#19** Anamorphic high-NA EUV optics (2015) — 출발점
- **#5** 0.55 NA Imaging & Overlay (2024) — 산업 baseline
- **#11** Moore's Law: First Imaging (2024) — 최초 결과
- **#14** DOF challenge & LCDU (2025)
- **#3** In-Line Projector (2025) — 학계 alternative

### 2.2 Mask 3D (M3D)
- **#12** M3D Characterization & Mitigation (Erdmann 2017) — 가장 종합적 review
- **#7** Novel high-k mask (2023)
- **#17** Best focus shift via optical constant screening (2025)
- (보조) **#2** SHARP actinic microscope — M3D 검증 데이터 출처

### 2.3 SMO / OPC / ILT / PMWO
- **#9** Fast SMO with mask 3D (2024) — 학계 가이드 ★OA
- **#10** PMWO: LWR + overlay (2025) — 산업 PMWO
- **#6** Contrast / dose DRAM (2025) — DRAM PMWO
- **#16** Deep RL illumination relay (2025) — RL 적용 사례

### 2.4 Resist / Stochastic
- **#21** Statistics of EUV nanopatterns (Fukuda 2025) — full chain stochastic
- **#1** Material vs optical stochastic LWR (2025) ★OA
- **#20** EUV photon absorption distribution (2025)
- **#4** PSCAR / CAR fundamentals (2017) ★free
- **#13** Resist SWA / SMO for resist profile (2025)

### 2.5 Source / LPP
- **#18** Tin plasma physics review (Versolato 2019) ★OA
- **#8** LPP spectrum (2025)

### 2.6 Fourier Optics 보조
- **#15** Central obscuration PSF/MTF technote ★free

---

## 3. 우선순위별 분류

### Priority A (반드시 — 핵심 14편)
1, 4, 5, 6, 7, 9, 10, 11, 12, 14, 16, 17, 18, 19, 20, 21

### Priority B (보조 — 7편)
2, 3, 8, 13, 15

> 참고: 위 분류는 인수인계 지시서의 Priority A/B 정의에 따라 임시 부여한 것. 실제 사용 시 프로젝트 진행 단계에 맞춰 조정 가능.

---

## 4. Phase별 추천 매핑

본 프로젝트의 6 Phase 로드맵에 따라 가장 먼저 보아야 할 논문:

| Phase | 핵심 논문 | 보조 논문 |
|-------|-----------|-----------|
| **Phase 1** — 기본 aerial image simulator (Fourier optics, pupil) | #19, #15 | #3, #11 |
| **Phase 2** — Partial coherence / source shape | #16 | #5, #11 |
| **Phase 3** — Wafer topography / DOF | #14 | #5 |
| **Phase 4** — Mask 3D | #12 (review 먼저), #7, #17 | #9, #2 |
| **Phase 5** — Resist (threshold → stochastic) | #4, #1, #20, #21 | #13 |
| **Phase 6** — OPC/ILT/SMO/PMWO | #9, #10, #6 | #16 |
| 광원 / 보조 | #18, #8 | — |

---

## 5. MVP 구현용 최소 3편 (인수인계 지시서 §10.6 대응)

가장 먼저 읽고 시뮬레이터 첫 버전을 만들 때 필요한 3편:

1. **#19 Anamorphic high-NA EUV optics (Migura 2015)**
   — 좌표 변환 + 광학 아키텍처 출발점
2. **#9 Fast SMO method for high-NA EUV (Li 2024)** ★OA
   — fast imaging model + SMO 통합 알고리즘 (구현 가능한 수식)
3. **#12 M3D Characterization and Mitigation (Erdmann 2017)**
   — Mask 3D 효과의 정량 체크리스트

---

## 6. Open Access 논문 우선 다운로드 리스트

브라우저에서 직접 받을 수 있는 무료 PDF:

| # | URL |
|---|-----|
| 1 | https://www.nature.com/articles/s41598-025-29021-2 |
| 2 | https://goldberg.lbl.gov/papers/Goldberg_SPIE88800_(2013).pdf |
| 3 | https://arxiv.org/pdf/2508.00433 |
| 4 | https://www.euvlitho.com/2017/P46.pdf |
| 5 | https://euvlitho.com/2024/S1.pdf |
| 7 | https://euvlitho.com/2023/P14.pdf |
| 9 | https://www.oejournal.org/oea/article/doi/10.29026/oea.2024.230235 |
| 11 | https://euvlitho.com/2024/P3.pdf |
| 12 | https://euvlsymposium.lbl.gov/pdf/2016/Oral/Wed_S2-1.pdf (LBL 슬라이드) |
| 15 | https://www.beckoptronic.com/uploads/cms/productsdownload/14/beck-tn-performance-of-optics-with-central-obscuration-v2-file.pdf |
| 16 | https://opg.optica.org/oe/abstract.cfm?uri=oe-33-2-2261 |
| 18 | https://ir.arcnl.nl/pub/67/00076OA.pdf |

→ **무료 11편**을 먼저 받으면 핵심의 절반 이상이 확보됨.

---

## 7. Paywalled 논문 접근 방법

다음 논문들은 SPIE Digital Library / AIP / De Gruyter 구독 필요:

- #6, #8, #10, #13, #14, #17, #19, #20 → **SPIE Digital Library**
- #21 → **AIP Journal of Applied Physics**
- #12 → **De Gruyter Advanced Optical Technologies** (LBL 슬라이드는 무료)

기관(학교/회사) 라이브러리 프록시를 통해 접근하시거나, 논문 저자에게 이메일로 reprint를 요청하는 것도 표준 방법입니다.

---

## 8. 매핑 검증이 필요한 논문

다음 논문은 원본 리스트의 제목과 정확히 일치하는 publication을 찾기 어려워 가장 가까운 매칭으로 매핑되었습니다. **사용자 확인 필요**:

- **#13** "Measurement and adjustment of resist SWA in EUV lithography"
  → 가장 가까운 매칭: SPIE 13686 paper 136860G "Controlling the resist profile in EUV imaging using SMO" (P. Dhagat et al. 2025)
  → 다른 후보가 있다면 알려주세요.

---

## 9. 다음 단계 제안

1. **Open Access 11편 먼저 다운로드** → `/논문/papers/pdfs/` 같은 폴더에 저장
2. **MVP 3편(#19, #9, #12)부터 정독** → Phase 1–4 구현 가이드 추출
3. **각 논문의 .md 파일에 직접 메모 추가** — 핵심 수식 발췌, 우리 코드의 어느 함수에 매핑되는지 표시
4. **Paywalled 논문은 기관 액세스로 한 번에 받기**

---

## 10. 작성 정보

- 작성일: 2026-04-25
- 작성자: 양 (자동 정리)
- 원본 리스트: `/논문/0.55 High-NA EUV참고 논문리스트.txt`
- 인수인계 지시서: `/논문/high_na_euv_paper_search_handoff.md`
