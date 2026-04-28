# Reviewer Directive - External Audit Workflow

Version: v2.2
Last updated: 2026-04-28
Status: active

This document defines how external review is performed for this repository.
The purpose is not to block study-grade progress with industrial-grade demands.
The purpose is to keep the simulator honest, reproducible, and useful for the
next phase of work.

## 1. Role Boundary

The implementation agent owns:

- Code changes.
- Unit tests.
- Local validation.
- Phase sequencing.
- Simplification choices.
- Pull request creation and merge hygiene.

The external reviewer owns:

- Independent review of code, notebooks, and documentation.
- Identification of physical, numerical, software, and audit risks.
- Consolidated recommendations for the next implementation step.
- Verification that documents match implemented behavior.

The reviewer does not take over implementation ownership.

## 2. Study-Grade Severity Policy

This is a study and visualization simulator. The reviewer should keep strict
severity for issues that break learning or create false confidence, and lower
severity for industrial calibration gaps that the project does not claim to
solve.

Keep as P0/P1:

- Failing tests or unexecuted claimed validation.
- Incorrect sign conventions for defocus, anamorphic axes, CRA, or phase.
- Unit confusion between m, nm, radians, waves, dose, or pixel coordinates.
- README, notebooks, and code disagreeing about what is implemented.
- Audit log entries claiming work that is not actually present.
- 3D plots presented as physical validation when the underlying quantity is a
  sparse sweep or replicated scalar.

Do not raise as P0 for study-grade work:

- Missing industrial ground truth.
- Missing strict mypy mode.
- Missing full RCWA / FDTD mask EM.
- Missing full resist chemistry calibration.
- Small code duplication that does not change behavior or interpretation.

## 3. Required Review Roles

Every substantial audit should cover four perspectives.

| Role | Focus |
| --- | --- |
| EUV / Physics | Physical plausibility, units, sign conventions, model limits, and paper alignment. |
| AI / Numerical | FFT sampling, finite values, convergence, stochastic reproducibility, and optimization behavior. |
| Software | Architecture, public APIs, maintainability, test coverage, CI, and repository hygiene. |
| Data Scientist | Integrates the three opinions, ranks risks, tracks trend metrics, and recommends the next step. |

## 4. Two-Stage Audit Output

For external reports, use this folder shape:

```text
audits/external/reports/EXT-AUD-<date>-<id>_<topic>/
├── A1_euv_opinion.md
├── A2_ai_opinion.md
├── A3_software_opinion.md
└── 00_FINAL_audit.md
```

Stage 1 writes the three specialist opinions. Stage 2 writes the integrated
final audit report. The final report should clearly state:

- Overall result: PASS, PASS WITH RISKS, CONDITIONAL FAIL, or FAIL.
- P0/P1/P2/P3 issues.
- Evidence files and commands.
- Whether documentation matches code.
- Recommended next implementation step.

## 5. Notebook Review Rules

Notebook plots must be reviewed for interpretation risk.

Required validation-first rules:

- Focus validation starts from a 2D x-defocus heatmap and a 2D contrast curve.
- Resist-depth validation starts from a 2D x-depth dose heatmap.
- 3D surfaces are demo-only unless they represent a genuinely x/y/z-resolved
  physical field with adequate sampling.
- Each notebook prints shape, min/max, finite checks, and sample counts.
- The notebook title or nearby markdown must state model limits such as
  "Beer-Lambert attenuation only" or "demo-only 3D view".

## 6. Documentation Review Rules

The reviewer must check that:

- README commands work or are clearly marked as expected commands.
- `PROJECT_OVERVIEW.md` and `PROJECT_PLAN.md` reflect current implementation.
- Notebook descriptions in README match notebook code.
- Renamed paths are reflected across docs.
- New archive or instruction documents have a clear status.
- Public path names are English ASCII.

## 7. Pull Request Review Rules

PR titles and squash merge titles must be direct and searchable.

Required format:

- Phase work: `phase<phase>-part<NN>-<kind>: <clear summary>`
- Non-phase work: `<scope>-<kind>: <clear summary>`

Examples:

- `phase3-part02-update: add dof contrast metrics`
- `phase5-part04-fix: clarify beer-lambert depth plots`
- `repo-update: polish english paths and residue cleanup`

## 8. Audit Log Rules

`audits/AUDIT_LOG.md` is the durable index. Each audit-relevant change should
include:

- Date.
- Phase or area.
- Change type.
- Result.
- Evidence file or command.
- Remaining follow-up, if any.

Do not mark a mitigation closed unless the file change and validation command
exist in the repository.

## 9. Reviewer Output Style

The final audit should be concise and actionable:

1. Findings first, ordered by severity.
2. File and line references where possible.
3. Clear pass/fail statement.
4. Concrete next-step recommendation.
5. No overclaiming beyond the evidence.

## 10. Current Standing Guidance

The repository should remain English-first for public paths, README navigation,
templates, and active project documents. Historical audit evidence may remain in
archived reports, but current instructions and entry points should stay aligned
with the implemented validation-first 2D workflow.
