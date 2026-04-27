# High-NA EUV Simulator — 통합 학습 문서

> 21편 논문 + 워크스페이스 문서(`high_na_euv_physics_considerations.md`, `high_na_euv_paper_search_handoff.md`) 를 프로젝트 맥락에서 통합 정리
> 작성일: 2026-04-25

---

## 0. 프로젝트 한 줄 정의

**13.5 nm EUV 빛이 source → collector → illuminator → reflective mask → 6-mirror anamorphic projection → wafer를 거쳐 형성되는 aerial image와 printed pattern을 Fourier optics + ray tracing + mask 3D + resist 모델로 근사하는 시뮬레이터.**

목적은 장비 복제가 아니라 **회절·반사·수차·M3D·topography·resist의 상호작용을 코드로 재현**하는 것이며, 결국 OPC/ILT/SMO 보정의 design space를 탐색하는 것이다.

---

## 1. 21편 통합으로 본 시뮬레이터 6 Phase 흐름

```text
                     ┌──────────────────────────────────────┐
                     │  광원 (paper 18, 8) — 광원 모델       │
                     │  λ=13.5 nm, plasma spectrum, OOB     │
                     └──────────────────┬───────────────────┘
                                        ▼
   ┌─────────────────────────────────────────────────────────────┐
   │ Phase 2: Illuminator (source shape)                         │
   │  paper 16 (Deep RL relay + facet matching)                  │
   │  paper 5, 11  (산업 baseline σ 설정)                          │
   └────────────────────────────┬────────────────────────────────┘
                                ▼
   ┌─────────────────────────────────────────────────────────────┐
   │ Phase 4: Reflective Mask (M3D)                              │
   │  paper 12 (Erdmann review — 6대 효과)                        │
   │  paper 7, 17 (absorber engineering)                         │
   │  paper 2 (SHARP — actinic 검증 데이터)                        │
   └────────────────────────────┬────────────────────────────────┘
                                ▼
   ┌─────────────────────────────────────────────────────────────┐
   │ Phase 1: Projection Optics (Fourier optics)                 │
   │  paper 19 (Anamorphic 4×/8× — 좌표계 출발점)                  │
   │  paper 15 (Central obscuration PSF/MTF)                     │
   │  paper 3 (In-Line projector — alternative)                  │
   └────────────────────────────┬────────────────────────────────┘
                                ▼
   ┌─────────────────────────────────────────────────────────────┐
   │ Phase 3: Wafer Topography / DOF                             │
   │  paper 14 (DOF challenge & LCDU)                            │
   │  paper 5 (focus control)                                    │
   └────────────────────────────┬────────────────────────────────┘
                                ▼
   ┌─────────────────────────────────────────────────────────────┐
   │ Phase 5: Photoresist (threshold → stochastic)               │
   │  paper 4 (PSCAR/CAR fundamentals)                           │
   │  paper 1 (material vs optical decomposition)                │
   │  paper 20 (depth-resolved absorption)                       │
   │  paper 13 (resist SWA)                                      │
   │  paper 21 (full Monte Carlo chain)                          │
   └────────────────────────────┬────────────────────────────────┘
                                ▼
   ┌─────────────────────────────────────────────────────────────┐
   │ Phase 6: Correction / Optimization                          │
   │  paper 9 (Fast SMO with M3D — 학계 구현 가이드)               │
   │  paper 10 (PMWO LWR/overlay)                                │
   │  paper 6 (PMWO DRAM application)                            │
   │  paper 16 (RL for source)                                   │
   └─────────────────────────────────────────────────────────────┘
```

---

## 2. 논문 21편의 내재화된 핵심 메시지 (모듈별)

### 2.1 광학 시스템 아키텍처 — Phase 1

**핵심 물음: 왜 anamorphic + central obscuration인가?**

- **#19 Migura 2015 (Zeiss/ASML)** — High-NA EUV의 출발점.
  - **8 nm hp 이하 → NA > 0.5 필요**, 그러나 4× full-field reticle은 mask shadowing 때문에 불가
  - 해법: **4× scan / 8× cross-scan anamorphic + half-field 26×16.5 mm**
  - 6" mask infrastructure 재사용
  - 시뮬레이터 함의: **mask coordinate → wafer coordinate 변환은 단순 4× 축소가 아니라 비대칭 스케일링**

- **#15 Beck Optronic technote** — central obscuration의 PSF/MTF 영향 정량화
  - obscuration ratio ε에 따라 first sidelobe 증가, MTF 중간대역 attenuation
  - cutoff frequency는 보존
  - 시뮬레이터 함의: **pupil function P(fx, fy)는 단순 disk가 아니라 annulus** — `P = (r² ≤ NA²) ∧ (r² ≥ NA_inner²)`

- **#3 Shintake 2025 (OIST)** — alternative in-line projector
  - 4-mirror coaxial로 oblique CRA를 제거하면 mask 3D 효과가 근본적으로 줄어듦
  - 시뮬레이터 함의: **CRA = 0 시뮬레이션 옵션을 두면 M3D 효과의 ablation study가 가능**

### 2.2 광원 — Phase 1 직전 / source 모델

- **#18 Versolato 2019 (ARCNL, OA)** — tin LPP plasma physics topical review
  - sub-ps ~ μs 6 orders 시간 스케일 물리
  - Sn⁸⁺~Sn¹⁴⁺의 4d→4f UTA로 13.5 nm in-band 형성
  - 시뮬레이터 함의: 광원을 **monochromatic point source로 단순화하되, spectral bandwidth (Δλ/λ ≈ 2%)와 angular content는 옵션으로 두기**

- **#8 LPP source spectrum 2025** — out-of-band radiation 측정
  - DUV/IR 누설이 wafer dose에 부가 영향
  - 시뮬레이터 함의: 정밀 모드에서 **OOB radiation을 별도 dose 항으로 추가** 가능

### 2.3 Illuminator (조명계) — Phase 2

- **#16 Li 2025 Optics Express (OA)** — Deep RL로 facet matching 최적화
  - one-mirror off-axis relay로 obscuration 제거
  - illumination efficiency 26.24%, mask uniformity ~99%
  - 시뮬레이터 함의: source shape를 **field facet × pupil facet 조합**으로 모델링하는 것이 산업 현실; 단순 σ 파라미터(annular/dipole)는 1차 근사

### 2.4 Reflective Mask & M3D — Phase 4

**가장 중요한 모듈 — High-NA의 핵심 challenge**

- **#12 Erdmann 2017 Adv. Opt. Tech.** — Mask 3D effect 6대 현상 review
  1. Asymmetric shadowing (CRA ≠ 0)
  2. Orientation-dependent CD bias (H/V 차이)
  3. Telecentricity error (pitch별 chief ray 변동)
  4. Contrast loss (destructive interference)
  5. Pitch/size-dependent **best-focus shift** (absorber wavefront)
  6. Secondary images (absorber top reflection ghost)
  - 시뮬레이터 함의: **이 6개 효과가 모두 코드에 등장하는지 체크리스트로 사용**

- **#7 EUVL 2023 P14 — High-k near-n=1 absorber** (★ free)
  - 굴절률 n ≈ 1, 흡수 k ≫ 0인 absorber → BF shift 최소화
  - 시뮬레이터 함의: absorber n, k를 시뮬레이션 파라미터로 노출

- **#17 SPIE 13686 2025 — Best focus shift optical constant screening**
  - high-k (Ni 등) + low-n attenuated PSM (RuTa, PtMo, PtTe) 후보 정량 비교
  - 시뮬레이터 함의: **NILS, MEEF, BF range 메트릭을 mask 모듈 출력으로 정의**

- **#2 SHARP 2013 (LBNL)** — actinic 13.5 nm mask 검사
  - 시뮬레이터 함의: 직접 구현 대상 아님. **rigorous M3D 시뮬레이션 출력의 ground truth 비교 데이터** 출처

### 2.5 Wafer Topography & DOF — Phase 3

- **#14 SPIE 13686 2025 — High-NA DOF challenge & LCDU**
  - 0.55 NA에서 LCDU **18–42% 향상** (vs 0.33 NA, 29 nm pitch hex)
  - DOF 감소 대응: **PMWO + micro focus-drilling**
  - 시뮬레이터 함의: **DOF = k₂·λ/NA² → 0.55 NA에서 ~3× 좁아짐**. wafer height map z(x,y)를 단순 z 정수배 다중 평면이 아닌 **defocus phase term** `exp(i·2π·Δz·cosθ/λ)` 으로 처리

- **#5 EUVL 2024 S1 (van Schoot, ★ free)** — focus/overlay control 솔루션
  - stitching, 고속 stage, 개선된 sensor
  - 시뮬레이터 함의: half-field stitching의 좌표 모델 reference

### 2.6 Photoresist & Stochastic — Phase 5

**가장 깊이 있는 모듈 — threshold → 4-stage Monte Carlo 까지 단계적 확장**

#### Level 0 — threshold (MVP)
워크스페이스 문서 §52: `if dose > threshold: exposed`

#### Level 1 — chemical blur (Gaussian)
- **#4 PSCAR/CAR fundamentals (★ free)** — CAR 기본 메커니즘
  - acid generation → diffusion (Gaussian, σ ≈ 2-4 nm) → deprotection
  - PSCAR로 RLS trade-off + photon shot noise 동시 완화

#### Level 2 — depth-resolved absorption
- **#20 imec 2025 — EUV photon absorption distribution at 0.55 NA**
  - 두께 방향 absorption 비대칭 (top vs bottom)
  - 시뮬레이터 함의: aerial image를 **`I(x, y, z)` 3D**로 확장
- **#13 ASML 2025 — Resist SWA / SMO for resist profile**
  - SWA-through-focus 측정, micro focus-drilling으로 균질화
  - 시뮬레이터 함의: focus map을 **z slice별로 다르게 둘 수 있는 옵션** (focus drilling)

#### Level 3 — full stochastic decomposition
- **#1 Park 2025 Sci. Reports (★ OA)** — material vs optical stochastic decomposition
  - 저전류·작은 CD: optical 지배
  - 고전류·큰 CD: material 지배
  - 두 효과는 **partial compensation** (단순 합 아님)
  - 시뮬레이터 함의: **LWR variance budget을 `σ²_total = σ²_optical(dose, CD) + σ²_material(dose, CD) + cross-term` 식으로 분리**
- **#21 Fukuda 2025 J. Appl. Phys.** — full stochastic chain Monte Carlo
  - photon → secondary electron → acid → deprotection → dissolution
  - binomial / beta-binomial / mixed Bernoulli convolution
  - 시뮬레이터 함의: 각 단계의 분포가 다음 단계로 전파되는 **Markov chain Monte Carlo** 구조

### 2.7 Correction / Optimization — Phase 6

**산업 PMWO vs 학계 fast SMO 두 line이 모두 있음**

#### 학계 — Fast SMO with M3D
- **#9 Li, Dong 2024 OEA (★ OA)** — **이 프로젝트의 핵심 구현 가이드**
  - Fast High-NA imaging model (M3D + anamorphic 포함)
  - mask: gradient-based + source: compressive sensing + MRC step
  - **Open Access — 수식과 알고리즘을 자유롭게 인용 가능**

#### 산업 — PMWO (Pupil-Mask-Wavefront Co-Optimization)
- **#10 SPIE 13686 2025** — PMWO with LWR/overlay metrics
- **#6 SPIE 13979 2025** — PMWO applied to DRAM 2D layout
- 시뮬레이터 함의: pupil + mask + wavefront 3변수 동시 최적화 framework
  - **목적함수: contrast + LWR + overlay penalty**

#### 대안 — Deep RL
- **#16** illuminator 단에서 RL로 facet 조합 최적화 (Phase 2와 6의 연결)

---

## 3. 핵심 수식 통합 표

| 수식 | 의미 | Phase | 출처 |
|------|------|-------|------|
| `R = k₁·λ/NA` | 분해능 한계 (k₁ ≈ 0.25–0.4) | 1 | Physics doc §8 |
| `DOF = k₂·λ/NA²` | 초점 깊이 (NA² 의존성) | 3 | Physics doc §9, paper 14 |
| `NA = n·sinθ` | 수집 각도 (n=1, EUV vacuum) | 1 | Physics doc §10 |
| `I(x,y) = \|F⁻¹{F{M}·P}\|²` | Fourier imaging | 1 | Physics doc §19 |
| `P → P·exp(i·2πW/λ)` | wavefront/aberration → pupil phase | 1, 4 | Physics doc §28 |
| `r⃗ = i⃗ - 2(i⃗·n⃗)n⃗` | 반사 벡터 | 3 | Physics doc §13 |
| `2d·sinθ = mλ` | Bragg reflection (multilayer) | 1 (mirror) | Physics doc §35 |
| `mλ = p·sinθ_m` | mask grating equation | 4 | Physics doc §38 |
| `OPL = ∫n·ds`, `φ = 2π·OPL/λ` | 위상 누적 | 1 | Physics doc §79 |
| `Dose = ∫I(t)dt` | resist dose | 5 | Physics doc §51 |
| `NILS = (CD/I)·∂I/∂x \|edge` | edge contrast | 4, 6 | paper 17 |
| Anamorphic: `(x_w, y_w) = (x_m/4, y_m/8)` | 좌표 변환 (asym) | 1 | paper 19 |
| Annular pupil OTF | central obscuration | 1 | paper 15 |
| `σ²_LWR = σ²_opt + σ²_mat + cross` | stochastic decomposition | 5 | paper 1 |

---

## 4. 시뮬레이터 모듈 → 논문 매핑 마스터표

| 모듈 | 입력 | 출력 | 핵심 논문 | 보조 논문 |
|------|------|------|-----------|-----------|
| **source.py** | λ, σ_bandwidth, source size | spectrum, angular dist | #18 | #8 |
| **illuminator.py** | source shape (annular/dipole/freeform) | pupil σ_in, σ_out, polarization | #16 | #5, #11 |
| **mask.py** (Kirchhoff) | M(x,y) binary | M_field(x,y) thin | physics doc §38 | — |
| **mask_3d.py** (rigorous) | absorber stack n, k, t | M_field with phase | #12 | #7, #17, #2 |
| **pupil.py** | NA, ε_obscuration, Zernike a_n | P(fx, fy) | #19, #15 | #3 |
| **aerial.py** | M, P, partial coherence | I(x,y) or I(x,y,z) | physics doc §19 | #14 |
| **wafer_topo.py** | z(x,y), focus offset | defocus phase map | physics doc §43-46 | #14, #5 |
| **resist_threshold.py** | I(x,y), threshold | binary printed pattern | physics doc §52 | — |
| **resist_blur.py** | I, Gaussian σ_blur | blurred dose | physics doc §53 | #4 |
| **resist_stochastic.py** | I, photon density, MC | LER, LWR, defect rate | #1, #21 | #4, #20, #13 |
| **smo.py** | target M_target, M, source | optimized M, source | #9 | #10, #6 |
| **pmwo.py** | M, source, wavefront | optimized triplet | #10, #6 | #9 |
| **metrics.py** | printed pattern | CD, EPE, NILS, LWR, MEEF | #14, #17 | #1 |

---

## 5. Phase별 구현 시작 가이드

### Phase 1 (1–2주차) — Scalar Fourier Optics MVP
- 읽을 논문: **#19** (필수, anamorphic 좌표) → **#15** (central obscuration)
- 구현 항목:
  - `pupil.py`: annular pupil with ε_obscuration
  - `aerial.py`: `I = |IFFT(FFT(M) · P)|²`
  - 좌표: anamorphic 4×/8× 옵션
- 검증 sanity check:
  - 단일 line/space 패턴의 Airy blur 재현
  - λ/NA² 단위로 contrast가 떨어지는지 확인

### Phase 2 (3주차) — Partial coherence
- 읽을 논문: **#16** (RL relay) — 단, 알고리즘 자체는 구현하지 말고 σ 파라미터 모델만 차용
- 구현 항목: source point sampling + incoherent intensity sum

### Phase 3 (4주차) — Wafer topography / DOF
- 읽을 논문: **#14** (DOF & LCDU)
- 구현 항목: defocus phase `exp(i·π·z(x,y)·NA²/λ)` (Fresnel 근사)

### Phase 4 (5–6주차) — Mask 3D
- 읽을 논문: **#12** (★ 가장 먼저), **#7**, **#17**
- 구현 항목:
  - Kirchhoff thin-mask vs domain decomposition method (DDM) approximation
  - absorber n, k 입력 → BF shift 출력 검증
  - **paper 12의 6개 효과 체크리스트**로 단위 테스트

### Phase 5 (7–8주차) — Resist
- 읽을 논문 (단계적):
  - Level 0: physics doc §52 (threshold)
  - Level 1: **#4** (PSCAR/CAR Gaussian blur)
  - Level 2: **#20**, **#13** (depth-resolved)
  - Level 3: **#1**, **#21** (full stochastic)

### Phase 6 (9–12주차) — Optimization
- **MVP**: **#9** (★ OA, 가장 직접 구현 가이드)
- **확장**: **#10**, **#6** (PMWO 산업 사례)
- 목적 함수:
  ```
  Loss = α·CD_error + β·EPE + γ·LWR + δ·overlay + λ·smoothness
  ```

---

## 6. 프로젝트의 현실적 단순화 (논문 → 시뮬레이터 매핑)

| 논문이 다루는 정밀도 | 우리 시뮬레이터의 단순화 |
|----------------------|---------------------------|
| Rigorous 3D EM mask (Maxwell, RCWA) | Kirchhoff thin-mask + boundary correction |
| Full stochastic chain Monte Carlo (paper 21) | 1차: threshold + Gaussian blur, 2차: dose-noise injection |
| Real plasma source physics (paper 18) | monochromatic point source + 옵션 spectral bandwidth |
| Real PMWO with industrial constraints (paper 6, 10) | 학계 fast SMO (paper 9) baseline 구현 |
| Anamorphic + central obscuration + 6-mirror cascade (paper 19) | 2D pupil function with annular shape + asym scale |
| Real resist 3D depth absorption (paper 20) | 2D aerial image + 옵션 z-slicing |
| Multilayer mirror angle/polarization-dependent reflectivity | constant R (예: 0.7^n_mirror) baseline |

---

## 7. 우선 검증해야 할 가정 (open questions)

각 phase에서 검증 없이 진행하면 위험한 가정들:

1. **Kirchhoff mask가 0.55 NA에서 충분히 정확한가?**
   - paper 12, 17은 명시적으로 부정. domain decomposition method (DDM) 또는 lookup table 추가 필요
2. **monochromatic 가정이 OOB radiation 효과를 무시해도 되는가?**
   - paper 8 — dose 계산 시 ~몇 % 오차 가능
3. **threshold resist + Gaussian blur가 LWR을 정량적으로 예측하는가?**
   - paper 1, 21 — NO. stochastic 분포 합성이 필요
4. **anamorphic 4×/8×에서 mask 좌표의 원점/회전은?**
   - paper 19 figure 참조 — scan direction이 1× 방향 (8× demag)
5. **central obscuration이 SMO 목적함수에 어떻게 영향?**
   - paper 9, 14 — pupil의 obscured 영역은 source 분포에서도 활용 불가

---

## 8. 즉시 시작 가능한 3가지 작업

### 작업 1: Open Access 11편 다운로드 (사용자 수동)
INDEX.md §6 참고. 브라우저로 11편 PDF 받아 `papers/pdfs/` 보관.

### 작업 2: MVP 3편 정독
- **#19** Migura 2015 — anamorphic coordinate 정확히 도식화
- **#9** Li 2024 OEA — fast imaging model 알고리즘 의사코드 추출
- **#12** Erdmann 2017 — M3D 6개 효과 단위 테스트 정의

### 작업 3: 시뮬레이터 디렉토리 스캐폴딩
```
high_na_euv_sim/
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
│   ├── phase1_aerial_image.py    # paper 19, 15
│   ├── phase4_m3d_checklist.py   # paper 12 6 effects
│   └── phase5_stochastic.py      # paper 1, 21
├── data/
│   └── absorber_nk/              # paper 7, 17 후보 재료
└── notebooks/
    └── 0_first_aerial_image.ipynb
```

---

## 9. 한 페이지 요약 (cheat sheet)

```text
WHAT  : 0.55 NA EUV simulator simulator
WHY   : aerial image, M3D, DOF, stochastic, OPC/ILT/SMO 통합 design space 탐색
WHERE : 6 Phase, 21편 논문, 13개 모듈

PHASE 1 (Fourier optics, anamorphic, obscuration)   → paper 19, 15, 3
PHASE 2 (partial coherence, illuminator)            → paper 16, 5, 11
PHASE 3 (DOF, wafer topography)                     → paper 14, 5
PHASE 4 (Mask 3D — 6 effects)                       → paper 12, 7, 17, 2
PHASE 5 (resist: threshold → stochastic)            → paper 4, 1, 20, 13, 21
PHASE 6 (SMO/PMWO/RL)                               → paper 9, 10, 6, 16
SOURCE  (광원 모델)                                  → paper 18, 8

MVP 3 편: #19 (좌표) + #9 (★OA SMO) + #12 (M3D 체크리스트)

핵심 trade-off  : NA↑ → R↑ but DOF↓ + M3D↑
핵심 단순화     : Kirchhoff mask + threshold resist + monochromatic source
핵심 위험       : 0.55 NA에서 Kirchhoff/threshold 가정의 정량적 한계
```

---

## 10. 다음 단계 권장 순서

1. **이 KNOWLEDGE.md를 READ-ONLY 기준 문서로 취급** — 새 논문이 추가될 때만 업데이트
2. **QUICK_REFERENCE.md** (별도 파일)에서 21편을 1줄씩 빠르게 lookup
3. **Phase 1 코드를 한 노트북에서 작성** — paper 19, 15만 봐도 충분히 시작 가능
4. **각 phase 시작 시 해당 phase의 논문을 다시 정독** + 단위 테스트로 paper의 메트릭 재현
5. **Mask 3D (Phase 4) 진입 전에 #12를 정독** — 이 단계가 프로젝트의 가장 큰 정확도 결정 요인
