# Repo Sync — safe git updates on a server — details

## Capability contract

Read/search status and fetch inspection may be read-only. Pull/rebase changes the working tree and needs explicit authority. Never delete, reset, auto-resolve, force-push, expose credentials, or run an unapproved post-pull command.

## Degraded mode

If network, credentials, Git, upstream tracking, or a clean conflict state is unavailable, preserve the tree and report branch, status, and the failed step. Do not call a fetched or conflicted repository updated.

## Evidence produced

| Artefact | Acceptance |
|---|---|
| Repository update evidence | Includes porcelain status, branch/upstream, before/after IDs, pull/autostash state, build exit, skipped repos, and redacted credentials |

## Quality standards

- An update must never destroy uncommitted or untracked work.
- A dirty working tree is reported to the operator, never silently wiped.
- A failed rebase or stash re-apply leaves the operator a clear recovery path.
- The same script is safe to run twice (idempotent) and safe to run on a
  repo someone edited five minutes ago.

## Worked example

A production checkout has a modified tracked config and an untracked upload. Report both, run the authorised `git pull --rebase --autostash`, leave the upload untouched, and record commit IDs. If the autostash conflicts, stop before the build and hand the exact recovery state to the owner.
