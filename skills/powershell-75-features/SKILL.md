---
name: powershell-75-features
description: "PowerShell 7.5/7.6 features and enhancements. PROACTIVELY activate for: (1) PowerShell 7.5 stable features, (2) PowerShell 7.6 preview features, (3) ConvertTo-CliXml/ConvertFrom-CliXml, (4) Test-Path -OlderThan/-NewerThan, (5) += operator optimization (8x-16x faster), (6) PSResourceGet 1.1.1/1.2.0, (7) Get-Clipboard -Delimiter, (8) Get-Command -ExcludeModule, (9) DSC v3 resources, (10) .NET 9/.NET 10 integration. Provides: Latest cmdlet usage, performance benchmarks, migration patterns."
license: MIT
compatibility: "PowerShell 7.5+ or 7.6-preview (Windows, Linux, macOS)"
metadata:
  author: myphsto
  version: "1.0"
---

# PowerShell 7.5/7.6 Features

## Version Overview

| Version | Status | .NET | Release |
|---------|--------|------|---------|
| **7.5.4** | Stable (LTS) | .NET 9.0.306 | October 2025 |
| **7.6.0-preview.6** | Preview | .NET 10.0.0 GA | December 2025 |

PowerShell 7.5 is the current stable LTS (Long-Term Support) release. PowerShell 7.6 is in preview with new features targeting GA in early 2026.

## 7.5 Features at a Glance

| Feature | What's new |
|---------|-----------|
| `ConvertTo-CliXml` / `ConvertFrom-CliXml` | In-memory XML serialization, no file I/O |
| `Test-Path -OlderThan` / `-NewerThan` | Filter paths by modification time |
| `Invoke-WebRequest` / `Invoke-RestMethod` `-PassThru` + `-OutFile` | Save to file AND return the response |
| `ConvertFrom-Json -IgnoreComments` / `-AllowTrailingCommas` | Parse relaxed JSON |
| `Resolve-Path` / `Convert-Path -Force` | Wildcards match hidden files |
| `New-FileCatalog` v2 default | SHA256-based catalogs |
| .NET 9 | ~28% faster pipelines, ~21% lower memory |
| PSResourceGet 1.1.1 | ~2x faster installs, Azure Artifacts, SecretManagement integration |

## Where to Read More

- **Full usage examples, performance data, 7.4 → 7.5 migration patterns, best practices:** [`references/ps75-features.md`](references/ps75-features.md)
- **CI/CD integration and .NET 9 benchmark details:** [`references/cicd-benchmarks.md`](references/cicd-benchmarks.md)
- **7.6 preview features (+= optimization, Get-Clipboard -Delimiter, Get-Command -ExcludeModule, PSResourceGet 1.2.0, DSC v3, PSForEach/PSWhere, .NET 10, experimental features, breaking changes):** [`references/powershell-7.6-preview.md`](references/powershell-7.6-preview.md)

## Known 7.5 Issues

### Out-GridView Search Broken

The search/filter box in `Out-GridView` is non-functional in 7.5.x. Use `Where-Object` or `Select-Object` for filtering:

```powershell
# Instead of: Get-Process | Out-GridView -Title "Select"
Get-Process | Where-Object CPU -gt 100 | Format-Table
```

## Resources

- [PowerShell 7.5 Release Notes](https://github.com/PowerShell/PowerShell/releases/tag/v7.5.4)
- [.NET 9 Performance](https://devblogs.microsoft.com/dotnet/performance-improvements-in-net-9)
- [PowerShell Team Blog](https://devblogs.microsoft.com/powershell)
