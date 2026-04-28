# CI/CD and Audit Workflow

Status: active
Last updated: 2026-04-28

This workflow keeps implementation, validation, documentation, and audit status
aligned before changes are merged.

## Required Local Checks

Run the fast checks before opening a pull request:

```bash
pytest tests/
python3 -m ruff check src tests
python3 -m mypy src --ignore-missing-imports
```

Run notebook execution checks when notebooks or plotting behavior changes:

```bash
MPLBACKEND=Agg jupyter nbconvert --to notebook --execute \
  notebooks/3d_focus_stack.ipynb \
  notebooks/3d_resist_depth.ipynb \
  --output-dir /tmp/high_na_euv_nbcheck \
  --ExecutePreprocessor.timeout=120
```

## Pull Request Flow

1. Create a branch with the `codex/` prefix.
2. Use a searchable title, for example
   `repo-update: polish english paths and residue cleanup`.
3. Update README, project docs, and audit logs when behavior or navigation
   changes.
4. Push the branch and open a PR.
5. Wait for CI checks.
6. Use squash merge with the same clear title.

## Audit Flow

Substantial changes should record:

- The phase or area touched.
- Files changed.
- Validation commands.
- Known limitations.
- Whether external audit is required.

Use `audits/AUDIT_LOG.md` as the durable index.

## Repository Hygiene Gate

Before merge:

- No untracked residue should remain.
- Public path names should be English ASCII.
- Cache files and notebook checkpoints should be absent or ignored.
- README-linked paths should exist.
- Stale renamed-path references should be removed.
