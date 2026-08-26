# Linux Mail Server — details

## Capability contract

Diagnosis defaults to read-only. Mail configuration, queue mutation, DNS publication, certificate changes, service reloads, or sending external test mail require explicit authority. Never expose mailbox credentials, private keys, or message content beyond approved evidence.

## Degraded mode

Without host, DNS, or recipient access, assess only available layers and label the rest `not assessed`. A successful TCP connection is not a delivery or reputation pass.

## Evidence produced

| Artefact | Acceptance condition |
|---|---|
| Mail-operation evidence | Includes redacted config, queue samples, log timeline, SMTP transcript, DNS/authentication/TLS results, authorised headers, and rollback. |

## Quality standards

- Verify with real SMTP tests and queue inspection, not assumption.
- Keep authentication records and mail config aligned.
- Separate transport problems from reputation and policy problems.

## Worked example

For a growing Postfix queue to one provider, sample deferred queue IDs, correlate enhanced status codes and logs, verify DNS/TLS/authentication, correct the evidenced cause, reload only after config validation, retry a small sample, and record delivery before releasing the remainder.

This skill covers running and debugging mail on a Debian/Ubuntu or RHEL-family server:
Postfix (default), Exim (alternative), Dovecot for IMAP, and the three
pillars of email authentication — SPF, DKIM, DMARC.

It does **not** own:

- **Firewall rules for SMTP ports** — `linux-firewall-ssl`.
- **DNS records themselves** (MX, SPF, DKIM, DMARC live at the DNS host) —
  but this skill *validates* them.
- **Mail clients** — out of scope.

Informed by *Linux Network Administrator's Guide* (Sendmail/Exim chapters,
translated to Postfix) and modern email authentication practice.
