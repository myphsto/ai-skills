# ASR Rules Reference

## Attack Surface Reduction Rule GUIDs

| GUID | Rule | Recommended Mode |
|------|------|-----------------|
| `BE9BA2D9-53EA-4CDC-84E5-9B1EEEE46550` | Block executable content from email/webmail | Block |
| `D4F940AB-401B-4EFC-AADC-AD5F3C50688A` | Block Office apps from creating child processes | Block |
| `3B576869-A4EC-4529-8536-B80A7769E899` | Block Office apps from creating executable content | Block |
| `75668C1F-73B5-4CF0-BB93-3ECF5CB7CC84` | Block Office apps from injecting into other processes | Block |
| `D3E037E1-3EB8-44C8-A917-57927947596D` | Block JavaScript/VBScript launching downloaded content | Block |
| `5BEB7EFE-FD9A-4556-801D-275E5FFC04CC` | Block execution of potentially obfuscated scripts | Block |
| `92E97FA1-2EDF-4476-BDD6-9DD0B4DDDC7B` | Block Win32 API calls from Office macros | Block |
| `01443614-CD74-433A-B99E-2ECDC07BFC25` | Block executable files unless they meet criteria | Audit |
| `C1DB55AB-C21A-4637-BB3F-A12568109D35` | Use advanced protection against ransomware | Block |
| `9E6C4E1F-7D60-472F-BA1A-A39EF669E4B2` | Block credential stealing from LSASS | Block |
| `D1E49AAC-8F56-4280-B9BA-993A6D77406C` | Block process creations from PSExec and WMI | Audit |
| `B2B3F03D-6A65-4F7B-A9C7-1C7EF74A9BA4` | Block untrusted/unsigned processes from USB | Audit |
| `26190899-1602-49E8-8B27-EB1D0A1CE869` | Block Office communication apps from creating child processes | Block |
| `7674BA52-37EB-4A4F-A9A1-F0F9A1619A2C` | Block Adobe Reader from creating child processes | Block |
| `E6DB77E5-3DF2-4CF1-B95A-636979351E5B` | Block persistence through WMI event subscription | Block |
| `56A863A9-875E-4185-98A7-B882C64B5CE5` | Block abuse of exploited vulnerable signed drivers | Block |

## ASR Rule Actions

| Value | Action | Use Case |
|-------|--------|----------|
| `1` | Block | Production - enforce policy |
| `2` | Audit | Testing - log without blocking |
| `6` | Warn | User notification |

## Enable ASR Rules

```powershell
# Enable in Block mode (production)
Add-MpPreference -AttackSurfaceReductionRules_Ids $guid -AttackSurfaceReductionRules_Actions 1

# Enable in Audit mode (testing)
Add-MpPreference -AttackSurfaceReductionRules_Ids $guid -AttackSurfaceReductionRules_Actions 2

# Remove ASR rule
Remove-MpPreference -AttackSurfaceReductionRules_Ids $guid
```

## Verify ASR Rules

```powershell
# List enabled ASR rules
Get-MpPreference | Select-Object -ExpandProperty AttackSurfaceReductionRules_Ids
Get-MpPreference | Select-Object -ExpandProperty AttackSurfaceReductionRules_Actions

# Check specific rule status
Get-MpPreference | ForEach-Object {
    [PSCustomObject]@{
        RuleId = $_.AttackSurfaceReductionRules_Ids
        Action = $_.AttackSurfaceReductionRules_Actions
    }
}
```
