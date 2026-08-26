---
name: linux-log-management
description: "Use when inspecting time-bounded journald or service logs, correlating web/database/security events, or managing logrotate retention; use linux-troubleshooting for multi-subsystem incidents."
license: MIT
compatibility: "Linux (Debian/Ubuntu or RHEL family); root for most operations"
metadata:
  author: myphsto
  version: "1.0"
  source: "https://github.com/peterbamuhigire/linux-skills"
---

# Log Management

## Distro support

`journalctl` and the systemd journal are **identical** on both families. The
differences are the legacy `/var/log/*` text-file names and the package
manager. The body uses Debian/Ubuntu paths; the **RHEL family** (Fedora, RHEL,
CentOS Stream, Rocky, Alma, Oracle) equivalents are in the matrix.

| Log / concept | Debian/Ubuntu | RHEL family |
|---|---|---|
| System log (legacy) | `/var/log/syslog` | `/var/log/messages` |
| Auth / sudo / SSH | `/var/log/auth.log` | `/var/log/secure` |
| Mail | `/var/log/mail.log` | `/var/log/maillog` |
| Web (Apache) | `/var/log/apache2/` | `/var/log/httpd/` |
| Cron | `/var/log/syslog` (CRON tag) | `/var/log/cron` |
| systemd journal | `journalctl …` | identical |
| logrotate configs | `/etc/logrotate.d/` | same |
| Package install | `apt install <pkg>` | `dnf install <pkg>` |

**RHEL-family note:** minimal RHEL/Fedora installs may not ship `rsyslog`, so
the legacy `/var/log/*` files may be absent — the journal (`journalctl`) is the
primary source. `journalctl -u <unit>`, `-p err`, `--since` all work the same.

## Use when

- Reading service, web, security, or database logs on a Linux server.
- Investigating spikes in errors, attacks, or slow queries.
- Reviewing log rotation or journal storage behavior.

## Do not use when

- The task is general incident routing without a clear symptom; use `linux-troubleshooting`.
- The task is metrics collection or centralized observability setup — outside this skill set.

## Required inputs

| Artefact | Source | Required? | If absent |
|---|---|---|---|
| Service/path and time window | Incident owner or alert | yes | Stop broad collection and request a bounded target |
| Symptom or event signature | Operator or monitoring evidence | yes | Return an inventory only; do not infer cause |
| Retention and privacy rules | Service owner or policy | for rotation/export | Do not delete, rotate early, or share sensitive records |

## Decision rules

| Condition | Action | Failure avoided |
|---|---|---|
| Event spans multiple services | Correlate timestamps and request IDs | Single-log attribution error |
| Log growth threatens disk | Preserve incident window, then apply authorised retention | Destroyed evidence |
| Sensitive fields appear | Redact values while retaining timestamp/context | Credential or personal-data exposure |
| Timestamp sources differ | Record timezone/clock offset | False sequence of events |

## Workflow

1. Confirm service, host, timezone, time window, retention, and read/search boundary.
2. Preserve a bounded evidence slice before changing rotation or services.
3. Correlate events across the minimum relevant sources and separate facts from inference.
4. Route the cause to the owning service; stop when evidence cannot distinguish candidates.
5. Apply only authorised rotation/retention changes and validate syntax.
6. On failure, recover the prior logrotate configuration and retain collected evidence.

## Outputs

| Artefact | Consumer | Acceptance condition |
|---|---|---|
| Log finding | Incident owner | States evidence, time coverage, cause/confidence, and gaps |
| Rotation change record | Operations | Shows authorised diff, validation, rollback, and result |
| Specialist handoff | Owning team | Includes the minimum reproducing records without secrets |

## Anti-patterns

- Grepping random logs. Fix: identify service, host, timezone, and timeframe first.
- Treating volume as proof of cause. Fix: correlate content with service behaviour.
- Changing rotation before understanding growth. Fix: measure source and preserve the incident window.
- Publishing raw secrets or tokens. Fix: redact values and retain only useful context.
- Treating rotated logs as proof nothing happened. Fix: mark the missing period unassessed.
- Mixing local and UTC timestamps silently. Fix: normalise or label timezone offsets.

## journalctl

```bash
sudo journalctl -u <service> -n 50 --no-pager       # last 50 lines
sudo journalctl -u <service> -f                      # follow live
sudo journalctl -u <service> --since "1 hour ago"
sudo journalctl -p err --since "today" --no-pager    # errors only
sudo journalctl -k --since "today" | grep -i oom     # kernel OOM events
sudo journalctl --disk-usage                         # journal size
```

---

## Nginx Logs

```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# HTTP status code distribution:
sudo awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -rn

# Top IPs by request count:
sudo awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -20

# Recent 5xx errors:
sudo grep '" 5' /var/log/nginx/access.log | tail -20
```

---

## Attack Pattern Detection

```bash
# Login brute-force attempts:
sudo grep -E "POST.*(login|wp-login|admin|xmlrpc)" /var/log/nginx/access.log | \
    awk '{print $1}' | sort | uniq -c | sort -rn | head

# Scanner activity (high 404 rate per IP):
sudo awk '$9 == 404 {print $1}' /var/log/nginx/access.log | \
    sort | uniq -c | sort -rn | head

# Attempts to access sensitive files:
sudo grep -E "\.(env|git|htaccess|sql|bak)" /var/log/nginx/access.log | tail -20
```

---

## fail2ban Log

```bash
sudo tail -f /var/log/fail2ban.log
sudo grep "Ban" /var/log/fail2ban.log | tail -20
sudo grep "$(date '+%Y-%m-%d')" /var/log/fail2ban.log | grep "Ban" | wc -l
```

---

## Other Key Logs

```bash
# PHP errors:
sudo tail -f /var/log/php8.3-fpm.log

# MySQL slow queries:
sudo tail -20 /var/log/mysql/mysql-slow.log 2>/dev/null
mysql -e "SHOW VARIABLES LIKE 'slow_query_log%';" 2>/dev/null

# Apache (port 8080 backend):
sudo tail -f /var/log/apache2/error.log

# Backup cron:
tail -50 ~/backups/mysql/cron.log
```

---

## logrotate

```bash
ls /etc/logrotate.d/                             # existing configs
sudo logrotate -f /etc/logrotate.d/nginx         # force rotate now
sudo logrotate -f /etc/logrotate.d/apache2
```

All log file locations: `references/log-locations.md`

---

## References

- `../../docs/continuous-improvement/incident-learning-standard.md`
- [`references/journalctl-reference.md`](references/journalctl-reference.md)
- [`references/log-analysis-patterns.md`](references/log-analysis-patterns.md)
- [`references/log-locations.md`](references/log-locations.md)
- [`references/details.md`](references/details.md)
