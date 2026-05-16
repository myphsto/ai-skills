# Windows 11 Quick Reference

## Common Admin Tasks

| Task | Command |
|------|---------|
| System restore point | `Checkpoint-Computer -Description "desc"` |
| Restart Explorer | `Stop-Process -Name explorer -Force` |
| Flush DNS | `Clear-DnsClientCache` |
| Check disk | `chkdsk C: /f /r` (requires reboot) |
| Repair system files | `sfc /scannow` |
| Repair Windows image | `DISM /Online /Cleanup-Image /RestoreHealth` |
| Reset network stack | `netsh winsock reset && netsh int ip reset` |
| Clear Windows Store cache | `wsreset.exe` |
| Open device manager | `devmgmt.msc` |
| Open disk management | `diskmgmt.msc` |
| Open services | `services.msc` |
| Open firewall | `wf.msc` |
| Open event viewer | `eventvwr.msc` |
| Open task scheduler | `taskschd.msc` |
| Open registry editor | `regedit` |
| System properties | `sysdm.cpl` |
| Network connections | `ncpa.cpl` |
| Programs and features | `appwiz.cpl` |

## Registry Hive Reference

| Hive | Abbreviation | Scope |
|------|-------------|-------|
| HKEY_LOCAL_MACHINE | HKLM: | System-wide |
| HKEY_CURRENT_USER | HKCU: | Current user |
| HKEY_CLASSES_ROOT | HKCR: | File associations |
| HKEY_USERS | HKU: | All user profiles |

## Service Startup Types

- `Disabled` - Service cannot be started
- `Manual` - Service starts on demand
- `Automatic` - Service starts with system boot
- `AutomaticDelayedStart` - Service starts delayed after boot

## NEVER Disable These Services

- `wuauserv` (Windows Update)
- `WinDefend` (Windows Defender)
- `EventLog` (Windows Event Log)
- `RpcSs` (Remote Procedure Call)
- `LSM` (Local Session Manager)
- `Schedule` (Task Scheduler)
- `Winmgmt` (WMI)
- `CryptSvc` (Cryptographic Services)
- `BITS` (Background Intelligent Transfer)

## NEVER Remove These Apps

- `Microsoft.WindowsStore` (Store - needed for updates)
- `Microsoft.WindowsCalculator`
- `Microsoft.WindowsTerminal`
- `Microsoft.DesktopAppInstaller` (winget)
- `Microsoft.VCLibs` (Visual C++ runtime)
- `Microsoft.UI.Xaml` (UI framework)
- `Microsoft.NET` (runtime)
- `Microsoft.HEIFImageExtension` / `Microsoft.WebpImageExtension` (image codecs)
