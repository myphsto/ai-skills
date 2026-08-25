# Just Enough Administration (JEA)

## What is JEA?

**Just Enough Administration** restricts PowerShell remoting sessions to specific cmdlets and parameters.

## Use Cases

- Delegate admin tasks without full admin rights
- Compliance requirements (SOC 2, HIPAA, PCI-DSS)
- Production environment hardening
- Audit trail for privileged operations

## Creating a JEA Endpoint

```powershell
# 1. Create role capability file
New-PSRoleCapabilityFile -Path "C:\JEA\RestartServices.psrc" `
    -VisibleCmdlets @{
        Name = 'Restart-Service'
        Parameters = @{
            Name = 'Name'
            ValidateSet = 'Spooler', 'W32Time', 'WinRM'
        }
    }, 'Get-Service'

# 2. Create session configuration file
New-PSSessionConfigurationFile -Path "C:\JEA\RestartServices.pssc" `
    -SessionType RestrictedRemoteServer `
    -RoleDefinitions @{
        'DOMAIN\ServiceAdmins' = @{ RoleCapabilities = 'RestartServices' }
    } `
    -LanguageMode NoLanguage

# 3. Register JEA endpoint
Register-PSSessionConfiguration -Name RestartServices `
    -Path "C:\JEA\RestartServices.pssc" `
    -Force

# 4. Connect to JEA endpoint (as delegated user)
Enter-PSSession -ComputerName Server01 -ConfigurationName RestartServices

# User can ONLY run allowed commands
Restart-Service -Name Spooler  # Allowed
Restart-Service -Name DNS      # Denied (not in ValidateSet)
Get-Process                    # Denied (not visible)
```

## JEA Audit Logging

```powershell
# Enable transcription and logging
New-PSSessionConfigurationFile -Path "C:\JEA\AuditedSession.pssc" `
    -SessionType RestrictedRemoteServer `
    -TranscriptDirectory "C:\JEA\Transcripts" `
    -RunAsVirtualAccount

# All JEA sessions are transcribed to C:\JEA\Transcripts
# Review audit logs
Get-ChildItem "C:\JEA\Transcripts" | Get-Content
```
