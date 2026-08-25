---
name: powershell-master
description: "PowerShell hub skill for cross-platform scripting, CI/CD, debugging, optimization, and module discovery. Use when a general PowerShell 7+ question is not covered by a specialized skill. Do not use for: security (use powershell-security), 7.5/7.6 features or PSResourceGet (use powershell-75-features), shell detection (use powershell-shell-detection), 2025 breaking changes (use powershell-2025-changes), or Windows admin (use win11-admin)."
license: MIT
compatibility: "PowerShell 7+ (pwsh) on Windows, Linux, or macOS; Windows PowerShell 5.1 for legacy notes"
metadata:
  author: myphsto
  version: "1.0"
---

# PowerShell Master

## Quick Navigation

> **Specialized skills take priority — delegate before answering:**

| Topic | Skill |
|-------|-------|
| Security (JEA, WDAC, SecretManagement, signing) | `powershell-security` |
| PSResourceGet, 7.5/7.6 features | `powershell-75-features` |
| Shell detection (PowerShell vs Git Bash) | `powershell-shell-detection` |
| 2025 breaking changes & migrations | `powershell-2025-changes` |
| Windows admin (registry, services, GPO) | `win11-admin` |

---

## When This Skill Applies

Use for general PowerShell questions **not** covered by the specialized skills above:

- Cross-platform PowerShell 7+ scripting
- CI/CD pipeline PowerShell integration
- Script debugging and optimization
- PowerShell module discovery and help
- Script structure best practices

---

## PowerShell Versions

| Version | Platform | Notes |
|---------|----------|-------|
| **7+ (pwsh)** | Windows/Linux/macOS | Recommended, cross-platform |
| **5.1** | Windows only | Legacy, built-in |

---

## Module Management

> **See `powershell-75-features` for PSResourceGet coverage**

```powershell
# Modern (recommended)
Install-PSResource -Name Az -Scope CurrentUser
Find-PSResource -Name "*Azure*"
Update-PSResource -Name Az
Get-InstalledPSResource

# Legacy (still works)
Install-Module -Name Az -Scope CurrentUser -Force
```

---

## Performance Optimization

```powershell
# Parallel ForEach (PS 7+)
1..10 | ForEach-Object -Parallel {
    Start-Sleep -Seconds 1
    "Processed $_"
} -ThrottleLimit 5

# Use .NET methods for performance
[System.IO.File]::ReadLines("large.txt") | Where-Object {$_ -match "pattern"}

# Use -Filter parameter when available
Get-ChildItem -Path C:\ -Filter *.log -Recurse

# ArrayList vs Array
$list = [System.Collections.ArrayList]::new()
1..1000 | ForEach-Object { [void]$list.Add($_) }
```

---

## Testing with Pester

```powershell
Install-Module -Name Pester -Force

Describe "Get-Something Tests" {
    Context "When input is valid" {
        It "Should return expected value" {
            $result = Get-Something -Name "Test"
            $result | Should -Be "Expected"
        }
    }
}

Invoke-Pester -Path ./tests -OutputFormat NUnitXml -OutputFile TestResults.xml
```

---

## Script Structure Best Practices

```powershell
<#
.SYNOPSIS    Brief description
.DESCRIPTION Detailed description
.PARAMETER Name Parameter description
.EXAMPLE    PS> .\script.ps1 -Name "John"
.NOTES      Author: Your Name | Version: 1.0.0
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$Name
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

try {
    Write-Verbose "Starting script"
    # ... script code ...
    Write-Verbose "Script completed successfully"
}
catch {
    Write-Error "Script failed: $_"
    exit 1
}
finally {
    # Cleanup
}
```

---

## Pre-Flight Checklist for Scripts

1. Platform Detection - Use `$IsWindows`, `$IsLinux`, `$IsMacOS`
2. Version Check - `#Requires -Version 7.0` if needed
3. Module Requirements - `#Requires -Modules` specified
4. Error Handling - `try/catch` blocks in place
5. Input Validation - Parameter validation attributes used
6. No Aliases - Full cmdlet names in scripts
7. Path Handling - Use `Join-Path` or `[IO.Path]::Combine()`
8. Encoding Specified - UTF-8 for cross-platform
9. Credentials Secure - Never hardcoded
10. Verbose Logging - `Write-Verbose` for debugging

---

## Common Pitfalls & Solutions

> **Note:** Version-specific pitfalls (e.g., Out-GridView in 7.5) belong in `powershell-75-features` or `powershell-2025-changes`. This section covers general, version-agnostic issues.

### Case Sensitivity
```powershell
# Linux/macOS are case-sensitive - use exact casing or Test-Path first
if (Test-Path "file.txt") { Get-Content "file.txt" }
```

### Execution Policy
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Or: powershell.exe -ExecutionPolicy Bypass -File script.ps1
```

### Module Import Failures
```powershell
if (-not (Get-Module -ListAvailable -Name Az)) {
    Install-Module -Name Az -Force -Scope CurrentUser
}
Import-Module -Name Az
```

### Array Concatenation Performance
```powershell
# Good: Use ArrayList or List
$list = [System.Collections.Generic.List[object]]::new()
$list.Add($item)
```

---

## Module Discovery & Help

```powershell
# Find modules
Find-Module -Tag "Azure"
Get-Command -Module Az.Compute
Get-Command -Verb Get -Noun *VM*

# Get help
Get-Help Get-AzVM -Full
Get-Help Get-AzVM -Examples
Get-Help Get-AzVM -Online

# Update help
Update-Help -Force -ErrorAction SilentlyContinue
```

---

## References

> **See [`references/cross_platform.md`](references/cross_platform.md)** for cross-platform best practices
> **See [`references/syntax.md`](references/syntax.md)** for variables, operators, control flow, functions
> **See [`references/modules.md`](references/modules.md)** for Az, Microsoft.Graph, PnP, AWS Tools
> **See [`references/cicd.md`](references/cicd.md)** for GitHub Actions, Azure DevOps, Bitbucket Pipelines
> **See [`references/cmdlet_ref.md`](references/cmdlet_ref.md)** for FileSystem, Process, Service, Network, Object Manipulation

---

Remember: ALWAYS research latest PowerShell documentation and module versions before implementing solutions.
