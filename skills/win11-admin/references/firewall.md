# Windows Firewall

## Firewall Management

```powershell
# Check firewall status
Get-NetFirewallProfile | Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction

# Enable all profiles
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True

# Set default deny inbound
Set-NetFirewallProfile -Profile Domain,Public,Private -DefaultInboundAction Block -DefaultOutboundAction Allow

# List all rules
Get-NetFirewallRule | Where-Object Enabled -eq True | Select-Object DisplayName, Direction, Action, Profile | Sort-Object DisplayName

# Create allow rule
New-NetFirewallRule -DisplayName "Allow MyApp" -Direction Inbound -Program "C:\MyApp\app.exe" -Action Allow -Profile Private

# Create port rule
New-NetFirewallRule -DisplayName "Allow HTTPS" -Direction Inbound -LocalPort 443 -Protocol TCP -Action Allow

# Block specific IP
New-NetFirewallRule -DisplayName "Block BadIP" -Direction Inbound -RemoteAddress "1.2.3.4" -Action Block

# Remove rule
Remove-NetFirewallRule -DisplayName "Allow MyApp"

# Disable rule
Disable-NetFirewallRule -DisplayName "Allow MyApp"

# Export/Import rules (backup)
netsh advfirewall export "$env:USERPROFILE\backups\firewall_$(Get-Date -Format yyyyMMdd).wfw"
# netsh advfirewall import "$env:USERPROFILE\backups\firewall_backup.wfw"
```
