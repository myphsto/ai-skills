# Container Deployment & Lifecycle — details

## Capability contract

Reading definitions, images, logs, and state is read-only. Pulling images, creating/replacing containers, changing volumes/networks, enabling units, or executing inside containers requires explicit deployment authority. Secret values must never be embedded in definitions or evidence.

## Degraded mode

Without engine access, validate the supplied definition statically and return unexecuted commands. Without health or rollback criteria, do not update production; label runtime, reboot, and SELinux checks `not assessed`.

## Evidence produced

| Artefact | Acceptance |
|---|---|
| Deployment evidence | Contains definition validation, image digest, health, ports/mounts, unit state, restart test, and redacted logs. |

Capture definition validation, image digest, inspected runtime state, health output, ports/mounts, unit status, restart/reboot test, and redacted logs.

## Quality standards

- Always set an explicit `--restart` policy; the default `no` is rarely right for a service.
- Validate compose files with `docker compose config` before `up`.
- Prefer Quadlet for Podman services on RHEL 9+; prefer compose-via-systemd-unit for Docker.

## Worked example

Deploy a pinned web image through Quadlet on RHEL, use `:Z` for its exclusive bind mount, define a health check and restart policy, then verify service health after a controlled restart. Roll back to the recorded digest if the health gate fails.

- The container/stack brought up and its verified running/health state.
- The persistence mechanism wired (systemd unit, generate systemd, or Quadlet).
- The restart policy chosen and why.
