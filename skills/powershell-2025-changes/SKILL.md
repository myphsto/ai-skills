---
name: powershell-2025-changes
description: "Critical PowerShell changes, deprecations, and migrations for 2025. PROACTIVELY activate for: (1) PowerShell 7.5 GA changes, (2) PowerShell 7.6 preview features, (3) Windows PowerShell 5.1 deprecation timeline, (4) PSReadLine 2.4+ updates, (5) Az PowerShell 14.x breaking changes, (6) Microsoft.Graph migration from AzureAD/MSOnline modules, (7) PSResourceGet replacing PowerShellGet 2.x, (8) DSC v3 and migration from DSC v1/v2, (9) ExecutionPolicy and constrained language mode updates, (10) .NET 9/.NET 10 integration impact. Provides: deprecation timeline, breaking-change checklist, migration scripts (AzureAD to Microsoft.Graph), and PSResourceGet upgrade steps."
---

# PowerShell 2025 Breaking Changes & Migrations

Critical changes, deprecations, and migration paths for PowerShell in 2025.

## PowerShell 2.0 Removal (August-September 2025)

### What's Removed

PowerShell 2.0 has been **completely removed** from:
- **Windows 11 version 24H2** (August 2025)
- **Windows Server 2025** (September 2025)

**Why:** Security improvements, reduced attack surface, legacy code cleanup

### Migration Path

```powershell
# Check if PowerShell 2.0 is installed
Get-WindowsOptionalFeature -Online -FeatureName MicrosoftWindowsPowerShellV2Root

# If you still need PowerShell 2.0 (NOT RECOMMENDED)
# - Use older Windows versions
# - Use Windows containers with older base images
# - Upgrade scripts to PowerShell 5.1 or 7+

# Recommended: Migrate to PowerShell 7.5+
winget install Microsoft.PowerShell
```

**Action Required:** Audit all scripts and remove `-Version 2.0` parameters from any PowerShell invocations.

---

## MSOnline & AzureAD Module Retirement

### Retirement Timeline

| Module | Stop Working | Retirement Complete |
|--------|--------------|---------------------|
| **MSOnline** | Late May 2025 | May 31, 2025 |
| **AzureAD** | March 30, 2025 | After July 1, 2025 |

**Critical:** These modules will stop functioning - not just deprecated, but **completely non-functional**.

### Migration Path

**From MSOnline/AzureAD to Microsoft.Graph:**

```powershell
# OLD (MSOnline) - STOPS WORKING MAY 2025
Connect-MsolService
Get-MsolUser
Set-MsolUser -UserPrincipalName "user@domain.com" -UsageLocation "US"

# NEW (Microsoft.Graph 2.32.0)
Connect-MgGraph -Scopes "User.ReadWrite.All"
Get-MgUser
Update-MgUser -UserId "user@domain.com" -UsageLocation "US"

# OLD (AzureAD) - STOPS WORKING MARCH 2025
Connect-AzureAD
Get-AzureADUser
New-AzureADUser -DisplayName "John Doe" -UserPrincipalName "john@domain.com"

# NEW (Microsoft.Graph 2.32.0)
Connect-MgGraph -Scopes "User.ReadWrite.All"
Get-MgUser
New-MgUser -DisplayName "John Doe" -UserPrincipalName "john@domain.com"
```

**Alternative:** Use Microsoft Entra PowerShell module (successor to AzureAD)

```powershell
Install-Module -Name Microsoft.Graph.Entra -Scope CurrentUser
Connect-Entra
Get-EntraUser
```

### Common Command Mappings

| MSOnline/AzureAD | Microsoft.Graph | Notes |
|------------------|----------------|-------|
| `Get-MsolUser` / `Get-AzureADUser` | `Get-MgUser` | Requires User.Read.All scope |
| `Get-MsolGroup` / `Get-AzureADGroup` | `Get-MgGroup` | Requires Group.Read.All scope |
| `Get-MsolDevice` / `Get-AzureADDevice` | `Get-MgDevice` | Requires Device.Read.All scope |
| `Connect-MsolService` / `Connect-AzureAD` | `Connect-MgGraph` | Scope-based permissions |

---

## WMIC Removal (Windows 11 25H2)

### What's Removed

**Windows Management Instrumentation Command-line (WMIC)** tool removed after upgrading to Windows 11 25H2+.

### Migration Path

**From WMIC to PowerShell WMI/CIM:**

```powershell
# OLD (WMIC) - REMOVED
wmic process list brief
wmic os get caption

# NEW (PowerShell CIM)
Get-CimInstance -ClassName Win32_Process | Select-Object Name, ProcessId, CommandLine
Get-CimInstance -ClassName Win32_OperatingSystem | Select-Object Caption, Version

# For detailed process info
Get-Process | Format-Table Name, Id, CPU, WorkingSet -AutoSize

# For system info
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion
```

---

## PowerShellGet → PSResourceGet Migration

> **See `powershell-7.5-features` skill for full PSResourceGet coverage** (commands, performance, security, Azure Artifacts).

**Key change:** PSResourceGet is the official successor to PowerShellGet (2x faster). Legacy `Install-Module` commands work via compatibility layer.

---

## Test-Json Schema Changes

### Breaking Change (PowerShell 7.4+)

**Test-Json** now uses **JsonSchema.NET** instead of **Newtonsoft.Json.Schema**.

**Impact:** No longer supports Draft 4 JSON schemas.

```powershell
# OLD (Draft 4 schema) - NO LONGER SUPPORTED
$schema = @"
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object"
}
"@

Test-Json -Json $json -Schema $schema  # FAILS in PowerShell 7.4+

# NEW (Draft 6+ schema) - SUPPORTED
$schema = @"
{
  "$schema": "http://json-schema.org/draft-06/schema#",
  "type": "object"
}
"@

Test-Json -Json $json -Schema $schema  # WORKS
```

---

## #Requires -PSSnapin Removed

### Breaking Change (PowerShell 7.4+)

All code related to `#Requires -PSSnapin` has been removed.

```powershell
# OLD (PowerShell 5.1 and earlier)
#Requires -PSSnapin Microsoft.Exchange.Management.PowerShell.SnapIn

# NEW (Use modules instead)
#Requires -Modules ExchangeOnlineManagement

Import-Module ExchangeOnlineManagement
Connect-ExchangeOnline
```

---

## Security Hardening (2025 Standards)

> **See `powershell-security` skill for full coverage of:** JEA configuration, WDAC policies, Constrained Language Mode, Script Block Logging, and code signing.

**2025 requirement:** Implement JEA for production environments and evaluate WDAC for script control.

---

## PowerShell 7.6 Preview Features

### Current Status (October 2025)

PowerShell 7.6.0 Preview 5 available (built on .NET 9.0.101)

**New Features:**
- **PSRedirectToVariable**: Allow redirecting to a variable
- **Module Rename**: ThreadJob → Microsoft.PowerShell.ThreadJob
- **PSResourceGet 1.1.0**: Improved performance and Azure Artifacts support

```powershell
# Check PowerShell version
$PSVersionTable.PSVersion
# 7.5.4 (stable) or 7.6.0-preview.5

# .NET version
[System.Runtime.InteropServices.RuntimeInformation]::FrameworkDescription
# .NET 9.0.101
```

---

## Migration Checklist

### Immediate Actions Required (2025)

- [ ] **Audit MSOnline/AzureAD usage** - Migrate to Microsoft.Graph 2.32.0 before May 2025
- [ ] **Remove PowerShell 2.0 references** - Upgrade to PowerShell 7.5+
- [ ] **Replace WMIC commands** - Use Get-CimInstance/Get-Process
- [ ] **Update JSON schemas** - Migrate Draft 4 to Draft 6+
- [ ] **Remove PSSnapin requirements** - Convert to modules
- [ ] **Adopt PSResourceGet** - See `powershell-7.5-features` for details
- [ ] **Implement JEA** - See `powershell-security` for configuration
- [ ] **Enable WDAC** - See `powershell-security` for policy templates
- [ ] **Test Constrained Language Mode** - See `powershell-security` for setup

### Recommended Actions

- [ ] **Upgrade to PowerShell 7.5.4** - Latest stable with .NET 9 (see `powershell-7.5-features`)
- [ ] **Adopt Az 14.5.0** - Latest Azure module with zone redundancy
- [ ] **Use Microsoft.Graph 2.32.0** - Actively maintained Graph SDK
- [ ] **Enable Script Block Logging** - See `powershell-security`
- [ ] **Implement Code Signing** - See `powershell-security`
- [ ] **Use Azure Key Vault** - See `powershell-security` for SecretManagement setup

---

## Testing Migration

```powershell
# Test for deprecated module usage
Get-Module MSOnline, AzureAD -ListAvailable
# If found, plan migration immediately

# Test for PowerShell 2.0 dependencies
Get-Content "script.ps1" | Select-String -Pattern "powershell.exe -Version 2"
# If found, remove version parameter

# Test for WMIC usage
Get-ChildItem -Path "C:\Scripts" -Recurse -Filter "*.ps1" |
    Select-String -Pattern "wmic" |
    Select-Object Path, Line

# Verify PowerShell version compatibility
#Requires -Version 7.0
Test-Path $PSCommandPath  # Ensures script is PowerShell 7+
```

---

## Resources

- [PowerShell 7.5 Release Notes](https://learn.microsoft.com/en-us/powershell/scripting/whats-new/what-s-new-in-powershell-75)
- [MSOnline/AzureAD Retirement Info](https://techcommunity.microsoft.com/blog/microsoft-entra-blog/action-required-msonline-and-azuread-powershell-retirement---2025-info-and-resou/4364991)
- **PSResourceGet details:** `powershell-7.5-features` skill
- **JEA/WDAC/Security:** `powershell-security` skill

---

**Last Updated:** October 2025
