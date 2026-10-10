---
name: aoc-solve-scala
description: Implement or repair an assigned AoC 2025 part in Scala 3 with active tests, verified execution, formatting, and focused commits
---

Follow `aoc-workflow` and the `scala3-aoc-2025` checkout's `AGENTS.md` (or its
legacy `CLAUDE.md` if that is the available guidance). Read applicable
project-local skills and the latest relevant review findings. The 2024 repository
is a style reference, not a path template: this repository uses sbt layout.

## Implement exactly the assigned part

1. Read the assigned part's rules in `problems/DayNNProblem.txt`, sample cases,
   and cached personal input. If its rules are missing or locked, report blocked.
   Design the algorithm and identify boundary cases before coding.
2. Implement `part1` or `part2` in `src/main/scala/aoc2025/DayNN.scala`, package
   `aoc2025`. Preserve working code for the other part. Replace the assigned
   placeholder and its out-of-scope ScalaDoc; do not solve an unassigned part.
   Keep parsing via `Source.fromResource` (paths such as `inputs/DayNN.txt`).
   Use idiomatic Scala 3, immutable data where suitable, meaningful preconditions,
   and ScalaDoc explaining the algorithm and complexity.
3. Add sample resources as needed and active tests in
   `src/test/scala/aoc2025/DayNNTest.scala`: official sample expectations,
   independently checked boundaries, and real-input regression assertions.
   Remove the assigned part's ignored-test tag. A real-input expected value
   copied from the implementation is a regression check, not independent proof.
   Preserve previous acceptance evidence and add a defect regression on repairs.
4. Ensure `src/main/scala/aoc2025/Main.scala` executes and labels the assigned
   part as `DayNN - partP: <answer>`. Unimplemented other parts may remain
   placeholders until assigned, but must never be treated as solved.
5. Verify tool versions from `.tool-versions` and `build.sbt`; use the repository's
   asdf setup if missing. Run `sbt scalafmtAll`, `sbt test`,
   `sbt scalafmtCheckAll`, and `sbt run`. All must succeed before committing.
   For multiple sbt commands use one semicolon-separated command string.
   Record the assigned part's exact answer and meaningful test results.
6. Commit only intended files with a focused `DayNN: solve part P` or repair
   message. Never commit a red build. Create/reuse a same-part submitter issue
   with answer, commit, sample/edge results, verification, and upstream links.
   Verify the handoff before marking your issue done.

## Reviewed rejection

Read the exact verdict and review findings. Re-read rules and investigate parsing,
bounds, overflow, and algorithm assumptions. Reproduce the bug, add a meaningful
regression test, fix, and run the verification above. Do not merely change the
expected answer to match a new guess. A repair creates a new submission attempt
and later review for the same part. The CTO authorizes repairs on a later wake-up.

Stop after the submitter handoff. Do not start another part or wake the CTO.
