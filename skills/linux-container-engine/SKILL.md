---
name: linux-container-engine
description: "Use when installing, configuring, hardening, or diagnosing Docker or Podman engines on Debian/Ubuntu or RHEL-family hosts. Covers daemon/rootless mode, registries, storage, and sockets; use linux-container-deployment to run workloads."
license: MIT
compatibility: "Linux (Debian/Ubuntu or RHEL family); root for most operations"
metadata:
  author: myphsto
  version: "1.0"
  source: "https://github.com/peterbamuhigire/linux-skills"
---

# Container Engine — Docker & Podman

This skill owns the **engine layer**: installing it, configuring the daemon /
Podman config, the storage driver, the default bridge, registries, and engine
hardening. It does **not** own running containers (`linux-container-deployment`),
disk cleanup (`linux-image-hygiene`), or KVM/libvirt VMs (`linux-virtualization`).

## Distro support

Two-family skill. The two engines are **Docker** (a root daemon, `dockerd`,
managed by `docker.service`) and **Podman** (daemonless, rootless by default,
shipped and preferred by the RHEL family). Both speak the OCI image format and
share most CLI verbs, but they configure differently: Docker reads
`/etc/docker/daemon.json`; Podman reads `/etc/containers/*.conf`
(`registries.conf`, `storage.conf`, `containers.conf`). The body below uses
Docker on Debian/Ubuntu; substitute per this matrix.

| Concept | Debian/Ubuntu | RHEL family |
|---|---|---|
| Default / preferred engine | Docker CE (daemon) | **Podman** (daemonless, rootless) |
| Docker install | Docker CE apt repo (`docker-ce`) | Docker CE dnf repo (`docker-ce`) |
| Podman install | `apt install podman` | `dnf install podman` (in base/AppStream) |
| Daemon config | `/etc/docker/daemon.json` | `/etc/docker/daemon.json` (Docker); Podman has no daemon |
| Registries config | `/etc/docker/daemon.json` mirrors + Podman `/etc/containers/registries.conf` | `/etc/containers/registries.conf` (Podman default) |
| Storage driver | `overlay2` (Docker) | `overlay` via `fuse-overlayfs` (rootless Podman) / `overlay2` (Docker) |
| Default bridge | `docker0` (Docker) / `cni-podman0` or netavark | `cni-podman0` / **netavark** (RHEL 9+) |
| Rootless support | Podman rootless; Docker rootless is opt-in | Podman rootless is the default model |
| Volume SELinux labels | n/a | **SELinux**: bind-mount with `:z`/`:Z` or the container is denied |
| Socket | `/var/run/docker.sock` (root-equivalent) | none for rootless Podman; user socket via `podman.socket` |

**RHEL-family notes:** prefer **Podman** — rootless, no root daemon, and a
Docker-compatible CLI (`alias docker=podman` covers most flows). Registries
live in `/etc/containers/registries.conf` (system) and
`~/.config/containers/registries.conf` (per-user, overrides system). SELinux
relabels bind-mounted volumes: append `:z` (shared) or `:Z` (private) to
`-v host:container` or the container gets permission denied. See
[`../linux-virtualization/references/selinux-reference.md`](../linux-virtualization/references/selinux-reference.md)

## Use when

- Installing Docker or Podman on a fresh host (either family).
- Choosing between the Docker daemon and rootless Podman for a workload.
- Writing or auditing `/etc/docker/daemon.json` or `/etc/containers/registries.conf`.
- Hardening the engine: userns-remap, `no-new-privileges`, socket permissions.

## Do not use when

- Running, stopping, or scheduling individual containers / compose stacks; use `linux-container-deployment`.
- Reclaiming disk from images, volumes, and networks; use `linux-image-hygiene`.
- Managing KVM/libvirt virtual machines; use `linux-virtualization`.
- Host firewall rules for published ports; use `linux-firewall-ssl`.

## Required inputs

| Artefact | Required? | Source | If absent |
|---|---|---|---|
| Distro, engine/version, tenancy model, and workload needs | yes | Host inventory and service owner | Stop before installation or replacement. |
| Registry, proxy, storage, network, and logging requirements | config work | Platform design | Keep vendor defaults and report the decision gap. |
| Change window and rollback | mutation | Approved change record | Inspect only; do not restart or replace the engine. |

- Which engine the host should run (Docker daemon, rootless Podman, or both).
- The family (Debian/Ubuntu vs RHEL) so install and config paths are correct.
- Whether containers must run rootless and any registry / mirror requirements.

## Decision rules

| Choice | Action | Failure or risk avoided |
|---|---|---|
| Docker or Podman | Prefer rootless Podman for daemonless/multi-tenant needs; choose Docker when its daemon/API ecosystem is required. | Unjustified privileged daemon. |
| Rootless or rootful | Use rootless unless privileged ports, devices, or host integration are proven requirements. | Host-wide compromise. |
| Registry trust | Allow only intended registries/mirrors and keep signature/TLS controls. | Untrusted image supply. |
| Storage driver | Verify backing filesystem compatibility before selecting overlay storage. | Corruption or engine startup failure. |

## Workflow

1. Detect the family and any already-installed engine before installing.
2. Install the chosen engine from the upstream repo; enable it.
3. Write `daemon.json` / `registries.conf` for storage, logging, registries, hardening.
4. Verify the engine reports the expected storage driver, registries, and security flags.

5. Stop if the socket, storage driver, registry trust, or rootless checks fail; recover with the saved engine config/package state and verify a test container before handoff.

## Outputs

| Artefact | Consumer | Acceptance condition |
|---|---|---|
| Engine configuration record | Platform operator | Names engine/version, mode, registries, storage, logging, security settings, and rollback. |
| Readiness evidence | Deployment owner | Version/info checks, expected socket ownership, storage driver, network, and rootless/daemon health pass. |
| Residual-risk record | Security owner | Records every privileged boundary or unavailable check. |

## Anti-patterns

- Granting Docker group membership casually. Fix: restrict it and record root-equivalent risk.
- Disabling registry TLS verification. Fix: install the correct CA and scope trust.
- Changing storage driver in place. Fix: plan export/re-pull, downtime, and rollback.
- Running rootful by habit. Fix: prove privileged requirements or use rootless mode.
- Calling engine startup readiness. Fix: verify socket, storage, network, namespace, and test container.
- Installing `docker.io` from the distro archive on production (lags upstream).
- Bind-mounting `/var/run/docker.sock` into a container without a hard reason.
- Running every container as root because `:Z` SELinux labelling "was easier" to skip.
- Disabling TLS verification for a registry. Correction: install the correct CA and scope registry trust explicitly.
- Changing storage drivers in place. Correction: plan image export/re-pull and rollback before migration.
- Adding broad Docker group membership. Correction: grant narrowly and record its root-equivalent risk.

## Install the engine

### Docker CE (both families, upstream repo)

```bash
# Debian/Ubuntu
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
    | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update && sudo apt install -y docker-ce docker-ce-cli containerd.io \
    docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker

# RHEL family
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl enable --now docker

docker version
```

`docker` group membership is **root-equivalent** on the host — only add trusted
admins.

### Distro-packaged Docker (Debian/Ubuntu: `docker.io` + `docker-compose-v2`)

The distro archive ships `docker.io` (no compose plugin). Fine for
non-production use (the upstream-repo path above is for production):

```bash
sudo apt install -y docker.io docker-compose-v2
sudo systemctl enable --now docker
docker compose version     # provided by docker-compose-v2
```

Without `docker-compose-v2`, `docker compose` is an unknown command and every
compose workflow breaks — install it whenever you use `docker.io`.

### Podman (preferred on RHEL; available on Debian/Ubuntu)

```bash
# Debian/Ubuntu
sudo apt install -y podman
# RHEL family (base / AppStream — no extra repo)
sudo dnf install -y podman

podman info
podman run --rm hello-world          # rootless, no daemon
```

Rootless Podman runs each container in **your** user namespace; a breakout
cannot reach host root. Rootless containers cannot bind privileged ports (<1024)
or get a routable IP without extra setup — those need root or `slirp4netns`/`pasta`.

---

## Daemon configuration (`/etc/docker/daemon.json`)

A production baseline pins storage, caps logs, and turns on hardening:

```json
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "5" },
  "storage-driver": "overlay2",
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": true,
  "userns-remap": "default",
  "default-address-pools": [ { "base": "172.30.0.0/16", "size": 24 } ],
  "registry-mirrors": ["https://mirror.gcr.io"]
}
```

Apply and verify:

```bash
sudo systemctl restart docker
docker info | grep -E 'Storage Driver|Logging Driver|Live Restore|userns'
```

Full rationale for each key — and the Podman equivalents — is in
[`references/container-engine-reference.md`](references/container-engine-reference.md).

---

## Registries (`/etc/containers/registries.conf`)

Podman (and Buildah/skopeo) read registries from
`/etc/containers/registries.conf` system-wide, overridable per-user at
`~/.config/containers/registries.conf`. Always set `unqualified-search-registries`
so a bare `podman pull nginx` is unambiguous:

```toml
unqualified-search-registries = ["registry.access.redhat.com", "docker.io"]

[[registry]]
location = "docker.io"

[[registry]]
location = "registry.example.com"
insecure = false
# blocked = true            # disable a registry entirely
```

Docker's registry mirrors live in `daemon.json` (`registry-mirrors`) instead.

---

## Storage driver & network bridge

```bash
docker info --format '{{.Driver}}'        # expect: overlay2
podman info --format '{{.Store.GraphDriverName}}'

docker network ls                          # default: bridge (docker0)
docker network inspect bridge | grep Subnet
podman network ls                          # default: podman (netavark on RHEL 9+)
```

`overlay2` is the correct default on modern kernels; rootless Podman uses
`overlay` via `fuse-overlayfs`. Avoid `devicemapper` (deprecated) and `vfs`
(no copy-on-write, huge disk use).

---

## Daemon hardening

- **`userns-remap`** maps container UID 0 to an unprivileged host UID, so a
  container root is not host root.
- **`no-new-privileges`** blocks `setuid` escalation inside containers.
- **`docker.sock` is root-equivalent.** It is owned `root:docker`, mode `0660`;
  do not loosen it and do not bind-mount it into containers.
- **Rootless Podman** sidesteps most of this — no root daemon, no root socket.

```bash
ls -l /var/run/docker.sock                 # expect srw-rw---- root docker
getent group docker                        # audit who has daemon access
docker info --format '{{.SecurityOptions}}'
```

> `[GROUNDING-GAP: daemon hardening (userns-remap, no-new-privileges, seccomp/AppArmor profiles, rootless socket perms) — grounded on Podman/Docker upstream docs; deepen with Container Security (Liz Rice)]`

Full detail (Dockerfile hardening, seccomp, capabilities, image scanning) is in
[`references/container-engine-reference.md`](references/container-engine-reference.md).

---

## References

- [`references/container-engine-reference.md`](references/container-engine-reference.md) — full Docker + Podman install, daemon config, networks, volumes, security, rootless.
- [`references/details.md`](references/details.md)
