---
name: aoc-solve-scala
description: Implement one Advent of Code 2025 day's part-1 in idiomatic Scala 3 inside scala3-aoc-2025, with ScalaDoc, tests, formatting, and incremental git commits
---

You work inside the `scala3-aoc-2025` checkout. Its `CLAUDE.md` is normative for layout and commands; this skill adds the per-day workflow. Reference implementation style: the 2024 solutions (Mill layout) for idiom, but this repo uses the **sbt layout** — do not copy 2024 paths blindly.

## Toolchain

Managed by asdf (`.tool-versions`): Java 25, sbt 2.0.10, Scala 3.9.0. Run `asdf install` if tools are missing. sbt 2 batch commands need `;` separators: `sbt "test"` or `sbt "coverage; test; coverageReport"`.

## Procedure (day NN, zero-padded)

1. Read `problems/DayNNProblem.txt` and the sample example(s) in it. Design the algorithm; note edge cases and the expected sample result(s).
2. Create the sample input file `src/main/resources/inputs/DayNNTest.txt` from the problem statement's example.
3. Implement `src/main/scala/aoc2025/DayNN.scala`, package `aoc2025`, object `DayNN`:
   - `val logger`, `def readFile(filename: String)` parsing via `Source.fromResource` — callers pass paths like `"inputs/DayNN.txt"` (no `./` prefix).
   - `def part1(...): ...` solving part 1. `def part2(...)` as an explicit out-of-scope stub (e.g. `???` or `0`) — document why in ScalaDoc.
   - Full ScalaDoc on object and every method explaining the approach (see `Day00.scala`, the Fibonacci dummy, for the template).
   - Idiomatic Scala 3: indent syntax, immutable data, `require` preconditions, `-Werror`-clean (no unused imports).
4. Write `src/test/scala/aoc2025/DayNNTest.scala` (munit `ScalaCheckSuite`, see `Day00Test.scala`): `readFile` test+real, `part1` test (sample → expected) and real (computed — fill in after running), `part2` test tagged `ignore` asserting the stub.
5. Extend `src/main/scala/aoc2025/Main.scala` `@main def solve()` with the DayNN block.
6. Verify: `sbt test` (all green), `sbt scalafmtCheckAll` (or `sbt scalafmtAll` then re-test). Run the solution: `sbt run` and record the part-1 answer.
7. Commit early and often (`DayNN: parse input`, `DayNN: solve part1`, ...). Never commit red.

## On rejection feedback (re-solve issue from the submitter)

Re-read the problem for misread rules, check off-by-one and boundary handling, verify sample-vs-real parsing differences, add a regression test for the found bug, fix, re-test, recommit, and hand the new answer back by creating a fresh submitter issue exactly as in "Next handoff" above.

## Handoff (mandatory Paperclip disposition — a bare comment is not enough)

Paperclip parks the issue as `blocked` unless the issue *state* is updated,
so the last step is a real disposition write, not just a report. After
committing and verifying green, run (and verify the echoed `status`):

`scripts/paperclip-issue-update.sh --issue-id "$PAPERCLIP_TASK_ID" --status done`
with the comment `"day NN solved"` plus the part-1 answer, the sample result,
and the files changed.

## Next handoff (you create it — the CTO does not watch the board)

Before that disposition write, hand the verified answer directly to the
ProblemSubmitter by creating their issue for the same `NN` (nothing advances
until this issue exists). First list the board and skip creation if a
`todo`/`in_progress` submit issue for that day already exists — reference the
existing id instead; duplicates cause double submissions. Resolve the submitter's agent id by name at runtime
(never hard-code agent UUIDs; they change on re-import):
`SUBMITTER_ID=$(curl -s -H "Authorization: Bearer $PAPERCLIP_API_KEY" "$PAPERCLIP_API_URL/api/companies/$PAPERCLIP_COMPANY_ID/agents" | python3 -c "import json,sys; print([a for a in json.load(sys.stdin) if a.get('name')=='Problem Submitter'][0]['id'])")`
then `curl -s -X POST -H "Authorization: Bearer $PAPERCLIP_API_KEY" -H "X-Paperclip-Run-Id: $PAPERCLIP_RUN_ID" -H "Content-Type: application/json" "$PAPERCLIP_API_URL/api/companies/$PAPERCLIP_COMPANY_ID/issues"` with title `"Submit day NN part 1 answer: <ANSWER>"`, description carrying the answer, the commit hash, the sample result, and the files changed, `"status": "todo"`, and `"assigneeAgentId": "$SUBMITTER_ID"`. Create it as a top-level issue: pass `"parentId": null` explicitly — never nest it as a subtask of your own issue. Verify the echoed issue id, reference it in your disposition comment, and only then mark done.
