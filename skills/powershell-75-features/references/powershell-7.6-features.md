# PowerShell 7.6 Features

PowerShell 7.6 is a stable GA release built on **.NET 10** (current 7.6.5, .NET 10.0.11). It shares almost all of the 7.5 engine and adds a small, verified set of new features. The `+=` array-append optimization often attributed to 7.6 actually landed in 7.5 (see below).

## Contents

- [+= Operator Optimization (7.5, not 7.6)](#-operator-optimization-landed-in-75-present-in-76)
- [Get-Clipboard -Delimiter (7.6)](#enhanced-get-clipboard)
- [Get-Command -ExcludeModule (7.6)](#enhanced-get-command)
- [PSResourceGet](#psresourceget)
- [DSC in PowerShell](#dsc-in-powershell)
- [.NET 10 Integration](#net-10-integration)
- [Experimental Features in 7.6.5](#experimental-features-in-765)
- [Breaking Changes in 7.6](#notable-behavior-and-breaking-changes-in-76)
- [Migration to PowerShell 7.6](#migration-to-powershell-76)
- [Measured Performance Comparison](#performance-comparison-74-vs-75-vs-76-measured)

## += Operator Optimization (Landed in 7.5, Present in 7.6)

The `+=` array-concatenation optimization was introduced in **PowerShell 7.5**, not 7.6. Verified timings for 10,000 appends (median, relative only):

| Runtime | `+=` 10K (ms) | List[int] 10K (ms) |
|---------|---------------|--------------------|
| 7.4.19  | 557–566       | 71–72              |
| 7.5.10  | 24–28         | 76–79              |
| 7.6.5   | 25–29         | 75–76              |

- In 7.5+ the same `foreach ($i in 1..10000) { $array += $i }` code runs about **20x faster** than 7.4 (no code changes required).
- The old guidance "use `List[T]` for speed" is no longer true for append-heavy loops: optimized `+=` is now ~3x **faster** than `List[T]` in 7.5/7.6.
- 7.6 adds nothing beyond 7.5 here; the numbers are flat.

## Enhanced Get-Clipboard

### -Delimiter Parameter (new in 7.6)

Specify custom delimiters when getting clipboard content (verified 7.6-only; absent in 7.4/7.5):

```powershell
# Get clipboard content split by custom delimiter
$items = Get-Clipboard -Delimiter ","
# Clipboard: "apple,banana,cherry"
# Result: @("apple", "banana", "cherry")

# Split by tabs (useful for Excel data)
$columns = Get-Clipboard -Delimiter "`t"
```

**Use Cases:**
- Parse copied data from spreadsheets
- Process comma-separated lists from clipboard
- Handle pipe-delimited values

## Enhanced Get-Command

### -ExcludeModule Parameter (new in 7.6)

Filter out commands from specific modules (verified 7.6-only; absent in 7.4/7.5):

```powershell
# Find all Get-* commands except from Az modules
Get-Command Get-* -ExcludeModule Az*

# Discover non-default commands
Get-Command -ExcludeModule Microsoft.PowerShell.*

# Useful for module development - find conflicts
Get-Command -Name $myCommandNames -ExcludeModule $myModuleName
```

**Use Cases:**
- Discover which module provides a command
- Find command conflicts across modules
- Development and debugging workflows

## PSResourceGet

PSResourceGet is the modern package-management module bundled with PowerShell 7.4+. It is a separately-versioned coordinated release that tracks the host version you are on (e.g. PowerShell 7.6.x ships PSResourceGet v1.2.0, 7.5.x ships v1.1.1, 7.4.x ships 1.0.x). Exact version varies by install, so always check with the command below — do not assume a specific number.

```powershell
# Check PSResourceGet version
Get-Module Microsoft.PowerShell.PSResourceGet -ListAvailable

# New-style commands replace the PowerShellGet equivalents
Install-PSResource -Name Az -Scope CurrentUser
Find-PSResource -Name "*Azure*"         # replaces Find-Module
Update-PSResource -Name Az              # replaces Update-Module
Get-InstalledPSResource                 # replaces Get-InstalledModule

# Azure Artifacts / private feed with a credential
$credential = Get-Credential   # or a PSCredential backed by Microsoft.PowerShell.SecretManagement
Install-PSResource -Name "MyModule" -Repository "PrivateFeed" -Credential $credential -Prerelease
```

## DSC in PowerShell

- PowerShell 7.x ships the **legacy** `PSDesiredStateConfiguration` module (v1.0) with `Get-DscResource`, `Test-DscResource`, and `Start-DscResource`. This is unchanged in 7.6.
- **DSC v3 is a separate, cross-platform project** (the `dsc` CLI, JSON/YAML configuration, no WMI/CIM dependency) and is **not bundled** with PowerShell 7.6. There is no `Enable-ExperimentalFeature` for it. See https://github.com/PowerShell/DSC and install it separately.
- The experimental features and "InvokeDscResource" naming from older preview claims do not exist in 7.6.5.

## .NET 10 Integration

PowerShell 7.6 runs on .NET 10 (verified: `.NET 10.0.11` on 7.6.5).

```powershell
# Check .NET version
[System.Runtime.InteropServices.RuntimeInformation]::FrameworkDescription
# .NET 10.0.11

# TimeProvider for testable time operations (worked in 7.5/.NET 9, still available)
$timeProvider = [System.TimeProvider]::System
$timeProvider.GetUtcNow()

# SearchValues for fast string searching (created, usable)
$chars = [System.Buffers.SearchValues[char]]::Create("aeiou")
$text = "Hello World"
$text.IndexOfAny($chars)   # 1 (position of 'e')
```

Note: measured performance shows **no startup or pipeline gains in 7.6 over 7.5** (see the performance table below). Treat any "faster startup / faster pipelines in 7.6" claim as unsubstantiated.

## Experimental Features in 7.6.5

Verified experimental features in a stock 7.6.5 install (all off by default):

```powershell
# List all experimental features
Get-ExperimentalFeature
# 7.6.5 ships exactly three:
# - PSLoadAssemblyFromNativeCode
# - PSProfileDSCResource
# - PSSerializeJSONLongEnumAsNumber
```

```powershell
# Enable an experimental feature (takes effect after restart)
Enable-ExperimentalFeature -Name PSSerializeJSONLongEnumAsNumber
# Restart PowerShell, then Get-ExperimentalFeature shows  Enabled: True
```

### Large-Enum JSON Serialization (PSSerializeJSONLongEnumAsNumber)

- **Default (feature off):** `ConvertTo-Json` serializes a `[long]`-backed enum as its **name string** (e.g. `"Huge"`).
- **With the feature enabled + restart:** it serializes the **numeric value** instead.
- This is opt-in only and therefore **not a default breaking change** in 7.6.

Native `~` tilde expansion for Windows native commands is **not** active by default in 7.6.5 (a `cmd /c "echo ~"` returns a literal `~`). Tilde expansion was an experimental feature (`PSNativeWindowsTildeExpansion`) on the 7.5 line; check `Get-ExperimentalFeature` on the target host rather than assuming it works.

## Notable Behavior and Breaking Changes in 7.6

Confirmed 7.6 GA breaking changes:
- `ThreadJob` module renamed to `Microsoft.PowerShell.ThreadJob`.
- `WildcardPattern.Escape` no longer escapes a lone backtick.
- `Join-Path -ChildPath` now accepts a `string[]` (can bind multiple child paths).
- A trailing space was removed from the event source name in event-log cmdlets.

Other behavior:
- UTF-8 (no BOM) remains the default encoding for the core cmdlets, continuing 7.x behavior.
- The long-enum-to-number serialization change is **not** a default breaking change — it is gated behind the `PSSerializeJSONLongEnumAsNumber` experimental feature (opt-in).

## Migration to PowerShell 7.6

### Version Check Script

```powershell
function Test-PowerShellVersion {
    $version = $PSVersionTable.PSVersion

    $info = @{
        Version = $version.ToString()
        Major = $version.Major
        Minor = $version.Minor
        IsPreview = $version.PreReleaseLabel -ne $null
        DotNetVersion = [System.Runtime.InteropServices.RuntimeInformation]::FrameworkDescription
    }

    # Feature availability
    $info.Has76Features = $version.Major -eq 7 -and $version.Minor -ge 6
    $info.Has75Features = $version.Major -eq 7 -and $version.Minor -ge 5
    $info.HasPlusEqualsOptimization = $version.Major -eq 7 -and $version.Minor -ge 5   # not 7.6!
    $info.HasGetClipboardDelimiter = $info.Has76Features
    $info.HasGetCommandExcludeModule = $info.Has76Features

    [PSCustomObject]$info
}

Test-PowerShellVersion
```

### Conditional Feature Usage

```powershell
# Use 7.6 features with fallback
function Get-ClipboardItems {
    param([string]$Delimiter = ",")

    $version = $PSVersionTable.PSVersion
    if ($version.Major -eq 7 -and $version.Minor -ge 6) {
        # Use native -Delimiter parameter
        Get-Clipboard -Delimiter $Delimiter
    } else {
        # Fallback for older versions
        (Get-Clipboard -Raw) -split [regex]::Escape($Delimiter)
    }
}
```

## Performance Comparison: 7.4 vs 7.5 vs 7.6 (measured)

| Operation | 7.4.19 | 7.5.10 | 7.6.5 | Notes |
|-----------|--------|--------|-------|-------|
| `+=` in loop (10K) | 557–566 ms | 24–28 ms | 25–29 ms | ~20x faster; a **7.5** feature |
| Cold startup | ~0.20–0.21 s | ~0.19–0.23 s | ~0.21–0.22 s | flat; 7.6 is NOT faster |
| Large pipeline (100K) | 300–310 ms | 264–271 ms | 309–320 ms | small 7.5 gain (~12%); 7.6 back to 7.4 level |
| Module loading (import) | 34–35 ms | 35–36 ms | 35–37 ms | negligible |

Memory-usage improvements are not substantiated by measured evidence; do not claim them.

## Resources

- [PowerShell 7.6 Release Notes](https://github.com/PowerShell/PowerShell/releases)
- [.NET 10 What's New](https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-10/overview)
- [PowerShell Team Blog](https://devblogs.microsoft.com/powershell)
- [DSC v3 Repository](https://github.com/PowerShell/DSC)