# ZFS replication reference

`zfs send` / `zfs receive` streams a dataset (or its deltas) to another
dataset — on the same host or across the network. This is ZFS-native
replication: checksummed, incremental, and resumable at snapshot granularity.

## Table of contents

1. Anatomy: send and receive
2. Local and remote replication
3. Recursive replication (`-R`)
4. Incremental replication
5. Offsite backup topology
6. Scheduling (systemd timer)
7. Verification and restore drill
8. Limits and gotchas

---

## 1. Anatomy: send and receive

```bash
# Snapshot to replicate from
zfs snapshot -r tank/@$(date +%Y-%m-%d_%H%M)

# Full send (first time) — target dataset must not exist yet
zfs send tank/data@snap1 | zfs recv backup/data

# Subsequent sends are incremental FROM the previous snapshot:
zfs send -i tank/data@snap1 tank/data@snap2 | zfs recv backup/data
```

Key points:

- The **target dataset** on the receiving side can have a different name
  (`backup/data`), but its ancestry must match the source's ancestry when you
  use `-R` (see gotchas).
- `zfs recv -n` dry-runs (no data written) — the destination pool must
  already exist; on success it is silent (exit 0), errors print to stderr.
- `zfs recv -F` destroys conflicting snapshots on the target — **destructive,
  confirm first**.

## 2. Local and remote replication

Local (same host, e.g., second pool for backups):

```bash
zfs send -i tank/data@prev tank/data@cur | zfs recv backup/data
```

Remote (over SSH; the remote side runs `zfs recv` as a privileged user):

```bash
zfs send -i tank/data@prev tank/data@cur | ssh backup@10.0.0.10 zfs recv tank-remote/data
```

Over a lossy/slow link, pipe through `gzip` or `zstd` (helps when the data
compresses well; hurts CPU):

```bash
zfs send -i tank/data@prev tank/data@cur | zstd | ssh backup@host "zstd -d | zfs recv tank-remote/data"
```

For very large transfers, stream to a file first (`-w`) so a dropped
connection does not restart from zero:

```bash
zfs send -w -i tank/data@prev tank/data@cur /tmp/repl.zfs
scp /tmp/repl.zfs backup@host:
ssh backup@host 'zfs recv tank-remote/data /tmp/repl.zfs'
```

## 3. Recursive replication (`-R`)

`-R` sends the dataset **and all descendants**, preserving the structure:

```bash
zfs send -R -i tank/@prev tank/@cur | ssh backup@host zfs recv -R backup/@cur
```

With `-R`, the target's path must mirror the source's *relative* structure
(`tank/data` → `backup/data`, `tank/data/web` → `backup/data/web`). Ancestry
must line up: you cannot incrementally `-R` into a target whose snapshot
history does not match.

## 4. Incremental replication

Incrementals are **snapshot-to-snapshot** — you can only send from a
snapshot that exists on the destination (or its chain). The retention policy
on the source therefore bounds how far back you can recover on the target.

Common cadence:

- hourly snapshots, keep 24
- daily snapshots, keep 14
- weekly snapshots, keep 8

Replicate the **daily** snapshot offsite (full `-R` on day 1, incremental
after); replicate hourly to a local staging pool if you need an RPO under an
hour.

## 5. Offsite backup topology

Typical hardened layout:

```
production host (tank)
   │  hourly  → local staging pool (mirror)     [RPO ≤ 1h, same site]
   │  daily   → offsite host via SSH (backup pool) [RPO 24h, other site]
   └  weekly  → cold archive (removable disk, stored off-site)
```

Rules:

- The offsite pool must be **at least as large** as the source (ZFS
  `used` is the number that matters, not capacity — see
  `zfs list -o used`).
- Encrypt in transit (SSH) and, for sensitive data, at rest
  (`encryption=aes-256-gcm` on the datasets — then the receiving host needs
  the key to import/use them).
- Keep at least one **restored copy** tested (see §7) — an untested backup
  is a hope, not a backup.

## 6. Scheduling (systemd timer)

Snapshot + replicate daily at 02:00, keep 14 daily / 8 weekly:

```ini
# /etc/systemd/system/zfs-daily-snapshot.service
[Unit]
Description=ZFS daily snapshot + offsite replication

[Service]
Type=oneshot
ExecStart=/usr/local/lib/zfs-daily-repl.sh
```

```bash
#!/bin/sh
# /usr/local/lib/zfs-daily-repl.sh
set -eu
ts=$(date +%Y-%m-%d_%H%M)
zfs snapshot -r "tank/@${ts}"

# replicate daily (incremental when possible)
last=$(zfs list -H -t snapshot -o name tank/data | sort | tail -n 2 | head -n 1 | cut -d@ -f2)
zfs send -R -i "tank/@${last}" "tank/@${ts}" | ssh backup@10.0.0.10 "zfs recv -R backup/@${ts}"

# retention: keep 14 daily + 8 weekly (weekly = Sundays)
zfs list -H -t snapshot -o name tank/data | cut -d@ -f2 | sort -r | \
  tail -n +15 | xargs -r -n1 sh -c 'zfs destroy "tank/data@"$0 2>/dev/null || true'
```

```ini
# /etc/systemd/system/zfs-daily-snapshot.timer
[Unit]
Description=Run ZFS daily snapshot+replication

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
systemctl enable --now zfs-daily-snapshot.timer
```

Also schedule the monthly scrub (same timer pattern, `OnCalendar=1st 03:00`):

```bash
zpool scrub tank
```

## 7. Verification and restore drill

Run **quarterly**, on a scratch dataset, not the production target:

```bash
# 1. Dry-run a recent incremental to prove the stream is valid
zfs send -R -i tank/data@prev tank/data@cur | zfs recv -n

# 2. Restore the latest snapshot to a scratch dataset
zfs send -R tank/data@latest | zfs recv scratch/restore
df -h /scratch/restore
# 3. Spot-check content (file counts, a known file's checksum)
find /scratch/restore -type f | wc -l
sha256sum /scratch/restore/<known-file>

# 4. Clean up
zfs destroy -r scratch/restore
```

Record the result (date, snapshot, verified file, duration) somewhere the
on-call can find it. A restore that has never been executed is unproven.

## 8. Limits and gotchas

| Gotcha | Detail |
|---|---|
| `recv` at the pool name | Receiving a dataset stream at the pool name (`zfs recv pool2`) maps the stream's root dataset onto the pool *root*. Always receive at the matching path (`zfs recv pool2/data`) |
| Ancestry mismatch with `-R` | Target snapshot history must match source history; if you re-archived, do a fresh full send |
| Target dataset exists | `zfs recv` fails unless the stream matches existing history; `-F` forces (destructive) |
| Encrypted datasets | The receiving host must be able to load the key, or receive with `encryption=on` and ship the key separately |
| `used` > target capacity | Replication fails mid-stream; size the target pool from `zfs list -o used`, not nominal capacity |
| Send from degraded source | Works, but the replica inherits the risk — fix the source first |
| Clock skew across hosts | Snapshot names are just labels (clock skew is cosmetic), but keep NTP healthy so retention math stays sane |
| `zfs send` of root dataset | Sending the pool root dataset is discouraged; send per top-level dataset instead |
