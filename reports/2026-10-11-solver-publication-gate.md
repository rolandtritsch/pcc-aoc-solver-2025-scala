# Solver publication gate repair — October 11, 2026

## Observed failure

Day10 part1's solver ([AOC-201][]) ran formatting/testing commands before staging
new source/test files. `.scalafmt.conf` uses `project.git = true`, so the normal
formatting task missed those untracked files. Checks appeared green, but CI
failed after the files were committed. It also created the submitter task before
the push finished. Instructions required verification; the missing protection
was a deterministic publication/handoff sequence.

## Package changes

- `aoc-solve-scala/scripts/aoc_solver_publish.py publish` explicitly formats
  intended Scala paths, including untracked files; runs formatting checks,
  active assigned-day tests, `sbt test`, and `sbt run`; checks the exact answer;
  commits only intended files; rechecks the tracked tree; pushes normally;
  verifies clean HEAD/tracking/live-remote equality; then creates or reconciles
  the same-part submitter task. Its receipt includes the full commit and handoff.
- Subprocess exit codes are preserved directly. Failed/timed-out commands leave
  private diagnostic logs outside the solution/company repos. No failed check
  permits task creation. Foreign dirty work is preserved and blocks publication.
- `verify` independently checks an existing full commit, formatting, active day
  tests, runner answer and remote parity. It does not edit source, commit, push,
  or create tasks. Submitter must pass it before submission/reconciliation,
  including legacy handoffs. Day12's noncomputational finale stays separate.
- Solver/submitter instructions, shared workflow, submission skill, and company
  README now describe the gate. Submitter also has the solve skill attached.
- A stable source-task marker reconciles a lost creation acknowledgement. An
  exact legacy same-part/commit/answer handoff can be reused after publication
  repair. Ambiguous/conflicting handoffs fail closed. Creation remains subject
  to the configured single concurrent solver; API duplicate checks are not an
  atomic server transaction.

## Validation

**13 regression checks passed**, covering untracked-file formatting, failed
build/push, preserved foreign work, wrong answer, empty test evidence, remote
mismatch, handoff-after-publication ordering, acknowledgement recovery,
legacy-handoff adoption/conflict, and last-minute parity failure.

A real isolated Scala checkout reproduced Day10 part1's untracked-file state
from gather commit `7e461c1` plus solution files from `7081947`. Explicit
`scalafmtOnly` followed by normal formatting/checks succeeded; six Day10 tests
and all 119 suite tests passed; `sbt run` returned 417. The shared live checkout
and the user's local Scala checkout were not used for these source edits.

## Live rollout and recovery

Imported only the three changed skills (`aoc-solve-scala`, `aoc-submit`,
`aoc-workflow`), with company/agent/project/issue import disabled. Updated
solver/submitter instruction files and added the helper skill to submitter.
API reads confirmed deployed Markdown/helper/tests match the company package.
Every agent retained its model, environment, command, heartbeat/concurrency
configuration. No agent was paused, cancelled, restarted, or manually invoked.

Follow-up audit found a deployment regression: replacing `aoc-workflow`
recreated its catalog files with mode `0644`, including the CTO's directly
executed `scripts/aoc_cto.py`. From 12:49 UTC the adapter rejected CTO wakes
before inference with `Command is not executable`. The README already requires
restoring executable mode after replacement; the rollout missed that check.
On October 11 at approximately 13:40 UTC, restored that launcher's mode to
`0755` and verified it runs `--version` successfully (OpenCode 1.18.31).
The WatchDog launcher retained `0755` and its recent runs succeeded. Future
skill replacements must verify executable permissions for every affected agent
command, in addition to content and configuration equality.

The next scheduled CTO wake at 13:44:19 UTC started successfully (run
`1a712be7-341a-42fd-9562-f042337d81ff`), cleared the agent's error status to
`running`, entered inference, checked the cycle gate, and inspected the shared
repository. This confirms launcher recovery; the run's subsequent decision and
build outcome were still pending at this verification point.

The original Day10 part2 run `1b336026-aed7-4074-ba95-0c9377a3890b` retained its
start/process/native session and completed normally. Loaded instructions are
not retroactively replaced in an active model session; the downstream gate
protects its handoff, while later solver runs load the new policy.

That protection was observed live: [AOC-210][] invoked `verify` and stopped
before site submission because local solution commit `ae8ed70` had not been
pushed. It recorded the mismatch and assigned publication completion
[AOC-211][] to the solver. That follow-up pushed the existing commit, confirmed
full remote parity, passed the verify gate, and completed at about 12:50 UTC.
AOC-210 resumed afterward. No board edits to live solution files were needed,
and the part2 answer remained 16765. This recovery proves the downstream gate
is being used, rather than merely existing in the package. The resulting
[Day10 part2 CI run][ci] also passed, including formatting and the full workflow.

[AOC-201]: https://paperclip.tritsch.org/AOC/issues/AOC-201
[AOC-210]: https://paperclip.tritsch.org/AOC/issues/AOC-210
[AOC-211]: https://paperclip.tritsch.org/AOC/issues/AOC-211

[ci]: https://github.com/rolandtritsch/scala3-aoc-2025/actions/runs/38140770068
