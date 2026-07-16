# Registry Administration

## Common Registry Hives

| Hive | Abbreviation | Scope |
|------|-------------|-------|
| HKEY_LOCAL_MACHINE | HKLM: | System-wide |
| HKEY_CURRENT_USER | HKCU: | Current user |
| HKEY_CLASSES_ROOT | HKCR: | File associations |
| HKEY_USERS | HKU: | All user profiles |

## Registry Operations

```powershell
# Read registry value
Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion" -Name "ProgramFilesDir"

# Create/set registry value
New-ItemProperty -Path "HKCU:\Software\MyApp" -Name "Setting" -Value 1 -PropertyType DWord -Force

# Modify existing value
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\System" -Name "EnableSmartScreen" -Value 1

# Delete registry value
Remove-ItemProperty -Path "HKCU:\Software\MyApp" -Name "Setting"

# Create registry key (folder)
New-Item -Path "HKLM:\SOFTWARE\Policies\MyPolicy" -Force

# Test if key/value exists
Test-Path "HKLM:\SOFTWARE\Policies\MyPolicy"
(Get-ItemProperty "HKLM:\SOFTWARE\MyKey" -Name "MyValue" -ErrorAction SilentlyContinue) -ne $null

# Export registry key (backup)
reg export "HKLM\SOFTWARE\Policies\Microsoft" "C:\backup\policies.reg" /y

# Import registry key (restore)
reg import "C:\backup\policies.reg"
```

## Common Win11 Registry Tweaks

```powershell
# --- TASKBAR ---
# Hide Search button (0=Hidden, 1=Icon, 2=SearchBox)
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Search" -Name "SearchboxTaskbarMode" -Value 0

# Hide Task View button
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "ShowTaskViewButton" -Value 0

# Hide Widgets
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "TaskbarDa" -Value 0

# Hide Chat/Teams icon
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "TaskbarMn" -Value 0

# Left-align taskbar (0=Left, 1=Center)
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "TaskbarAl" -Value 0

# --- EXPLORER ---
# Show file extensions
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "HideFileExt" -Value 0

# Show hidden files
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "Hidden" -Value 1

# Show full path in title bar
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\CabinetState" -Name "FullPath" -Value 1

# Disable Snap Assist flyout
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "SnapAssist" -Value 0

# Classic right-click context menu (Win10 style)
New-Item -Path "HKCU:\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" -Value "" -Force

# Revert to Win11 context menu
Remove-Item -Path "HKCU:\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}" -Recurse -Force

# --- STARTUP ---
# Disable startup delay
New-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Serialize" -Name "StartupDelayInMSec" -Value 0 -PropertyType DWord -Force
```

## Rollback Commands

```powershell
# --- TASKBAR ROLLBACK ---
# Restore Search button
Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Search" -Name "SearchboxTaskbarMode" -ErrorAction SilentlyContinue

# Restore Task View button
Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "ShowTaskViewButton" -ErrorAction SilentlyContinue

# Restore Widgets
Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "TaskbarDa" -ErrorAction SilentlyContinue

# Restore Chat/Teams icon
Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "TaskbarMn" -ErrorAction SilentlyContinue

# Restore centered taskbar
Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "TaskbarAl" -ErrorAction SilentlyContinue

# --- EXPLORER ROLLBACK ---
# Hide file extensions again
Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "HideFileExt" -ErrorAction SilentlyContinue

# Hide hidden files again
Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "Hidden" -ErrorAction SilentlyContinue

# Restore Snap Assist flyout
Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "SnapAssist" -ErrorAction SilentlyContinue

# Restore Win11 context menu
Remove-Item -Path "HKCU:\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}" -Recurse -Force -ErrorAction SilentlyContinue

# --- STARTUP ROLLBACK ---
Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Serialize" -Name "StartupDelayInMSec" -ErrorAction SilentlyContinue

# Full rollback: restart Explorer to apply
Stop-Process -Name explorer -Force
```
