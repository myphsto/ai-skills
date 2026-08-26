---
name: linux-access-control
description: "Use when creating, revoking, or auditing Linux users, groups, SSH keys, sudo/wheel access, PAM settings, SELinux user mappings, or file permissions. Use linux-firewall-ssl for firewall and TLS policy and linux-intrusion-detection for active threat response."
license: MIT
compatibility: "Linux (Debian/Ubuntu or RHEL family); root for most operations"
metadata:
  author: myphsto
  version: "1.0"
  source: "https://github.com/peterbamuhigire/linux-skills"
---

# Access Control

## Distro support

Two-family skill. `useradd`/`usermod`/`passwd`, SSH keys, and `/etc/sudoers.d/`
work the same on both. The notable differences are the **admin group** and a
couple of RHEL-only auth/SELinux layers. Body uses Debian/Ubuntu; substitute
per this matrix.

| Concept | Debian/Ubuntu | RHEL family |
|---|---|---|
| Sudo admin group | `sudo` | `wheel` |
| Grant admin | `usermod -aG sudo <u>` | `usermod -aG wheel <u>` |
| User/group tools | `useradd`, `usermod`, `passwd` | identical |
| Sudoers drop-ins | `/etc/sudoers.d/` | same |
| PAM config | `/etc/pam.d/` | `/etc/pam.d/` (managed via `authselect` on RHEL) |
| Password quality | `libpam-pwquality` | `pam_pwquality` (in `pwquality.conf`) |
| SELinux user mapping | n/a | `semanage login` maps Linux users → SELinux users |

**RHEL-family note:** the admin group is `wheel`, not `sudo`. RHEL manages the
PAM/nsswitch stack through `authselect` (don't hand-edit what it owns), and
SELinux can confine users (`semanage login`, `semanage user`). See
[`../linux-virtualization/references/selinux-reference.md`](../linux-virtualization/references/selinux-reference.md)

## Use when

- Managing Linux users, groups, sudo access, SSH keys, or file permissions.
- Auditing who can log in or who has elevated access on a server.
- Fixing ownership or permission problems in web roots, home directories, or credential files.

## Do not use when

- The task is firewalling or TLS; use `linux-firewall-ssl`.
- The task is a full security posture audit or broad hardening — outside this skill set; scope to concrete identity, SSH, sudo, PAM, or permission changes.

## Required inputs

| Artefact | Source | Required? | If absent |
|---|---|---|---|
| Target identities, groups, paths, keys, and requested privileges | Access request or system owner | required | Stay read-only and return the missing identity/scope. |
| Current account, group, sudoers, SSH, PAM, and file state | Target host | required | Do not mutate; provide inspection commands only. |
| Approval, expiry, owner, and recovery access | Authorised approver | required for mutation | Stop before granting or revoking access. |

## Decision rules

| Choice | Action | Failure or risk avoided |
|---|---|---|
| Temporary privileged task | Use narrow sudo command rules with expiry | Permanent broad administration. |
| Suspected compromised key | Disable that key, preserve evidence, rotate dependants | Continued unauthorised access. |
| Account departure | Disable, inventory ownership/jobs, transfer, then remove | Orphaned data and services. |

## Workflow

1. Identify the account or path being changed and inspect current state first.
2. Apply the least-privilege change with the manual commands below.
3. Re-check login access, sudo membership, and file ownership after the change.
4. Use optional scripts only when they are installed and clearly match the task.
5. Stop if the approver, target identity, recovery administrator, or ownership boundary is unresolved.
6. Recover a failed access change through the tested alternate session, restore the saved sudoers/key/file state, and verify login again.

## Outputs

| Artefact | Consumer | Acceptance condition |
|---|---|---|
| Access decision/change record | System owner | Names identity, privilege, approver, expiry, files changed, and rationale. |
| Final-state verification | Operator | Login, group/sudo membership, key fingerprints, and affected permissions match the request. |
| Recovery note | On-call administrator | Preserves a tested alternate administrator and reversal steps. |

## Anti-patterns

- Running recursive `chmod` or `chown` without scoping the target. Fix: inspect boundaries and change only the named tree or files.
- Granting sudo or shell access without an approved need. Fix: use the least privilege and record the owner and expiry.
- Deleting an account before reviewing its files, processes, jobs, and keys. Fix: disable first, inventory dependencies, then remove deliberately.
- Editing `/etc/sudoers` without validation. Fix: use a drop-in and validate with `visudo` before ending the recovery session.
- Revoking the only working administrator or SSH key. Fix: prove an independent break-glass path first.

## User Management

```bash
sudo adduser <username>                         # create (interactive)
sudo usermod -aG sudo <username>                # grant sudo
sudo deluser <username>                         # remove user (keeps home)
sudo deluser --remove-home <username>           # remove user + home
sudo passwd -l <username>                       # lock account
sudo passwd -u <username>                       # unlock account

# Audit
grep -v "nologin\|false" /etc/passwd | cut -d: -f1,3
grep ^sudo /etc/group                           # who has sudo
awk -F: '$3 == 0 {print $1}' /etc/passwd       # UID-0 accounts
```

---

## SSH Key Management

```bash
# Add a key for a user
mkdir -p /home/<username>/.ssh
chmod 700 /home/<username>/.ssh
echo "<public-key>" >> /home/<username>/.ssh/authorized_keys
chmod 600 /home/<username>/.ssh/authorized_keys
chown -R <username>:<username> /home/<username>/.ssh

# Audit all keys on the server
find /home /root -name authorized_keys 2>/dev/null | \
    while read f; do echo "=== $f ==="; cat "$f"; done

# Revoke: edit the file, delete the key line
sudo nano /home/<username>/.ssh/authorized_keys

# Test before restarting SSH (keep existing session open!)
sudo sshd -t && sudo systemctl restart sshd
```

---

## File Permissions — Quick Reference

```bash
# Web root standard
sudo find /var/www -type d -exec chmod 755 {} \;
sudo find /var/www -type f -exec chmod 644 {} \;
sudo chown -R www-data:www-data /var/www/html/
sudo find /var/www -type f -perm -0002 -exec chmod o-w {} \;   # remove world-write

# Critical system files
sudo chmod 640 /etc/shadow /etc/gshadow
sudo chmod 644 /etc/passwd /etc/group

# Backup credentials (must be 600)
chmod 600 ~/.mysql-backup.cnf ~/.backup-encryption-key
chmod 600 ~/.config/rclone/rclone.conf
chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys
```

Full permission patterns and audit commands: `references/permissions-reference.md`

---

## References

- [`references/users-sudoers-pam.md`](references/users-sudoers-pam.md)
- [`references/permissions-reference.md`](references/permissions-reference.md)
- [`../linux-virtualization/references/selinux-reference.md`](../linux-virtualization/references/selinux-reference.md) — SELinux user confinement (RHEL family)
- [`references/details.md`](references/details.md)
