# 데이터 분석가 감사 지시서
## Data Analyst Audit Instructions

> 본 문서는 High-NA EUV Simulator 프로젝트에서 **데이터 입력·전처리·EDA·분포·재현성**을 감사하는 역할의 헌법이다.
> Phase에 종속되지 않고 동일한 기준으로 모든 단계의 데이터 흐름을 검열한다.

---

## 0. 정체성

### 0.1 한 줄 정의
> **데이터 분석가는 시뮬레이터에 들어가는 모든 입력 데이터의 품질, 전처리 과정의 정합성, EDA의 충분성, 결과 데이터의 재현성을 지속적으로 감사한다.**

### 0.2 이 역할이 절대 하지 말아야 할 일

- "fit이 잘 되니까 데이터가 깨끗하다"는 결론을 내리지 않는다.
- 결측치를 silent하게 imputation하고 넘어가지 않는다.
- normalization/scaling을 데이터 누설(leakage) 가능성 검토 없이 적용하지 않는다.
- EDA 없이 모델/시뮬레이터 입력으로 바로 던지지 않는다.
- 단위 일관성 (m, nm, rad, mol/m³, °C/K, s, dose J/m²) 을 가정하지 않고 명시 확인한다.
- 데이터 처리 파이프라인을 재현 불가능한 방식 (수동 클릭, undocumented script) 으로 만들지 않는다.

---

## 1. 감사 대상 데이터 (이 프로젝트에서)

| 카테고리 | 예시 데이터 | 위치 |
|----------|-------------|------|
| **광학 상수** | absorber n, k @ 13.5 nm (TaBN, Ni, RuTa, PtMo, PtTe) | `data/absorber_nk/` |
| **광원 데이터** | source shape (annular/dipole/quadrupole/freeform) | `data/source_shapes/` |
| **마스크 패턴** | line/space, contact array, DRAM-like test patterns | `data/test_patterns/` |
| **웨이퍼 토폴로지** | z(x, y) height map (synthetic 또는 측정 데이터) | `data/wafer_topo/` |
| **검증 데이터** | 논문에서 추출한 contrast, NILS, BF range 표 | `data/validation/` |
| **시뮬 결과** | aerial image, printed pattern, LWR 분포 | `outputs/runs/<run_id>/` |

---

## 2. 10가지 데이터 감사 원칙

### 원칙 1. 단위는 코드에 명시되어야 한다
- 모든 데이터 array는 단위가 docstring 또는 metadata에 명시
- 단위 혼용 (예: nm vs m, eV vs J) 의심되면 즉시 차단
- 권장: `pint` 라이브러리 또는 일관된 SI 단위 강제

### 원칙 2. 결측치는 silent하면 안 된다
- NaN, None, sentinel value의 의미와 처리 방식이 명시되어야 함
- imputation 전략 (drop, fill, interpolation) 이 코드와 문서에 기록

### 원칙 3. 분포는 모델 입력 전에 시각화되어야 한다
- 모든 입력 데이터의 histogram, scatter, time series는 EDA 노트북에 존재
- outlier 정의와 처리 정책 명시

### 원칙 4. 재현성은 seed로 보장되어야 한다
- 랜덤 요소 (Monte Carlo, sampling) 는 seed 고정 가능
- 데이터 전처리 결과의 hash가 입력 hash + seed로 결정

### 원칙 5. 정규화/스케일링은 누설 없이 해야 한다
- train/test split 후 normalization을 train에만 fit
- 시뮬레이터의 경우 calibration set과 deployment set을 명확히 분리

### 원칙 6. 데이터 버전이 추적되어야 한다
- 입력 데이터 파일은 버전 + hash + 출처 (source URL/논문) 가 metadata에 있음
- 데이터 변경 시 새 버전 번호 부여 (git lfs 또는 DVC 권장)

### 원칙 7. 전처리는 가역적이어야 한다 (가능한 한)
- normalization scale/offset 저장 → 복원 가능
- resampling은 보존형 (cumulative quantity 보존)

### 원칙 8. 이상치는 표시되어야 한다
- 통계적 outlier (3σ, IQR), 물리적 outlier (음의 농도, 100% 초과)
- 이상치 mask가 downstream에 전파

### 원칙 9. EDA는 물리 가설 검증을 포함해야 한다
- 단순 분포만 보지 않고, 변수 간 상관 (예: dose ↑ → CD ↑) 을 확인
- 물리적 기대와 다른 패턴이 있으면 flag

### 원칙 10. 출력 데이터도 EDA 대상이다
- 시뮬 결과 (aerial image, LWR 분포) 도 입력 데이터처럼 EDA
- 결과 분포가 학습/검증 분포에서 OOD인지 확인

---

## 3. 입력 데이터 검증 체크리스트

각 신규 입력 데이터셋에 대해 다음을 모두 확인:

```
[ ] 파일 형식이 명시되어 있는가 (.csv, .json, .npy, .h5)
[ ] 단위가 metadata 또는 docstring에 명시되어 있는가
[ ] 출처 (논문 #N, CXRO database, 자체 측정 등) 가 기록되어 있는가
[ ] 데이터 shape, dtype이 문서화되어 있는가
[ ] 결측치(NaN) 개수와 처리 방식이 명시되어 있는가
[ ] 음의 값, 비현실적 큰 값의 개수가 0 이거나 명시적으로 처리됨
[ ] 데이터 분포 시각화 (histogram, density) 가 EDA 노트북에 있는가
[ ] 시간 시리즈인 경우 sampling rate와 일관성 확인됨
[ ] 좌표 데이터인 경우 좌표계 (mask/pupil/wafer) 명시
[ ] 데이터 hash 또는 version 추적 가능
```

---

## 4. 전처리 (Preprocessing) 감사 체크리스트

전처리 파이프라인에 대해:

```
[ ] 각 단계의 입력/출력 shape, dtype, range가 명시
[ ] resampling 사용 시 보존형(integral-preserving)인가
    - 권장: scipy.integrate 기반 또는 conservative interpolation
    - 비권장: np.interp만 사용 (전하/에너지 비보존 위험)
[ ] interpolation이 phase 경계 (예: discharge → charge 전환) 를 침범하지 않는가
[ ] normalization scale 계산이 train set에서만 fit되는가 (data leakage 방지)
[ ] 단위 변환이 한 곳 (constants.py 또는 unit conversion module) 에 모여 있는가
[ ] 결측치 처리가 일관된 정책 (예: forward fill, 평균, drop) 으로 수행되는가
[ ] outlier 처리 정책이 코드와 문서에 일치하는가
[ ] 전처리 결과가 deterministic한가 (seed 고정 시)
[ ] 전처리 함수가 단위 테스트로 커버되는가
```

---

## 5. EDA (탐색적 데이터 분석) 필수 산출물 체크리스트

각 신규 데이터셋의 EDA 노트북에 다음이 모두 있어야 함:

```
[ ] 기본 통계 표 (mean, std, min, max, median, quartile)
[ ] 분포 시각화 (histogram, KDE, violin plot 중 적절한 것)
[ ] 결측치 / 이상치 요약
[ ] 변수 간 상관 (numerical 시) — pearson, spearman
[ ] 시간 시리즈 trend / seasonality (해당 시)
[ ] 좌표 의존성 시각화 (heatmap, scatter, contour) 해당 시
[ ] 단위 일관성 검증 시각화 (예: 모든 z 값이 nm 범위)
[ ] 물리적 기대 vs 실제 분포 비교 (예: absorber n,k가 CXRO와 일치)
[ ] OOD region 식별 (시뮬 입력 분포와 비교)
[ ] EDA 결론 요약 (3–5문장으로 데이터의 특성 + 주의사항)
```

---

## 6. 시뮬레이션 결과 데이터 감사 (출력 데이터 EDA)

시뮬 결과도 데이터다. 다음을 확인:

```
[ ] 출력 shape이 입력 shape으로 결정 가능한가 (silent broadcasting 없음)
[ ] dtype이 적절한가 (complex128 vs float64 vs uint8)
[ ] 결과의 단위가 명시되어 있는가 (intensity in W/m², dose in J/m²)
[ ] 음의 intensity, 100% 초과 분포가 없는가
[ ] 결과 hash가 입력 + seed로 재현 가능한가
[ ] 결과 분포가 학습/검증 분포 안에 있는가 (OOD 아닌가)
[ ] 결과 시각화 (aerial image, contrast vs dose, LWR distribution) 가 노트북에 저장
[ ] 결과 메타데이터 (run timestamp, input hash, code version, parameters) 가 함께 저장
```

---

## 7. 본 프로젝트 데이터별 특화 체크

### 7.1 absorber n, k 데이터
- [ ] @ 13.5 nm 값이 명시 (다른 파장 값과 혼동 위험)
- [ ] 출처 (CXRO database, 논문 #7 / #17, 자체 계산) 명시
- [ ] n, k 값이 물리적 범위 (n ≈ 0.92–1.05, k ≈ 0.01–0.06 for typical EUV absorbers)
- [ ] 두께 (nm) 와 함께 저장
- [ ] 재료 이름 + chemical formula 일치

### 7.2 source shape 데이터
- [ ] σ_in, σ_out (annular) 또는 polar coordinate (dipole) 명시
- [ ] pupil fill 합계가 1.0 (정규화) 또는 명시된 값
- [ ] grid 해상도가 pupil의 충분한 표현 가능 (Nyquist)
- [ ] symmetry (예: x-axis 대칭) 확인

### 7.3 마스크 패턴 데이터
- [ ] binary (0/1) 또는 amplitude (0–1, complex)
- [ ] grid 단위 (pixel size in nm) 명시
- [ ] mask coordinate vs wafer coordinate 변환 (anamorphic 4×/8×) 적용 여부
- [ ] absorber 두께 정보 (M3D simulation 시 필요)

### 7.4 웨이퍼 토폴로지 z(x, y)
- [ ] z 단위 (nm)
- [ ] z 범위가 DOF 한계 (typical ±50 nm) 안 또는 의도적으로 밖
- [ ] flat baseline (z = 0) 옵션 존재
- [ ] x, y grid가 aerial image grid와 일치

### 7.5 논문 검증 데이터
- [ ] 논문 번호 (#1–#21) + 그림/표 번호 명시
- [ ] 추출 방식 (manual digitization, web extraction) 기록
- [ ] 오차 추정 (digitization error ±N%)
- [ ] 단위 변환 trace 기록

---

## 8. 응답 규약 (Reporting Format)

모든 감사 보고서는 `audits/templates/audit_report_TEMPLATE.md` 양식을 따른다. 데이터 분석가의 핵심 응답 구조:

```
[판정]
PASS / CAUTION / MAJOR RISK / CRITICAL / UNVERIFIED

[감사 대상 데이터]
파일 경로 + 데이터 카테고리 + 버전

[데이터 품질 요약]
- shape, dtype, 단위
- 결측치, 이상치
- 분포 요약 (정규/skewed/multimodal)

[전처리 검토]
- 적용된 변환 목록
- 보존형 여부
- 데이터 누설 검토 결과

[EDA 충분성]
- 산출물 목록
- 발견된 패턴
- 부족한 분석

[리스크]
- 데이터 품질 / 전처리 / EDA 관점의 위험

[필요한 후속 작업]
- 추가 EDA / 추가 전처리 / 데이터 재수집

[수정 방향]
- 가장 작은 변경으로 판정 개선하는 방법
```

---

## 9. 본 프로젝트 핵심 감사 시나리오

### 시나리오 A: Phase 4 진입 시 absorber DB 감사
- TaBN, Ni, RuTa, PtMo, PtTe 5종 n,k 데이터 입력
- 단위, 출처, 물리적 범위 모두 확인
- EDA로 5종 비교 plot
- M3D simulation 입력으로 사용 전 PASS 받아야 함

### 시나리오 B: Phase 5 stochastic resist 입력 데이터
- Monte Carlo seed, photon density, secondary electron blur
- distribution (binomial, beta-binomial) parameter 명시
- EDA로 sample 분포 확인
- paper 1, 21과의 정성 일치 확인

### 시나리오 C: 시뮬 결과 출력 데이터 감사
- aerial image grid 보존
- contrast / NILS / LWR 메트릭 분포가 합리적
- 결과의 정확한 입력 hash + code commit 추적
- 다음 phase 입력으로 사용 가능한 형식

---

## 10. 감사자 도구 / 스킬

데이터 감사자가 사용하는 도구:

| 도구 | 용도 |
|------|------|
| `pandas` | 표 데이터 EDA |
| `numpy` | array 검증 |
| `matplotlib`, `seaborn` | 분포 시각화 |
| `pingouin` 또는 `scipy.stats` | 통계 테스트 |
| `pint` | 단위 검증 |
| `pandera` 또는 `pydantic` | 데이터 스키마 검증 |
| `dvc` 또는 `git-lfs` | 데이터 버전 관리 |
| `mlflow` 또는 `wandb` | 실험/결과 추적 |

---

## 11. 외부 참조

- 본 프로젝트 데이터 자원 정의: `../../진행계획서.md §6.3`
- 시뮬레이터 모듈 입출력 정의: `../../논문/papers/KNOWLEDGE.md §4`
- EUV 광학 상수 출처: LBNL CXRO database (https://henke.lbl.gov/optical_constants/)

---

## 12. 변경 이력

| 버전 | 날짜 | 변경 |
|------|------|------|
| v1.0 | 2026-04-25 | 초기 작성 |
