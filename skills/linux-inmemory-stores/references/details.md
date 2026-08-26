# Redis & Memcached (in-memory stores) — details

## Capability contract

Inspection requires read access to service state, sockets, and configuration. Installation, configuration edits, firewall changes, restarts, and secret placement require explicit host-mutation authority and least-privilege elevation. Never print authentication material.

## Degraded mode

Without host access, return a family-specific change plan and verification commands. Without workload measurements, do not invent a memory ceiling. If authentication or socket exposure cannot be checked, mark the service posture `not assessed`, never safe.

## Evidence produced

| Artefact | Acceptance |
|---|---|
| Store evidence pack | Contains redacted config, version, socket, authentication, memory/eviction, and recovery results; unavailable checks are marked. |

Capture redacted config excerpts, package/unit versions, socket output, authentication rejection, memory/eviction statistics, and recovery-test result. Unavailable checks remain `not assessed`.

## Quality standards

- Never expose Redis or Memcached to an untrusted network. Bind to localhost or a
  private interface, require authentication, and firewall the port.
- Set `maxmemory` explicitly on Redis caches — an unbounded Redis will consume all
  RAM and be OOM-killed.
- Keep the secret out of the world-readable config where possible; source the
  password from an external secrets manager or environment.
- Record unit, socket, ceiling, authentication result, and persistence result without exposing secrets.

## Worked example

A 2 GiB Redis cache with disposable keys and private application clients receives a measured `maxmemory` below host capacity and `allkeys-lru`; ACL authentication is configured before the private bind. Acceptance requires the expected private socket, rejected unauthenticated `PING`, authorised `INFO memory`, and a documented decision that persistence is disabled.
