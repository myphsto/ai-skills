# Server Provisioning — details

## Capability contract

Read and execute access to the new host is required. User, SSH, firewall, package, boot, and service changes require explicit build authority. Destructive disk actions, DNS changes, public exposure, or production cutover require separate confirmation.

## Degraded mode

If console or second-session access is unavailable, do not harden SSH or remove the current access path. If reboot or external reachability cannot be tested, hand off a qualified partial build with those gates marked `not assessed`.

## Evidence produced

| Artefact | Acceptance condition |
|---|---|
| Provisioning evidence | Includes host facts, package/update result, tested administrator login, firewall and MAC state, services/ports, post-reboot checks, and exceptions. |

## Quality standards

- Provisioning should create a predictable baseline, not an improvised snowflake.
- Security and access validation are part of provisioning, not follow-up chores.
- Leave the server ready for repeatable operational workflows.

## Worked example

For a new Rocky Linux web host, create and test a `wheel` administrator from a second session, apply updates, retain SELinux enforcing, expose only SSH/HTTP/HTTPS through firewalld, install only the approved web role, reboot, and record live reachability plus service health before deployment.

Sets up a fresh server. Ask first:
1. **Hostname?**
2. **Timezone?** (default: Africa/Nairobi)
3. **Which stack?** (confirm: Nginx + Apache + PHP8.3 + MySQL + PostgreSQL + Redis)

Work through sections in order. Full commands: `references/provisioning-steps.md`
