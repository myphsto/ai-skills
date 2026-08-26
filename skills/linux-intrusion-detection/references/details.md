# Intrusion Detection — details

## Capability contract

Default investigation uses read/search access and is read-only. Bans, unbans, jail changes, package installation, quarantine, and `rkhunter --propupd` require explicit response authority. Never refresh a baseline merely to silence an unexplained finding.

## Degraded mode

If logs were rotated, tools are absent, or no trusted baseline exists, report available signals and missing coverage. Mark attribution and compromise status undetermined; a clean partial scan is not a clean host.

## Evidence produced

| Artefact | Acceptance |
|---|---|
| Detection evidence pack | Includes jail status, timestamped triggering logs, scanner output, package correlation, authorised diff/action, and post-change status |

## Quality standards

- Changes must improve signal without creating blind spots.
- Preserve evidence when investigating suspicious behavior.
- Keep monitoring rules understandable and reviewable.

## Worked example

When `/usr/bin/ssh` changes after an approved OpenSSH update, preserve the warning, match package timestamps and verification, and document the benign cause. Update properties only after approval; an unmatched hash blocks re-baselining.
