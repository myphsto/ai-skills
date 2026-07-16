# gh Command Patterns

Use these patterns for GitHub PR review. Prefer the current repository context unless the user supplied a different repository; then add `--repo <owner/repo>`.

## Preflight

```bash
gh --version
gh auth status
git rev-parse --show-toplevel
git status --short --branch
```

Do not print token-bearing environment variables. If auth fails, ask the user to authenticate with `gh auth login`.

## Resolve PR Context

For a URL like:

```text
https://github.com/owner/repo/pull/42
```

derive:

- repo: `owner/repo`
- pr: `42`

Then pass `--repo owner/repo` on `gh pr` commands when the local checkout is not already that repository.

```bash
# Current branch or explicit branch/number
gh pr view --json title,body,state,headRefName,baseRefName,headRefOid,number,htmlUrl,mergeable,reviewDecision

# With reviews and comments
gh pr view --json title,body,state,headRefName,baseRefName,headRefOid,number,htmlUrl,mergeable,reviewDecision,reviews,comments

# Raw diff for review evidence
gh pr diff <number-or-branch>

# Changed-file names from local git when target/source refs are available
git diff --name-only <target>...<source>
git diff --no-ext-diff --binary <target>...<source>
```

Useful API calls:

```bash
# PR metadata
gh api repos/{owner}/{repo}/pulls/{number}

# PR files for review evidence
gh api repos/{owner}/{repo}/pulls/{number}/files

# Existing comments for duplicate detection
gh api repos/{owner}/{repo}/pulls/{number}/comments

# Issue comments (summary-level)
gh api repos/{owner}/{repo}/issues/{number}/comments

# File contents at the PR head SHA for line-placement checks
gh api repos/{owner}/{repo}/contents/<path>?ref=<head-sha>

# Check CI status
gh api repos/{owner}/{repo}/commits/<sha>/status
```

## Build A Bounded Review Packet

Start with compact GitHub evidence before reading full files. Use the changed
file inventory to decide whether the PR is in large-PR triage mode.

```bash
# Metadata and latest SHAs.
gh api repos/{owner}/{repo}/pulls/{number} \
  | jq '{number,title,state,head:{sha: .sha, ref: .ref}, base:{sha: .sha, ref: .ref},
         body,mergeable,review_comments,comments,
         checks_url: .url + "/checks"}'

# Optional compact review packet. Use this default readable packet first when
# the helper is available; it is the primary way to avoid pasting large raw diff
# bodies while preserving review quality.
python_bin="$(command -v python3 || command -v python || true)"
if [ -n "$python_bin" ]; then
  gh api repos/{owner}/{repo}/pulls/{number}/files \
    | "$python_bin" skills/github-pr-review/scripts/build_review_packet.py
else
  echo "Python not found; use manual compact diff inspection instead." >&2
fi

# Use JSON only when another script needs structured data.
python_bin="$(command -v python3 || command -v python || true)"
if [ -n "$python_bin" ]; then
  gh api repos/{owner}/{repo}/pulls/{number}/files \
    | "$python_bin" skills/github-pr-review/scripts/build_review_packet.py --json
fi

# If shell piping is awkward, save the files JSON to a temporary file first.
# Keep this file outside the repo unless the user asked for a benchmark artifact.
python_bin="$(command -v python3 || command -v python || true)"
tmp_files="$(mktemp)"
gh api repos/{owner}/{repo}/pulls/{number}/files > "$tmp_files"
if [ -n "$python_bin" ]; then
  "$python_bin" skills/github-pr-review/scripts/build_review_packet.py "$tmp_files"
fi
rm -f "$tmp_files"

# If the helper is unavailable, fall back to a changed-file inventory with
# rough line counts. Review this before fetching targeted files or raw hunks.
gh api repos/{owner}/{repo}/pulls/{number}/files \
  | jq -r '.[] | [.filename, (.additions|tostring), (.deletions|tostring), .status]'
```

The helper intentionally caps changed files, high-risk files, hunk headers, and
candidate signals. Use `python3` or `python`, whichever is available in the
local environment, and check `build_review_packet.py --help` for the current
cap flags. Use `omitted_context` as residual risk unless a named candidate
needs one targeted follow-up. Do not treat the helper as mandatory: if it fails,
is missing, or would hide important review evidence, continue with compact
manual inspection and targeted file reads.

For large PRs, classify files into lanes before reading more:

- public API/controllers
- auth/security/config
- persistence/migrations
- business logic
- tests
- docs/churn/generated

Fetch head or base file contents only for a named candidate or inline placement
check. Keep a small candidate ledger before fetching:

```text
c1 migration-backfill: need to know whether V34 adds NOT NULL to existing rows
c2 auth-boundary: need to verify whether non-admin callers can set admin fields
```

State the candidate before fetching, for example: "Validate c1 by reading the
V34 migration window." Prefer `sed`/`nl` windows around relevant lines over
whole-file output, especially when the packet already provides hunk headers or
signal excerpts.

Avoid repository tree scans, search API calls, generated-source checks, and
historical file reads unless the compact packet plus a targeted file excerpt
cannot validate a concrete diff-backed candidate. The PR diff is the review
surface; broader repository context is supporting evidence, not the starting
point.

Avoid commands that print selected raw diffs for many files, such as broad
`jq -r '... + .patch'` filters. If a hunk body is needed, fetch the single
target file's diff after naming the candidate it validates.

## Draft Comments

Inline comments should target the new side of the latest PR diff when the finding is tied to a changed line. Before posting, verify that the chosen line is current for the PR head branch and is not merely a nearby context line.

For inline comments, use the API with `subject_type=line`:

```bash
gh api --method POST repos/{owner}/{repo}/pulls/{number}/comments \
  --field body="Review comment body" \
  --field path="path/to/file.ext" \
  --field line=42 \
  --field subject_type=line \
  --field commit_id=<head-sha>
```

For Markdown bodies with backticks, quotes, links, code fences, or hidden markers, write the body to a temporary file and feed it. This avoids shell quoting mistakes and literal `\n` text.

```bash
COMMENT_FILE="$(mktemp)"
cat > "$COMMENT_FILE" <<'EOF'
This return path now skips validation for cached orders. Please keep the existing validation call before returning so expired orders cannot bypass the status check.

_github-pr-review_

<!-- github-pr-review:<commit-sha>:<finding-id> -->
EOF

gh api --method POST repos/{owner}/{repo}/pulls/{number}/comments \
  --field "body=$(cat "$COMMENT_FILE")" \
  --field path="path/to/file.ext" \
  --field line=42 \
  --field subject_type=line \
  --field commit_id=<head-sha>
```

Summary comments are safer when a finding spans multiple files, line placement is uncertain, the issue is approach-level, or inline placement fails.

```bash
gh pr comment <number> --body "Review summary body"
```

For multiline summary comments, use the issues comments API:

```bash
gh api --method POST repos/{owner}/{repo}/issues/{number}/comments \
  --field "body=@comment.md"
```

## Verify Inline Placement

Use this gate before drafting or posting an inline comment:

First normalize each draft comment into this schema:

```json
{
  "type": "inline",
  "finding_id": "fnd-001",
  "file": "path/to/file.ext",
  "line": 42,
  "body": "Post-ready Markdown body"
}
```

Use `type: "summary"` with omitted or null `file` and `line` when the finding spans files, is approach-level, targets generated/churn scope broadly, or cannot be placed on a verified new-side line. Inline comments require a `file` matching the PR diff `filename` and an integer new-side `line`.

1. Read the PR head SHA:

```bash
gh api repos/{owner}/{repo}/pulls/{number} | jq '.head.sha'
```

2. Read the GitHub files for the target file and confirm the intended line is in the current PR diff. Prefer a changed line that contains the problem; avoid anchoring broad findings to unchanged context lines.

```bash
gh api repos/{owner}/{repo}/pulls/{number}/files \
  | jq '.[] | select(.filename=="path/to/file.ext")'
```

3. Fetch the file at the PR head SHA and verify the selected line contains the expected text. URL-encode path separators as `%2F`.

```bash
gh api repos/{owner}/{repo}/contents/path%2Fto%2Ffile.ext?ref=<head-sha> \
  | jq -r '.content' | base64 -d
```

If the intended line is context-only, ambiguous, missing from the latest diff, or does not match the head-file text, use a summary comment instead of an inline comment. After posting, inspect the comment position and confirm GitHub recorded the expected `path`, `line`, and `commit_id` before reporting success.

## Reply To Existing Threads

When re-checking a prior finding, reply to the original comment if the issue still exists. Do not create a new inline thread for the same unresolved finding.

List comments and find the relevant comment:

```bash
gh api repos/{owner}/{repo}/pulls/{number}/comments
gh api repos/{owner}/{repo}/issues/{number}/comments
```

Reply with a follow-up comment referencing the original:

```bash
gh api --method POST repos/{owner}/{repo}/issues/{number}/comments \
  --field "body=This still appears unresolved because ..."
```

For Markdown-heavy replies, write the body to a temporary file:

```bash
REPLY_FILE="$(mktemp)"
cat > "$REPLY_FILE" <<'EOF'
This still appears unresolved because the latest diff still returns cached orders before validation runs. Please keep the validation call before the early return.

_github-pr-review_

<!-- github-pr-review:<commit-sha>:<finding-id>:follow-up -->
EOF

gh api --method POST repos/{owner}/{repo}/issues/{number}/comments \
  --field "body=$(cat "$REPLY_FILE")"
```

## Duplicate Markers

Append a hidden marker to each comment body before posting:

```text
_github-pr-review_

<!-- github-pr-review:<commit-sha>:<finding-id> -->
```

The visible `_github-pr-review_` line is attribution. The hidden marker is for idempotency. Use the latest PR head SHA for `<commit-sha>` so retries on the same version deduplicate while later pushes can be reviewed independently. Before posting, inspect existing comments and skip a draft if its marker already exists. This keeps retries idempotent without needing to delete or update old comments.

Use content-addressed finding IDs derived from the finding fingerprint: run `scripts/build_review_packet.py --fingerprint "category" "file-or-null" "problem description"` to get a stable `fnd-<12 hex chars>` ID. This keeps the same finding deduping across review runs on different commits. Fall back to rigid `fnd-001`, `fnd-002`, `fnd-003` only when the script is unavailable. Do not use candidate, rejected, summary, or longer descriptive IDs in new finding markers; those are harder for CI-based reviewers using the same marker convention to dedupe against on the same commit.

## Self-Created PR Commands

When the agent creates a PR, use these commands:

```bash
# Push the branch
git push origin <branch>

# Create the PR
gh pr create \
  --title "Title" \
  --body "Description" \
  --base <target-branch> \
  --head <source-branch>

# Create PR with draft mode
gh pr create \
  --title "Title" \
  --body "Description" \
  --base <target-branch> \
  --head <source-branch> \
  --draft

# Check CI status after creation
gh api repos/{owner}/{repo}/commits/<sha>/check-runs
gh api repos/{owner}/{repo}/commits/<sha>/statuses
```

## Shell-Safe Markdown Bodies

Do not pass multi-line Markdown through quoted shell strings when the body contains links, code, backticks, quotes, or hidden markers. Prefer file-backed patterns.

Post a summary comment from a Markdown file:

```bash
gh api --method POST repos/{owner}/{repo}/issues/{number}/comments \
  --field "body=$(cat comment.md)"
```
