---
name: linux-archive-integrity
description: "Use when creating, signing, encrypting, listing, comparing, or restoring metadata-preserving tar archives on Debian/Ubuntu or RHEL-family hosts. Covers ACLs, xattrs, incrementals, and verification; use linux-rsync-sync for file-tree mirrors."
license: MIT
compatibility: "Linux (Debian/Ubuntu or RHEL family); root for most operations"
metadata:
  author: myphsto
  version: "1.0"
  source: "https://github.com/peterbamuhigire/linux-skills"
---

# Archive Integrity (tar + verify)

## Distro support

`tar`, `gzip`, `xz`, `sha256sum`, and `gpg` are identical on both families.
The only real differences are SELinux contexts (RHEL labels files; capture them
with `--xattrs --selinux`) and that ACL/xattr support needs the `acl`/`attr`
packages present. Body uses Debian/Ubuntu; the **RHEL family** (Fedora, RHEL,
CentOS Stream, Rocky, Alma, Oracle) notes are in the matrix.

| Concept | Debian/Ubuntu | RHEL family |
|---|---|---|
| Install tar/xz | preinstalled; `apt install xz-utils` | preinstalled; `dnf install xz` |
| ACL / xattr tooling | `apt install acl attr` | `dnf install acl attr` |
| `--acls --xattrs --numeric-owner` | identical | identical |
| `--listed-incremental` (level 0/1) | identical | identical |
| SELinux context capture | n/a (not labelled) | add `--selinux` (stored as an xattr) and/or `restorecon -R` on restore |
| GPG signing/encryption | `apt install gnupg` | `dnf install gnupg2` |

**RHEL-family gotcha:** with SELinux enforcing, an archive restored to a new
path can land with the wrong context. Either capture contexts with
`tar --xattrs --selinux` (they ride along as `security.selinux` xattrs) or run
`restorecon -R <path>` after extraction. `--numeric-owner` is essential when
restoring onto a host whose UID/GID-to-name mapping differs from the source.

## Use when

- Creating a sealed, portable archive of a directory tree with permissions,
  ownership, ACLs, and xattrs intact.
- Verifying that an archive is intact and restorable *before* you rely on it.
- Running level-0 / level-1 incremental tar backups with a snapshot file.
- Producing a sha256 sidecar or GPG-signed archive for tamper-evidence.

## Do not use when

- You want an efficient mirror or hard-linked snapshot tree; use
  [`../linux-rsync-sync/SKILL.md`](../linux-rsync-sync/SKILL.md).
- You need a crash-consistent image of a live database volume; use
  [`../linux-filesystem-snapshots/SKILL.md`](../linux-filesystem-snapshots/SKILL.md).
- You are restoring an existing encrypted backup in an incident; use
  [`../linux-disaster-recovery/SKILL.md`](../linux-disaster-recovery/SKILL.md).

## Required inputs

| Artefact | Required? | Source | If absent |
|---|---|---|---|
| Source tree, destination, restore platform, and retention | yes | Data owner and recovery plan | Stop before archive creation. |
| Required ACL/xattr/SELinux/ownership fidelity | yes | Restore requirements | Use full metadata flags and flag portability uncertainty. |
| Compression, signing, encryption, and key source | conditional | Storage/security policy | Default to gzip and checksum only; do not invent key handling. |

- The directory tree to archive and the archive destination path.
- The compression choice (gzip for universal/fast, xz for best ratio).
- Whether metadata fidelity (ACLs, xattrs, SELinux, numeric owner) is required.
- Whether a sha256 sidecar and/or GPG signature is required.

## Decision rules

| Choice | Action | Failure or risk avoided |
|---|---|---|
| gzip or xz | Use gzip for frequent/recovery-sensitive copies and xz for CPU-tolerant cold storage. | Excessive restore delay or waste. |
| Metadata flags | Preserve numeric owners, ACLs, xattrs, and SELinux contexts when cross-host fidelity matters. | Incorrect access after restore. |
| Incremental chain | Protect and retain the snapshot file with every dependent archive. | Unrestorable incremental series. |
| Signature/encryption | Sign for origin integrity; encrypt for confidentiality; manage keys separately. | Confusing checksum, authenticity, and secrecy. |

## Workflow

1. Create the archive with the metadata flags the restore target needs.
2. Verify immediately: list it (`tar -tvf`) and ideally `--compare` it against
   the source tree.
3. Write a `.sha256` sidecar; optionally sign/encrypt with GPG.
4. Record the archive path, size, and verification result.

5. Stop retention or deletion of the source when listing, checksum, signature, or isolated restore fails; recover by rebuilding the archive from the unchanged source and rerun every failed check.

## Outputs

| Artefact | Consumer | Acceptance condition |
|---|---|---|
| Archive and manifest | Recovery operator | Paths, flags, size, checksum, retention, and required metadata are recorded. |
| Verification report | Data owner | Archive lists cleanly, checksum passes, and isolated content/metadata comparison meets scope. |
| Crypto evidence | Security owner | Signature verifies or encryption/decryption test passes without exposing keys. |

## Anti-patterns

- Trusting archive creation alone. Fix: list, checksum, and restore-test it.
- Dropping metadata silently. Fix: declare and verify ownership, ACL, xattr, and SELinux requirements.
- Extracting over production first. Fix: restore into isolation and compare content/metadata.
- Losing incremental snapshot metadata. Fix: version and retain it with every dependent archive.
- Confusing checksum with authenticity. Fix: use a verified signature when origin proof is required.
- Creating an archive and never test-listing it.
- Dropping ACLs/xattrs/SELinux silently on metadata-sensitive trees.
- Treating `tar` exit 0 as proof of integrity without a `--compare` or checksum.
- Storing the GPG/sha256 verifier in the same blob it is meant to verify.
- Extracting over production as the first restore test. Correction: restore into isolation and compare metadata/content.
- Losing a listed-incremental snapshot file. Correction: version and retain it with the archive chain.

## Create A Compressed Archive

```bash
# gzip (.tar.gz) — universal, fast, good default for rotated backups
tar -czf /backups/www-$(date +%F).tar.gz -C /var www

# xz (.tar.xz) — best ratio, slow CPU; use for cold/archival copies
tar -cJf /backups/www-$(date +%F).tar.xz -C /var www

# -C changes directory first so the archive holds 'www/...' not '/var/www/...'
```

Grounded in RHCSA: `tar -cvf archive.tar /files`, `-z` for gzip, `-j` for
bzip2, `-J` for xz; `-C /targetdir` controls the path stored/extracted (Sander
van Vugt, RHCSA 8 Cert Guide).

Compression trade-offs:

| Tool | CPU | Ratio | When |
|---|---|---|---|
| `gzip` (`-z`, `.gz`) | fast | medium | Default. Every Unix reads it. |
| `xz` (`-J`, `.xz`) | slow | best | Cold archives, disk-bound hosts. |
| `bzip2` (`-j`, `.bz2`) | medium | medium | Legacy; rarely the best choice now. |
| `zstd` (`--zstd`, `.zst`) | fast | very good | Modern; needs `zstd` package. |

---

## Preserve Permissions / Ownership / ACLs / xattrs

```bash
# Full-fidelity archive: numeric UID/GID, POSIX ACLs, extended attributes.
sudo tar --acls --xattrs --numeric-owner -czf /backups/etc-$(date +%F).tar.gz \
         -C / etc

# On RHEL with SELinux, also capture the security context xattr:
sudo tar --acls --xattrs --selinux --numeric-owner \
         -czf /backups/www-$(date +%F).tar.gz -C /var www
```

- `--numeric-owner` — store UID/GID numbers, not names. Essential for restoring
  onto a host with a different `/etc/passwd` mapping.
- `--acls` — preserve POSIX ACLs (`getfacl`/`setfacl` entries).
- `--xattrs` — preserve extended attributes (capabilities, `security.*`).
- Extract with the same flags (`tar --acls --xattrs -xzf ...`) or the metadata
  is dropped on restore.

---

## Listed-Incremental (level-0 / level-1) Backups

`--listed-incremental=SNAP` records file state in a snapshot file. The first run
(snapshot file absent/empty) is a **full level-0**; subsequent runs capture only
what changed since — a **level-1 incremental**.

```bash
SNAP=/backups/www.snar

# Level 0 (full) — fresh snapshot file
sudo tar --listed-incremental="$SNAP" -czf /backups/www-L0.tar.gz -C /var www

# Level 1 (incremental) — same snapshot file, now populated
sudo tar --listed-incremental="$SNAP" -czf /backups/www-L1-$(date +%F).tar.gz -C /var www
```

Restore by extracting level-0 first, then each incremental **in order** (use
`--incremental` on extract so deletions are replayed). Keep the `.snar` snapshot
file with the backup set — without it you cannot continue the chain.

Full incremental chain and restore order:
[`references/incremental-and-verify.md`](references/incremental-and-verify.md).

---

## Verify The Archive

```bash
# 1. List contents (cheap sanity check; -v shows perms/owner/size)
tar -tvf /backups/www-$(date +%F).tar.gz | head

# 2. Compare archive against the live tree — flags any file that differs
sudo tar --acls --xattrs --compare -f /backups/www-$(date +%F).tar.gz -C /var
#                                  ^ --compare / -d : diff archive vs filesystem

# 3. sha256 sidecar — tamper-evidence and corruption detection
sha256sum /backups/www-$(date +%F).tar.gz > /backups/www-$(date +%F).tar.gz.sha256
sha256sum -c /backups/www-$(date +%F).tar.gz.sha256   # verify later
```

`tar -tvf` succeeding proves the archive is *readable and complete*; a clean
`--compare` proves it *matches the source*; the `.sha256` proves it has *not
changed on disk* since creation. A real backup uses all three.

Grounded in RHCSA: `tar -tvf` lists archive contents before extraction (Sander
van Vugt, RHCSA 8 Cert Guide).

---

## Optional GPG Signing / Encryption

```bash
# Detached signature (tamper-evidence; recipients verify with your public key)
gpg --detach-sign --armor /backups/www-$(date +%F).tar.gz
gpg --verify /backups/www-$(date +%F).tar.gz.asc /backups/www-$(date +%F).tar.gz

# Symmetric encryption for an offsite copy (AES256, passphrase from a 0600 file)
gpg --batch --symmetric --cipher-algo AES256 \
    --passphrase-file ~/.backup-encryption-key \
    -o /backups/www-$(date +%F).tar.gz.gpg /backups/www-$(date +%F).tar.gz
```

Key hygiene (store the key off the server, never in the backup it unlocks) is
covered in
[`../linux-disaster-recovery/references/backup-strategy.md`](../linux-disaster-recovery/references/backup-strategy.md).

[GROUNDING-GAP: Modern dedup/snapshot backup tools — borg and restic — supersede
hand-rolled tar incrementals for many use cases (dedup, encryption, prune
policies). Not covered here; from upstream borg/restic docs; deepen with UNIX &
Linux System Administration Handbook.]

Full tar flag reference: [`references/tar-reference.md`](references/tar-reference.md).

---

## References

- [`references/tar-reference.md`](references/tar-reference.md)
- [`references/incremental-and-verify.md`](references/incremental-and-verify.md)
- [`references/details.md`](references/details.md)
