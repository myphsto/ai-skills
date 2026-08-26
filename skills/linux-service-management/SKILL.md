---
name: linux-service-management
description: "Use when operating or diagnosing systemd units, timers, targets, journal logs, restart policy, dependencies, or cgroup limits. Use a service-specific skill for application configuration and linux-virtualization for VM or system-container lifecycle."
license: MIT
compatibility: "Linux (Debian/Ubuntu or RHEL family); root for most operations"
metadata:
  author: myphsto
  version: "1.0"
  source: "https://github.com/peterbamuhigire/linux-skills"
---

# Service Management

## Distro support

systemd is **identical** on both supported families — `systemctl`, `journalctl`,
unit files, targets, and timers all work the same. The only differences are a
few **unit names** and the package manager. The commands below use the
Debian/Ubuntu names; the **RHEL family** (Fedora, RHEL, CentOS Stream, Rocky,
Alma, Oracle) equivalents are in the matrix.

| Concept | Debian/Ubuntu | RHEL family |
|---|---|---|
| Web server unit | `apache2` | `httpd` |
| Cron daemon unit | `cron` | `crond` |
| SSH daemon unit | `ssh` | `sshd` |
| Database unit | `mysql` / `mariadb` | `mariadb` |
| Firewall unit | `ufw` | `firewalld` |
| Install a service pkg | `apt install <pkg>` | `dnf install <pkg>` |
| systemctl / journalctl | identical | identical |
| Unit file locations | `/etc/systemd/system`, `/lib/systemd/system` | same |
| Targets (`multi-user`/`graphical`) | identical | identical |
| cgroup v2 resource control (`CPUWeight=`, `CPUQuota=`, `IOWeight=`, `MemoryMax=`) | identical | identical |
| `nice` / `renice` / `ionice` | identical | identical |

In `sk-*` scripts, resolve unit names with the `svc_name` helper from
`common.sh` (e.g. `svc_name apache` → `apache2` or `httpd`) instead of
hardcoding.

## Use when

- Managing `systemd` services on a Linux server.
- Investigating why a service failed, restarted, or will not enable correctly.
- Performing controlled restarts or reloads after config changes.

## Do not use when

- The task is only log analysis; use `linux-log-management`.
- The task is broad symptom-driven triage across multiple subsystems; use `linux-troubleshooting`.

## Required inputs

| Artefact | Source | Required? | If absent |
|---|---|---|---|
| Unit name, host family, symptom, timestamp, and expected service behaviour | Incident/change request | required | Use read-only unit discovery; do not guess an alias. |
| Unit definition/drop-ins, status, journal, dependencies, and recent config/package changes | Host and change history | required for diagnosis | Return collection commands and mark root cause unresolved. |
| Change window, health check, and rollback/recovery authority | Service owner | required for reload/restart/edit | Stop before mutation. |

## Decision rules

| Choice | Action | Failure or risk avoided |
|---|---|---|
| Config supports reload | Validate then reload | Avoidable connection interruption. |
| Binary/environment/dependency changed | Controlled restart after validation | Old process retaining stale state. |
| Rapid restart loop | Stop retries, inspect first failure and limits | Log flooding and dependency damage. |

## Workflow

1. Inspect service status and recent logs before taking action.
2. Apply the smallest restart, reload, or enablement change needed.
3. Follow the crashed-service workflow when a normal restart is insufficient.
4. Confirm the unit is healthy and serving traffic after the change.
5. Stop if the unit identity, config validation, dependency impact, health probe, rollback, or action authority is unresolved.
6. Recover by restoring the prior unit/drop-in/config, running `daemon-reload` when needed, and returning the service to its last verified state.

## Outputs

| Artefact | Consumer | Acceptance condition |
|---|---|---|
| Unit diagnosis or controlled action | System operator | Names unit/load/active/sub state, failure cause, dependencies, and exact action. |
| Unit/drop-in change record | Reviewer | `systemd-analyze verify` or service-native config checks pass and rollback is documented. |
| Runtime verification | Service owner | Unit remains stable and its real endpoint/job/timer behaviour succeeds. |

## Anti-patterns

- Repeatedly restarting without reading status/journal. Fix: capture the first failure and resolve its cause.
- Treating `active (running)` as application health. Fix: probe the service's real socket, protocol, or job outcome.
- Reloading after an invalid config edit. Fix: use the service's native validator before systemd action.
- Editing vendor unit files in `/usr/lib` or `/lib`. Fix: use a reviewed drop-in and `daemon-reload`.
- Using `enable` as proof the service is running. Fix: verify enablement and current runtime state separately.

## Core Commands

```bash
sudo systemctl status <service>           # check status + last log lines
sudo systemctl start|stop|restart <service>
sudo systemctl reload <service>           # graceful (not all services support)
sudo systemctl enable|disable <service>   # boot behaviour
sudo systemctl is-active <service>
sudo systemctl is-enabled <service>
```

## Services Quick Reference

| Service | Safe reload? | Notes |
|---------|-------------|-------|
| `nginx` | Yes | Always run `nginx -t` first |
| `apache2` | Yes | Run `apache2ctl configtest` first |
| `mysql` | No | Brief downtime on restart |
| `postgresql` | Yes | reload re-reads postgresql.conf |
| `php8.3-fpm` | Yes | reload finishes active requests |
| `redis` | No | |
| `fail2ban` | Yes | reload re-reads jail configs |
| `certbot.timer` | — | systemd timer, not a daemon |
| `cron` | No | |
| `msmtp` | — | not a daemon; test with command |

Full per-service operations: `references/service-reference.md`

## Viewing Logs (journalctl)

```bash
sudo journalctl -u <service> -n 50 --no-pager     # last 50 lines
sudo journalctl -u <service> -f                   # follow live
sudo journalctl -u <service> --since "1 hour ago"
sudo journalctl -u <service> -p err --no-pager    # errors only
```

## Diagnosing A Crashed Service

```bash
# Step 1: Read exit code and recent logs
sudo systemctl status <service> --no-pager

# Step 2: Get full error context
sudo journalctl -u <service> --since "5 min ago" --no-pager

# Step 3: Test config (web servers)
sudo nginx -t                    # nginx
sudo apache2ctl configtest       # apache2
sudo php-fpm8.3 -t              # php-fpm

# Step 4: Check for disk full or port conflicts
df -h
sudo ss -tlnp | grep <port>
```

## Check All Services At Once

```bash
sudo systemctl list-units --type=service --state=failed
sudo systemctl list-units --type=service --state=running | \
    grep -E "nginx|apache|mysql|postgresql|php|redis|fail2ban"
```

## Process Priority & cgroup Resource Control

A background service must never starve the host. systemd runs every service
in a **cgroup v2** control group, so you can cap its CPU, I/O, and memory.

```bash
# Ad-hoc, per-process: nice (CPU) + ionice (disk I/O)
nice -n 10 /usr/local/bin/backup.sh          # lower CPU priority (-20 high .. 19 low)
sudo renice -n 10 -p <pid>                    # re-prioritize a running process
ionice -c 3 /usr/local/bin/backup.sh          # idle I/O class — yields the disk
nice -n 19 ionice -c 3 /usr/local/bin/heavy.sh

# Per-service, persistent, kernel-enforced — via the unit [Service] section:
#   Nice=10               CPUWeight=20        CPUQuota=50%
#   IOSchedulingClass=idle  IOWeight=20       MemoryMax=512M  TasksMax=64

# Apply a limit to a running service without editing the unit:
sudo systemctl set-property nginx.service CPUQuota=50% MemoryMax=512M
sudo systemctl set-property --runtime mysql.service IOWeight=50   # until reboot

# Inspect effective limits + live usage:
systemctl show nginx.service -p CPUWeight -p CPUQuotaPerSecUSec -p MemoryMax
systemd-cgtop                                 # top-like per-cgroup usage
```

`CPUWeight=`/`IOWeight=` are relative shares under contention; `CPUQuota=`/
`MemoryMax=` are hard ceilings. See
[`references/resource-control-and-targets.md`](references/resource-control-and-targets.md)
for the full directive table and a worked resource-limited service.

## systemd Targets (boot state & ordering)

Targets are the modern replacement for SysV runlevels — a group of units
that defines the system state.

```bash
systemctl get-default                          # current boot target
sudo systemctl set-default multi-user.target   # boot headless (no GUI) — server default
sudo systemctl set-default graphical.target    # boot into a desktop
sudo systemctl isolate rescue.target           # switch state live (single-user repair)
systemctl list-units --type=target             # active targets
systemctl list-dependencies multi-user.target  # what boots in this target
```

| Target | Runlevel | Meaning |
|---|---|---|
| `multi-user.target` | 3 | Full system, **no GUI** — normal server default |
| `graphical.target`  | 5 | multi-user **plus** a graphical login |
| `rescue.target`     | 1 | Single-user repair mode |

Dependency ordering in a unit: `Wants=` (soft) / `Requires=` (hard) pull a
dependency in; `After=`/`Before=` order startup (ordering is **separate** from
requirement); `[Install] WantedBy=multi-user.target` is what `systemctl
enable` hooks into to start the service at boot. Details in
[`references/resource-control-and-targets.md`](references/resource-control-and-targets.md).

## Node.js Services (Product-Specific)

```bash
# Any Node.js service registered in systemd:
sudo systemctl status <service-name>
sudo journalctl -u <service-name> -n 50 --no-pager
sudo systemctl restart <service-name>    # after code update via update-all-repos
```

For creating a new Node.js systemd unit, see `linux-webstack`.

---

## References

- [`references/service-reference.md`](references/service-reference.md)
- [`references/timers-and-cron.md`](references/timers-and-cron.md)
- [`references/resource-control-and-targets.md`](references/resource-control-and-targets.md)
- [`references/details.md`](references/details.md)
