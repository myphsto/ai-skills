# Archive Integrity (tar + verify) — details

## Capability contract

Listing sources and archives is read-only. Archive creation, overwrite, encryption, extraction, and deletion require explicit filesystem authority; restoring ownership, ACLs, or SELinux contexts requires separately authorised elevation. Never expose key material.

## Degraded mode

Without source access, return a command plan only. If ACL/xattr tools or keys are unavailable, do not claim metadata or authenticity verification; identify exactly which attributes remain unassessed.

## Evidence produced

| Artefact | Acceptance |
|---|---|
| Archive evidence | Contains create/list/compare results, checksum, size, metadata restoration checks, and signature status. |

Capture create/list/compare exit status, checksum, archive size, sampled ownership/ACL/xattr/SELinux restoration, signature verification, and every unassessed attribute.

## Quality standards

- An unverified archive is not a backup. Always list or compare after create.
- Use `--numeric-owner` for any archive that may restore to a different host.
- Prefer gzip for live/rotated backups (universal, fast); xz for cold archives.
- Keep the sha256 sidecar next to the archive and offsite alongside it.

## Worked example

Archive `/var/www` for cross-host restore with numeric owners, ACLs, xattrs, and SELinux attributes, create a SHA-256 sidecar, then extract into a temporary tree and compare both content and metadata before retention begins.

- The exact `tar` create command and the verification command(s) run.
- Archive path, compressed size, and sha256 digest.
- Any GPG signature/encryption produced and where its key lives.
