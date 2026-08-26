# Disaster Recovery — details

## Capability contract

Read/search access may assess backups and recovery options. Decryption, filesystem repair, database replacement, bootloader/initramfs work, service stops, and destructive restores require explicit authority, protected credentials, and a recovery target. Never overwrite the sole surviving copy.

## Degraded mode

Fallback when restore verification is unavailable: report the narrowest recoverable scope and blocking gap. Missing checksums, keys, isolated space, capacity, or application validation mean the recovery point has not passed.

## Evidence produced

| Artefact | Acceptance |
|---|---|
| Backup qualification | Shows source, timestamp, checksum, decrypt test, and incident relation |
| Restore execution record | Includes approval, target backup, commands, before-state backup, and timestamps |
| Recovery validation | Proves application queries/files, service health, access, and residual data gap |

## Quality standards

- Restore the smallest correct scope first when possible.
- Use timestamps and incident facts to choose the backup, not guesswork.
- Verification after restore is mandatory.

## Worked example

A table was corrupted at 10:20 EAT. Verify and decrypt the 10:00 database backup into an isolated database, validate row counts and application queries, then restore only the affected database after approval. Keep a dump of the damaged live database for rollback and investigation.
