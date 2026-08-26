# Web Stack Management — details

## Capability contract

Diagnosis defaults to read-only. Read/execute access is required to inspect config, services, ports, sockets, logs, and requests. Editing config, changing labels/booleans, or reloading/restarting production services requires explicit authority and rollback.

## Degraded mode

Without host or request access, produce a request-hop diagnosis tree and label live configuration, runtime, SELinux, and health checks `not assessed`. Do not infer health from static snippets alone.

## Evidence produced

| Artefact | Acceptance condition |
|---|---|
| Web-stack evidence | Includes config diff, services/listeners, config-test output, logs, relevant SELinux findings, reload status, and end-to-end request result. |

## Quality standards

- Validate configs before reload every time.
- Keep responsibility boundaries clear across Nginx, Apache, PHP-FPM, and Node.js.
- Verify with real request behavior, not just successful daemon restarts.

## Worked example

For a 502 on Rocky Linux, trace the Nginx upstream, confirm the backend listener, inspect `httpd`/PHP-FPM status and logs, check socket permissions and SELinux denials, correct the evidenced layer, pass daemon config tests, reload only that service, and verify the external request.

```
Client → Nginx (443/80)
           ├── Astro/static → /dist/ folders
           ├── PHP direct → PHP-FPM socket
           ├── PHP apps → Apache (port 8080)
           └── Node.js APIs → localhost:<port>
```
