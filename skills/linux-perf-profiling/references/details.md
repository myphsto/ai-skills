# Linux Performance Profiling — details

## Capability contract

Default to read-only diagnosis and search of available metrics. Process/host sampling must be bounded. Package installation, lowering `perf_event_paranoid`, workload generation, tuning, restarts, and configuration changes require explicit permission; this skill does not tune.

## Degraded mode

When `perf`, sysstat history, kernel symbols, or target access is unavailable, use the narrowest available USE evidence and label missing dimensions `not assessed`. Never convert one instantaneous sample into a pass or root-cause claim.

## Evidence produced

| Artefact | Acceptance |
|---|---|
| Profiling evidence pack | Contains bounded samples, scope/workload, history, errors, available stacks, and an explicit confidence statement. |

Capture timestamped bounded samples, tool versions, workload context, historical comparison, perf command/overhead, top stacks where available, errors, and an explicit inconclusive result when evidence does not isolate a bottleneck.

## Quality standards

- Sample over a window (`vmstat 1`, several lines) — never trust one instant.
- Ignore the first `iostat`/`mpstat` line: it is averages since boot, not now.
- Pair every claim with the field that proves it (e.g. "disk-bound: `%util` 98,
  `await` 40 ms").

## Worked example

For a latency spike, record request load, sample `vmstat`, ignore the first `iostat` line, correlate high device `await` with per-process I/O and kernel errors, then hand storage evidence to the owning team. High load alone is insufficient.

- The classified bottleneck (CPU / I/O-wait / memory) and the metrics proving it.
- For CPU cases, the top symbols/stacks from `perf report`.
- A concrete next step (which tuning skill, which subsystem).
