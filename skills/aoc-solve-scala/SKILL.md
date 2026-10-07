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

## On rejection feedback (via CTO)

Re-read the problem for misread rules, check off-by-one and boundary handling, verify sample-vs-real parsing differences, add a regression test for the found bug, fix, re-test, recommit, hand the new answer back.

## Handoff

Report to the CTO: "day NN solved" with the part-1 answer, sample result, and files changed.
