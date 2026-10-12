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
5. Use the mandatory [publication helper][publisher] below. It explicitly
   formats intended Scala files, including untracked new files, runs formatting
   verification, the assigned day tests, `sbt test`, and `sbt run`, and checks the
   exact answer. It preserves real process exit codes without shell pipelines.
6. The helper commits only the intended solution/test/sample/Main files,
   rechecks formatting on the committed tree, pushes normally, verifies clean
   HEAD/tracking/live-remote equality, and only then creates or reuses the
   same-part submitter task. Do not create that task or mark solve done earlier.

## Mandatory publication and handoff gate

Prepare a JSON file in the run scratch directory with a `description` containing
upstream task links, cycle start, canonical checkout, sample/edge and independent
cross-check evidence, material paths, and relevant review findings. Do not put
credentials in it. The helper appends the exact answer, full commit hash and
verification receipt; it resolves the submitter from the company API.

Using this skill's base directory from the skill tool response:

```bash
python3 <skill-base>/scripts/aoc_solver_publish.py publish \
  --day NN --part P --answer ANSWER --handoff /path/to/run-scratch/handoff.json
```

`AOC_REPO_DIR` and the normal Paperclip runtime variables identify the checkout,
source task and authenticated API. The helper defaults to the assigned day's
source, test, sample and `Main.scala`. If the sample file does not exist or is not
intended work, supply `--files` with the exact intended subset of those paths.
Only intended files may be dirty or staged. Additional assets require a reviewed
extension of the gate; do not bypass it with manual Git/API commands.

The machine-readable result contains `handoffIssue`, `handoffId`, answer, commit,
and the publication checks. Record it on the source issue, then mark solve done
using `aoc-workflow`. On any nonzero exit, preserve work, report the exact blocker
and owner/action, and stop. A successful push without a confirmed handoff is
unfinished: rerun the helper to reconcile its stable source-task marker. Never
force-push or create a duplicate after an ambiguous API response.

The repository's `project.git = true` excludes untracked files from ordinary
formatting discovery. The helper uses `scalafmtOnly` for explicit paths before
normal formatting and checks the tracked tree again after committing. Running
checks before `git add`, then assuming that covers a later commit, is insufficient.
Do not pipe verification through `tail`/`grep` unless failure propagation is
explicitly preserved; the helper uses direct subprocesses instead.

A downstream agent can independently check an existing computational handoff:

```bash
python3 <skill-base>/scripts/aoc_solver_publish.py verify \
  --day NN --part P --answer ANSWER --commit FULL_SOLUTION_HASH
```

This mode fetches origin, checks committed formatting, executes the assigned day
tests, `sbt test` and `sbt run`, and confirms the exact answer and remote parity.
It does not edit/format source, commit, push, create issues, or change assignments.
Missing or failed evidence blocks submission. Legacy handoffs created before this
gate must pass this independent check; a missing old receipt alone is not failure.

[publisher]: scripts/aoc_solver_publish.py

## Reviewed rejection

Read the exact verdict and review findings. Re-read rules and investigate parsing,
bounds, overflow, and algorithm assumptions. Reproduce the bug, add a meaningful
regression test, fix, and run the verification above. Do not merely change the
expected answer to match a new guess. A repair creates a new submission attempt
and later review for the same part. The CTO authorizes repairs on a later wake-up.

Stop after the submitter handoff. Do not start another part or wake the CTO.
