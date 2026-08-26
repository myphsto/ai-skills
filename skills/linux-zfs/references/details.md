# ZFS: Pools, Datasets, Snapshots, Replication — details

## Capability contract

Read-only inspection (`zpool status`, `zfs list`) is always allowed. Creating,
destroying, scrubbing, replacing disks, and replication are mutating and
require explicit authority. `zpool destroy` and wiping a disk are
destructive — require typed confirmation.

## Degraded mode

If `zpool status` shows a pool degraded/faulted, stop all provisioning work on
that pool, report the state with the failed device, and route to the
Health & Maintenance section. Do not create new datasets or replicate from a
degraded pool without the user accepting reduced durability.

## Evidence produced

| Category | Artefact | Acceptance condition |
|---|---|---|
| Pool health | `zpool status` output | ONLINE, no FAILED devices, resilver complete. |
| Dataset state | `zfs list` + property dump | Compression, quotas, mount points as agreed. |
| Replication | `zfs get replicated` on target | Target dataset present with matching snapshot. |

## Quality standards

- Never wipe a disk that shows a filesystem or partition without explicit
  confirmation naming that disk.
- State failure tolerance in plain language before creating any pool.
- Run `zpool scrub` after creation and after any disk replacement; schedule
  recurring scrubs.
- Verify end state (`zpool status`, test I/O, mount check) before declaring
  success.

## Worked example

"Put these four 16 TB drives into a pool for offsite backups" → inventory
confirms four unformatted 16 TB disks → layout: two mirrors (tolerates one
failure per mirror), `zpool create -o compression=lz4 backup mirror /dev/sdb
/dev/sdc mirror /dev/sde /dev/sdf` → dataset `backup/daily` with quota →
test write → `zpool scrub backup` → snapshot cadence via systemd timer →
verify `zpool status` ONLINE and dataset mounted.
