---
name: win11-admin
description: "Windows 11 system administration and hardening: registry, services, Group Policy, debloating and telemetry, performance tuning, CIS/STIG hardening, firewall, Defender, scheduled tasks, drivers, Windows Update, and user accounts. Use when asked for any Windows 11 Pro/Enterprise admin task. Provides production-ready PowerShell commands, registry paths, GPO settings, hardening baselines, and rollback procedures."
license: MIT
compatibility: "Windows 11 Pro/Enterprise; PowerShell 5.1 or 7+; admin rights for most operations"
metadata:
  author: myphsto
  version: "1.0"
---

# Windows 11 Administration & Hardening

## CRITICAL: Safety Rules

1. **ALWAYS create a System Restore Point before changes**
2. **ALWAYS backup registry keys before modifying them**
3. **ALWAYS test on non-production systems first**
4. **NEVER disable Windows Update completely**
5. **NEVER disable Windows Defender without explicit user consent**
6. **Provide rollback commands for every change**

```powershell
# Create restore point before ANY system change
Checkpoint-Computer -Description "Before Win11 Admin changes" -RestorePointType MODIFY_SETTINGS

# Backup specific registry key before modification
reg export "HKLM\SOFTWARE\Key" "$env:USERPROFILE\backups\reg_backup_$(Get-Date -Format yyyyMMdd_HHmmss).reg"
```

---

## Domain Reference Files

Read the relevant reference file for the domain the user is asking about. Do not load all files — only the one(s) matching the request.

| Domain | Reference File | Covers |
|--------|---------------|--------|
| Registry | [`references/registry.md`](references/registry.md) | HKLM/HKCU operations, taskbar tweaks, explorer settings, rollbacks |
| Services | [`references/services.md`](references/services.md) | Service management, safe-to-disable list, critical services |
| Group Policy | [`references/gpo.md`](references/gpo.md) | Telemetry, privacy, Defender, lock screen, gpedit.msc paths |
| Debloating | [`references/debloating.md`](references/debloating.md) | AppX removal, telemetry disable, Copilot/Recall, NEVER-remove list |
| Performance | [`references/performance.md`](references/performance.md) | Visual effects, power plans, memory/disk, startup optimization |
| Security | [`references/security.md`](references/security.md) | CIS benchmark, audit policy, SMB, UAC, BitLocker, rollbacks |
| Firewall | [`references/firewall.md`](references/firewall.md) | Profile management, rules, export/import |
| Network | [`references/network.md`](references/network.md) | IP/DNS config, connections, adapters, Wi-Fi |
| Scheduled Tasks | [`references/tasks.md`](references/tasks.md) | Task CRUD, telemetry tasks to disable |
| Windows Update | [`references/updates.md`](references/updates.md) | Update check, pause, active hours, WSUS |
| Users & Permissions | [`references/users.md`](references/users.md) | Local users/groups, UAC, ACL management |
| Diagnostics | [`references/diagnostics.md`](references/diagnostics.md) | System/hardware info, event logs, SFC/DISM |

### Cross-Domain References

| Reference File | Covers |
|---------------|--------|
| [`references/quick_ref.md`](references/quick_ref.md) | Common tasks table, MMC shortcuts, registry hives, service startup types, NEVER-disable/remove lists |
| [`references/asr_rules.md`](references/asr_rules.md) | Attack Surface Reduction rule GUIDs, modes, enable/verify commands |

---

## When to Activate

PROACTIVELY activate for ANY Windows 11 administration task:

- Registry modifications (HKLM, HKCU, policies)
- Service management (disable, enable, startup type)
- Group Policy configuration (local or domain)
- Bloatware removal and telemetry control
- Performance optimization (visual effects, memory, disk)
- Security hardening (CIS, STIG, DISA baselines)
- Firewall rules and network configuration
- Windows Defender settings and exclusions
- Scheduled tasks management
- Driver and hardware troubleshooting
- Windows Update control and WSUS
- User accounts, UAC, and permissions

---

## Workflow

1. **Identify the domain** from the user's request
2. **Read the matching reference file** — only load what's needed
3. **Create a restore point** before any destructive change
4. **Preview before applying** — show what will change, get confirmation
5. **Provide rollback commands** alongside every change
