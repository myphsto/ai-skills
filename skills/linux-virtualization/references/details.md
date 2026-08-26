# Linux Virtualization — details

## Capability contract

Inspection defaults to read-only. Read/execute access to the host is required. Start/stop, snapshot, backup, resize, migration, XML/profile edits, storage/network changes, or deletion require explicit authority. Deletion and overwrite require named target verification and a recoverable backup.

## Degraded mode

Without host or guest access, review supplied definitions/logs and mark capacity, storage consistency, runtime, and workload health `not assessed`. Without a verified backup or recovery path, stop before destructive or irreversible work.

## Evidence produced

| Artefact | Acceptance condition |
|---|---|
| Virtualisation evidence | Includes target definition, host capacity, attachments, state/logs, backup or snapshot identity/location, lifecycle result, and workload health. |

## Quality standards

- Keep host and guest responsibilities distinct.
- Snapshot or back up before risky mutations when possible.
- Validate both orchestration state and actual workload health.

## Worked example

Before changing a production libvirt VM, identify its disks and networks, check host capacity, create an application-consistent backup to independent storage, record restore steps, take a short-lived snapshot, apply the approved change, verify guest and application health, then remove the snapshot only after the retention gate.
