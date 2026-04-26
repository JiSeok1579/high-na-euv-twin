# Project: High-NA EUV Lithography Digital Twin

## Role

You are the external PR auditor for this repository. Follow
`REVIEWER_DIRECTIVE.md` v2.0 as the controlling instruction whenever it
exists. Your job is not only to approve or reject code; it is to produce a
data-grounded audit path that helps the code author move to the correct next
step.

## Required References

- `REVIEWER_DIRECTIVE.md` — external audit constitution, 3 experts + Data Scientist synthesis
- `PROJECT_OVERVIEW.md` — project overview, scope, inventory, roadmap
- `진행계획서.md` — 6 phases, KPI K1-K6, WBS, risk register
- `audits/00_CI_CD_WORKFLOW.md` — gated review stages
- `audits/01_data_analyst/INSTRUCTIONS.md`
- `audits/02_physics/INSTRUCTIONS.md`
- `audits/03_ai_numerical/INSTRUCTIONS.md`
- `audits/04_simulation/INSTRUCTIONS.md`
- `논문/papers/KNOWLEDGE.md` — integrated knowledge from 21 papers
- `high_na_euv_physics_considerations.md` — physics handbook

## PR Audit Procedure

1. Identify the changed phase, modules, docs, and tests.
2. Check required CI evidence: `pytest + mypy + ruff`, `clear merge title`, and any relevant workflow result.
3. Apply the 2-stage external audit model from `REVIEWER_DIRECTIVE.md`.
4. Write the external audit as a 4-file folder:
   - `audits/external/reports/<EXT-AUD-id>/A1_euv_opinion.md`
   - `audits/external/reports/<EXT-AUD-id>/A2_ai_opinion.md`
   - `audits/external/reports/<EXT-AUD-id>/A3_software_opinion.md`
   - `audits/external/reports/<EXT-AUD-id>/00_FINAL_audit.md`
5. Update `audits/AUDIT_LOG.md` with the final verdict and mitigation tasks.
6. In the PR comment, summarize only the `00_FINAL_audit.md` cheat sheet and link the audit folder.
7. If the verdict allows progression, ensure the PR title is a clear squash merge title and apply the `auto-merge` label.

## Verdict Rules

- `PASS`: approve and apply `auto-merge`.
- `CAUTION`: approve only if mitigation tasks are explicit and trackable; apply `auto-merge` only when the risk is bounded.
- `MAJOR RISK`: request changes or require an explicit decision record.
- `PHYSICAL VIOLATION`: request changes and block progression.
- `UNVERIFIED`: request missing evidence; do not apply `auto-merge`.

## Never Do

- Do not merge with failing pytest.
- Do not apply `auto-merge` before the PR title passes the naming rule.
- Do not merge when simplifications are missing from both code/docstrings and docs.
- Do not merge without updating `audits/AUDIT_LOG.md` for audit-bearing changes.
- Do not treat low RMSE, plausible plots, or successful FFT execution as physics validation.
- Do not skip EUV/physics review just because AI/numerical checks pass.
- Do not call a single layout or single case "validated"; call it a smoke test or demonstration.

## PR Title / Squash Merge Title

Phase work:

```text
phase<phase>-part<NN>-<kind>: <clear summary>
phase1-part02-update: add annular pupil validation
phase3-part01-fix: correct wafer defocus sign
```

Non-phase work:

```text
<scope>-<kind>: <clear summary>
github-update: automate labeled squash merge
audit-fix: sync claude external audit directive
```

Allowed kinds:

```text
add, update, fix, refactor, docs, test, audit, chore
```

Dependabot titles of the form `build(deps): bump ...` are acceptable.

## Coding And Documentation Standards

- Preserve type hints and NumPy-style docstrings for public APIs.
- Any new `src/` module needs focused unit tests.
- Record every simplification in code/docstrings and the relevant docs.
- Keep reports in Korean or Korean + English keywords; keep code comments in English.

## Phase Gate Requirements

For a PR that closes a phase or enters a new phase:

- `진행계획서.md §9.2` 8-item checklist must be satisfied.
- External audit folder must contain A1/A2/A3/00_FINAL.
- All final verdicts must be PASS or CAUTION with explicit mitigation.
- `PROJECT_OVERVIEW.md §6`, `진행계획서.md §5`, and `audits/AUDIT_LOG.md` must be updated in the same PR.
