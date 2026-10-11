# WatchDog repair verification — October 11, 2026

## Confirmed failure mechanisms

The investigation snapshot contained 72 WatchDog runs: 56 failed, 16 timed out,
and none succeeded. Recent provider errors rejected the 32,000-token allowance
against available credits. A sampled timeout run received
`cross_issue_influence_run_context_required` while trying to update its report:
timer runs lack a source task, and checkout does not establish one. Preparation
and tool calls consumed the deadline. The collector missed OpenCode tool events
inside Paperclip log `chunk` envelopes; its old fixture used the wrong format.

## Implemented repair

The company-owned adapter runner controls collection and reporting before model
inference. It reads bounded full report details (issue-list descriptions are
previews), evaluates current-cycle evidence, optionally interprets anomalies,
and creates a self-assigned task already done with a run-specific idempotency key.
Only that report is written; no checkout, PATCH, or corrective action occurs.

Phase limits are 15/45/30/20 seconds beneath the 120-second adapter timeout.
Flash receives one tool-free request only for new/changed anomalies, capped at
2,048 completion tokens and 8 KiB input. Failed interpretation triggers a persisted
one-hour cooldown. Partial evidence is reported as unknown; persistence failure
fails the run. The ten-minute schedule and balanced stall thresholds remain.

The collector parses actual nested log envelopes, inspects active suspects before
newest unrecovered failures, excludes historical puzzle tasks, recognizes CTO
review waits, and records evidence gaps. Public company UI links are configured
separately from the internal API address. External monitoring is deferred.

## Validation and live rollout

- 56 WatchDog tests passed locally and in the deployed ECS runtime.
- 20 existing CTO gate/wrapper tests passed.
- The actual Paperclip OpenCode parser accepted runner summaries and usage events.
- Manifest model/routing/schedule bindings, Markdown reference links, and whitespace
  were checked. Solver stays Pro; all other agents stay Flash.
- Skill imports excluded agents and tasks; explicit WatchDog config updates
  preserved vaulted credentials and its activated ten-minute timer. Executable
  modes for both imported wrappers were restored and tested.
- AOC-135 was created done with model credentials intentionally unavailable;
  the check succeeded in about two seconds. Credentials were restored afterward.
- AOC-136 completed with a model request failure, retaining deterministic findings.
- These early checks exposed unsupported issue sorting and truncated previews;
  both were corrected before final scheduled validation.
- AOC-137 completed using full baseline details and the persisted cooldown, without
  model inference. Its report had no issue-sort or missing-baseline error.
- Nineteen historical unfinished reports were cancelled by the board with an
  explanation; one additional failed report had appeared since the 18-report
  planning snapshot. Existing evidence was retained. WatchDog cannot do this cleanup.

The user added provider credits during rollout. Resuming the existing submission
completed AOC-125 after authenticated reconciliation of answer 848 and local
verification, without resubmitting. The existing review AOC-127 was resumed next;
AOC-127 then completed with an explicit accepted review and no outstanding repair.
The reviewer committed improvement `f750e75` (range-coverage skill and cross-check)
in scala3-aoc-2025; the next CTO timer can sync and select the next part.

## Three actual scheduled checks

| Report | Scheduler run | Runtime | Result |
| --- | --- | --- | --- |

| [AOC-138](https://paperclip.tritsch.org/AOC/issues/AOC-138) | `7a5ab24b-1f91-4483-abbc-b0273ace35ab` | 1.413 s | succeeded; one done report; healthy |
| [AOC-142](https://paperclip.tritsch.org/AOC/issues/AOC-142) | `e174f112-3a57-4d55-9cf2-b80421422974` | 1.502 s | succeeded; one done report; healthy |
| [AOC-144](https://paperclip.tritsch.org/AOC/issues/AOC-144) | `7912b242-edb4-4dcd-bc92-0df5e2eef9c5` | 1.337 s | succeeded; one done report; unknown |

The first two checks had complete requested telemetry coverage and no anomalies.
The third saved an explicit unknown: an active run had no visible task association
(`run_issue_unavailable:3c3ae205-85d9-4878-a7f2-f78030e822bf`). It still completed
its report successfully, exercising the partial-coverage path. All three checks
observed all seven agents and skipped Flash inference (`no_anomalies`).
No assignment-triggered WatchDog run appeared during this window. The activated
600-second interval, 120-second adapter timeout, and single-run concurrency were
preserved. Current puzzle work continued independently: Day05 part2 progressed
through solving and submission to review AOC-143 while the CTO respected the gate.
