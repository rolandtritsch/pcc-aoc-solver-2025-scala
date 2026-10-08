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
6. Hand the day directly to the ProblemSolver by creating their issue for the same `NN` (the CTO does not watch the board, so nothing advances until this issue exists). Read the one-line part-1 ask from the problem statement, resolve the solver agent id by name (never hard-code UUIDs), and verify the echoed issue id:
   `SOLVER_ID=$(curl -s -H "Authorization: Bearer $PAPERCLIP_API_KEY" "$PAPERCLIP_API_URL/api/companies/$PAPERCLIP_COMPANY_ID/agents" | python3 -c "import json,sys; print([a for a in json.load(sys.stdin) if a.get('name')=='Problem Solver'][0]['id'])")`
   then `curl -s -X POST -H "Authorization: Bearer $PAPERCLIP_API_KEY" -H "X-Paperclip-Run-Id: $PAPERCLIP_RUN_ID" -H "Content-Type: application/json" "$PAPERCLIP_API_URL/api/companies/$PAPERCLIP_COMPANY_ID/issues"` with title `"Solve day NN part 1: <one-line part-1 ask>"`, description naming both committed files plus the ask, `"status": "todo"`, and `"assigneeAgentId": "$SOLVER_ID"`.

## Etiquette (site rules, non-negotiable)

- Cache aggressively: never download the same input twice; keep everything in the repo.
- One request at a time, back off (minutes, not seconds) on HTTP errors or rate-limit hints.
- Inputs are personal to the session owner — never publish them elsewhere or mix sessions.

## Handoff (mandatory Paperclip disposition — a bare comment is not enough)

Paperclip parks the issue as `blocked` unless the issue *state* is updated,
so the last step is a real disposition write, not just a report. After
committing, run (and verify the echoed `status` in the response):

`scripts/paperclip-issue-update.sh --issue-id "$PAPERCLIP_TASK_ID" --status done`
with the comment `"day NN gathered"` plus line counts of both files — or, on
a blocker, `--status blocked` with the exact blocker (bad cookie → 400
puzzled page, network error, etc.).

Only once the solver issue exists and the disposition write is confirmed is the handoff complete. The ProblemSolver picks the day up from its assigned issue; the CTO follows the pipeline state on the board.
