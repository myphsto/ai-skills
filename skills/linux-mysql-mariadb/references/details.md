# MySQL & MariaDB Operations — details

## Capability contract

Diagnostics default to read-only database and host access. Package changes, SQL writes, config edits, restarts, backup rotation, restores, and binlog replay require explicit authority. Credentials must come from the approved secret provider and never appear in commands or evidence.

## Degraded mode

Without database access, return version-specific commands and label values unverified. Without workload evidence, do not prescribe numeric tuning. Without an isolated restore target, mark recovery `not proven`.

## Evidence produced

| Artefact | Acceptance |
|---|---|
| Database recovery evidence | Contains redacted config/version, backup checksum, binlog coordinates, restore logs, reconciliation, and health result. |

Capture redacted variables/config, server version, backup checksum and manifest, binlog coordinates/retention, restore logs, reconciliation counts, and final health checks.

## Quality standards

- Tune via a numbered drop-in file; keep the packaged config pristine.
- Always `--single-transaction` for InnoDB dumps (consistent, non-locking).
- A backup you have not test-restored is not a backup.
- Evidence identifies engine/version, config source, checksum, restore target, and recovery result while redacting credentials.

## Worked example

For a MariaDB service with a 15-minute RPO, take a consistent dump, record its binlog position, restore it to scratch, and replay to a chosen timestamp. Do not claim PITR until replay and reconciliation pass.
