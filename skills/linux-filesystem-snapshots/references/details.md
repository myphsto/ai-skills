# Filesystem Snapshots (LVM / ZFS / Btrfs) — details

## Capability contract

Topology and capacity inspection are read-only. Snapshot creation/deletion, application quiesce, send/receive, mount, and rollback require explicit storage authority. Rollback is destructive and requires separate confirmation naming the exact target and discarded interval.

## Degraded mode

Without storage access, provide technology-qualified commands only. Without application quiesce evidence, label consistency crash-only. Without COW monitoring or a replication target, do not call the snapshot a backup.

## Evidence produced

| Artefact | Acceptance |
|---|---|
| Snapshot evidence | Contains topology/capacity, quiesce proof, listing, mount/read, replication/integrity, and cleanup or rollback. |

Capture topology, free/COW space, quiesce evidence, snapshot listing, mount/read test, replication status, integrity result, and final cleanup or rollback checks.

## Quality standards

- Treat a snapshot as a *consistency tool*, not a backup. Always copy off-host.
- Size LVM COW space generously and monitor `lvs` `Data%` — a full COW snapshot
  is silently invalidated.
- Quiesce or use `--single-transaction` dumps for databases; a raw snapshot of
  a busy DB can still be mid-transaction.

## Worked example

For an LVM-backed database, invoke the approved quiesce hook, create a monitored short-lived snapshot, resume writes, back up from the read-only mount, verify the copy, then remove the snapshot before COW pressure grows.

- The snapshot created (LV/subvolume/dataset name) and how it was made.
- How the data was moved offsite (tar/rsync/send) or that rollback was used.
- Confirmation the snapshot was released and free space reclaimed.
