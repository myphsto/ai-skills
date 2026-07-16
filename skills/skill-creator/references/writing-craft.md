# Writing Craft for Skills

Deep guide on writing skill instructions that agents follow reliably. Read this when drafting or improving a skill.

## Core Philosophy

**The agent is already very smart.** Only add context it doesn't already have. For every paragraph, ask: "Does this justify its token cost?"

**Explain the why.** LLMs have good theory of mind. When given reasoning, they go beyond rote instructions and make better decisions in novel situations:

```markdown
# Weak: rigid directive
ALWAYS validate XML after every edit. NEVER skip this step.

# Strong: reasoning-based
Validate XML after each edit because a single malformed tag cascades into
silent corruption when the document is repacked. The 2-second validation
check prevents 20 minutes of debugging later.
```

**Write for a million invocations.** Instructions must generalize — don't overfit to your test cases.

## Persuasion Principles

LLMs respond to the same persuasion principles as humans. Research (Meincke et al., 2025, N=28,000) found persuasion techniques more than doubled compliance rates (33% → 72%).

| Skill Type | Use | Avoid |
|------------|-----|-------|
| Discipline-enforcing | Authority + Commitment + Social Proof | Liking, Reciprocity |
| Technique/guidance | Moderate Authority + Unity | Heavy authority |
| Collaborative | Unity + Commitment | Authority, Liking |
| Reference | Clarity only | All persuasion |

**Authority** — Imperative language ("YOU MUST", "Never"). Use for discipline skills and safety-critical practices.

**Commitment** — Require announcements ("Announce skill usage"), force explicit choices ("Choose A, B, or C"), use tracking (checklists). Ensures skills are actually followed.

**Scarcity** — Time-bound requirements ("Before proceeding"), sequential dependencies ("Immediately after X"). Prevents "I'll do it later."

**Social Proof** — Universal patterns ("Every time"), failure modes ("X without Y = failure"). Establishes norms.

**Unity** — Collaborative language ("our codebase", "we're colleagues"). Use for non-hierarchical collaborative workflows.

**Ethical test:** Would this technique serve the user's genuine interests if they fully understood it? If not, don't use it.

## Anti-Patterns

**Narrative storytelling** — Extract the reusable technique, not the story.
```
# BAD: "In session 2025-10-03, we found empty projectDir caused..."
# GOOD: Extract the reusable technique, not the story
```

**Multi-language dilution** — One excellent example beats five mediocre ones.
```
# BAD: example-js.js, example-py.py, example-go.go
# GOOD: One excellent example in the most relevant language
```

**Code in flowcharts** — Use code blocks for code, flowcharts for decisions only.

**Over-explaining common knowledge** — Assume the agent knows basics.
```
# BAD: "PDF (Portable Document Format) files are a common format..."
# GOOD: "Use pdfplumber for text extraction:"
```

**Too many options** — Don't present every possible tool.
```
# BAD: "You can use pypdf, or pdfplumber, or PyMuPDF, or pdf2image..."
# GOOD: "Use pdfplumber for text extraction. For scanned PDFs requiring OCR, use pdf2image."
```

## Bulletproofing Discipline Skills

Skills that enforce rules need extra hardening because agents will rationalize away the rules under pressure.

**Close every loophole explicitly:**
```markdown
Write code before test? Delete it. Start over.

**No exceptions:**
- Don't keep it as "reference"
- Don't "adapt" it while writing tests
- Don't look at it
- Delete means delete
```

**Add a foundational principle early:**
```markdown
**Violating the letter of the rules is violating the spirit of the rules.**
```
This cuts off the entire class of "I'm following the spirit" rationalizations.

**Build a rationalization table** — capture every excuse from baseline testing:
```markdown
| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after" | Tests after = "what does this do?" not "what should this do?" |
```

**Create a red flags list:**
```markdown
## Red Flags - STOP and Start Over
- Code before test
- "I already manually tested it"
- "This is different because..."
**All of these mean: Delete code. Start over.**
```

## Cross-Platform Compatibility

**Instructions should be agent-agnostic:**
- Say "run the script" not "use the Bash tool to run"
- Say "read the reference file" not "use the Read tool on"
- If a skill requires a specific platform, declare it in the `compatibility` field

**Account for different execution environments:**
- Codex sandboxes have network off by default and workspace-write-only permissions
- Windsurf Cascade has a 20 tool-call limit per prompt
- Not all environments support subagents or parallel execution

**Script portability:**
- Use `uv run` (Python PEP 723) or `npx` (Node) for self-contained scripts
- Don't assume specific shells beyond basic POSIX sh/bash
- Don't assume network access — document it in `compatibility` if required
