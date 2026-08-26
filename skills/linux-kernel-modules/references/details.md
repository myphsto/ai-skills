# Kernel Module Management — details

## Capability contract

Module inspection is read-only. Load/unload, persistent config, blacklist, initramfs rebuild, and reboot require explicit authority. A remote boot-time storage or network change additionally requires working console/out-of-band recovery.

## Degraded mode

Without host/kernel access, provide inspection commands only. Without dependency, boot-role, or console evidence, refuse unload/blacklist and mark reboot safety unassessed.

## Evidence produced

| Artefact | Acceptance |
|---|---|
| Module change evidence | Contains kernel/module identity, dependencies, device mapping, initramfs result, log check, and reboot outcome. |

Capture `uname`, `modinfo`, `lsmod`, device-driver mapping, dependency/use state, persistent config, initramfs command/result, kernel log checks, and reboot outcome.

## Quality standards

- Always `modinfo` and `lsmod` before unloading or blacklisting.
- Persist intent in `/etc/modprobe.d/` or `/etc/modules-load.d/` rather than
  relying on one-off runtime `modprobe` commands.
- Treat any boot-time module change as a change that requires an initramfs
  rebuild and a tested reboot.

## Worked example

Before blacklisting a conflicting NIC driver, map the interface to its bound module, confirm an alternate driver and console access, test the change at runtime when safe, rebuild the correct initramfs, and verify networking after a controlled reboot.

- What was inspected, loaded, unloaded, or blacklisted, and where it was
  persisted.
- Whether an initramfs rebuild was required and which command was run.
- The verification performed (re-`lsmod`, `/sys/module/.../parameters/`,
  reboot test) and any remaining boot/connectivity risk.
