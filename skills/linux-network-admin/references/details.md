# Linux Network Administration — details

## Capability contract

Diagnosis defaults to read-only. Read/execute access is required for host inspection. Persistent address, route, VLAN, DNS, or time changes require explicit authority and a recovery path; firewall and remote-provider changes require separate scope.

## Degraded mode

Without host access, provide a layer-by-layer probe plan and qualify all conclusions. Without console or timed rollback, do not apply remote persistent changes that could sever access.

## Evidence produced

| Artefact | Acceptance condition |
|---|---|
| Network-change evidence | Includes before/after link, address, route, resolver state, targeted probes, config validation, rollback readiness, and end-to-end checks. |

## Quality standards

- Prefer observation before mutation.
- Treat persistent network changes as high-risk and validate them carefully.
- Distinguish local host issues from remote service issues.

## Worked example

For a remote AlmaLinux host that lost a static route after reboot, capture `ip` and `nmcli` state, identify the owning connection, prepare a timed rollback, add the persistent route, reactivate safely, then prove the route, destination port, and application response before cancelling rollback.
