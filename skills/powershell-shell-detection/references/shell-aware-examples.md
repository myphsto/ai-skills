# Shell-Aware Script Design & Practical Examples

## When to Use PowerShell vs Git Bash on Windows

### Use PowerShell When:

- **Windows-specific tasks** - Registry, WMI, Windows services
- **Azure/Microsoft 365 automation** - Az, Microsoft.Graph modules
- **Module ecosystem** - Leverage PSGallery modules
- **Object-oriented pipelines** - Rich object manipulation
- **Native Windows integration** - Built into Windows
- **CI/CD with pwsh** - GitHub Actions, Azure DevOps
- **Cross-platform scripting** - PowerShell 7 works on Linux/macOS

**Example PowerShell Scenario:**
```powershell
# Azure VM management with Az module
Connect-AzAccount
Get-AzVM -ResourceGroupName "Production" |
    Where-Object {$_.PowerState -eq "VM running"} |
    Stop-AzVM -Force
```

### Use Git Bash When:

- **Unix tool compatibility** - sed, awk, grep, find
- **Git operations** - Native Git command-line experience
- **POSIX script execution** - Running Linux shell scripts
- **Cross-platform shell scripts** - Bash scripts from Linux/macOS
- **Text processing** - Unix text utilities (sed, awk, cut)
- **Development workflows** - Node.js, Python, Ruby with Unix tools

**Example Git Bash Scenario:**
```bash
# Git workflow with Unix tools
git log --oneline | grep -i "feature" | awk '{print $1}' |
    xargs git show --stat
```

## Shell-Aware Script Design

### Detect and Adapt (PowerShell)

```powershell
# Detect if running in PowerShell or Git Bash context
function Test-PowerShellContext {
    return ($null -ne $PSVersionTable)
}

# Adapt path handling based on context
function Get-CrossPlatformPath {
    param([string]$Path)

    if (Test-PowerShellContext) {
        # PowerShell: Use Join-Path
        return (Resolve-Path $Path -ErrorAction SilentlyContinue).Path
    }
    else {
        # Non-PowerShell context
        Write-Warning "Not running in PowerShell. Path operations may differ."
        return $Path
    }
}
```

### Detect and Adapt (Bash)

```bash
# Detect shell environment
detect_shell() {
    if [ -n "$MSYSTEM" ]; then
        echo "git-bash"
    elif [ -n "$PSModulePath" ]; then
        echo "powershell"
    elif [ -n "$WSL_DISTRO_NAME" ]; then
        echo "wsl"
    else
        echo "unix"
    fi
}

# Adapt path handling
convert_path() {
    local path="$1"
    local shell_type=$(detect_shell)

    case "$shell_type" in
        git-bash)
            # Convert Windows path to Unix style
            echo "$path" | sed 's|\\|/|g' | sed 's|^\([A-Z]\):|/\L\1|'
            ;;
        *)
            echo "$path"
            ;;
    esac
}

# Usage
shell_type=$(detect_shell)
echo "Running in: $shell_type"
```

## Practical Examples

### Example 1: Cross-Shell File Finding

**PowerShell:**
```powershell
Get-ChildItem -Path "C:\Projects" -Recurse -File |
    Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-7) } |
    Select-Object FullName, LastWriteTime
```

**Git Bash:**
```bash
find /c/Projects -type f -mtime -7 -exec ls -lh {} \;
```

### Example 2: Process Management

**PowerShell:**
```powershell
Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force
```

**Git Bash:**
```bash
ps aux | grep chrome | awk '{print $2}' | xargs kill -9 2>/dev/null
```

### Example 3: Text File Processing

**PowerShell:**
```powershell
Get-Content "logs.txt" |
    Select-String -Pattern '\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b' |
    ForEach-Object { $_.Matches.Value } |
    Sort-Object -Unique
```

**Git Bash:**
```bash
grep -oE '\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b' logs.txt |
    sort -u
```

## Troubleshooting Cross-Shell Issues

### Issue 1: Command Not Found

**Problem:** Command works in one shell but not another

**Solution:** PowerShell cmdlets don't exist in Bash. Use native commands or install PowerShell Core (pwsh) in Git Bash:
```bash
pwsh -Command "Get-Process"
```

### Issue 2: Path Format Mismatches

**Problem:** Paths don't work across shells

**Solution:** Use cygpath for conversion or normalize paths:
```bash
win_path=$(cygpath -w "/c/Users/John/file.txt")
pwsh -Command "Test-Path '$win_path'"
```

### Issue 3: Alias Conflicts

**Problem:** `ls`, `cd`, `cat` behave differently

**Solution:** Use full cmdlet names in PowerShell scripts:
```powershell
Get-ChildItem  # Instead of: ls
```
