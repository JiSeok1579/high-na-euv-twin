# High-NA EUV Lithography Simulator: 물리 법칙 및 프로젝트 고려사항 정리

## 0. 문서 목적

이 문서는 **High-NA EUV Lithography Machine을 직접 복제하는 설계서가 아니라**,  
연구/교육/시뮬레이션 목적의 **High-NA EUV 리소그래피 시뮬레이터 또는 노광 시뮬레이터**를 구축할 때 고려해야 할 물리 법칙, 수학 모델, 공정 지식, 구현 우선순위를 정리한 문서이다.

목표는 다음과 같다.

```text
입력:
- EUV 광원 조건
- 조명계 조건
- 반사형 마스크 패턴
- 투영 광학계 조건
- 웨이퍼 topography
- photoresist 모델

출력:
- wafer 위 aerial image
- focus error map
- dose correction map
- ray/vector map
- 예상 printed pattern
- CD error / EPE / overlay error
```

---

## 1. 전체 시스템 개념

High-NA EUV 리소그래피 시뮬레이터는 다음 흐름을 모사해야 한다.

```text
[Light Source]
      ↓
[Source Vessel / Collector]
      ↓
[Illuminator]
      ↓
[Reflective Mask]
      ↓
[Projection Optics: Mirror Cascade]
      ↓
[Wafer Topology Model]
      ↓
[Aerial Image Solver]
      ↓
[Resist Model]
      ↓
[Correction / Optimizer]
```

각 단계는 독립적인 모듈처럼 보이지만, 실제로는 서로 강하게 연결되어 있다.

예를 들어:

```text
NA 증가
→ 해상도 향상
→ depth of focus 감소
→ wafer topography 민감도 증가
→ focus/dose 보정 필요
→ OPC/ILT 난도 증가
```

---

# Part A. 빛과 파동의 기본 물리

## 2. Maxwell 방정식

### 핵심 개념

빛은 전자기파이다. 전기장과 자기장이 서로를 만들며 공간을 전파한다.

### 프로젝트에서 필요한 이유

Maxwell 방정식은 다음 현상의 근본 출발점이다.

```text
- 빛의 전파
- 반사
- 간섭
- 회절
- 편광
- 위상 변화
- 물질과의 상호작용
```

### 구현 고려사항

완전한 Maxwell solver는 계산량이 매우 크다. 따라서 프로젝트 초기에는 다음 근사를 사용하는 것이 현실적이다.

```text
1. Scalar diffraction model
2. Fourier optics model
3. Vector diffraction model
4. 필요 시 RCWA/FDTD 같은 full-wave solver 부분 적용
```

---

## 3. 파동 방정식

### 핵심 식

```math
\nabla^2 E - \frac{1}{c^2}\frac{\partial^2 E}{\partial t^2} = 0
```

### 의미

빛의 전기장 \(E\)는 파동처럼 공간을 따라 전파된다.

### 프로젝트에서 필요한 이유

리소그래피에서 빛은 직선으로만 이동하지 않는다. aperture, mask edge, mirror aperture를 지나면서 회절하고 간섭한다.

따라서 다음 현상을 설명하려면 파동 모델이 필요하다.

```text
- Airy disk
- diffraction blur
- line/space pattern merging
- aerial image formation
- phase error
```

---

## 4. 파장, 주파수, 광속 관계

### 핵심 식

```math
c = \lambda f
```

### 의미

파장 \(\lambda\)가 짧을수록 더 높은 공간 주파수의 패턴을 전달할 수 있다.

### EUV 기준

반도체 EUV 리소그래피에서 대표적으로 사용하는 파장은 다음과 같이 둔다.

```text
λ = 13.5 nm
```

### 프로젝트 고려사항

시뮬레이터의 기본 파라미터는 다음처럼 설정한다.

```python
lambda_euv = 13.5e-9  # meter
```

---

# Part B. 회절과 분해능

## 5. Huygens-Fresnel 원리

### 핵심 개념

파면의 각 점은 새로운 작은 파동의 출발점처럼 행동한다.

### 의미

빛은 aperture나 edge를 지난 뒤 단순히 직진하지 않고 퍼진다.

### 프로젝트에서 필요한 이유

다음 현상을 설명한다.

```text
- aperture diffraction
- mask edge diffraction
- Airy pattern
- aerial image blur
```

---

## 6. 회절 Diffraction

### 핵심 개념

빛이 유한한 구멍, 마스크 패턴, edge, slit 등을 지날 때 퍼지는 현상이다.

### 리소그래피에서의 의미

회로 패턴은 매우 작은 선과 공간으로 구성되어 있다. 이 구조는 빛 입장에서 회절 grating처럼 작동한다.

### 프로젝트 고려사항

회절을 무시하면 다음을 예측할 수 없다.

```text
- 선폭 증가 또는 감소
- line merging
- contact hole collapse
- contrast 감소
- 패턴 edge blur
```

---

## 7. Airy Disk / Point Spread Function

### 핵심 개념

점광원을 광학계로 모아도 완벽한 점이 아니라 중심 밝기와 어두운 고리를 가진 퍼진 패턴이 생긴다.

### 의미

광학계가 한 점을 찍으면 실제 wafer 위에는 퍼진 점이 형성된다.

### 프로젝트에서 필요한 이유

Airy disk 또는 PSF는 실제 패턴이 왜 번지는지를 설명한다.

```text
ideal pattern
→ optical PSF와 convolution
→ blurred aerial image
```

---

## 8. Rayleigh 분해능 기준

### 핵심 식

리소그래피에서는 보통 다음 형태로 사용한다.

```math
R = k_1 \frac{\lambda}{NA}
```

### 변수

```text
R  : 최소 분해 가능한 거리
k1 : 공정 계수
λ  : 파장
NA : numerical aperture
```

### 의미

두 점 또는 두 선이 간신히 구분되는 최소 한계를 나타낸다.

### 프로젝트에서 중요한 이유

Rayleigh 기준은 다음을 결정한다.

```text
- 만들 수 있는 최소 선폭
- line/space pitch 한계
- EUV 파장을 써야 하는 이유
- High-NA가 필요한 이유
- 패턴이 붙거나 분리되는 경계
```

---

## 9. Depth of Focus, DOF

### 핵심 식

```math
DOF = k_2 \frac{\lambda}{NA^2}
```

### 의미

초점이 맞는 허용 높이 범위이다.

### 중요한 trade-off

```text
NA 증가
→ resolution 향상
→ DOF 감소
→ wafer height/topography 영향 증가
```

### 프로젝트 고려사항

High-NA EUV 모델에서는 wafer height map을 반드시 고려해야 한다.

```text
z(x, y) 변화
→ local defocus 발생
→ aerial image blur
→ CD error / EPE 증가
```

---

# Part C. Numerical Aperture와 광학계 한계

## 10. Numerical Aperture, NA

### 핵심 식

```math
NA = n \sin\theta
```

### 변수

```text
n : 매질의 굴절률
θ : 광학계가 받아들이는 최대 각도
```

EUV는 진공에서 전파되므로 보통 \(n \approx 1\)로 둔다.

### 의미

NA는 광학계가 얼마나 넓은 각도의 빛을 받아들일 수 있는지를 나타낸다.

---

## 11. NA 증가의 효과

### 장점

```text
NA ↑
→ 더 많은 고차 회절광 수집
→ 더 작은 패턴 분해 가능
→ 해상도 향상
```

### 단점

```text
NA ↑
→ DOF 감소
→ focus 민감도 증가
→ mask 3D effect 증가
→ polarization effect 증가
→ optical aberration 민감도 증가
```

### 프로젝트 고려사항

NA는 단순히 크게 설정하면 좋은 값이 아니다. 다음과 같이 같이 평가해야 한다.

```text
- Resolution
- DOF
- pupil cutoff
- mask shadowing
- wafer topography sensitivity
- aberration tolerance
```

---

# Part D. 기하광학과 벡터 계산

## 12. Ray 개념

### 핵심 개념

빛을 파동이 아니라 직선 광선으로 근사한다.

### 프로젝트에서 필요한 위치

```text
- source vessel
- collector mirror
- illuminator
- projection mirror cascade
- wafer incident angle map
```

### 한계

Ray tracing은 회절과 간섭을 직접 설명하지 못한다. 따라서 wave optics와 함께 사용해야 한다.

---

## 13. 반사의 법칙

### 핵심 식

```math
\vec r = \vec i - 2(\vec i \cdot \vec n)\vec n
```

### 변수

```text
vec i : 입사 방향 벡터
vec n : 표면 법선 벡터
vec r : 반사 방향 벡터
```

### 프로젝트에서 필요한 이유

EUV 광학계는 렌즈 대신 거울 cascade를 사용하므로 반사 벡터 계산이 핵심이다.

### 구현 예시

```python
def reflect(i, n):
    i = normalize(i)
    n = normalize(n)
    return i - 2 * dot(i, n) * n
```

---

## 14. Ray-Surface Intersection

### 광선 식

```math
\vec r(t) = \vec o + t\vec d
```

### 표면 식

```math
F(x,y,z)=0
```

### 교점 계산

```math
F(\vec o + t\vec d)=0
```

을 풀어 ray가 mirror 또는 wafer와 만나는 위치를 구한다.

### 프로젝트 고려사항

거울 표면이 spherical, aspherical, freeform일 수 있으므로 numerical root solving이 필요할 수 있다.

---

## 15. Surface Normal

### 표면이 \(z=f(x,y)\)일 때

```math
\vec n = \frac{(-f_x, -f_y, 1)}{\sqrt{f_x^2 + f_y^2 + 1}}
```

### 프로젝트에서 필요한 이유

```text
- mirror reflection
- wafer local tilt
- local incidence angle
- topology-induced phase error
```

---

## 16. 좌표 변환

### 핵심 식

```math
\vec x' = R\vec x + \vec t
```

### 필요한 좌표계

```text
- source coordinate
- collector coordinate
- illuminator coordinate
- mask coordinate
- pupil coordinate
- projection optics coordinate
- wafer coordinate
- stage coordinate
```

### 프로젝트 고려사항

각 모듈의 좌표계를 명확히 정의하지 않으면 vector map과 aerial image가 맞지 않는다.

---

# Part E. Fourier Optics

## 17. Fourier Transform

### 핵심 개념

복잡한 마스크 패턴은 여러 공간 주파수 성분의 합으로 볼 수 있다.

### 리소그래피 의미

```text
작은 pitch / 좁은 line width
→ 높은 spatial frequency
→ 광학계가 전달하기 어려움
```

### 프로젝트 고려사항

마스크 패턴을 Fourier transform해서 pupil cutoff와 곱하는 방식으로 aerial image를 계산한다.

---

## 18. Pupil Function

### 핵심 개념

광학계가 어떤 공간 주파수를 통과시키는지 나타내는 함수이다.

```math
P(f_x, f_y)
```

### 구성 요소

```text
- aperture limit
- NA cutoff
- aberration phase
- defocus phase
- apodization
- polarization effect
```

---

## 19. Fourier Imaging Model

### 핵심 식

```math
E_{wafer}(x,y)
=
\mathcal{F}^{-1}
\left[
\mathcal{F}\{M(x,y)\} \cdot P(f_x,f_y)
\right]
```

```math
I(x,y)=|E_{wafer}(x,y)|^2
```

### 의미

마스크 패턴이 optical pupil을 거쳐 wafer 위 전기장과 intensity image로 변환된다.

### 프로젝트에서 가장 먼저 구현할 모델

```text
mask pattern M(x,y)
→ FFT
→ pupil filter P(fx, fy)
→ IFFT
→ aerial image I(x,y)
```

---

## 20. PSF, OTF, MTF

### PSF: Point Spread Function

점 하나가 광학계를 통과했을 때 wafer에 생기는 퍼짐 함수.

### OTF: Optical Transfer Function

광학계가 공간 주파수를 얼마나 전달하는지 나타내는 함수.

### MTF: Modulation Transfer Function

OTF의 크기 성분으로, contrast 전달 능력을 나타낸다.

### 프로젝트 고려사항

```text
PSF → blur 계산
OTF → 주파수 전달 분석
MTF → contrast 성능 평가
```

---

## 21. Convolution

### 핵심 식

```math
Image = Object * PSF
```

### 의미

이상적인 마스크 이미지가 광학계의 PSF와 섞여 실제 aerial image가 된다.

### 프로젝트 고려사항

초기 모델에서는 Fourier optics와 convolution 모델을 서로 검증용으로 사용할 수 있다.

---

# Part F. 간섭, Coherence, 조명계

## 22. 간섭 Interference

### 핵심 식

```math
I = |E_1 + E_2|^2
```

### 의미

서로 다른 경로의 빛이 위상에 따라 밝아지거나 어두워진다.

### 프로젝트 고려사항

회절광들이 wafer 위에서 간섭해 aerial image를 만든다.

---

## 23. Coherence

### 종류

```text
- temporal coherence
- spatial coherence
- partial coherence
```

### 리소그래피에서의 중요성

실제 리소그래피 조명은 완전 coherent도, 완전 incoherent도 아니다. 부분 coherence 모델이 필요하다.

---

## 24. Partial Coherence Imaging

### 계산 개념

```text
for each source point:
    coherent image 계산
sum intensities incoherently
```

### 프로젝트 고려사항

조명계 source shape에 따라 aerial image가 달라진다.

```text
- conventional illumination
- annular illumination
- dipole illumination
- quadrupole illumination
- freeform illumination
```

---

## 25. Illuminator Model

### 역할

Illuminator는 마스크에 입사하는 빛의 각도 분포를 설계한다.

### 고려할 파라미터

```text
- source shape
- pupil fill
- partial coherence σ
- angular distribution
- intensity uniformity
```

### 프로젝트 고려사항

특정 패턴에 맞는 source shape를 최적화하는 SMO 모델로 확장할 수 있다.

---

# Part G. 편광과 High-NA 효과

## 26. 편광 Polarization

### 핵심 개념

편광은 빛의 전기장 방향이다.

### High-NA에서 중요한 이유

NA가 커지면 광선 각도가 커지고 s/p polarization 차이가 커진다.

---

## 27. s/p Polarization

### 정의

```text
s-polarization: 전기장이 입사면에 수직
p-polarization: 전기장이 입사면에 평행
```

### 프로젝트 고려사항

EUV multilayer mirror의 반사율은 입사각과 polarization에 따라 달라질 수 있다.

초기 모델에서는 무시할 수 있지만, High-NA 정밀 모델에서는 포함해야 한다.

---

# Part H. 수차와 Wavefront Error

## 28. Aberration

### 핵심 개념

이상적인 wavefront와 실제 wavefront의 차이이다.

```math
W(x,y)
```

### 주요 수차

```text
- defocus
- astigmatism
- coma
- spherical aberration
- distortion
- field curvature
```

### 프로젝트 고려사항

수차는 pupil function에 phase term으로 넣을 수 있다.

```math
P \rightarrow P \cdot e^{i 2\pi W/\lambda}
```

---

## 29. Zernike Polynomial

### 핵심 개념

원형 pupil 위의 wavefront error를 표현하는 표준 basis이다.

```math
W(\rho,\theta)=\sum a_n Z_n(\rho,\theta)
```

### 프로젝트에서 필요한 이유

```text
- mirror alignment error 모델링
- wavefront error 표현
- aberration correction
- optical performance 평가
```

---

# Part I. EUV 특수 물리

## 30. EUV 파장

### 기본값

```text
λ = 13.5 nm
```

### 의미

짧은 파장 덕분에 기존 DUV보다 더 작은 패턴을 만들 수 있다.

---

## 31. EUV 흡수

### 핵심 개념

EUV는 대부분의 물질과 공기에서 강하게 흡수된다.

### 결과

```text
- 공기 중 전파 어려움
- 진공 필요
- 일반 렌즈 사용 어려움
- 반사형 광학계 필요
```

### 프로젝트 고려사항

전파 손실은 단순화해서 다음처럼 모델링 가능하다.

```math
I_{out}=I_{in}e^{-\alpha L}
```

---

## 32. Plasma Source

### 핵심 개념

EUV는 고온 plasma에서 발생한다고 모델링할 수 있다.

### 시뮬레이션 파라미터

```text
- source size
- wavelength bandwidth
- angular distribution
- source power
- pulse fluctuation
- intensity noise
```

### 프로젝트 고려사항

초기에는 실제 plasma 물리 대신 ray/intensity source로 단순화한다.

---

## 33. Debris / Contamination

### 핵심 개념

광원에서 나온 입자나 오염물이 mirror에 영향을 줄 수 있다.

### 시뮬레이션 모델

```text
- mirror reflectivity degradation
- contamination map
- time-dependent intensity loss
```

---

# Part J. Multilayer Mirror 물리

## 34. EUV Multilayer Mirror

### 핵심 개념

EUV는 투과 렌즈 대신 다층 반사거울을 사용한다.

### 프로젝트 고려사항

각 mirror는 다음 속성을 가져야 한다.

```python
Mirror = {
    "surface_type": "sphere | asphere | freeform",
    "position": [x, y, z],
    "normal_function": "n(x,y,z)",
    "aperture": "radius or boundary",
    "reflectivity": "R(theta, lambda, polarization)",
    "wavefront_error": "W(x,y)"
}
```

---

## 35. Bragg Reflection

### 핵심 식

```math
2d\sin\theta = m\lambda
```

### 의미

다층막에서 특정 파장과 각도 조건에서 반사가 강화된다.

### 프로젝트 고려사항

거울 반사율은 상수 하나가 아니라 다음에 의존한다.

```text
- wavelength
- incidence angle
- polarization
- multilayer stack
- contamination
```

---

## 36. Mirror Reflectivity Loss

### 핵심 식

```math
I_{out}=I_{in}\prod_i R_i
```

### 의미

여러 거울을 거치면 광량이 급격히 줄어든다.

### 프로젝트 고려사항

projection optics의 mirror 수가 증가하면 throughput이 감소한다.

---

# Part K. 반사형 마스크 물리

## 37. EUV Reflective Mask

### 구성

```text
- substrate
- multilayer reflector
- capping layer
- absorber pattern
```

### 의미

EUV 마스크는 투과형이 아니라 반사형이다.

---

## 38. Mask Diffraction

### Grating equation

```math
m\lambda = p\sin\theta_m
```

### 의미

마스크 패턴은 회절 grating처럼 작동한다.

### 프로젝트 고려사항

패턴 pitch가 작아질수록 고차 회절광이 projection pupil 밖으로 잘려나갈 수 있다.

---

## 39. Mask 3D Effect

### 핵심 개념

마스크 absorber는 실제 두께가 있으므로 단순한 2D 패턴이 아니다.

### High-NA에서 중요한 이유

입사각이 커지면 absorber shadowing이 커진다.

### 발생 문제

```text
- pattern shift
- CD asymmetry
- shadowing
- image imbalance
```

---

# Part L. Projection Optics

## 40. Projection System

### 핵심 역할

마스크 이미지를 축소해서 wafer 위에 투영한다.

### 고려사항

```text
- magnification / demagnification
- mirror cascade
- wavefront error
- distortion
- pupil shape
- chief ray angle
```

---

## 41. Demagnification

### 개념

마스크 패턴은 wafer에 축소되어 투영된다.

예:

```text
mask feature 40 nm
→ 4x reduction
→ wafer feature 10 nm
```

### 프로젝트 고려사항

mask coordinate와 wafer coordinate 사이의 scale factor를 명확히 설정해야 한다.

---

## 42. Telecentricity

### 핵심 개념

wafer에 들어오는 chief ray angle이 위치에 따라 크게 변하지 않도록 하는 성질이다.

### 깨질 경우

```text
- focus 변화에 따른 image shift
- overlay error
- CD variation
```

---

# Part M. Wafer Topography와 Focus

## 43. Wafer Height Map

### 핵심 식

```math
z = z(x,y)
```

### 의미

wafer 표면 높이를 위치별로 나타낸다.

### 프로젝트 고려사항

height map은 focus error 계산의 입력이다.

---

## 44. Local Tilt

### 핵심 식

```math
\frac{\partial z}{\partial x}, \frac{\partial z}{\partial y}
```

### 의미

wafer 표면이 국소적으로 얼마나 기울어져 있는지를 나타낸다.

### 영향

```text
- local incidence angle 변화
- focus plane mismatch
- overlay error
```

---

## 45. Defocus

### 핵심 식

```math
\Delta z(x,y)=z(x,y)-z_{focus}(x,y)
```

### 의미

wafer 표면이 최적 초점면에서 벗어난 정도이다.

### 프로젝트 고려사항

defocus는 aerial image blur와 CD error를 발생시킨다.

---

## 46. Defocus Phase

### 개념

Fourier optics에서는 defocus를 pupil phase error로 넣을 수 있다.

```math
P \rightarrow P \cdot e^{i\phi_{defocus}}
```

### 프로젝트 고려사항

wafer topography를 단순 높이 값으로만 보지 말고 optical phase error로 변환해야 한다.

---

# Part N. Aerial Image와 Image Quality

## 47. Aerial Image

### 핵심 식

```math
I(x,y)=|E(x,y)|^2
```

### 의미

photoresist 위에 도달한 빛의 세기 분포이다.

### 프로젝트에서 핵심 출력

```text
- aerial image map
- image contrast
- edge slope
- line merging 여부
```

---

## 48. Image Contrast

### 핵심 식

```math
Contrast = \frac{I_{max}-I_{min}}{I_{max}+I_{min}}
```

### 의미

선과 공간이 얼마나 잘 구분되는지를 나타낸다.

---

## 49. NILS

### 의미

Normalized Image Log Slope는 edge 근처에서 이미지가 얼마나 급격히 변하는지 나타낸다.

### 프로젝트 고려사항

NILS가 낮으면 edge 위치가 불안정해지고 EPE가 커진다.

---

# Part O. Photoresist와 공정 물리

## 50. Photoresist

### 핵심 개념

빛을 받으면 화학적으로 변하는 감광막이다.

### EUV에서 중요한 점

EUV photon은 에너지가 크고 photon 수가 상대적으로 적어서 stochastic effect가 중요하다.

---

## 51. Dose

### 핵심 식

```math
Dose = \int I(t)dt
```

### 의미

resist가 받은 단위 면적당 에너지이다.

### 프로젝트 고려사항

local dose map을 사용해 위치별 보정을 적용할 수 있다.

---

## 52. Threshold Resist Model

### 가장 단순한 모델

```text
if dose > threshold:
    exposed
else:
    unexposed
```

### 프로젝트 적용

MVP에서는 threshold model로 충분하다. 이후 chemical blur, stochastic noise를 추가한다.

---

## 53. Chemical Blur

### 핵심 개념

photoresist 내부에서 산 또는 반응 생성물이 확산되며 image가 추가로 blur된다.

### 프로젝트 고려사항

aerial image에 Gaussian blur 또는 diffusion kernel을 적용해 근사 가능하다.

---

## 54. Stochastic Effect

### 핵심 개념

EUV에서는 photon shot noise와 화학 반응 확률성이 패턴 변동을 만든다.

### 발생 문제

```text
- line edge roughness
- local CD variation
- random missing contact
- bridge defect
```

---

# Part P. 패턴 평가 지표

## 55. CD, Critical Dimension

### 의미

패턴의 핵심 선폭이다.

### 예시

```text
target CD = 16 nm
printed CD = 17.2 nm
CD error = +1.2 nm
```

---

## 56. EPE, Edge Placement Error

### 의미

패턴 edge가 목표 위치에서 얼마나 벗어났는지를 나타낸다.

### 프로젝트 고려사항

최종 loss function에 반드시 포함해야 할 지표이다.

---

## 57. Overlay

### 의미

여러 공정 layer가 서로 얼마나 정확히 정렬되는지이다.

### 문제

overlay error가 크면 회로 연결 오류 또는 short가 발생할 수 있다.

---

# Part Q. 보정과 최적화

## 58. OPC, Optical Proximity Correction

### 핵심 개념

빛이 퍼지고 왜곡될 것을 예상해서 마스크 패턴을 미리 보정한다.

### 프로젝트에서의 역할

```text
target wafer pattern
→ mask bias / assist feature / edge correction
→ printed pattern 개선
```

---

## 59. ILT, Inverse Lithography Technology

### 핵심 개념

목표 wafer pattern에서 역으로 최적의 mask pattern을 계산한다.

### 수학적 성격

Inverse problem이다.

```text
desired output
→ find input mask/source/dose/focus
```

---

## 60. SMO, Source-Mask Optimization

### 핵심 개념

source shape와 mask pattern을 동시에 최적화한다.

### 목적

```text
- contrast 증가
- process window 증가
- CD error 감소
- EPE 감소
```

---

## 61. Loss Function

### 예시

```math
Loss =
\alpha CD_{error}
+ \beta EPE
+ \gamma Overlay
+ \delta DosePenalty
+ \epsilon SmoothnessPenalty
```

### 프로젝트 고려사항

최적화 대상은 다음이 될 수 있다.

```text
- dose map
- focus map
- source shape
- mask bias
- OPC pattern
- mirror alignment parameter
```

---

## 62. Regularization

### 핵심 개념

최적화 결과가 물리적으로 불가능하거나 너무 복잡해지는 것을 막는다.

### 예시

```text
- dose map이 너무 급격히 변하지 않도록 제한
- mask pattern이 제조 불가능하게 복잡해지지 않도록 제한
- mirror correction 범위 제한
```

---

# Part R. 수치해석과 구현

## 63. Sampling

### 핵심 개념

grid 간격이 충분히 작아야 고주파 패턴을 제대로 표현할 수 있다.

### 프로젝트 고려사항

mask grid, pupil grid, wafer grid의 해상도를 일관되게 설계해야 한다.

---

## 64. Nyquist 조건

### 핵심 식

```math
\Delta x \leq \frac{1}{2f_{max}}
```

### 의미

표현하려는 최대 공간 주파수의 두 배 이상으로 샘플링해야 aliasing을 피할 수 있다.

---

## 65. FFT

### 역할

Fourier optics 계산의 핵심 도구이다.

### 프로젝트에서 사용 위치

```text
mask pattern
→ FFT
→ pupil filtering
→ IFFT
→ aerial image
```

---

## 66. Interpolation

### 필요한 이유

서로 다른 grid의 데이터를 맞춰야 한다.

```text
- wafer height map
- dose map
- aerial image grid
- mask coordinate
- wafer coordinate
```

---

# Part S. 열, 진동, 기계 오차

## 67. Thermal Expansion

### 핵심 식

```math
\Delta L = \alpha L \Delta T
```

### 의미

온도 변화로 부품이 팽창하거나 수축한다.

### 프로젝트 고려사항

초정밀 광학계에서는 작은 열 변형도 wavefront error를 만든다.

---

## 68. Mirror Deformation

### 핵심 개념

거울 표면이 열, 응력, 오염 등으로 미세하게 변형될 수 있다.

### 모델링 방식

```text
surface error map
→ wavefront error W(x,y)
→ pupil phase error
```

---

## 69. Vibration

### 핵심 개념

스테이지 또는 광학계 진동이 노광 중 위치 오차를 만든다.

### 영향

```text
- overlay error
- image blur
- focus noise
```

---

# Part T. 제어와 계측

## 70. Feedback Control

### 핵심 개념

측정값을 보고 다시 보정하는 제어 방식이다.

### 예시

```text
measured focus error
→ stage z correction
→ exposure update
```

---

## 71. Feedforward Control

### 핵심 개념

미리 측정한 wafer map이나 distortion map을 사용해 선제적으로 보정한다.

### 예시

```text
wafer topology map
→ exposure 전 focus/dose map 생성
```

---

## 72. Metrology

### 필요한 계측 항목

```text
- wafer height / focus map
- overlay error
- CD measurement
- EPE measurement
- mirror wavefront error
- illumination uniformity
```

### 프로젝트 고려사항

시뮬레이터 검증을 위해 synthetic metrology data 또는 실제 측정 데이터를 입력으로 받을 수 있게 설계한다.

---

# Part U. 프로젝트 구현 우선순위

## 73. 1단계: Scalar Fourier Optics MVP

### 구현 목표

```text
mask pattern M(x,y)
→ FFT
→ pupil function P(fx,fy)
→ IFFT
→ aerial image I(x,y)
```

### 포함할 물리

```text
- wavelength λ
- NA
- Rayleigh resolution
- circular pupil
- simple line/space mask
```

### 출력

```text
- aerial image
- contrast
- line merging 여부
```

---

## 74. 2단계: Wafer Topography / Defocus 추가

### 구현 목표

```text
z(x,y)
→ local defocus
→ defocus phase
→ degraded aerial image
```

### 포함할 물리

```text
- DOF
- height map
- local tilt
- defocus phase
```

### 출력

```text
- focus error map
- CD variation map
- topology-induced blur
```

---

## 75. 3단계: Ray Tracing / Mirror Cascade 추가

### 구현 목표

```text
source
→ collector
→ illuminator
→ projection mirror cascade
→ wafer incident vector map
```

### 포함할 물리

```text
- vector reflection
- ray-surface intersection
- mirror normal
- coordinate transform
- reflectivity loss
```

### 출력

```text
- ray path
- mirror hit map
- wafer incident angle map
- intensity loss
```

---

## 76. 4단계: Partial Coherence / Source Shape 추가

### 구현 목표

```text
source point별 coherent image 계산
→ intensity 합산
→ partial coherence image
```

### 포함할 물리

```text
- annular source
- dipole source
- quadrupole source
- pupil fill
```

---

## 77. 5단계: Resist Model 추가

### 구현 목표

```text
aerial image
→ dose map
→ threshold resist
→ printed pattern
```

### 확장

```text
- chemical blur
- stochastic noise
- line edge roughness
```

---

## 78. 6단계: Correction / Optimization 추가

### 구현 목표

```text
target pattern - printed pattern error 최소화
```

### 최적화 변수

```text
- dose map
- focus map
- mask bias
- source shape
- OPC correction
```

---

# Part V. 핵심 수식 모음

## 79. 주요 공식

### 파장-주파수 관계

```math
c = \lambda f
```

### NA

```math
NA = n\sin\theta
```

### Rayleigh Resolution

```math
R = k_1 \frac{\lambda}{NA}
```

### Depth of Focus

```math
DOF = k_2 \frac{\lambda}{NA^2}
```

### 반사 벡터

```math
\vec r = \vec i - 2(\vec i \cdot \vec n)\vec n
```

### Aerial Image

```math
I(x,y)=|E(x,y)|^2
```

### Fourier Imaging

```math
E_{wafer}
=
\mathcal{F}^{-1}
[
\mathcal{F}\{M\}P
]
```

### Mirror Loss

```math
I_{out}=I_{in}\prod_i R_i
```

### Optical Path Length

```math
OPL=\int n\,ds
```

### Phase

```math
\phi=\frac{2\pi}{\lambda}OPL
```

### Dose

```math
Dose=\int I(t)dt
```

---

# Part W. 최종 체크리스트

## 80. 반드시 고려해야 할 항목

```text
[광원]
- λ = 13.5 nm
- source size
- angular distribution
- intensity noise
- spectral bandwidth

[조명계]
- pupil fill
- source shape
- partial coherence
- illumination uniformity

[마스크]
- reflective mask
- absorber pattern
- mask diffraction
- mask 3D effect
- shadowing

[투영광학]
- mirror cascade
- mirror reflectivity
- wavefront error
- aberration
- NA
- pupil function

[웨이퍼]
- height map z(x,y)
- local tilt
- defocus
- stage position
- overlay

[이미징]
- Fourier optics
- PSF / OTF / MTF
- aerial image
- image contrast
- NILS

[Resist]
- dose
- threshold
- chemical blur
- stochastic noise
- printed pattern

[보정]
- focus correction
- dose correction
- OPC
- ILT
- SMO
- feedback/feedforward control

[평가]
- CD error
- EPE
- overlay error
- defect probability
- process window
```

---

# 81. 프로젝트의 현실적인 범위 정의

## 가능한 목표

```text
High-NA EUV 노광 현상을 근사하는 시뮬레이터 구축
```

구체적으로 가능:

```text
- Fourier optics 기반 aerial image solver
- wafer topology 기반 defocus model
- ray tracing 기반 mirror cascade vector map
- simplified resist model
- dose/focus correction optimizer
- OPC/ILT 기초 모델
```

## 피해야 할 목표

```text
실제 High-NA EUV Lithography Machine 복제
```

이유:

```text
- 원자 수준 mirror 표면 정밀도 필요
- EUV plasma source 및 debris control 필요
- 진공/열/진동/스테이지 제어 필요
- 고정밀 계측 및 feedback 필요
- 실제 장비 수준의 optical prescription은 공개적으로 재현 불가
```

---

# 82. 최종 요약

이 프로젝트에서 가장 중요한 물리 법칙과 모델은 다음 5개이다.

```text
1. Rayleigh resolution
   → 얼마나 작은 패턴을 만들 수 있는가

2. Fourier optics
   → 마스크 패턴이 wafer aerial image로 어떻게 변하는가

3. Vector reflection / ray tracing
   → EUV mirror cascade에서 빛이 어떻게 이동하는가

4. Defocus / wafer topography
   → wafer 높이 변화가 image를 어떻게 왜곡하는가

5. Photoresist / dose model
   → 빛의 세기 분포가 실제 printed pattern으로 어떻게 바뀌는가
```

최소 구현 모델은 다음과 같다.

```text
λ = 13.5 nm
NA = 0.55
mask pattern M(x,y)
pupil function P(fx,fy)
wafer height map z(x,y)
aerial image I(x,y)
threshold resist model
```

이 최소 모델만으로도 다음 현상을 1차적으로 재현할 수 있다.

```text
- 회절
- 분해능 한계
- Airy blur
- line merging
- defocus blur
- wafer topology 영향
- dose/focus correction 필요성
```

---

## 부록: 추천 구현 순서 요약

```text
Step 1. 2D scalar Fourier optics simulator
Step 2. NA / Rayleigh / pupil cutoff 적용
Step 3. wafer height map과 defocus phase 추가
Step 4. threshold resist model 추가
Step 5. CD / EPE 계산기 추가
Step 6. ray tracing mirror cascade 추가
Step 7. partial coherence source model 추가
Step 8. dose/focus correction optimizer 추가
Step 9. OPC / ILT 기초 알고리즘 추가
Step 10. stochastic resist / noise model 추가
```

