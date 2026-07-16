# Windows Update Management

```powershell
# Check for updates (requires PSWindowsUpdate module)
# Install-Module -Name PSWindowsUpdate -Force
# Get-WindowsUpdate

# Check update history
Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 20

# Current Windows version
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsBuildNumber

# Pause updates (35 days max via registry)
$pauseDate = (Get-Date).AddDays(35).ToString("yyyy-MM-ddTHH:mm:ssZ")
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings" -Name "PauseUpdatesExpiryTime" -Value $pauseDate

# Active hours (prevent restarts during work)
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings" -Name "ActiveHoursStart" -Value 8
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings" -Name "ActiveHoursEnd" -Value 23

# WSUS configuration (enterprise)
# New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate" -Force
# Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate" -Name "WUServer" -Value "https://wsus.company.com:8531"
```
