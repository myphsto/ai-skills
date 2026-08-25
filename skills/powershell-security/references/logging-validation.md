# Constrained Language Mode, Logging & Input Validation

## Constrained Language Mode

### What is Constrained Language Mode?

Restricts PowerShell language features to prevent malicious code execution.

```powershell
# Check current language mode
$ExecutionContext.SessionState.LanguageMode
# Output: FullLanguage (admin) or ConstrainedLanguage (standard user)

# Set system-wide constrained language mode
# Via Environment Variable or Group Policy
# Set: __PSLockdownPolicy = 4

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
# HKLM:\Software\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging
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
