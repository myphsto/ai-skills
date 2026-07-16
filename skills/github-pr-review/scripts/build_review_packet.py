#!/usr/bin/env python3
"""Build a compact review packet from GitHub PR files JSON.

Input is the JSON array returned by:
  gh api repos/{owner}/{repo}/pulls/{number}/files

The output is intentionally lossy: it preserves file inventory, hunk headers,
lane classification, and high-signal added-line patterns without dumping whole
diffs into the model context.

Default output is a concise text packet for agent review. Use `--json` when a
script needs structured output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


LANE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("tests", re.compile(r"(^|/)(test|tests|spec|__tests__)(/|$)|Test\.(kt|java|py|ts|tsx|js)$", re.I)),
    ("public_api", re.compile(r"(controller|route|endpoint|(^|/)[A-Za-z0-9]+Resource\.(kt|java|py|ts|tsx|js)$)", re.I)),
    ("auth_security_config", re.compile(r"(security|auth|oauth|permission|role|policy|secret|token|cors)", re.I)),
    ("persistence_migration", re.compile(r"(migration|db/|repository|schema|sql|flyway)", re.I)),
    ("business_logic", re.compile(r"(service|manager|handler|processor|validator|client)", re.I)),
    ("docs_churn_generated", re.compile(r"(^|/)(docs?|README|CHANGELOG|AGENTS|package-lock|yarn.lock|pnpm-lock|build.gradle|pom.xml)", re.I)),
]

SIGNAL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("public_endpoint", re.compile(r"@(Get|Post|Put|Delete|Patch)?Mapping|router\.|app\.(get|post|put|delete|patch)", re.I)),
    ("permit_all_or_auth_disabled", re.compile(r"permitAll|csrf\s*\{\s*it\.disable|disable\(\)|anonymous|AllowAll", re.I)),
    ("cache_operation", re.compile(r"cache|redis|evict|clear(Cache|cache)?|delete(Keys|keys|Cache|cache)", re.I)),
    (
        "admin_permission_boundary",
        re.compile(r"admin\w*(permission|role|auth|field|resource)\w*|(permission|role|auth|field|resource)\w*admin\w*", re.I),
    ),
    ("logs_values_or_identifiers", re.compile(r"logger\.(info|warn|error|debug).*?(value|token|tkid|password|secret|key|agent)", re.I)),
    ("broad_exception_swallow", re.compile(r"catch\s*\(.*Exception|except\s+Exception", re.I)),
    ("removed_symbol_or_file", re.compile(r"^deleted file mode|^-.*def |^-.*fun |^-.*class ", re.I)),
    ("quantity_or_count_contract", re.compile(r"count|quantity|qty|size|sumOf|length|total", re.I)),
]

LANE_PRIORITY: dict[str, int] = {
    "auth_security_config": 60,
    "public_api": 55,
    "persistence_migration": 45,
    "business_logic": 40,
    "tests": 20,
    "other": 15,
    "docs_churn_generated": 10,
}

SIGNAL_PRIORITY: dict[str, int] = {
    "permit_all_or_auth_disabled": 100,
    "cache_operation": 95,
    "admin_permission_boundary": 82,
    "public_endpoint": 90,
    "logs_values_or_identifiers": 85,
    "quantity_or_count_contract": 80,
    "removed_symbol_or_file": 75,
    "broad_exception_swallow": 65,
}

PATH_RISK_PATTERNS: list[tuple[int, re.Pattern[str]]] = [
    (35, re.compile(r"controller|route|endpoint", re.I)),
    (30, re.compile(r"security|auth|permission|policy|token|secret|cors", re.I)),
    (25, re.compile(r"cache|redis", re.I)),
    (18, re.compile(r"admin\w*(permission|field|resource)|(permission|field|resource)\w*admin", re.I)),
    (22, re.compile(r"repository|migration|schema|sql|flyway", re.I)),
    (20, re.compile(r"service|manager|handler|processor|validator|client", re.I)),
    (15, re.compile(r"count|quantity|qty|total|status|date|currency|null", re.I)),
]


def read_json(path: str | None) -> Any:
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    return json.load(sys.stdin)


def compute_fingerprint(category: str, file: str | None, problem_key: str) -> str:
    """Compute a stable finding fingerprint from category, file path, and problem key.

    Normalizes the problem key by lowercasing, replacing non-alphanumeric runs with
    spaces, trimming, and collapsing whitespace. Builds compact JSON with keys in
    order: category, file, problem_key. Hashes with SHA-256 and returns the first
    12 lowercase hex characters prefixed with 'fnd-'.
    """
    normalized = re.sub(r"[^a-z0-9]+", " ", problem_key.lower().strip())
    normalized = " ".join(normalized.split())
    payload = json.dumps(
        {"category": category, "file": file, "problem_key": normalized},
        separators=(",", ":"),
        sort_keys=False,
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"fnd-{digest[:12]}"


def classify_lane(path: str) -> str:
    for lane, pattern in LANE_PATTERNS:
        if pattern.search(path):
            return lane
    return "other"


def hunk_headers(patch: str, limit: int) -> list[str]:
    return [line for line in patch.splitlines() if line.startswith("@@")][:limit]


def signal_text_score(text: str) -> int:
    score = 0
    if re.search(r"@\w*Mapping|router\.|app\.(get|post|put|delete|patch)", text, re.I):
        score += 50
    if re.search(r"\bfun\b|\bdef\b|\bclass\b|=>|\{", text):
        score += 20
    if re.search(r"redisTemplate|cacheManager|sumOf|count\(|size|total|quantity|qty", text, re.I):
        score += 20
    if re.search(r"^\s*import\b|^\s*//|^\s*#", text):
        score -= 35
    return score


def signals_for_patch(path: str, patch: str, limit: int) -> list[dict[str, str]]:
    signals: list[dict[str, str]] = []
    for line in patch.splitlines():
        if not line.startswith("+") or line.startswith("+++"):
            continue
        text = line[1:].strip()
        for name, pattern in SIGNAL_PATTERNS:
            if pattern.search(text):
                signals.append({"kind": name, "path": path, "line_excerpt": text[:220]})
                break
    return sorted(
        signals,
        key=lambda signal: (
            SIGNAL_PRIORITY.get(signal["kind"], 0) + signal_text_score(signal["line_excerpt"]),
            signal["line_excerpt"],
        ),
        reverse=True,
    )[:limit]


def path_risk_score(path: str) -> int:
    return sum(score for score, pattern in PATH_RISK_PATTERNS if pattern.search(path))


def source_path_score(path: str) -> int:
    if re.search(r"(^|/)src/(main|app|lib|server|api)(/|$)", path):
        return 20
    if re.search(r"(^|/)(test|tests|__tests__|spec|src/test)(/|$)", path, re.I):
        return -25
    return 0


def file_risk_score(item: dict[str, Any]) -> int:
    changed_lines = item["additions"] + item["deletions"]
    return (
        LANE_PRIORITY.get(item["lane"], 0)
        + path_risk_score(item["path"])
        + source_path_score(item["path"])
        + min(changed_lines, 250) // 10
        + (15 if item["new_file"] or item["deleted_file"] else 0)
    )


def signal_risk_score(signal: dict[str, str]) -> int:
    return (
        SIGNAL_PRIORITY.get(signal["kind"], 0)
        + LANE_PRIORITY.get(classify_lane(signal["path"]), 0)
        + path_risk_score(signal["path"])
        + source_path_score(signal["path"])
        + signal_text_score(signal["line_excerpt"])
    )


def top_by_risk(items: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    return sorted(
        items,
        key=lambda item: (file_risk_score(item), item["additions"] + item["deletions"], item["path"]),
        reverse=True,
    )[:limit]


def top_by_size(items: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    return sorted(items, key=lambda item: item["additions"] + item["deletions"], reverse=True)[:limit]


def file_flags(item: dict[str, Any]) -> str:
    flags = []
    if item["new_file"]:
        flags.append("new")
    if item["renamed_file"]:
        flags.append("renamed")
    if item["deleted_file"]:
        flags.append("deleted")
    return f" ({', '.join(flags)})" if flags else ""


def one_line(text: str, limit: int = 180) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    return compact if len(compact) <= limit else f"{compact[: limit - 1]}..."


def render_text_packet(packet: dict[str, Any]) -> str:
    budget = packet["budget"]
    lines = [
        "review_packet",
        f"- large_pr_mode: {str(packet['large_pr_mode']).lower()}",
        f"- changed_files: {budget['changed_file_count']}",
        f"- changed_line_estimate: {budget['changed_line_estimate']}",
        f"- post_packet_file_fetch_limit: {budget['post_packet_file_fetch_limit']}",
        f"- supporting_files_per_confirmed_finding_limit: {budget['supporting_files_per_confirmed_finding_limit']}",
        f"- lane_counts: {json.dumps(packet['lane_counts'], sort_keys=True)}",
        "",
        "high_risk_files:",
    ]

    for item in packet["high_risk_files"]:
        lines.append(
            f"- {item['path']} [{item['lane']}] +{item['additions']} -{item['deletions']}{file_flags(item)}"
        )
    if not packet["high_risk_files"]:
        lines.append("- none")

    lines.extend(["", "candidate_signals:"])
    for signal in packet["candidate_signals"]:
        lines.append(f"- {signal['kind']} {signal['path']}: {one_line(signal['line_excerpt'])}")
    if not packet["candidate_signals"]:
        lines.append("- none")

    lines.extend(["", "diff_hunks:"])
    for hunk in packet["diff_hunks"]:
        refs = " | ".join(one_line(ref, 100) for ref in hunk["hunk_refs"])
        lines.append(f"- {hunk['path']} [{hunk['lane']}]: {refs}")
    if not packet["diff_hunks"]:
        lines.append("- none")

    lines.extend(["", "largest_files:"])
    for item in packet["largest_files"]:
        lines.append(
            f"- {item['path']} [{item['lane']}] +{item['additions']} -{item['deletions']}{file_flags(item)}"
        )

    lines.extend(["", "omitted_context:"])
    for item in packet["omitted_context"]:
        lines.append(f"- {item}")

    return "\n".join(lines)


def build_packet(
    files: list[dict[str, Any]],
    signal_limit: int,
    hunk_limit: int,
    max_changed_files: int,
    max_high_risk_files: int,
    max_diff_hunks: int,
    max_signals: int,
) -> dict[str, Any]:
    changed_files: list[dict[str, Any]] = []
    diff_hunks: list[dict[str, Any]] = []
    signals: list[dict[str, str]] = []

    for entry in files:
        path = entry.get("filename") or ""
        patch = entry.get("patch") or ""
        additions = entry.get("additions", 0)
        deletions = entry.get("deletions", 0)
        changes = entry.get("changes", 0)
        status = entry.get("status", "modified")
        lane = classify_lane(path)
        changed_files.append(
            {
                "path": path,
                "old_path": entry.get("previous_filename"),
                "new_file": status == "added",
                "renamed_file": status == "renamed",
                "deleted_file": status == "removed",
                "additions": additions,
                "deletions": deletions,
                "lane": lane,
            }
        )
        headers = hunk_headers(patch, hunk_limit)
        if headers:
            diff_hunks.append({"path": path, "lane": lane, "hunk_refs": headers})
        signals.extend(signals_for_patch(path, patch, signal_limit))

    changed_line_estimate = sum(item["additions"] + item["deletions"] for item in changed_files)
    large_pr_mode = len(changed_files) > 30 or changed_line_estimate > 2000
    lane_counts: dict[str, int] = {}
    for item in changed_files:
        lane_counts[item["lane"]] = lane_counts.get(item["lane"], 0) + 1

    high_risk_lanes = {
        "public_api",
        "auth_security_config",
        "persistence_migration",
        "business_logic",
    }
    high_risk_files = [
        item for item in changed_files if item["lane"] in high_risk_lanes or item["additions"] + item["deletions"] >= 100
    ]
    omitted: list[str] = [
        "Full patch bodies omitted after extracting hunk headers and candidate signals."
    ]
    if len(changed_files) > max_changed_files:
        omitted.append(
            f"Changed-file list truncated from {len(changed_files)} to {max_changed_files}; lane_counts retains the full file count."
        )
    if len(high_risk_files) > max_high_risk_files:
        omitted.append(
            f"High-risk file list truncated from {len(high_risk_files)} to {max_high_risk_files} by generic risk ranking."
        )
    if len(diff_hunks) > max_diff_hunks:
        omitted.append(f"Hunk header list truncated from {len(diff_hunks)} to {max_diff_hunks}.")
    if len(signals) > max_signals:
        omitted.append(f"Candidate signals truncated from {len(signals)} to {max_signals} by generic risk ranking.")

    ranked_high_risk_files = top_by_risk(high_risk_files, max_high_risk_files)
    ranked_diff_hunks = sorted(
        diff_hunks,
        key=lambda item: (LANE_PRIORITY.get(item["lane"], 0) + path_risk_score(item["path"]), item["path"]),
        reverse=True,
    )
    ranked_signals = sorted(
        signals,
        key=lambda signal: (signal_risk_score(signal), signal["path"], signal["line_excerpt"]),
        reverse=True,
    )

    return {
        "large_pr_mode": large_pr_mode,
        "budget": {
            "changed_file_count": len(changed_files),
            "changed_line_estimate": changed_line_estimate,
            "post_packet_file_fetch_limit": 5,
            "supporting_files_per_confirmed_finding_limit": 2,
        },
        "lane_counts": lane_counts,
        "changed_files": changed_files[:max_changed_files],
        "largest_files": top_by_size(changed_files, min(max_changed_files, 25)),
        "high_risk_files": ranked_high_risk_files,
        "diff_hunks": ranked_diff_hunks[:max_diff_hunks],
        "candidate_signals": ranked_signals[:max_signals],
        "omitted_context": omitted,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files_json", nargs="?", help="Path to GitHub PR files JSON. Reads stdin when omitted.")
    parser.add_argument("--signal-limit-per-file", type=int, default=2)
    parser.add_argument("--hunk-limit-per-file", type=int, default=4)
    parser.add_argument("--max-changed-files", type=int, default=60)
    parser.add_argument("--max-high-risk-files", type=int, default=20)
    parser.add_argument("--max-diff-hunks", type=int, default=50)
    parser.add_argument("--max-signals", type=int, default=50)
    parser.add_argument("--json", action="store_true", help="Emit structured JSON instead of the default text packet.")
    parser.add_argument(
        "--fingerprint",
        nargs=3,
        metavar=("CATEGORY", "FILE", "PROBLEM_KEY"),
        help="Compute a stable finding fingerprint from category, file path (or 'null'), and problem key. Outputs fnd-<12 hex chars>.",
    )
    args = parser.parse_args()

    if args.fingerprint:
        category, file_arg, problem_key = args.fingerprint
        file_path = None if file_arg.lower() == "null" else file_arg
        sys.stdout.write(compute_fingerprint(category, file_path, problem_key) + "\n")
        return 0

    files = read_json(args.files_json)
    if not isinstance(files, list):
        raise SystemExit("Expected GitHub PR files JSON array")

    packet = build_packet(
        files,
        args.signal_limit_per_file,
        args.hunk_limit_per_file,
        args.max_changed_files,
        args.max_high_risk_files,
        args.max_diff_hunks,
        args.max_signals,
    )
    if args.json:
        json.dump(packet, sys.stdout, separators=(",", ":"))
        sys.stdout.write("\n")
    else:
        sys.stdout.write(render_text_packet(packet))
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
