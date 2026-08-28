# Constrained Language Mode, Logging & Input Validation

## Constrained Language Mode

### What is Constrained Language Mode?

Restricts PowerShell language features to prevent malicious code execution.

```powershell
# Check current language mode
$ExecutionContext.SessionState.LanguageMode
# Output: "FullLanguage" on a default Windows install (verified: Win11 25H2,
# both PS 7.x and 5.1, admin AND standard-user sessions).

# ConstrainedLanguage appears only when AppLocker/WDAC (Device Guard) policy is
# in effect. NOTE: the legacy "__PSLockdownPolicy = 4" environment variable NO
# LONGER forces CLM on current Windows (verified: no-op in PS 7.x and 5.1 on
# Win11 25H2), and PowerShell 7 ignores the Windows PowerShell language-mode GPO
# registry values. There is no per-process registry/env toggle on modern builds.

# Test constrained mode behavior
# FullLanguage allows:
[System.Net.WebClient]::new()  # Allowed

# ConstrainedLanguage blocks:
[System.Net.WebClient]::new()  # Blocked
Add-Type -TypeDefinition "..."  # Blocked
```

## Script Block Logging

### Enable Logging

```powershell
# Enable via Group Policy or Registry
# The ScriptBlockLogging policy key does NOT exist by default - create it first.
# HKLM:\Software\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging
New-Item -Path "HKLM:\Software\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" -Force | Out-Null
New-ItemProperty -Path "HKLM:\Software\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" `
     -Name "EnableScriptBlockLogging" -Value 1 -PropertyType DWord
New-ItemProperty -Path "HKLM:\Software\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" `
     -Name "EnableScriptBlockInvocationLogging" -Value 1 -PropertyType DWord

# Log location: Windows Event Log
# Event Viewer > Applications and Services Logs > Microsoft > Windows > PowerShell > Operational
```

### Review Logs

```powershell
# Query script block logs
Get-WinEvent -LogName "Microsoft-Windows-PowerShell/Operational" |
    Where-Object { $_.Id -eq 4104 } |  # Script Block Logging event
    Select-Object TimeCreated, Message |
    Out-GridView
```

## Input Validation

### Prevent Injection Attacks

```powershell
# WRONG - No validation
function Get-UserData {
    param($Username)
    Invoke-Sqlcmd -Query "SELECT * FROM Users WHERE Username = '$Username'"
}
# Vulnerable to SQL injection

# CORRECT - Parameterized queries
function Get-UserData {
    param(
        [ValidatePattern('^[a-zA-Z0-9_-]+$')]
        [string]$Username
    )
    Invoke-Sqlcmd -Query "SELECT * FROM Users WHERE Username = @Username" `
        -Variable @{Username=$Username}
}

# CORRECT - ValidateSet for known values
function Restart-AppService {
    param(
        [ValidateSet('Web', 'API', 'Worker')]
        [string]$ServiceName
    )
    Restart-Service -Name "App${ServiceName}Service"
}
```
