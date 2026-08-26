# Linux cloud-init — details

## Capability contract

Read access to the source configuration is required. Execution on a disposable target is preferred. Editing, image publication, or production rebuilds require explicit authority; never place private keys or plaintext secrets in evidence.

## Degraded mode

If no parser or disposable instance is available, perform a read-only structural review, label runtime checks `not assessed`, and return the exact commands the operator must run. An unbooted configuration is not validated.

## Evidence produced

| Artefact | Acceptance condition |
|---|---|
| Provisioning validation evidence | Contains parser output, test-instance `cloud-init status --long`, relevant log excerpts, and checks for every declared outcome. |

## Quality standards

- Keep configurations reproducible, explicit, and safe for unattended execution.
- Validate before rollout, especially for multi-server deployments.
- Treat logs and instance state as the source of truth when debugging.

## Worked example

For a Rocky Linux image that must create an administrator and install Nginx, select cloud-config, use the `wheel` group and RHEL package names, validate the YAML, boot one disposable VM, then record the created user, key-only login, package version, and service state before scaling out.
