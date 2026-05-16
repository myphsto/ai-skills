#!/usr/bin/env python3
"""
Evaluate PowerShell/Win11 skills for content preservation after deduplication.

Checks that:
1. Cross-references point to valid files
2. Removed content still exists somewhere in the skill tree
3. No orphaned references
4. Key topics are covered across the skill set
"""

import os
import sys
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Set

SKILLS_DIR = Path(__file__).parent.parent / "skills"

# Topics that must exist somewhere in the skill tree after deduplication
REQUIRED_TOPICS = {
    # powershell-security topics (authoritative)
    "SecretManagement": {"skill": "powershell-security", "keywords": ["SecretManagement", "Set-Secret", "Get-Secret"]},
    "JEA": {"skill": "powershell-security", "keywords": ["Just Enough Administration", "New-PSRoleCapabilityFile", "Register-PSSessionConfiguration"]},
    "WDAC": {"skill": "powershell-security", "keywords": ["Windows Defender Application Control", "New-CIPolicy", "ConvertFrom-CIPolicy"]},
    "ConstrainedLanguage": {"skill": "powershell-security", "keywords": ["Constrained Language Mode", "__PSLockdownPolicy"]},
    "ScriptBlockLogging": {"skill": "powershell-security", "keywords": ["Script Block Logging", "EnableScriptBlockLogging"]},
    "CodeSigning": {"skill": "powershell-security", "keywords": ["Set-AuthenticodeSignature", "Get-AuthenticodeSignature"]},

    # powershell-7.5-features topics (authoritative)
    "PSResourceGet": {"skill": "powershell-7.5-features", "keywords": ["PSResourceGet", "Install-PSResource", "Find-PSResource"]},
    "ConvertToCliXml": {"skill": "powershell-7.5-features", "keywords": ["ConvertTo-CliXml", "ConvertFrom-CliXml"]},
    "TestPathOlderThan": {"skill": "powershell-7.5-features", "keywords": ["Test-Path", "OlderThan", "NewerThan"]},
    "PlusEqualsOpt": {"skill": "powershell-7.5-features", "keywords": ["+=", "operator", "optimization"]},
    "GetClipboardDelim": {"skill": "powershell-7.5-features", "keywords": ["Get-Clipboard", "Delimiter"]},
    "DSCv3": {"skill": "powershell-7.5-features", "keywords": ["DSC v3", "PSDesiredStateConfiguration"]},

    # powershell-2025-changes topics
    "PS2Removal": {"skill": "powershell-2025-changes", "keywords": ["PowerShell 2.0", "removed"]},
    "MSOnlineRetirement": {"skill": "powershell-2025-changes", "keywords": ["MSOnline", "retirement", "Microsoft.Graph"]},
    "WMICRemoval": {"skill": "powershell-2025-changes", "keywords": ["WMIC", "Get-CimInstance"]},
    "PSSnapinRemoval": {"skill": "powershell-2025-changes", "keywords": ["PSSnapin", "#Requires"]},

    # win11-admin topics
    "RegistryAdmin": {"skill": "win11-admin", "keywords": ["registry", "HKLM:", "Set-ItemProperty"]},
    "ServicesMgmt": {"skill": "win11-admin", "keywords": ["Get-Service", "Set-Service", "StartupType"]},
    "Debloating": {"skill": "win11-admin", "keywords": ["bloatware", "Remove-AppxPackage", "Get-AppxPackage"]},
    "CISHardening": {"skill": "win11-admin", "keywords": ["CIS", "auditpol", "account lockout"]},
    "Firewall": {"skill": "win11-admin", "keywords": ["NetFirewall", "Set-NetFirewallProfile"]},
    "ASRRules": {"skill": "win11-admin", "keywords": ["ASR", "AttackSurfaceReduction"]},
    "QuickRef": {"skill": "win11-admin", "keywords": ["Checkpoint-Computer", "devmgmt.msc"]},

    # powershell-master topics
    "CICD": {"skill": "powershell-master", "keywords": ["GitHub Actions", "Azure DevOps", "Bitbucket"]},
    "AzModule": {"skill": "powershell-master", "keywords": ["Az.Accounts", "Az.Compute", "Az.Storage"]},
    "MicrosoftGraph": {"skill": "powershell-master", "keywords": ["Microsoft.Graph", "Connect-MgGraph"]},
    "Pester": {"skill": "powershell-master", "keywords": ["Pester", "Invoke-Pester", "Describe"]},
    "CmdletRef": {"skill": "powershell-master", "keywords": ["cmdlet", "Get-ChildItem", "Get-Process"]},

    # powershell-shell-detection topics
    "ShellDetection": {"skill": "powershell-shell-detection", "keywords": ["PSModulePath", "MSYSTEM"]},
    "PathConversion": {"skill": "powershell-shell-detection", "keywords": ["cygpath", "MSYS_NO_PATHCONV"]},
}

# Cross-references that should exist
CROSS_REFS = [
    {"from": "powershell-master", "to": "powershell-security", "about": "JEA/WDAC/security"},
    {"from": "powershell-master", "to": "powershell-7.5-features", "about": "PSResourceGet"},
    {"from": "powershell-2025-changes", "to": "powershell-security", "about": "JEA/WDAC/Constrained Language"},
    {"from": "powershell-2025-changes", "to": "powershell-7.5-features", "about": "PSResourceGet"},
    {"from": "win11-admin", "to": "powershell-security", "about": "Defender/ASR"},
    {"from": "win11-admin", "to": "references", "about": "quick_ref"},
    {"from": "win11-admin", "to": "references", "about": "asr_rules"},
    {"from": "powershell-master", "to": "references", "about": "cmdlet_ref"},
]

@dataclass
class EvalResult:
    name: str
    passed: bool
    detail: str
    category: str

results: List[EvalResult] = []
errors: int = 0
warnings: int = 0
passes: int = 0

def log(name: str, passed: bool, detail: str, category: str, is_warning: bool = False):
    global passes, errors, warnings
    results.append(EvalResult(name, passed, detail, category))
    if passed:
        passes += 1
        print(f"  PASS [{category}] {name}")
    elif is_warning:
        warnings += 1
        print(f"  WARN [{category}] {name}: {detail}")
    else:
        errors += 1
        print(f"  FAIL [{category}] {name}: {detail}")

def read_skill_files(skill_dir: Path) -> Dict[str, str]:
    """Read all .md files in a skill directory."""
    files = {}
    for md_file in skill_dir.rglob("*.md"):
        rel = md_file.relative_to(skill_dir)
        files[str(rel)] = md_file.read_text()
    return files

def has_content(content: str, keywords: List[str]) -> bool:
    """Check if content contains all keywords (case-insensitive)."""
    text = content.lower()
    return all(kw.lower() in text for kw in keywords)

def main():
    print("=" * 70)
    print("SKILL EVALUATION: PowerShell/Win11 Skills Post-Dedup")
    print("=" * 70)

    # Read all skill files
    skills = {}
    for skill_name in REQUIRED_TOPICS.values():
        sname = skill_name["skill"]
        skill_path = SKILLS_DIR / sname
        if skill_path.exists():
            skills[sname] = read_skill_files(skill_path)

    # Also check standalone skills
    for skill_dir in SKILLS_DIR.iterdir():
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
            if skill_dir.name not in skills:
                skills[skill_dir.name] = read_skill_files(skill_dir)

    print(f"\nLoaded {len(skills)} skills: {', '.join(sorted(skills.keys()))}\n")

    # --- TEST 1: Required topics coverage ---
    print("-" * 50)
    print("TEST 1: Required Topics Coverage")
    print("-" * 50)

    for topic, info in REQUIRED_TOPICS.items():
        skill_name = info["skill"]
        keywords = info["keywords"]
        skill_files = skills.get(skill_name, {})

        # Search across all files in the skill
        found = False
        found_in = None
        for fname, content in skill_files.items():
            if has_content(content, keywords):
                found = True
                found_in = fname
                break

        log(topic, found,
            f"Expected in {skill_name}/, found in {found_in or 'nowhere'}",
            "coverage")

    # --- TEST 2: Cross-references valid ---
    print(f"\n{'-' * 50}")
    print("TEST 2: Cross-References Valid")
    print("-" * 50)

    for ref in CROSS_REFS:
        from_skill = ref["from"]
        to_skill = ref["to"]
        about = ref["about"]

        from_files = skills.get(from_skill, {})
        found_ref = False

        for fname, content in from_files.items():
            # Check for markdown-style or plain cross-reference
            if to_skill in content or (to_skill == "references" and "references/" in content):
                found_ref = True
                break

        log(f"{from_skill} → {to_skill} ({about})", found_ref,
            f"No cross-ref found in {from_skill}/",
            "cross-ref")

    # --- TEST 3: Reference files exist ---
    print(f"\n{'-' * 50}")
    print("TEST 3: Reference Files Exist")
    print("-" * 50)

    ref_checks = [
        ("win11-admin", "references/quick_ref.md"),
        ("win11-admin", "references/asr_rules.md"),
        ("powershell-master", "references/cmdlet_ref.md"),
    ]

    for skill_name, ref_file in ref_checks:
        full_path = SKILLS_DIR / skill_name / ref_file
        exists = full_path.exists()
        log(f"{skill_name}/{ref_file}", exists,
            f"File {'exists' if exists else 'missing'}",
            "refs")

    # --- TEST 4: No hardcoded paths ---
    print(f"\n{'-' * 50}")
    print("TEST 4: No Hardcoded Paths")
    print("-" * 50)

    hardcoded_patterns = [
        r"C:\\Users\\cesco",
        r"C:\\Users\\[^$*\w]",  # Hardcoded user paths (exclude $var, wildcards, example names)
    ]
    # Whitelist example paths that are clearly documentation, not real paths
    whitelisted = {"C:\\Users\\N", "C:\\Users\\J", "C:\\Users\\John", "C:\\Users\\*"}

    for skill_name, skill_files in skills.items():
        for fname, content in skill_files.items():
            for pattern in hardcoded_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    log(f"{skill_name}/{fname} hardcoded path", False,
                        f"Found: {matches}",
                        "safety")

    # --- TEST 5: Rollback commands present ---
    print(f"\n{'-' * 50}")
    print("TEST 5: Rollback Commands Present")
    print("-" * 50)

    rollback_checks = [
        ("win11-admin", "registry", ["Remove-ItemProperty", "rollback", "Rollback"]),
        ("win11-admin", "GPO", ["Remove-ItemProperty", "rollback", "Rollback"]),
        ("win11-admin", "CIS", ["rollback", "Rollback", "net accounts"]),
        ("win11-admin", "Defender", ["Set-MpPreference", "rollback", "Rollback"]),
    ]

    for skill_name, section, keywords in rollback_checks:
        skill_files = skills.get(skill_name, {})
        found = False
        for fname, content in skill_files.items():
            if has_content(content, keywords):
                found = True
                break
        log(f"{skill_name} {section} rollback", found,
            f"No rollback commands for {section}",
            "safety")

    # --- TEST 6: No duplicate content blocks ---
    print(f"\n{'-' * 50}")
    print("TEST 6: No Duplicate Content Blocks")
    print("-" * 50)

    # Check that JEA config code only lives in powershell-security
    jea_code = "New-PSRoleCapabilityFile"
    jea_locations = []
    for sname, sfiles in skills.items():
        for fname, content in sfiles.items():
            if jea_code in content:
                jea_locations.append(f"{sname}/{fname}")

    if len(jea_locations) == 1 and "powershell-security" in jea_locations[0]:
        log("JEA config dedup", True, f"Only in {jea_locations[0]}", "dedup")
    else:
        log("JEA config dedup", False,
            f"Found in: {', '.join(jea_locations)}", "dedup")

    # Check WDAC code only in security
    wdac_code = "New-CIPolicy"
    wdac_locations = []
    for sname, sfiles in skills.items():
        for fname, content in sfiles.items():
            if wdac_code in content:
                wdac_locations.append(f"{sname}/{fname}")

    if len(wdac_locations) == 1 and "powershell-security" in wdac_locations[0]:
        log("WDAC config dedup", True, f"Only in {wdac_locations[0]}", "dedup")
    else:
        log("WDAC config dedup", False,
            f"Found in: {', '.join(wdac_locations)}", "dedup")

    # Check PSResourceGet details only in 7.5-features
    psr_code = "Install-PSResource"
    psr_locations = []
    for sname, sfiles in skills.items():
        for fname, content in sfiles.items():
            if psr_code in content:
                psr_locations.append(f"{sname}/{fname}")

    # PSResourceGet should be in 7.5-features and possibly referenced elsewhere
    has_authoritative = any("powershell-7.5-features" in loc for loc in psr_locations)
    log("PSResourceGet dedup", has_authoritative,
        f"Authoritative copy in 7.5-features. Locations: {', '.join(psr_locations)}",
        "dedup")

    # --- TEST 7: Line count check ---
    print(f"\n{'-' * 50}")
    print("TEST 7: Line Count (Conciseness)")
    print("-" * 50)

    line_limits = {
        "powershell-master": 900,
        "powershell-2025-changes": 300,
        "powershell-security": 450,
        "powershell-7.5-features": 800,
        "win11-admin": 750,
        "powershell-shell-detection": 500,
    }

    for skill_name, limit in line_limits.items():
        skill_files = skills.get(skill_name, {})
        total_lines = sum(len(c.splitlines()) for c in skill_files.values())
        within = total_lines <= limit
        log(f"{skill_name} lines ({total_lines}/{limit})", within,
            f"Over limit by {total_lines - limit} lines" if not within else f"Under limit by {limit - total_lines}",
            "conciseness", is_warning=not within)

    # --- SUMMARY ---
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"  PASS:   {passes}")
    print(f"  WARN:   {warnings}")
    print(f"  FAIL:   {errors}")
    print(f"  TOTAL:  {passes + warnings + errors}")

    if errors == 0:
        print(f"\n  All critical checks passed. {warnings} warning(s).")
    else:
        print(f"\n  {errors} critical check(s) failed.")

    # Detailed breakdown by category
    categories = {}
    for r in results:
        if r.category not in categories:
            categories[r.category] = {"pass": 0, "fail": 0, "warn": 0}
        if r.passed:
            categories[r.category]["pass"] += 1
        elif any("WARN" in str(r) for r in [r]):
            categories[r.category]["warn"] += 1
        else:
            categories[r.category]["fail"] += 1

    print(f"\n  By category:")
    for cat, counts in sorted(categories.items()):
        print(f"    {cat:15s} P:{counts['pass']} W:{counts['warn']} F:{counts['fail']}")

    return 1 if errors > 0 else 0

if __name__ == "__main__":
    sys.exit(main())
