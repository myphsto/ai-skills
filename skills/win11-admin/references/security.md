# Security Hardening (CIS/STIG)

## CIS Benchmark Key Settings

```powershell
# --- ACCOUNT POLICIES ---
# Set minimum password length (14 chars - CIS)
net accounts /minpwlen:14

# Set password history (24 - CIS)
net accounts /uniquepw:24

# Set account lockout threshold (5 attempts - CIS)
net accounts /lockoutthreshold:5

# --- AUDIT POLICY ---
# Enable auditing for key events
auditpol /set /category:"Logon/Logoff" /success:enable /failure:enable
auditpol /set /category:"Account Logon" /success:enable /failure:enable
auditpol /set /category:"Account Management" /success:enable /failure:enable
auditpol /set /category:"Policy Change" /success:enable /failure:enable
auditpol /set /category:"Privilege Use" /success:enable /failure:enable

# --- NETWORK ---
# Disable NetBIOS over TCP/IP
$adapters = Get-WmiObject Win32_NetworkAdapterConfiguration -Filter "IPEnabled=True"
foreach ($adapter in $adapters) {
    $adapter.SetTcpipNetbios(2)  # 2 = Disable
}

# Disable LLMNR (Link-Local Multicast Name Resolution)
New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\DNSClient" -Force
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\DNSClient" -Name "EnableMulticast" -Value 0

# --- SMB ---
# Disable SMBv1 (critical security)
Disable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -NoRestart
Set-SmbServerConfiguration -EnableSMB1Protocol $false -Force

# Enable SMB signing
Set-SmbServerConfiguration -RequireSecuritySignature $true -Force
Set-SmbClientConfiguration -RequireSecuritySignature $true -Force

# --- UAC ---
# Ensure UAC is enabled and set to highest level
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "EnableLUA" -Value 1
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "ConsentPromptBehaviorAdmin" -Value 2  # Prompt for consent on secure desktop
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "PromptOnSecureDesktop" -Value 1

# --- REMOTE ---
# Disable Remote Desktop (if not needed)
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server" -Name "fDenyTSConnections" -Value 1

# Disable Remote Assistance
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Remote Assistance" -Name "fAllowToGetHelp" -Value 0

# --- BITLOCKER ---
# Check BitLocker status
Get-BitLockerVolume | Select-Object MountPoint, VolumeStatus, EncryptionMethod, ProtectionStatus

# Enable BitLocker on C:
# Enable-BitLocker -MountPoint "C:" -EncryptionMethod XtsAes256 -UsedSpaceOnly -RecoveryPasswordProtector
```

## CIS Rollback Commands

```powershell
# --- ACCOUNT POLICIES ROLLBACK ---
net accounts /minpwlen:7
net accounts /uniquepw:24
net accounts /lockoutthreshold:0

# --- AUDIT POLICY ROLLBACK ---
auditpol /set /category:"Logon/Logoff" /success:disable /failure:disable
auditpol /set /category:"Account Logon" /success:disable /failure:disable
auditpol /set /category:"Account Management" /success:disable /failure:disable
auditpol /set /category:"Policy Change" /success:disable /failure:disable
auditpol /set /category:"Privilege Use" /success:disable /failure:disable

# --- NETWORK ROLLBACK ---
$adapters = Get-WmiObject Win32_NetworkAdapterConfiguration -Filter "IPEnabled=True"
foreach ($adapter in $adapters) { $adapter.SetTcpipNetbios(0) }
Remove-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\DNSClient" -Name "EnableMulticast" -ErrorAction SilentlyContinue

# --- SMB ROLLBACK ---
Enable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -NoRestart
Set-SmbServerConfiguration -EnableSMB1Protocol $true -Force
Set-SmbServerConfiguration -RequireSecuritySignature $false -Force
Set-SmbClientConfiguration -RequireSecuritySignature $false -Force

# --- UAC ROLLBACK ---
Remove-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "EnableLUA" -ErrorAction SilentlyContinue
Remove-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "ConsentPromptBehaviorAdmin" -ErrorAction SilentlyContinue
Remove-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "PromptOnSecureDesktop" -ErrorAction SilentlyContinue

# --- REMOTE ROLLBACK ---
Remove-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server" -Name "fDenyTSConnections" -ErrorAction SilentlyContinue
Remove-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Remote Assistance" -Name "fAllowToGetHelp" -ErrorAction SilentlyContinue
```
