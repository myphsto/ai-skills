---
name: linux-virtualization
description: "Use when operating KVM/libvirt virtual machines or LXD system containers, including lifecycle, snapshots, backups, storage, networking, and host inspection. Use linux-container-engine and linux-container-deployment for Docker or Podman application containers."
license: MIT
compatibility: "Linux (Debian/Ubuntu or RHEL family); root for most operations"
metadata:
  author: myphsto
  version: "1.0"
  source: "https://github.com/peterbamuhigire/linux-skills"
---

# Linux Virtualization

This skill owns the **VM and system-container layer** on a host: **LXD** system
containers (Canonical's native, Ubuntu-centric) and **KVM/libvirt** for full
virtual machines.

It does **not** own:

- **Application containers (Docker/Podman), compose, and image cleanup** — use
  `linux-container-engine`, `linux-container-deployment`, `linux-image-hygiene`.
- **Kubernetes** — out of scope for v1.
- **Cloud provider VMs** (EC2, DigitalOcean droplets) — managed at the
  provider side.
- **Applications inside containers** — managed by application-specific
  skills.

Informed by the Canonical *Ubuntu Server Guide* (LXD, KVM chapters).

## Distro support

Two-family skill. KVM/libvirt (`virsh`, `virt-install`) is portable across both
families; **LXD** system containers are Ubuntu-centric (Canonical/snap) with no
native LXD on RHEL. Body uses Debian/Ubuntu; substitute per this matrix.

> **Application containers (Docker/Podman) are not covered here.** For the
> container engine, running containers, and image cleanup, use
> **`linux-container-engine`** (install/configure Docker & Podman),
> **`linux-container-deployment`** (run containers, compose, systemd/Quadlet),
> and **`linux-image-hygiene`** (prune images/volumes). This skill keeps **KVM/libvirt VMs and LXD system
> containers** only.

| Concept | Debian/Ubuntu | RHEL family |
|---|---|---|
| System containers | LXD (snap) | `systemd-nspawn` (no native LXD); Podman for app containers |
| VMs (KVM) | `qemu-kvm`, `libvirt-daemon-system` | `qemu-kvm`, `libvirt` |
| Manage VMs | `virsh`, `virt-install` | identical |
| VM/container firewall | `ufw` (known quirks) | `firewalld` + nftables |
| LXD volume labeling | n/a | **SELinux**: mount with `:z`/`:Z` for host-shared storage |

**RHEL-family notes:** LXD is Ubuntu-centric and not native on RHEL — on the
RHEL family use `systemd-nspawn` for system containers and Podman for
application containers (see `linux-container-engine`). KVM/libvirt is identical
across families. SELinux relabels bind-mounted host storage — append `:z`
(shared) or `:Z` (private). See
[`references/selinux-reference.md`](references/selinux-reference.md).

## Use when

- Managing LXD system containers or KVM/libvirt VMs on a host.
- Investigating VM or LXD-container lifecycle failures.
- Taking snapshots or backups before risky changes.
- Listing LXD containers and VMs on a host.
- Creating or restoring LXD container snapshots.
- Exporting/backing up an LXD container or VM to a tar file.
- Debugging why an LXD container or VM won't start.

## Do not use when

- The task is **application containers** (Docker/Podman, compose, image cleanup); use `linux-container-engine`, `linux-container-deployment`, `linux-image-hygiene`.
- The task is configuration management for the host itself — outside this skill set.
- The task is ordinary application service management outside the VM/LXD layer.
- Running or deploying Docker/Podman application containers — use
  `linux-container-deployment` (engine setup: `linux-container-engine`).

- Deploying a web application *inside* a container — use
  `linux-site-deployment`.

- Host firewall rules — use `linux-firewall-ssl`.
- Kubernetes/Nomad orchestration — out of scope.

## Required inputs

| Artefact | Source | Required? | If absent |
|---|---|---|---|
| Host family, hypervisor/container layer, target identity, and desired lifecycle outcome | Operator and host inventory | required | Discover read-only; do not act on an ambiguous name. |
| Current guest definition, storage/network attachments, state, and host capacity | libvirt/LXD host | required for mutation | Return a preflight report only. |
| Backup/snapshot policy, downtime window, recovery target, and change authority | Workload owner | required for destructive or disruptive action | Stop before mutation. |

## Decision rules

| Choice | Action | Failure or risk avoided |
|---|---|---|
| Full OS isolation/legacy kernel workload | Use KVM/libvirt | Container-host coupling. |
| Lightweight system container on supported Ubuntu host | Use LXD | Unneeded VM overhead. |
| Packaged application container | Route to category 12 | Competing lifecycle tools. |

## Workflow

1. Identify the owning virtualization layer and target workload.
2. Inspect current state before changing it.
3. Apply the matching workflow below for lifecycle, snapshot, backup, or startup diagnosis.
4. Verify the guest or container state and host-level impact after the action.
5. Stop if the target, storage/network ownership, capacity, backup consistency, rollback, downtime, or action authority is unresolved.
6. Recover by reverting the recorded definition/snapshot or restoring the independent backup, then verify both guest state and workload health.

## Outputs

| Artefact | Consumer | Acceptance condition |
|---|---|---|
| Guest diagnosis or lifecycle action | Virtualisation operator | Correct target/layer is identified and host plus guest state match the requested outcome. |
| Snapshot/backup/recovery record | Workload owner | Artifact location, consistency method, retention, restore command, and verification are recorded. |
| Capacity and impact evidence | Infrastructure owner | CPU, memory, storage, network attachments, downtime, and rollback are checked before change. |

## Anti-patterns

- Treating LXD system containers and Docker/Podman application containers as interchangeable. Fix: route application containers to category 12.
- Deleting a guest, disk, snapshot, or image before proving ownership. Fix: inventory attachments, dependants, backup, and retention first.
- Debugging only inside the guest. Fix: inspect host capacity, libvirt/LXD state, storage, networking, and logs.
- Calling a snapshot a backup. Fix: export or copy recovery data to an independent failure domain and test restore metadata.
- Starting a migration or resize without capacity/downtime checks. Fix: preflight destination compatibility and define rollback.

## Standing rules

1. **LXD over legacy LXC.** `lxc` (the LXD CLI) is the modern, declarative
   wrapper. Direct `lxc-*` (legacy) commands are discouraged.
2. **Always snapshot before mutating.** Snapshot → mutate → verify. Roll
   back on failure.
3. **Snapshots are not backups.** They live on the same pool. Export
   containers/VMs to tar on separate storage for real backup.
4. **Resource limits are mandatory in production.** Unbounded containers
   eat the host. Set `limits.memory`, `limits.cpu`, and `limits.disk` in
   every profile.
5. **Privileged containers are banned unless justified in writing.**
   Unprivileged is the default.

---

## Quick reference — manual commands

### LXD

```bash
# List all containers
lxc list
lxc list -f compact                            # compact format
lxc info <name>                                # detailed state, IP, resource use

# Launch and basic lifecycle
lxc launch ubuntu:24.04 web01
lxc exec web01 -- bash
lxc stop web01
lxc start web01
lxc delete web01 --force

# Snapshots
lxc snapshot web01 before-upgrade-2026-04-10
lxc info web01 | grep -A10 Snapshots
lxc restore web01 before-upgrade-2026-04-10
lxc delete web01/before-upgrade-2026-04-10    # delete a snapshot

# Full export / backup
lxc export web01 /backups/lxd/web01-$(date +%Y%m%d).tar.gz
lxc import /backups/lxd/web01-20260410.tar.gz

# Resource limits (applied to running container)
lxc config set web01 limits.memory 1GB
lxc config set web01 limits.cpu 2
lxc config device override web01 root size=10GB

# Copy between hosts
lxc remote add remotehost <ip>
lxc copy web01 remotehost:web01-copy
```

Full LXD reference (`lxd init`, profiles, storage backends, networks,
cloud-init integration, 6 worked examples) — see
[`references/lxd-reference.md`](references/lxd-reference.md).

> **Docker / Podman application containers are not covered here.** Use
> `linux-container-engine`, `linux-container-deployment`, and
> `linux-image-hygiene`.

### KVM / libvirt

```bash
sudo virsh list --all                          # all VMs
sudo virsh dominfo <vm>
sudo virsh start <vm>
sudo virsh shutdown <vm>                       # graceful (via ACPI)
sudo virsh destroy <vm>                        # hard power-off
sudo virsh snapshot-create-as <vm> snap-before-upgrade
sudo virsh snapshot-list <vm>
sudo virsh snapshot-revert <vm> snap-before-upgrade
```

---

## Detailed workflows

### Workflow: "What's running on this host?"

```bash
echo "=== LXD ==="
lxc list 2>/dev/null || echo "(lxd not installed)"
echo
echo "=== KVM ==="
sudo virsh list --all 2>/dev/null || echo "(libvirt not installed)"
```

(For Docker/Podman containers on the host, use `sk-container-ps` from
`linux-container-deployment`.)

### Workflow: "Snapshot before I mess with it"

```bash
lxc snapshot web-prod before-upgrade-$(date +%Y%m%d-%H%M)
# ... do the risky thing ...
# If it breaks:
lxc restore web-prod before-upgrade-20260410-1530
# When confirmed stable, delete the snapshot:
lxc delete web-prod/before-upgrade-20260410-1530
```

### Workflow: "Back up a container to cold storage"

```bash
DEST=/backups/lxd
mkdir -p "$DEST"
lxc export web-prod "$DEST/web-prod-$(date +%Y%m%d).tar.gz"
# Then ship off-host:
rclone copy "$DEST/web-prod-$(date +%Y%m%d).tar.gz" gdrive:lxd-backups/
```

### Workflow: "Why won't this LXD container start?"

```bash
lxc info web01 | grep -A10 -E 'Status|Log'
lxc info --show-log web01
# Resource limits too tight?
lxc config show web01 | grep -E 'limits\.'
```

(For "why won't this Docker/Podman container start?" use
`linux-container-deployment`.)

---

## Troubleshooting / gotchas

- **LXD containers "lose" their IP on boot.** They use DHCP from `lxdbr0`
  by default; if the bridge has no DHCP server, set a static IP in the
  profile or container config.
- **KVM VMs with bridged networking don't get IPs.** Check that the host
  bridge has a DHCP server on the VLAN, or configure the VM with cloud-init
  static networking.
- **LXD container file ownership looks weird from the host.** Unprivileged
  containers remap UIDs (`uid 1000` inside = `uid 1001000` outside). Use
  `lxc file push/pull` to move files without fighting ownership.

---

## References

- [`references/lxd-reference.md`](references/lxd-reference.md) — full LXD
  reference: init, profiles, storage, networks, 6 worked examples.
- [`references/selinux-reference.md`](references/selinux-reference.md) — SELinux volume labeling (RHEL family)
- For Docker/Podman application containers: `linux-container-engine`,
  `linux-container-deployment`, `linux-image-hygiene`.
- Book: *Ubuntu Server Guide* (Canonical, Focal) — LXD and KVM chapters.
- Man pages: `lxc(1)`, `virsh(1)`.
- [`references/details.md`](references/details.md)
