# Access Control — details

## Capability contract

Audit requests default to read-only. Read access to account and permission state is required; editing users, groups, keys, PAM, sudoers, SELinux mappings, or files requires explicit authority. Never expose private keys or revoke the last tested administrator.

## Degraded mode

Without privileged access, report observable state and exact root-level checks as `not assessed`. Without a safe second login or console, stop before lockout-capable changes.

## Evidence produced

| Artefact | Acceptance condition |
|---|---|
| Access-control evidence | Shows before/after identity state, key fingerprints, sudoers validation, affected modes, tested login/privilege behaviour, and approval. |

## Quality standards

- Prefer reversible, explicit changes over blanket permission fixes.
- Preserve SSH access and validate the impact before removing keys or users.
- Credential files must remain tightly permissioned.

## Worked example

To offboard a deployment user, record current groups, keys, processes, cron jobs, and owned files; disable login; verify the replacement automation identity; transfer required ownership; remove authorised keys; then confirm the account cannot authenticate while the service still deploys.
