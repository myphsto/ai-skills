---
name: linux-intrusion-detection
description: "Use when operating fail2ban, investigating its bans, or running qualified rkhunter/chkrootkit checks. Compliance-grade auditing (auditd, AIDE) is outside this skill set."
license: MIT
compatibility: "Linux (Debian/Ubuntu or RHEL family); root for most operations"
metadata:
  author: myphsto
  version: "1.0"
  source: "https://github.com/peterbamuhigire/linux-skills"
---

# Intrusion Detection

## Distro support

Two-family skill. fail2ban and the rootkit scanners (rkhunter, chkrootkit)
run on both families; install and a couple of paths differ, and the RHEL
family adds SELinux AVC denials as an intrusion signal. Body uses
Debian/Ubuntu; substitute per this matrix. **auditd and AIDE are outside
this skill set** (compliance/forensic tooling is not included).

| Concept | Debian/Ubuntu | RHEL family |
|---|---|---|
| fail2ban install | `apt install fail2ban` | `dnf install fail2ban` (**EPEL** on RHEL/Rocky/Alma; main on Fedora) |
| fail2ban backend | reads `/var/log/auth.log` | reads journald / `/var/log/secure` (use `backend = systemd`) |
| rkhunter / chkrootkit | `apt install rkhunter chkrootkit` | `dnf install rkhunter chkrootkit` (**EPEL** on RHEL/Rocky/Alma/Oracle; main on Fedora) |
| Rootkit scan auto-run | `/etc/cron.daily/rkhunter` + `/etc/default/rkhunter` | no packaged wrapper — use systemd timer / cron |
| MAC denials as IDS signal | AppArmor (`journalctl -k \| grep apparmor`) | **SELinux AVC** (`ausearch -m AVC`, `aureport --avc`) |
| Web/auth log paths | `/var/log/auth.log` | `/var/log/secure` |

**RHEL-family note:** fail2ban on RHEL usually needs `backend = systemd` (and
the right `logpath`/journal match) because `/var/log/auth.log` does not exist —
auth events go to `/var/log/secure` and journald. Treat new SELinux AVC denials
as a triage signal. See
[`../linux-virtualization/references/selinux-reference.md`](../linux-virtualization/references/selinux-reference.md)

## Use when

- Managing fail2ban or rootkit scanners (rkhunter/chkrootkit) on Ubuntu/Debian or RHEL-family servers.
- Investigating bans or rootkit-scanner warnings.
- Hardening host monitoring after repeated abuse or suspicious changes.

## Do not use when

- The task is perimeter firewalling or certificates; use `linux-firewall-ssl`.
- The task is a broad read-only security audit or full hardening — outside this skill set.
- The task is system-call auditing (auditd) — outside this skill set.
- The task is file-integrity / hash drift (AIDE) — outside this skill set.

## Required inputs

| Artefact | Source | Required? | If absent |
|---|---|---|---|
| Host, distro, time window, and signal | Incident owner, alert, or host logs | yes | Inspect current status only; do not claim an incident |
| Known-good baseline and change history | Configuration management or owner | for attribution | Treat integrity warnings as unresolved leads |
| Response authority | Incident commander | for mutation | Preserve evidence; do not ban, tune, or re-baseline |

## Decision rules

| Evidence | Action | Failure avoided |
|---|---|---|
| Failures match a jail and policy | Apply authorised ban or tuning | Blocking an address without evidence |
| Warning matches an approved package change | Record benign disposition | Persistent false positive |
| Unexpected change lacks explanation | Preserve evidence and escalate | Baseline laundering |
| SELinux AVC alone | Investigate context | False intrusion declaration |

## Workflow

1. Establish host, clock, log coverage, and authorised boundary; stop when scope is unclear.
2. Preserve the alert and correlated auth, journal, or SELinux records before mutation.
3. Compare the signal with package history and trusted baselines; stop if attribution is unsupported.
4. Classify it as explained, suspicious, confirmed, or unassessed.
5. Apply only authorised reversible containment; restore saved config if validation fails.
6. Re-run the narrow check and record unresolved indicators.

## Outputs

| Artefact | Consumer | Acceptance condition |
|---|---|---|
| Finding disposition | Incident owner | Links each signal to timestamped evidence and confidence |
| Response record | Operations | Names authorised action and reversal |
| Coverage note | Security owner | States tools, logs, time range, and unassessed areas |

## Anti-patterns

- Disabling a noisy jail without understanding why it fired. Fix: test its filter against the triggering logs.
- Re-baselining blindly after a suspicious change. Fix: attribute the change before updating properties.
- Treating detection tooling as root-cause analysis. Fix: correlate the signal with system and application evidence.
- Banning an address from an alert summary alone. Fix: cite triggering records and policy.
- Treating a partial clean scan as a clean host. Fix: state tool and time coverage.
- Updating properties before explanation. Fix: preserve and attribute changes first.

## fail2ban

```bash
sudo fail2ban-client status                      # all jails + count
sudo fail2ban-client status <jail>               # specific jail (bans, IPs)
sudo tail -f /var/log/fail2ban.log               # live ban activity

# Unban an IP
sudo fail2ban-client set <jail> unbanip <ip>

# Reload after config change
sudo systemctl reload fail2ban
sudo fail2ban-client status                      # verify jails loaded
```

Full jail configuration templates: `references/fail2ban-jails.md`

---

## File integrity (AIDE) and system-call auditing (auditd) — out of scope

The two **compliance / forensic** layers (AIDE hash drift, auditd
system-call attribution) are not part of this skill set. This skill stays
focused on **active** intrusion detection: blocking abusive hosts (fail2ban)
and rootkit signature scanning (rkhunter/chkrootkit). When a scanner finding
needs deeper attribution, record it as evidence and stop — do not assume
auditd or AIDE tooling is available.

---

## Rootkit scanning (rkhunter + chkrootkit)

Signature/heuristic layer on top of AIDE (drift) and auditd (attribution).
rkhunter keeps a file-property baseline and checks for known rootkit
fingerprints; chkrootkit is a baseline-free signature scanner. Run **both** —
they catch different things, and agreement raises confidence.

```bash
# Install (RHEL family: enable EPEL first on RHEL/Rocky/Alma/Oracle)
sudo apt install rkhunter chkrootkit        # dnf install rkhunter chkrootkit

# Refresh definitions, then baseline file properties on a KNOWN-CLEAN host
sudo rkhunter --update
sudo rkhunter --propupd                     # like aideinit — clean host only!

# Scan
sudo rkhunter --check --sk --rwo            # --sk = no pause, --rwo = warnings only
sudo chkrootkit -q                          # -q = show only INFECTED/suspicious

# Re-baseline after a CONFIRMED-legitimate change (e.g. package upgrade)
sudo rkhunter --propupd
```

**Warnings are "verify", never "confirmed rootkit".** Most are false
positives (package updates, hidden `.git`, DHCP promiscuous mode). Confirm a
changed binary against the package (`dpkg -V` / `rpm -V`), whitelist the
*specific* false positive in `/etc/rkhunter.conf.local` (set `PKGMGR=DPKG` or
`RPM`), and never disable a whole test to silence one line. Correlate flagged
paths with AIDE and auditd before declaring an incident.

Install, scheduling (systemd timer / cron), false-positive tuning, and the
full triage flow: `references/rootkit-scanning.md`

---

## References

- [`references/fail2ban-jails.md`](references/fail2ban-jails.md)
- [`references/rootkit-scanning.md`](references/rootkit-scanning.md) — rkhunter + chkrootkit on both families (install, baseline, scheduling, false positives, triage)
- [`../linux-virtualization/references/selinux-reference.md`](../linux-virtualization/references/selinux-reference.md) — SELinux AVC denials as an IDS signal (RHEL family)
- [`references/details.md`](references/details.md)
