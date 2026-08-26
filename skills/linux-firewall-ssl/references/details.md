# Firewall & SSL Management — details

## Capability contract

Read/search inspection may be read-only. Firewall mutation, package installation, certificate issuance, web-server edits, and reloads require explicit change authority and root access. Preserve an independent management session before default-deny or SSH rule changes.

## Degraded mode

Without DNS, network, root, Certbot, or a second management session, report verified local state and label public reachability, issuance, renewal, or lockout safety `not assessed`. Never interpret an unavailable probe as success.

## Evidence produced

| Artefact | Acceptance |
|---|---|
| Firewall/TLS evidence pack | Includes before/after rules, listeners, config test, Certbot inventory/dry run, external probe result, and redactions |

## Quality standards

- Rules expose only named services to approved sources or zones.
- Management access remains independently verified during policy changes.
- Certificate identity, chain, expiry, and automated renewal are checked.
- Failed external checks remain failures or unassessed, never passes.

## Worked example

A Rocky host must expose HTTPS publicly and SSH only from `198.51.100.0/24`. Confirm `public` is the interface zone, preserve a second SSH session, add `https` and the source-limited SSH rule permanently, reload, then verify both runtime and permanent rules before running `certbot renew --dry-run`.
