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

The CTO command wrapper `scripts/aoc_cto.py` runs the gate before launching
OpenCode, avoiding inference entirely while the current cycle is busy.
The CTO also runs `scripts/aoc_cycle_gate.py` from this skill directory before
selection and immediately before creating work.
Current-cycle tasks at or after `AOC_CYCLE_STARTED_AT` gate execution: any
unfinished stage or missing successful review means exit before looking for
more work. The helper is read-only, paginated, bounded to 20 seconds, and fails
closed on unavailable/ambiguous evidence. WatchDog and Model Tester do not gate
the puzzle cycle. A completed rejected review permits same-part repair only.

After the gate clears, the CTO synchronizes the solution branch with origin: fetch, fast-forward
pull incoming commits, push outgoing committed work, and verify clean
local/tracking/remote equality. Dirty or divergent work requires reconciliation
without discarding files or force-pushing. Then **only `sbt run` and `sbt test`**
determine its next part or code repair, in day/part order. Day00-only output means
Day01 part1. Missing/failed/ambiguous relevant command evidence is unfinished;
pre-cycle task statuses, acceptances, and reviews cannot advance or block
selection. Current-cycle review completion must clear the gate first.
Historical tasks provide context, and current-cycle tasks prevent duplicate
execution only after command-based selection. Do not mistake an old blocked
issue for current-cycle work.

Use `AOC_REPO_DIR` for the canonical shared checkout, never a warmup or
per-agent clone. Carry its exact path and the cycle start in every handoff.
Gatherer commits material there. The solver must use the `aoc-solve-scala`
publication helper to verify, commit and push material/solution commits before
creating a submitter handoff; it records exact remote parity and command evidence.
A locally committed solution alone does not permit a handoff. Reviewer commits improvements there; CTO pushes them on its next
gate-cleared synchronization. If HTTPS push needs credentials, use the injected
`GH_TOKEN` through `gh auth setup-git`; never write tokens into URLs or files.

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

Solver-to-submitter creation is exclusively through
`aoc-solve-scala/scripts/aoc_solver_publish.py publish`, after its publication
checks. The general API procedure below applies to other stage handoffs and to
recording the solver's confirmed handoff/status; it is not a solver bypass.
Submitter must independently run the helper's `verify` mode before any numerical
submission or acceptance reconciliation. A failed gate blocks the current part.


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

On a 409 run-ownership conflict, reconcile checkout once with the current
run ID. If it still fails, stop retries and record the exact final disposition
and verified downstream issue so the board can reconcile the stranded status.
Use `unblockDescriptor` (owner and concrete action) or an actual blocker link
when setting `blocked`; a reason-only update can be rejected.

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

## Terminal season completion

The 2025 edition ends at Day12. After all 24 day/part pairs in the current
cycle have accepted completed reviews with no repair required, and no specialist
run or current-cycle task remains active, the cycle gate returns `mode: complete`.
The CTO launcher exits successfully before model inference and cannot start
another gatherer task. Day12 part2 uses authenticated finale acceptance evidence,
not a fabricated computation. Missing reviews, rejections, and pending repairs
are not completion. A deliberate board reset uses a new cycle start timestamp.
