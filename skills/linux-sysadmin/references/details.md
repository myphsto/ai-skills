# Linux Server Admin Hub — details

Supplemental sections for the hub: capability contract, degraded mode,
evidence, quality standards, and a worked routing example.

## Capability contract

Routing requires read access to the request and skill catalogue. System
inspection is read-only by default. Editing, package changes, service reloads,
network changes, destructive actions, and production mutation are governed by
the selected specialist and require explicit authority.

## Degraded mode

If the server or catalogue cannot be inspected, return the top three plausible
skills with the missing fact that separates them. Do not issue family-specific
or mutating commands and do not treat unobserved system state as healthy.

## Evidence produced

| Category | Artefact | Acceptance condition |
|---|---|---|
| Routing | Route record | Selected skill, trigger evidence, neighbour distinction, and verification target are present. |

## Quality standards

- Route quickly and explicitly; do not leave the user in the hub longer than necessary.
- Confirm destructive work, validate configs before reload, and prefer idempotent changes.
- Detect the distro family (`/etc/os-release`) before selecting packages, paths, services, or firewall tooling.

## Worked example

"The website is returning 502 after a PHP upgrade" routes first to
`linux-webstack`, with `linux-service-management` and `linux-log-management` as
neighbours. The handoff records the distro family, affected virtual host,
recent package change, and a read-only first pass before any reload.
