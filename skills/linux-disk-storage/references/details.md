# Disk & Storage — details

## Capability contract

Read/search diagnosis needs shell access to `df`, `du`, `findmnt`, and `lsblk`. Cleanup, partition, swap, mount, and `/etc/fstab` changes require explicit root-level change authority. Never reveal share credentials or infer deletion approval from disk pressure.

## Degraded mode

If root, package tools, network reachability, credentials, or a maintenance window is unavailable, report the observable usage and the exact unassessed operation. Provide safe commands for an operator; do not mark capacity, mount persistence, or boot safety as passed.

## Evidence produced

| Artefact | Acceptance |
|---|---|
| Storage evidence pack | Includes before/after `df`, inode and consumer evidence, filesystem type, authorised commands, applicable `mount -a`, and redacted residual risk |

## Quality standards

- Measurements identify the affected mount rather than only the directory path.
- Every deletion is bounded by path, age or retention rule, and explicit authority.
- Network mounts survive an unavailable peer without blocking boot.
- Verification proves reclaimed capacity or a correctly mounted target.

## Worked example

An alert shows `/var` at 96% while `/` is healthy. The operator supplies a 14-day journal policy. Measure `/var` separately, find 18 GiB in journald, vacuum only to the approved boundary, and record before/after `df` plus `journalctl --disk-usage`; do not delete application backups discovered on another mount.
