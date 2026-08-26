#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pyyaml",
# ]
# ///
"""
Quick validation script for skills.

Hard errors (exit 1): spec violations in frontmatter, body size, evals.
Advisory warnings (non-fatal, exit 0): best-practice gaps.
Use --strict to fail on warnings.
"""

import json
import re
import sys
from pathlib import Path

import yaml

MAX_SKILL_NAME_LENGTH = 64
MAX_SKILL_BODY_LINES = 500
MAX_DESCRIPTION_LENGTH = 1024
MAX_COMPATIBILITY_LENGTH = 500

# Advisory (non-fatal) thresholds
ADVISORY_DESCRIPTION_LENGTH = 500
ADVISORY_BODY_LINES = 300
ADVISORY_CODE_FENCE_LINES = 120
ADVISORY_CODE_FENCE_LINES_NO_REFS = 60
ADVISORY_MIN_EVALS = 3
TRIGGER_PATTERNS = (
    "use when",
    "use this skill",
    "activate",
    "when the user",
    "when asked",
    "trigger",
)


def count_code_fence_lines(body):
    """Count body lines inside fenced code blocks."""
    count = 0
    in_fence = False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            count += 1
    return count


def advise_skill(skill_path, frontmatter, description, body, body_lines, evals):
    """Advisory best-practice checks. Returns a list of warning strings."""
    warnings = []

    if "metadata" not in frontmatter:
        warnings.append(
            "No `metadata` block — keep a consistent block on every skill in a catalog (e.g., author, version)"
        )
    if "license" not in frontmatter:
        warnings.append("No `license` field — set it (e.g., MIT) or reference a bundled license file")

    if len(description) > ADVISORY_DESCRIPTION_LENGTH:
        warnings.append(
            f"Description is {len(description)} chars — trim toward what the skill does + when to use it "
            f"(descriptions load at startup for every skill)"
        )
    if not any(p in description.lower() for p in TRIGGER_PATTERNS):
        warnings.append("Description has no 'when to use' trigger language (e.g., 'Use when ...')")

    if body_lines > ADVISORY_BODY_LINES:
        warnings.append(
            f"SKILL.md body is {body_lines} lines — consider moving detailed content to references/ "
            f"(progressive disclosure)"
        )

    fence_lines = count_code_fence_lines(body)
    has_refs = (skill_path / "references").is_dir()
    if fence_lines > ADVISORY_CODE_FENCE_LINES or (
        fence_lines > ADVISORY_CODE_FENCE_LINES_NO_REFS and not has_refs
    ):
        warnings.append(
            f"Body is code-heavy ({fence_lines} code lines) — consider moving detailed examples to references/"
        )

    eval_count = len(evals.get("evals", []))
    if eval_count < ADVISORY_MIN_EVALS:
        warnings.append(f"Only {eval_count} eval case(s) — aim for 3-5 realistic prompts")

    return warnings


def validate_skill(skill_path):
    """Validate a skill. Returns (valid, message, warnings)."""
    skill_path = Path(skill_path)

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found", []

    content = skill_md.read_text()
    if not content.startswith("---"):
        return False, "No YAML frontmatter found", []

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format", []

    frontmatter_text = match.group(1)

    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return False, "Frontmatter must be a YAML dictionary", []
    except yaml.YAMLError as e:
        return False, f"Invalid YAML in frontmatter: {e}", []

    allowed_properties = {
        "name",
        "description",
        "license",
        "compatibility",
        "allowed-tools",
        "metadata",
    }

    unexpected_keys = set(frontmatter.keys()) - allowed_properties
    if unexpected_keys:
        allowed = ", ".join(sorted(allowed_properties))
        unexpected = ", ".join(sorted(unexpected_keys))
        return (
            False,
            f"Unexpected key(s) in SKILL.md frontmatter: {unexpected}. Allowed properties are: {allowed}",
            [],
        )

    if "name" not in frontmatter:
        return False, "Missing 'name' in frontmatter", []
    if "description" not in frontmatter:
        return False, "Missing 'description' in frontmatter", []

    name = frontmatter.get("name", "")
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}", []
    name = name.strip()
    if name:
        if not re.match(r"^[a-z0-9-]+$", name):
            return (
                False,
                f"Name '{name}' should be hyphen-case (lowercase letters, digits, and hyphens only)",
                [],
            )
        if name.startswith("-") or name.endswith("-") or "--" in name:
            return (
                False,
                f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens",
                [],
            )
        if len(name) > MAX_SKILL_NAME_LENGTH:
            return (
                False,
                f"Name is too long ({len(name)} characters). "
                f"Maximum is {MAX_SKILL_NAME_LENGTH} characters.",
                [],
            )

    # Name must match directory name
    dir_name = skill_path.name
    if name and name != dir_name:
        return False, f"Name '{name}' does not match directory name '{dir_name}'", []

    description = frontmatter.get("description", "")
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}", []
    description = description.strip()
    if not description:
        return False, "Description must not be empty", []
    if "<" in description or ">" in description:
        return False, "Description cannot contain angle brackets (< or >)", []
    if len(description) > MAX_DESCRIPTION_LENGTH:
        return (
            False,
            f"Description is too long ({len(description)} characters). Maximum is {MAX_DESCRIPTION_LENGTH} characters.",
            [],
        )

    compatibility = frontmatter.get("compatibility")
    if compatibility is not None:
        if not isinstance(compatibility, str):
            return False, f"Compatibility must be a string, got {type(compatibility).__name__}", []
        compatibility = compatibility.strip()
        if not compatibility:
            return False, "Compatibility must not be empty", []
        if len(compatibility) > MAX_COMPATIBILITY_LENGTH:
            return (
                False,
                f"Compatibility is too long ({len(compatibility)} characters). "
                f"Maximum is {MAX_COMPATIBILITY_LENGTH} characters.",
                [],
            )

    metadata = frontmatter.get("metadata", None)
    if metadata is not None:
        if not isinstance(metadata, dict):
            return (
                False,
                f"Metadata must be a mapping of string keys to string values, got {type(metadata).__name__}",
                [],
            )
        for key, value in metadata.items():
            if not isinstance(key, str) or not isinstance(value, str):
                return (
                    False,
                    f"Metadata must be a mapping of string keys to string values "
                    f"(got key {key!r} -> {value!r})",
                    [],
                )

    # SKILL.md body must be under MAX_SKILL_BODY_LINES
    body = content[match.end():]
    body_lines = len(body.splitlines())
    if body_lines > MAX_SKILL_BODY_LINES:
        return (
            False,
            f"SKILL.md body is {body_lines} lines. Maximum is {MAX_SKILL_BODY_LINES} lines.",
            [],
        )

    # evals/evals.json must exist and parse
    evals_json = skill_path / "evals" / "evals.json"
    if not evals_json.exists():
        return False, "evals/evals.json not found", []
    try:
        evals = json.loads(evals_json.read_text())
    except (json.JSONDecodeError, OSError) as e:
        return False, f"evals/evals.json is not valid JSON: {e}", []
    if not isinstance(evals, dict) or not isinstance(evals.get("evals"), list):
        return False, "evals/evals.json must be a JSON object with an 'evals' array", []

    warnings = advise_skill(skill_path, frontmatter, description, body, body_lines, evals)
    return True, "Skill is valid!", warnings


if __name__ == "__main__":
    argv = sys.argv[1:]
    strict = "--strict" in argv
    args = [a for a in argv if a != "--strict"]
    if len(args) != 1:
        print("Usage: python quick_validate.py <skill_directory> [--strict]")
        sys.exit(1)

    valid, message, warnings = validate_skill(args[0])
    print(message)
    for warning in warnings:
        print(f"  [warn] {warning}")
    if not valid:
        sys.exit(1)
    sys.exit(1 if strict and warnings else 0)
