# Debloating

## Remove Pre-installed Apps

```powershell
# List all installed UWP/AppX packages
Get-AppxPackage | Select-Object Name, PackageFullName | Sort-Object Name

# List provisioned packages (installed for all users)
Get-AppxProvisionedPackage -Online | Select-Object DisplayName

# Common bloatware to remove
$bloatware = @(
    "Microsoft.BingNews"
    "Microsoft.BingWeather"
    "Microsoft.GamingApp"
    "Microsoft.GetHelp"
    "Microsoft.Getstarted"
    "Microsoft.MicrosoftOfficeHub"
    "Microsoft.MicrosoftSolitaireCollection"
    "Microsoft.People"
    "Microsoft.PowerAutomateDesktop"
    "Microsoft.Todos"
    "Microsoft.WindowsAlarms"
    "Microsoft.WindowsFeedbackHub"
    "Microsoft.WindowsMaps"
    "Microsoft.WindowsSoundRecorder"
    "Microsoft.Xbox.TCUI"
    "Microsoft.XboxGameOverlay"
    "Microsoft.XboxGamingOverlay"
    "Microsoft.XboxIdentityProvider"
    "Microsoft.XboxSpeechToTextOverlay"
    "Microsoft.YourPhone"
    "Microsoft.ZuneMusic"
    "Microsoft.ZuneVideo"
    "MicrosoftTeams"
    "Clipchamp.Clipchamp"
    "Microsoft.549981C3F5F10"  # Cortana
)

# Preview what would be removed
$bloatware | ForEach-Object {
    $pkg = Get-AppxPackage -Name $_ -ErrorAction SilentlyContinue
    if ($pkg) { Write-Host "Found: $($pkg.Name)" -ForegroundColor Yellow }
    else { Write-Host "Not found: $_" -ForegroundColor Gray }
}

# Remove for current user (uncomment after review)
# $bloatware | ForEach-Object {
#     Get-AppxPackage -Name $_ | Remove-AppxPackage -ErrorAction SilentlyContinue
# }

# Remove provisioned (prevents reinstall for new users)
# $bloatware | ForEach-Object {
#     Get-AppxProvisionedPackage -Online | Where-Object DisplayName -eq $_ |
#         Remove-AppxProvisionedPackage -Online -ErrorAction SilentlyContinue
# }
```

## NEVER Remove These

```
- Microsoft.WindowsStore (Store - needed for updates)
- Microsoft.WindowsCalculator
- Microsoft.WindowsTerminal
- Microsoft.DesktopAppInstaller (winget)
- Microsoft.VCLibs (Visual C++ runtime)
- Microsoft.UI.Xaml (UI framework)
- Microsoft.NET (runtime)
- Microsoft.HEIFImageExtension / Microsoft.WebpImageExtension (image codecs)
```

## Disable Telemetry & Tracking

```powershell
# Disable Diagnostic Data
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Name "AllowTelemetry" -Value 0

# Disable feedback notifications
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Siuf\Rules" -Name "NumberOfSIUFInPeriod" -Value 0 -Force

# Disable app suggestions and pre-installed apps
$cdm = "HKCU:\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"
Set-ItemProperty -Path $cdm -Name "ContentDeliveryAllowed" -Value 0
Set-ItemProperty -Path $cdm -Name "OemPreInstalledAppsEnabled" -Value 0
Set-ItemProperty -Path $cdm -Name "PreInstalledAppsEnabled" -Value 0
Set-ItemProperty -Path $cdm -Name "SilentInstalledAppsEnabled" -Value 0
Set-ItemProperty -Path $cdm -Name "SoftLandingEnabled" -Value 0
Set-ItemProperty -Path $cdm -Name "SubscribedContentEnabled" -Value 0
Set-ItemProperty -Path $cdm -Name "SystemPaneSuggestionsEnabled" -Value 0

# Disable Copilot (Win11 23H2+)
New-Item -Path "HKCU:\Software\Policies\Microsoft\Windows\WindowsCopilot" -Force
Set-ItemProperty -Path "HKCU:\Software\Policies\Microsoft\Windows\WindowsCopilot" -Name "TurnOffWindowsCopilot" -Value 1

# Disable Recall (Win11 24H2+)
New-Item -Path "HKCU:\Software\Policies\Microsoft\Windows\WindowsAI" -Force
Set-ItemProperty -Path "HKCU:\Software\Policies\Microsoft\Windows\WindowsAI" -Name "DisableAIDataAnalysis" -Value 1
```
