# AoC Solver 2025

An agent company that works through [Advent of Code 2025](https://adventofcode.com/2025) part-1 puzzles, one day at a time, implementing tested Scala 3 solutions in [scala3-aoc-2025](https://github.com/rolandtritsch/scala3-aoc-2025).

## Org

| Agent | Role | Reports to |
| ----- | ---- | ---------- |
| CTO | Owns the day-loop and pipeline state | — (root) |
| ProblemGatherer | Fetches problem text + personal input | cto |
| ProblemSolver | Principal Scala engineer, implements part-1 | cto |
| ProblemSubmitter | Posts answers, routes verdicts | cto |

Skills: `aoc-gather`, `aoc-solve-scala`, `aoc-submit`.

## Getting started

```bash
npx paperclipai company import ./aoc-solver-2025 --dry-run
npx paperclipai company import ./aoc-solver-2025
```

Secrets (stored in paperclip's vault, never in this package): `OPENROUTER_API_KEY` (all agents), `AOC_SESSION` (gatherer, submitter), optional `GH_TOKEN` (solver, for pushing).

The CTO heartbeat starts paused — drive Day01 manually first, then enable it.
