# PowerShell 7.5 CI/CD Integration and Performance Benchmarks

## CI/CD Integration

```yaml
# GitHub Actions with PowerShell 7.5
- name: Setup PowerShell 7.5
  uses: actions/setup-powershell@v1
  with:
    pwsh-version: '7.5.x'

- name: Run Script with 7.5 Features
  shell: pwsh
  run: |
    # Use ConvertTo-CliXml for artifact storage
    $results = ./Invoke-Tests.ps1
    $results | ConvertTo-CliXml | Out-File "results.xml"

    # Download dependencies with -PassThru
    $response = Invoke-WebRequest $depUrl -OutFile "deps.zip" -PassThru
    Write-Host "Downloaded $($response.RawContentLength) bytes"
```

## Performance Benchmarks

Measured locally on the same machine (median timings; use for relative comparison, not absolutes — timings vary by hardware):

| Operation | 7.4.19 | 7.5.10 | 7.6.5 | Improvement |
|-----------|--------|--------|-------|-------------|
| `+=` 10K appends | 557–566 ms | 24–28 ms | 25–29 ms | ~20x faster; a **7.5** feature |
| Cold startup | ~0.20–0.21 s | ~0.19–0.23 s | ~0.21–0.22 s | flat — no real gain in 7.5 or 7.6 |
| Large pipeline (100K) | 300–310 ms | 264–271 ms | 309–320 ms | small 7.5 gain (~12%); 7.6 back to 7.4 level |
| Module loading (import) | 34–35 ms | 35–36 ms | 35–37 ms | negligible |

**Do not claim** startup, memory, or pipeline improvements in 7.6 — the measured data shows no such gains. Memory reductions are not substantiated by measured evidence here.

## .NET 9 /.NET 10 Notes

PowerShell 7.5 runs on .NET 9; PowerShell 7.6 runs on .NET 10 (verified `.NET 10.0.11` on 7.6.5). JIT/memory claims should be measured per workload; the timing table above is the safe reference.

```powershell
# Example: Large dataset processing (measured)
Measure-Command { $r = 1..100000 | ForEach-Object { $_ * 2 } }
# 7.4.19: ~300-310 ms
# 7.5.10: ~264-271 ms (small gain)
# 7.6.5:  ~309-320 ms (no gain over 7.4)

# The += optimization that matters most for aggregation loops landed in 7.5:
Measure-Command { $a = @(); foreach ($i in 1..10000) { $a += $i } }
# 7.4.19: ~560 ms   ->   7.5.10/7.6.5: ~25 ms  (~20x faster)
```
