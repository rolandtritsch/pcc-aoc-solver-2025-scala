# Recursive self-improvement for AoC Solver 2025

Research checked October 10, 2026. Audience: SolutionReviewer and CTO.

## Recommendation

Use a bounded, evidence-driven learning loop: inspect an attempt, explain its
outcome, select a reusable improvement, validate it, commit it in scala3-aoc-2025,
and retrieve it before the next relevant attempt. The reviewer stops after one
improvement pass. Only the CTO authorizes the next puzzle cycle on a later wake-up.

Here, improvement means evolving instructions, reusable skills, scripts, and
verification procedures. It does not mean changing model weights or claiming an
unlimited autonomous recursive improvement process. The recommendation combines
ideas from the papers below; its benefit for this company remains to be measured.

## What the research supports

| Approach | Evidence and mechanism | Useful adaptation here | Limitation |
| --- | --- | --- | --- |
| [Reflexion][] | Agents retain linguistic reflections on feedback in episodic memory rather than updating model weights. Its experiments include coding and other tasks. | Keep linked attempt reports and retrieve relevant lessons before the next solve. | Reflections need accurate feedback; benchmark results do not establish AoC performance. |
| [Self-Refine][] | A model generates, critiques, and refines outputs iteratively without extra training; the authors evaluate several tasks. | Make proposed improvements concrete and test them before adopting them. | Same-model critique is not an independent correctness oracle. |
| [Voyager][] | A Minecraft agent combines environment feedback, an iterative improvement mechanism, and an executable skill library. | Store validated reusable procedures and scripts in a discoverable project library. | Minecraft results do not prove transfer to puzzle solving or Paperclip coordination. |
| [Intrinsic self-correction study][limits] | The authors find that reasoning self-correction without external feedback can fail and sometimes degrade performance. | Require compiler/test results, reproducible cases, and site verdict evidence; keep rollback possible. | This studies specific models/tasks; it is a reason to validate, not a universal claim that critique cannot help. |

The papers support these individual patterns in their evaluated settings. None
proves that combining them is the best AoC workflow. This package chooses that
combination because the company already has observable compiler, test, git,
submission, and review signals.

## What we can establish so far

The following are local observations from the package and adjacent solution
checkout inspected on October 10, 2026, not a live Paperclip audit:

| Observation | What worked or failed | Action |
| --- | --- | --- |
| The checkout contains Day01–Day11 implementations, tests, input resources, and gather/solve commits. | The per-day repository layout and focused history support inspection and reuse. This does not independently prove AoC acceptance. | Preserve the layout and gather acceptance evidence from linked verdicts or the authenticated page. |
| Main prints both parts, but Day01 part2 is a documented zero placeholder and its test is ignored. Other daily suites also contain ignored part2 tests. | Runtime output and a green suite can misrepresent unfinished work if interpreted without source/test inspection. | CTO combines run/test output with actual implementation, active tests, acceptance, and review. |
| The old CTO selected the next day using absent problem files. | File presence cannot establish whether either part is solved, submitted, or reviewed. | Track progress by year/day/part and evidence, not by the next missing statement. |
| The old submitter immediately created next-day or re-solve issues. | Explicit handoffs avoided relying on a passive coordinator, but bypassed a review-and-wait boundary. | Preserve explicit handoffs inside a cycle and make reviewer the final recipient. |
| Gather, solver, and submit skills repeated issue lookup/creation and referenced an unbundled update helper. | Coordination instructions could drift and depend on an unavailable executable. | Use the shared workflow skill now; consider a tested project-local helper after repeated operational evidence. |
| The old package assumed 25 days and part1-only completion. The official [2025 calendar][calendar] ends at Day12. | A historical completion claim or stale season boundary is insufficient for both-part completion. | Order both parts through Day12 and inspect the actual final completion interaction. |

We have not inspected live execution logs, measured costs, or replayed a rejected
submission in this update. Do not infer particular failure causes, model quality,
acceptance rates, or speedups from these observations. A later reviewer should
use actual issue/run evidence to confirm or revise them.

## Review protocol

For each assigned attempt, link the statement, solution commit, tests and command
results, and authoritative verdict. Then answer:

1. **What worked?** Identify a technique or workflow step supported by evidence.
2. **What did not?** Record an observed failure or inefficiency, including an
   accepted solution's discovered defect. Missing evidence is itself a gap.
3. **Why not?** Support the root cause with a reproduced case or execution
   evidence. Label untested explanations as hypotheses.
4. **Can we fix it, and how?** Specify the smallest repair or improvement and its
   acceptance check. Puzzle-answer repair stays with the solver on a later cycle.
5. **Should we distill a skill?** Identify its reusable trigger and a validated
   procedure. Extend an existing skill if it already covers that capability.
6. **Is there repeat work?** Compare earlier reviews before creating another
   abstraction. Name the repeated steps, errors, and their operational cost.
7. **Would a script help?** State deterministic inputs/outputs and a concrete
   fixture or safe validation case. Do not claim deterministic puzzle reasoning;
   automate reliable mechanical steps around it.

## Skill and script adoption

Commit improvements in **scala3-aoc-2025**, with reusable scripts in `scripts/`
and skills in `skills/<name>/SKILL.md`. Keep references next to their skill and
make discovery explicit in the project's `AGENTS.md`. The company package
contains the reviewer operating skill; the project contains skills distilled
from its actual solving work. Do not write these artifacts to personal memory.

Prefer a demonstrated reusable technique over a generic reminder. Examples that
may become skills include boundary-case design, tiny brute-force reference
solvers for checking an optimized algorithm, and choosing exact numeric types
when overflow is reproduced. These are candidates, not findings from this audit.

Potential scripts, to build only when repeated work justifies them:

| Candidate | Minimum useful contract | Validation before adoption |
| --- | --- | --- |
| Progress inspection | Checkout plus recorded evidence → earliest unfinished day/part and reasons; run/test failures remain visible. | Missing days, ignored stubs, legitimate zero answers, historical acceptance, unresolved reviews, build failures, and Day12 finale. |
| Paperclip handoff | Explicit year/day/part/stage/attempt → verified existing or newly created issue. | Mock API cases for blocked work, ambiguous assignee, pagination, timeout reconciliation, and concurrent creation; do not claim atomic deduplication without support. |
| Verdict extraction | Saved response HTML → accepted/rejected/rate-limited/unknown plus original wording. | Fixtures for right/wrong answers, high/low, login pages, wrong level, wait times, and changed markup. No automatic POST retry. |
| Verification summary | Build/run/test outputs plus inspected source/tests → answer and verification evidence. | Nonzero exit codes, unrelated passing tests, ignored placeholders, and sample/real-input separation. |

One review makes one improvement pass, possibly with no code change. Run relevant
checks and representative use cases; do not weaken tests to pass. Record failed
experiments and revert only their own changes. Commit validated improvements
locally with file paths and hashes on the review issue. Pushing needs separate
authorization. Leave unfinished ideas as recommendations, without downstream
issues, wake-ups, or another review of the review.

## Measuring whether it helps

From available issue/run evidence, record first-submission acceptance, rejected
attempts, repeated error categories, solver/test repair cycles, duplicate
handoffs, time spent on mechanical work, and improvement validation outcomes.
Track review overhead as well as savings; include model and puzzle changes when
comparing attempts. Missing timing or billing data is unknown, not zero.

For a script, compare replayable fixtures or the repeated manual procedure. For
a skill, check a later applicable solve and report whether the lesson was used
and whether the targeted error recurred. Changes across different puzzles are
observational evidence, not controlled proof of causality. Remove or revise a
skill that adds overhead or causes regressions, and retain previous commits for
recovery. A no-change review is preferable to unsupported generalizations.

[Reflexion]: https://arxiv.org/abs/2303.11366
[Self-Refine]: https://arxiv.org/abs/2303.17651
[Voyager]: https://arxiv.org/abs/2305.16291
[limits]: https://arxiv.org/abs/2310.01798
[calendar]: https://adventofcode.com/2025
