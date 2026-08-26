# Log Management — details

## Capability contract

Read/search access to journals and log files is sufficient for analysis. Rotation changes, vacuuming, deletion, permission changes, and service reloads require explicit authority; shared evidence must redact secrets and personal data.

## Degraded mode

Fallback when required access is unavailable: report the exact time/source coverage and mark missing periods unassessed. Never equate absent or rotated logs with absence of an event.

## Evidence produced

| Artefact | Acceptance |
|---|---|
| Time-bounded log extract | Names source, host, timezone, command, and redactions |
| Correlation record | Links the conclusion to timestamps/request IDs and states uncertainty |
| Rotation verification | Includes `logrotate` debug/forced-test result and post-change disk state |

## Quality standards

- Use time-bounded inspection instead of dumping entire logs.
- Prefer concrete log evidence over speculation.
- Keep rotation and retention changes deliberate.

## Worked example

For an Nginx 502 spike from 14:00–14:10 EAT, extract only that access/error interval, correlate upstream errors with PHP-FPM journal entries, and preserve request IDs. If older logs rotated, mark earlier onset unassessed rather than declaring 14:00 the start.
