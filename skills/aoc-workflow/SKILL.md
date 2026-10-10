---
name: aoc-workflow
description: Coordinate the AoC 2025 part-by-part pipeline, evidence, duplicate-safe handoffs, and CTO wake-up boundary
---

## Cycle and evidence

WatchDog is an independent observer outside this pipeline. Its self-assigned
`WatchDog check ` report tasks do not authorize work, count as puzzle stages,
or block CTO selection. Specialists do not assign or hand puzzle work to it.

Only the CTO authorizes a part on a manual or timer wake-up. The authorized
cycle is gather if needed → solve → submit → review → **wait**. Accepted and
rejected attempts both end at the reviewer. Only a later CTO wake-up can start
part2, the next day, or a repair. Order parts by day first, then part, through
Day12; Day00 is a template. Specialist notifications are not advancement triggers.

The CTO first synchronizes the solution branch with origin: fetch, fast-forward
pull incoming commits, push outgoing committed work, and verify clean
local/tracking/remote equality. Dirty or divergent work requires reconciliation
without discarding files or force-pushing. Then **only `sbt run` and `sbt test`**
determine its next part or code repair, in day/part order. Day00-only output means
Day01 part1. Missing/failed/ambiguous relevant command evidence is unfinished;
old task statuses, acceptances, and reviews cannot advance or block selection.
Historical tasks provide context, and current-cycle tasks prevent duplicate
execution only after command-based selection. Do not mistake an old blocked
issue for current-cycle work.

Read the checkout's `AGENTS.md` and applicable `skills/*/SKILL.md` before work.
Reviewer improvements live and are committed in `scala3-aoc-2025`: reusable
`scripts/` and `skills/<name>/SKILL.md`. Consult the latest relevant review
before repeating work. Do not execute an unvalidated script just because it exists.

Use `(year=2025, day=NN, part=P, stage)` in issue titles/descriptions. `NN` is
zero-padded for repository paths; use its unpadded integer in AoC URLs. Stages
are gather, solve, submit, review. Carry upstream issue links, artifact paths,
verified answer, commit, command exit codes/results, test evidence, and original
verdict when available. Review issues identify the submission attempt/commit,
so a new repaired answer gets a new review instead of reusing an old verdict.
Carry the CTO decision commit and source issue through the cycle. Pre-reset
records are informational, not current assignments or progress evidence.

A current submission/review cycle is complete with a real implementation,
meaningful active passing tests, authoritative acceptance tied to the verified
answer, and a completed review. This is the specialists' delivery contract; the
CTO selects its next computational part solely from synchronized run/test results.
A rejection's review can be done
while that part remains unfinished. Printed `0`, missing tests, ignored tests,
or green unrelated tests are not completion evidence. An authenticated page
showing the matching accepted answer may reconcile historical acceptance.
Do not assume acceptance from "already completed" or "wrong level" responses.
If evidence is unavailable, report it as unavailable rather than resetting history.

## Paperclip handoffs

Use the runtime's Paperclip coordination skill for checkout/authentication.
Never hard-code agent UUIDs or API URLs, and never print credentials. This
package does not supply `scripts/paperclip-issue-update.sh`; use the API below
or a verified available helper. Encode JSON with a JSON library or `jq`, not
interpolated multiline shell strings.

1. Read `GET /api/companies/{companyId}/agents` and
   `GET /api/companies/{companyId}/issues`, including all relevant result pages.
   Resolve the recipient by its exact agent name; missing or ambiguous names
   block the handoff. Inspect descriptions and comments, not titles alone.
2. Reuse matching active work (`todo`, `in_progress`, `in_review`, or `blocked`)
   by current repository cycle, year, day, part, and stage. For review, also match
   attempt/commit. A blocked issue within that current cycle is an existing
   blocker; an old blocked task is only historical context. Check
   completed handoffs recorded on the source issue when resuming a run.
3. If no matching work exists, `POST /api/companies/{companyId}/issues` with a
   JSON object containing `title`, `description`, `status: "todo"`, the resolved
   `assigneeAgentId`, and explicit `parentId: null`. Verify successful HTTP status
   plus the returned ID, assignee, and description. If a request times out,
   reconcile the board before retrying creation. Duplicate checks are best-effort,
   not atomic; a future helper must address concurrent creation if it occurs.
4. Only after verifying the handoff, `PATCH /api/issues/{issueId}` with
   `{"status":"done","comment":"<result, evidence, and handoff issue link>"}`.
   Reviewer has no downstream handoff; its comment contains the completed review
   and recommendations for the next CTO cycle. Verify the returned status.
5. On a blocker, PATCH `status: "blocked"` with its exact reason, owner, and
   concrete unblock action. A comment alone does not complete a task.

All requests use `Authorization: Bearer $PAPERCLIP_API_KEY` and the injected
`PAPERCLIP_API_URL`/`PAPERCLIP_COMPANY_ID`. Mutations also require
`X-Paperclip-Run-Id: $PAPERCLIP_RUN_ID` and `Content-Type: application/json`.
Use the current issue ID from `PAPERCLIP_TASK_ID`; do not reuse IDs from old resets.

Recipients are `Problem Gatherer`, `Problem Solver`, `Problem Submitter`, and
`Solution Reviewer`. The CTO creates/reuses one authorized stage issue; gatherer
hands the same part to solver (or submitter for the finale), solver to submitter,
and submitter to reviewer. No specialist creates next-part or retry work.

## Finale and paused state

The 2025 calendar ends at Day12. For a noncomputational final part, gather the
authenticated instructions if missing, let submitter perform only the actual
site interaction, and let reviewer check completion evidence. Do not fabricate
an answer, Scala implementation, or computational tests. All earlier acceptance
and review requirements still apply. Never create Day13 work.

Keep the CTO heartbeat paused until explicitly enabled. Company package updates
and model changes do not resume paused agents or authorize live deployment.
