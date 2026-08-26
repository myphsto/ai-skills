---
name: linux-zfs
description: "Use when creating or managing ZFS pools, choosing vdev layouts (mirror, RAIDZ, stripe), setting dataset properties (compression, quotas, ACLs, encryption), taking ZFS snapshots or clones, replicating with zfs send/receive, or diagnosing pool health (scrub, resilver, disk replacement) on Debian/Ubuntu or the RHEL family."
license: MIT
compatibility: "Linux (Debian/Ubuntu or RHEL family); root required; zfsutils-linux + matching kernel module (EPEL kmod-zfs on RHEL)"
metadata:
  author: myphsto
  version: "1.0"
---

# ZFS: Pools, Datasets, Snapshots, Replication

## Distro support

ZFS is **out-of-tree** on both families. The commands themselves are
identical; only the install path and kernel-module lifecycle differ.

| Concept | Debian/Ubuntu | RHEL family |
|---|---|---|
| Install | `apt install zfsutils-linux` | `dnf install kmod-zfs zfsutils-linux` (EPEL) or `dnf install zfs` (Fedora) |
| Kernel module | built automatically on kernel upgrades | `kmod-zfs` must match the running kernel — a kernel upgrade can leave the module **stale** until EPEL ships the match |
| Mount service | `zfs-mount` | `zfs-mount` (plus `zfs-import`) |
| Root filesystem | keep `/` on ext4/xfs; ZFS for additional storage | same |
| Day-to-day tools | `zpool`, `zfs` | identical |

Version note: OpenZFS **2.4.4** (Aug 2026) is the current stable, supporting
Linux kernels 4.18–7.2. Distro repos commonly still ship 2.2.x/2.3.x — check
`zfs version` before assuming a feature (e.g., 2.4's slow-vdev "sit out",
ZIL on special vdevs, `zpool scrub -a`, `zarcstat` naming).

**Rules of the road**

- Never put `/` on ZFS on a running server — that requires reinstalling into
  the new root. ZFS here manages **additional** disks (NAS, backups, VM
  storage, shared data).
- Expect ARC to hold a large share of RAM (tunable via
  `org.zfs.zfs.arc_max`). Size the pool host accordingly.
- On the RHEL family, after **every** kernel update run
  `systemctl restart zfs` (or reboot) and confirm `zpool status` still
  reports healthy — a stale module is the #1 post-upgrade failure.

## Use when

- Creating a ZFS pool from a set of disks and choosing the vdev layout.
- Managing datasets: compression, quotas, ACLs, encryption, mount options.
- Taking, cloning, or rolling back ZFS snapshots.
- Replicating datasets to another host or disk with `zfs send` / `zfs recv`.
- Diagnosing pool health: scrub, resilver, replacing a failed disk, expanding.
- Tuning ARC, L2ARC, SLOG, block sizes, or compression for a specific workload.

## Do not use when

- The filesystem is Btrfs (subvolumes, `btrfs send`) — use `linux-filesystem-snapshots`.
- The task is plain block-level work (partitions, LVM, ext4/XFS, RAID via mdadm) — use `linux-disk-storage`.
- You only need a conceptual comparison of snapshot technologies — `linux-filesystem-snapshots` covers the comparison table.

## Required inputs

| Artefact | Source | Required? | If absent |
|---|---|---:|---|
| Target disks and their intended use | `lsblk` + user | yes | List candidates with `lsblk -o NAME,SIZE,MODEL,FSTYPE,STATE` and ask which ones may be wiped. |
| Availability requirement (tolerate 1 / 2 / n failures) | User | yes | Ask — it decides mirror vs RAIDZ width. Never guess. |
| Pool name and mount layout | User | yes | Propose a name (`tank`, `backup`, `nas`) and a mount root, require confirmation. |
| Encryption need | User | conditional | Default to unencrypted with a note; require explicit yes for `encryption=on`. |

## Decision rules

| Situation | Choose | Why |
|---|---|---|
| 1 disk | no pool (or single-disk pool, explicitly accepted as no redundancy) | RAIDZ needs ≥3; a single disk is a risk the user must accept |
| 2–4 disks | mirrors (pairs) | simplest, fastest, replace any one |
| 5–8 disks | RAIDZ1 | survives one disk, good space efficiency |
| 9+ disks, durability priority | RAIDZ2 (or mirrored vdevs in a stripe) | survives two simultaneous failures |
| High write latency / transactional workloads | add a dedicated `log` vdev (SSD) | ZIL on SSD removes write sync latency |
| Space efficiency over speed, many small files | `compression=lz4` | near-free CPU cost, usually 1.3–2× savings |
| Deduplication | off | huge RAM cost, rarely worth it; state why when asked |
| recordsize / volblocksize | 128K default datasets; match zvol volblocksize to guest FS cluster (4K/16K typical for VMs) | immutable after creation — wrong choice means recreate + copy |
| ARC sizing | leave default; cap with `zfs_arc_max` only on shared hosts | target ARC hit ratio ≥ 90–95%; never set `zfs_arc_min` |

## Workflow

1. **Inventory** — `lsblk -o NAME,SIZE,MODEL,FSTYPE,STATE` plus
   `blkid`. Confirm every target disk has no filesystem/partitions you need.
   **Wiping a disk is destructive — confirm explicitly before any
   `zpool create` on it.**
2. **Layout** — pick vdev layout from Decision Rules; state the failure
   tolerance it gives in plain language.
3. **Create** — `zpool create` (see reference). Set
   `ashift=12` only if disks are >4Kn-native and you know it; modern tools
   auto-detect.
4. **Datasets** — create the datasets the workloads need; set
   `compression=lz4`, quotas, `atime=off` where appropriate.
5. **Verify** — `zpool status`, `zpool list`, `zfs list`, write/read a test
   file, confirm mount point.
6. **Protect** — establish a snapshot cadence and (if requested) replication.
7. **Maintain** — schedule monthly `zpool scrub` (timer/cron), and on RHEL,
   verify the module after every kernel update.

## Outputs

| Artefact | Consumer | Acceptance condition |
|---|---|---|
| Pool layout decision | Operator | Vdev layout, disk list, failure tolerance stated and confirmed. |
| Pool + datasets | Workloads | `zpool status` ONLINE, datasets mounted, test I/O verified. |
| Snapshot/replication policy | Operator | Cadence, retention, and restore test documented. |

## Anti-patterns

- RAIDZ across 2 disks. Fix: mirrors for 2–4 disks, RAIDZ1 starts at 3.
- Deduplication "because it saves space". Fix: off by default; explain the RAM
  cost and use compression instead.
- Replicating to a smaller or slower disk than the source without saying so.
  Fix: state capacity and performance impact first.
- Declaring a pool healthy from a clean `zpool create` exit code. Fix:
  `zpool status` + scrub + test I/O.
- Skipping the RHEL module check after a kernel update. Fix: `modinfo zfs |
  grep version` vs running kernel, `zpool status` healthy.
- Adding L2ARC or a SLOG "because it's fast" without a measured need. Fix:
  L2ARC is a read-only cache that only helps HDD pools with a read working
  set larger than RAM; a SLOG only helps workloads with sustained sync
  writes. Measure first (see tuning reference).

## References

- [`references/zfs-reference.md`](references/zfs-reference.md) — pool and
  dataset command cookbook: layouts, properties, snapshots, clones, expand,
  replace, encryption.
- [`references/zfs-replication.md`](references/zfs-replication.md) —
  `zfs send`/`recv` patterns, incremental replication, offsite topology,
  scheduling, and restore-from-replica drills.
- [`references/zfs-tuning.md`](references/zfs-tuning.md) — ARC/L2ARC/SLOG
- [`references/details.md`](references/details.md)
  tuning, TXG/dirty-data limits, recordsize and volblocksize, compression,
  2.4.x parameters, and sanoid/syncoid + Proxmox notes.
