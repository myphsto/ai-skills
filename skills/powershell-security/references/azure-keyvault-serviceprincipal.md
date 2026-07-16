# Azure Key Vault & Service Principal Authentication

## Azure Key Vault Integration

```powershell
# Install and import Az.KeyVault
Install-Module -Name Az.KeyVault -Scope CurrentUser
Import-Module Az.KeyVault

# Authenticate to Azure
Connect-AzAccount

# Register Azure Key Vault as secret vault
Register-SecretVault -Name AzureKV `
    -ModuleName Az.KeyVault `
    -VaultParameters @{
        AZKVaultName = 'MyKeyVault'
        SubscriptionId = 'your-subscription-id'
    }

# Store secret in Azure Key Vault
Set-Secret -Name "ApiKey" -Secret "your-api-key" -Vault AzureKV

# Retrieve from Azure Key Vault
$apiKey = Get-Secret -Name "ApiKey" -Vault AzureKV -AsPlainText
```

## Automation Scripts with SecretManagement

```powershell
<#
.SYNOPSIS
    Secure automation script using SecretManagement

.DESCRIPTION
    Demonstrates secure credential handling without hardcoded secrets
#>

#Requires -Modules Microsoft.PowerShell.SecretManagement

[CmdletBinding()]
param()

# Retrieve credentials from vault
$dbConnectionString = Get-Secret -Name "SQLConnectionString" -AsPlainText
$apiToken = Get-Secret -Name "APIToken" -AsPlainText

# Use credentials securely
try {
    # Database operation
    $connection = New-Object System.Data.SqlClient.SqlConnection($dbConnectionString)
    $connection.Open()

    # API call with token
    $headers = @{ Authorization = "Bearer $apiToken" }
    $response = Invoke-RestMethod -Uri "https://api.example.com/data" -Headers $headers

    # Process results
    Write-Host "Operation completed successfully"
}
catch {
    Write-Error "Operation failed: $_"
}
finally {
    if ($connection) { $connection.Close() }
}
```

## Service Principal Authentication (Azure)

```powershell
# Store service principal credentials in vault
Set-Secret -Name "AzureAppId" -Secret "app-id-guid"
Set-Secret -Name "AzureAppSecret" -Secret "app-secret-value"
Set-Secret -Name "AzureTenantId" -Secret "tenant-id-guid"

# Retrieve and authenticate
$appId = Get-Secret -Name "AzureAppId" -AsPlainText
$appSecret = Get-Secret -Name "AzureAppSecret" -AsPlainText
$tenantId = Get-Secret -Name "AzureTenantId" -AsPlainText

$secureSecret = ConvertTo-SecureString $appSecret -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential($appId, $secureSecret)

Connect-AzAccount -ServicePrincipal -Credential $credential -Tenant $tenantId
```
