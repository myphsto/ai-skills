---
name: linux-container-deployment
description: "Use when running, updating, debugging, or supervising containers and Compose/Quadlet stacks on Debian/Ubuntu or RHEL-family hosts. Covers lifecycle, health, volumes, and systemd; use linux-container-engine for setup and linux-image-hygiene for pruning."
license: MIT
compatibility: "Linux (Debian/Ubuntu or RHEL family); root for most operations"
metadata:
  author: myphsto
  version: "1.0"
  source: "https://github.com/peterbamuhigire/linux-skills"
---

# Container Deployment & Lifecycle

This skill owns **running** containers. It does **not** own installing the
engine (`linux-container-engine`) or disk cleanup (`linux-image-hygiene`).

## Distro support

Two-family skill. The container CLI is the same idea on both — `docker` on a
Docker host, `podman` on the RHEL family — and most verbs are identical. The
difference is **how you run containers as managed services**: Docker uses a
hand-written systemd unit that calls `docker compose`; Podman uses
`podman generate systemd` (legacy) or **Quadlet** `.container` units (RHEL 9+,
the modern path). The body below uses Docker on Debian/Ubuntu; substitute per
this matrix.

| Concept | Debian/Ubuntu | RHEL family |
|---|---|---|
| Run a container | `docker run` | `podman run` (rootless by default) |
| Multi-container stack | `docker compose` (v2 plugin) | `podman compose` / `docker-compose` shim |
| As a systemd service | hand-written unit → `docker compose up -d` | `podman generate systemd` **or Quadlet `.container`** |
| Quadlet unit location (system) | n/a | `/etc/containers/systemd/*.container` |
| Quadlet unit location (rootless) | n/a | `~/.config/containers/systemd/*.container` |
| Start user services at boot | systemd system units | `loginctl enable-linger <user>` for rootless |
| Restart policy | `--restart unless-stopped` | `--restart unless-stopped` / unit `Restart=` |
| Volume SELinux labels | n/a | bind-mount with `:z`/`:Z` |

**RHEL-family notes:** prefer **Quadlet** over `podman generate systemd` on
RHEL 9+ — you write a declarative `.container` file and systemd generates the
unit at boot, so there is no stale generated unit to maintain. For rootless
services to start at boot you must `loginctl enable-linger <user>`. SELinux
relabels bind mounts: append `:z`/`:Z` to `-v host:container`. See
[`../linux-virtualization/references/selinux-reference.md`](../linux-virtualization/references/selinux-reference.md)

## Use when

- Running, stopping, inspecting, or debugging a container's lifecycle.
- Bringing up a multi-container stack with compose (Docker or Podman).
- Making containers start on boot and restart on failure as systemd services.
- Choosing restart policies for background services vs batch jobs.

## Do not use when

- Installing or configuring the engine / daemon; use `linux-container-engine`.
- Reclaiming disk from images/volumes/networks; use `linux-image-hygiene`.
- Managing KVM/libvirt VMs; use `linux-virtualization`.
- Deploying the application code itself inside the container; use `linux-site-deployment`.

## Required inputs

| Artefact | Required? | Source | If absent |
|---|---|---|---|
| Image digest, command/Compose/Quadlet definition, ports, volumes, and secrets | yes | Release artefact and service owner | Stop; do not infer a runnable deployment. |
| Engine/mode, distro, SELinux state, and service identity | yes | Host inventory | Inspect only until confirmed. |
| Health check, rollback image, and maintenance window | production update | Release plan | Do not replace the running workload. |

- The container or compose project and its image (pinned by digest in production).
- Whether it must survive reboot (systemd service / Quadlet) or is a one-off.
- The engine in use (Docker daemon vs rootless Podman) and any SELinux volume needs.

## Decision rules

| Choice | Action | Failure or risk avoided |
|---|---|---|
| One-off or service | Use an ephemeral run for bounded jobs; use Compose/systemd/Quadlet for persistent services. | Workload disappearing after logout/reboot. |
| Image reference | Pin production images by digest and record provenance. | Mutable-tag surprise. |
| Podman supervision | Prefer Quadlet on supported RHEL systems; use generated units only for legacy constraints. | Stale generated units. |
| Volume label | Use `:Z` for exclusive or `:z` for shared SELinux bind mounts after verifying ownership. | Denied access or unsafe relabel. |

## Workflow

1. Validate the compose file or run command before applying (`docker compose config`).
2. Bring the container/stack up; choose an explicit restart policy.
3. For persistence, wire it to systemd (compose unit, `generate systemd`, or Quadlet).
4. Verify the container is running, healthy, and restarts on failure / reboot.

5. Stop when definition validation or the health gate fails; recover by restoring the prior digest/definition and prove health plus restart behaviour again.

## Outputs

| Artefact | Consumer | Acceptance condition |
|---|---|---|
| Deployment definition | Release operator | Validates, pins the image, declares health/restart, volumes, ports, identity, and secret references. |
| Runtime verification | Service owner | Container/stack is healthy, expected ports and mounts work, logs are clean, and restart/reboot behaviour passes. |
| Rollback record | On-call operator | Names prior digest/definition and tested rollback command. |

## Anti-patterns

- Using mutable production tags. Fix: pin and record an image digest.
- Embedding secrets in definitions. Fix: reference the approved secret/file mechanism.
- Updating without a health gate. Fix: define readiness and rollback before replacement.
- Ignoring bind-mount labels or ownership. Fix: verify host permissions and apply the narrow SELinux label.
- Starting a service from a login shell. Fix: supervise it with Compose/systemd/Quadlet and test reboot.
- Starting a long-running container with a bare `docker run` from a login shell (dies on reboot).
- Leaving `restart: no` on a background service so a crash means silent downtime.
- Using `nginx:latest` in a compose file instead of a pinned digest.
- Injecting secrets as literal environment values. Correction: use the approved secret/file mechanism and redact inspection output.
- Updating without a health gate. Correction: define readiness and rollback before replacement.
- Using bind mounts without checking ownership/SELinux labels. Correction: validate host path permissions and apply the narrow label.

## Lifecycle — single container

```bash
docker run -d --name web --restart unless-stopped -p 8080:80 nginx:1.27-alpine
docker ps                                  # running
docker ps -a                               # include stopped
docker logs -f --tail 100 web
docker exec -it web sh
docker stop web && docker start web
docker restart web
docker rm -f web
```

On Podman every verb above works with `podman` substituted; containers run
rootless in your user namespace unless started as root.

### Restart policies

Pick a policy explicitly — the default `no` leaves a crashed container dead.

| Policy | When to use |
|---|---|
| `no` | one-off jobs (fine for `docker run --rm`) |
| `on-failure[:max]` | batch jobs that should retry a bounded number of times |
| `always` | background services that must always run |
| `unless-stopped` | services, but respect an operator `stop` across reboots — **usually right** |

```bash
docker run -d --name app --restart unless-stopped \
    --memory 1g --cpus 2 --pids-limit 200 myapp:2026.04.10
```

---

## Multi-container stacks — compose

Compose v2 ships as the `docker compose` subcommand (two words, no separate
binary). On Podman use `podman compose` (a thin wrapper, or the `podman-compose`
package). Both read `compose.yaml` (or legacy `docker-compose.yml`):

```yaml
# compose.yaml
name: webstack
services:
  web:
    image: nginx:1.27-alpine@sha256:aaaa...    # pinned by digest
    restart: unless-stopped
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro,Z   # :Z for SELinux on RHEL
    depends_on:
      app: { condition: service_healthy }
    deploy:
      resources:
        limits: { cpus: "1.0", memory: 256M }
    security_opt: ["no-new-privileges:true"]
  app:
    image: registry.example.com/myapp:2026.04.10@sha256:bbbb...
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://127.0.0.1:3000/healthz"]
      interval: 30s
      timeout: 5s
      retries: 3
```

```bash
docker compose config                          # validate before applying
docker compose up -d
docker compose ps
docker compose logs -f --tail 100 app
docker compose pull && docker compose up -d     # rolling update
docker compose down                             # stop and remove (add -v for volumes)

# Podman equivalents:
podman compose up -d
podman compose ps
```

Full compose detail is in
[`references/compose-and-systemd-reference.md`](references/compose-and-systemd-reference.md).

---

## Containers as systemd services

### Docker — a compose unit

`/etc/systemd/system/webstack.service`:

```ini
[Unit]
Description=Webstack Compose project
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/webstack
ExecStart=/usr/bin/docker compose up -d --remove-orphans
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload && sudo systemctl enable --now webstack
```

### Podman — `podman generate systemd` (legacy)

Create the container first, then generate a unit from it. The unit must land in
`~/.config/containers/systemd/` for rootless or `/etc/systemd/system/` for root,
and rootless needs linger enabled:

```bash
mkdir -p ~/.config/systemd/user && cd ~/.config/systemd/user
podman generate systemd --new --name --files web
systemctl --user daemon-reload
loginctl enable-linger "$USER"                 # start at boot, not just at login
systemctl --user enable --now container-web.service
```

> `[GROUNDING-GAP: Quadlet (.container/.pod/.network units) is newer than the RHCSA 8 corpus — grounded on Podman/Docker upstream docs; deepen with Container Security (Liz Rice)]`

### Podman — Quadlet `.container` units (RHEL 9+, preferred)

Quadlet replaces `generate systemd`: you write a declarative unit and systemd
generates the service at boot. Drop `web.container` into
`/etc/containers/systemd/` (system) or `~/.config/containers/systemd/` (rootless):

```ini
# /etc/containers/systemd/web.container
[Unit]
Description=nginx web container
After=network-online.target

[Container]
Image=docker.io/library/nginx:1.27-alpine
PublishPort=8080:80
Volume=/srv/www:/usr/share/nginx/html:ro,Z
NoNewPrivileges=true

[Service]
Restart=always

[Install]
WantedBy=multi-user.target default.target
```

```bash
sudo systemctl daemon-reload          # Quadlet generates web.service
sudo systemctl start web.service
systemctl status web.service
```

There is no generated file to maintain — edit the `.container` and reload.

---

## References

- [`references/compose-and-systemd-reference.md`](references/compose-and-systemd-reference.md) — compose v2, podman compose, podman generate systemd, Quadlet `.container` units, restart policies, resource limits.
- [`references/details.md`](references/details.md)
