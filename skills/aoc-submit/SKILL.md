---
name: aoc-submit
description: Submit one Advent of Code 2025 part-1 answer via HTTP POST with session cookie, parse the verdict, respect rate limits
---

Advent of Code has no API. Submit with plain HTTP + the `AOC_SESSION` cookie — do not use Playwright.

## Procedure (day NN, part 1)

1. Take exactly one answer from the CTO assignment (a tested, committed part-1 result). Never invent or tweak answers.
2. POST it:
   `curl -fsSL --cookie "session=$AOC_SESSION" --data "level=1&answer=<ANSWER>" "https://adventofcode.com/2025/day/NN/answer"`
   Save the response HTML to /tmp and extract the verdict text (`<main>` article).
3. Classify the verdict:
   - Accepted ("That's the right answer!") → report success.
   - Wrong / too high / too low → capture the exact wording.
   - Rate-limited ("You gave an answer too recently... please wait") → wait the stated minutes (plus margin) and retry at most twice, then report back blocked.
   - Part 2 unlocked text on a part-1 submit → treat as accepted (part 2 itself is out of scope; do not submit part-2 answers).

## Etiquette

One submission per answer. Never guess repeatedly or script retries — a wrong answer means at least minutes of re-analysis by the ProblemSolver first.

## Handoff (mandatory Paperclip disposition — a bare comment is not enough)

Paperclip parks the issue as `blocked` unless the issue *state* is updated,
so the last step is a real disposition write, not just a report. After
classifying the verdict, run (and verify the echoed `status`):

`scripts/paperclip-issue-update.sh --issue-id "$PAPERCLIP_TASK_ID" --status done`
with the comment `"day NN accepted"`, or `"day NN rejected:
<too high|too low|wrong>"` with the verbatim verdict — the submit task itself
is complete once the verdict is delivered; on rejection the CTO re-tasks the
ProblemSolver from that verdict. If rate-limited with retries exhausted,
use `--status blocked` with `"day NN blocked: <reason>"` and the wait time
as the unblock action. Never invent a new answer yourself.
