# Linux DNS Server — details

## Capability contract

Read-only inspection is the default for diagnosis. Editing zones/configuration, reloading DNS, changing delegation, opening firewall access, or enabling transfer/recursion requires explicit authority. Do not expose TSIG private material.

## Degraded mode

Without access to the authoritative host, validate supplied text where possible and mark live reload, delegation, propagation, and SELinux checks `not assessed`. Do not treat a local syntax pass as published DNS success.

## Evidence produced

| Artefact | Acceptance condition |
|---|---|
| DNS change evidence | Includes reviewed diff, validators, reload result, direct answers from each authority, SOA serial, transfer result where relevant, and rollback. |

## Quality standards

- Validate zone syntax before reload every time.
- Keep serial management explicit and predictable.
- Verify from the authoritative source, not only from cached resolvers.

## Worked example

To add `api.example.org A 192.0.2.40`, confirm the authoritative zone and serial policy, edit the managed source, validate configuration and zone, reload, query each authoritative server with recursion disabled, and record the returned address, TTL, and new SOA serial.
