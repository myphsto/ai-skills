# System Information & Diagnostics

```powershell
# Full system info
Get-ComputerInfo | Select-Object CsName, WindowsProductName, WindowsVersion, OsBuildNumber, OsArchitecture, CsProcessors, CsTotalPhysicalMemory

# Hardware info
Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed
Get-CimInstance Win32_PhysicalMemory | Select-Object Manufacturer, Capacity, Speed, MemoryType
Get-CimInstance Win32_DiskDrive | Select-Object Model, Size, MediaType

# BIOS/UEFI info
Get-CimInstance Win32_BIOS | Select-Object Manufacturer, SMBIOSBIOSVersion, ReleaseDate

# Drivers
Get-CimInstance Win32_PnPSignedDriver | Where-Object DeviceName -ne $null | Select-Object DeviceName, DriverVersion, DriverDate | Sort-Object DeviceName

# System uptime
(Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime

# Event logs (errors last 24h)
Get-WinEvent -FilterHashtable @{LogName='System'; Level=2; StartTime=(Get-Date).AddHours(-24)} -ErrorAction SilentlyContinue | Select-Object TimeCreated, Id, Message -First 20

# Check system file integrity
# sfc /scannow
# DISM /Online /Cleanup-Image /RestoreHealth

# Installed software
Get-CimInstance Win32_Product | Select-Object Name, Version, Vendor | Sort-Object Name
# Faster alternative (registry-based)
Get-ItemProperty "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*" | Select-Object DisplayName, DisplayVersion, Publisher | Sort-Object DisplayName
```
