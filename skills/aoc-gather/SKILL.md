---
name: aoc-gather
description: Fetch one Advent of Code 2025 day's problem statement and personal input via HTTP with session cookie, observing site etiquette
---

Advent of Code has no API. Everything below uses plain HTTP with the user's login session cookie (`AOC_SESSION` env/secret). This is more reliable than browser automation — do not use Playwright for gathering.

## Procedure (day NN, zero-padded, 01–25)

1. Work in the `scala3-aoc-2025` checkout. Confirm the previous day's part-1 was accepted before fetching (the CTO guarantees this; double-check anyway).
2. Fetch the problem page (public, no auth needed, but send the cookie anyway):
   `curl -fsSL --cookie "session=$AOC_SESSION" "https://adventofcode.com/2025/day/NN" -o /tmp/aoc-NN.html`
3. Convert to text (strip tags; `pandoc -f html -t plain` if available, else `lynx -dump`, else careful `sed`). Write the result to `problems/DayNNProblem.txt`. Sanity-check: file must contain "--- Day NN" and "--- Part One ---"; reject HTML error pages.
4. Fetch the personal input (requires the session cookie):
   `curl -fsSL --cookie "session=$AOC_SESSION" "https://adventofcode.com/2025/day/NN/input" -o src/main/resources/inputs/DayNN.txt`
   Sanity-check: non-empty, ends with newline, not HTML.
5. Commit both files (`git add problems/DayNNProblem.txt src/main/resources/inputs/DayNN.txt && git commit -m "DayNN: gather problem and input"`).

## Etiquette (site rules, non-negotiable)

- Cache aggressively: never download the same input twice; keep everything in the repo.
- One request at a time, back off (minutes, not seconds) on HTTP errors or rate-limit hints.
- Inputs are personal to the session owner — never publish them elsewhere or mix sessions.

## Handoff

Report to the CTO: "day NN gathered" with line counts of both files, or the exact blocker (bad cookie → 400 puzzled page, network error, etc.).
