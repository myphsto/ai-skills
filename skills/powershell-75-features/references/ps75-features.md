# PowerShell 7.5 Feature Details

Full usage examples, performance data, and 7.4 → 7.5 migration patterns for PowerShell 7.5.

Related: [cicd-benchmarks.md](cicd-benchmarks.md) (CI/CD integration, .NET 9 benchmark details), [powershell-7.6-preview.md](powershell-7.6-preview.md) (7.6 preview features).

## Contents

- [New Cmdlets](#new-cmdlets)
  - [ConvertTo-CliXml and ConvertFrom-CliXml](#convertto-clixm-and-convertfrom-clixm)
  - [Enhanced Test-Path Cmdlet](#enhanced-test-path-cmdlet)
  - [Enhanced Web Cmdlets](#enhanced-web-cmdlets)
  - [Enhanced Test-Json Cmdlet](#enhanced-test-json-cmdlet)
  - [Enhanced Resolve-Path and Convert-Path](#enhanced-resolve-path-and-convert-path)
  - [New-FileCatalog Version 2 Default](#new-filecatalog-version-2-default)
- [PSResourceGet 1.1.1 (March 2025)](#psresourceget-111-march-2025)
- [Migration from PowerShell 7.4](#migration-from-powershell-74)
- [Best Practices for PowerShell 7.5](#best-practices-for-powershell-75)
- [Backward Compatibility](#backward-compatibility)

## New Cmdlets

### ConvertTo-CliXml and ConvertFrom-CliXml

Convert objects to/from CLI XML format without file I/O:

```powershell
# ConvertTo-CliXml - Convert object to XML string
$process = Get-Process -Name pwsh
$xmlString = $process | ConvertTo-CliXml

# ConvertFrom-CliXml - Convert XML string back to object
$restored = $xmlString | ConvertFrom-CliXml
$restored.ProcessName  # Outputs: pwsh

# Use cases:
# - Serialize objects for API transmission
# - Store object state in databases/caches
# - Share objects across PowerShell sessions
# - Clipboard operations with rich objects
```

**Difference from Export/Import-Clixml:**
- `Export-Clixml`: Writes to file
- `ConvertTo-CliXml`: Returns string (no file I/O)

### Enhanced Test-Path Cmdlet

#### -OlderThan and -NewerThan Parameters

Filter paths by modification time:

```powershell
# Find files older than 30 days
Test-Path "C:\Logs\*.log" -OlderThan (Get-Date).AddDays(-30)

# Find files newer than 1 hour
Test-Path "C:\Temp\*" -NewerThan (Get-Date).AddHours(-1)

# Cleanup old log files
Get-ChildItem "C:\Logs" -Filter "*.log" |
  Where-Object { Test-Path $_.FullName -OlderThan (Get-Date).AddDays(-90) } |
  Remove-Item -WhatIf

# Find recent downloads
Get-ChildItem "C:\Users\*\Downloads" -Recurse |
  Where-Object { Test-Path $_.FullName -NewerThan (Get-Date).AddDays(-7) }
```

**Use Cases:**
- Log rotation automation
- Backup file cleanup
- Recent file monitoring
- Cache invalidation

### Enhanced Web Cmdlets

#### -PassThru with -OutFile

Save response to file AND return content:

```powershell
# Before PowerShell 7.5 (choose one):
Invoke-WebRequest -Uri $url -OutFile "download.zip"  # Save only
$response = Invoke-WebRequest -Uri $url              # Return only

# PowerShell 7.5 (both):
$response = Invoke-WebRequest -Uri $url -OutFile "download.zip" -PassThru
$response.StatusCode  # 200
# File also saved to download.zip

# Download and verify
$result = Invoke-RestMethod -Uri "https://api.example.com/data.json" `
  -OutFile "data.json" `
  -PassThru

Write-Host "Downloaded $($result.Length) bytes"
# File saved to data.json
```

**Benefits:**
- Download progress tracking
- HTTP header inspection
- Status code verification
- Combined file save + content processing

### Enhanced Test-Json Cmdlet

#### IgnoreComments and AllowTrailingCommas

Parse relaxed JSON formats:

```powershell
# JSON with comments (previously invalid)
$jsonWithComments = @"
{
  // This is a comment
  "name": "example",  // inline comment
  /* Multi-line
     comment */
  "version": "1.0"
}
"@

# PowerShell 7.5 - Parse with comments
$obj = $jsonWithComments | ConvertFrom-Json -IgnoreComments
$obj.name  # Outputs: example

# JSON with trailing commas (previously invalid)
$jsonTrailing = @"
{
  "items": [
    "first",
    "second",  // trailing comma
  ],
}
"@

# PowerShell 7.5 - Parse with trailing commas
$obj = $jsonTrailing | ConvertFrom-Json -AllowTrailingCommas

# Validate JSON with relaxed syntax
Test-Json -Json $jsonWithComments -IgnoreComments
Test-Json -Json $jsonTrailing -AllowTrailingCommas
```

**Use Cases:**
- Parse configuration files with comments
- Handle JSON from JavaScript tools
- Accept relaxed JSON from APIs
- Config file validation

### Enhanced Resolve-Path and Convert-Path

#### -Force Parameter for Wildcard Hidden Files

Access hidden/system files with wildcards:

```powershell
# PowerShell 7.4 and earlier - Hidden files not matched
Resolve-Path "C:\Users\*\.*" | Select-Object -First 5
# Skips .vscode, .gitignore, etc.

# PowerShell 7.5 - Include hidden files
Resolve-Path "C:\Users\*\.*" -Force | Select-Object -First 5
# Includes .vscode, .gitignore, .bashrc, etc.

# Find all hidden config files
Resolve-Path "C:\Projects\*\.*" -Force |
  Where-Object { (Get-Item $_).Attributes -match "Hidden" }

# Convert-Path also supports -Force
Convert-Path "~/.config/*" -Force
```

**Use Cases:**
- Backup scripts including hidden files
- Configuration discovery
- Security audits
- Development environment setup

### New-FileCatalog Version 2 Default

FileCatalog version 2 is now default:

```powershell
# PowerShell 7.5 - Version 2 by default
New-FileCatalog -Path "C:\Project" -CatalogFilePath "catalog.cat"
# Creates version 2 catalog (SHA256)

# Explicitly specify version
New-FileCatalog -Path "C:\Project" `
  -CatalogFilePath "catalog.cat" `
  -CatalogVersion 2

# Test file integrity
Test-FileCatalog -Path "C:\Project" -CatalogFilePath "catalog.cat"
```

**Version Differences:**
- Version 1: SHA1 hashing (legacy)
- Version 2: SHA256 hashing (default, more secure)

## PSResourceGet 1.1.1 (March 2025)

### Modern Package Management

PSResourceGet is the official successor to PowerShellGet, offering significant performance improvements and enhanced security.

**Key Features:**
- **2x faster** module installation
- **Improved security** - SecretManagement integration for secure credential storage
- **Azure Artifacts support** - Enterprise private feed integration
- **Better error handling** - Clearer error messages and retry logic

```powershell
# Install PSResourceGet (included in PowerShell 7.4+)
Install-Module -Name Microsoft.PowerShell.PSResourceGet -Force

# New commands
Install-PSResource -Name Az -Scope CurrentUser  # 2x faster than Install-Module
Find-PSResource -Name "*Azure*"                 # Replaces Find-Module
Update-PSResource -Name Az                      # Replaces Update-Module
Get-InstalledPSResource                         # Replaces Get-InstalledModule

# Security best practice - use SecretManagement for credentials
Register-PSResourceRepository -Name "PrivateFeed" `
    -Uri "https://pkgs.dev.azure.com/org/project/_packaging/feed/nuget/v3/index.json" `
    -Trusted

# Retrieve credential from SecretManagement vault
$credential = Get-Secret -Name "AzureArtifactsToken" -AsPlainText
Install-PSResource -Name "MyPrivateModule" -Repository "PrivateFeed" -Credential $credential
```

**Performance Comparison:**
| Operation | PowerShellGet | PSResourceGet 1.1.1 | Improvement |
|-----------|--------------|---------------------|-------------|
| Install module | 10-15s | 5-7s | 2x faster |
| Search modules | 3-5s | 1-2s | 2-3x faster |
| Update module | 12-18s | 6-9s | 2x faster |

**Security Enhancements:**
- Never use plaintext credentials in scripts
- Use SecretManagement module for storing repository credentials
- Support for Azure DevOps Personal Access Tokens (PAT)
- Integrated authentication with Azure Artifacts

```powershell
# WRONG - plaintext credential
$cred = New-Object PSCredential("user", (ConvertTo-SecureString "password" -AsPlainText -Force))

# CORRECT - SecretManagement
Install-Module Microsoft.PowerShell.SecretManagement
Register-SecretVault -Name LocalVault -ModuleName Microsoft.PowerShell.SecretStore
Set-Secret -Name "RepoToken" -Secret "your-token"

$token = Get-Secret -Name "RepoToken" -AsPlainText
Install-PSResource -Name "Module" -Repository "Feed" -Credential $token
```

## Migration from PowerShell 7.4

### Check Version

```powershell
# Current version
$PSVersionTable.PSVersion
# 7.5.4 (latest stable as of October 2025)

# .NET version
[System.Runtime.InteropServices.RuntimeInformation]::FrameworkDescription
# .NET 9.0.306

# PSResourceGet version
Get-Module Microsoft.PowerShell.PSResourceGet -ListAvailable
# Version 1.1.1 (latest as of March 2025)
```

### Update Scripts for 7.5

```powershell
# Replace file-based XML serialization
# Before:
$data | Export-Clixml -Path "temp.xml"
$xml = Get-Content "temp.xml" -Raw
Remove-Item "temp.xml"

# After:
$xml = $data | ConvertTo-CliXml

# Use new Test-Path filtering
# Before:
Get-ChildItem | Where-Object {
  $_.LastWriteTime -lt (Get-Date).AddDays(-30)
}

# After:
Get-ChildItem | Where-Object {
  Test-Path $_.FullName -OlderThan (Get-Date).AddDays(-30)
}

# Leverage -PassThru for downloads
# Before:
Invoke-WebRequest -Uri $url -OutFile "file.zip"
$size = (Get-Item "file.zip").Length

# After:
$response = Invoke-WebRequest -Uri $url -OutFile "file.zip" -PassThru
$size = $response.RawContentLength
```

## Best Practices for PowerShell 7.5

1. **Use ConvertTo/From-CliXml for in-memory serialization:**
```powershell
# Serialize to clipboard
$data | ConvertTo-CliXml | Set-Clipboard

# Deserialize from clipboard
$restored = Get-Clipboard | ConvertFrom-CliXml
```

2. **Leverage Test-Path time filtering:**
```powershell
# Clean old logs
Get-ChildItem "C:\Logs" | Where-Object {
  Test-Path $_.FullName -OlderThan (Get-Date).AddDays(-90)
} | Remove-Item
```

3. **Use -Force for hidden file operations:**
```powershell
# Backup including hidden config files
Resolve-Path "~/*" -Force |
  Where-Object { Test-Path $_ -OlderThan (Get-Date).AddDays(-1) } |
  Copy-Item -Destination "C:\Backup\"
```

4. **Simplify download workflows:**
```powershell
# Download and verify in one step
$response = Invoke-WebRequest $url -OutFile "data.zip" -PassThru
if ($response.StatusCode -eq 200) {
  Expand-Archive "data.zip" -Destination "data/"
}
```

5. **Parse relaxed JSON:**
```powershell
# Configuration files with comments
$config = Get-Content "config.jsonc" -Raw |
  ConvertFrom-Json -IgnoreComments
```

## Backward Compatibility

PowerShell 7.5 maintains compatibility with 7.x scripts:
- All 7.0-7.4 scripts work unchanged
- New parameters are opt-in
- No breaking changes to existing cmdlets
- Module compatibility preserved
