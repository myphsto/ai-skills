# Performance Optimization

## Visual Effects

```powershell
# Disable animations and visual effects for performance
$path = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
Set-ItemProperty -Path $path -Name "VisualFXSetting" -Value 2  # 2=Custom

$advanced = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
Set-ItemProperty -Path $advanced -Name "TaskbarAnimations" -Value 0

# Disable transparency effects
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" -Name "EnableTransparency" -Value 0

# Disable animation effects via SystemParametersInfo
# Best performance settings
$regPath = "HKCU:\Control Panel\Desktop"
Set-ItemProperty -Path $regPath -Name "UserPreferencesMask" -Value ([byte[]](0x90,0x12,0x03,0x80,0x10,0x00,0x00,0x00))
Set-ItemProperty -Path $regPath -Name "MenuShowDelay" -Value "0"

# Disable window animations
Set-ItemProperty -Path "HKCU:\Control Panel\Desktop\WindowMetrics" -Name "MinAnimate" -Value "0"
```

## Power Plan

```powershell
# List power plans
powercfg /list

# Set High Performance
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c

# Create Ultimate Performance plan (desktop)
powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61

# Disable hibernation (saves disk space)
powercfg /hibernate off

# Disable USB selective suspend
powercfg /setacvalueindex SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0
powercfg /setactive SCHEME_CURRENT
```

## Memory & Disk

```powershell
# Check memory usage
Get-CimInstance Win32_OperatingSystem | Select-Object @{N='TotalGB';E={[math]::Round($_.TotalVisibleMemorySize/1MB,2)}}, @{N='FreeGB';E={[math]::Round($_.FreePhysicalMemory/1MB,2)}}, @{N='UsedPct';E={[math]::Round((1-$_.FreePhysicalMemory/$_.TotalVisibleMemorySize)*100,1)}}

# Check disk space
Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{N='UsedGB';E={[math]::Round($_.Used/1GB,2)}}, @{N='FreeGB';E={[math]::Round($_.Free/1GB,2)}}

# Disk cleanup (silent)
cleanmgr /sagerun:1

# Clear temp files
Remove-Item "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "C:\Windows\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue

# Clear Windows Update cache
Stop-Service wuauserv -Force
Remove-Item "C:\Windows\SoftwareDistribution\Download\*" -Recurse -Force
Start-Service wuauserv

# Analyze disk usage (largest folders)
Get-ChildItem "C:\" -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    [PSCustomObject]@{
        Folder = $_.FullName
        SizeGB = [math]::Round((Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum / 1GB, 2)
    }
} | Sort-Object SizeGB -Descending | Format-Table
```

## Startup Optimization

```powershell
# List startup programs
Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location

# Registry startup locations
Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -ErrorAction SilentlyContinue
Get-ItemProperty "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run" -ErrorAction SilentlyContinue

# Scheduled tasks at startup
Get-ScheduledTask | Where-Object {$_.Triggers -match "AtStartup" -or $_.Triggers -match "AtLogon"} | Select-Object TaskName, State

# Disable specific startup item
Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "ProgramName" -ErrorAction SilentlyContinue
```
