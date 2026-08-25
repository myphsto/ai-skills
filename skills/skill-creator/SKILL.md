---
name: skill-creator
description: "Guide for creating, updating, evaluating, and scoring effective skills. Use when you want to create a new skill, update an existing skill, or fully evaluate and score a skill. Extends your agent's capabilities with specialized knowledge, workflows, or tool integrations."
license: MIT
compatibility: "Python 3 + pyyaml for helper scripts (via uv or a local venv); manual workflow fallback if unavailable"
metadata:
  author: myphsto
  version: "1.0"
---

# Skill Creator

This skill provides guidance for creating effective skills for agentic CLI tools (Claude Code, Codex, Gemini CLI, OpenCode, etc.).

## About Skills

Skills are modular, self-contained folders that extend your agent's capabilities by providing
specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific
domains or tasks—they transform your agent from a general-purpose assistant into a specialized agent
equipped with procedural knowledge that no model can fully possess.

### What Skills Provide

1. Specialized workflows - Multi-step procedures for specific domains
2. Tool integrations - Instructions for working with specific file formats or APIs
3. Domain expertise - Company-specific knowledge, schemas, business logic
4. Bundled resources - Scripts, references, and assets for complex and repetitive tasks

### Skill Types

Classify the skill before writing — it shapes testing and instruction design:

- **Discipline** — enforces rules agents might rationalize away (TDD, verification). Needs pressure testing.
- **Technique** — teaches a concrete method with steps (data extraction, deployment). Needs eval-driven testing.
- **Pattern** — provides a mental model for problem-solving (error handling strategies). Needs recognition + application testing.
- **Reference** — API docs, syntax guides, tool documentation. Needs retrieval + gap testing.

## Core Principles

### Concise is Key

The context window is a public good. Skills share the context window with everything else your agent needs: system prompt, conversation history, other Skills' metadata, and the actual user request.

**Default assumption: your agent is already very smart.** Only add context the agent doesn't already have. Challenge each piece of information: "Does the agent really need this explanation?" and "Does this paragraph justify its token cost?"

Prefer concise examples over verbose explanations.

### Set Appropriate Degrees of Freedom

Match the level of specificity to the task's fragility and variability:

**High freedom (text-based instructions)**: Use when multiple approaches are valid, decisions depend on context, or heuristics guide the approach.

**Medium freedom (pseudocode or scripts with parameters)**: Use when a preferred pattern exists, some variation is acceptable, or configuration affects behavior.

**Low freedom (specific scripts, few parameters)**: Use when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed.

Think of your agent as exploring a path: a narrow bridge with cliffs needs specific guardrails (low freedom), while an open field allows many routes (high freedom).

### Anatomy of a Skill

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (required)
│   │   ├── name: (required)
│   │   ├── description: (required)
│   │   ├── license: (optional)
│   │   ├── compatibility: (optional)
│   │   ├── metadata: (optional)
│   │   └── allowed-tools: (optional, experimental)
│   └── Markdown instructions (required)
├── evals/
│   └── evals.json (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation intended to be loaded into context as needed
    └── assets/           - Files used in output (templates, icons, fonts, etc.)
```

#### SKILL.md (required)

Every SKILL.md consists of:

- **Frontmatter** (YAML): Required `name` and `description` are the only fields the agent reads to determine when the skill gets used — be clear and comprehensive about what the skill does and when to use it. Optional spec fields: `license`, `compatibility`, `metadata` (covered in Phase 2) and experimental `allowed-tools` — see the [Agent Skills spec](https://agentskills.io/specification).
- **Body** (Markdown): Instructions and guidance for using the skill. Only loaded AFTER the skill triggers (if at all).

#### Evals (required)

Every skill includes `evals/evals.json` with at least 2 test cases:

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "Realistic user prompt with specific details",
      "expected_output": "What success looks like",
      "files": []
    }
  ]
}
```

Test cases are written during the eval phase and used to verify the skill works before shipping.

#### Bundled Resources (optional)

##### Scripts (`scripts/`)

Executable code (Python/Bash/etc.) for tasks that require deterministic reliability or are repeatedly rewritten.

- **When to include**: When the same code is being rewritten repeatedly or deterministic reliability is needed
- **Example**: `scripts/rotate_pdf.py` for PDF rotation tasks
- **Benefits**: Token efficient, deterministic, may be executed without loading into context
- **Note**: Scripts may still need to be read by the agent for patching or environment-specific adjustments

##### References (`references/`)

Documentation and reference material intended to be loaded as needed into context to inform the agent's process and thinking.

- **When to include**: For documentation that the agent should reference while working
- **Examples**: `references/finance.md` for financial schemas, `references/api_docs.md` for API specifications
- **Use cases**: Database schemas, API documentation, domain knowledge, company policies, detailed workflow guides
- **Benefits**: Keeps SKILL.md lean, loaded only when the agent determines it's needed
- **Best practice**: If files are large (>10k words), include grep search patterns in SKILL.md
- **Avoid duplication**: Information should live in either SKILL.md or references files, not both. Prefer references files for detailed information unless it's truly core to the skill—this keeps SKILL.md lean while making information discoverable without hogging the context window. Keep only essential procedural instructions and workflow guidance in SKILL.md; move detailed reference material, schemas, and examples to references files.

##### Assets (`assets/`)

Files not intended to be loaded into context, but rather used within the output the agent produces.

- **When to include**: When the skill needs files that will be used in the final output
- **Examples**: `assets/logo.png` for brand assets, `assets/slides.pptx` for PowerPoint templates, `assets/frontend-template/` for HTML/React boilerplate
- **Use cases**: Templates, images, icons, boilerplate code, fonts, sample documents that get copied or modified
- **Benefits**: Separates output resources from documentation, enables OpenCode to use files without loading them into context

#### What to Not Include in a Skill

A skill should only contain essential files that directly support its functionality. Do NOT create extraneous documentation or auxiliary files, including:

- README.md
- INSTALLATION_GUIDE.md
- QUICK_REFERENCE.md
- CHANGELOG.md
- etc.

The skill should only contain the information needed for an AI agent to do the job at hand. It should not contain auxiliary context about the process that went into creating it, setup and testing procedures, user-facing documentation, etc. Creating additional documentation files just adds clutter and confusion.

### Progressive Disclosure Design Principle

Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by the agent (Unlimited because scripts can be executed without reading into context window)

#### Progressive Disclosure Patterns

Keep SKILL.md body to the essentials and under 500 lines to minimize context bloat. Split content into separate files when approaching this limit. When splitting out content into other files, it is very important to reference them from SKILL.md and describe clearly when to read them, to ensure the reader of the skill knows they exist and when to use them.

**Key principle:** When a skill supports multiple variations, frameworks, or options, keep only the core workflow and selection guidance in SKILL.md. Move variant-specific details (patterns, examples, configuration) into separate reference files.

**Pattern 1: High-level guide with references**

```markdown
# PDF Processing

## Quick start

Extract text with pdfplumber:
[code example]

## Advanced features

- **Form filling**: See [FORMS.md](FORMS.md) for complete guide
- **API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
- **Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
```

The agent loads FORMS.md, REFERENCE.md, or EXAMPLES.md only when needed.

**Pattern 2: Domain-specific organization**

For Skills with multiple domains, organize content by domain to avoid loading irrelevant context:

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

When the user asks about sales metrics, the agent only reads sales.md.

Similarly, for skills supporting multiple frameworks or variants, organize by variant:

```
cloud-deploy/
├── SKILL.md (workflow + provider selection)
└── references/
    ├── aws.md (AWS deployment patterns)
    ├── gcp.md (GCP deployment patterns)
    └── azure.md (Azure deployment patterns)
```

When the user chooses AWS, the agent only reads aws.md.

**Pattern 3: Conditional details**

Show basic content, link to advanced content:

```markdown
# DOCX Processing

## Creating documents

Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents

For simple edits, modify the XML directly.

**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For OOXML details**: See [OOXML.md](OOXML.md)
```

The agent reads REDLINING.md or OOXML.md only when the user needs those features.

**Important guidelines:**

- **Avoid deeply nested references** - Keep references one level deep from SKILL.md. All reference files should link directly from SKILL.md.
- **Structure longer reference files** - For files longer than 100 lines, include a table of contents at the top so the agent can see the full scope when previewing.

## Skill Creation Loop

Skill creation follows a loop, not a linear process. The eval phase is mandatory — every skill is evaluated and scored before shipping.

```
Capture → Draft → Validate → Eval → Improve → (loop) → Ship
```

### Skill Naming

- Use lowercase letters, digits, and hyphens only; normalize user-provided titles to hyphen-case (e.g., "Plan Mode" -> `plan-mode`).
- When generating names, generate a name under 64 characters (letters, digits, hyphens).
- Prefer short, verb-led phrases that describe the action.
- Namespace by tool when it improves clarity or triggering (e.g., `gh-address-comments`, `linear-address-issue`).
- Name the skill folder exactly after the skill name.

### Install Locations

Skills install to `.agents/skills/<name>/` for cross-client portability. Platform-specific locations:

| Platform | Path |
|----------|------|
| Cross-client (recommended) | `.agents/skills/<name>/` or `~/.agents/skills/<name>/` |
| Claude Code | `~/.claude/skills/<name>/` |
| Windsurf | `.windsurf/skills/<name>/` or `~/.codeium/windsurf/skills/<name>/` |
| Codex | `.agents/skills/<name>/` (repo, user, or `/etc/codex/skills/`) |

---

### Phase 1: Capture

Extract or ask for:

1. **What** should this skill enable an agent to do?
2. **When** should it trigger? (user phrases, contexts, symptoms)
3. **What type** is it? (Discipline, Technique, Pattern, Reference — see Skill Types above)
4. **Expected output** — what does success look like?
5. **Where** will it be installed? (see Install Locations)

To create an effective skill, clearly understand concrete examples of how the skill will be used. This understanding can come from either direct user examples or generated examples that are validated with user feedback.

For example, when building an image-editor skill, relevant questions include:

- "What functionality should the image-editor skill support? Editing, rotating, anything else?"
- "Can you give some examples of how this skill would be used?"
- "I can imagine users asking for things like 'Remove the red-eye from this image' or 'Rotate this image'. Are there other ways you imagine this skill being used?"
- "What would a user say that should trigger this skill?"

To avoid overwhelming users, avoid asking too many questions in a single message. Start with the most important questions and follow up as needed for better effectiveness.

Conclude this phase when there is a clear sense of the functionality the skill should support.

To turn concrete examples into a skill plan, analyze each example by:

1. Considering how to execute on the example from scratch
2. Identifying what scripts, references, and assets would be helpful when executing these workflows repeatedly

Example: When building a `pdf-editor` skill to handle queries like "Help me rotate this PDF," the analysis shows:

1. Rotating a PDF requires re-writing the same code each time
2. A `scripts/rotate_pdf.py` script would be helpful to store in the skill

---

### Phase 2: Draft

Initialize the skill directory and write the SKILL.md.

When creating a new skill from scratch, run `init_skill.py`:

```bash
scripts/init_skill.py <skill-name> --path <output-directory> [--resources scripts,references,assets] [--examples]
```

**Dependencies:** The scripts require `pyyaml` — use `uv run scripts/<script>.py ...` if `uv` is available (it handles dependencies), otherwise create a local venv: `python3 -m venv .venv && .venv/bin/pip install -r scripts/requirements.txt`, then run `.venv/bin/python scripts/<script>.py ...`. If neither is available or declined, continue with the manual workflow — the scripts are simple enough to skip.

The script creates the skill directory, SKILL.md template, `evals/evals.json`, and optional resource directories.

#### Writing SKILL.md

Read `references/writing-craft.md` for instruction design principles — how to write instructions agents actually follow.

**Frontmatter:**

- `name`: The skill name (must match directory name)
- `description`: The primary triggering mechanism — describes what the skill does AND when to use it
- `license` (optional): License name or bundled license file reference
- `compatibility` (optional): Environment requirements — include only if the skill needs a specific OS, system package, or network access (max 500 chars)
- `metadata` (optional): String → string map. For a skill catalog, keep a consistent block across all skills (e.g., `author`, `version`)

**YAML safety:** Use double quotes for string-valued frontmatter fields to avoid YAML plain-scalar failures on punctuation:

```yaml
# Fragile: breaks on ": "
description: Use when the user says: "comment on OBT-1234"

# Safe: quoted scalar
description: "Use when the user says: \"comment on OBT-1234\""
```

**Description anti-patterns:**

```yaml
# BAD: workflow leak — agent follows description instead of reading full skill
description: "Use when executing plans - dispatches subagent per task with code review"

# BAD: too vague
description: "Helps with PDFs"

# BAD: first person
description: "I can help you with async tests when they're flaky"

# GOOD: what it does + when to trigger, no workflow
description: "Use when implementing any feature or bugfix, before writing implementation code"

# GOOD: specific symptoms
description: "Use when tests have race conditions, timing dependencies, or pass/fail inconsistently"
```

**Description rules:**
- Start with what the skill does, then include triggering conditions
- Include specific keywords agents would search for (error messages, symptoms, tool names)
- Write in third person (injected into system prompt)
- Be slightly "pushy" — agents tend to undertrigger skills, so cast a wider net
- Never summarize the skill's internal workflow in the description

**Body:** Write instructions for using the skill and its bundled resources. Always use imperative/infinitive form.

**Script design guidelines** (if the skill includes `scripts/`):
- Non-interactive — no TTY prompts, agents run in non-interactive shells
- Good `--help` output — description, flags, examples
- Structured output — JSON/CSV over free-form text
- Helpful error messages — what went wrong, what was expected, what to try
- Idempotent where possible — "create if not exists" over "create and fail on duplicate"
- Data to stdout, diagnostics to stderr
- Pin dependency versions for reproducibility

After drafting, run structural validation immediately:

```bash
scripts/quick_validate.py <path/to/skill-folder>
```

**Dependencies:** Same as Phase 2 (`pyyaml` via `uv` or a local venv) — see above.

Do not proceed to eval until validation passes. Re-run after every frontmatter edit.

---

### Phase 3: Validate

Run `quick_validate.py` to check YAML frontmatter format, required fields, naming rules, line count, name-to-directory match, plus advisory best-practice warnings (non-fatal; `--strict` fails on them). Fix hard errors before proceeding; address warnings as part of Phase 4/5.

---

### Phase 4: Eval

Evaluate the skill inline. This phase is mandatory and produces a scored scorecard.

Read `references/testing-guide.md` for writing good test prompts, assertions, and grading principles.

#### 4a: Contract Compliance

Verify the skill's stated output contract matches what it would actually produce. If the skill declares an output format (e.g., "return exactly 3 failure modes"), simulate a run and confirm compliance.

#### 4b: Description Quality

Check the description against these criteria:
- No workflow leaks (agent shouldn't skip reading the full skill)
- Triggers are comprehensive but not overly broad
- Written in third person
- Includes specific keywords and symptoms
- Score: pass/fail per criterion

#### 4c: Catalog Fit

Read sibling skill descriptions in the install location. Check for:
- Overlapping triggers that could cause confusion
- Missing triggers that belong in another skill
- Clear differentiation between related skills
- Score: list any conflicts and severity

#### 4d: Edge Cases

Test the skill mentally against:
- Trivial input (should the skill skip heavy process?)
- Missing context (should the skill infer or ask?)
- Competing skill triggers (which skill should win?)
- Score: pass/fail per edge case

#### 4e: Test Cases

If the skill type is Discipline, run pressure testing — see `references/testing-guide.md`.

For all other skill types, write eval cases that cover the skill thoroughly. Good evals test:
- **Output contract** — does the skill produce its declared format and counts?
- **Trigger coverage** — test each trigger phrase from the description (whatever they are)
- **Scope rules** — if the skill has scope guidance (e.g., "critique feature, not repo"), test it
- **Edge cases** — trivial input, missing context, competing triggers
- **Decision quality** — if the skill makes judgment calls, test when heavy process triggers vs. skips

**How to write good evals:**
- Make prompts realistic — what a real user would actually say (specific, with file paths, context, casual language)
- Vary phrasing, formality, and detail levels — don't write all prompts the same way
- If the skill makes judgment calls, include at least one eval that tests decision quality rather than output formatting alone
- Require concrete evidence for a PASS — don't give benefit of the doubt

Write 3-5 realistic test prompts in `evals/evals.json`, then run them:
1. Execute each test prompt as if the agent were following the skill
2. Compare output against `expected_output`
3. Note failures and their root cause

#### 4f: Scorecard

Produce an inline scorecard:

```
Eval score: X/10

Dimensions:
- Contract compliance: pass/fail — notes
- Description quality: pass/fail — notes
- Catalog fit: pass/fail — notes
- Edge cases: pass/fail — notes
- Test cases: X/Y passed — notes

Patterns:
- The skill reliably ...
- The remaining weakness is ...

Recommended improvements:
- ...
```

---

### Phase 5: Improve

Address every failing dimension from the eval scorecard:

1. **Generalize from feedback** — fix underlying issues, don't overfit to test cases
2. **Keep the skill lean** — remove instructions that aren't pulling their weight
3. **Explain the why** — reasoning-based instructions ("Do X because Y causes Z") outperform rigid directives
4. **Bundle repeated work** — if every eval run needed the same helper, add it to `scripts/`

After improvements, loop back to Phase 3 (Validate) and Phase 4 (Eval). Repeat until all dimensions pass and the score meets the risk level.

---

### Phase 6: Ship

When the eval scorecard passes, the skill is ready. Copy it to the target install location.

**Final checklist:**
- [ ] `quick_validate.py` exits 0
- [ ] Eval scorecard all dimensions pass
- [ ] SKILL.md body under 500 lines
- [ ] File references one level deep
- [ ] Scripts are non-interactive with good `--help`
- [ ] `evals/evals.json` exists with at least 2 test cases
- [ ] No time-sensitive information
- [ ] Instructions are agent-agnostic (no platform-specific tool names)

## Reference Files

- `references/testing-guide.md` — pressure testing, assertion design, eval-driven testing, grading principles
- `references/writing-craft.md` — instruction design, persuasion principles, anti-patterns, bulletproofing, cross-platform
