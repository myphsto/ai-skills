---
name: linux-sysadmin
description: "Use when a Debian/Ubuntu or RHEL-family server request needs routing across provisioning, security, services, networking, recovery, databases, containers, storage, or performance; use linux-troubleshooting when an unexplained symptom spans components."
license: MIT
compatibility: "Linux (Debian/Ubuntu or RHEL family); root for most operations"
metadata:
  author: myphsto
  version: "1.0"
  source: "https://github.com/peterbamuhigire/linux-skills"
---

# Linux Server Admin Hub

Routing hub for the 32 specialist `linux-*` skills. It names the right
specialist, hands off with the context that specialist needs, and keeps the
first pass read-only until mutation is explicitly authorised.

## Use when

- The user has a Linux server task but has not yet chosen the right specialist skill.
- You need routing across provisioning, security, networking, operations, recovery, or performance.
- You need the default operating rules before entering a narrower workflow.

## Do not use when

- The task is already clearly scoped to a specialist skill and you can move there directly.
- The task targets a non-Linux system (Windows, macOS, BSD).

## Required inputs

| Artefact | Source | Required? | If absent |
|---|---|---:|---|
| Server role, intended outcome, or observed symptom | User request | yes | Ask for or gather only the context needed to route safely. |
| Distro family and version | `/etc/os-release` or user | conditional | Route provisionally and require detection before family-specific commands. |
| Authority boundary and operational constraints | User and environment | yes for mutation | Default to read-only diagnosis; do not infer production-change authority. |

## Decision rules

| Choice | Route or action | Failure or risk avoided |
|---|---|---|
| Cause is unknown and symptom spans components | `linux-troubleshooting` first | Premature repair of the wrong subsystem |
| Users, SSH, sudo, PAM, or firewall/TLS changes | `linux-access-control` or `linux-firewall-ssl` | Generic edits to identity or network policy |
| ZFS pool, dataset, snapshot, or replication task | `linux-zfs` | Generic disk/storage tools applied to a ZFS-managed hierarchy |
| Compliance / auditd / AIDE / benchmark request | Outside this skill set | Routing to a skill that no longer exists in this repo |

## Workflow

1. Classify the task using the routing table.
2. Load the matching specialist skill and follow its workflow as the source of truth.
3. Stop before destructive, externally visible, or production-changing work that lacks explicit authority.
4. If the first route fails, return to the observed symptom and select the nearest diagnostic skill rather than guessing a repair.
5. Verify the result with service checks, config validation, or follow-up inspection before closing.

## Outputs

| Artefact | Consumer | Acceptance condition |
|---|---|---|
| Ranked specialist route | Operator or downstream agent | Primary skill is named and the closest rejected neighbour is explained when ambiguous. |
| Authority and context handoff | Selected specialist | Distro, server role, change boundary, and missing evidence are explicit. |
| Verification target | Operator | A concrete service, configuration, log, backup, or system state proves completion. |

## Anti-patterns

- Solving a database backup from the hub. Fix: hand off to `linux-mysql-mariadb` or `linux-postgresql` and follow its workflow.
- Guessing a route from one keyword. Fix: compare the requested outcome with the nearest neighbour descriptions.
- Treating an unknown distro as Ubuntu. Fix: detect the family before selecting packages, paths, services, or firewall tooling.
- Turning a request for analysis into an authorised repair. Fix: keep the first pass read-only unless mutation is explicit.
- Claiming completion after a command exits zero. Fix: inspect the service, configuration, logs, backup, or system state named by the specialist.

## Skill menu

```
Linux Server Management
═══════════════════════════════════════════════════════════

  PROVISIONING & PACKAGES
   linux-server-provisioning   set up a new server (from scratch)
   linux-cloud-init            bootstrap with cloud-init / autoinstall / Kickstart
   linux-package-management    packages: apt, dnf, snap, flatpak, unattended-upgrades
   linux-repo-sync             safely update git repos (never destroy local work)

  WEB
   linux-webstack              Nginx, Apache, PHP-FPM, Node.js platform
   linux-site-deployment       deploy one site to an existing web host

  SECURITY & ACCESS
   linux-access-control        users, groups, SSH keys, sudo, PAM, permissions
   linux-firewall-ssl          ufw / firewalld + Certbot TLS
   linux-intrusion-detection   fail2ban, rkhunter / chkrootkit

  OPERATIONS
   linux-service-management    systemd units, timers, journal, cgroups
   linux-disk-storage          disks, inodes, swap, LVM, NFS / CIFS mounts
   linux-system-monitoring     read-only host health snapshot
   linux-log-management        journalctl, logrotate, correlation
   linux-troubleshooting       diagnose an unknown issue

  NETWORKING
   linux-network-admin         interfaces, netplan / NM, DNS client, NTP
   linux-dns-server            BIND9 / Unbound
   linux-mail-server           Postfix / Dovecot, SPF / DKIM / DMARC

  VIRTUALIZATION & CONTAINERS
   linux-virtualization        KVM / libvirt, LXD
   linux-container-engine      Docker / Podman install & hardening
   linux-container-deployment  run & operate containers / Compose
   linux-image-hygiene         reclaim disk from the container engine

  DATABASES & CACHING
   linux-mysql-mariadb         MySQL / MariaDB (install, tune, backup, PITR)
   linux-postgresql            PostgreSQL (install, tune, backup, PITR)
   linux-inmemory-stores       Redis, Memcached

  STORAGE & BACKUP
   linux-zfs                   ZFS pools, datasets, snapshots, replication, tuning
   linux-filesystem-snapshots  point-in-time snapshots (LVM / Btrfs / ZFS)
   linux-rsync-sync            offsite & incremental sync
   linux-archive-integrity     metadata-preserving tar archives
   linux-disaster-recovery     restore from verified backups

  PERFORMANCE & KERNEL
   linux-perf-profiling        find the bottleneck before tuning
   linux-sysctl-tuning         persistent sysctl tuning from measured evidence
   linux-kernel-modules        load / parameterise / blacklist modules

═══════════════════════════════════════════════════════════
```

## Routing table

| Task | Skill |
|--------|-------|
| New server from scratch | linux-server-provisioning |
| Cloud bootstrap (cloud-init / autoinstall / Kickstart) | linux-cloud-init |
| Package management (apt/dnf/snap/flatpak) | linux-package-management |
| Automated git repo updates | linux-repo-sync |
| Nginx / Apache / PHP / Node platform | linux-webstack |
| Deploy a website | linux-site-deployment |
| Users, sudo, SSH access | linux-access-control |
| Firewall + TLS certificates | linux-firewall-ssl |
| Intrusion detection / fail2ban | linux-intrusion-detection |
| systemd services and timers | linux-service-management |
| Disks, inodes, swap, LVM, mounts | linux-disk-storage |
| System health snapshot | linux-system-monitoring |
| Logs (journalctl, rotation) | linux-log-management |
| Unknown symptom diagnosis | linux-troubleshooting |
| Interfaces, DNS client, NTP | linux-network-admin |
| Run a DNS server | linux-dns-server |
| Run a mail server | linux-mail-server |
| KVM / libvirt / LXD | linux-virtualization |
| Docker / Podman engine | linux-container-engine |
| Run containers / Compose | linux-container-deployment |
| Container disk reclamation | linux-image-hygiene |
| MySQL / MariaDB | linux-mysql-mariadb |
| PostgreSQL | linux-postgresql |
| Redis / Memcached | linux-inmemory-stores |
| ZFS pools / datasets / replication / tuning | linux-zfs |
| Filesystem snapshots | linux-filesystem-snapshots |
| rsync backups | linux-rsync-sync |
| Create/verify archives | linux-archive-integrity |
| Restore from backup | linux-disaster-recovery |
| Performance profiling | linux-perf-profiling |
| Kernel sysctl tuning | linux-sysctl-tuning |
| Kernel modules | linux-kernel-modules |

## Standing rules

- Confirm before every destructive operation (restore, drop, reset, delete) — require explicit confirmation.
- Validate configuration before every reload (`nginx -t`, `postconf -t`, `sshd -t`, …).
- Repo-update scripts MUST preserve local work: `git pull --rebase --autostash` plus a `git status --porcelain` dirty-check; NEVER `git reset --hard` or `git clean -fd` in an automated updater. See `linux-repo-sync`.
- Backup credential files must always be mode 600.
- Prefer idempotent commands and playbooks that are safe to re-run.

## References

- [`references/details.md`](references/details.md)
