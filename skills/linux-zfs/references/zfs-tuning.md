# ZFS tuning reference

Workload tuning for ZFS pools and datasets: module parameters, cache
(ARC/L2ARC), the log device (SLOG), block sizes, and compression. Defaults
are well reasoned — tune only against measured workload evidence, and record
before/after numbers.

## Table of contents

1. Where the knobs live
2. ARC (main memory cache)
3. L2ARC (secondary read cache)
4. SLOG (log device) and sync writes
5. TXG and dirty data limits
6. Block sizes: recordsize and volblocksize
7. Compression
8. 2.4.x tuning parameters
9. Tools (snapshots and replication automation)
10. What not to tune
11. Sources

---

## 1. Where the knobs live

Runtime (per-boot): `/sys/module/zfs/parameters/<name>` — inspect with
`cat /sys/module/zfs/parameters/<name>` (there is no sysctl interface for
ZFS on Linux).

Persistent (survives reboot), Linux:

```bash
echo "options zfs zfs_arc_max=21474836480" > /etc/modprobe.d/zfs.conf
# e.g. cap ARC at 20 GiB
```

Proxmox uses the same `/sys/module/zfs/parameters` tree; the GUI exposes some
of it, but the files are the source of truth.

## 2. ARC (main memory cache)

ARC holds compressed blocks, so 64 GB of RAM can serve well over 64 GB of
logical data. It reclaims space automatically; it does not need manual
sizing in most cases.

```bash
# monitor (2.1.x/2.2.x: arc_summary; 2.4.x adds zarcstat/zarcsummary)
arc_summary
grep -E '^(size|hits|misses) ' /proc/spl/kstat/zfs/arcstats   # raw counters
```

- **Hit ratio** is the number to watch: target ≥ 90–95% on a busy pool. A
  falling hit ratio means the working set outgrew RAM — add RAM, add L2ARC
  (HDD pools only), or accept disk I/O.
- `zfs_arc_max` — cap ARC when the host also runs databases/VMs that need
  guaranteed memory. Do **not** use `zfs_arc_min` (it prevents ARC from
  giving memory back).
- On a shared host, cap ARC and verify the tenant workloads still have what
  they need; measure, don't guess.

## 3. L2ARC (secondary read cache)

A **read-only** overflow cache for ARC: it never improves write performance,
and it only helps when the read working set is larger than RAM on a pool
backed by slower (HDD) devices. All-flash pools rarely benefit — the disks
are already faster than the cache would be useful.

Guidance (community consensus, treat as Tier 4):

| Parameter | Purpose |
|---|---|
| `l2arc_rebuild_enabled` | Keep L2ARC content across reboots — warm cache at boot and less rewrite wear. Recommended if you use L2ARC. |
| `l2arc_write_max` | Sustained write limit to the device (protects against one-pass sequential streams evicting useful data). |
| `l2arc_write_boost` | Temporary boost while the device warms up. |
| `l2arc_mfuonly` | Accept only most-frequently-used data, not most-recently-used. |
| `l2arc_exclude_special` | Don't cache into L2ARC what already sits on an equally fast special vdev (both NVMe). |

Rules: the device must be faster than the data vdevs; use NVMe (or a fast
SATA SSD for older HDD pools); it stores copies of data that already exists
on redundant vdevs, so it does not need its own redundancy. Add or remove
with `zpool add pool cache <dev>` / `zpool remove pool <dev>` — safe online.

## 4. SLOG (log device) and sync writes

ZFS batches writes into transaction groups (TXGs, ~5 s) — async writes get
sequential-write throughput. **Sync writes** (apps that demand immediate
durability: databases, some NFS/SMB clients) bypass the batching and land
where the ZIL lives: on the pool itself unless a log vdev exists.

- Only add a SLOG for workloads with sustained **sync** writes. Check whether
  the workload actually does them (e.g. `zpool iostat -v` log row, or the
  application's sync usage). Most home-lab and general file workloads never
  need one.
- Sizing: 8–16 GB is enough (it only holds ~5 s of sync writes). The device
  needs high write endurance and fast random writes — enterprise NVMe or a
  mirrored pair. A slow SLOG degrades performance; if in doubt, omit it.
- 2.4.x: the ZIL may live on a **special vdev** (parameter
  `zil_special_is_slog`) — one fast device can then serve both small-block
  and log duties.
- `sync=disabled` per dataset makes ZFS lie about durability (data lives in
  RAM until TXG commit). Only for data that is cheap to rebuild, and only
  with the user's explicit acceptance of the risk. `sync=always` forces
  everything through the log — for testing, not for production.

## 5. TXG and dirty data limits

Pseudo-write-cache knobs — advanced, and the commit flush can spike CPU
(compressing 30 GB of dirty data at once has locked hosts). Use only with
headroom and monitoring:

| Parameter | Purpose |
|---|---|
| `zfs_txg_timeout` | TXG commit interval (default 5 s). Higher = quieter disks, more data in volatile memory. |
| `zfs_dirty_data_max` | Absolute cap on dirty data held in memory. |
| `zfs_dirty_data_max_percent` | Same, as a fraction of RAM. |

## 6. Block sizes: recordsize and volblocksize

Set per dataset at creation; **immutable after creation**.

- `recordsize` (datasets): default 128K. Smaller (16–32K) for workloads that
  touch lots of small blocks (databases with small records); larger (256K–1M)
  for sequential media. Wrong-and-large = wasted space and read amplification
  on small updates; wrong-and-small = more metadata, more IOPS for large
  files.
- `volblocksize` (zvols): match the guest filesystem's cluster size — 4K for
  NTFS/ext4 guests, 16K is a common Proxmox/VM middle ground. A 128K
  volblocksize forces reading 8 blocks to fetch a 1 MB file's worth of
  4K-aligned data; 4K volblocksize forces 256 blocks for the same file.
  Proxmox's defaults are reasonable; don't change them without a measured
  reason.
- `special_small_blocks` must be **lower** than the dataset recordsize to be
  meaningful (e.g. `special_small_blocks=64k` with 256K+ recordsize).

## 7. Compression

- `lz4` is the default recommendation: near-free CPU, real savings on VM
  images and general data.
- `zstd` when the pool stores highly compressible archival data or the host
  has CPU to spare; measure before assuming it wins.
- Enable at the pool or parent-dataset level so children inherit; Proxmox
  guides the same: `zfs set compression=on <pool>/vmdata` for VM storage.
- Deduplication: **off**. RAM cost scales with data volume and the DDT is a
  single point of failure for the pool; compression covers most of the
  savings use case.

## 8. 2.4.x tuning parameters

New in the 2.4 series (OpenZFS 2.4.4, Aug 2026, is the current stable;
kernels 4.18–7.2 supported):

| Parameter | Purpose |
|---|---|
| `zfs_dio_strict` | strictness of direct I/O alignment handling |
| `vdev_read_sit_out_secs` | auto "sit out" of abnormally slow vdevs (autosit) — removes a slow member from I/O instead of waiting on it |
| `vdev_raidz_outlier_check_interval_ms` / `vdev_raidz_outlier_insensitivity` | rate/leniency of outlier (slow disk) detection in RAIDZ |
| `zfs_spa_flush_txg_time` / `zfs_spa_note_txg_time` | TXG timing controls |
| `metaslab_perf_bias` | allocation bias toward faster vdevs in mixed pools |
| `zil_special_is_slog` | allow the ZIL on a special vdev |
| `zfs_delete_dentry` / `zfs_delete_inode` | dentry/inode cache management |

New 2.4 operations worth knowing: `zpool scrub -a` (all pools),
`zfs rewrite -P` (preserve birth time, smaller incremental streams), and the
`send:encrypted` delegation permission for encrypted replication.

## 9. Tools (snapshot and replication automation)

- **zfs-auto-snapshot** — cron-based hourly/daily/weekly/monthly snapshots
  with retention. Simple; fine for one host.
- **sanoid + syncoid** — policy-driven snapshots and replication to remote
  hosts with retention, compression, and resume; the de-facto standard for
  ZFS backup topologies. Prefer these over hand-rolled scripts when the
  topology outgrows a one-liner.
- Proxmox: the `zfspool` storage backend (sparse zvols, per-VM subvolumes,
  native snapshot/clone). For encrypted replication in Proxmox, data is sent
  without encryption properties and the target determines encryption — plan
  key handling on every node.

## 10. What not to tune

- Don't add L2ARC to an all-flash pool "because it's fast" — measure first;
  it usually does nothing useful there.
- Don't add a SLOG for a pool that has no sync-write workload.
- Don't disable sync pool-wide to chase benchmark numbers.
- Don't enable deduplication "for the savings".
- Don't tune `recordsize`/`volblocksize` after the fact — they're immutable;
  the fix is a new dataset and a copy.
- Don't tune before measuring: capture `zpool iostat -v`, ARC stats, and the
  workload's I/O pattern first, then change one knob at a time.

## 11. Sources

- OpenZFS 2.4.4 release notes (Aug 21, 2026) — [github.com/openzfs/zfs/releases](https://github.com/openzfs/zfs/releases) (Tier 2)
- OpenZFS 2.4.0 release notes — [github.com/openzfs/zfs/releases/tag/zfs-2.4.0](https://github.com/openzfs/zfs/releases/tag/zfs-2.4.0) (Tier 2)
- OpenZFS Module Parameters docs — [openzfs.github.io](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Module%20Parameters.html) (Tier 2)
- Proxmox VE Storage: ZFS — [pve.proxmox.com/wiki/ZFS](https://pve.proxmox.com/wiki/ZFS) (Tier 2)
- Level1Techs "ZFS Guide for starters and advanced users" (Exard3k, with
  corrections in-thread) — [forum.level1techs.com/t/196035](https://forum.level1techs.com/t/zfs-guide-for-starters-and-advanced-users-concepts-pool-config-tuning-troubleshooting/196035) (Tier 4 — community guide; used for ARC/L2ARC/SLOG/special-vdev tuning heuristics, corroborated against the Tier 2 docs above where possible)
- Daniele Messi, "Proxmox ZFS Performance Tuning 2026" — [daniele-messi.com](https://daniele-messi.com/en/blog/proxmox-zfs-performance-tuning-2026-optimize-home-lab-storage) (Tier 4 — blog; used only for the lz4/ARC-hit-ratio/dedup-off consensus, which matches the Tier 2 docs)
