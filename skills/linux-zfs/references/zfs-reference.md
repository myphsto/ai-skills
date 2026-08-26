# ZFS command reference

Command cookbook for ZFS pools and datasets. All commands are identical on
Debian/Ubuntu and the RHEL family; only the install path differs.

## Table of contents

1. Install and verify
2. Vdev layouts
3. Pool create / import / export
4. Datasets and properties
5. Snapshots, clones, rollback
6. Pool health and maintenance
7. Memory (ARC)
8. Troubleshooting

---

## 1. Install and verify

Debian/Ubuntu:

```bash
apt install zfsutils-linux
```

RHEL family (EPEL required on RHEL 8/9/10; Fedora ships it in the base repo):

```bash
dnf install epel-release        # RHEL 8/9/10 only
dnf install kmod-zfs zfsutils-linux
```

Verify the module matches the running kernel:

```bash
uname -r
modinfo zfs | grep ^version
systemctl enable --now zfs.target   # the unit is zfs.target, not zfs.service
zpool version    # prints the ZFS on-disk version
```

If `modinfo zfs` version != `uname -r`, the module is stale — install the
matching `kmod-zfs` (or reboot) before doing anything else.

## 2. Vdev layouts

A pool is a set of **vdevs** (virtual devices). Failure tolerance is
per-vdev: a vdev fails when its layout's tolerance is exceeded.

| Vdev | Disks | Survives | Notes |
|---|---|---|---|
| single | 1 | none | testing only; state the risk explicitly |
| mirror | 2, 4, 6… | (n/2 − 1) | read speed ≈ fastest member; write ≈ single disk |
| RAIDZ1 | 3–9 | 1 | space eff ≈ (n−1)/n |
| RAIDZ2 | 4–10 | 2 | better parity; slower writes |
| RAIDZ3 | 5–16 | 3 | large disks / high durability |
| log (ZIL) | 1–2 SSD | per its own layout | reduces sync-write latency; small and fast |
| cache (L2ARC) | SSD | n/a | read cache for >memory workloads |
| spare | 1+ | hot spare for auto-replace | `zpool create tank … spare /dev/sdX`; auto-activates on vdev failure (Linux has no `zpool fail` — failure is detected by I/O errors) |

Rules of thumb:

- Keep vdevs within a pool the same size — pool capacity is the sum of the
  smallest member per vdev. Mixed-size mirrors are rejected; pass
  `zpool create -f` to force it (capacity = smallest member). `zpool attach`
  requires the new device to be at least as large as the one mirrored.
- **Never add a disk to an existing vdev** to "make it bigger" — you add a
  **new vdev** (stripe across vdevs reduces overall tolerance to the weakest
  vdev).
- `ashift` (sector size): modern 4Kn disks auto-detect; force `ashift=12`
  only when you have verified the disks are 4Kn-native.

## 3. Pool create / import / export

```bash
# Two mirrors (4 disks): survives one failure per mirror
# (-O sets dataset properties; -o sets pool properties — compression is a
#  dataset property, so -O)
zpool create -O compression=lz4 backup \
  mirror /dev/sdb /dev/sdc \
  mirror /dev/sde /dev/sdf

# RAIDZ2 with a log vdev and a hot spare (6 data disks + SSD + spare)
zpool create -O compression=lz4 tank \
  raidz2 /dev/sdb /dev/sdc /dev/sde /dev/sdf /dev/sdh \
  log /dev/nvme0n1 \
  spare /dev/sdg

# Inspect
zpool create -n scratch mirror /dev/sdb /dev/sdc   # dry run: simulates, changes nothing
zpool status
zpool list
zpool get all tank | less
```

Import / export (e.g., moving a pool between hosts):

```bash
zpool export tank                 # clean off a host
zpool import tank                 # auto-detect
zpool import -d /dev/disk tank    # non-standard device paths
zpool import -R /newroot tank     # remount datasets under /newroot
zpool import -f tank              # force (only if you are sure)
# rename a pool: export, then import under the new name (no `zpool rename`)
zpool export tank
zpool import tank newname
```

**Creating a pool wipes the listed disks.** Confirm each device by serial and
model before running.

## 4. Datasets and properties

```bash
zfs create tank/data
zfs create -o quota=2T -o refquota=200G tank/data/project1
zfs destroy tank/data/project1          # destroys dataset + snapshots
zfs rename tank/data tank/files         # no data movement
zfs mount / zfs unmount tank/data
zfs set mountpoint=/srv/data tank/data
```

Properties worth setting:

```bash
zfs set compression=lz4 tank/data        # near-free, usually 1.3-2x savings
zfs set atime=off tank/data              # avoid atime write amplification
zfs set quota=10T tank/data              # hard limit, whole subtree
zfs set refquota=500G tank/data/project1 # hard limit, this dataset only
zfs set readonly=on tank/data           # immutable (set after snapshot you want to protect)
zfs set acltype=posix tank/data         # or nfsv4 for NFS ACLs
zfs set xattr=sa tank/data              # safer xattr storage
```

Encryption (create-time only, cannot be added later):

```bash
zfs create -o encryption=aes-256-gcm -o keyformat=passphrase -o keylocation=prompt tank/secure
# or keylocation=file:///etc/zfs/keys/secure.key (chmod 600, backed up off-box)
zfs load-key tank/secure        # at boot / after reboot
zfs unmount tank/secure && zfs unload-key tank/secure   # must unmount first, else "busy"
```

Encrypted datasets cannot be sent across hosts unless the receiving side
imports the key (`-o encryption=on` on the target dataset or key send via
`zfs key`).

## 5. Snapshots, clones, rollback

Snapshot naming convention: `<dataset>@<YYYY-MM-DD_HHMM>` — keep it
sortable.

```bash
zfs snapshot tank/data@2026-08-25_0200
zfs snapshot -r tank/data@nightly        # recursive: snapshots every descendant dataset with the same name
zfs list -t snapshot
zfs destroy tank/data@2026-08-25_0200
zfs hold protect tank/data@nightly       # prevent destroy
zfs holds tank/data@nightly              # list holds (takes a snapshot, not a dataset)
zfs release protect tank/data@nightly    # remove a hold

# Clone (instant, shares blocks; lives as a writable dataset)
zfs clone tank/data@nightly tank/data-dev
zfs destroy -R tank/data-dev             # -R if it gained snapshots/children (clones inherit origin snapshots)
zfs promote tank/data-dev                # decouple from origin (clone becomes independent);
                                          # the base snapshot moves to the promoted dataset
                                          # (tank/data@nightly -> tank/data-dev@nightly)

# Rollback (destroys changes made after the snapshot — confirm first)
zfs rollback tank/data@2026-08-25_0200
zfs rollback -r tank/data@2026-08-25_0200   # -r destroys newer snapshots
```

Bulk snapshots via a helper (common pattern):

```bash
ts=$(date +%Y-%m-%d_%H%M)
zfs snapshot -r "tank/@${ts}"
# keep last 7 daily:
zfs list -H -t snapshot -o name | awk -F@ '{print $2}' | sort -r | tail -n +8 | \
  xargs -r -n1 sh -c 'zfs destroy "tank/data@"$0 2>/dev/null || true'
```

## 6. Pool health and maintenance

```bash
zpool status                  # the command to memorize
zpool iostat -v               # per-device throughput
zpool scrub tank              # checksum pass; run monthly
zpool scrub -s tank           # pause
zpool status                  # shows scrub progress + checksum errors

# Disk lifecycle (offline/online only work on redundant vdevs — a single
# disk pool reports "no valid replicas")
zpool offline tank /dev/sdc   # planned removal
zpool online tank /dev/sdc    # bring back
zpool replace tank /dev/sdc /dev/sdi   # hot-swap a failed disk (resilvers automatically;
                                       # the old device is removed when the replace finishes —
                                       # no zpool remove needed)
# zpool fail <pool> <dev> exists on FreeBSD/Solaris only — NOT available on Linux
zpool remove tank /dev/sdh    # remove a top-level vdev you added with zpool add
zpool expand tank             # after replacing with a larger disk in a mirror
zpool add tank mirror /dev/sdg /dev/sdh   # new vdev (stripe)
zpool attach tank /dev/sdb /dev/sdc       # mirror an existing single disk (new device must be >= existing size)
zpool detach tank /dev/sdc    # undo an attach
zpool resilver tank           # after clearing a stuck resilver (last resort)
```

Fault tolerance per layout: single = 0, mirror(2) = 1, RAIDZ1 = 1,
RAIDZ2 = 2, RAIDZ3 = 3. A pool is **DEGRADED** at tolerance, **FAULTED**
beyond it. Beyond tolerance, data on the lost vdevs may be gone — stop and
assess before any further mutation.

## 7. Memory (ARC)

```bash
# ZFS tunables live in /sys/module/zfs/parameters/ (there is no sysctl
# interface for ZFS on Linux)
cat /sys/module/zfs/parameters/zfs_arc_max
arc_summary                # quick ARC health summary (2.4.x: zarcsummary)
# cap ARC at 75% of RAM (runtime):
echo $(awk '{print int($2*0.75/1024)}' /proc/meminfo) > /sys/module/zfs/parameters/zfs_arc_max
# persist the cap across reboots:
echo "options zfs zfs_arc_max=$(( `grep MemTotal /proc/meminfo | awk '{print int($2*0.75/1024)}' ))" \
  > /etc/modprobe.d/zfs.conf
```

ARC grows up to ~75–80% of available RAM by default. On a box that is also a
database or container host, cap it with `zfs_arc_max` (tunable, or
`/etc/modprobe.d/zfs.conf` for persistence).

## 8. Troubleshooting

| Symptom | First checks |
|---|---|
| Pool DEGRADED | `zpool status` → failed/FAULTED device; `zpool replace` the disk; watch resilver |
| Resilver stuck at 0% | device not actually replaced; `zpool status -v`; check `dmesg` for I/O errors on the new disk |
| `cannot import: no such pool` | wrong device paths (`-d`), disk labels wiped, or pool was created on a different host with `hostid` |
| Module stale after kernel update (RHEL) | `modinfo zfs | grep version` vs `uname -r`; install matching `kmod-zfs` or reboot |
| Checksum errors appearing in scrub | failing disk (replace), or memory issue (`mce`, RAM test); errors on a single device → replace that device |
| Disk full but quota shows room | quota is per-dataset; check `zfs list -o name,used,quota,refquota` and `zfs used` (ref vs used) |
| Dataset won't mount | `zfs get mountpoint,locked,readonly tank/data`; encrypted? `zfs load-key`; `zfs mount -a` |
