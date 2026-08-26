# Service Management — details

## Capability contract

Diagnosis defaults to read-only. Read/execute access is required for systemd and journal inspection. Editing units/drop-ins, changing enablement/resource limits, or reloading/restarting a production unit requires explicit authority; masking, stopping critical units, or changing targets needs separate confirmation.

## Degraded mode

Without host execution, review supplied unit/config/logs and label runtime stability and application health `not assessed`. Without a service-specific validator, require a documented low-risk test and rollback before reload.

## Evidence produced

| Artefact | Acceptance condition |
|---|---|
| Service-management evidence | Includes unit identity/status, journal timeline, dependencies, config validation, before/after properties, action result, and application health. |

## Quality standards

- Status and logs come before restart loops.
- Prefer reloads when safe and supported.
- Verification must include both unit state and real service behavior.

## Worked example

When `httpd` enters a restart loop on AlmaLinux, capture status and first-failure journal entries, inspect overrides and config syntax, correct the evidenced error, reset the failed state only after validation, start once, then verify the HTTP endpoint and absence of renewed failures.
