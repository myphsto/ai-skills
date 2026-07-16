# User & Permission Management

```powershell
# List local users
Get-LocalUser | Select-Object Name, Enabled, LastLogon, PasswordExpires

# List local groups
Get-LocalGroup | Select-Object Name, Description

# Get group members
Get-LocalGroupMember -Group "Administrators"

# Create local user
New-LocalUser -Name "newuser" -Password (Read-Host -AsSecureString "Password") -FullName "New User" -Description "Created by admin"

# Add user to group
Add-LocalGroupMember -Group "Administrators" -Member "newuser"

# Disable user
Disable-LocalUser -Name "username"

# Check UAC level
Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" | Select-Object EnableLUA, ConsentPromptBehaviorAdmin, PromptOnSecureDesktop

# File/folder permissions
Get-Acl "C:\Folder" | Format-List

# Set permissions
$acl = Get-Acl "C:\Folder"
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule("Users","ReadAndExecute","ContainerInherit,ObjectInherit","None","Allow")
$acl.SetAccessRule($rule)
Set-Acl "C:\Folder" $acl
```
