# PowerShell 7.5 Feature Details

Full usage examples, performance data, and 7.4 → 7.5 migration patterns for PowerShell 7.5.

Related: [cicd-benchmarks.md](cicd-benchmarks.md) (CI/CD integration, .NET 9 benchmark details), [powershell-7.6-features.md](powershell-7.6-features.md) (7.6 features).

## Contents

- [New Cmdlets](#new-cmdlets)
  - [ConvertTo-CliXml and ConvertFrom-CliXml](#convertto-clixm-and-convertfrom-clixm)
  - [Enhanced Test-Path Cmdlet](#enhanced-test-path-cmdlet)
  - [Enhanced Web Cmdlets](#enhanced-web-cmdlets)
  - [Enhanced Test-Json Cmdlet](#enhanced-test-json-cmdlet)
  - [Enhanced Resolve-Path and Convert-Path](#enhanced-resolve-path-and-convert-path)
  - [New-FileCatalog Version 2 Default](#new-filecatalog-version-2-default)
- [PSResourceGet](#psresourceget)
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

**Availability:** these cmdlets are new in PowerShell 7.5+. They do not exist in
Windows PowerShell 5.1 (verified absent on a patched Win11 25H2) or in 7.4.x, so
feature-detect with `Get-Command ConvertTo-CliXml -ErrorAction SilentlyContinue`
and fall back to `Export-Clixml` / `Import-Clixml` on older hosts.

### Enhanced Test-Path Cmdlet

#### -OlderThan and -NewerThan Parameters

Filter paths by modification time.

**Note:** these parameters are not new in 7.5 — they date back to **Windows PowerShell 3.0** (verified working on 7.4.19 and later).

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

Save response to file AND return content.

**Note:** combining `-OutFile` with `-PassThru` already works in **7.4.19**, so it is not new in 7.5.

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

#### -Options (relaxed JSON) and ConvertFrom-Json -DateKind

Relaxed JSON support landed in 7.5 as **enum options on `Test-Json`**, not as `-IgnoreComments`/`-AllowTrailingCommas` parameters (those do not exist on `ConvertFrom-Json` or `Test-Json`).

```powershell
# Validate JSON that contains comments (7.5+)
Test-Json -Json $jsonWithComments -Options IgnoreComments

# Validate JSON with trailing commas (7.5+)
Test-Json -Json $jsonTrailing -Options AllowTrailingCommas

# Both relaxed options together
Test-Json -Json $relaxedJson -Options IgnoreComments, AllowTrailingCommas
```

`ConvertFrom-Json` gained **`-DateKind`** in 7.5 to control how string dates are converted:

```powershell
# Interpret dates as UTC
$obj = $json | ConvertFrom-Json -DateKind Utc

# Interpret dates as local
$obj = $json | ConvertFrom-Json -DateKind Local
```

**Use Cases:**
- Validate configuration files with comments (JSONC)
- Accept relaxed JSON from JavaScript tools
- Control date-parse semantics when reading JSON
- Config file validation

### Enhanced Resolve-Path and Convert-Path

#### -Force Parameter for Wildcard Hidden Files

Access hidden/system files with wildcards. Verified: the **`-Force` parameter is new in 7.5** (absent in 7.4.19), covering both `Resolve-Path` and `Convert-Path`:

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

`New-FileCatalog` supports a `-CatalogVersion` parameter (there is **no** `-Force` parameter). Version 2 uses SHA256 and is the default in PowerShell 7.x.

```powershell
# Version 2 by default in 7.x
New-FileCatalog -Path "C:\Project" -CatalogFilePath "catalog.cat"
# Creates a version 2 catalog (SHA256)

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

Verified: catalogs written with `-CatalogVersion 2` embed the SHA256 object identifier (and no MD5 OID); version 1 catalogs contain neither. There is no `Get-FileCatalog` cmdlet.

## PSResourceGet

### Modern Package Management

PSResourceGet is the official successor to PowerShellGet and is **bundled with PowerShell 7.4+**. It is a coordinated separate release, so the exact version varies by install (check with `Get-Module ... -ListAvailable`; do not assume a specific number).

**Key Features:**
- **Faster module metadata operations** (install/search/update) than module 1.x PowerShellGet
- **SecretManagement integration** for secure credential storage
- **Azure Artifacts support** - enterprise private feed integration
- **Better error handling** - clearer error messages and retry logic

```powershell
# Check what ships in this install (version varies)
Get-Module Microsoft.PowerShell.PSResourceGet -ListAvailable

# New commands
Install-PSResource -Name Az -Scope CurrentUser
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
# 7.5.10 (latest 7.5 LTS)

# .NET version
[System.Runtime.InteropServices.RuntimeInformation]::FrameworkDescription
# .NET 9.x

# PSResourceGet version
Get-Module Microsoft.PowerShell.PSResourceGet -ListAvailable
# Version varies per install (keep this check, don't hardcode)
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

5. **Validate relaxed JSON with Test-Json -Options:**
```powershell
# Configuration files with comments (JSONC)
Test-Json -Json (Get-Content "config.jsonc" -Raw) -Options IgnoreComments
```

6. **Control date parsing with ConvertFrom-Json -DateKind:**
```powershell
$req = Get-Content "response.json" -Raw | ConvertFrom-Json -DateKind Utc
```

## Backward Compatibility

PowerShell 7.5 maintains compatibility with 7.x scripts:
- All 7.0-7.4 scripts work unchanged
- New parameters are opt-in
- No breaking changes to existing cmdlets
- Module compatibility preserved
