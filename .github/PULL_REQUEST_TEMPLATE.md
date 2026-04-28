## PR Title / Squash Merge Title

Required format:

- Phase work: `phase<phase>-part<NN>-<kind>: <clear summary>`
- Non-phase work: `<scope>-<kind>: <clear summary>`

Examples:

- `phase1-part02-update: add annular pupil validation`
- `phase3-part01-fix: correct wafer defocus sign`
- `repo-update: polish english paths and residue cleanup`

Allowed kinds: `add`, `update`, `fix`, `refactor`, `docs`, `test`, `audit`, `chore`.

## Change Summary

Describe the change in one short paragraph.

## Affected Phase / Module

- [ ] Phase 1 (Fourier optics)
- [ ] Phase 2 (partial coherence)
- [ ] Phase 3 (wafer focus / DOF)
- [ ] Phase 4 (mask 3D)
- [ ] Phase 5 (resist)
- [ ] Phase 6 (SMO / PMWO)
- [ ] Cross-cutting docs, audit, or repository hygiene

## Change Type

- [ ] feat: new behavior
- [ ] fix: bug fix
- [ ] docs: documentation only
- [ ] refactor: structural cleanup
- [ ] test: test change
- [ ] chore: repository maintenance

## Self-Audit

| Role | Status | Notes |
| --- | --- | --- |
| Data Analyst | PASS / CAUTION / N/A | |
| Physics | PASS / CAUTION / N/A | |
| AI / Numerical | PASS / CAUTION / N/A | |
| Simulation | PASS / CAUTION / N/A | |

## Simplification Assumptions

- New simplification, if any: `N/A`
- Documented in code comments and docs: [ ] Yes / [ ] No / [ ] N/A

## Tests

- [ ] New or changed modules have tests.
- [ ] `pytest tests/` passes locally.
- [ ] Existing tests are not regressed.

## Related Papers / Documents

- Reference papers:
- Reference docs:

## Phase Gate

- [ ] Yes - the phase-gate checklist in `PROJECT_PLAN.md` also passes.
- [ ] No - normal change.

---

@claude Please review this PR.
