---
name: powershell-security
description: "Modern PowerShell security practices: SecretManagement, credential protection, JEA, WDAC, code signing, ConstrainedLanguage mode, audit logging, AMSI, AppLocker, and supply-chain security. Use when hardening PowerShell scripts or automation, storing credentials, configuring JEA endpoints or WDAC policies, signing modules or scripts, or setting up PowerShell audit logging. Provides setup, configuration, and policy templates."
license: MIT
compatibility: "Windows for WDAC/JEA/AppLocker/Script Block logging; SecretManagement and module signing are cross-platform"
metadata:
  author: myphsto
  version: "1.0"
---

# PowerShell Security Best Practices (2025)

Modern security practices for PowerShell scripts and automation: credential management, secret storage, least-privilege remoting, script control, and audit logging.

## Domain Reference Files

Read the file(s) matching the task — do not load all of them.

| Topic | Reference file | Covers |
|-------|---------------|--------|
| SecretManagement & credentials | [`references/secret-management.md`](references/secret-management.md) | Module install, vault registration, set/get secrets, no-hardcode rules, Managed Identity |
| JEA | [`references/jea.md`](references/jea.md) | Role capabilities, session configurations, JEA audit logging |
| WDAC & code signing | [`references/wdac-signing.md`](references/wdac-signing.md) | WDAC policy creation, Authenticode signing/verification, execution policy |
| Logging & validation | [`references/logging-validation.md`](references/logging-validation.md) | ConstrainedLanguage mode, Script Block logging, log review, input validation |
| Azure Key Vault | [`references/azure-keyvault-serviceprincipal.md`](references/azure-keyvault-serviceprincipal.md) | AKV setup, Service Principal auth, full automation script template |

## Security Checklist

### Script Development

- [ ] Never hardcode credentials (use SecretManagement)
- [ ] Use parameterized queries for SQL operations
- [ ] Validate all user input with `[ValidatePattern]`, `[ValidateSet]`, etc.
- [ ] Enable `Set-StrictMode -Version Latest`
- [ ] Use `try/catch` for error handling
- [ ] Avoid `Invoke-Expression` with user input
- [ ] Sign production scripts
- [ ] Enable Script Block Logging

### Automation

- [ ] Use Managed Identity or Service Principal (never passwords)
- [ ] Store secrets in SecretManagement or Azure Key Vault
- [ ] Implement JEA for delegated admin tasks
- [ ] Enable audit logging for all privileged operations
- [ ] Use least privilege principle
- [ ] Rotate credentials regularly
- [ ] Monitor failed authentication attempts

### Production Environments

- [ ] Implement WDAC policies for script control
- [ ] Use Constrained Language Mode for non-admin users
- [ ] Enable PowerShell logging (Script Block + Transcription)
- [ ] Require signed scripts (via execution policy)
- [ ] Regular security audits
- [ ] Keep PowerShell updated (7.5+)
- [ ] Use JEA for remote administration

## Resources

- [SecretManagement Documentation](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.secretmanagement)
- [JEA Documentation](https://learn.microsoft.com/en-us/powershell/scripting/security/remoting/jea/overview)
- [WDAC Documentation](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/windows-defender-application-control)
- [PowerShell Security Best Practices](https://learn.microsoft.com/en-us/powershell/scripting/security/securing-powershell)
- [Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/)
