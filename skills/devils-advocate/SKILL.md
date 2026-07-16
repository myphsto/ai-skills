---
name: devils-advocate
description: "Stress-test arguments, plans, designs, diffs, and repo decisions by exposing logic holes, weak assumptions, and serious opposing positions. Use when the user asks for devil's advocate, hostile critic, hole-poking, argument teardown, challenge this reasoning, counter-argument, or wants the strongest critique of a feature, design, plan, branch, repo, or implementation decision. Also triggers on potato in critique context."
---

# Devil's Advocate

## Overview

Use this skill to pressure-test reasoning. The objective is to break weak logic fast,
not to be supportive.

Critique the argument, not the person.
Target the strongest implied claim, not the easiest sentence to attack.
When a broader workflow asks for a **Critical Review**, this skill can supply
the critique section as long as the output stays proportional and decision-focused.

## Required Output Contract

Return exactly these three sections, in this order:

1. `Three Failure Modes`
2. `Two Unproven Assumptions`
3. `One Unaddressed Counter-Argument`

Use numbered bullets under each section.

### Section Requirements

`Three Failure Modes`
- Exactly 3 items.
- Each item states: what fails, why it fails, and the trigger condition.

`Two Unproven Assumptions`
- Exactly 2 items.
- Each item names the assumption and the missing evidence.

`One Unaddressed Counter-Argument`
- Exactly 1 item.
- Must be a credible opposing position that materially weakens the argument.

## Critique Method

1. Extract the core claim in one sentence.
   - If the user gave a repo, branch, diff, feature, or design without an explicit
     claim, infer the strongest plausible claim behind it and label the inference.
   - For code or branch review, prefer the feature's implied claim ("this change
     is a sound way to solve X") over line-by-line nitpicks.
2. Identify dependencies: evidence, constraints, incentives, timelines, and external systems.
3. Stress-test for:
   - weak causality,
   - base-rate neglect,
   - adversarial behavior,
   - scale and worst-case breakdowns,
   - second-order effects.
4. Stay proportional to scope.
   - Trivial change: attack whether the process or claimed impact is inflated.
   - Non-trivial change: attack correctness, rollout safety, incentives, and
     decision quality.
   - Do not manufacture architectural criticism for a one-line copy fix.
5. Emit only the required output contract.

## Tone and Boundaries

- Be blunt, direct, and specific.
- No praise, hedging, or comfort language.
- No insults, slurs, or identity-based attacks.
- No solution proposals unless user asks separately.
- No filler objections. Every item should be capable of materially changing the
  user's confidence or decision.

## Scope Rules

- If the user asks about a **repo or branch**, critique the strongest implied
  thesis of the recent work, not the entire repository unless asked.
- If the user asks about a **design or plan**, critique the chosen approach and
  the reasoning behind approval.
- If the user asks about **implementation code**, critique the assumption that
  this code is a sound or sufficient realization of the intended behavior.
- If context is thin, infer narrowly and label the inference instead of broadening
  the target.

## Output Template

```text
Three Failure Modes
1. <failure mode>
2. <failure mode>
3. <failure mode>

Two Unproven Assumptions
1. <assumption>
2. <assumption>

One Unaddressed Counter-Argument
1. <counter-argument>
```

## Edge Cases

- If the user provides only a topic, infer a plausible claim, label the inference,
  then run the contract.
- If the user explicitly requests different counts, follow the user-specified counts
  while keeping the same section names.
- If the topic is trivial, keep the critique proportional. The point is to find
  the strongest real objection, not to simulate depth.

