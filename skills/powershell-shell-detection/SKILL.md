---
name: powershell-shell-detection
description: "PowerShell vs Git Bash/MSYS2 shell detection and cross-shell compatibility on Windows. Use when detecting the active shell (PowerShell, pwsh, Git Bash, cmd, WSL), handling shell-specific paths, MSYS_NO_PATHCONV, CRLF vs LF line endings, env-var differences, profile loading differences, or calling .ps1 from bash and bash from PowerShell. Provides detection one-liners, cygpath helpers, and cross-shell invocation recipes."
license: MIT
compatibility: "Windows (PowerShell 5.1/7+ and Git Bash/MSYS2; WSL notes)"
metadata:
  author: myphsto
  version: "1.0"
---

# PowerShell Shell Detection & Cross-Shell Compatibility

Critical guidance for distinguishing between PowerShell and Git Bash/MSYS2 shells on Windows, with shell-specific path handling and compatibility notes.

## Shell Detection Priority (Windows)

When working on Windows, correctly identifying the shell environment is crucial for proper path handling and command execution.

### Detection Order (Most Reliable First)

1. **process.env.PSModulePath** (PowerShell specific)
2. **process.env.MSYSTEM** (Git Bash/MinGW specific)
3. **process.env.WSL_DISTRO_NAME** (WSL specific)
4. **uname -s output** (Cross-shell, requires execution)

## PowerShell Detection

### Primary Indicators

**PSModulePath (Most Reliable):**
```powershell
# PowerShell detection
if ($env:PSModulePath) {
    Write-Host "Running in PowerShell"
    # PSModulePath contains 3+ paths separated by semicolons
    $env:PSModulePath -split ';'
}

# Check PowerShell version
$PSVersionTable.PSVersion
# Output: 7.6.5 (PowerShell 7) or 5.1.x (Windows PowerShell)
```

**PowerShell-Specific Variables:**
```powershell
# These only exist in PowerShell
$PSVersionTable    # Version info
$PSScriptRoot      # Script directory
$PSCommandPath     # Script full path
$IsWindows         # Platform detection (PS 7+)
$IsLinux           # Platform detection (PS 7+)
$IsMacOS           # Platform detection (PS 7+)
```

### Shell Type Detection in Scripts

```powershell
function Get-ShellType {
    if ($PSVersionTable) {
        return "PowerShell $($PSVersionTable.PSVersion)"
    }
    elseif ($env:PSModulePath -and ($env:PSModulePath -split ';').Count -ge 3) {
        return "PowerShell (detected via PSModulePath)"
    }
    else {
        return "Not PowerShell"
    }
}

Get-ShellType
```

## Git Bash / MSYS2 Detection

### Primary Indicators

**MSYSTEM Environment Variable (Most Reliable):**
```bash
# Bash detection in Git Bash/MSYS2
if [ -n "$MSYSTEM" ]; then
    echo "Running in Git Bash/MSYS2: $MSYSTEM"
fi

# MSYSTEM values:
# MINGW64 - Native Windows 64-bit environment
# MINGW32 - Native Windows 32-bit environment
# MSYS    - POSIX-compliant build environment
```

**Secondary Detection Methods:**
```bash
# Using OSTYPE (Bash-specific)
case "$OSTYPE" in
    msys*)   echo "MSYS/Git Bash" ;;
    cygwin*) echo "Cygwin" ;;
    linux*)  echo "Linux" ;;
    darwin*) echo "macOS" ;;
esac

# Using uname (Most portable)
case "$(uname -s)" in
    MINGW64*) echo "Git Bash 64-bit" ;;
    MINGW32*) echo "Git Bash 32-bit" ;;
    MSYS*)    echo "MSYS" ;;
    CYGWIN*)  echo "Cygwin" ;;
    Linux*)   echo "Linux" ;;
    Darwin*)  echo "macOS" ;;
esac
```

## Cross-Shell Compatibility on Windows

### Critical Differences

| Aspect | PowerShell | Git Bash/MSYS2 |
|--------|-----------|----------------|
| **Environment Variable** | `$env:VARIABLE` | `$VARIABLE` |
| **Path Separator** | `;` (semicolon) | `:` (colon) |
| **Path Style** | `C:\Windows\System32` | `/c/Windows/System32` |
| **Home Directory** | `$env:USERPROFILE` | `$HOME` |
| **Temp Directory** | `$env:TEMP` | `/tmp` |
| **Command Format** | `Get-ChildItem` | `ls` (native command) |
| **Aliases** | PowerShell cmdlet aliases | Unix command aliases |

### Path Handling: PowerShell vs Git Bash

**PowerShell Path Handling:**
```powershell
# Native Windows paths work directly
$path = "C:\Users\John\Documents"
Test-Path $path  # True

# Forward slashes also work in PowerShell 7+
$path = "C:/Users/John/Documents"
Test-Path $path  # True

# Use Join-Path for cross-platform compatibility
$configPath = Join-Path -Path $PSScriptRoot -ChildPath "config.json"

# Use [System.IO.Path] for advanced scenarios
$fullPath = [System.IO.Path]::Combine($home, "documents", "file.txt")
```

**Git Bash Path Handling:**
```bash
# Git Bash uses Unix-style paths
path="/c/Users/John/Documents"
test -d "$path" && echo "Directory exists"

# Automatic path conversion (CAUTION)
# Git Bash converts Unix-style paths to Windows-style
# /c/Users → C:\Users (automatic)
# Arguments starting with / may be converted unexpectedly

# Use cygpath for manual conversion
cygpath -u "C:\path"      # → /c/path (Unix format)
cygpath -w "/c/path"      # → C:\path (Windows format)
cygpath -m "/c/path"      # → C:/path (Mixed format)
```

## Automatic Path Conversion in Git Bash (CRITICAL)

Git Bash/MSYS2 automatically converts paths in certain scenarios, which can cause issues:

### What Triggers Conversion

```bash
# Leading forward slash triggers conversion
command /foo         # Converts to C:\msys64\foo

# Path lists with colons
export PATH=/foo:/bar  # Converts to C:\msys64\foo;C:\msys64\bar

# Arguments after dashes
command --path=/foo    # Converts to --path=C:\msys64\foo
```

### What's Exempt from Conversion

```bash
# Arguments with equals sign (variable assignments)
VAR=/foo command      # NOT converted

# Drive specifiers
command C:/path       # NOT converted

# Arguments with semicolons (already Windows format)
command "C:\foo;D:\bar"  # NOT converted

# Double slashes (Windows switches)
command //e //s       # NOT converted
```

### Disabling Path Conversion

```bash
# Disable ALL conversion (Git Bash)
export MSYS_NO_PATHCONV=1
command /foo  # Stays as /foo

# Exclude specific patterns (MSYS2)
export MSYS2_ARG_CONV_EXCL="*"           # Exclude everything
export MSYS2_ARG_CONV_EXCL="--dir=;/test"  # Specific prefixes
```

## When to Use Which Shell

| Choose PowerShell when | Choose Git Bash when |
|---|---|
| Windows-specific tasks (Registry, WMI, services) | Unix tool compatibility (sed, awk, grep) |
| Azure/M365 automation (Az, Microsoft.Graph) | Git operations / POSIX scripts |
| Module ecosystem (PSGallery) | Text processing pipelines |
| Object-oriented pipelines | Cross-platform bash scripts |

> **See [`references/shell-aware-examples.md`](references/shell-aware-examples.md)** for shell-aware script design patterns, practical cross-shell examples, and troubleshooting.

## Environment Variable Comparison

### Common Environment Variables

| Variable | PowerShell | Git Bash | Purpose |
|----------|-----------|----------|---------|
| **Username** | `$env:USERNAME` | `$USER` | Current user |
| **Home Directory** | `$env:USERPROFILE` | `$HOME` | User home |
| **Temp Directory** | `$env:TEMP` | `/tmp` | Temporary files |
| **Path List** | `$env:Path` (`;` sep) | `$PATH` (`:` sep) | Executable paths |
| **Shell Detection** | `$env:PSModulePath` | `$MSYSTEM` | Shell identifier |

### Cross-Shell Variable Access

**PowerShell accessing environment variables:**
```powershell
$env:PATH              # Current PATH
$env:PSModulePath      # PowerShell module paths
$env:MSYSTEM           # Would be empty in PowerShell
[Environment]::GetEnvironmentVariable("PATH", "Machine")  # System PATH
```

**Git Bash accessing environment variables:**
```bash
echo $PATH             # Current PATH
echo $MSYSTEM          # Git Bash: MINGW64, MINGW32, or MSYS
echo $PSModulePath     # Would be empty in pure Bash
```

## Troubleshooting

> **See [`references/shell-aware-examples.md`](references/shell-aware-examples.md)** for practical cross-shell examples and troubleshooting common issues (command not found, path mismatches, alias conflicts).

## Best Practices Summary

### PowerShell Scripts
1. ✅ Use `$PSScriptRoot` for script-relative paths
2. ✅ Use `Join-Path` or `[IO.Path]::Combine()` for paths
3. ✅ Avoid hardcoded backslashes
4. ✅ Use full cmdlet names (no aliases)
5. ✅ Test on all target platforms
6. ✅ Use `$IsWindows`, `$IsLinux`, `$IsMacOS` for platform detection

### Git Bash Scripts
1. ✅ Check `$MSYSTEM` for Git Bash detection
2. ✅ Use `cygpath` for path conversion when needed
3. ✅ Set `MSYS_NO_PATHCONV=1` to disable auto-conversion if needed
4. ✅ Quote paths with spaces
5. ✅ Use Unix-style paths (`/c/...`) within Bash
6. ✅ Convert to Windows paths when calling Windows tools

### Cross-Shell Development
1. ✅ Document which shell your script requires
2. ✅ Add shell detection at script start
3. ✅ Provide clear error messages for wrong shell
4. ✅ Consider creating wrapper scripts for cross-shell compatibility
5. ✅ Test in both PowerShell and Git Bash if supporting both

## Resources

- [PowerShell Documentation](https://learn.microsoft.com/powershell)
- [Git for Windows Documentation](https://git-scm.com/doc)
- [MSYS2 Documentation](https://www.msys2.org/docs/what-is-msys2/)
- [Cygpath Documentation](https://www.cygwin.com/cygwin-ug-net/cygpath.html)

---

**Last Updated:** October 2025
