# Container Image & Volume Hygiene — details

## Capability contract

Storage measurement and candidate listing are read-only. Every prune is destructive and requires explicit scope; `--volumes` requires separate confirmation from data owners. Scheduled cleanup requires authority to create and enable units.

## Degraded mode

Without engine access, return measurement commands only. If object ownership cannot be established, do not classify it as unused. If reclaim cannot be measured, report the result as unverified.

## Evidence produced

| Artefact | Acceptance |
|---|---|
| Reclaim evidence | Contains engine/user context, pre/post usage, candidate scope, approval, prune output, and timer status. |

Capture engine/user context, pre/post `system df`, filesystem free space, candidate list, approval for aggressive scopes, prune output, and timer status. Never call an unmeasured action successful.

## Quality standards

- Always run `system df` before pruning so the reclaim is measured, not guessed.
- Start with safe prunes; reserve `-a --volumes` for hosts you fully understand.
- Volumes hold data — never auto-prune volumes on a stateful host without review.

## Worked example

For rootless Podman pressure, inspect the affected user's store, preserve images referenced by stopped rollback containers, prune dangling build artefacts only, and compare both Podman and filesystem bytes before and after.

- The disk reclaimed (before/after `system df`).
- Exactly which objects were pruned (images/containers/volumes/networks/cache).
- Any scheduled timer installed and its next-run time.
