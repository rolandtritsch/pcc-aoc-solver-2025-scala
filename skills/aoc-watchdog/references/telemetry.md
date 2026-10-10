# WatchDog telemetry collector

Run from the company-managed `aoc-watchdog` skill directory using Python 3's standard library:

```bash
python3 -B scripts/aoc_watchdog.py
python3 -B scripts/aoc_watchdog.py --baseline /tmp/watchdog-baseline.json
```

Runtime inputs are `PAPERCLIP_API_URL`, `PAPERCLIP_API_KEY`,
`PAPERCLIP_COMPANY_ID`, `PAPERCLIP_AGENT_ID`, and `PAPERCLIP_RUN_ID`.
Do not pass credentials on the command line or obtain board credentials.
The optional baseline is the JSON snapshot from the last completed WatchDog
report for this company. Unknown, future, or over-one-hour-old baselines are
rejected; cost deltas also require the same UTC-day usage window.

Output is one JSON snapshot (schema version 1) with observation/run identity,
per-agent activity and progress hints, usage/deltas when available, findings,
coverage gaps, and `correctiveActionsTaken: false`. Exit 0 means collection is
complete; exit 2 means partial/unknown coverage, not an unhealthy task disposition.
Both may contain useful findings. Findings use healthy/warning/critical/unknown
severity. No baseline means trend coverage is initially unknown.

The collector uses GETs only, with no redirects or corrective endpoints. It
collects for at most 60 seconds, caps each request timeout at five seconds,
retries a network failure once, and prints at most 32 KiB. It fetches at most
three anomalous run details, 100 events and a 32 KiB log tail per suspect.
Raw logs, event payloads, credentials, and private input are never printed.

Twenty-minute silence/progress ages are only stall suspicions. Three repeated
no-progress attempts must refer to the same runnable task. Repeated structured
action/result patterns, including OpenCode tool-use logs, are candidates for
loop diagnosis. Costs are recorded usage, not guaranteed real-time billing.
Verify useful artifacts, tests, verdicts, and handoffs before interpreting a
progress hint as real work. Missing data is not zero or evidence of health.

The company WatchDog operating skill owns report creation and final disposition.
This helper creates no tasks, changes no files, and never pauses/cancels agents.
The observer's current run/report is excluded from puzzle progress checks;
previous unfinished reports can be findings. The CTO also excludes these reports
from its puzzle-cycle gate. Do not run sbt or solve a puzzle merely to monitor it.

After changing the collector or checks, run:

```bash
python3 -B -m unittest discover -s scripts/tests -v
```

Keep `scripts/aoc_watchdog.py` and its imported `aoc_watchdog_checks.py` together
in deployment checkouts. No extra Python dependency is required.
