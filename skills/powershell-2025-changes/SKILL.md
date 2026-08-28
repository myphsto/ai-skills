---
name: powershell-2025-changes
description: "PowerShell breaking changes, retired modules, and migration guidance. Activate when: (1) scripts fail due to retired MSOnline/AzureAD modules, (2) WMIC commands are missing, (3) Test-Json schema validation breaks, (4) PSSnapin requirements fail. DO NOT activate for current PowerShell features (use powershell-75-features), security hardening (use powershell-security), or general PowerShell scripting (use powershell-master)."
license: MIT
compatibility: "Windows with PowerShell 5.1 or 7+; PowerShell 7.4+ for Test-Json and PSSnapin changes"
metadata:
  author: myphsto
  version: "1.0"
---

# PowerShell Breaking Changes & Migration Guide

## Retired Modules (Already Retired)

### MSOnline & AzureAD → Microsoft.Graph

Both modules are **fully retired** and non-functional. Migrate to Microsoft.Graph or Microsoft Entra PowerShell.

```powershell
# Install replacement
Install-PSResource -Name Microsoft.Graph -Scope CurrentUser

# Migration mapping
# OLD (MSOnline)          → NEW (Microsoft.Graph)
Connect-MsolService       → Connect-MgGraph -Scopes "User.ReadWrite.All"
Get-MsolUser              → Get-MgUser
Set-MsolUser ...          → Update-MgUser ...
Get-MsolGroup             → Get-MgGroup

# Alternative: Microsoft Entra PowerShell
Install-PSResource -Name Microsoft.Graph.Entra -Scope CurrentUser
Connect-Entra
Get-EntraUser
```

### WMIC → CIM/PowerShell Cmdlets

WMIC is **removed** from Windows 11 24H2+. Use PowerShell equivalents.

```powershell
# OLD (WMIC)              → NEW (PowerShell)
wmic process list brief   → Get-CimInstance Win32_Process | Select Name, ProcessId, CommandLine
wmic os get caption       → Get-CimInstance Win32_OperatingSystem | Select Caption, Version
wmic cpu get name         → Get-CimInstance Win32_Processor | Select Name
```

---

## Breaking Changes

### Test-Json Schema (PowerShell 7.4+)

Switched from Newtonsoft.Json.Schema to JsonSchema.NET. The `$schema` dialect is
no longer honored the same way: simple draft-04 schemas still validate (verified
on 7.6.x), but keyword forms that only exist in draft-04 (e.g. boolean
`exclusiveMinimum`) throw `Cannot parse the JSON schema`. Migrate draft-04 schemas
to draft-06+ to be safe.

```powershell
# Update $schema URI from draft-04 to draft-06 or later
$schema = '{"$schema":"http://json-schema.org/draft-06/schema#","type":"object"}'
Test-Json -Json $json -Schema $schema
```

### #Requires -PSSnapin No Longer Enforced (PowerShell 7.4+)

Snap-ins are legacy. In PowerShell 7.x a `#Requires -PSSnapin` is silently
ignored and the script still runs; in 5.1 it blocks the script if the snap-in is
missing (both verified on Win11 25H2). Migrate to module requirements.

```powershell
# OLD
#Requires -PSSnapin Microsoft.Exchange.Management.PowerShell.SnapIn

# NEW
#Requires -Modules ExchangeOnlineManagement
Import-Module ExchangeOnlineManagement
```

---

## Migration Checklist

- [ ] Replace MSOnline/AzureAD with Microsoft.Graph
- [ ] Remove WMIC calls — use Get-CimInstance/Get-Process
- [ ] Update JSON schemas from Draft 4 to Draft 6+
- [ ] Replace `#Requires -PSSnapin` with `#Requires -Modules`
- [ ] Audit scripts for PowerShell 2.0 references

---

## Testing Migration

```powershell
# Find deprecated module usage in scripts
Get-ChildItem -Recurse -Filter "*.ps1" | Select-String -Pattern "MSOnline|AzureAD|wmic|PSSnapin"

# Verify PowerShell 7+ compatibility
#Requires -Version 7.0
Test-Path $PSCommandPath
```

---

## Related Skills

- **Current PowerShell 7.5/7.6 features:** `powershell-75-features`
- **Security hardening (JEA, WDAC, SecretManagement):** `powershell-security`
- **General PowerShell scripting:** `powershell-master`
