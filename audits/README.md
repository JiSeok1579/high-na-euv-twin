# 감사 시스템 (Audit System)

> High-NA EUV Simulator 프로젝트의 **gated review** 체계.
> 모든 코드 진행은 4개 역할의 감사를 통과해야 다음 Phase로 진행할 수 있다.

---

## 1. 왜 감사 시스템인가

본 프로젝트는 학술 논문 21편과 자체 물리 핸드북·심층 보고서에 기반해 시뮬레이터를 만드는 연구 프로젝트다. 다음 위험을 자동으로 막을 장치가 없다면 코드는 빠르게 "그럴듯해 보이지만 물리적으로 잘못된" 방향으로 흐른다.

- 회절식이 맞아도 좌표계 단위가 틀린 경우
- FFT가 작동해도 Nyquist를 위반한 경우
- contrast가 그래프로 멋져 보여도 보존 법칙이 깨진 경우
- ML 모델이 수렴해도 PDE residual이 비물리적인 영역에서 작동하는 경우

본 감사 시스템은 이런 실패를 **코드가 main에 들어가기 전에** 4개의 다른 시각으로 검증해 차단한다.

---

## 2. 4개 감사 역할

| 폴더 | 역할 | 주 감사 대상 |
|------|------|-------------|
| `01_data_analyst/` | **데이터 분석가** | 입력 데이터 품질, 전처리, EDA 결과물 |
| `02_physics/` | **물리학자 (상시 검증자)** | 보존법칙, BC/IC, 좌표계, 부호 규약, 인과성 |
| `03_ai_numerical/` | **AI / 수치 분석가** | FFT 샘플링, 무차원화, 수치 안정성, gradient, ML model validity |
| `04_simulation/` | **시뮬레이션 검증자** | Phase entry/exit criteria, 단위 테스트, ablation, 결과 해석, 단순화 정당성 |

각 폴더 안에 **INSTRUCTIONS.md** (지시서) + **reports/** (감사 보고서 보관) 가 있다.

---

## 3. 폴더 구조

```
audits/
├── README.md                       ← 본 문서
├── 00_CI_CD_WORKFLOW.md            ← gated review 워크플로
├── AUDIT_LOG.md                    ← 모든 감사 이력 기록
│
├── 01_data_analyst/
│   ├── INSTRUCTIONS.md             ← 데이터 분석가 지시서
│   └── reports/                    ← 감사 보고서 저장
│
├── 02_physics/
│   ├── INSTRUCTIONS.md             ← 물리학자 지시서 (상시 물리 검증자)
│   └── reports/
│
├── 03_ai_numerical/
│   ├── INSTRUCTIONS.md             ← AI/수치 지시서
│   └── reports/
│
├── 04_simulation/
│   ├── INSTRUCTIONS.md             ← 시뮬레이션 검증자 지시서
│   └── reports/
│
└── templates/
    ├── audit_report_TEMPLATE.md    ← 감사 보고서 양식
    └── change_request_TEMPLATE.md  ← 변경 요청 양식
```

---

## 4. CI/CD 워크플로 한 줄 요약

```
[코드 변경]
    → [pytest 자동 테스트 통과]
    → [4개 역할 감사 보고서 작성]
    → [모두 PASS / 일부 CAUTION 허용]
    → [Phase Gate 승인]
    → [main 머지 또는 다음 Phase 진행]
```

전체 플로는 `00_CI_CD_WORKFLOW.md` 참고.

---

## 5. 감사 판정 등급 (5단계)

모든 감사 보고서는 다음 중 하나로 판정한다.

| 등급 | 의미 | 다음 행동 |
|------|------|-----------|
| **PASS** | 현재 증거로 타당 | 진행 |
| **CAUTION** | 그럴듯하나 결정적 검증 부족 | 조건부 진행 + 후속 검증 task 생성 |
| **MAJOR RISK** | 진행은 가능하나 핵심 리스크 큼 | 의사결정 회의 필요 |
| **PHYSICAL VIOLATION / CRITICAL** | 명백히 잘못됨 | **차단 — 수정 후 재감사** |
| **UNVERIFIED** | 정보 부족으로 판정 불가 | 정보 확보 후 재감사 |

**Phase Gate 통과 조건**: 모든 감사가 PASS 또는 CAUTION (with mitigation task) 이어야 한다.
**진행 차단**: 1개 이상의 감사가 MAJOR RISK 또는 PHYSICAL VIOLATION이면 차단.

---

## 6. 어느 감사가 어느 Phase에 적용되는가

| Phase | 데이터 | 물리 | AI/수치 | 시뮬레이션 |
|-------|--------|------|---------|-----------|
| Phase 1 (Fourier optics MVP) | △ | ★★ | ★★ | ★ |
| Phase 2 (Partial coherence) | ★ | ★★ | ★ | ★ |
| Phase 3 (Wafer topography) | ★ | ★★ | ★ | ★ |
| Phase 4 (Mask 3D) | ★★ (absorber DB) | ★★★ | ★★ | ★★ |
| Phase 5 L0–L1 (Resist MVP/blur) | ★ | ★★ | ★ | ★ |
| Phase 5 L2–L3 (Depth/Stochastic) | ★★ | ★★ | ★★ (MC sampling) | ★★ |
| Phase 6 (SMO/PMWO) | ★ | ★★ | ★★★ (gradient) | ★★ |

★★★ 필수, ★★ 권장, ★ 옵션, △ 해당 없음

---

## 7. 감사 보고서 파일명 규약

```
audits/<role_folder>/reports/YYYY-MM-DD_<phase>_<short-topic>_<verdict>.md

예:
audits/02_physics/reports/2026-05-01_phase1_anamorphic_coordinate_PASS.md
audits/03_ai_numerical/reports/2026-05-15_phase4_FFT_sampling_CAUTION.md
audits/04_simulation/reports/2026-06-01_phase5_stochastic_unit_test_MAJOR_RISK.md
```

---

## 8. 다음 단계

1. **첫 감사 시작 시** — 해당 역할의 `INSTRUCTIONS.md` 정독
2. **감사 보고서 작성** — `templates/audit_report_TEMPLATE.md` 복사 후 작성
3. **AUDIT_LOG.md 업데이트** — 한 줄 요약 추가
4. **Phase Gate 시점** — `00_CI_CD_WORKFLOW.md`의 게이트 체크리스트 사용

---

## 9. 외부 참조 문서

- 프로젝트 진입점: `../PROJECT_OVERVIEW.md`
- 진행계획서 (Phase 정의): `../진행계획서.md`
- 물리 핸드북 (감사 기준): `../high_na_euv_physics_considerations.md`
- 심층 연구 보고서: `../고해상도 ... .docx`
- 논문 통합 학습: `../논문/papers/KNOWLEDGE.md`

본 감사 시스템의 모든 판정은 위 문서에서 정의된 물리·수식·메트릭을 기준으로 한다.
