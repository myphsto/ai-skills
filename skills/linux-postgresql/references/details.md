# PostgreSQL Operations — details

## Capability contract

Inspection defaults to read-only host and database access. Initialization, role/data changes, config edits, reloads/restarts, archive writes, restores, and WAL replay require explicit authority. Credentials use the approved secret path and stay out of evidence.

## Degraded mode

Without cluster access, return version- and family-qualified commands only. Without workload evidence, do not recommend numeric tuning. Without an isolated restore or archived WAL access, separate backup creation from unassessed recovery.

## Evidence produced

| Artefact | Acceptance |
|---|---|
| PostgreSQL recovery evidence | Contains redacted auth/settings, cluster version, manifests/checksums, WAL health, restore logs, and reconciliation. |

Capture redacted effective settings and auth evidence, cluster/version output, manifests/checksums, WAL health, restore logs, reconciliation queries, and final service health.

## Quality standards

- Prefer `scram-sha-256` over `md5`/`trust` in `pg_hba.conf`.
- `shared_buffers` ~25% of RAM; `effective_cache_size` ~50–75% (a hint, not an allocation).
- Use `pg_dump -Fc` (custom format) so `pg_restore` can do selective/parallel restores.
- Record exact versions, cluster path, config source, checksum, restore target, and result.

## Worked example

For a one-hour RPO, confirm the archive command, take a base backup, preserve required WAL, restore to an isolated cluster, and recover to a timestamp inside the test window. `pg_basebackup` success alone is not PITR evidence.
