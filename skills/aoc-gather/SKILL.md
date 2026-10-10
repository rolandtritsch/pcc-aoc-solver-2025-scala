---
name: aoc-gather
description: Gather missing AoC 2025 statement text for an assigned part and cache its personal input using authenticated HTTP
---

Follow `aoc-workflow`. Work only on the CTO-authorized day and part in the
`scala3-aoc-2025` checkout. Read its `AGENTS.md` and applicable local skills.

## Gather and validate

1. Check `problems/DayNNProblem.txt` and
   `src/main/resources/inputs/DayNN.txt`. Reuse valid cached input for both parts.
   Reuse cached statement text if it contains the assigned part's actual rules.
   Do not assume a part1 file is sufficient for part2.
2. When statement text is missing, fetch the authenticated page using plain
   HTTP with the `AOC_SESSION` cookie, for example:
   `curl -fsSL --cookie "session=$AOC_SESSION" "https://adventofcode.com/2025/day/$DAY" -o /tmp/aoc-day.html`
   (`DAY` is the unpadded day number). Extract only the puzzle articles using a
   real HTML parser, or `pandoc`/`lynx` followed by inspection. Preserve part1
   when adding newly unlocked part2 to `problems/DayNNProblem.txt`.
3. Validate the day heading and actual assigned-part statement (usually
   `--- Part Two ---` for part2); do not require a `--- Part One ---` heading,
   which the site's first article does not necessarily contain. Reject login,
   error, or truncated pages. If part2 is locked, mark blocked with acceptance
   reconciliation as the unblock action; do not guess its rules.
4. Fetch input only if absent. Use the same cookie at
   `https://adventofcode.com/2025/day/$DAY/input`. Check non-empty content, a final
   newline, and absence of an HTML/login response. If cached input looks corrupt,
   report the blocker rather than overwriting it or repeatedly downloading it.
5. Commit only the changed intended files with a focused `DayNN: gather part P
   material` message. If everything is cached, cite the existing commit and
   avoid an empty commit. Record paths, checks, and commit in the handoff.
6. Create/reuse the same-part solver issue before marking your issue done.
   For Day12's noncomputational finale, hand the authenticated instructions to
   submitter instead. Follow the shared handoff and disposition procedure.

## Site etiquette

Advent of Code uses plain HTTP, not an answer API. No browser automation is
needed. Cache input, avoid duplicate requests, make one request at a time, and
back off in minutes on errors or rate-limit hints. Keep session credentials out
of logs. Never mix personal inputs between accounts or publish them elsewhere.
Stop after the authorized handoff; do not fetch the next part or wake the CTO.
