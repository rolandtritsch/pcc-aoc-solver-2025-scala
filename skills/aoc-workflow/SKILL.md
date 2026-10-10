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

A normal part is complete only with a real implementation, meaningful active
passing tests, authoritative acceptance tied to the verified answer, and a
completed review without unresolved repair. A rejection's review can be done
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
   by year, day, part, and stage. For review, also match attempt/commit. A blocked
   issue is an existing blocker, not permission to create a duplicate. Check
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
