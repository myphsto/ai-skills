---
name: linux-image-hygiene
description: "Use when measuring or reclaiming Docker/Podman storage and scheduling safe cleanup on Debian/Ubuntu or RHEL-family hosts. Covers images, cache, networks, and authorised volume pruning; use linux-container-engine for engine setup."
license: MIT
compatibility: "Linux (Debian/Ubuntu or RHEL family); root for most operations"
metadata:
  author: myphsto
  version: "1.0"
  source: "https://github.com/peterbamuhigire/linux-skills"
---

# Container Image & Volume Hygiene

This skill owns **disk reclamation**. It does not own installing the engine
(`linux-container-engine`) or running containers (`linux-container-deployment`).

## Distro support

Two-family skill. The prune commands are nearly identical between Docker and
Podman; the differences are storage location (Docker keeps everything under
`/var/lib/docker`; rootless Podman under `~/.local/share/containers`) and that
on RHEL you usually drive Podman. The body below shows Docker on Debian/Ubuntu;
substitute per this matrix.

| Concept | Debian/Ubuntu | RHEL family |
|---|---|---|
| Disk usage report | `docker system df` | `podman system df` |
| Prune (safe: dangling + stopped) | `docker system prune` | `podman system prune` |
| Prune everything unused | `docker system prune -a --volumes` | `podman system prune -a --volumes` |
| Unused images only | `docker image prune -a` | `podman image prune -a` |
| Dangling images only | `docker image prune` | `podman image prune` |
| Unused volumes | `docker volume prune` | `podman volume prune` |
| Unused networks | `docker network prune` | `podman network prune` |
| Storage root | `/var/lib/docker` | `/var/lib/containers` (root) / `~/.local/share/containers` (rootless) |
| Schedule | `systemd` timer (system) | `systemd` timer; rootless uses `--user` + linger |

**RHEL-family notes:** rootless Podman storage is per-user under
`~/.local/share/containers/storage` — a `docker system prune` as root will not
touch it; run `podman system prune` as the owning user. A scheduled prune for a
rootless user needs a `--user` timer plus `loginctl enable-linger`. 

## Use when

- A container host is filling its disk (`/var/lib/docker`, container storage).
- Removing dangling images, stopped containers, unused volumes/networks, build cache.
- Setting up automatic, scheduled cleanup with a systemd timer.

## Do not use when

- Installing or configuring the engine; use `linux-container-engine`.
- Running or supervising containers; use `linux-container-deployment`.
- General host disk triage outside containers; use `linux-disk-storage`.

## Required inputs

| Artefact | Required? | Source | If absent |
|---|---|---|---|
| Engine, execution user, storage root, and pressure target | yes | Host inventory and filesystem metrics | Measure only; do not prune. |
| Object ownership and retention policy | yes for `-a`/volumes | Workload owners | Limit to dangling objects or stop. |
| Approved destructive scope and rollback/re-pull plan | mutation | Change approval | Produce a candidate list only. |

- The engine in use (Docker daemon vs rootless Podman) and whose storage to clean.
- How aggressive the prune may be (dangling-only vs `-a --volumes`).
- For scheduling: the cadence and whether it is a system or rootless-user timer.

## Decision rules

| Choice | Action | Failure or risk avoided |
|---|---|---|
| Dangling versus all unused | Start with dangling; use `-a` only after reconciling stopped workloads and rollback images. | Deleting needed rollback artefacts. |
| Volumes | Exclude by default; prune only named approved volumes after backup/ownership checks. | Irrecoverable state loss. |
| Rootful versus rootless | Inspect each relevant user's storage separately. | Cleaning the wrong store. |
| Scheduled prune | Schedule only a conservative, logged scope with disk thresholds. | Unattended destructive cleanup. |

## Workflow

1. Measure first with `docker system df` / `podman system df`.
2. Identify what is genuinely unused (dangling images, stopped containers, orphan volumes).
3. Prune from least to most aggressive; confirm before `-a --volumes`.
4. Optionally install a scheduled prune (systemd timer) and verify it ran.

5. Stop before any object whose owner or retention need is unresolved; recover deleted images by re-pulling recorded digests, while volumes require the separately proven backup restore path.

## Outputs

| Artefact | Consumer | Acceptance condition |
|---|---|---|
| Prune plan | Host owner | Lists engine/user, exact candidate classes, exclusions, approvals, and commands. |
| Reclaim report | Capacity owner | Shows before/after engine and filesystem usage plus objects removed. |
| Timer evidence | On-call operator | Conservative scope, schedule, logs, next run, and failure status are verifiable. |

## Anti-patterns

- Pruning volumes by default. Fix: exclude them unless owners separately approve named targets.
- Treating unused as ownerless. Fix: reconcile stopped workloads and rollback images.
- Cleaning the wrong user store. Fix: record engine, rootful/rootless mode, and execution user.
- Reporting estimated savings as reclaimed. Fix: compare pre/post engine and filesystem usage.
- Scheduling aggressive cleanup silently. Fix: use conservative scope with logs, thresholds, and alerts.
- Running `docker system prune -a --volumes` on a host with paused-to-investigate images, or with data-bearing volumes.
- Scheduling an aggressive `-a --volumes` prune unattended on a DB/stateful host.
- Cleaning root Docker storage and assuming rootless Podman storage was also freed.
- Treating "unused" as ownerless. Correction: reconcile stopped stacks, rollback images, and named volumes with owners.
- Reporting estimated savings as reclaimed. Correction: capture before/after filesystem and engine measurements.
- Scheduling cleanup without logs or alerting. Correction: retain unit output and alert on failure or low space.

## Measure before you prune

```bash
docker system df                # TYPE / TOTAL / ACTIVE / RECLAIMABLE
docker system df -v             # per-image, per-volume detail
# Podman:
podman system df
```

`RECLAIMABLE` is the headline number — what a prune would free.

---

## Prune scopes (least to most aggressive)

```bash
# 1. Dangling images only (untagged <none> layers) — always safe
docker image prune

# 2. Stopped containers + dangling images + unused networks + build cache
docker system prune

# 3. All images not used by a running container (not just dangling)
docker image prune -a
docker image prune -a --filter 'until=720h'    # only images older than 30 days

# 4. Everything unused, INCLUDING named volumes — destructive
docker system prune -a --volumes

# Targeted:
docker container prune          # stopped containers
docker volume prune             # unused volumes (data loss risk!)
docker network prune            # unused user-defined networks
docker builder prune            # build cache
```

> **`docker system prune -a` deletes images not used by a *running* container —
> including ones you stopped to investigate. Always run `docker system prune`
> (no `-a`) first, and never auto-prune `--volumes` on a stateful host.**

> **Prune commands prompt for confirmation interactively.** In non-interactive
> contexts (scripts, agents, timers) add `-f` only after the scope above has
> been approved — an unanswered prompt also consumes the rest of a piped
> script's stdin, silently aborting everything after it.

Podman is the same surface:

```bash
podman image prune -a           # all unused images
podman system prune             # stopped containers + dangling + cache
podman system prune -a --volumes
podman volume prune
```

> `[GROUNDING-GAP: image/volume/cache prune semantics and filters (until=, label=, dangling=) — grounded on Podman/Docker upstream docs; deepen with Container Security (Liz Rice)]`

---

## Scheduled prune (systemd timer)

The cleanest way to keep a host tidy is a `*.timer` + `*.service` pair that runs
a safe prune nightly. System scope (Docker / root Podman):

```ini
# /etc/systemd/system/container-prune.service
[Unit]
Description=Scheduled container image/cache prune

[Service]
Type=oneshot
ExecStart=/usr/local/bin/sk-container-prune --yes --schedule-safe
```

```ini
# /etc/systemd/system/container-prune.timer
[Unit]
Description=Run container prune daily

[Timer]
OnCalendar=*-*-* 03:30:00
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now container-prune.timer
systemctl list-timers container-prune.timer
```

The `sk-container-prune` script below installs exactly this timer for you.
For rootless Podman use `systemctl --user` units plus
`loginctl enable-linger <user>`. Full detail (filters, storage layout, cron
alternative) is in
[`references/prune-and-scheduling.md`](references/prune-and-scheduling.md).

> `[GROUNDING-GAP: systemd prune timer scheduling — grounded on Podman/Docker + systemd.timer upstream docs; deepen with Container Security (Liz Rice)]`

---

## References

- [`references/prune-and-scheduling.md`](references/prune-and-scheduling.md) — prune scopes, filters, storage layout, and the systemd prune timer.
- [`references/details.md`](references/details.md)
