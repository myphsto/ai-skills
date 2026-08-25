# WDAC & Code Signing

## Windows Defender Application Control (WDAC)

### PowerShell Script Control

**WDAC** replaces AppLocker for controlling which PowerShell scripts can execute.

```powershell
# Create WDAC policy for signed scripts only
New-CIPolicy -FilePath "C:\WDAC\PowerShellPolicy.xml" `
    -ScanPath "C:\Scripts" `
    -Level FilePublisher `
    -Fallback Hash `
    -UserPEs

# Allow only signed scripts
Set-RuleOption -FilePath "C:\WDAC\PowerShellPolicy.xml" `
    -Option 3 # Required WHQL

# Convert to binary policy
ConvertFrom-CIPolicy -XmlFilePath "C:\WDAC\PowerShellPolicy.xml" `
    -BinaryFilePath "C:\Windows\System32\CodeIntegrity\SIPolicy.p7b"

# Reboot to apply policy
Restart-Computer
```

## Code Signing

### Why Sign Scripts?

- Verify script integrity
- Meet organizational security policies
- Enable WDAC enforcement
- Prevent tampering

### Signing a Script

```powershell
# Get code signing certificate
$cert = Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert

# Sign script
Set-AuthenticodeSignature -FilePath "C:\Scripts\MyScript.ps1" -Certificate $cert

# Verify signature
$signature = Get-AuthenticodeSignature -FilePath "C:\Scripts\MyScript.ps1"
$signature.Status  # Should be "Valid"
```

### Execution Policy

```powershell
# Check current execution policy
Get-ExecutionPolicy

# Set execution policy (requires admin)
Set-ExecutionPolicy RemoteSigned -Scope LocalMachine

# Bypass for single script (testing only)
PowerShell.exe -ExecutionPolicy Bypass -File "script.ps1"
```
