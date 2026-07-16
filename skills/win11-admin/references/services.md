# Services Management

## Service Operations

```powershell
# List all services with status
Get-Service | Sort-Object Status, Name | Format-Table Name, DisplayName, Status, StartType

# Get specific service info
Get-Service -Name "wuauserv" | Select-Object *

# Check service dependencies
Get-Service -Name "wuauserv" -DependentServices
Get-Service -Name "wuauserv" -RequiredServices

# Change startup type
Set-Service -Name "ServiceName" -StartupType Disabled   # Disabled/Manual/Automatic/AutomaticDelayedStart

# Stop and disable
Stop-Service -Name "ServiceName" -Force
Set-Service -Name "ServiceName" -StartupType Disabled

# Start and set automatic
Set-Service -Name "ServiceName" -StartupType Automatic
Start-Service -Name "ServiceName"
```

## Safe-to-Disable Services (Win11 Pro)

```powershell
# Services commonly safe to disable on standalone workstations
# ALWAYS verify before disabling - requirements vary by environment

$safeToDisable = @(
    "DiagTrack"          # Connected User Experiences and Telemetry
    "dmwappushservice"   # WAP Push Message Routing
    "MapsBroker"         # Downloaded Maps Manager
    "RetailDemo"         # Retail Demo Service
    "WMPNetworkSvc"      # Windows Media Player Network Sharing
    "XblAuthManager"     # Xbox Live Auth Manager
    "XblGameSave"        # Xbox Live Game Save
    "XboxGipSvc"         # Xbox Accessory Management
    "XboxNetApiSvc"      # Xbox Live Networking
)

# Review before disabling
$safeToDisable | ForEach-Object {
    $svc = Get-Service -Name $_ -ErrorAction SilentlyContinue
    if ($svc) {
        [PSCustomObject]@{
            Name = $svc.Name
            DisplayName = $svc.DisplayName
            Status = $svc.Status
            StartType = $svc.StartType
        }
    }
}

# Disable after review (user must confirm)
# $safeToDisable | ForEach-Object {
#     Set-Service -Name $_ -StartupType Disabled -ErrorAction SilentlyContinue
# }
```

## NEVER Disable These Services

```
- wuauserv (Windows Update)
- WinDefend (Windows Defender)
- EventLog (Windows Event Log)
- RpcSs (Remote Procedure Call)
- LSM (Local Session Manager)
- Schedule (Task Scheduler)
- Winmgmt (WMI)
- CryptSvc (Cryptographic Services)
- BITS (Background Intelligent Transfer)
```
