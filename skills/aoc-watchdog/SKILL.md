---
name: aoc-watchdog
description: Run independent ten-minute, report-only checks of AoC agent health and useful progress using a bounded company-owned telemetry collector
---

## Boundaries and schedule

WatchDog has no manager, puzzle assignment, or corrective authority. Its heartbeat
interval is 600 seconds, with one concurrent run and a 120-second adapter timeout.
The package starts with periodic heartbeats disabled; activation is a separate
live operation. Non-timer wake-ups must remain disabled (`wakeOnDemand: false`
and its assignment/on-demand/automation aliases). Self-assignment must not create
another invocation. Unexpected non-timer notifications exit without new work.

Only the current report task may be created, checked out, or updated. All other
work is read-only. Do not register corrective watchdogs, submit watchdog decisions,
pause/cancel/restart agents, change budgets, or wake/mention another agent. The
ordinary puzzle `aoc-workflow` handoff rules do not apply to monitoring reports.
Read [the design research][research] for rationale and detection limits.

## One report per monitoring run

1. On a timer wake-up, start a two-minute clock. Read your injected
   `PAPERCLIP_AGENT_ID`, `PAPERCLIP_COMPANY_ID`, and `PAPERCLIP_RUN_ID`. Use the
   runtime Paperclip skill for authentication and JSON encoding; never log secrets.
   This timer procedure creates a task even with an empty inbox.
2. Query company issues assigned to yourself with title prefix `WatchDog check `,
   and inspect their descriptions for the exact current run ID. Reuse an existing
   report only for this same run. Otherwise POST a top-level task to
   `/api/companies/{companyId}/issues`, using `parentId: null`, your own
   `assigneeAgentId`, `status: "todo"`, and title
   `WatchDog check <UTC timestamp> — <run ID>`. Its description identifies the
   company, observer run ID, check start time, and report-only purpose.
   Verify the returned ID/assignment. On ambiguous creation, reconcile by run ID
   before one retry; never create multiple reports for the same run.
3. Check out that reporting issue with your identity and current run ID. If another
   run owns it, stop. Creating and checking out the reporting task are the only
   preparation writes. All mutations use `X-Paperclip-Run-Id` and JSON bodies.
4. Find the latest completed earlier WatchDog report (self-assigned, correct
   prefix/company, different run ID). Extract its `watchdog-snapshot` fenced JSON
   from the description to a temporary baseline file. Reject unrelated JSON.
   If missing, collect without a baseline and report the trend limitation.
5. Read [the telemetry guide][telemetry] and locate this company-managed
   `aoc-watchdog` skill directory. Run from that directory:

   ```bash
   python3 -B scripts/aoc_watchdog.py --baseline /tmp/watchdog-baseline.json > /tmp/watchdog-snapshot.json
   ```

   Omit `--baseline` when unavailable. The helper uses
   injected Paperclip credentials and company/run/agent IDs; no board credentials,
   AoC session, browser, Scala build, or git write is needed. It collects for at
   most 60 seconds and emits at most 32 KiB. Exit 2 means partial/unknown coverage,
   not permission to discard its valid JSON or retry indefinitely.
6. Interpret the snapshot against the actual pipeline rules. Verify suspected
   causes from linked issues and available artifacts only within remaining time.
   Last-useful-action timestamps and output are activity hints; meaningful progress
   requires a new artifact, verified implementation/test result, verdict, or valid
   handoff. Repeated generic comments do not prove useful work. When semantic
   evidence is absent, say unknown rather than claiming progress or a root cause.
7. PATCH your reporting issue with its completed human report in `comment` and
   the complete snapshot in the description under a `watchdog-snapshot` fenced
   code block. Preserve the description's run identity. Use `status: "done"` and
   verify the response. Report severity is separate from task status: an unhealthy
   company can have a successfully completed report. Complete partial checks with
   unknown coverage rather than leaving a self-waking continuation.
8. Stop. Do not create downstream tasks, schedule retries, or wake the CTO.
   If required task writes fail, record a failed run outcome and stop; the next
   scheduled check can observe an unfinished report, but must not repair it.

## Findings and evidence

Balanced defaults are 20 minutes without evidenced progress or three repeated
no-progress attempts for the same runnable issue. Three identical action/result
pairs, or three repetitions of a two-pair cycle, are loop indicators. These are
suspicions to check, not proof that difficult reasoning is useless.

- **Healthy:** observed work is consistent with expectations and required health
  coverage is available. Say which progress is verified and which is only hinted.
- **Warning:** suspected stall, repeated failure, stranded assignment, missing
  handoff in the observed window, duplicate stage, wrong part order, or overdue
  timer. Explain evidence and legitimate-wait exceptions.
- **Critical:** repeated unproductive work with measured ongoing consumption,
  confirmed from evidence. Recommend stopping affected work to the operator;
  take no action. Mere silence or an unavailable cost measurement is insufficient.
- **Unknown:** missing baseline, denied telemetry, API/collector failure, truncated
  coverage, unavailable metrics, or unsupported event formats. Known warnings or
  critical findings retain their severity alongside explicitly unknown coverage.

A paused/idle specialist, Model Tester without an assignment, recorded blocker,
submission backoff, and wait for the next CTO timer can be normal. A paused agent
with an active run is still an anomaly. WatchDog's current report/run is excluded
from progress/loop checks; previous unfinished reports remain visible.

Write UTC observation time, monitored agents, active tasks/runs, changes since the
previous check, verified progress, findings with issue/run links and timestamps,
measured token/cost changes or unavailable values, recurring-report links, and
operator recommendations. Include `correctiveActionsTaken: false` in the snapshot.
Missing measurements are not zero. Do not paste raw logs, private puzzle input,
or credentials. Put the record on the task only; no Slack/email/mention alerts.

[research]: references/watchdog-design.md

[telemetry]: references/telemetry.md
