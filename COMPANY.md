---
name: AoC Solver 2025
description: Advent of Code 2025 Scala 3 solver squad with CTO-controlled part-by-part progress and evidence-driven solution review.
slug: aoc-solver-2025
schema: agentcompanies/v1
version: 0.2.0
license: MIT
authors:
  - name: Roland Tritsch
goals:
  - Complete both parts of Advent of Code 2025 through Day12, including the final completion interaction
  - Produce tested, idiomatic, ScalaDoc-documented Scala 3 solutions
  - Authorize one part per CTO wake-up, in increasing day and part order
  - Review every final verdict and commit validated reusable skills and scripts in scala3-aoc-2025
---

AoC Solver 2025 works through [Advent of Code 2025][aoc] in the
[scala3-aoc-2025][repo] repository. The CTO selects one unfinished part on each
manual or timer wake-up. ProblemGatherer obtains missing material, ProblemSolver
implements the assigned part, and ProblemSubmitter submits its verified answer.
SolutionReviewer examines every accepted or rejected attempt and implements
validated workflow improvements. Review ends the cycle; only a later CTO wake-up
may authorize another part or a repair.

The order is Day01 part1, Day01 part2, Day02 part1, and so on through Day12.
The final day's completion interaction follows the authenticated site rather
than an invented computational answer. Existing verified acceptances are retained.
The CTO heartbeat interval is five minutes; it starts **paused** and is enabled
only explicitly.
Model Tester remains a manually assigned probe outside the puzzle pipeline.

[aoc]: https://adventofcode.com/2025
[repo]: https://github.com/rolandtritsch/scala3-aoc-2025
