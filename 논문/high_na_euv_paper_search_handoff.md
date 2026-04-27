# 논문 탐색 인수인계 지시서  
## High-NA EUV Lithography Simulator / Simulator Project

작성 목적: 이 문서는 본 프로젝트를 처음 인수받은 연구자가 **어떤 프로젝트를 만들려고 하는지 이해하고**, 그 프로젝트에 필요한 논문을 **어떤 방향으로 찾아야 하는지** 안내하기 위한 지시서이다.

---

## 1. 프로젝트 개요

본 프로젝트의 목표는 실제 High-NA EUV Lithography Machine을 제작하거나 복제하는 것이 아니다.  
목표는 다음과 같은 **연구/교육/시뮬레이션용 시뮬레이터**을 구축하는 것이다.

> EUV 광원이 생성한 13.5 nm 빛이 source vessel, collector, illuminator, reflective mask, projection mirror cascade를 지나 wafer에 도달할 때, 회절·반사·수차·마스크 3D 효과·웨이퍼 topography·defocus·photoresist 반응에 의해 최종 패턴이 어떻게 형성되고 왜곡되는지 계산하는 소프트웨어 모델

즉, 실제 장비 구현이 아니라 다음을 예측하는 모델이다.

- 웨이퍼 위 aerial image
- line/space 패턴의 해상 한계
- Airy disk / PSF / OTF / MTF
- mask diffraction
- High-NA에 따른 depth of focus 감소
- wafer topography에 따른 local defocus
- dose/focus correction map
- OPC / ILT / SMO 기반 보정 방향
- CD error, EPE, overlay error
- stochastic resist defect 가능성

---

## 2. 프로젝트를 한 문장으로 설명

> High-NA EUV 리소그래피의 광학 경로와 웨이퍼 패턴 형성 과정을 Fourier optics, ray tracing, mask 3D model, wafer topography, photoresist model, computational lithography 최적화로 근사하는 시뮬레이터를 만든다.

---

## 3. 우리가 만들려는 시스템의 전체 흐름

```text
EUV Light Source
    ↓
Source Vessel / Collector
    ↓
Illuminator / Source Shape
    ↓
Reflective EUV Mask
    ↓
Projection Optics / Mirror Cascade
    ↓
Wafer Topography / Defocus
    ↓
Aerial Image Simulation
    ↓
Photoresist / Threshold or Stochastic Model
    ↓
Correction / Optimization
```

---

## 4. 논문 탐색자의 핵심 임무

논문 탐색자는 다음 질문들에 답할 수 있는 자료를 찾아야 한다.

1. High-NA EUV에서 해상도와 DOF는 어떻게 결정되는가?
2. 0.55 NA EUV에서 기존 0.33 NA EUV와 무엇이 달라지는가?
3. EUV reflective mask의 3D 효과는 aerial image에 어떤 영향을 주는가?
4. Mirror cascade와 pupil function은 어떻게 모델링하는가?
5. Fourier optics 기반 lithography simulation은 어떻게 구현하는가?
6. Partial coherence illumination은 어떻게 계산하는가?
7. Wafer topography와 defocus는 aerial image와 CD error에 어떻게 반영하는가?
8. Photoresist는 단순 threshold model로 충분한가, 아니면 stochastic model이 필요한가?
9. OPC, ILT, SMO는 어떤 목적함수와 최적화 방식으로 구현되는가?
10. 실제 장비의 세부 구조가 없어도 공개 논문 기반으로 근사 모델을 만들 수 있는 범위는 어디까지인가?

---

## 5. 논문 탐색 우선순위

### Priority A — 반드시 찾아야 하는 핵심 논문

#### A1. High-NA EUV overview / roadmap

찾아야 할 내용:

- High-NA EUV가 왜 필요한가
- NA 0.55의 의미
- 기존 0.33 NA EUV 대비 개선점
- resolution / contrast / process window 변화
- anamorphic imaging 개념
- High-NA에서 새로 심각해지는 문제

검색 키워드:

```text
"High-NA EUV lithography review"
"0.55 NA EUV lithography imaging overlay"
"High NA EUV prospects challenges"
"High NA EUV roadmap 0.55 NA"
"High NA EUV anamorphic imaging"
```

우선 볼 출처:

- SPIE Advanced Lithography proceedings
- imec High-NA EUV articles
- ASML public technical articles
- Journal of Micro/Nanolithography, MEMS, and MOEMS
- Optics Express / Light: Science & Applications

---

#### A2. Fourier optics 기반 lithography simulation

찾아야 할 내용:

- mask field에서 aerial image 계산하는 방식
- pupil function 정의
- coherent / incoherent / partial coherent imaging
- Hopkins imaging theory
- TCC, transmission cross coefficient
- PSF, OTF, MTF
- defocus phase
- aberration phase

검색 키워드:

```text
"Fourier optics lithography simulation"
"Hopkins theory partial coherent imaging lithography"
"transmission cross coefficient lithography"
"pupil function aerial image lithography"
"EUV aerial image simulation Fourier optics"
```

논문 선택 기준:

- 실제 코드로 구현 가능한 수식이 있는 논문
- aerial image 계산 과정을 단계별로 설명하는 논문
- mask → pupil → wafer image로 이어지는 모델이 있는 논문

---

#### A3. High-NA EUV mask 3D effect

찾아야 할 내용:

- reflective mask 구조
- absorber shadowing
- mask-induced phase error
- diffraction order imbalance
- non-telecentricity
- threshold-to-size 변화
- NILS 변화
- mask 3D rigorous electromagnetic simulation

검색 키워드:

```text
"High NA EUV mask 3D effects"
"EUV mask shadowing high NA"
"mask 3D induced imaging mechanisms high NA EUV"
"reflective EUV mask absorber shadowing"
"EUV mask diffraction order imbalance"
```

중요 포인트:

- High-NA에서는 mask를 단순 2D binary pattern으로 보면 부정확할 가능성이 크다.
- 초기 MVP에서는 Kirchhoff mask model로 시작하되, 이후 mask 3D correction을 추가해야 한다.

---

#### A4. Source-Mask Optimization, SMO

찾아야 할 내용:

- source shape 최적화
- mask pattern 최적화
- annular / dipole / quadrupole illumination
- freeform illumination
- gradient-based SMO
- compressive sensing based SMO
- High-NA EUV용 fast SMO model

검색 키워드:

```text
"source mask optimization high NA EUV"
"fast source mask co-optimization high-NA EUV lithography"
"SMO EUV lithography mask 3D"
"computational lithography source mask optimization"
"freeform source optimization lithography"
```

연구자가 확인해야 할 것:

- source shape를 어떤 변수로 표현하는가
- mask update를 어떤 gradient로 계산하는가
- objective function이 CD/EPE/NILS 중 무엇을 최소화하는가
- High-NA 특유의 anamorphic magnification을 포함하는가

---

#### A5. OPC / ILT / computational lithography

찾아야 할 내용:

- OPC의 기본 모델
- ILT의 inverse problem formulation
- differentiable lithography simulation
- AI/ML 기반 ILT
- hotspot detection
- full-chip optimization
- EPE 기반 loss function

검색 키워드:

```text
"inverse lithography technology review"
"AI based inverse lithography technology"
"computational lithography review OPC ILT"
"differentiable lithography simulation"
"machine learning computational lithography EUV"
```

필요한 이유:

이 프로젝트의 최종 목표가 단순히 빛이 퍼지는 것을 보는 데서 끝나지 않고,  
`target pattern`에 맞게 `mask/source/dose/focus`를 보정하는 것이기 때문이다.

---

### Priority B — 모델 정확도를 높이기 위해 필요한 논문

#### B1. EUV photoresist / stochastic effects

찾아야 할 내용:

- EUV photon shot noise
- secondary electron blur
- acid diffusion
- line edge roughness, LER
- stochastic defects
- missing contact
- random bridge
- resist blur model

검색 키워드:

```text
"EUV lithography stochastic defects review"
"High NA EUV resist stochastic effects"
"EUV photoresist shot noise secondary electron blur"
"EUV line edge roughness stochastic modeling"
"resist model aerial image threshold stochastic EUV"
```

초기 구현에서는 threshold model로 충분하지만, 고급 모델에서는 stochastic resist model이 필요하다.

---

#### B2. Wafer topography / focus / leveling

찾아야 할 내용:

- wafer height map
- local defocus
- focus control
- leveling sensor
- depth of focus high NA EUV
- topography-induced CD variation
- focus exposure matrix

검색 키워드:

```text
"wafer topography defocus EUV lithography"
"focus control high NA EUV lithography"
"depth of focus high NA EUV wafer topology"
"topography induced CD variation lithography"
"wafer leveling lithography simulation"
```

중요 포인트:

High-NA에서 DOF는 NA^2에 반비례하므로 topography 영향이 커진다.  
따라서 wafer height map을 단순 데이터가 아니라 optical phase error로 연결해야 한다.

---

#### B3. Multilayer mirror / EUV reflectivity

찾아야 할 내용:

- Mo/Si multilayer mirror
- Bragg reflection
- angle-dependent reflectivity
- phase shift
- reflectance loss through multiple mirrors
- mirror contamination

검색 키워드:

```text
"EUV multilayer mirror high NA reflectivity phase"
"Mo Si multilayer EUV 13.5 nm reflectance angle"
"High NA EUV multilayer mirror phase effects"
"EUV mirror cascade reflectivity simulation"
```

필요한 이유:

EUV는 렌즈를 사용하지 않고 반사형 다층 거울을 쓰므로, 각 거울의 reflectivity와 phase error가 aerial image에 영향을 준다.

---

#### B4. Aberration / Zernike / wavefront error

찾아야 할 내용:

- Zernike polynomial
- wavefront error
- defocus, astigmatism, coma, spherical aberration
- aberration impact on CD/EPE
- aberration compensation in lithography

검색 키워드:

```text
"Zernike aberration EUV lithography"
"wavefront error impact lithography aerial image"
"aberration compensation EUV lithography"
"pupil aberration CD error lithography"
```

---

### Priority C — 구현 보조 논문/자료

#### C1. Ray tracing / mirror geometry

찾아야 할 내용:

- vector reflection
- freeform mirror modeling
- ray-surface intersection
- sequential ray tracing
- non-sequential ray tracing
- optical path length

검색 키워드:

```text
"ray tracing freeform mirror optical system"
"sequential ray tracing mirror cascade"
"vector reflection ray tracing optics"
"optical path length wavefront ray tracing"
```

#### C2. Numerical methods

찾아야 할 내용:

- FFT 기반 optical simulation
- sampling / aliasing
- GPU acceleration
- differentiable FFT optics
- adjoint optimization

검색 키워드:

```text
"FFT based lithography simulation"
"differentiable Fourier optics lithography"
"GPU accelerated computational lithography"
"adjoint optimization inverse lithography"
```

---

## 6. 논문 검색 시 제외하거나 낮은 우선순위로 둘 것

다음 자료는 프로젝트 초기에 우선순위를 낮춘다.

```text
- 실제 EUV 장비 제조 공정 세부 레시피
- 비공개 장비 구조 추정성 자료
- 특허만 있고 물리 모델이 부족한 자료
- 특정 기업 장비 분해/복제 목적의 자료
- 안전하지 않거나 불법적인 reverse engineering 목적 자료
- 광원 plasma hardware 제조 세부 공정만 다루는 자료
- 너무 오래된 DUV 전용 논문 중 EUV/High-NA에 적용이 어려운 자료
```

이 프로젝트는 실제 장비 복제가 아니라 시뮬레이션 모델 구축이 목적이므로, 논문 탐색도 공개된 모델링/물리/계산 리소그래피 중심으로 해야 한다.

---

## 7. 논문을 찾은 뒤 정리해야 하는 양식

각 논문마다 아래 항목으로 요약할 것.

```markdown
## 논문 제목

- 링크 / DOI:
- 연도:
- 저자 / 기관:
- 분야:
  - High-NA overview
  - Fourier optics
  - Mask 3D
  - SMO
  - OPC/ILT
  - Resist
  - Wafer topography
  - Mirror / multilayer
  - Aberration
- 핵심 문제:
- 사용한 모델:
- 핵심 수식:
- 입력 데이터:
- 출력 데이터:
- 우리 프로젝트에 쓸 수 있는 부분:
- 구현 난이도:
  - Low / Medium / High
- 우선순위:
  - A / B / C
- 비고:
```

---

## 8. 특히 찾아야 하는 수식/모델

논문에서 아래 수식이나 모델을 발견하면 반드시 따로 정리한다.

### 8.1 Resolution / DOF

```text
R = k1 * lambda / NA
DOF = k2 * lambda / NA^2
```

찾아야 할 것:

- k1, k2 범위
- High-NA에서의 실제 해석
- process window와의 관계

---

### 8.2 Fourier imaging model

```text
E_wafer = IFFT( FFT(Mask) * Pupil )
I_wafer = |E_wafer|^2
```

찾아야 할 것:

- coherent imaging
- partial coherent imaging
- Hopkins TCC
- source integration

---

### 8.3 Defocus phase

찾아야 할 것:

- wafer height map을 pupil phase로 넣는 방법
- defocus와 CD error 관계
- DOF와 topography tolerance

---

### 8.4 Mask 3D model

찾아야 할 것:

- Kirchhoff model과 rigorous EM model 차이
- absorber shadowing 수식
- diffraction order imbalance
- high-NA에서의 chief ray angle 영향

---

### 8.5 Resist model

찾아야 할 것:

- threshold resist model
- Gaussian blur resist model
- stochastic model
- shot noise / acid diffusion / secondary electron blur

---

### 8.6 Optimization loss

찾아야 할 것:

```text
Loss = alpha * CD_error
     + beta * EPE
     + gamma * overlay_error
     + delta * dose_penalty
     + regularization
```

확인할 것:

- 논문이 어떤 loss를 쓰는가
- gradient를 어떻게 계산하는가
- mask/source/dose/focus 중 어떤 변수를 최적화하는가

---

## 9. 프로젝트 구현 로드맵과 논문 매핑

### Phase 1 — 기본 aerial image simulator

필요 논문:

- Fourier optics
- pupil function
- coherent imaging
- Rayleigh resolution

구현 목표:

```text
mask pattern → FFT → pupil filtering → IFFT → aerial image
```

---

### Phase 2 — Partial coherence / source shape

필요 논문:

- Hopkins theory
- TCC
- source integration
- annular/dipole/quadrupole illumination

구현 목표:

```text
source points별 aerial image 계산 → intensity sum
```

---

### Phase 3 — Wafer topography / defocus

필요 논문:

- DOF
- wafer height map
- defocus phase
- focus-exposure matrix

구현 목표:

```text
z(x,y) → local defocus → aerial image degradation → focus correction map
```

---

### Phase 4 — Mask 3D effect

필요 논문:

- EUV reflective mask
- absorber shadowing
- rigorous EM simulation
- mask diffraction order imbalance

구현 목표:

```text
2D mask model → approximate 3D mask model
```

---

### Phase 5 — Resist model

필요 논문:

- threshold model
- stochastic resist
- EUV shot noise
- LER / missing contact

구현 목표:

```text
aerial image → dose map → printed pattern
```

---

### Phase 6 — OPC / ILT / SMO

필요 논문:

- inverse lithography
- source-mask optimization
- AI computational lithography
- differentiable simulator

구현 목표:

```text
target pattern과 printed pattern의 차이를 최소화하도록 mask/source/dose/focus 최적화
```

---

## 10. 논문 검색 결과의 최종 산출물

논문 탐색자가 최종적으로 제출해야 하는 결과물은 다음과 같다.

```text
1. 핵심 논문 10개 리스트
2. 각 논문별 1페이지 요약
3. 구현에 바로 쓸 수 있는 수식 목록
4. phase별 참고 논문 매핑표
5. 아직 부족한 연구 영역
6. MVP 구현에 바로 필요한 최소 논문 3개 추천
```

---

## 11. 추천 검색 순서

논문 탐색자는 다음 순서로 검색한다.

```text
1. High-NA EUV overview / roadmap
2. Fourier optics lithography simulation
3. Partial coherence / Hopkins theory
4. High-NA EUV mask 3D effect
5. Wafer topography / defocus
6. EUV photoresist stochastic effect
7. OPC / ILT / SMO
8. Multilayer mirror reflectivity
9. Aberration / Zernike modeling
10. GPU / differentiable implementation
```

---

## 12. 논문 탐색자가 주의해야 할 점

- 실제 장비 복제 관점으로 자료를 찾지 말 것.
- 논문은 “구현 가능한 수식과 모델”이 있는 것을 우선할 것.
- High-NA EUV는 0.55 NA, 13.5 nm, reflective mask, anamorphic imaging, mask 3D effect가 핵심이다.
- 단순 광학 ray tracing만으로는 부족하다. Fourier optics와 partial coherence가 반드시 필요하다.
- 웨이퍼 topography는 단순 3D 지형이 아니라 defocus phase와 CD/EPE error로 연결해야 한다.
- OPC/ILT/SMO는 프로젝트 후반부의 최적화 모듈과 연결된다.
- resist stochastic effect는 초기 MVP에서는 생략 가능하지만, 고급 모델에서는 필요하다.

---

## 13. 최종 요약

이 프로젝트에 필요한 논문은 크게 다음 6개 축으로 찾으면 된다.

```text
1. High-NA EUV system physics
2. Fourier optics / aerial image simulation
3. Mask 3D / reflective EUV mask effects
4. Wafer topography / defocus / DOF
5. Photoresist / stochastic patterning
6. Computational lithography / OPC / ILT / SMO
```

논문 탐색의 핵심 기준은 다음이다.

> “이 논문이 우리 시뮬레이터의 어떤 모듈을 구현하는 데 도움이 되는가?”

논문을 찾을 때는 단순히 유명한 논문보다,  
**수식·알고리즘·입출력 정의·구현 가능한 모델**이 명확한 논문을 우선 선택해야 한다.
