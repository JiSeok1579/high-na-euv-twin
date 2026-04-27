# Audit System

> Gated review framework for the High-NA EUV Lithography Simulator.
> Code changes should pass the relevant review roles before they advance to
> the next phase or merge to `main`.

## 1. Why This Exists

This project builds a research and education simulator from 21 reference papers
and an internal physics handbook. Without a review gate, the code can become
visually plausible while still being physically or numerically wrong.

Common failure modes:

- Correct diffraction equations with inconsistent coordinate units.
- Working FFT code that violates Nyquist sampling.
- Attractive contrast plots that break conservation or normalization checks.
- ML or optimization routines that converge in a physically invalid regime.

The audit system blocks these failures before they land on `main` by checking
the work from four complementary roles.

## 2. Review Roles

| Folder | Role | Primary focus |
|---|---|---|
| `01_data_analyst/` | Data analyst | Input data quality, preprocessing, and exploratory analysis. |
| `02_physics/` | Physics reviewer | Conservation laws, boundary/initial conditions, coordinates, signs, and causality. |
| `03_ai_numerical/` | AI and numerical reviewer | FFT sampling, nondimensionalization, stability, gradients, and ML validity. |
| `04_simulation/` | Simulation reviewer | Phase gates, unit tests, ablations, result interpretation, and simplification rationale. |

Each role folder contains `INSTRUCTIONS.md` and a `reports/` directory.

## 3. Folder Structure

```text
audits/
├── README.md
├── 00_CI_CD_WORKFLOW.md
├── AUDIT_LOG.md
│
├── 01_data_analyst/
│   ├── INSTRUCTIONS.md
│   └── reports/
│
├── 02_physics/
│   ├── INSTRUCTIONS.md
│   └── reports/
│
├── 03_ai_numerical/
│   ├── INSTRUCTIONS.md
│   └── reports/
│
├── 04_simulation/
│   ├── INSTRUCTIONS.md
│   └── reports/
│
└── templates/
    ├── audit_report_TEMPLATE.md
    └── change_request_TEMPLATE.md
```

## 4. CI/CD Flow

```text
[code change]
    -> [pytest and static checks pass]
    -> [relevant role reviews are recorded]
    -> [PASS, or CAUTION with mitigation]
    -> [phase gate approval]
    -> [merge to main or advance to the next phase]
```

See `00_CI_CD_WORKFLOW.md` for the full flow.

## 5. Verdict Levels

| Verdict | Meaning | Next action |
|---|---|---|
| **PASS** | Current evidence is acceptable. | Proceed. |
| **CAUTION** | Plausible, but important evidence is incomplete. | Proceed conditionally and create mitigation tasks. |
| **MAJOR RISK** | Work may continue, but the core risk is high. | Review the decision before merging. |
| **PHYSICAL VIOLATION / CRITICAL** | The result is clearly wrong. | Block, fix, and re-audit. |
| **UNVERIFIED** | Insufficient information. | Gather evidence and re-audit. |

Phase gates pass only when every relevant review is `PASS` or `CAUTION` with a
tracked mitigation task. One or more `MAJOR RISK` or `PHYSICAL VIOLATION`
verdicts block progress.

## 6. Phase Coverage

| Phase | Data | Physics | AI/Numerical | Simulation |
|---|---|---|---|---|
| Phase 1, Fourier optics MVP | Optional | Recommended | Recommended | Basic |
| Phase 2, Partial coherence | Basic | Recommended | Basic | Basic |
| Phase 3, Wafer topography | Basic | Recommended | Basic | Basic |
| Phase 4, Mask 3D | Recommended | Required | Recommended | Recommended |
| Phase 5 L0-L1, Resist MVP/blur | Basic | Recommended | Basic | Basic |
| Phase 5 L2-L3, Depth/stochastic | Recommended | Recommended | Recommended | Recommended |
| Phase 6, SMO/PMWO | Basic | Recommended | Required | Recommended |

## 7. Report Naming

```text
audits/<role_folder>/reports/YYYY-MM-DD_<phase>_<short-topic>_<verdict>.md
```

Examples:

```text
audits/02_physics/reports/2026-05-01_phase1_anamorphic_coordinate_PASS.md
audits/03_ai_numerical/reports/2026-05-15_phase4_FFT_sampling_CAUTION.md
audits/04_simulation/reports/2026-06-01_phase5_stochastic_unit_test_MAJOR_RISK.md
```

## 8. Operating Steps

1. Read the role-specific `INSTRUCTIONS.md`.
2. Write the review report from `templates/audit_report_TEMPLATE.md`.
3. Add a one-line entry to `AUDIT_LOG.md`.
4. Use `00_CI_CD_WORKFLOW.md` at phase-gate time.

## 9. Reference Documents

- Project entry point: `../PROJECT_OVERVIEW.md`
- Project execution plan in the repository root
- Physics handbook: `../high_na_euv_physics_considerations.md`
- Deep research report document in the repository root
- Integrated paper knowledge base under the reference-paper folder

All audit verdicts should be grounded in the physics, formulas, simplifications,
and metrics defined by those documents.
