# System Monitoring — details

## Capability contract

Default mode is read-only using process, kernel, socket, filesystem, and backup status commands. Installing tools, changing priorities/limits, killing processes, tuning kernel values, or restarting services requires explicit authority and a specialist handoff.

## Degraded mode

If tools, privileges, historical baselines, or repeated samples are unavailable, report the instantaneous measurements and missing context. Do not classify a transient snapshot as sustained health or pressure.

## Evidence produced

| Artefact | Acceptance |
|---|---|
| Host-health snapshot | Includes host, role, timestamps, commands, units, and all core resource areas |
| Pressure diagnosis | Correlates repeated samples with impact and states confidence |
| Specialist handoff | Names the failure domain, reproducing evidence, and unassessed checks |

## Quality standards

- Start broad, then narrow based on evidence.
- Distinguish transient spikes from sustained pressure.
- End with a clear operational conclusion, not just raw command output.

## Worked example

Load average is 12 on an eight-core host, but CPU idle remains 70% and I/O wait is 25%. Repeated `vmstat`/`iostat` samples show blocked tasks on one volume, so route to linux-disk-storage instead of changing CPU limits.
