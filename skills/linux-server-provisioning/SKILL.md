---
name: linux-server-provisioning
description: "Use when interactively provisioning a fresh Debian/Ubuntu or RHEL-family server after first boot, including identity, admin access, updates, firewall, services, and verification. Use linux-cloud-init for unattended first boot."
license: MIT
compatibility: "Linux (Debian/Ubuntu or RHEL family); root for most operations"
metadata:
  author: myphsto
  version: "1.0"
  source: "https://github.com/peterbamuhigire/linux-skills"
---

# Server Provisioning

## Distro support

Two-family skill. The provisioning *sequence* is the same; the tools at each
step differ. Body uses Debian/Ubuntu; substitute per this matrix.

| Provisioning step | Debian/Ubuntu | RHEL family |
|---|---|---|
| Package manager | `apt` | `dnf` |
| Update + base packages | `apt update && apt install …` | `dnf install …` (`ensure_epel` for extras on RHEL/Rocky/Alma) |
| Admin user group | `usermod -aG sudo <u>` | `usermod -aG wheel <u>` |
| Firewall | `ufw` | `firewalld` |
| Auto security updates | `unattended-upgrades` | `dnf-automatic` |
| Workstation AppImage support | `fuse3 desktop-file-utils`; add `libfuse2`/`libfuse2t64` for legacy AppImages | `fuse3 desktop-file-utils`; add app-specific libs such as `mpv-libs` when needed |
| Mandatory access control | AppArmor (already on) | **SELinux enforcing** (already on) |
| Time sync | `systemd-timesyncd` | `chronyd` |
| Install automation | autoinstall (subiquity) | **Kickstart** (Anaconda) |
| Regenerate GRUB2 | `update-grub` → `/boot/grub/grub.cfg` | `grub2-mkconfig -o /boot/grub2/grub.cfg` (UEFI: `/boot/efi/EFI/<distro>/`) |
| Set/list default kernel | `grub-set-default` + `update-grub` | `grubby --set-default` / `grub2-set-default`; `grubby --default-kernel` |
| Edit kernel boot args | edit `GRUB_CMDLINE_LINUX` + regenerate | `grubby --update-kernel ALL --args/--remove-args` |

See [`../linux-cloud-init/references/kickstart-reference.md`](../linux-cloud-init/references/kickstart-reference.md)
for automated installs and
[`../linux-virtualization/references/selinux-reference.md`](../linux-virtualization/references/selinux-reference.md)
for SELinux. Workstation-only AppImage package baselines are owned by
[`linux-package-management`](../linux-package-management/SKILL.md); add them
only when the target host is a desktop/workstation, not a headless production
server. In `sk-*` scripts use the `common.sh` primitives (`pkg_install`,
`ensure_epel`, `firewall_allow`, `svc_name`) instead of hardcoding. Plan:
`docs/multi-distro/plan.md`.

## Use when

- Building a fresh Ubuntu/Debian server for production use.
- Standardizing a new host before application deployment.
- Performing the baseline setup that later specialist skills depend on.

## Do not use when

- The host is already provisioned and you only need a narrower change.
- The setup should be fully declarative from image boot; use `linux-cloud-init`.

## Required inputs

| Artefact | Source | Required? | If absent |
|---|---|---|---|
| Host role, distribution/release, hostname, timezone, and network identity | Build request and host facts | required | Stop the build and return the missing decisions. |
| Admin access model and break-glass path | System owner | required | Do not alter SSH or disable root/password access. |
| Required services, exposure, update, backup, and monitoring policy | Service owner | required | Produce only a minimal OS baseline and flag unowned controls. |

## Decision rules

| Choice | Action | Failure or risk avoided |
|---|---|---|
| Repeatable image first boot | Route to `linux-cloud-init` | Manual, non-repeatable image setup. |
| Interactive host baseline | Follow this ordered build | Skipped prerequisites and lockout. |
| Fleet-wide ongoing state | Out of scope for this skill set | Configuration drift after provisioning. |

## Workflow

1. Collect the required server identity and stack decisions up front.
2. Work through the numbered provisioning sections in order.
3. Validate access, package installs, services, and baseline security after each major stage.
4. Finish with post-install verification before handing the host to deployment or operations work.
5. Stop if recovery access, role ownership, destructive-storage scope, or an exposure decision is unresolved.
6. Recover a failed stage from the recorded config/package backup or console path, revalidate access, and repeat verification before continuing.

## Outputs

| Artefact | Consumer | Acceptance condition |
|---|---|---|
| Provisioned host baseline | Deployment/operations team | Identity, admin access, updates, firewall, required services, time, and mandatory access control match the approved build. |
| Build decision record | System owner | Records distro-specific choices, exposed ports, installed roles, exceptions, and recovery access. |
| Post-install evidence | Handoff reviewer | Checklist passes after a reboot and includes real service/path checks. |

## Anti-patterns

- Disabling the current login before testing the new administrator. Fix: keep one session open and prove a second key-based login.
- Opening broad firewall ranges for convenience. Fix: expose only approved services and verify from the intended source network.
- Installing the whole example stack regardless of role. Fix: select only owner-approved services.
- Changing SELinux to permissive to bypass a denial. Fix: diagnose labels/booleans and retain enforcing mode.
- Handing off before verification. Fix: complete access, update, firewall, service, logging, backup, and reboot checks.

## Section Overview

| # | Section | Est. time |
|---|---------|-----------|
| 1 | System update + hostname + timezone | 5 min |
| 2 | Admin user + sudo | 2 min |
| 3 | SSH hardening | 5 min |
| 4 | UFW firewall | 2 min |
| 5 | Automatic security updates | 2 min |
| 6 | Web stack (Nginx, Apache, PHP-FPM) | 10 min |
| 7 | Databases (MySQL, PostgreSQL, Redis) | 10 min |
| 8 | Supporting tools (fail2ban, certbot, rclone, msmtp, Node.js) | 10 min |
| 9 | Nginx snippets + catch-all config | 10 min |
| 10 | Clone linux-skills + install sk-* scripts | 5 min |
| 11 | Post-install security check | 5 min |

---

## Critical Steps (Do Not Skip)

```bash
# After SSH hardening — ALWAYS test in a second terminal before closing first:
ssh administrator@<server-ip>

# After Apache port change — verify it's on 8080 not 80:
ss -tlnp | grep apache

# After MySQL install — bind to localhost:
grep bind-address /etc/mysql/mysql.conf.d/mysqld.cnf

# Final check:
sudo bash ~/.claude/skills/scripts/server-audit.sh
```

---

## Quick Reference

```bash
# Test Nginx config
sudo nginx -t && sudo systemctl reload nginx

# All services should be active after provisioning:
for s in nginx apache2 mysql postgresql php8.3-fpm redis fail2ban; do
    printf "%-20s %s\n" $s "$(systemctl is-active $s)"
done

# Verify firewall
sudo ufw status verbose
```

Full step-by-step installation commands: `references/provisioning-steps.md`
Next step after provisioning: verify identity, firewall, and services via
`linux-access-control` and `linux-firewall-ssl`.

---

## Boot / bootloader management

Part of standing up a host is owning its boot path — GRUB2 config, which kernel
is the default, boot parameters, and (critically) being able to **roll back to a
known-good kernel after a panic**. This lives here because it is provisioning-time
ownership of the boot path; *recovery* of a broken/unbootable GRUB from rescue
media belongs to `linux-disaster-recovery`.

```bash
# List installed kernels; mark the running one and the GRUB default
sudo sk-kernel-rollback --list

# After booting a prior kernel from the GRUB menu post-panic, make it the default
sudo sk-kernel-rollback                 # interactive pick + confirm
sudo sk-kernel-rollback --to 5.15.0-91-generic

# Regenerate GRUB after editing /etc/default/grub
sudo update-grub                         # Debian/Ubuntu
sudo grub2-mkconfig -o /boot/grub2/grub.cfg   # RHEL family
```

Full model, per-family commands, and the post-panic rollback workflow:
`references/grub2-and-kernel-rollback.md`

---

## References

- [`references/provisioning-steps.md`](references/provisioning-steps.md)
- [`references/post-install-verification.md`](references/post-install-verification.md)
- [`references/grub2-and-kernel-rollback.md`](references/grub2-and-kernel-rollback.md) — GRUB2 config model per family, default-kernel and boot-parameter management, kernel lifecycle, and rolling back to a known-good kernel after a panic
- [`../linux-cloud-init/references/kickstart-reference.md`](../linux-cloud-init/references/kickstart-reference.md) — Kickstart automated install (RHEL family)
- [`../linux-virtualization/references/selinux-reference.md`](../linux-virtualization/references/selinux-reference.md) — SELinux on a fresh RHEL server
- [`../linux-disaster-recovery/SKILL.md`](../linux-disaster-recovery/SKILL.md) — GRUB *regeneration after corruption* and initramfs/filesystem repair from a rescue environment (use when GRUB itself is broken, not just the kernel)
- [`references/details.md`](references/details.md)
