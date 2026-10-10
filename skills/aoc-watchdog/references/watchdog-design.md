# WatchDog design and research

Sources checked October 10, 2026. This is the design rationale for the independent
AoC company observer, not a claim that monitoring can prove all agents healthy.

## Recommendations applied

| Source | Recommendation or demonstrated pattern | Application here |
| --- | --- | --- |
| [Google SRE][sre] | Keep monitoring simple, distinguish symptoms from causes, and reduce noise with actionable evidence. | Report observed stalls, failures, and consumption separately from suspected causes; recognize intended waits. |
| [OpenHands stuck detector][openhands] | Detect repeated action/observation pairs, repeated errors, and alternating cycles in bounded recent event windows. | Compare stable structured signatures; ignore incidental IDs and timestamps, and avoid counting log chatter as a loop. |
| [Anthropic effective agents][agents] | Use environmental feedback and explicit stopping conditions; complexity has cost and latency tradeoffs. | Combine a deterministic collector with an interpreting agent, hard time bounds, and no recursive tasks or corrective authority. |
| [Anthropic long-running harnesses][harnesses] | Durable progress artifacts help successive sessions understand and verify completed work. | Persist compact snapshots and evidence links on fresh report tasks; inspect actual work products before declaring useful progress. |

These sources support the patterns, not the selected numerical thresholds.
Twenty minutes, three attempts, a ten-minute schedule, and a two-minute check
are user-selected starting defaults to tune from observations.

## Existing Paperclip support

The inspected local Paperclip source exposes company agents, active/recent runs,
run liveness and continuation fields, bounded event/log reads, issues, and
per-agent recorded costs. Company-scope read permissions are checked; access
may be denied under restricted execution contexts. Treat denial as unknown.

Paperclip also has active-run and task watchdog mechanisms. The company observer
reads their signals but does not register with corrective mechanisms or submit
watchdog decisions. Their preexisting behavior remains separate from this v1.

In this version, `wakeOnDemand` gates non-timer wake-ups, including assignment;
self-assigned reporting tasks otherwise risk starting another run. Disable those
wake-ups and cap concurrency at one. The CTO must exclude report tasks from its
puzzle-cycle gate. Periodic heartbeats are disabled during company import, so
activation requires an explicit later deployment step.

## What the collector establishes

The stdlib-only collector bundled with the company's `aoc-watchdog` skill uses GET requests exclusively. It
collects active issues and recently completed issues, active runs and ten recent
runs per agent, and recorded per-agent usage since UTC midnight. It inspects at
most three anomalous runs, up to 100 events and a 32 KiB log tail for each.
Responses are capped at 1 MiB, collection at 60 seconds, each network operation
at five seconds, and output at 32 KiB. One network retry is allowed for safe GETs;
HTTP errors and redirects do not trigger retries. It never prints raw log bodies.

Available cost deltas compare the same UTC-day window against the prior snapshot.
Midnight, missing observations, and delayed billing can make deltas unavailable;
recorded usage does not capture provider spend not yet reported to Paperclip.

Liveness timestamps are hints: Paperclip can regard comments and tool calls as
activity. The observer therefore must verify artifacts, tests, verdicts, and
handoffs before claiming useful progress. Repetition checks support structured
action/result events and completed OpenCode `tool_use` JSON log records. Unknown
formats and partial windows limit coverage. Detailed loop inspection focuses on
long-running, retried, or failed runs, so a short loop may only become observable
on a later check. Single-run observations cannot prove a root cause.

## Boundaries and failure modes

Each actual monitoring run creates a fresh self-assigned report, with run identity
used to reconcile retries. A continuation of that same run uses the same report.
Write a complete report even when findings are critical; `done` describes the
monitoring task, not the company's health. The agent only writes its own current
report. It neither edits another task nor closes older unfinished reports.

Intentional pauses, idle agents, recorded external blockers, rate-limit waits,
and the review-to-CTO wait are not stalls. New work on different parts concurrently,
duplicate stage issues, missing handoffs, and overdue timers are candidates for
investigation. Handoff absence in a bounded window is explicitly not proof that
no handoff exists anywhere in history.

This observer shares the Paperclip control plane: when it is down, task creation
and telemetry collection can both fail. Run failures and later missed-check
observations help expose this, but reliable detection of the observer itself
requires a future external monitor. V1 also cannot prevent token burn by itself;
it documents evidence and recommends operator action. Hard budget enforcement or
automatic shutdown would be a separate design and authorization change.

## Validation and deployment

Run the fixture/transport tests from the company's `aoc-watchdog` skill directory:

```bash
python3 -B -m unittest discover -s scripts/tests -v
```

Validate the company import preview for the root relationship, skill reference,
600-second interval, disabled non-timer wake-ups, concurrency one, and timeout
120. Verify the company-managed skill includes its collector, checks module,
and telemetry guide before activation.
Verify WatchDog's own runtime credentials can read the full company and write its
self-assigned report without admin credentials. Retain existing model, secret,
workspace, and other agents' paused settings. Enable only WatchDog's timer when
live activation is authorized; confirm one task per actual scheduled run and no
assignment-triggered run. The implementation itself performs no live activation.

[sre]: https://sre.google/sre-book/monitoring-distributed-systems/
[openhands]: https://github.com/OpenHands/software-agent-sdk/blob/main/openhands-sdk/openhands/sdk/conversation/stuck_detector.py
[agents]: https://www.anthropic.com/engineering/building-effective-agents
[harnesses]: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
