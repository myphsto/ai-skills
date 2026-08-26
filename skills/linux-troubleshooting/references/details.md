# Troubleshooting — details

## Capability contract

Default triage uses read/search access only. Restarts, deletes, rollbacks, package/config changes, database writes, firewall actions, and recovery operations require explicit authority after evidence identifies the failure mode.

## Degraded mode

Without logs, history, privileges, network probes, or reproduction, return the most specific supported failure-domain hypothesis and list unassessed branches. Do not close an incident because the symptom temporarily disappears.

## Evidence produced

| Artefact | Acceptance |
|---|---|
| Incident timeline | Records onset, impact, changes, commands, timestamps, and interventions |
| Failure-domain diagnosis | Cites discriminating evidence, alternatives ruled out, and confidence |
| Fix verification | Repeats the user-visible check plus service/resource checks and rollback result |

## Quality standards

- Diagnose from evidence, not intuition.
- Separate triage from final remediation until the failure mode is clear.
- Keep the path short and explicit so incidents stay understandable under pressure.

## Worked example

For a 502 after deployment, first capture proxy and upstream status, listeners, disk/memory, and matching logs. If Nginx is healthy but PHP-FPM is absent due to invalid config, validate that config and route the bounded service fix; do not restart the whole host.
