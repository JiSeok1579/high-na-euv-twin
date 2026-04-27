# GitHub + Claude Code 자동 머지 셋업 가이드

> 대상 리포지터리: **https://github.com/JiSeok1579/high-na-euv-sim**
> 목적: 코드 변경 → CI 통과 → Claude Code 검토 + 4-역할 감사 → 자동 머지 → main 진행
> 본 문서는 한 번 따라 하면 끝까지 작동하도록 작성된 셋업 매뉴얼이다.
> 작성일: 2026-04-26

---

## 0. 무엇을 만드는가

```
[로컬 코드 push 또는 @claude 요청]
            ↓
   ┌────────────────────────┐
   │ GitHub Actions: CI     │ ← pytest + mypy + ruff + coverage
   └─────────┬──────────────┘
             ▼
   ┌────────────────────────┐
   │ GitHub Actions: Claude │ ← claude-code-action 이 PR 코드 검토
   │   - 4-역할 감사 체크    │   audits/INSTRUCTIONS.md 기반 자체 감사
   │   - audit 보고서 첨부   │   audits/*/reports/ 에 .md 작성
   │   - approve or request │
   └─────────┬──────────────┘
             ▼
   ┌────────────────────────┐
   │ Branch protection      │ ← required check 통과 시
   │ + Auto-merge           │   auto-merge label이면 squash merge까지 자동 진행
   └─────────┬──────────────┘
             ▼
        [main 머지]
```

**최종 결과**: 개발자가 명명 규칙에 맞는 PR을 열거나 `@claude` 멘션만 하면 → CI + 감사 + `auto-merge` label → squash merge까지 자동 진행.

---

## 1. 사전 준비

### 1.1 필요한 계정 / 액세스

- [ ] GitHub 계정 (`JiSeok1579`) 에 리포지터리 admin 권한
- [ ] Anthropic Console 계정 (https://console.anthropic.com)
- [ ] 로컬 git 설치 + GitHub CLI (`gh`) 권장

### 1.2 로컬 환경 점검

```bash
git --version          # 2.30+
gh --version           # 2.30+ (옵션이지만 강력 추천)
python --version       # 3.11+
```

### 1.3 GitHub CLI 로그인 (옵션)

```bash
gh auth login
# GitHub.com → HTTPS → Y → Login with web browser
```

---

## 2. STEP 1 — Anthropic API key 발급 + GitHub Secret 등록

### 2.1 API key 발급

1. https://console.anthropic.com 로그인
2. 좌측 메뉴 **API Keys** → **Create Key**
3. 이름: `github-actions-high-na-euv-sim`
4. 생성된 키를 **임시로 복사** (한 번만 보임, `sk-ant-api03-...`)

### 2.2 GitHub Secret 등록

웹 UI:
1. https://github.com/JiSeok1579/high-na-euv-sim/settings/secrets/actions
2. **New repository secret**
3. Name: `ANTHROPIC_API_KEY`
4. Secret: 위에서 복사한 값
5. **Add secret**

CLI 대안:
```bash
gh secret set ANTHROPIC_API_KEY \
  --repo JiSeok1579/high-na-euv-sim \
  --body "sk-ant-api03-..."
```

### 2.3 (옵션) Workspace folder 권한 secret 추가

Claude Code가 PR 머지·라벨링·comment 작성을 자동으로 하려면 별도 토큰이 필요할 수 있다. 첫 셋업에는 기본 `GITHUB_TOKEN` 으로 충분.

### 2.4 (옵션) Workflow 파일 변경 PR까지 자동 머지

GitHub Actions workflow 파일(`.github/workflows/*.yml`)을 바꾸는 PR은 기본 `GITHUB_TOKEN`으로 merge가 차단될 수 있다. 예: Dependabot이 `actions/checkout` 또는 `actions/setup-python`을 업데이트하는 PR.

이 PR까지 완전 자동 머지하려면 `workflow` scope가 포함된 fine-grained 또는 classic PAT를 만들고 repository secret으로 등록한다.

```bash
gh secret set AUTOMERGE_TOKEN \
  --repo JiSeok1579/high-na-euv-sim \
  --body "<token-with-workflow-scope>"
```

`AUTOMERGE_TOKEN`이 없으면 일반 코드/문서/파이썬 의존성 자동 머지는 유지되고, workflow 변경 PR은 수동 확인 대상으로 남긴다.

---

## 3. STEP 2 — GitHub Actions 워크플로 파일 생성

### 3.1 디렉토리 준비

로컬에서:
```bash
cd "/Users/yangjiseok/Desktop/High-NA EUV Lithography Simulator"
mkdir -p .github/workflows
```

### 3.2 CI 워크플로 — `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  test:
    name: pytest + mypy + ruff
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
          cache-dependency-path: requirements-dev.txt

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt

      - name: Lint with ruff
        run: ruff check src tests

      - name: Type check with mypy
        run: mypy src --ignore-missing-imports
        continue-on-error: true   # 초기에는 경고만, 점차 강제로 전환

      - name: Run pytest
        run: pytest tests/ -v --tb=short --cov=src --cov-report=term-missing --cov-report=xml

      - name: Upload coverage report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: coverage.xml
          retention-days: 14
```

### 3.3 Claude Code 워크플로 — `.github/workflows/claude.yml`

```yaml
name: Claude Code Review

on:
  # 1) PR 열림 / 새 commit push
  pull_request:
    types: [opened, synchronize, reopened]
  # 2) @claude 멘션
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
  issues:
    types: [opened, assigned]

jobs:
  claude:
    if: |
      (github.actor != 'dependabot[bot]') &&
      ((github.event_name == 'pull_request') ||
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'pull_request_review_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'issues' && (contains(github.event.issue.body, '@claude') || contains(github.event.issue.title, '@claude'))))

    runs-on: ubuntu-latest
    timeout-minutes: 30
    env:
      HAS_ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY != '' }}

    permissions:
      contents: write          # 코드 push, 머지
      pull-requests: write     # PR 코멘트, approve, merge
      issues: write            # 이슈 코멘트
      id-token: write          # OIDC (필요 시)

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run Claude Code
        if: env.HAS_ANTHROPIC_API_KEY == 'true'
        uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          # 본 프로젝트 전용 시스템 프롬프트
          claude_args: |
            --append-system-prompt "$(cat .github/CLAUDE.md)"

      - name: Skip Claude Code when secret is missing
        if: env.HAS_ANTHROPIC_API_KEY != 'true'
        run: |
          echo "ANTHROPIC_API_KEY is not configured; skipping Claude Code Review."
```

### 3.4 PR title 검증 워크플로 — `.github/workflows/pr-title.yml`

PR title은 squash merge title로 그대로 사용된다. Phase가 나뉜 작업은 Phase 번호, part 번호, 작업 종류, 명확한 요약을 포함해야 한다.

```yaml
name: PR Naming

on:
  pull_request:
    types: [opened, edited, synchronize, reopened, ready_for_review]

permissions:
  contents: read

jobs:
  clear-merge-title:
    name: clear merge title
    runs-on: ubuntu-latest
    steps:
      - name: Validate PR title used as squash merge title
        env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: |
          set -euo pipefail

          phase_pattern='^phase[0-9]+-part[0-9]{2}-(add|update|fix|refactor|docs|test|audit|chore): .{12,}$'
          scope_pattern='^[a-z0-9][a-z0-9-]*-(add|update|fix|refactor|docs|test|audit|chore): .{12,}$'
          dependabot_pattern='^build\(deps\): bump .{12,}$'

          if [[ "${PR_TITLE}" =~ ${phase_pattern} || "${PR_TITLE}" =~ ${scope_pattern} || "${PR_TITLE}" =~ ${dependabot_pattern} ]]; then
            echo "Clear merge title accepted: ${PR_TITLE}"
            exit 0
          fi

          cat <<'EOF'
          PR title will become the squash merge title and must be clear.

          Phase work:
            phase<phase>-part<NN>-<kind>: <clear summary>
            phase1-part02-update: add annular pupil validation
            phase3-part01-fix: correct wafer defocus sign

          Non-phase work:
            <scope>-<kind>: <clear summary>
            github-update: automate labeled squash merge
            docs-fix: clarify auto merge setup guide
            build(deps): bump actions/checkout from 4 to 6

          Allowed kinds:
            add, update, fix, refactor, docs, test, audit, chore
          EOF
          exit 1
```

### 3.5 Auto-merge 워크플로 — `.github/workflows/auto-merge.yml`

`auto-merge` 라벨이 붙은 PR에만 GitHub native auto-merge를 활성화한다. 실제 머지는 GitHub branch protection이 required checks 통과를 확인한 뒤 수행한다. squash merge 제목은 PR title로 고정한다.

```yaml
name: Auto-Merge

on:
  pull_request_target:
    types: [opened, edited, reopened, synchronize, ready_for_review, labeled]
  pull_request_review:
    types: [submitted]
  workflow_dispatch:
    inputs:
      pr_number:
        description: "Pull request number to enable native auto-merge for"
        required: true
        type: number

jobs:
  enable-auto-merge:
    name: Enable native auto-merge
    runs-on: ubuntu-latest
    if: github.event_name != 'pull_request_review' || github.event.review.state == 'approved'
    permissions:
      contents: write
      pull-requests: write
      issues: read
    concurrency:
      group: auto-merge-${{ github.event.pull_request.number || inputs.pr_number }}
      cancel-in-progress: false
    steps:
      - name: Enable auto-merge for labeled PR
        env:
          GH_TOKEN: ${{ secrets.AUTOMERGE_TOKEN || github.token }}
          AUTO_MERGE_LABEL: auto-merge
          PR_NUMBER: ${{ github.event.pull_request.number || inputs.pr_number }}
        run: |
          set -euo pipefail

          if [ -z "${PR_NUMBER}" ]; then
            echo "No PR number was provided by the event."
            exit 1
          fi

          state="$(gh pr view "${PR_NUMBER}" --repo "${GITHUB_REPOSITORY}" --json state --jq '.state')"
          if [ "${state}" != "OPEN" ]; then
            echo "PR #${PR_NUMBER} is ${state}; skipping."
            exit 0
          fi

          draft="$(gh pr view "${PR_NUMBER}" --repo "${GITHUB_REPOSITORY}" --json isDraft --jq '.isDraft')"
          if [ "${draft}" = "true" ]; then
            echo "PR #${PR_NUMBER} is a draft; skipping."
            exit 0
          fi

          has_label="$(
            gh pr view "${PR_NUMBER}" --repo "${GITHUB_REPOSITORY}" --json labels --jq '.labels[].name' \
              | grep -Fx "${AUTO_MERGE_LABEL}" || true
          )"
          if [ -z "${has_label}" ]; then
            echo "PR #${PR_NUMBER} does not have the '${AUTO_MERGE_LABEL}' label; skipping."
            exit 0
          fi

          pr_title="$(gh pr view "${PR_NUMBER}" --repo "${GITHUB_REPOSITORY}" --json title --jq '.title')"
          phase_pattern='^phase[0-9]+-part[0-9]{2}-(add|update|fix|refactor|docs|test|audit|chore): .{12,}$'
          scope_pattern='^[a-z0-9][a-z0-9-]*-(add|update|fix|refactor|docs|test|audit|chore): .{12,}$'
          dependabot_pattern='^build\(deps\): bump .{12,}$'
          if [[ ! "${pr_title}" =~ ${phase_pattern} && ! "${pr_title}" =~ ${scope_pattern} && ! "${pr_title}" =~ ${dependabot_pattern} ]]; then
            echo "PR title is not a clear merge title: ${pr_title}"
            echo "Use: phase<phase>-part<NN>-<kind>: <clear summary>"
            echo "Or:  <scope>-<kind>: <clear summary>"
            exit 1
          fi

          auto_merge_subject="$(gh pr view "${PR_NUMBER}" --repo "${GITHUB_REPOSITORY}" --json autoMergeRequest --jq '.autoMergeRequest.commitHeadline // ""')"
          if [ -n "${auto_merge_subject}" ]; then
            if [ "${auto_merge_subject}" = "${pr_title}" ]; then
              echo "Native auto-merge is already enabled for PR #${PR_NUMBER} with the current title."
              exit 0
            fi

            echo "Updating native auto-merge title for PR #${PR_NUMBER}."
            gh pr merge "${PR_NUMBER}" --disable-auto --repo "${GITHUB_REPOSITORY}"
          fi

          head_owner="$(gh pr view "${PR_NUMBER}" --repo "${GITHUB_REPOSITORY}" --json headRepositoryOwner --jq '.headRepositoryOwner.login')"
          merge_args=("${PR_NUMBER}" --auto --squash --subject "${pr_title}" --body "Auto-merged after required checks passed." --repo "${GITHUB_REPOSITORY}")
          if [ "${head_owner}" = "${GITHUB_REPOSITORY_OWNER}" ]; then
            merge_args+=(--delete-branch)
          fi

          echo "Enabling GitHub native auto-merge for PR #${PR_NUMBER}."
          gh pr merge "${merge_args[@]}"
```

> 핵심 안전장치: 임의의 첫 번째 PR을 찾지 않고, 이벤트가 가리키는 PR 번호만 처리한다. `auto-merge` 라벨이 없거나 draft 상태면 아무 작업도 하지 않는다.

---

## 4. STEP 3 — Claude 행동 가이드 (`.github/CLAUDE.md`)

Claude Code가 PR을 검토할 때 본 프로젝트의 **감사 시스템**과 **Phase 정책**을 알도록 시스템 프롬프트를 주입한다.

```markdown
# Project: High-NA EUV Lithography Simulator

## 너의 역할 (in this repo)

너는 본 리포지터리의 PR을 검토하고, 본 프로젝트의 4-역할 감사 시스템 (audits/) 의 시각으로 변경 사항을 평가한다. 합격 시 PR title을 명확한 squash merge title로 정리하고, `auto-merge` label을 부여해 머지까지 자동 진행되도록 한다. 문제 발견 시 변경 요청을 남긴다.

## 핵심 참조 문서

- `PROJECT_OVERVIEW.md` — 프로젝트 개요 + scope + simplifications
- `진행계획서.md` — 6-Phase + KPI K1-K6 + WBS + 위험 등록부
- `audits/00_CI_CD_WORKFLOW.md` — gated review 6 stage
- `audits/01_data_analyst/INSTRUCTIONS.md`
- `audits/02_physics/INSTRUCTIONS.md`
- `audits/03_ai_numerical/INSTRUCTIONS.md`
- `audits/04_simulation/INSTRUCTIONS.md`
- `논문/papers/KNOWLEDGE.md` — 21편 논문 통합 학습
- `high_na_euv_physics_considerations.md` — 물리 핸드북 82 sections

## PR 검토 절차 (이 순서대로)

1. **변경 사항 파악**: 어느 Phase, 어느 모듈에 해당하는지 식별
2. **자동 테스트 결과 확인**: CI workflow의 pytest / mypy / ruff 통과 여부
3. **4-역할 감사 적용**:
   - 데이터: 새 입력 데이터가 있다면 단위·결측·EDA 점검
   - 물리: 보존법칙·좌표계·BC/IC·인과성·단순화 명시
   - AI/수치: FFT 샘플링·무차원화·gradient·MC convergence
   - 시뮬레이션: Phase Gate 8요소 + ablation + 결과 정직성
4. **감사 보고서 첨부**: 변경 영향이 있는 역할의 보고서를 `audits/<role>/reports/YYYY-MM-DD_<phase>_<topic>_<verdict>.md` 로 PR에 추가 commit
5. **AUDIT_LOG.md 업데이트**: 한 줄 요약 추가
6. **판정 적용**:
   - PASS → PR approve, `auto-merge` label 부여
   - CAUTION → 조건부 approve + mitigation issue 자동 생성 + 해결 추적 가능할 때만 `auto-merge` label 부여
   - MAJOR RISK → request changes, 의사결정 필요 라벨
   - PHYSICAL VIOLATION → request changes, 차단 라벨
   - UNVERIFIED → request changes, 정보 요청 코멘트

## 절대 하지 말아야 할 일

- pytest 실패 상태로 머지하지 않는다.
- `auto-merge` label은 PASS 또는 CAUTION(with mitigation) 판정에서만 부여한다.
- PR title은 squash merge title로 쓰이므로 아래 명명 규칙을 통과하기 전에는 `auto-merge` label을 붙이지 않는다.
- 단순화 가정이 코드 주석 + docs/ 둘 다에 없으면 머지하지 않는다.
- AUDIT_LOG.md 갱신 없이 머지하지 않는다.
- "RMSE 낮으니 통과" 같은 정량적 부족한 근거로 통과시키지 않는다.
- physics 감사를 건너뛰고 AI/수치만 보고 통과시키지 않는다.
- 1개 layout / 1개 case 결과를 "검증 완료" 라고 PR description에 쓰면 정정 요청.

## 코딩 / PR 스타일 강제

- PR title / squash merge title:
  - Phase 작업: `phase<phase>-part<NN>-<kind>: <clear summary>`
  - 예: `phase1-part02-update: add annular pupil validation`
  - 예: `phase3-part01-fix: correct wafer defocus sign`
  - 비 Phase 작업: `<scope>-<kind>: <clear summary>`
  - 예: `github-update: automate labeled squash merge`
  - kind 허용값: `add`, `update`, `fix`, `refactor`, `docs`, `test`, `audit`, `chore`
- 커밋 메시지: PR title과 같은 정보를 유지하되 더 짧게 쓸 수 있다.
- 모든 단순화는 docstring + 해당 모듈 문서에 동시 기록
- `src/` 추가 시 동일 이름의 `tests/` 단위 테스트 필수
- type hint 의무
- numpy docstring 양식

## 출력 형식

PR 코멘트는 한국어로, 코드 주석은 영어로. 보고서는 한국어 + 영어 키워드 혼용 가능 (audits/templates/audit_report_TEMPLATE.md 양식 준수).

## Phase Gate 시점의 추가 의무

다음 Phase 진입을 시도하는 PR (예: Phase 1 종료 + Phase 3 진입) 의 경우:

- 진행계획서.md §9.2 의 8-요소 체크리스트를 모두 ✅ 확인
- 4-역할 감사 보고서가 모두 PASS 또는 CAUTION (with mitigation)
- PROJECT_OVERVIEW.md §6 산출물 상태 갱신
- 진행계획서.md §5 산출물 표 갱신
- 위 셋이 같은 PR 안에 포함되어야 머지 승인
```

저장 위치: `.github/CLAUDE.md`

---

## 5. STEP 4 — `.gitignore` + `.gitattributes`

### 5.1 `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Test / coverage
.pytest_cache/
.coverage
.coverage.*
htmlcov/
.tox/
.nox/
.hypothesis/
coverage.xml
*.cover

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project-specific
outputs/runs/
*.log
notebooks/.ipynb_checkpoints/

# Secret / local
.env
.env.local
*.local
```

### 5.2 `.gitattributes`

```gitattributes
# 한국어 파일명 보존
* text=auto eol=lf

*.md text
*.py text
*.yml text
*.yaml text
*.txt text

# Notebooks: line-by-line diff 가능하게
*.ipynb text

# Binary
*.docx binary
*.pdf binary
*.png binary
*.jpg binary
```

---

## 6. STEP 5 — PR 템플릿 + CODEOWNERS

### 6.1 `.github/PULL_REQUEST_TEMPLATE.md`

```markdown
## 변경 요약

(한 단락)

## 영향 받는 Phase / 모듈

- [ ] Phase 1 (Fourier optics)
- [ ] Phase 2 (Partial coherence)
- [ ] Phase 3 (Wafer topography)
- [ ] Phase 4 (Mask 3D)
- [ ] Phase 5 (Resist)
- [ ] Phase 6 (SMO/PMWO)
- [ ] Cross-cutting / 문서 / 감사

## 변경 종류

- [ ] feat: 새 기능
- [ ] fix: 버그 수정
- [ ] docs: 문서만 변경
- [ ] refactor: 리팩터
- [ ] test: 테스트 추가/수정
- [ ] chore: 기타

## 자체 감사 결과 (4-역할)

| Role | Status | Notes |
|------|--------|-------|
| Data Analyst | PASS / CAUTION / N/A | |
| Physics | PASS / CAUTION / N/A | |
| AI / Numerical | PASS / CAUTION / N/A | |
| Simulation | PASS / CAUTION / N/A | |

## 단순화 가정

- 새로 도입한 단순화 (있다면): _______________
- 코드 주석 + docs/ 모두에 기록되었는가: [ ] Yes / [ ] No

## 단위 테스트

- [ ] 새 모듈에 단위 테스트 추가됨
- [ ] `pytest tests/` 로컬에서 모두 통과
- [ ] 기존 테스트 영향 없음

## 관련 논문 / 문서

- 참조 논문: #
- 참조 문서: 

## Phase Gate 시점인가

- [ ] Yes — 진행계획서 §9.2 8-요소 체크리스트도 통과
- [ ] No — 일반 변경

---

@claude 검토 부탁
```

### 6.2 `.github/CODEOWNERS`

```
# 모든 변경에 본인 자동 review 요청
*       @JiSeok1579

# 감사 시스템 변경은 더 신중하게
audits/         @JiSeok1579
진행계획서.md     @JiSeok1579
PROJECT_OVERVIEW.md  @JiSeok1579
```

---

## 7. STEP 6 — Branch protection + Auto-merge 설정

### 7.1 Branch protection rule

웹 UI:
1. https://github.com/JiSeok1579/high-na-euv-sim/settings/branches
2. **Add classic branch protection rule** 또는 **Add rule**
3. Branch name pattern: `main`
4. 다음을 체크:
   - ✅ **Require a pull request before merging**
     - ✅ Require approvals: **0** (완전 자동 머지 기본값)
     - ✅ Dismiss stale pull request approvals when new commits are pushed
     - ☐ Require review from Code Owners (단독 자동 머지에서는 끔, 엄격 모드에서는 켬)
   - ✅ **Require status checks to pass before merging**
     - ✅ Require branches to be up to date before merging
     - 검색하여 추가: `pytest + mypy + ruff`, `clear merge title`
     - 선택: `claude` (Claude check는 워크플로 첫 실행 후 추가 가능)
   - ✅ **Require conversation resolution before merging**
   - ☐ Restrict who can push to matching branches (선택)
   - ✅ **Allow force pushes**: ❌ off
   - ✅ **Allow deletions**: ❌ off
5. **Create / Save changes**

CLI 대안 (`gh api`):
```bash
gh api -X PUT \
  /repos/JiSeok1579/high-na-euv-sim/branches/main/protection \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["pytest + mypy + ruff", "clear merge title"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 0,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
EOF
```

### 7.2 Auto-merge 활성화

웹 UI:
1. https://github.com/JiSeok1579/high-na-euv-sim/settings
2. **General** 페이지 스크롤 → **Pull Requests**
3. ✅ **Allow auto-merge**
4. (옵션) ✅ **Automatically delete head branches** (머지 후 브랜치 자동 삭제)
5. (옵션) merge button 종류:
   - ✅ Allow squash merging (추천)
   - ☐ Allow merge commits
   - ☐ Allow rebase merging

### 7.3 CLI 자동 설정 스크립트

로컬에서 다음 스크립트를 실행하면 repository setting, 라벨, branch protection을 한 번에 적용한다.

```bash
scripts/configure_github_automerge.sh JiSeok1579/high-na-euv-sim
```

기본 required check context는 `["pytest + mypy + ruff","clear merge title"]` 이다. Claude check까지 required status로 강제하려면 워크플로가 한 번 실행되어 check 이름이 보인 뒤 아래처럼 실행한다.

```bash
REQUIRED_CONTEXTS_JSON='["pytest + mypy + ruff","clear merge title","claude"]' \
  scripts/configure_github_automerge.sh JiSeok1579/high-na-euv-sim
```

스크립트는 `auto-merge`, `blocked`, `audit` 라벨을 생성/갱신하고, `main`에 다음 보호 규칙을 적용한다.

- PR review 0개 기본값 (완전 자동 머지)
- Code Owner review는 기본 비활성 (`REQUIRE_CODE_OWNER_REVIEWS=true` 로 엄격 모드 전환 가능)
- stale approval dismiss
- required status checks 통과 필수
- conversation resolution 필수
- force push / branch deletion 차단

엄격 모드 예시:

```bash
REQUIRED_APPROVING_REVIEW_COUNT=1 \
REQUIRE_CODE_OWNER_REVIEWS=true \
  scripts/configure_github_automerge.sh JiSeok1579/high-na-euv-sim
```

---

## 8. STEP 7 — 첫 commit + push (기존 코드 올리기)

### 8.1 로컬 git 초기화 + 원격 연결

```bash
cd "/Users/yangjiseok/Desktop/High-NA EUV Lithography Simulator"

# 이미 git 저장소가 아니라면
git init -b main

# 원격 추가
git remote add origin https://github.com/JiSeok1579/high-na-euv-sim.git

# GitHub에서 README/license를 만들어 두었다면 먼저 받기
git pull origin main --allow-unrelated-histories

# .gitignore + .gitattributes + .github/* 가 위 STEP에서 생성된 상태
git add .
git status

# 첫 commit
git commit -m "Initial import: Phase 1 MVP + audits + papers + docs

- src/: Phase 1 Fourier optics MVP (constants, pupil, mask, aerial)
- tests/: phase1_aerial_image.py (5 tests, all passing locally)
- notebooks/: 0_first_aerial_image.ipynb (5 sections)
- docs/: phase1_design.md (Phase 1 design + 7 simplifications)
- audits/: 4-role audit system + CI/CD workflow + templates
- 논문/papers/: 21 papers metadata + KNOWLEDGE.md + INDEX.md
- PROJECT_OVERVIEW.md, 진행계획서.md, physics_considerations.md
- .github/: workflows + CLAUDE.md + PR template + CODEOWNERS"

# push
git push -u origin main
```

### 8.2 첫 PR 테스트

```bash
# 새 브랜치
git checkout -b test/claude-action-smoke

# 사소한 변경 (예: README 한 줄)
echo "" >> README.md
echo "_본 줄은 Claude Code Action smoke test용_" >> README.md

git add README.md
git commit -m "test: smoke test for Claude Code Action"
git push -u origin test/claude-action-smoke

# PR 생성
gh pr create \
  --base main \
  --head test/claude-action-smoke \
  --title "github-test: validate claude action smoke merge" \
  --body "@claude 이 PR은 Action 셋업 검증용입니다. CI 통과 + Claude 검토 + auto-merge가 작동하는지 확인 요청드립니다."
```

이 PR을 만들면:
- ✅ CI workflow가 자동 트리거 → pytest/mypy/ruff 실행
- ✅ Claude workflow가 자동 트리거 → PR 검토 코멘트 작성
- ✅ Branch protection이 status check + clear merge title 통과 후 머지 허용
- ✅ `auto-merge` 라벨이 붙으면 squash merge까지 자동 진행

---

## 9. STEP 8 — 자동 머지 흐름 검증

### 9.1 정상 플로우

```
1. 개발자: feature/* 브랜치에서 작업 → push → PR open
   PR description에 @claude 멘션
        ↓
2. CI workflow 자동 시작
   - ruff check src tests           ← 통과
   - mypy src --ignore-missing      ← 통과
   - pytest tests/ -v --cov         ← 통과
   - PR title 명명 규칙              ← 통과
        ↓
3. Claude workflow 자동 시작
   - .github/CLAUDE.md 시스템 프롬프트 로드
   - PR diff 읽기
   - 4-역할 감사 적용
   - audits/<role>/reports/YYYY-MM-DD_<topic>_<verdict>.md 작성
   - AUDIT_LOG.md 업데이트
   - PR에 코멘트로 감사 결과 요약
   - Phase Gate 시점이면 8-요소 체크
   - PASS 시 PR approve + `auto-merge` label 부여
        ↓
4. Branch protection이 모든 required check 통과 확인
        ↓
5. `auto-merge` 라벨이 있으면 워크플로가 GitHub native auto-merge 활성화
        ↓
6. required checks 통과 후 PR title을 squash title로 사용해 자동 merge
        ↓
7. main 브랜치 갱신 + feature 브랜치 삭제 (auto-delete)
```

### 9.2 차단 플로우 예시

```
- pytest 실패 → CI 차단 → 머지 불가 → @claude 가 실패 원인 분석 코멘트
- 단순화 가정 누락 → Claude가 request changes → 머지 차단
- 물리 위반 발견 → Claude가 request changes + audits/02_physics/reports/ 에 PHYSICAL_VIOLATION 보고서 → 머지 차단
- Phase Gate 8-요소 미달 → Claude가 부족 항목 리스트 코멘트 → request changes
```

---

## 10. 보안 / 운영 고려사항

### 10.1 비용 관리

- Anthropic API 사용량은 PR 빈도와 코드 변경 크기에 비례
- 추정: PR 1건당 Claude Sonnet 입력 ~30K tokens, 출력 ~3K tokens → 약 $0.10-0.30 / PR
- `claude.yml` 의 `if:` 조건으로 트리거 범위 제한 (예: 작성자 화이트리스트)

### 10.2 비용 제한 옵션

```yaml
# claude.yml 에 추가
jobs:
  claude:
    if: |
      github.actor == 'JiSeok1579' &&  # 본인 PR만
      ((github.event_name == 'pull_request') ||
       (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')))
```

### 10.3 PR 자동 머지의 위험

**Claude가 잘못된 판단으로 머지하는 케이스를 줄이기 위해**:
- 완전 자동 머지 기본값은 approval 0개이므로 `auto-merge` label을 PASS/CAUTION(with mitigation)에서만 부여
- 팀/공유 저장소에서는 approval 1개 + Code Owner review를 엄격 모드로 켬
- main 직접 push 금지 (force push 차단)
- auto-merge는 `auto-merge` 라벨이 붙은 PR에만 활성화
- PR title 검증을 required check로 걸어 squash merge history를 명확하게 유지
- 결정적 변경 (audits/, 진행계획서.md, PROJECT_OVERVIEW.md) 은 CODEOWNERS로 본인 review 강제

### 10.4 API key 관리

- ✅ Repository secret 으로만 보관 (.env 절대 commit 금지)
- ✅ `.gitignore` 에 `.env*` 포함됨
- ✅ key rotation 권장: 분기별 1회 신규 발급 → 교체
- ❌ key를 코드/문서에 노출 금지 (한 번이라도 commit 되면 history rewrite + key revoke 필요)

---

## 11. 문제 해결 (Troubleshooting)

### Q1. CI workflow가 실행되지 않음
- `.github/workflows/ci.yml` 가 main 브랜치에 push 되었는지 확인
- Actions 탭이 비활성화 되어 있을 수 있음 → Settings → Actions → Allow all actions

### Q2. Claude Action 이 권한 오류로 실패
- `permissions:` 블록이 워크플로에 있는지 확인 (contents: write, pull-requests: write 등)
- `ANTHROPIC_API_KEY` secret 이름이 정확한지 (대소문자 일치)
- API key가 만료되지 않았는지 Anthropic Console에서 확인

### Q3. Claude가 `@claude` 를 인식하지 못함
- `if:` 조건의 `contains(github.event.comment.body, '@claude')` 가 정확한지 확인
- Issue comment vs review comment vs PR comment 트리거 분기 확인

### Q4. Auto-merge 가 안 됨
- Settings → General → Pull Requests → "Allow auto-merge" 가 켜져 있는지
- PR에 `auto-merge` 라벨이 붙어 있는지
- PR title이 `clear merge title` check를 통과했는지
- Branch protection의 required status check 가 모두 PASS 인지
- PR이 conflict 없이 mergeable 인지

### Q5. Code Owner review 가 본인 PR이라 자동 통과 안 됨
- 완전 자동 머지 모드에서는 `REQUIRE_CODE_OWNER_REVIEWS=false`, `REQUIRED_APPROVING_REVIEW_COUNT=0`
- 엄격 모드가 필요할 때만 Code Owner review를 켠다

### Q6. 한국어 파일명이 깨짐
- `.gitattributes` 의 `* text=auto eol=lf` 가 적용되었는지
- `git config core.quotepath false` (로컬)
- macOS NFD vs Linux NFC 차이 — `git config core.precomposeunicode true`

---

## 12. 검증 체크리스트

```
[ ] Anthropic API key 발급 + GitHub secret 등록
[ ] .github/workflows/ci.yml push 됨
[ ] .github/workflows/claude.yml push 됨
[ ] .github/workflows/pr-title.yml push 됨
[ ] .github/workflows/auto-merge.yml push 됨
[ ] .github/CLAUDE.md push 됨
[ ] .github/PULL_REQUEST_TEMPLATE.md push 됨
[ ] .github/CODEOWNERS push 됨
[ ] .gitignore + .gitattributes push 됨
[ ] Settings → Branches → main 보호 규칙 활성화
[ ] Settings → General → Allow auto-merge 활성화
[ ] `auto-merge` 라벨 생성됨
[ ] `clear merge title` required check 활성화됨
[ ] 첫 smoke test PR 작성 + 자동 흐름 확인
[ ] CI 통과 확인 (Actions 탭에서 녹색 체크)
[ ] Claude 코멘트 확인 (PR 페이지)
[ ] Auto-merge 작동 확인 (머지 후 main 갱신)
[ ] AUDIT_LOG.md 자동 갱신 확인
```

---

## 13. 다음 단계 (셋업 후)

1. **로컬 → 원격 첫 동기화**: STEP 7의 첫 commit + push
2. **smoke test PR**: Claude Action이 실제로 코멘트 다는지 확인
3. **Phase 1 정식 PR**: 현재까지 작업 (src/ + tests/ + docs/) 을 main → main 으로 squash 머지
4. **Phase 1 감사 보고서 4건 작성**: 직전 점검에서 권장한 audits/*/reports/ 4개 .md
5. **Phase 3 또는 Phase 5 MVP 시작**: feature 브랜치 → @claude 검토 → 자동 머지

---

## 14. 부록: 권장 추가 워크플로 (옵션)

### 14.1 Dependabot — `.github/dependabot.yml`

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - dependencies
      - python
      - auto-merge
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - dependencies
      - github_actions
```

### 14.2 Issue 템플릿 — `.github/ISSUE_TEMPLATE/audit_request.md`

```markdown
---
name: 감사 요청 (Audit Request)
about: 특정 모듈 / Phase 의 4-역할 감사 요청
labels: audit
---

## 감사 요청 대상

- Phase: 
- 모듈 / 파일: 
- 변경 사항 요약: 

## 어떤 역할의 감사가 필요한가

- [ ] 데이터
- [ ] 물리
- [ ] AI / 수치
- [ ] 시뮬레이션

## 우선순위

- [ ] Critical (즉시)
- [ ] High (1주일 내)
- [ ] Normal

@claude 위 항목 검토 부탁
```

### 14.3 라벨 자동화 — `.github/labeler.yml`

```yaml
phase-1:
  - changed-files:
    - any-glob-to-any-file:
      - src/pupil.py
      - src/mask.py
      - src/aerial.py
      - src/constants.py
      - tests/phase1_*

phase-3:
  - changed-files:
    - any-glob-to-any-file:
      - src/wafer_topo.py
      - tests/phase3_*

audit:
  - changed-files:
    - any-glob-to-any-file:
      - audits/**/*

documentation:
  - changed-files:
    - any-glob-to-any-file:
      - docs/**/*
      - PROJECT_OVERVIEW.md
      - 진행계획서.md
      - 논문/**/*
```

---

## 15. 변경 이력

| 버전 | 날짜 | 변경 |
|------|------|------|
| v1.0 | 2026-04-26 | 초기 작성. STEP 1–8 + 보안 + 트러블슈팅 + 옵션 워크플로 |

---

> **다음 액션**: STEP 1 (API key 발급) 부터 순차 진행. STEP 7 (첫 commit) 시점에서 막히면 알려주세요. 워크플로 파일 (`.github/*`) 은 본 문서에서 그대로 복사 가능.
