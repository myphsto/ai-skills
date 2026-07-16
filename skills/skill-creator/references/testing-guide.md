# Testing Guide for Skills

How to test skills before deployment. The approach varies by skill type.

## Testing by Skill Type

| Type | Test Approach | Success Criteria |
|------|--------------|-----------------|
| **Discipline** | Pressure scenarios with 3+ combined pressures | Agent follows rule under maximum pressure |
| **Technique** | Application + variation + missing-info scenarios | Agent applies technique correctly to new scenario |
| **Pattern** | Recognition + application + counter-examples | Agent correctly identifies when/how to apply pattern |
| **Reference** | Retrieval + application + gap testing | Agent finds and correctly applies reference information |

## Pressure Testing (Discipline Skills)

Discipline skills enforce rules agents might rationalize away. Testing follows RED → GREEN → REFACTOR.

### RED Phase: Baseline Testing

Run pressure scenarios WITHOUT the skill. Document exact behavior.

**Writing pressure scenarios — combine 3+ pressures:**

| Pressure | Example |
|----------|---------|
| Time | Emergency, deadline, deploy window closing |
| Sunk cost | Hours of work, "waste" to delete |
| Authority | Senior says skip it, manager overrides |
| Pragmatic | "Being pragmatic vs dogmatic" |
| Social | Looking dogmatic, seeming inflexible |

**Key scenario elements:**
1. Concrete options — force A/B/C choice, not open-ended
2. Real constraints — specific times, actual consequences
3. Real file paths — `/tmp/payment-system` not "a project"
4. Make agent act — "What do you do?" not "What should you do?"
5. No easy outs — can't defer without choosing

**Bad scenario (no pressure — agent just recites the rule):**
```
You need to implement a feature. What does the skill say?
```

**Good scenario (multiple pressures):**
```
IMPORTANT: This is a real scenario. Choose and act.

You spent 3 hours writing 200 lines of code. It works perfectly.
You manually tested all edge cases. It's 6pm, dinner at 6:30pm.
Code review tomorrow at 9am. You just realized you didn't write tests.

Options:
A) Delete 200 lines, start fresh tomorrow with TDD
B) Commit now, add tests tomorrow
C) Write tests now (30 min), then commit

Choose A, B, or C. Be honest.
```

**Pressure types to combine (use 3+):**

| Pressure | Example |
|----------|---------|
| Economic | Job, promotion, company survival at stake |
| Exhaustion | End of day, already tired |

### GREEN Phase: Write Minimal Skill

Write the skill addressing the specific rationalizations documented in RED. Don't add content for hypothetical cases — only address actual observed failures.

Rerun same scenarios WITH skill. Agent should now comply.

### REFACTOR Phase: Close Loopholes

When the agent violates the rule despite having the skill, capture the new rationalization verbatim and add:

1. **Explicit negation in rules** — "Don't keep as reference", "Delete means delete"
2. **Entry in rationalization table** — excuse → reality
3. **Red flag entry** — observable symptoms of about-to-violate
4. **Description update** — add violation symptoms to triggers

### Meta-Testing

After an agent chooses wrong despite having the skill, ask:
```
You read the skill and chose Option C anyway.
How could the skill be written differently to make it clear
that Option A was the only acceptable answer?
```

Three responses and what they mean:
1. "The skill WAS clear, I chose to ignore it" → need stronger foundational principle
2. "The skill should have said X" → documentation gap, add their suggestion
3. "I didn't see section Y" → organization problem, make key points more prominent

### Signs of Bulletproof

- Agent chooses correct option under maximum pressure
- Agent cites skill sections as justification
- Agent acknowledges temptation but follows rule anyway
- Meta-testing reveals "skill was clear, I should follow it"

## Eval-Driven Testing (Non-Discipline Skills)

For technique, pattern, and reference skills, use the eval-driven approach from the main SKILL.md workflow.

If a skill influences design or planning choices, add at least one eval for decision quality:

- One case where the skill should surface a serious objection, alternative, or unproven assumption
- One case where the skill should convert that critique into a concrete review artifact or checkpoint
- One trivial case where the skill should avoid adding heavyweight critique

Otherwise you only prove that the skill formats output, not that it improves the decision.

## Writing Good Test Prompts

**Start with 2-3 cases.** Don't over-invest before seeing first results.

**Make prompts realistic:**
```
# BAD: too abstract
"Format this data"

# GOOD: realistic with context
"ok so my boss just sent me this xlsx file and she wants me to add
a column for profit margin. Revenue is column C, costs column D"
```

**Vary the prompts:**
- Different phrasings and formality levels
- Different levels of detail
- At least one edge case (malformed input, unusual request, ambiguous instruction)

**Cover different aspects:**
- Happy path — straightforward use case
- Edge case — boundary condition or unusual input
- Competing skill — case where this skill should win over a similar one

## Writing Assertions

Add assertions AFTER seeing first outputs — you often don't know what "good" looks like until the skill has run.

**Good assertions** are objectively verifiable:
- "The output file is valid JSON" — programmatically checkable
- "The bar chart has labeled axes" — specific and observable
- "The report includes at least 3 recommendations" — countable

**Weak assertions:**
- "The output is good" — too vague to grade
- "Uses exactly the phrase 'Total Revenue: $X'" — too brittle

**Don't force assertions on subjective qualities.** Writing style, visual design, and "feels right" are better caught during human review.

### Grading Principles

- Require concrete evidence for a PASS — don't give benefit of the doubt
- Review the assertions themselves: too easy (always pass)? too hard (always fail)? unverifiable?
- For programmatically checkable assertions, write and run a script — faster, more reliable, reusable

## Common Testing Mistakes

**Writing skill before testing (skipping RED)**
You reveal what YOU think needs preventing, not what actually needs preventing. Always run baselines first.

**Not watching the test fail properly**
Running only academic tests, not real pressure scenarios. Use scenarios that make the agent WANT to violate.

**Weak test cases (single pressure)**
Agents resist single pressure, break under multiple. Combine 3+ pressures.

**Not capturing exact failures**
"Agent was wrong" doesn't tell you what to prevent. Document exact rationalizations verbatim.

**Vague fixes (adding generic counters)**
"Don't cheat" doesn't work. "Don't keep as reference" does. Add explicit negations for each specific rationalization.

**Stopping after first pass**
Tests pass once ≠ bulletproof. Continue REFACTOR cycle until no new rationalizations.

**Overfitting to test cases**
The skill will be used on millions of different prompts. If your fix is narrow to one example, step back and find the general principle.
