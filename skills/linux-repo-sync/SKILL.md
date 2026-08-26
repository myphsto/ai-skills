---
name: linux-repo-sync
description: "Use when writing, reviewing, or running unattended or menu-driven Git repository updates that must preserve tracked and untracked local work."
license: MIT
compatibility: "Linux (Debian/Ubuntu or RHEL family); root for most operations"
metadata:
  author: myphsto
  version: "1.0"
  source: "https://github.com/peterbamuhigire/linux-skills"
---

# Repo Sync — safe git updates on a server

## Distro support

**Fully portable.** This skill is `git`-only and identical on both families
(Debian/Ubuntu and the RHEL family: Fedora, RHEL, CentOS Stream, Rocky, Alma,
Oracle). The doctrine below — `pull --rebase --autostash`, porcelain
dirty-checks, never `reset --hard`/`clean -fd` — is distro-neutral. The only
difference is installing git itself.

| Concept | Debian/Ubuntu | RHEL family |
|---|---|---|
| Install git | `apt install git` | `dnf install git` |
| Everything else (`git pull --rebase --autostash`, status, conflict recovery) | identical | identical |

## Use when

- Writing, reviewing, or running any script that pulls git repos on a server
  (a repo-update menu, a deploy hook, a cron sync).
- Updating one or many repos on a managed host as part of deployment or
  routine maintenance.
- Deciding how an automated update should treat local, uncommitted, or
  untracked changes in a server-side working tree.

## Do not use when

- The task is a one-off `git pull` a developer runs by hand in their own
  checkout and watches the output of.
- The task is authoring a generic script scaffold; apply the git update
  doctrine below only to the git steps.

## Required inputs

| Artefact | Source | Required? | If absent |
|---|---|---|---|
| Repository path(s) and intended branch | Operator or approved registry | yes | Skip the target; never search and update arbitrary repos |
| Interactive or unattended mode | Scheduler/operator | yes | Default to report-only planning |
| Remote/authentication and post-pull command | Repository owner | for update/build | Do not infer credentials or run a build |
| Deployment/change authority | Service owner | for integration | Fetch/status only; do not integrate commits |

## Decision rules

| State | Action | Failure avoided |
|---|---|---|
| Dirty tracked work | Warn and use `--rebase --autostash` | Lost local edits |
| Untracked files present | Preserve them and report collision risk | Deleted uploads/config |
| Rebase or stash conflict | Stop with recovery commands | Destructive auto-resolution |
| Detached HEAD or missing upstream | Stop and request intended branch | Updating the wrong history |

## Workflow

1. Confirm the path is a git working tree (`<path>/.git` exists).
2. Check the working tree state with `git status --porcelain` before touching it.
3. Pull with `git pull --rebase --autostash` so local work is stashed,
   the rebase runs, and the work is re-applied on top.
4. On conflict, stop and tell the operator how to recover — never discard.
5. Leave untracked files in place, always.
6. Run any post-pull build only after a clean, successful update.

## Outputs

| Artefact | Consumer | Acceptance condition |
|---|---|---|
| Per-repo update result | Operator | Records branch, before/after commit, dirty state, and outcome |
| Conflict handoff | Repository owner | Gives exact status plus safe continue/abort/stash recovery |
| Post-pull result | Service owner | Runs only after successful integration and records exit status |

## Anti-patterns

- `git reset --hard HEAD` in automation. Fix: preserve local work with rebase/autostash and stop on conflict.
- `git clean -fd` or `-fdx`. Fix: leave untracked files untouched and report collisions.
- Resetting local changes as a routine pre-pull step. Fix: inventory and preserve the dirty state.
- Auto-resolving or auto-aborting a rebase/stash conflict. Fix: leave state intact for the owner.
- Removing uploads, `.env`, or generated config to avoid conflicts. Fix: stop and report the conflicting path.

## Capability Recovery

On conflict, leave Git's state intact and show `git status`, `git rebase --continue`, `git rebase --abort`, and `git stash list`. Never choose the recovery path for the owner.

## The doctrine (binding on every repo-update script)

This is a STANDARD, not a suggestion. It exists because a repo-update menu
script once ran `git reset --hard HEAD` + `git clean -fd` before pulling and
silently wiped a developer's uncommitted edits. That must never be possible
again on any server we manage.

1. **NEVER use `git reset --hard` in an automated or menu repo-update
   script.** It destroys uncommitted changes to tracked files with no undo.
2. **NEVER use `git clean -fd` (or `-fdx`) in an automated or menu
   repo-update script.** It deletes untracked files — uploads, `.env`,
   generated config — that git is not tracking precisely because they must
   survive.
3. **Prefer `git pull --rebase --autostash`.** `--autostash` stashes any
   local changes before the rebase and re-applies them afterwards, so local
   work is preserved through the update. This is the default pull command for
   every server-side update.
4. **Detect a dirty working tree before pulling** with
   `git status --porcelain`. If it is non-empty, warn the operator that local
   changes exist (and will be stashed and re-applied, not discarded). Never
   discard them.
5. **On a rebase or stash-reapply conflict, STOP.** Do not auto-resolve, do
   not auto-abort. Report the conflict and the recovery options to the
   operator:
   - `git rebase --continue` after resolving the conflicting files, or
   - `git rebase --abort` to return to the pre-pull state, and
   - `git stash list` — the autostash is preserved here; recover it with
     `git stash pop` once the tree is clean.
6. **Untracked files are left in place, always.** An update never removes a
   file git is not tracking.

## The safe pattern (copy-paste)

```bash
update_repo_safely() {
    local path="$1"

    [[ -d "$path/.git" ]] || { echo "not a git repo: $path" >&2; return 1; }
    cd "$path" || return 1

    # 1. Detect a dirty working tree — warn, never wipe.
    if [[ -n "$(git status --porcelain)" ]]; then
        echo "WARNING: $path has local changes."
        echo "         They will be stashed and re-applied, not discarded."
    fi

    # 2. Pull with rebase + autostash: local work is preserved.
    if git pull --rebase --autostash; then
        # An autostash re-apply conflict does NOT fail the pull (exit 0):
        # git leaves conflict markers in the tree and keeps the autostash.
        # Detect unmerged files so we never report success on a conflicted tree.
        if git status --porcelain | grep -qE '^(U.|.U|AA|DD)'; then
            echo "ERROR: pull succeeded but re-applying your stashed local changes" >&2
            echo "       hit a conflict in $path (conflict markers are in the tree)." >&2
            echo "  Resolve the files, then:  git add <files>  (then git stash drop)" >&2
            echo "  Or restore original state: git checkout HEAD -- <files> && git stash pop" >&2
            return 1
        fi
        echo "updated: $(git rev-parse --abbrev-ref HEAD) -> $(git log -1 --oneline)"
    else
        # 3. Conflict — stop and hand the operator a recovery path.
        echo "ERROR: pull/rebase hit a conflict in $path." >&2
        echo "  Resolve the files, then:  git rebase --continue" >&2
        echo "  Or roll back the pull:     git rebase --abort"   >&2
        echo "  Your stashed local work:   git stash list  (recover with: git stash pop)" >&2
        return 1
    fi
}
```

What this never does: no `git reset --hard`, no `git clean`, no removal of
untracked files, no automatic conflict resolution.

## Canonical script on this server

`/usr/local/bin/update-all-repos` is the menu-driven repo-update tool that
must exist on every managed server. It
must follow this doctrine: a porcelain dirty-check plus
`git pull --rebase --autostash`, never `git reset --hard` + `git clean -fd`.
The `sk-update-all-repos` script (`linux-site-deployment`) is the engine
version of the same tool and is held to the same standard.

If you find any repo-update script on a server still doing `git reset --hard`
or `git clean -fd`, that is a bug to fix, not a pattern to copy.

## Verify

```bash
# A repo-update script is safe iff this returns nothing:
grep -nE 'git[[:space:]]+reset[[:space:]]+--hard|git[[:space:]]+clean[[:space:]]+-fd' /usr/local/bin/update-all-repos

# And iff it pulls with autostash:
grep -n 'pull --rebase --autostash' /usr/local/bin/update-all-repos
```

## References

- [`references/safe-update-pattern.md`](references/safe-update-pattern.md)
- [`references/details.md`](references/details.md)
