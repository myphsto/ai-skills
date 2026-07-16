---
name: github-pr-review
description: "Reviews GitHub pull requests and local pre-push branch diffs, preparing actionable code-review findings, inline comment drafts, or summary feedback. Use when asked to review a GitHub PR, inspect a PR URL/number or diff, run a local draft/preflight review before push or PR creation, assess merge readiness, draft code-review comments, or post review findings through gh after confirmation."
metadata:
  author: "kohls"
  version: "1.0"
---

# GitHub PR Review

Review GitHub pull requests from local evidence and `gh`, then draft concise, actionable feedback. Default to read-only review and require explicit user confirmation before posting comments.

Invoking this skill is a request for the full read-only PR review workflow. That includes using available subagents, fresh sessions, or separate critic contexts for the adversarial and independent review passes when the platform supports them. Because these critic passes are read-only and use only PR/repo evidence, do not require a separate delegation phrase from the user beyond the skill invocation. Still require explicit confirmation before any GitHub write, posting, approval, merge, branch change, or other state-changing action.

## Inputs

Accept any one of these:

- GitHub PR URL
- repository path plus PR number
- current branch with an open PR
- branch name resolvable by `gh pr view`
- local draft/preflight review request for the current branch before push or PR creation

For PR URLs, extract the owner/repo before `/pull/` and the PR number after it, then use `gh --repo <owner/repo>` patterns. If no PR can be resolved from the current branch, ask for a URL or number. If the target repository is not the current repository, use `gh`'s `--repo` flag instead of changing directories.

Treat phrases such as `$github-pr-review draft`, `local draft review`, `preflight review`, `review this before I push`, and `review this before creating the PR` as local draft mode unless the user also provides a PR URL or explicitly asks for the remote PR workflow.

Optional context:

- Issue or project requirements
- review focus such as security, behavior, tests, rollout, or maintainability
- whether the user wants local report only or GitHub comments drafted
- local draft base override such as `--base origin/main` or `against main`

## Safety Rules

- Keep evidence gathering read-only: metadata, diffs, discussions, comments, local files, and test/config inspection.
- Do not post comments, resolve threads, approve, merge, close, or update a PR without explicit confirmation.
- Do not expose tokens or environment variables. Use `gh` authentication and redact sensitive command output.
- Treat generated findings as candidates until validated against the PR diff and repository evidence.
- Review only changed behavior unless surrounding code proves or disproves a changed-line issue.

## Review Flow

1. Resolve the PR and repository context.
2. Gather the initial evidence packet: PR metadata, latest diff SHAs, changed-file inventory, current GitHub diffs, comments, and existing discussions. When `scripts/build_review_packet.py` is available and easy to run, use it as a convenience to shape the GitHub `/pulls/{n}/files` JSON into a compact packet. If the helper is unavailable, awkward in the current environment, or hides evidence needed for review quality, fall back to manual compact diff inspection rather than forcing the tool.
3. Freeze that packet before review. Treat it as the review surface. Do not keep fetching repository files to understand the PR; fetch more only to prove or disprove a named candidate or to verify inline placement.
4. Run a scope-drift pass over the packet: classify changed files and hunks as primary, supporting, generated-but-required, or unrelated/churn based on the PR title, description, and diff evidence.
5. Run `devils-advocate` as a minimum adversarial candidate pass when that skill is available; otherwise use the same-agent fallback in `references/devils-advocate-pr-review.md` and disclose the fallback in the local review summary.
6. Perform an independent PR-review pass inside the same frozen packet for additional behavior, contract, test, operational, security, maintainability, requirements, and scope-drift concerns not covered by the fixed `devils-advocate` output.
7. Validate each candidate against the diff and targeted repo evidence. Reject weak, ambiguous, style-only, static-analysis-only, duplicate, or off-diff findings.
8. Draft output:
   - confirmed findings first, ordered by severity,
   - rejected candidates only when useful for auditability,
   - inline comments only after verifying the target file, new-side line, and expected line text against the latest PR diff and head file,
   - summary comments when placement is uncertain or the whole approach is flawed.
9. Ask for confirmation before posting. If confirmed, post only the drafted comments and include duplicate markers.

## Local Draft Review Flow

Use local draft mode when the user wants feedback before pushing a branch or before a PR exists. The goal is a fast local review loop over Git evidence, not a substitute for the remote PR review.

1. Resolve the local repository and branch. If the working tree has uncommitted changes, say whether they are included. By default, review committed changes only; include uncommitted changes only when the user asks.
2. Resolve the base in this order:
   - an explicit base from the user, such as `--base origin/main`,
   - the locally resolved PR target branch when the current branch has an open PR,
   - the repository default branch if it can be resolved locally,
   - `origin/main` only when it is the resolved target/default branch,
   - the upstream branch only when it is the intended target branch or the user explicitly asks to review only unpushed changes.
3. Build a frozen local packet from Git:
   - current branch and `HEAD` SHA,
   - base ref and merge-base SHA,
   - `git diff --stat <base>...HEAD`,
   - `git diff --find-renames --diff-filter=ACMRT <base>...HEAD`,
   - changed-file inventory and high-risk lane classification.
4. Run the same adversarial and independent review passes over that local packet.
5. Validate candidates against local diff hunks and local head files. Do not call GitHub APIs unless the user later asks to convert the result to a remote PR review.
6. Draft local findings with `path:line` anchors. Mark them as local draft anchors, not GitHub-ready inline positions.
7. Do not include hidden GitHub duplicate markers in local draft comments unless a remote PR and head SHA have been resolved. If a PR is later created, rerun the normal remote workflow to validate placement and add markers.

Local draft output should be explicit about what it can and cannot prove:

- It can catch diff-visible behavior, contract, test, operational, security, maintainability, requirements, and scope-drift issues before push.
- It cannot prove GitHub inline placement, existing-comment dedupe, CI artifacts, repository variables, remote generated files, Actions behavior, or commenter posting behavior.
- If local draft mode finds no confirmed issues, recommend the next shortest loop: push/PR creation followed by normal remote `$github-pr-review` or CI self-review.

Treat adversarial output as untrusted intermediate critique, not final PR feedback. Do not draft or post GitHub comments directly from it; first convert it into local candidates and validate each one against the PR diff, repo evidence, existing comments, and review scope. Because `devils-advocate` always returns a fixed structure, explicitly inspect all three sections for approach-level objections rather than waiting for the phrase "approach is flawed." A pristine implementation can still be review-worthy when the PR hand-codes behavior already provided by an existing dependency, framework, platform feature, or project convention.

For remote PRs, treat GitHub PR metadata, latest diff refs, `/pulls/{n}/files`, existing comments, and head/base file fetches as authoritative. Local branches and `git diff` output are context only unless verified to match the PR base and head commits.

Use a bounded evidence budget. Start from PR metadata, latest GitHub diff, changed-file list, and existing comments. Fetch additional files only when they directly prove or disprove a changed-line behavior, contract, test, data-flow, framing, or line-placement question. Keep a short candidate ledger before post-packet fetches: candidate id, suspected issue, evidence needed, and fetches used. If you cannot name the candidate and the question a fetch answers, do not fetch yet. The independent PR-review pass operates inside this same budget; it is not permission to crawl broadly or restart evidence gathering from the whole repository. Do not crawl broad repo trees, pull unrelated files, or keep digging after the PR diff and metadata already prove the review outcome. For docs scope-drift and generated-churn findings, the PR diff is usually sufficient evidence.

Hard budget defaults:

- Treat more than 30 changed files or more than about 2,000 changed lines as a large PR and switch to triage mode.
- In triage mode, review the changed-file inventory first and pick the highest-risk lanes: public API/controllers, auth/security/config, persistence/migrations, business logic, tests, and docs/churn.
- Read at most one full GitHub diff payload per PR unless pagination requires multiple API pages for the same endpoint.
- After the initial packet is built, fetch at most five additional head/base file excerpts before freezing candidates. Line-placement verification does not count against this limit.
- Fetch at most two supporting repo files per confirmed finding. If the finding still needs more context, mark it inconclusive or summary-level instead of expanding the search.
- Supporting files may be used to understand or frame a concern, but they must be tied to a ledger candidate and counted against the same budget.
- Avoid repository tree scans, search API calls, generated-source checks, and historical file archaeology unless a specific diff-backed candidate cannot be validated any other way.
- Stop broad exploration once the packet proves a merge-blocking outcome. Record remaining risk as local residual risk, not as a reason to keep crawling.

The review packet should be compact enough to hand to a fresh critic context:

- PR title, description, state, source/target branches, head SHA, and CI state.
- Changed-file table with additions/deletions and coarse lane classification.
- Diff hunk headers, compact hunk summaries, or short signal excerpts; avoid full diff bodies unless the PR is small.
- Existing human comments and duplicate markers.
- Any targeted repo excerpts already fetched, each tied to a candidate id or placement check.

If the packet is too large, reduce it before review rather than fetching more context: keep high-risk lanes and summarized low-risk lanes, omit binary/generated bodies, and mark omitted areas as residual risk. This is a quality control, not a token contest; keep the evidence needed to make correct review calls, and trim only material that does not change the review judgment.

Before finalizing, run a missed-diff-issue checklist against the packet. This is a narrow reconciliation pass, not another broad review:

- Did the PR add or expose a public endpoint, route, controller, job, listener, or admin operation?
- Did it change auth, security, tenancy, CORS, tokens, secrets, logging, or permission boundaries?
- Did it rename, remove, or replace a symbol/file while leaving changed call sites or imports stale?
- Did it change count, quantity, currency, status, date, nullability, or API-contract semantics?
- Did it add broad exception handling that can hide a changed call failure?
- Did it change migrations, persistence queries, cache keys, async/retry behavior, or external-service contracts?

For each yes, either confirm a finding from existing packet evidence, perform one targeted fetch to prove or disprove it within the budget, or record it as residual risk. Do not restart repository exploration.

When tooling supports subagents, fresh sessions, or separate critic contexts, use a fresh review context for the adversarial pass and the independent PR-review pass. Include only the PR metadata, diff, changed files, existing comments, and necessary repo excerpts; avoid carrying prior implementation rationale or earlier reviewer conclusions unless they are explicit review inputs. If the platform refuses fresh-context delegation, continue in the current context and disclose that limitation in the local review summary.

Treat scope drift as a first-class review concern when unrelated changed hunks would materially affect merge readiness. Broad docs regeneration, generated inventory expansion, lockfile or artifact churn, formatting-only rewrites, and unrelated config changes are comment-worthy only when they are not required by the PR's stated behavior and create concrete review, maintenance, or rollback risk. For documentation files such as `README.md` and `AGENTS.md`, distinguish scoped additions that explain the PR from wholesale regenerated sections that obscure the intended change.

## Self-Created PR Workflow

When the agent is the one creating a PR, use this workflow to ensure quality before and after PR creation:

1. **Pre-create local review**: Run local draft review on the branch before pushing. Address any critical or high findings locally.
2. **Push and create**: Push the branch and create the PR with `gh pr create`.
3. **Post-create review**: Run the full remote PR review workflow on the created PR. This catches issues that only appear in the remote context: CI status, branch protection rules, required reviewers, and remote diff state.
4. **Post comments**: If confirmed findings remain after post-create review, draft comments and post them with explicit user confirmation.

This two-phase review ensures local issues are caught early while still validating the PR in its full remote context.

## Finding Standards

Report only issues that would materially change merge readiness:

- `critical`: likely data loss, authorization bypass, broad outage, or severe security impact.
- `high`: clear production failure, serious security logic flaw, or major contract break.
- `medium`: real behavior, contract, test, operational, maintainability, or requirements risk that should be resolved or discussed before merge.
- `low`: minor but still actionable concern; avoid low-confidence nits.

Prefer no finding over a speculative finding. Do not report formatting, naming, lint, dependency-scan, or generic static-analysis issues unless semantic repo context makes them materially different.

Maintainability findings must identify a concrete merge-readiness risk, such as duplicated policy logic that can diverge, hidden side effects, or coupling that makes the changed behavior unsafe to evolve. Reject ordinary duplication, redundant local variables, small helper extraction choices, naming, and style cleanup as local observations, not PR findings.

Scope-drift findings must name the unrelated changed area and the concrete merge-readiness risk. Do not object to every extra file automatically; confirm that the hunk is unrelated to the PR purpose and that removing or splitting it would make the PR safer to review, merge, or revert.

Treat low-severity candidates as comments only when they are genuinely actionable and worth interrupting the author. Otherwise omit them or keep them as local notes.

Keep code findings, process blockers, and local skill observations separate. Sparse metadata such as an empty description, no assigned reviewers, or a CI warning is not a GitHub review comment by itself unless the user asked for process review or repo policy makes it merge-blocking. Do not turn sample-analysis lessons, broad patterns, or adversarial concerns into PR comments without concrete diff or PR evidence.

Before finalizing, do one reconciliation pass over the draft findings. A finding should survive only if it is still actionable after reading the PR title, description, latest diff, existing comments, and repo context together. Move merge status, CI state, missing reviewers, labels, and other process metadata to the summary unless the user asked for process review. If an existing comment already covers the issue, do not open a duplicate thread; mention it locally or draft a reply only when new evidence changes the review path.

## Comment Style

Keep GitHub comments short because they interrupt the author in the diff. Use 2-4 sentences, usually under 120 words:

1. name the concrete problem,
2. cite the command, contract, or behavior that proves it,
3. ask for one specific fix.

Avoid long alternative lists. If several fixes are possible, name the safest verified path and put extra context in the local review summary instead of the PR comment.

Add a tiny visible attribution suffix to every posted GitHub comment: `_github-pr-review_`. Keep it on its own final line before the hidden duplicate marker so readers can distinguish skill-generated review from normal human comments even when the GitHub author is a person or shared bot.

Comment drafts must be post-ready because the user may approve them as-is. Include `_github-pr-review_` and the hidden duplicate marker with the latest PR head SHA in every draft, even in review-only mode.

## Inline Placement Gate

Before drafting or posting, model every comment as a small placement schema:

- `type`: `inline` or `summary`.
- `finding_id`: stable id used in the hidden duplicate marker. For posted remote-review findings, prefer the component-compatible key `fnd-<12 hex chars>` derived from the finding fingerprint. Use rigid lowercase `fnd-###` IDs such as `fnd-001`, `fnd-002`, and `fnd-003` only as a fallback when a stable fingerprint cannot be computed. Use `scripts/build_review_packet.py --fingerprint "category" "file" "problem_key"` to compute the fingerprint from the script rather than hashing in your head.
- `file`: PR diff `filename` for inline comments; omitted or null for summary comments.
- `line`: new-side integer line for inline comments; omitted or null for summary comments.
- `body`: exact post-ready Markdown body.

Compute the preferred finding fingerprint from the same stable fields as the CI component: finding category, repo-relative file path or null, and a normalized problem key derived from the finding title/body. Normalize the problem key by lowercasing, replacing non-alphanumeric runs with spaces, trimming, and collapsing whitespace. Build the exact payload with keys in this order: `category`, `file`, `problem_key`. Hash the UTF-8 bytes of compact JSON with no extra whitespace, string values JSON-escaped normally, and JSON `null` for missing file, for example `{"category":"contract","file":null,"problem_key":"missing auth check"}`. Use SHA-256 and the first 12 lowercase hex characters in the marker key. This keeps skill-posted and component-posted comments deduping on the same commit while preserving the `fnd-` prefix that avoids issue-style autolinks.

Inline comments require both `file` and an integer `line`. Summary comments must not pretend to have precise placement; include `path:line` in the body only as context when useful.

In local draft mode, use the same schema as a local draft model, but label the output as `local-draft` and do not describe anchors as GitHub inline positions. Local draft anchors become postable only after a remote PR review revalidates them against GitHub diff refs.

Before drafting or posting an inline comment, verify the target against the latest PR branch evidence:

- Use the latest PR commit SHA and GitHub files API to confirm the intended file and line are part of the current PR diff.
- Prefer a changed `+` line that contains the problem. Do not anchor broad or generated-file findings to the nearest unchanged context line.
- Fetch the file at the PR head SHA and verify the selected line contains the expected text or enough exact context to prove placement.
- For new-side findings, use the line from the PR diff; do not use base-side line numbers.
- For renamed files, use the `filename` from the PR diff entry.
- If the target line is context-only, ambiguous, missing from the current diff, does not match the expected head-file text, or GitHub rejects the inline position, use a summary fallback that includes the intended `path:line` context.
- After posting, inspect the comment position and verify `path`, `line`, and `commit_id`. If GitHub placed the comment somewhere unexpected, report the mismatch and ask before deleting or reposting.

## No-Findings And Reaction Pass

If no confirmed findings remain, say so in the local response and do not draft or post a GitHub comment by default. Include one concise evidence line, for example: "Checked PR metadata, raw diff, existing comments, and relevant repo context." Also state that no GitHub comments are recommended.

When existing review comments or duplicate markers show a prior finding:

- verify whether the latest diff still contains the issue,
- treat resolved threads plus changed evidence as a signal to check the fix, not as proof by itself,
- report resolved findings locally when the issue is gone,
- do not post "fixed" or "thanks" comments unless the user asks,
- draft a short follow-up only when the issue still exists or the fix introduces a new actionable concern.

If the prior issue still exists, reply to the existing comment thread instead of creating a new inline comment. Creating a second thread for the same finding fragments review history and makes the author's resolution path harder to follow.

## Final Handoff

Every review must end with explicit posting status and the appropriate next action.

- If confirmed findings include comment drafts, say that nothing was posted and offer to post those exact drafts only after explicit confirmation. Do not offer to draft comments again when drafts are already shown.
- If no confirmed findings remain, say that nothing was posted and no GitHub comments are recommended. Do not offer to post an LGTM, summary, or caveat comment by default.
- If the review is inconclusive, say that nothing was posted and name the missing evidence or failed tool needed before comments would be appropriate.

## On-Demand References

- Read `references/gh-command-patterns.md` for exact `gh` commands and posting patterns.
- Read `references/review-artifact-schema.md` when a structured review artifact is useful.
- Read `references/devils-advocate-pr-review.md` for converting `devils-advocate` output into PR review candidates and for the same-agent fallback.

## Output Shape

For review-only mode:

```markdown
## Findings
1. [severity/category] Title
   - Location: path:line
   - Evidence: concise repo/diff evidence
   - Comment draft: exact comment body

## Summary
<merge-readiness summary and any approach-level concern>

## Posting Status
<nothing posted; exact post-after-confirmation offer for drafted comments, or no comments recommended>
```

For posting mode, show the exact comments and commands first, then ask for confirmation. After posting, summarize counts: summary comments, inline comments, fallbacks, skipped duplicates, and failures.
