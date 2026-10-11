---
name: aoc-watchdog
description: Run bounded ten-minute report-only AoC agent monitoring with deterministic task persistence and optional Flash anomaly interpretation
---

## Runtime ownership

The company-owned `scripts/aoc_watchdog_runner.py` is the WatchDog adapter command.
On a timer invocation it reads the prior completed report, runs the read-only
collector/checks, optionally interprets anomalies, and POSTs one self-assigned
completed task containing the human report and `watchdog-snapshot` JSON.

Creating the task already done avoids Paperclip's rejection of updates from
source-task-less timer runs. The run-specific idempotency key and bounded
reconciliation prevent duplicate reports. The runner never checks out or PATCHes
reports. Same-run retries reuse the completed task. Failed persistence is a failed
run; saved partial evidence is a completed reporting task with unknown coverage.

The timer is 600 seconds, adapter timeout 120 seconds, concurrency one, and all
non-timer wake-ups disabled. Imported heartbeats start disabled; activation is
separate. The runner delegates adapter probes to OpenCode but handles `run`
itself. Do not replace it with an autonomous tool loop or load setup research
inside a timed check.

Phase limits are preparation 15 seconds, collection 45, optional interpretation
30, and persistence 20. Hard Linux wall-clock deadlines leave ten seconds under
the adapter timeout. Required API write errors stop the run; no unlimited retries.

## Interpretation and findings

Flash interpretation uses one tool-free OpenRouter request only for new or
changed warning/critical findings. Input is capped at 8 KiB, completion at 2,048
tokens, and runtime at 30 seconds. A provider failure skips interpretation for an
hour, persisted across reports. Repeated unchanged anomalies remain documented
without repeated model calls. Missing credentials, rejected requests, empty or
invalid responses, and timeouts retain the deterministic report. Model text never
removes findings or changes coverage. Measured usage is recorded when available.

Balanced stall thresholds are 20 minutes without evidenced progress or three
repeated no-progress attempts for the same runnable task. Repeated stable
action/result pairs and alternating cycles are loop suspicions. Current-cycle
puzzle tasks, legitimate blockers, pauses, unassigned specialists, and CTO review
waits receive separate treatment. Costs are recorded measurements, not guaranteed
current provider billing. Activity timestamps do not establish semantic progress.

Reports include UTC time, coverage gaps, all visible agents, active tasks/runs,
progress hints, usage deltas, evidence links, new/recurring findings, optional
interpretation status, operator recommendations, and `correctiveActionsTaken:
false`. Missing measurements are unavailable, never asserted zero. No raw logs,
private input, credentials, Slack/email, or mentions belong in reports.

## Authority and setup

WatchDog has no manager and no corrective authority. Its only write is creation
of its current completed report. Never alter other work, close historical reports,
wake agents, register corrective watchdogs, submit watchdog decisions, or obtain
board/admin credentials. No puzzle builds, submissions, or Git changes occur.

Read [telemetry and verification][telemetry] and [design research][research]
during setup. Configure the deployed runner path and executable mode after import;
replacement imports can reset file modes. Keep its collector/checks alongside it.
The company README owns deployment instructions.

This observer shares Paperclip's failure domain. If Paperclip is unavailable it
cannot persist a report; the run must fail visibly. Independent external
monitoring is deferred and this version cannot detect its own total absence.

[telemetry]: references/telemetry.md
[research]: references/watchdog-design.md
