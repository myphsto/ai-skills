# Container Engine — Docker & Podman — details

## Capability contract

Inspection is read-only. Repository changes, package installation, daemon configuration, socket permissions, user/group changes, and restarts require explicit host-mutation authority. Treat Docker socket access and `docker` group membership as root-equivalent.

## Degraded mode

Without host access, provide family-qualified install and verification steps. If storage-driver, cgroup, SELinux, or rootless prerequisites cannot be checked, mark them `not assessed` and do not declare the engine ready.

## Evidence produced

| Artefact | Acceptance |
|---|---|
| Engine readiness evidence | Contains source/version, redacted config, engine info, socket ownership, namespace, storage/network, and unit results. |

Capture package/repository source, version, redacted config, engine info, socket ownership, user namespace status, storage/network checks, unit state, and rollback result if invoked.

## Quality standards

- Pin the storage driver (`overlay2`) and cap logs in `daemon.json` from day one.
- Treat `docker` group membership and `docker.sock` as root-equivalent; restrict both.
- Prefer rootless Podman on multi-tenant hosts; justify any root daemon in writing.

## Worked example

On a multi-tenant RHEL host, select rootless Podman, verify subordinate IDs and user lingering, allow only approved registries, then confirm an unprivileged test container starts after reboot. Do not substitute Docker merely because its CLI is familiar.

- The engine installed and its verified version / storage driver.
- The `daemon.json` / `registries.conf` applied and why each key is set.
- Any hardening (userns-remap, `no-new-privileges`, socket perms) and residual risk.
