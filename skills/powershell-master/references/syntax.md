# PowerShell Syntax & Cmdlets

## Cmdlet Structure

```powershell
# Verb-Noun pattern
Get-ChildItem
Set-Location
New-Item
Remove-Item

# Common parameters (available on all cmdlets)
Get-Process -Verbose
Set-Content -Path file.txt -WhatIf
Remove-Item -Path folder -Confirm
Invoke-RestMethod -Uri $url -ErrorAction Stop
```

## Variables & Data Types

```powershell
# Variables (loosely typed)
$string = "Hello World"
$number = 42
$array = @(1, 2, 3, 4, 5)
$hashtable = @{Name="John"; Age=30}

# Strongly typed
[string]$name = "John"
[int]$age = 30
[datetime]$date = Get-Date

# Special variables
$PSScriptRoot  # Directory containing the script
$PSCommandPath  # Full path to the script
$args  # Script arguments
$_  # Current pipeline object
```

## Operators

```powershell
# Comparison operators
-eq  # Equal
-ne  # Not equal
-gt  # Greater than
-lt  # Less than
-match  # Regex match
-like  # Wildcard match
-contains  # Array contains

# Logical operators
-and
-or
-not

# PowerShell 7+ ternary operator
$result = $condition ? "true" : "false"

# Null-coalescing (PS 7+)
$value = $null ?? "default"
```

## Control Flow

```powershell
# If-ElseIf-Else
if ($condition) {
    # Code
} elseif ($otherCondition) {
    # Code
} else {
    # Code
}

# Switch
switch ($value) {
    1 { "One" }
    2 { "Two" }
    {$_ -gt 10} { "Greater than 10" }
    default { "Other" }
}

# Loops
foreach ($item in $collection) {
    # Process item
}

for ($i = 0; $i -lt 10; $i++) {
    # Loop code
}

while ($condition) {
    # Loop code
}

do {
    # Loop code
} while ($condition)
```

## Functions

```powershell
function Get-Something {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Name,

        [Parameter()]
        [int]$Count = 1,

        [Parameter(ValueFromPipeline=$true)]
        [string[]]$InputObject
    )

    begin {
        # Initialization
    }

    process {
        # Process each pipeline object
        foreach ($item in $InputObject) {
            # Work with $item
        }
    }

    end {
        # Cleanup
        return $result
    }
}
```

## Pipeline & Filtering

```powershell
# Pipeline basics
Get-Process | Where-Object {$_.CPU -gt 100} | Select-Object Name, CPU

# Simplified syntax (PS 3.0+)
Get-Process | Where CPU -gt 100 | Select Name, CPU

# ForEach-Object
Get-ChildItem | ForEach-Object {
    Write-Host $_.Name
}

# Simplified (PS 4.0+)
Get-ChildItem | % Name

# Group, Sort, Measure
Get-Process | Group-Object ProcessName
Get-Service | Sort-Object Status
Get-ChildItem | Measure-Object -Property Length -Sum
```

## Error Handling

```powershell
# Try-Catch-Finally
try {
    Get-Content -Path "nonexistent.txt" -ErrorAction Stop
}
catch [System.IO.FileNotFoundException] {
    Write-Error "File not found"
}
catch {
    Write-Error "An error occurred: $_"
}
finally {
    # Cleanup code
}

# Error action preference
$ErrorActionPreference = "Stop"  # Treat all errors as terminating
$ErrorActionPreference = "Continue"  # Default
$ErrorActionPreference = "SilentlyContinue"  # Suppress errors
```
