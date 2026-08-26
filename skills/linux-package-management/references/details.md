# Linux Package Management — details

## Capability contract

Read access to OS and package state is required. Package mutation, repository trust changes, reboot, or service restart requires explicit authority. Never disable signature checks or accept an unknown key to make a transaction pass.

## Degraded mode

Without host execution, return family-correct inspection and transaction commands with versions unresolved and runtime checks marked `not assessed`. Without a maintenance window, stop before disruptive upgrades.

## Evidence produced

| Artefact | Acceptance condition |
|---|---|
| Package-operation evidence | Includes simulation/transaction output, installed and candidate versions, repository provenance, relevant update logs, and service checks. |

## Quality standards

- Prefer official repositories and explicit package intent.
- Keep upgrades observable and reversible where possible.
- Verify both package state and runtime health after updates.

## Worked example

For a held Nginx update on Ubuntu, inspect `apt-cache policy`, holds, changelog, and simulated transaction; schedule the approved update, validate Nginx configuration, apply it, confirm the installed version and HTTP health, and state whether a reboot remains required.
