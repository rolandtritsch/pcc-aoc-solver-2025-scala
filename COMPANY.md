---
name: AoC Solver 2025
description: Autonomous Advent of Code 2025 part-1 solver squad. Gathers each day's problem and input, implements idiomatic Scala 3 solutions with tests, submits answers, and advances day by day.
slug: aoc-solver-2025
schema: agentcompanies/v1
version: 0.1.0
license: MIT
authors:
  - name: Roland Tritsch
goals:
  - Solve all part-1 puzzles of Advent of Code 2025
  - Produce clean, idiomatic, ScalaDoc-documented Scala 3 solutions with tests
  - Advance strictly sequentially: next day starts only after the previous part-1 is accepted
---

AoC Solver 2025 is a small agent company that works through [Advent of Code 2025](https://adventofcode.com/2025) one day at a time. The CTO owns the day-loop and pipeline state. The ProblemGatherer fetches the next problem statement and personal input (Advent of Code has no API; fetching uses plain HTTP with the user's session cookie). The ProblemSolver — a Principal Scala Software Engineer — implements the part-1 solution in the [scala3-aoc-2025](https://github.com/rolandtritsch/scala3-aoc-2025) repository following its conventions. The ProblemSubmitter posts the answer and routes wrong answers back to the ProblemSolver.

Work flows as a strict pipeline per day: gather → solve (test green, committed) → submit (accepted) → next day. Part-2 puzzles are out of scope: solutions stub `part2` with an implementation that returns 0.

The CTO heartbeat (periodic "are we done, fetch next?" check) starts **paused** so days can be driven manually first; it is enabled explicitly once the Day01 loop is proven.
