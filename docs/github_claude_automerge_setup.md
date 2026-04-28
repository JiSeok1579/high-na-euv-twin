# GitHub, Claude Review, and Auto-Merge Setup

Status: active
Last updated: 2026-04-28

This guide documents the repository automation model.

## Required Account

Use the GitHub account `JiSeok1579` for commits, pushes, pull requests, and
merges. Do not use old `jiseokyang777` credentials.

Recommended local identity:

```bash
git config user.name "JiSeok1579"
git config user.email "didwltjr1579@naver.com"
gh auth status
```

## Branch and Title Rules

Use `codex/` branches for agent work.

PR and squash merge titles must use:

```text
phase<phase>-part<NN>-<kind>: <clear summary>
<scope>-<kind>: <clear summary>
```

Examples:

```text
phase5-part04-update: add resist depth validation
repo-update: polish english paths and residue cleanup
```

## Required GitHub Settings

Recommended repository settings:

- Squash merge enabled.
- Merge commits disabled unless explicitly needed.
- Delete branch on merge enabled.
- Branch protection on `main`.
- Required status checks for tests, lint, type check, and PR title validation.
- Auto-merge enabled.

The helper script can apply the expected labels and repository settings:

```bash
scripts/configure_github_automerge.sh
```

## Claude Review

Claude review should follow `REVIEWER_DIRECTIVE.md`.

Review focus:

- Physical plausibility and model limits.
- Numerical stability and sampling.
- Software architecture and tests.
- Documentation-code consistency.
- Audit log honesty.

## Auto-Merge Flow

1. Commit local changes with a clear English message.
2. Push the `codex/` branch.
3. Open a PR with the same searchable title.
4. Add the `auto-merge` label when ready.
5. Wait for all required checks.
6. Use squash auto-merge with the same clear subject.

Example:

```bash
gh pr create --title "repo-update: polish english paths and residue cleanup" \
  --body "Repository polish, path normalization, and documentation sync."
gh pr merge --squash --auto \
  --subject "repo-update: polish english paths and residue cleanup"
```

## Verification

Before merge, verify:

```bash
pytest tests/
git ls-files --others --exclude-standard
git -c core.quotePath=false ls-files | perl -ne 'print if /[^\x00-\x7F]/'
```

The first command should pass, the second should be empty, and the third should
print no tracked non-ASCII paths.
