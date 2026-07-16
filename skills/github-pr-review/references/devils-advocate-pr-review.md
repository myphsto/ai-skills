# Devil's Advocate Checklist for PR Review

Use this list to stress-test every finding before posting. The goal is to eliminate false positives and avoid wasting the author's time.

## Core Questions

1. **Is this real?** Does the diff actually contain the problem, or am I reading a context line, a comment, or a file that was deleted?
2. **Is this new?** Did this code exist before the PR? If the same pattern appears on the base side, it's not a regression introduced by this change.
3. **Is this harmful?** Would a real user actually hit this? Or is it a theoretical edge case that the framework already guards against?
4. **Am I second-guessing a deliberate choice?** Does the author's commit message or PR description explain the trade-off? If so, is my concern still valid given the stated intent?
5. **Do I have the right context?** Am I looking at the PR head SHA, or could a later push have already fixed this?

## Common False Positives

- **Framework safety**: Spring Security, CSRF, CORS, and rate-limiting defaults may already cover what looks like a missing guard.
- **Test-only code**: Code inside test files, mocks, or fixtures is not production risk.
- **Generated code**: Lock files, build outputs, or auto-generated sources should not be reviewed for logic.
- **Refactoring**: If a function was moved but not changed, flagging it as a regression is wrong.
- **Already addressed**: The PR description or a prior comment thread may explain the decision.

## Self-Correction Protocol

Before posting any finding:

1. Re-read the exact diff lines, not the hunk header.
2. Check the PR description for a stated trade-off.
3. Ask: "If I were defending this code, what would I say?"
4. If the answer is strong, downgrade or drop the finding.

## Tone Rules

- Never say "this is wrong" or "this is a bug" as a first line.
- Always lead with the observation, then the concern, then a suggestion.
- If unsure, phrase as a question: "What happens when X?" not "You forgot X."
