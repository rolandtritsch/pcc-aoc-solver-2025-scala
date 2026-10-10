---
name: aoc-review
description: Review AoC submission evidence and improve future work through tested, committed project-local skills and scripts, then stop until the CTO wakes
---

Follow `aoc-workflow`. You receive final accepted/rejected attempts from submitter
or historical accepted work from CTO. Read [the research][research] for design
rationale and limits; use the checkout's `AGENTS.md`, applicable local skills,
and prior review findings for the actual review.

## Review and learn

1. Inspect the assigned part's statement, source, tests, git changes/history,
   solver command results, and original submission verdict. For the finale,
   inspect actual site prerequisites and completion evidence instead of
   requiring a computational implementation. Missing required evidence is a
   blocker with an owner and action, not a reason to invent a verdict.
2. Explain **what worked, what did not, why not, whether we can fix it, and how**.
   Separate observed facts, hypotheses, and missing information. An accepted
   answer does not prove every boundary case is correct. A rejected answer is
   not explained until there is evidence for the proposed cause.
3. Compare with previous reviews: identify repeated manual work, repeated errors,
   reusable problem-solving techniques, and existing skills/scripts worth reusing.
   Distill a skill when a validated technique has a clear reusable trigger;
   extend an existing skill rather than duplicating it. Build a script when
   repeated mechanical work benefits from deterministic inputs and outputs.
4. Choose a small evidence-backed improvement and make **one improvement pass**.
   It is valid to make no change if nothing useful is demonstrated. Unfinished
   or speculative work stays in the report for a later CTO decision. Do not
   spawn improvement tasks or repeatedly refine your own review.
5. Put all newly distilled skills and scripts in **scala3-aoc-2025**, never in
   this company package, a personal skill store, or Codex memory:
   - `skills/<descriptive-name>/SKILL.md` with `name`, `description`, clear trigger,
     inputs, procedure, evidence/validation, and stopping conditions.
   - Reusable executables in `scripts/`; supporting skill references may live
     beneath its skill directory. Keep behavior-specific guidance concise.
   - Update project `AGENTS.md` with discovery/use instructions where necessary.
     Do not edit generated guidance if the repository has a source workflow.
6. Validate before adoption. Exercise scripts on fixtures or safe read-only
   inputs, including their relevant failure cases; do not submit answers or
   create live tasks just to test a helper. Validate skill frontmatter, links,
   and a realistic use case. Run relevant repository checks when changes affect
   the build or solutions. Do not weaken assertions, skip tests, or change known
   expected answers to make an improvement appear successful.
7. Inspect the diff and unrelated changes, check whitespace, and **commit** only
   validated improvement files in scala3-aoc-2025 with a focused message such as
   `Review DayNN part P: <improvement>`. Commit does not authorize push. If
   validation fails, revert only your failed improvement, record the failure,
   and retain the existing workflow. Puzzle-answer repairs remain solver work
   authorized by a later CTO wake-up.

## Durable report and stop

Publish the report in the review issue's comment or document before disposition:

- Year/day/part, attempt, verdict, reviewed solution commit, and upstream links.
- What worked; what failed; supported root cause or explicitly labeled hypotheses.
- Can it be fixed, how, and which puzzle repair remains for the CTO/solver.
- Reusable lessons, repeated work, skill/script changes or reasons for no change.
- Improvement file paths, commit hashes, validation evidence, and adoption limits.
- Next CTO recommendation, including any unresolved repair or evidence gap.

Mark the review `done` when its report and any chosen validated improvements are
complete. A rejection review may finish with a recorded pending solver repair;
that part is not complete. Missing required evidence keeps the review `blocked`.
Do not create downstream work, mention/wake CTO, submit answers, enable timers,
or start another part. Stop; only a later manual or timer CTO wake-up proceeds.

[research]: references/recursive-self-improvement.md
