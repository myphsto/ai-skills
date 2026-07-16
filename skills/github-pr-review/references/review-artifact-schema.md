# Review Artifact Schema

Every review run produces a JSON artifact. Use this schema for consistency across runs and for CI-based reviewers to deduplicate.

## Top-Level Fields

```json
{
  "pr_number": 42,
  "repo": "owner/repo",
  "head_sha": "abc123...",
  "base_sha": "def456...",
  "review_timestamp": "2025-01-15T10:00:00Z",
  "review_mode": "remote_pr_review | local_pre_push_review | self_created_pr_pre_push | self_created_pr_post_push",
  "findings": [...],
  "summary": "One-paragraph overview of the review"
}
```

## Finding Object

```json
{
  "finding_id": "fnd-001",
  "severity": "critical | high | medium | low | informational",
  "category": "security | correctness | performance | maintainability | test_coverage",
  "title": "Short description of the issue",
  "description": "Detailed explanation with evidence from the diff",
  "file": "path/to/file.ext",
  "line": 42,
  "commit_id": "abc123...",
  "status": "posted_inline | posted_summary | rejected | duplicate | false_positive",
  "duplicate_of": null,
  "marker_sha": "abc123...",
  "marker_id": "fnd-001"
}
```

## Field Notes

- `finding_id`: Content-addressed ID like `fnd-937d2e1046e4` derived from the finding fingerprint (category, file, problem_key). Used in the hidden marker for cross-run deduplication. Compute with `scripts/build_review_packet.py --fingerprint`.
- `severity`: Reflects real-world impact, not personal preference.
- `category`: Helps the author triage findings by type.
- `file` and `line`: Required for inline findings. Omit or set to null for summary findings.
- `status`: Track what happened to each finding. `posted_inline` means an inline comment was posted. `rejected` means the finding was dropped after devil's advocate review.
- `duplicate_of`: If this finding duplicates an existing comment, reference the original finding ID.
- `marker_sha`: The PR head SHA used in the hidden marker for deduplication.
- `marker_id`: The finding ID used in the hidden marker.

## Hidden Marker Format

```html
<!-- github-pr-review:<commit-sha>:<finding-id> -->
```

Example:

```html
<!-- github-pr-review:abc123def456:fnd-001 -->
```

## Artifact Storage

- Write the artifact to a temporary file during the review run.
- Do not commit the artifact to the repository.
- If the user requests a benchmark artifact, save outside the repo with a clear filename.
