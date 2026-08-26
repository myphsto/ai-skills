# rsync Sync & Incremental Backup — details

## Capability contract

Source/destination inspection and dry-run are read-only. Transfer writes require destination authority; `--delete` requires explicit destructive approval tied to the reviewed preview. Remote access uses approved keys and verified host identity.

## Degraded mode

Without destination access, produce a dry-run command and verification plan. Without delete approval, omit `--delete`. Without checksum capacity, report metadata-based verification and label content integrity unassessed.

## Evidence produced

| Artefact | Acceptance |
|---|---|
| Transfer evidence | Contains itemised preview, approved deletion scope, transfer statistics, host verification, and post-run comparison. |

Capture the itemised dry-run, approved destructive scope, command with secrets omitted, transfer statistics, SSH identity verification, post-run comparison, and snapshot link target where used.

## Quality standards

- A trailing slash on the source means "contents of"; no slash means "the
  directory itself". Decide deliberately — this is the most common rsync bug.
- Preview `--delete` before running it. Deletion is unrecoverable.
- Throttle (`--bwlimit`) any transfer that shares a production link.

## Worked example

Mirror `/srv/data/` to an offsite `data/` path over SSH with a reviewed exclude file and bandwidth cap. Approve deletion only after inspecting itemised dry-run output, then require an empty second dry-run before declaring sync success.

- The exact rsync command run and the dry-run preview that justified it.
- Bytes transferred, files deleted (if any), and the verification result.
- The snapshot directory created, for incremental runs.
