# Popular PowerShell Modules

## Azure (Az Module 14.5.0)

**Latest:** Az 14.5.0 (October 2025) with zone redundancy and symbolic links

```powershell
# Install Azure module 14.5.0
Install-PSResource -Name Az -Scope CurrentUser
# Or: Install-Module -Name Az -Scope CurrentUser -Force

# Connect to Azure
Connect-AzAccount

# Common operations
Get-AzVM
Get-AzResourceGroup
New-AzResourceGroup -Name "MyRG" -Location "EastUS"

# NEW in Az 14.5: Zone redundancy for storage
New-AzStorageAccount -ResourceGroupName "MyRG" -Name "storage123" `
    -Location "EastUS" -SkuName "Standard_LRS" -EnableZoneRedundancy

# NEW in Az 14.5: Symbolic links in NFS File Share
New-AzStorageFileSymbolicLink -Context $ctx -ShareName "nfsshare" `
    -Path "symlink" -Target "/target/path"
```

**Key Submodules:**
- `Az.Accounts` - Authentication (MFA required Sep 2025+)
- `Az.Compute` - VMs, scale sets
- `Az.Storage` - Storage accounts (zone redundancy support)
- `Az.Network` - Virtual networks, NSGs
- `Az.KeyVault` - Key Vault operations
- `Az.Resources` - Resource groups, deployments

## Microsoft Graph (Microsoft.Graph 2.32.0)

**CRITICAL:** MSOnline and AzureAD modules retired (March-May 2025). Use Microsoft.Graph instead.

```powershell
# Install Microsoft Graph 2.32.0 (October 2025)
Install-PSResource -Name Microsoft.Graph -Scope CurrentUser
# Or: Install-Module -Name Microsoft.Graph -Scope CurrentUser

# Connect with required scopes
Connect-MgGraph -Scopes "User.Read.All", "Group.ReadWrite.All"

# Common operations
Get-MgUser
Get-MgGroup
New-MgUser -DisplayName "John Doe" -UserPrincipalName "john@domain.com" -MailNickname "john"
Get-MgTeam

# Migration from AzureAD/MSOnline
# OLD: Connect-AzureAD / Connect-MsolService
# NEW: Connect-MgGraph
# OLD: Get-AzureADUser / Get-MsolUser
# NEW: Get-MgUser
```

## PnP PowerShell (SharePoint/Teams)

```powershell
# Install PnP PowerShell
Install-Module -Name PnP.PowerShell -Scope CurrentUser

# Connect to SharePoint Online
Connect-PnPOnline -Url "https://tenant.sharepoint.com/sites/site" -Interactive

# Common operations
Get-PnPList
Get-PnPFile -Url "/sites/site/Shared Documents/file.docx"
Add-PnPListItem -List "Tasks" -Values @{"Title"="New Task"}
```

## AWS Tools for PowerShell

```powershell
# Install AWS Tools
Install-Module -Name AWS.Tools.Installer -Force
Install-AWSToolsModule AWS.Tools.EC2,AWS.Tools.S3

# Configure credentials
Set-AWSCredential -AccessKey $accessKey -SecretKey $secretKey -StoreAs default

# Common operations
Get-EC2Instance
Get-S3Bucket
New-S3Bucket -BucketName "my-bucket"
```

## Other Popular Modules

```powershell
# Pester (Testing framework)
Install-Module -Name Pester -Force

# PSScriptAnalyzer (Code analysis)
Install-Module -Name PSScriptAnalyzer

# ImportExcel (Excel manipulation without Excel)
Install-Module -Name ImportExcel

# PowerShellGet 3.x (Modern package management)
Install-Module -Name Microsoft.PowerShell.PSResourceGet
```
