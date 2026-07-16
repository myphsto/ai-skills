# Scheduled Tasks

```powershell
# List all scheduled tasks
Get-ScheduledTask | Select-Object TaskName, State, TaskPath | Sort-Object TaskPath, TaskName

# Get task details
Get-ScheduledTask -TaskName "TaskName" | Get-ScheduledTaskInfo

# Create scheduled task
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\Scripts\backup.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At "03:00"
$settings = New-ScheduledTaskSettingsSet -RunOnlyIfNetworkAvailable -WakeToRun
Register-ScheduledTask -TaskName "DailyBackup" -Action $action -Trigger $trigger -Settings $settings -User "SYSTEM" -RunLevel Highest

# Disable task
Disable-ScheduledTask -TaskName "TaskName"

# Remove task
Unregister-ScheduledTask -TaskName "TaskName" -Confirm:$false

# Run task immediately
Start-ScheduledTask -TaskName "TaskName"

# Common telemetry tasks to disable
$telemetryTasks = @(
    "\Microsoft\Windows\Application Experience\Microsoft Compatibility Appraiser"
    "\Microsoft\Windows\Application Experience\ProgramDataUpdater"
    "\Microsoft\Windows\Customer Experience Improvement Program\Consolidator"
    "\Microsoft\Windows\Customer Experience Improvement Program\UsbCeip"
    "\Microsoft\Windows\DiskDiagnostic\Microsoft-Windows-DiskDiagnosticDataCollector"
)

$telemetryTasks | ForEach-Object {
    $task = Get-ScheduledTask -TaskPath ($_ -replace '[^\\]*$','') -TaskName ($_ -replace '.*\\','') -ErrorAction SilentlyContinue
    if ($task) {
        Write-Host "Found: $($task.TaskName) [$($task.State)]"
    }
}
```
