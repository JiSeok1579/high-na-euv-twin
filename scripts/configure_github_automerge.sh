#!/usr/bin/env bash
set -euo pipefail

REPO="${1:-${GITHUB_REPOSITORY:-JiSeok1579/high-na-euv-twin}}"
BRANCH="${BRANCH:-main}"
AUTO_MERGE_LABEL="${AUTO_MERGE_LABEL:-auto-merge}"
REQUIRED_CONTEXTS_JSON="${REQUIRED_CONTEXTS_JSON:-[\"pytest + mypy + ruff\",\"clear merge title\"]}"
REQUIRED_APPROVING_REVIEW_COUNT="${REQUIRED_APPROVING_REVIEW_COUNT:-0}"
REQUIRE_CODE_OWNER_REVIEWS="${REQUIRE_CODE_OWNER_REVIEWS:-false}"

case "${REQUIRE_CODE_OWNER_REVIEWS}" in
  true|false) ;;
  *)
    echo "REQUIRE_CODE_OWNER_REVIEWS must be true or false." >&2
    exit 1
    ;;
esac

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is required." >&2
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "gh is not authenticated. Run: gh auth login" >&2
  exit 1
fi

branch_exists=true
if ! gh api "repos/${REPO}/branches/${BRANCH}" >/dev/null 2>&1; then
  branch_exists=false
fi

echo "Configuring repository settings for ${REPO}..."
gh api --method PATCH "repos/${REPO}" \
  -F allow_auto_merge=true \
  -F delete_branch_on_merge=true \
  -F allow_squash_merge=true \
  -F allow_merge_commit=false \
  -F allow_rebase_merge=false >/dev/null

ensure_label() {
  local name="$1"
  local color="$2"
  local description="$3"

  gh label create "${name}" \
    --repo "${REPO}" \
    --color "${color}" \
    --description "${description}" \
    --force >/dev/null
}

echo "Ensuring workflow labels..."
ensure_label "${AUTO_MERGE_LABEL}" "0e8a16" "Enable full automatic squash merge after required checks pass"
ensure_label "blocked" "d73a4a" "Blocked by failing checks, unresolved review, or audit risk"
ensure_label "audit" "5319e7" "Requires or updates the 4-role audit workflow"
ensure_label "needs-title-fix" "fbca04" "PR title must be rewritten before it can become a squash merge title"
ensure_label "dependencies" "0366d6" "Pull requests that update dependencies"
ensure_label "python" "3572A5" "Python dependency or runtime update"
ensure_label "github_actions" "000000" "GitHub Actions workflow dependency update"

if [ "${branch_exists}" = "false" ]; then
  echo "Branch '${BRANCH}' does not exist on ${REPO} yet."
  echo "Repository settings and labels were applied."
  echo "Push the initial '${BRANCH}' branch, then rerun this script to apply branch protection."
  exit 0
fi

protection_json="$(mktemp)"
trap 'rm -f "${protection_json}"' EXIT

cat >"${protection_json}" <<JSON
{
  "required_status_checks": {
    "strict": true,
    "contexts": ${REQUIRED_CONTEXTS_JSON}
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": ${REQUIRE_CODE_OWNER_REVIEWS},
    "required_approving_review_count": ${REQUIRED_APPROVING_REVIEW_COUNT}
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
JSON

echo "Applying branch protection to ${BRANCH}..."
gh api --method PUT "repos/${REPO}/branches/${BRANCH}/protection" \
  --input "${protection_json}" >/dev/null

echo "Done."
echo "Required status contexts: ${REQUIRED_CONTEXTS_JSON}"
echo "Required approving review count: ${REQUIRED_APPROVING_REVIEW_COUNT}"
echo "Require code owner reviews: ${REQUIRE_CODE_OWNER_REVIEWS}"
echo "Auto-merge is label-gated by: ${AUTO_MERGE_LABEL}"
