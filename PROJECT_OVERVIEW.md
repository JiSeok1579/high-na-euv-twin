# High-NA EUV Lithography Digital Twin — 프로젝트 총정리

> 작성일: 2026-04-25
> 위치: `~/Desktop/High-NA EUV Lithography Digital Twin/`
> 본 문서는 프로젝트의 단일 진입점(single source of truth)이다. 처음 보는 사람도 이 문서만 읽으면 프로젝트의 정체성, 자산, 범위, 진행 상태, 다음 단계를 알 수 있도록 작성됨.

---

## 1. 프로젝트 한 줄 정의

> **0.55 NA EUV 노광 장비(ASML EXE 시리즈)에서 13.5 nm EUV 빛이 광원 → 조명계 → 반사형 마스크 → 6-mirror anamorphic projection → wafer를 거쳐 형성되는 aerial image와 printed pattern을 Fourier optics + ray tracing + mask 3D + photoresist 모델로 근사하는 연구·교육용 디지털 트윈 시뮬레이터를 만든다.**

### 이 프로젝트가 아닌 것
- 실제 High-NA EUV 장비 복제 또는 reverse engineering
- 특정 기업 장비 분해 / 제조 공정 레시피 추출
- 광원 plasma hardware 제조

### 이 프로젝트가 추구하는 것
- 공개된 물리 모델·수식·논문 기반의 **근사 시뮬레이션 모델**
- 회절·반사·수차·M3D·topography·resist의 상호작용을 **코드로 재현**
- OPC/ILT/SMO/PMWO **보정의 design space**를 탐색할 수 있는 도구

---

## 2. 워크스페이스 자산 인벤토리

```
High-NA EUV Lithography Digital Twin/
│
├── PROJECT_OVERVIEW.md              ← 본 문서 (진입점)
│
├── REVIEWER_DIRECTIVE.md            ← Claude 외부 감사자 지침 (v2.0)
│     • 3 전문가 (EUV/AI/Software) 병렬 + Data Scientist 통합자
│     • 2-stage 외부 감사 → 4-md 폴더 산출 (A1+A2+A3+00_FINAL)
│     • 코드 작성자가 올바르게 진행하도록 데이터 기반 최적화 권고
│
├── high_na_euv_physics_considerations.md
│     • 82개 섹션, ~31KB. 시뮬레이터 구현 관점의 물리 수식·모델·구현 우선순위.
│     • Part A–W로 구성: Maxwell → 회절 → NA → 기하광학 → Fourier → coherence
│       → 편광 → 수차 → multilayer → mask → projection → wafer → aerial → resist
│       → 평가지표 → 보정 → 수치해석 → 열·진동 → 제어·계측 → 6단계 구현 우선순위
│     • 구현 핸드북으로 가장 자주 펼치게 될 문서.
│
├── 고해상도 극자외선 리소그래피(0.55 High-NA EUV)의 물리적 한계,
│   광학적 아키텍처 및 확률론적 모델링에 관한 심층 연구 보고서.docx
│     • 3MB, 9개 주요 섹션, 22개 헤딩, 2개 표.
│     • 학술 보고서 톤의 심층 리뷰. 다음을 다룸:
│         §1 미세공정 한계와 High-NA 필연성
│         §2 LPP 광원 물리 (다가 이온, 광대역 spectrum)
│         §3 Anamorphic 광학계 수학 (4×/8×) + 등방성 파국 + 다층막 각도 한계
│         §4 다중 반사경 + central obscuration 회절 영향
│         §5 마스크 3D + High-k/Low-n absorber
│         §6 DOF 붕괴 + micro focus-drilling + PMWO
│         §7 확률론적 결함 + RLS trade-off + 광학·재료 stochastics 분리
│         §8 Hyper-NA (NA ≥ 0.75) 미래 전망
│         §9 결론
│     • 학문적 배경 / 발표·문서화에 사용. 시뮬레이터 코딩에서는 보조.
│
├── audits/                          ← 감사 시스템 (gated review, 2-layer)
│     • Layer 1 — 4-역할 self-audit (코드 작성자용)
│       - 01_data_analyst/INSTRUCTIONS.md (데이터 입력·전처리·EDA)
│       - 02_physics/INSTRUCTIONS.md (물리 검증자, 10원칙·6 smoke test)
│       - 03_ai_numerical/INSTRUCTIONS.md (FFT·sampling·gradient·MC)
│       - 04_simulation/INSTRUCTIONS.md (Phase Gate 8요소 + ablation)
│     • Layer 2 — external/ 외부 감사 (Claude, REVIEWER_DIRECTIVE v2.0)
│       - reports/EXT-AUD-<id>/ 폴더 단위, 4-md 산출 (A1/A2/A3/00_FINAL)
│       - 첫 사례: EXT-AUD-2026-04-26-001 Phase 1 Initial Review (PASS w/ 1 P0)
│     • README.md (시스템 개요), 00_CI_CD_WORKFLOW.md (gated review 6 단계)
│     • AUDIT_LOG.md (감사 이력 + 미해결 mitigation task 추적)
│     • templates/ (audit_report, change_request)
│
├── .github/                          ← GitHub Actions + PR 자동화
│     • workflows/ci.yml (pytest + mypy + ruff + coverage)
│     • workflows/claude.yml (Claude Code Review + 4-역할 감사)
│     • workflows/pr-title.yml (PR title = squash merge title 명명 규칙 검증)
│     • workflows/auto-merge.yml (`auto-merge` label 기반 native auto-merge)
│     • CLAUDE.md, PULL_REQUEST_TEMPLATE.md, CODEOWNERS, dependabot.yml
│
├── docs/github_claude_automerge_setup.md
│     • GitHub + Claude Code + branch protection + 자동 머지 셋업 가이드
│
├── scripts/
│     • configure_github_automerge.sh (repo setting, labels, branch protection 자동 적용)
│
└── 논문/                             ← Reference paper 저장소
    │
    ├── 0.55 High-NA EUV참고 논문리스트.txt
    │     • 21편 원본 제목 리스트 (정렬되지 않은 raw 입력)
    │
    ├── high_na_euv_paper_search_handoff.md
    │     • 16KB. 논문 탐색자 인수인계 지시서.
    │     • 6개 핵심 주제축, 13개 검색 가이드, Phase별 매핑, 정리 양식 정의.
    │
    └── papers/                       ← 21편 논문 정리 (이번 작업 결과)
        │
        ├── README.md                 폴더 구성 안내
        ├── INDEX.md                  마스터 인덱스 (21편 표 + 분야별 + Phase별)
        ├── KNOWLEDGE.md              ★ 통합 학습 문서 (379줄)
        │     • 6 Phase 흐름도 + 모듈별 내재화 + 핵심 수식 통합표
        │       + 시뮬레이터 모듈 ↔ 논문 매핑 + Phase별 구현 가이드
        │       + open questions + cheat sheet
        ├── QUICK_REFERENCE.md        21편 1줄 카드 (Phase별 lookup)
        │
        └── 01_*.md … 21_*.md         21편 개별 메타데이터 (각 1.5–2.2KB)
              • 각 파일: 링크, DOI, 연도, 저자, 분야, 우선순위,
                핵심 문제, 사용 모델, 핵심 결과, 우리 프로젝트 적용 부분, 난이도
```

**문서 간 관계 도식**:
```
                    [PROJECT_OVERVIEW.md]   ← 여기서 시작
                            │
              ┌─────────────┼──────────────┐
              ▼             ▼              ▼
   [physics_                [.docx         [논문/papers/
    considerations.md]      심층 보고서]     KNOWLEDGE.md]
    (구현 핸드북)            (학술 톤)        (논문 통합 학습)
              │             │              │
              └─────────────┴──────────────┘
                            │
                  [실제 시뮬레이터 코드]   ← 아직 없음. 다음 단계.
```

---

## 3. 시뮬레이터 시스템 흐름

```
EUV Light Source (λ = 13.5 nm, LPP plasma, ~2% bandwidth)
        ↓
Source Vessel / Collector  (debris mitigation, multilayer mirror)
        ↓
Illuminator  (annular / dipole / quadrupole / freeform source shape, σ control)
        ↓
Reflective EUV Mask  (multilayer + capping + absorber pattern; M3D effects)
        ↓
Projection Optics  (4× scan / 8× cross-scan anamorphic 6-mirror cascade
                    + central obscuration, ~NA 0.55)
        ↓
Wafer Topography  (z(x, y) height map → local defocus phase)
        ↓
Aerial Image Solver  (Fourier optics: I = |IFFT(FFT(M)·P)|²)
        ↓
Photoresist Model  (threshold → chemical blur → depth-resolved → stochastic)
        ↓
Correction / Optimization  (OPC, ILT, SMO, PMWO; loss = α·CD + β·EPE + …)
```

**핵심 trade-off chain (왜 어렵나):**
```
NA ↑ → Resolution ↑ → DOF ↓ → wafer topology 민감도 ↑ → focus/dose 보정 부담 ↑
                  → mask CRA ↑ → M3D 효과 ↑ → mask absorber engineering 필요
                  → polarization 차이 ↑ → s/p 분리 모델 필요
                  → aberration tolerance ↓ → wavefront control 정밀도 ↑
```

---

## 4. 프로젝트 범위 (스코프)

### 4.1 In-scope (우리가 만들 것)

| 구성요소 | 설명 | 핵심 모델 |
|----------|------|-----------|
| **Aerial image solver** | mask → wafer 빛 분포 | Fourier optics + annular pupil + anamorphic 좌표 |
| **Mask 3D module** | 두꺼운 absorber의 위상·shadowing | Kirchhoff thin-mask + boundary correction (1차) |
| **Wafer topography** | 높이 → defocus phase | Fresnel 근사 |
| **Photoresist model** | dose → printed pattern | Level 0 threshold → Level 3 stochastic Monte Carlo |
| **Ray tracing** | mirror cascade vector map | vector reflection + ray-surface intersection |
| **Partial coherence** | source shape | source point sampling + incoherent intensity sum |
| **OPC/ILT/SMO/PMWO** | mask·source 최적화 | gradient + compressive sensing (paper 9 baseline) |
| **Metrics** | CD, EPE, NILS, LWR, MEEF, LCDU | 모든 phase에서 출력 |

### 4.2 Out-of-scope (안 만들 것)

| 항목 | 이유 |
|------|------|
| 실제 plasma source physics | paper 18을 reference로만, monochromatic point source로 단순화 |
| Rigorous Maxwell mask EM (RCWA/FDTD) | 계산량 + 데이터 부재. Kirchhoff + correction으로 대체 |
| Real multilayer mirror angle/polarization-dependent reflectivity | 상수 R로 baseline 시작 |
| 열·진동·기계 오차의 정량 모델 | 정성적으로만 인지, 입력 noise로 추상화 |
| 기업 장비 prescription 재현 | 공개 정보 기반 generic 모델만 |

---

## 5. 구현 로드맵 — 6 Phase

`physics_considerations.md` Part U + `papers/KNOWLEDGE.md` §5와 동기화.

| Phase | 기간 | 산출물 | 핵심 입력 논문 | 핵심 검증 |
|-------|------|--------|-----------------|-----------|
| **Phase 1** Scalar Fourier optics MVP | 1–2주 | `aerial.py`, `pupil.py` (annular + anamorphic) | #19, #15 | line/space Airy blur 재현 |
| **Phase 2** Partial coherence | 3주 | `illuminator.py` (annular/dipole/quadrupole) | #16, #5 | source shape별 contrast 변화 |
| **Phase 3** Wafer topography & DOF | 4주 | `wafer_topo.py` (defocus phase) | #14, #5 | DOF = k₂·λ/NA² 정량 검증 |
| **Phase 4** Mask 3D | 5–6주 | `mask_3d.py`, M3D 6 효과 단위 테스트 | #12, #7, #17 | paper 12의 6개 효과 재현 |
| **Phase 5** Photoresist | 7–8주 | `resist.py` (Level 0 → 3) | #4, #1, #20, #13, #21 | LWR/CDU 정성적 일치 |
| **Phase 6** Correction / Optimization | 9–12주 | `smo.py`, `pmwo.py`, `metrics.py` | #9, #10, #6 | target → mask 역최적화 |

**MVP 정의 (Phase 1+3+5의 최소 모듈로 first end-to-end 통과):**
```
λ = 13.5 nm, NA = 0.55, ε_obs = 0.2 (예시)
mask: 단순 line/space binary
pupil: annular (ε)
wafer height: z = 0 (flat 우선)
resist: threshold
출력: aerial image + binary printed pattern + CD error
```

**우선 학습 5편 (모두 무료/OA):**
1. **#19** Migura 2015 Anamorphic — 좌표계 출발점 (paywall, 학교 라이브러리)
2. **#15** Beck Optronic central obscuration ★free — annular pupil 정량
3. **#9** Li 2024 OEA Fast SMO ★OA — fast imaging + SMO 구현 가이드
4. **#12** Erdmann 2017 M3D review — 6 효과 체크리스트
5. **#11** ASML 2024 First Imaging ★free — 시뮬레이터 target 수치

---

## 6. 산출물(Deliverables) 목록

### 6.1 이미 완료 (current state)

- ✅ `high_na_euv_physics_considerations.md` — 82개 섹션 물리 핸드북
- ✅ `.docx 심층 연구 보고서` — 학술 톤 종합 리뷰
- ✅ `논문/0.55 High-NA EUV참고 논문리스트.txt` — 21편 원본 리스트
- ✅ `논문/high_na_euv_paper_search_handoff.md` — 탐색 인수인계
- ✅ `논문/papers/` 25개 파일 — 21편 메타데이터 + 통합 학습 4종

### 6.2 다음으로 만들 것 (in progress / not started)

- ⏳ `논문/papers/pdfs/` — Open Access 11편 다운로드 (사용자 수동, 외부 네트워크 필요)
- ✅ `src/` (Phase 1) — `constants.py`, `pupil.py`, `mask.py`, `aerial.py`
- ✅ `src/optics/zernike.py` — Zernike wavefront helper 공용화
- ✅ `src/wafer_topo.py` — Phase 3 defocus sign convention + pupil phase helper
- ✅ `src/dof.py` — Phase 3 focus-stack contrast + nominal DOF metric + k2 fit + focus-drilling average
- ⏳ `src/` (Phase 2–6) — `illuminator.py`, `mask_3d.py`, `resist_*.py`, `smo.py`, `pmwo.py`, `metrics.py`
- ✅ `tests/phase1_aerial_image.py` — 5 unit tests, all PASS
- ✅ `tests/audits/test_fft_invariants.py` — Parseval / fftshift / NA scaling / grid refinement invariant tests
- ✅ `tests/phase3_DOF.py` — defocus sign / conjugacy / sampling / DOF / k2 / focus-drilling regression tests
- ⏳ `tests/` (Phase 2–6) — 후속 Phase 단위 테스트
- ✅ `notebooks/0_first_aerial_image.ipynb` — Phase 1 데모
- ⏳ `notebooks/` (Phase 2–6) — 후속 데모
- ⏳ `data/absorber_nk/` — absorber n,k 데이터 (paper 7, 17 후보 재료)
- ✅ `docs/phase1_design.md` — Phase 1 설계 결정 + 단순화 명시
- ✅ `.pre-commit-config.yaml` — ruff + basic file hygiene hooks
- ✅ `.github/` + `scripts/configure_github_automerge.sh` — CI, Claude review, title-gated auto-merge 셋업
- ✅ `docs/phase3_design.md` — defocus 부호 컨벤션 + DOF/k2/focus-drilling 현재 한계
- ✅ `docs/phase3_DOF_analysis.md` — DOF metric Part 03 분석 노트
- ⏳ `docs/` (Phase 2–6, API) — 후속 문서

### 6.3 권장 디렉토리 스캐폴딩 (제안)

```
High-NA EUV Lithography Digital Twin/
├── PROJECT_OVERVIEW.md
├── high_na_euv_physics_considerations.md
├── 고해상도 ... .docx
├── 논문/ … (현재 그대로 유지)
│
├── src/
│   ├── source.py
│   ├── illuminator.py
│   ├── mask.py
│   ├── mask_3d.py
│   ├── pupil.py
│   ├── aerial.py
│   ├── wafer_topo.py
│   ├── resist.py
│   ├── smo.py
│   ├── pmwo.py
│   └── metrics.py
├── tests/
│   ├── phase1_aerial_image.py        # paper 19, 15
│   ├── phase3_DOF_check.py           # paper 14
│   ├── phase4_m3d_checklist.py       # paper 12 6 effects
│   └── phase5_stochastic_LWR.py      # paper 1, 21
├── data/
│   └── absorber_nk/                  # paper 7, 17 후보 재료
├── notebooks/
│   ├── 0_first_aerial_image.ipynb
│   ├── 1_partial_coherence.ipynb
│   ├── 2_DOF_topography.ipynb
│   ├── 3_M3D_effects.ipynb
│   ├── 4_resist_models.ipynb
│   └── 5_SMO_PMWO.ipynb
├── docs/
│   └── api/
└── README.md
```

---

## 7. 핵심 수식 빠른 참조

| 영역 | 수식 | 적용 Phase |
|------|------|-----------|
| 분해능 | `R = k₁·λ/NA`, `λ=13.5nm, NA=0.55, k₁≈0.3` | 1 |
| 초점 깊이 | `DOF = k₂·λ/NA²` | 3 |
| Numerical Aperture | `NA = n·sinθ`, `n=1` (vacuum) | 1 |
| Fourier imaging | `I = \|IFFT(FFT(M)·P)\|²` | 1 |
| Pupil + 수차 | `P → P·exp(i·2πW/λ)` | 1, 4 |
| 반사 벡터 | `r = i − 2(i·n)n` | 3 |
| Bragg | `2d·sinθ = mλ` | 1 (multilayer) |
| Mask grating | `mλ = p·sinθ_m` | 4 |
| Anamorphic | `(x_w, y_w) = (x_m/4, y_m/8)` | 1 |
| Annular pupil | `P = (r ≤ NA) ∧ (r ≥ NA·ε)` | 1 |
| Defocus phase | `φ = π·z·NA²/λ` (Fresnel) | 3 |
| Dose | `D = ∫I(t)dt` | 5 |
| LWR decomposition | `σ²_LWR = σ²_opt(D,CD) + σ²_mat(D,CD) + cross` | 5 |
| NILS | `(CD/I)·∂I/∂x \|edge` | 4, 6 |

---

## 8. 핵심 trade-off 표

| 변수 | ↑하면 좋은 점 | ↑하면 나쁜 점 |
|------|---------------|----------------|
| **NA** | Resolution | DOF↓, M3D↑, polarization 효과↑, aberration 민감도↑ |
| **Source σ (sigma)** | feature size 다양성 대응 | contrast↓ |
| **Absorber 두께** | 절대 흡수↑ | shadowing↑, BF shift↑ |
| **Resist 두께** | 패턴 transfer 용이 | top-bottom dose 차이↑ (depth-resolved 필요) |
| **Dose** | LWR↓, sensitivity 부족 보완 | throughput↓, photo damage↑ |
| **Mirror 수** | aberration correction 자유도↑ | reflectivity loss↑ (R^N) |

---

## 9. 알려진 위험과 미해결 질문 (Open Questions)

`papers/KNOWLEDGE.md` §7과 동기화.

1. **Kirchhoff thin-mask가 0.55 NA에서 정량적으로 정확한가?**
   - paper 12, 17은 명시적으로 부정. → DDM(domain decomposition method) 또는 lookup table 필요
2. **monochromatic 가정의 dose 오차?**
   - paper 8 — OOB radiation으로 ~몇 % 오차 가능
3. **threshold + Gaussian blur가 LWR 정량 예측?**
   - paper 1, 21 — NO. stochastic 분포 합성 필요
4. **anamorphic 4×/8× 좌표 원점/회전 컨벤션?**
   - paper 19 figure 정독 필요
5. **central obscuration 영역의 source 활용 가능 여부?**
   - paper 9, 14 — pupil obscured 영역은 source에서도 활용 불가
6. **paper #13 매핑 정확도** — 원 제목 "Measurement and adjustment of resist SWA in EUV"가 SPIE 13686 paper 136860G "Controlling resist profile via SMO"와 정확히 일치하는지 확인 필요
7. **단위 테스트의 ground truth 부재** — synthetic data로 sanity check만 가능. 실험 데이터 확보가 어려움 (industrial proprietary)

---

## 10. 즉시 실행 가능한 다음 단계

### Step 1 — 논문 다운로드 (사용자 수동, 1일)
- Open Access 11편을 브라우저로 받아 `논문/papers/pdfs/`에 저장
- 다운로드 URL: `papers/INDEX.md §6` 또는 `papers/QUICK_REFERENCE.md` 체크리스트
- 이 환경의 네트워크는 외부 도메인 차단되어 자동 다운로드 불가

### Step 2 — 정독 5편 + 코딩 환경 (1주)
- 우선 학습 5편 (#19, #15, #9, #12, #11) 정독 — 핵심 수식·알고리즘 발췌해 각 .md 파일에 메모
- Python 환경: `numpy + scipy + matplotlib + jupyter`
- 디렉토리 스캐폴딩 (위 §6.3) 생성

### Step 3 — Phase 1 MVP (1–2주)
- `pupil.py`: annular pupil function (paper 15 수식)
- `aerial.py`: `I = |IFFT(FFT(M)·P)|²`
- `tests/phase1_aerial_image.py`: 단순 line/space 패턴의 Airy blur 재현 + paper 19 anamorphic 좌표 검증

### Step 4 — Phase 4 진입 전 #12 정독 (1주)
- M3D 6 효과를 단위 테스트로 변환
- absorber n, k DB 구축 (`data/absorber_nk/` — paper 7, 17 후보)

### Step 5 — Long-term (3개월+)
- Phase 5 stochastic resist (paper 21 Markov chain MC)
- Phase 6 SMO (paper 9 baseline)
- 산업 PMWO 비교 (paper 6, 10 — 가능하면 institutional access)
- Hyper-NA (NA ≥ 0.75) 확장 시뮬레이션 (.docx §8과 연계)

---

## 11. 문서 활용 가이드 — 어느 문서를 언제 읽을까?

| 상황 | 펼칠 문서 |
|------|-----------|
| 처음 프로젝트 인수받음 | **PROJECT_OVERVIEW.md** (현재 문서) |
| 시뮬레이터 코딩 시작 | `high_na_euv_physics_considerations.md` 의 해당 Part |
| 논문 21편 빠른 lookup | `논문/papers/QUICK_REFERENCE.md` |
| 특정 논문 상세 메타데이터 | `논문/papers/XX_*.md` |
| 21편을 프로젝트 맥락에서 통합 이해 | `논문/papers/KNOWLEDGE.md` |
| 학술 발표·문서화 | `.docx 심층 연구 보고서` |
| 새 논문 추가 시 | `INDEX.md`와 `KNOWLEDGE.md`에 항목 추가 |

---

## 12. 한 페이지 요약 (cheat sheet)

```
WHAT       0.55 NA EUV digital twin simulator (research/education)
WHY        High-NA의 회절·M3D·DOF·stochastic·SMO design space 탐색
WHERE      ~/Desktop/High-NA EUV Lithography Digital Twin/
HOW        Fourier optics + ray tracing + Kirchhoff mask + threshold→stochastic resist

자산 (현재):
  ✅ 물리 핸드북 (.md, 82 sections)
  ✅ 심층 연구 보고서 (.docx, 9 sections)
  ✅ 21편 논문 메타데이터 + 통합 학습 (KNOWLEDGE.md, QUICK_REFERENCE.md, INDEX.md)
  ⏳ 시뮬레이터 코드 (아직 없음)
  ⏳ Open Access PDF 다운로드 (사용자 수동)

다음 단계:
  1. OA 11편 다운로드
  2. 우선 학습 5편 정독: #19 #15 #9 #12 #11
  3. Phase 1 MVP 코딩 (annular pupil + anamorphic + Fourier imaging)
  4. Phase 4 진입 시 #12 다시 정독 후 M3D 단위 테스트

핵심 trade-off:    NA↑ → R↑  but DOF↓ + M3D↑
가장 큰 위험:      Phase 4 (Mask 3D) 의 Kirchhoff 가정 정량 한계
가장 단순화:       monochromatic + Kirchhoff + threshold + 상수 R
MVP 3편:           #19 (좌표) + #9 ★OA (SMO 구현 가이드) + #12 (M3D 체크리스트)
```

---

## 13. 변경 이력 / 메인테넌스

- **2026-04-25** 초기 작성. 워크스페이스 스캔, 21편 정리 완료, .docx 구조 확인.
- **2026-04-26** Phase 1 (Scalar Fourier Optics MVP) 구현 완료.
  - `src/constants.py`, `src/pupil.py`, `src/mask.py`, `src/aerial.py` 작성
  - `tests/phase1_aerial_image.py` 5/5 PASS (단일 pinhole PSF, line/space cutoff, annular sidelobe, anamorphic 26×33→6.5×4.125 mm, CD helper)
  - `notebooks/0_first_aerial_image.ipynb` (5 섹션 end-to-end)
  - `docs/phase1_design.md` (좌표·정규화·단순화 7개 명시)
  - KPI K1 (광학 파트), K2 (정성적 회절 cutoff at λ/NA = 24.5 nm) 합격
  - 디렉토리 스캐폴딩 (`src/`, `tests/`, `notebooks/`, `data/`, `docs/`) 생성
  - `pytest.ini` 작성 — `phase*_*.py` 자동 발견

> 새 논문 추가 / Phase 진행 / 코드 모듈 추가 시 본 문서의 §2(인벤토리), §5(로드맵), §6(산출물)을 동시 업데이트할 것.
