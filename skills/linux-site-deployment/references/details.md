# Site Deployment — details

## Capability contract

Read/search access to repository and host is required. Building in staging may be authorised separately. Production file changes, web reloads, certificate issuance, DNS/cutover, or public exposure require explicit authority. Destructive cleanup waits until rollback retention expires.

## Degraded mode

Fallback when DNS, certificate issuance, external probing, or production authority is unavailable: stop at the narrowest validated stage and mark cutover gates `not assessed`. A successful local build is not a deployed site.

## Evidence produced

| Artefact | Acceptance condition |
|---|---|
| Deployment evidence | Includes revision/build output, config tests, release ownership/context, TLS and external checks, update registration, rollback target, and logs. |

## Quality standards

- Deployment should leave the site reachable, renewable, and maintainable.
- Nginx validation and repo-registration steps are mandatory.
- Final verification must prove both HTTP behavior and operational update path.

## Worked example

For an Astro site on AlmaLinux, build the pinned revision into a versioned release, label it `httpd_sys_content_t`, install a reviewed Nginx vhost, pass `nginx -t`, switch the release, issue/verify TLS after DNS is ready, test the external page and assets, and record rollback plus update registration.

Ask these questions first:

1. **Domain name?** (e.g. example.com)
2. **Site type?**
   - **A** — Astro/static (Nginx serves `/dist/` directly)
   - **B** — PHP app (Nginx → Apache port 8080)
   - **C** — Astro + PHP hybrid (static front + PHP backend)
3. **Repo URL?**
4. **Node.js API needed?** (separate systemd service)
