---
name: aoc-submit
description: Submit or reconcile an assigned AoC 2025 part, preserve authoritative verdict evidence, and hand final verdicts to SolutionReviewer
---

Follow `aoc-workflow` and applicable project-local skills. Use plain HTTP with
`AOC_SESSION`; never invent or change the tested committed answer.

## Submit or reconcile

1. Verify assignment year, day, part, answer, commit, and test evidence. Inspect
   prior submission issues for the same answer/part. Preserve verified accepted
   answers and never repost known wrong answers unchanged. Reconcile uncertain
   or historical acceptance from the authenticated puzzle page first. Record
   the matching accepted answer and part if present; absence is not rejection.
2. For an authorized new answer, submit exactly the assigned level (`PART` is
   `1` or `2`, `DAY` is unpadded):
   `curl -fsSL --cookie "session=$AOC_SESSION" --data-urlencode "level=$PART" --data-urlencode "answer=$ANSWER" "https://adventofcode.com/2025/day/$DAY/answer" -o /tmp/aoc-verdict.html`
   Save the response and extract the article with an HTML parser. Preserve
   verbatim verdict text on the issue, not just a temporary response path.
3. Classify authoritative acceptance ("That's the right answer!") or rejection
   (wrong, too high, too low). Unlock links alone are insufficient. "Already
   completed"/"wrong level", login pages, network failures, and unrecognized
   responses require reconciliation; never assume success or blindly retry a POST.
4. Rate limits stay with you. Record the server's wait time plus a margin. Retry
   only after that wait, at most twice for explicit rate-limit responses; do not
   run a tight retry loop. If the wake-up cannot safely accommodate the wait,
   mark blocked with earliest retry time. Exhausted retries are also blocked.
   Authentication failures identify the session owner as unblock owner; do not
   expose the cookie. Nonfinal failures do not create review or repair issues.
5. On acceptance or rejection, create/reuse a same-part **Solution Reviewer**
   issue, also matching the submission attempt/commit. Include exact verdict,
   answer, commit, test results, artifacts, and upstream links. Mark submission
   done only after verifying that handoff. A rejected submission task is done,
   but the puzzle part remains unfinished.

## Day12 finale

When specifically authorized by the CTO, inspect the authenticated final-part
instructions and prerequisites. Perform only the interaction actually offered
by the site. Do not send an invented numeric answer or require fabricated code.
If prerequisites are unmet or completion is uncertain, block with the exact
missing evidence/action. Hand authoritative completion evidence to the reviewer
using the same procedure; do not claim season completion yourself.

Stop after handing the final verdict to reviewer. Never route a rejection to
solver, create gathering work, start part2, or mention/wake the CTO.
