# Sysctl Performance Tuning — details

## Capability contract

Reading sysctls and drop-ins is read-only. Live writes, drop-in edits, module loading, load generation, and rollback require explicit authority. Security sysctls are out of scope for this skill.

## Degraded mode

Without representative load testing, return candidate keys and an experiment design only. If a key/algorithm is unavailable, do not force it. If rollback cannot be observed, do not apply the change.

## Evidence produced

| Artefact | Acceptance |
|---|---|
| Tuning experiment evidence | Contains kernel/config provenance, before/after values, comparable load metrics, guardrails, and rollback result. |

Capture kernel, feature availability, config provenance, before/after keys, load-test parameters and metrics, errors, guardrails, and rollback result.

## Quality standards

- One owned drop-in file, high number prefix (e.g. `60-`/`99-`) so it wins.
- Set only keys you can justify against a measured bottleneck.
- Confirm BBR is available before selecting it (`tcp_available_congestion_control`).

## Worked example

After profiling shows a connection-accept queue bottleneck, record current `somaxconn`, application backlog, and saturation, test one bounded increase under the same load, then persist only if latency improves without memory or error regression.

- The drop-in file written and the keys it changed.
- Before/after values for each tuned key.
- The load-test result that justified (or reverted) the change.
