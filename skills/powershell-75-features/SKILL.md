---
name: powershell-75-features
description: "PowerShell 7.5/7.6 features and enhancements. PROACTIVELY activate for: (1) PowerShell 7.5 stable features, (2) PowerShell 7.6 features, (3) ConvertTo-CliXml/ConvertFrom-CliXml, (4) Test-Path -OlderThan/-NewerThan, (5) += operator optimization (7.5 feature, ~20x vs 7.4), (6) PSResourceGet, (7) Get-Clipboard -Delimiter, (8) Get-Command -ExcludeModule, (9) DSC / DscResource, (10) .NET 9/.NET 10 integration. Provides: Latest cmdlet usage, performance benchmarks, migration patterns."
license: MIT
compatibility: "PowerShell 7.5+ / 7.6 (Windows, Linux, macOS)"
metadata:
  author: myphsto
  version: "1.0"
---

# PowerShell 7.5/7.6 Features

## Version Overview

| Version | Status | .NET | Release |
|---------|--------|------|---------|
| **7.6.5** | Stable, current GA (LTS) | .NET 10.0.11 | Aug 2026 |
| **7.5.10** | Stable (standard, non-LTS) | .NET 9 | 2025 |
| **7.4.19** | Stable (prior LTS) | .NET 8 | 2025 |

PowerShell 7.6 is the current GA release and is LTS (7.6.5, built on .NET 10). 7.5.10 (built on .NET 9) is a standard non-LTS release; 7.4.19 (built on .NET 8) is the prior LTS line.

## 7.5 Features at a Glance

| Feature | What's new |
|---------|-----------|
| `ConvertTo-CliXml` / `ConvertFrom-CliXml` | In-memory XML serialization, no file I/O (new in 7.5) |
| `Test-Path -OlderThan` / `-NewerThan` | Filter paths by modification time (present since Windows PowerShell 3.0; not new in 7.5) |
| `Invoke-WebRequest` / `Invoke-RestMethod` `-PassThru` + `-OutFile` | Save to file AND return the response (not new in 7.5) |
| `ConvertFrom-Json -DateKind` / `Test-Json -Options` | Date parsing control; relaxed JSON via `-Options IgnoreComments` / `-Options AllowTrailingCommas` |
| `Resolve-Path` / `Convert-Path -Force` | Wildcards match hidden files (new in 7.5) |
| `New-FileCatalog -CatalogVersion 2` | SHA256-based catalogs (no `-Force` param) |
| .NET 9 | ~12% faster 100K pipelines (measured); startup and module-load unchanged |
| PSResourceGet | Bundled with PowerShell 7.4+; Azure Artifacts + SecretManagement credential support |

## Where to Read More

- **Full usage examples, performance data, 7.4 → 7.5 migration patterns, best practices:** [`references/ps75-features.md`](references/ps75-features.md)
- **CI/CD integration and .NET 9 benchmark details:** [`references/cicd-benchmarks.md`](references/cicd-benchmarks.md)
- **7.6 features (Get-Clipboard -Delimiter, Get-Command -ExcludeModule, PSResourceGet, .NET 10, experimental features, breaking changes):** [`references/powershell-7.6-features.md`](references/powershell-7.6-features.md)

## Known 7.5 Issues

### Out-GridView Search Broken

The search/filter box in `Out-GridView` is non-functional in 7.5.x. Use `Where-Object` or `Select-Object` for filtering:

```powershell
# Instead of: Get-Process | Out-GridView -Title "Select"
Get-Process | Where-Object CPU -gt 100 | Format-Table
```

## Resources

- [PowerShell 7.5 Release Notes](https://github.com/PowerShell/PowerShell/releases/tag/v7.5.10)
- [.NET 9 Performance](https://devblogs.microsoft.com/dotnet/performance-improvements-in-net-9)
- [PowerShell Team Blog](https://devblogs.microsoft.com/powershell)
