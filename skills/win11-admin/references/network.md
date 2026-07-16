# Network Configuration

## Network Diagnostics

```powershell
# IP configuration
Get-NetIPAddress | Where-Object AddressFamily -eq "IPv4" | Select-Object InterfaceAlias, IPAddress, PrefixLength

# DNS configuration
Get-DnsClientServerAddress | Where-Object AddressFamily -eq 2 | Select-Object InterfaceAlias, ServerAddresses

# Set DNS (e.g., Cloudflare)
Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses "1.1.1.1","1.0.0.1"

# Flush DNS cache
Clear-DnsClientCache

# Check active connections
Get-NetTCPConnection -State Established | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, OwningProcess | Sort-Object RemoteAddress

# Check listening ports
Get-NetTCPConnection -State Listen | Select-Object LocalAddress, LocalPort, OwningProcess | Sort-Object LocalPort

# Resolve process for port
Get-NetTCPConnection -LocalPort 8080 | ForEach-Object { Get-Process -Id $_.OwningProcess }

# Network adapter info
Get-NetAdapter | Select-Object Name, Status, LinkSpeed, MacAddress

# Wi-Fi profiles
netsh wlan show profiles

# Speed test (basic)
Test-NetConnection -ComputerName "8.8.8.8" -InformationLevel Detailed
```
