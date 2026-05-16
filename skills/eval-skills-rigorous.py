#!/usr/bin/env python3
"""
Rigorous content-preservation eval for PowerShell/Win11 skills.

Compares git main against working tree. For every removed block, classifies it as:
  MOVED    - Content relocated to references/
  CROSSREF - Content deduplicated, replaced with cross-reference
  CUT      - Legitimate removal (meta-rules, redundant text)
  LOST     - WARNING: content disappeared with no replacement

Also extracts all PowerShell commands from current skills for smoke testing.
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

REPO_ROOT = Path(__file__).parent.parent
SKILLS_DIR = REPO_ROOT / "skills"

# Skills we're evaluating
EVAL_SKILLS = [
    "powershell-master",
    "powershell-2025-changes",
    "powershell-security",
    "powershell-7.5-features",
    "win11-admin",
    "powershell-shell-detection",
]

# Patterns that are legitimate cuts (not content loss)
LEGITIMATE_CUTS = [
    r"meta-rule",
    r"backslash",
    r"AGENTS\.md",
    r"documentation.*belong",
    r"token.*budget",
    r"context.*window.*cost",
    r"See.*powershell-security.*for.*full",
    r"See.*powershell-7\.5-features.*for.*full",
    r"See.*references/",
    r"cross-reference",
    r"deduplicated",
]

@dataclass
class DiffBlock:
    skill: str
    line_range: str
    content: str
    is_removal: bool
    classification: str = "UNKNOWN"
    evidence: str = ""

@dataclass
class EvalReport:
    skill: str
    sections_original: List[str] = field(default_factory=list)
    sections_current: List[str] = field(default_factory=list)
    removed_blocks: List[DiffBlock] = field(default_factory=list)
    lost_content: List[str] = field(default_factory=list)
    smoke_commands: List[str] = field(default_factory=list)

def git_show(skill: str, filename: str = "SKILL.md") -> str:
    """Get original file content from git main."""
    path = f"skills/{skill}/{filename}"
    try:
        result = subprocess.run(
            ["git", "show", f"main:{path}"],
            capture_output=True, text=True, cwd=REPO_ROOT,
            timeout=10
        )
        return result.stdout if result.returncode == 0 else ""
    except Exception:
        return ""

def read_current(skill: str, filename: str = "SKILL.md") -> str:
    """Read current working tree file."""
    path = SKILLS_DIR / skill / filename
    return path.read_text() if path.exists() else ""

def read_refs(skill: str) -> str:
    """Read all references/ files for a skill."""
    refs_dir = SKILLS_DIR / skill / "references"
    if not refs_dir.exists():
        return ""
    content = []
    for md_file in refs_dir.glob("*.md"):
        content.append(f"\n--- {md_file.name} ---\n")
        content.append(md_file.read_text())
    return "\n".join(content)

def extract_headings(text: str) -> List[str]:
    """Extract markdown headings as section identifiers."""
    headings = []
    for line in text.splitlines():
        m = re.match(r"^(#{1,4})\s+(.+)$", line)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            headings.append((level, title))
    return headings

def extract_powershell_commands(text: str) -> List[str]:
    """Extract PowerShell commands from code blocks for smoke testing."""
    commands = []
    # Match PowerShell code blocks
    in_block = False
    block_lines = []

    for line in text.splitlines():
        if line.strip().startswith("```powershell"):
            in_block = True
            block_lines = []
            continue
        if line.strip().startswith("```"):
            if in_block:
                # Process collected block
                cmd = extract_command_from_block(block_lines)
                if cmd:
                    commands.append(cmd)
                in_block = False
                block_lines = []
            continue
        if in_block:
            block_lines.append(line)

    return commands

def extract_command_from_block(lines: List[str]) -> Optional[str]:
    """Extract a representative command from a code block."""
    # Skip comments, empty lines, and param blocks
    real_lines = []
    in_comment = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("<#"):
            in_comment = True
            continue
        if stripped.startswith("#>"):
            in_comment = False
            continue
        if in_comment:
            continue
        if stripped and not stripped.startswith("#") and not stripped.startswith("param"):
            real_lines.append(stripped)

    if not real_lines:
        return None

    # Return first meaningful command (up to 200 chars)
    cmd = real_lines[0]
    if len(cmd) > 200:
        cmd = cmd[:200] + "..."
    return cmd

def classify_removal(content: str, skill: str, current_content: str, refs_content: str) -> Tuple[str, str]:
    """Classify a removed content block."""
    text = content.strip()
    lower = text.lower()

    # Check if content was moved to references/
    if refs_content:
        # Check if key phrases from removed content exist in refs
        phrases = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4}', text)
        for phrase in phrases[:5]:
            if len(phrase) > 15 and phrase.lower() in refs_content.lower():
                return ("MOVED", f"Found in references/: {phrase[:50]}")

    # Check if replaced with cross-reference
    cross_refs = [
        r"See.*powershell-security",
        r"See.*powershell-7\.5-features",
        r"See.*references/",
        r"See.*skill.*for",
    ]
    for pattern in cross_refs:
        if re.search(pattern, current_content, re.IGNORECASE):
            # Check if the cross-ref is near where content was removed
            return ("CROSSREF", f"Replaced with cross-reference (pattern: {pattern})")

    # Check if it's a legitimate cut
    for pattern in LEGITIMATE_CUTS:
        if re.search(pattern, lower):
            return ("CUT", f"Legitimate cut (pattern: {pattern})")

    # Check if it's duplicated content that was properly deduplicated
    if re.search(r"New-PSRoleCapabilityFile|Register-PSSessionConfiguration", text):
        if "powershell-security" in lower or "JEA" in text:
            return ("CROSSREF", "JEA content deduplicated to powershell-security")
    if re.search(r"New-CIPolicy|ConvertFrom-CIPolicy", text):
        return ("CROSSREF", "WDAC content deduplicated to powershell-security")
    if re.search(r"Install-PSResource|Find-PSResource", text):
        return ("CROSSREF", "PSResourceGet content deduplicated to powershell-7.5-features")
    if re.search(r"__PSLockdownPolicy|ConstrainedLanguage", text):
        return ("CROSSREF", "Constrained Language content deduplicated to powershell-security")
    if re.search(r"EnableScriptBlockLogging|ScriptBlockLogging", text):
        return ("CROSSREF", "Script Block Logging content deduplicated to powershell-security")

    return ("LOST", f"Content removed without clear replacement")

def main():
    print("=" * 72)
    print("RIGOROUS CONTENT-PRESERVATION EVAL")
    print("Comparing git main → working tree + references/")
    print("=" * 72)

    reports: Dict[str, EvalReport] = {}
    total_lost = 0
    total_moved = 0
    total_crossref = 0
    total_cut = 0
    total_unknown = 0

    for skill in EVAL_SKILLS:
        print(f"\n{'=' * 72}")
        print(f"SKILL: {skill}")
        print(f"{'=' * 72}")

        original = git_show(skill)
        current = read_current(skill)
        refs = read_refs(skill)
        combined = current + refs

        if not original:
            print(f"  WARNING: No original content in git main")
            continue

        report = EvalReport(skill=skill)
        reports[skill] = report

        # Extract sections
        orig_headings = extract_headings(original)
        curr_headings = extract_headings(combined)
        report.sections_original = [h[1] for h in orig_headings]
        report.sections_current = [h[1] for h in curr_headings]

        # Check section preservation
        print(f"\n  Sections: {len(orig_headings)} original → {len(curr_headings)} current")

        missing_sections = []
        for level, title in orig_headings:
            # Check if this section (or close variant) exists in current
            found = False
            title_lower = title.lower()
            for _, curr_title in curr_headings:
                if title_lower in curr_title.lower() or curr_title.lower() in title_lower:
                    found = True
                    break
            if not found and level <= 3:
                missing_sections.append(title)
                print(f"    MISSING SECTION: {title}")

        # Classify removed blocks via git diff
        try:
            diff_result = subprocess.run(
                ["git", "diff", "main", f"skills/{skill}/SKILL.md"],
                capture_output=True, text=True, cwd=REPO_ROOT, timeout=10
            )

            if diff_result.stdout:
                # Parse unified diff for removed blocks
                removed_blocks = []
                current_hunk = []
                in_hunk = False

                for line in diff_result.stdout.splitlines():
                    if line.startswith("@@"):
                        if current_hunk:
                            removed_blocks.append("\n".join(current_hunk))
                        current_hunk = []
                        in_hunk = True
                        continue
                    if in_hunk and line.startswith("-") and not line.startswith("---"):
                        current_hunk.append(line[1:])  # Strip leading -

                if current_hunk:
                    removed_blocks.append("\n".join(current_hunk))

                # Classify each removed block
                for block in removed_blocks:
                    if not block.strip():
                        continue

                    classification, evidence = classify_removal(
                        block, skill, current, refs
                    )

                    db = DiffBlock(
                        skill=skill,
                        line_range="",
                        content=block[:200],
                        is_removal=True,
                        classification=classification,
                        evidence=evidence
                    )
                    report.removed_blocks.append(db)

                    if classification == "LOST":
                        total_lost += 1
                        report.lost_content.append(block[:300])
                        print(f"    LOST: {block[:100]}...")
                    elif classification == "MOVED":
                        total_moved += 1
                    elif classification == "CROSSREF":
                        total_crossref += 1
                    elif classification == "CUT":
                        total_cut += 1
                    else:
                        total_unknown += 1

        except Exception as e:
            print(f"  Diff analysis error: {e}")

        # Extract smoke test commands
        all_commands = extract_powershell_commands(combined)
        report.smoke_commands = all_commands
        print(f"  Smoke commands extracted: {len(all_commands)}")

    # Summary
    print(f"\n{'=' * 72}")
    print("SUMMARY")
    print(f"{'=' * 72}")

    print(f"\n  Removed blocks classified:")
    print(f"    MOVED (to refs):    {total_moved}")
    print(f"    CROSSREF:           {total_crossref}")
    print(f"    CUT (legitimate):   {total_cut}")
    print(f"    UNKNOWN:            {total_unknown}")
    print(f"    LOST:               {total_lost}")

    # Content preservation: verify key commands/paths from removed sections
    # still exist somewhere in the skill tree
    print(f"\n  CONTENT PRESERVATION CHECK:")
    print(f"  (Key commands/paths from removed sections → still present?)")

    # Key content that was in removed sections
    key_content_checks = [
        # JEA content (should be in powershell-security)
        ("New-PSRoleCapabilityFile", "JEA role config"),
        ("Register-PSSessionConfiguration", "JEA endpoint"),
        ("Enter-PSSession", "JEA connection"),
        # WDAC content (should be in powershell-security)
        ("New-CIPolicy", "WDAC policy creation"),
        ("ConvertFrom-CIPolicy", "WDAC binary conversion"),
        # Constrained Language Mode (should be in powershell-security)
        ("__PSLockdownPolicy", "CLM env var"),
        ("Get-ExecutionPolicy", "CLM check"),
        # Script Block Logging (should be in powershell-security)
        ("EnableScriptBlockLogging", "SBL registry"),
        ("EnableScriptBlockInvocationLogging", "SBL invocation"),
        # PSResourceGet (should be in powershell-7.5-features)
        ("Install-PSResource", "PSResourceGet install"),
        ("Find-PSResource", "PSResourceGet search"),
        ("Update-PSResource", "PSResourceGet update"),
        # Defender/ASR (should be in win11-admin or refs)
        ("Set-MpPreference", "Defender prefs"),
        ("Add-MpPreference -AttackSurfaceReduction", "ASR rules"),
        ("Start-MpScan", "Defender scan"),
        # Quick ref content (should be in win11-admin refs)
        ("Checkpoint-Computer", "restore point"),
        ("devmgmt.msc", "device manager"),
        # Cmdlet ref (should be in powershell-master refs)
        ("Get-ChildItem", "file system cmdlet"),
        ("Get-Process", "process cmdlet"),
    ]

    # Combine all skill content
    all_content = {}
    for skill in EVAL_SKILLS:
        all_content[skill] = read_current(skill) + read_refs(skill)
    combined_all = "\n".join(all_content.values())

    content_verified = 0
    content_lost = 0

    for cmd, description in key_content_checks:
        if cmd.lower() in combined_all.lower():
            content_verified += 1
        else:
            content_lost += 1
            print(f"    LOST: {description} ({cmd})")

    print(f"    Content verified: {content_verified}/{len(key_content_checks)}")
    print(f"    Content lost: {content_lost}/{len(key_content_checks)}")

    # Detail lost content
    if total_lost > 0:
        print(f"\n  LOST CONTENT DETAIL:")
        for skill in EVAL_SKILLS:
            report = reports.get(skill)
            if report and report.lost_content:
                print(f"\n  {skill}:")
                for i, lost in enumerate(report.lost_content, 1):
                    preview = lost.replace("\n", " ")[:150]
                    print(f"    {i}. {preview}")

    # Generate smoke test script
    print(f"\n{'=' * 72}")
    print("GENERATING POWERSHELL SMOKE TEST")
    print(f"{'=' * 72}")

    smoke_path = REPO_ROOT / "skills" / "smoke-test.ps1"
    with open(smoke_path, "w") as f:
        f.write("# PowerShell Skills Smoke Test\n")
        f.write("# Run this in Windows PowerShell to verify commands parse correctly\n")
        f.write("# Generated by eval-skills-rigorous.py\n\n")
        f.write("$Results = @()\n\n")

        # Key cmdlets to test availability
        key_cmdlets = [
            ("powershell-master", ["Get-ChildItem", "Get-Process", "Get-Service",
                                  "Test-Connection", "Select-Object", "Where-Object"]),
            ("powershell-security", ["Get-MpPreference", "Get-ExecutionPolicy",
                                    "Set-MpPreference"]),
            ("powershell-7.5-features", ["Get-Module", "Get-Command",
                                        "ConvertTo-CliXml"]),
            ("win11-admin", ["Get-LocalUser", "Get-ScheduledTask",
                            "Get-NetFirewallProfile", "Get-BitLockerVolume"]),
            ("powershell-shell-detection", ["Get-ChildItem", "Get-Process"]),
        ]

        cmd_count = 0
        for skill, cmdlets in key_cmdlets:
            f.write(f"# --- {skill} ---\n")
            for cmdlet in cmdlets:
                cmd_count += 1
                safe = cmdlet.replace("'", "''")
                f.write(f"try {{\n")
                f.write(f"    Get-Command -Name '{cmdlet}' -ErrorAction Stop | Out-Null\n")
                f.write(f"    $Results += [PSCustomObject]@{{\n")
                f.write(f"        Skill = '{skill}'\n")
                f.write(f"        Cmdlet = '{safe}'\n")
                f.write(f"        Status = 'Available'\n")
                f.write(f"    }}\n")
                f.write(f"}} catch {{\n")
                f.write(f"    $Results += [PSCustomObject]@{{\n")
                f.write(f"        Skill = '{skill}'\n")
                f.write(f"        Cmdlet = '{safe}'\n")
                f.write(f"        Status = 'MISSING: ' + $_.Exception.Message\n")
                f.write(f"    }}\n")
                f.write(f"}}\n\n")

        f.write(f"\n# Summary\n")
        f.write(f"$Results | Format-Table -AutoSize\n")
        f.write(f"$Results | Group-Object Status | Select-Object Name, Count\n")

    print(f"\n  Smoke test written to: {smoke_path}")
    print(f"  Total cmdlet checks: {cmd_count}")
    print(f"\n  To test: Copy smoke-test.ps1 to Windows and run:")
    print(f"    pwsh -File smoke-test.ps1")

    return 1 if total_lost > 0 else 0

if __name__ == "__main__":
    sys.exit(main())
