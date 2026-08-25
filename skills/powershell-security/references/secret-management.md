# SecretManagement & Credential Management

## SecretManagement Module (Recommended 2025 Standard)

### Overview

**Microsoft.PowerShell.SecretManagement** is the official solution for secure credential storage in PowerShell.

**Why use SecretManagement:**
- Never store plaintext credentials in scripts
- Cross-platform secret storage
- Multiple vault provider support
- Integration with Azure Key Vault, 1Password, KeePass, etc.

### Installation

```powershell
# Install SecretManagement module
Install-Module -Name Microsoft.PowerShell.SecretManagement -Scope CurrentUser

# Install vault provider (choose one or more)
Install-Module -Name Microsoft.PowerShell.SecretStore  # Local encrypted vault
Install-Module -Name Az.KeyVault                        # Azure Key Vault
Install-Module -Name SecretManagement.KeePass          # KeePass integration
```

### Basic Usage

```powershell
# Register a vault
Register-SecretVault -Name LocalVault -ModuleName Microsoft.PowerShell.SecretStore

# Store a secret
$password = Read-Host -AsSecureString -Prompt "Enter password"
Set-Secret -Name "DatabasePassword" -Secret $password -Vault LocalVault

# Retrieve a secret
$dbPassword = Get-Secret -Name "DatabasePassword" -Vault LocalVault -AsPlainText
# Or as SecureString
$dbPasswordSecure = Get-Secret -Name "DatabasePassword" -Vault LocalVault

# List secrets
Get-SecretInfo

# Remove a secret
Remove-Secret -Name "DatabasePassword" -Vault LocalVault
```

### Azure Key Vault & Automation

> **See [`azure-keyvault-serviceprincipal.md`](azure-keyvault-serviceprincipal.md)** for Azure Key Vault setup, Service Principal authentication, and full automation script template.

## Credential Management Best Practices

### Never Hardcode Credentials

```powershell
# WRONG - Hardcoded credentials
$password = "MyPassword123"
$username = "admin"

# WRONG - Plaintext in script
$cred = New-Object System.Management.Automation.PSCredential("admin", "password")

# CORRECT - SecretManagement
$password = Get-Secret -Name "AdminPassword" -AsPlainText
$securePassword = ConvertTo-SecureString $password -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential("admin", $securePassword)

# CORRECT - Interactive prompt (for manual runs)
$cred = Get-Credential -Message "Enter admin credentials"

# CORRECT - Managed Identity (Azure automation)
Connect-AzAccount -Identity
```

### Service Principal Authentication

> **See [`azure-keyvault-serviceprincipal.md`](azure-keyvault-serviceprincipal.md)** for Service Principal credential storage and authentication.
