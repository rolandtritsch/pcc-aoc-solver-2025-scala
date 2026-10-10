"""Conservative, deterministic checks over bounded Paperclip telemetry."""
import hashlib
import json
import re
from datetime import datetime, timezone

ACTIVE = {"queued", "running"}
OPEN = {"todo", "in_progress", "in_review", "blocked"}
LEVELS = {"healthy": 0, "unknown": 1, "warning": 2, "critical": 3}


def timestamp(value):
    try:
        result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return result if result.tzinfo else None
    except (TypeError, ValueError):
        return None


def elapsed(now, value):
    at = timestamp(value)
    return max(0, (now - at).total_seconds()) if at else None


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def issue_id(run):
    context = run.get("contextSnapshot") or {}
    return run.get("issueId") or context.get("issueId") or context.get("taskId")


def puzzle(issue):
    # Only conventional puzzle titles count; arbitrary monitoring text does not.
    match = re.search(r"\bday\s*0*(\d+)\b.*?\bpart\s*([12])\b", issue.get("title", ""), re.I)
    if match and 1 <= int(match[1]) <= 12:
        return (int(match[1]), int(match[2]))
    return None


def report_issue(issue, observer_id):
    return issue.get("assigneeAgentId") == observer_id and issue.get("title", "").startswith("WatchDog check ")


def event_patterns(events):
    """Only structured action/result pairs count; never count log chatter as a loop."""
    pairs, action = [], None
    ignored = {"id", "seq", "createdAt", "timestamp", "toolCallId", "call_id", "runId", "agentId", "usage", "metrics"}

    def clean(value):
        if isinstance(value, dict):
            return {k: clean(v) for k, v in value.items() if k not in ignored}
        if isinstance(value, list):
            return [clean(v) for v in value]
        return value

    for event in events:
        kind = str(event.get("eventType", "")).lower()
        payload = event.get("payload") or {}
        if kind in {"tool.call", "tool_call", "action"}:
            action = fingerprint(clean(payload)) if payload else None
        elif kind in {"tool.result", "tool_result", "observation", "tool.error"} and action:
            if payload:
                pairs.append(fingerprint([action, clean(payload)]))
            action = None
    if len(pairs) >= 3 and len(set(pairs[-3:])) == 1:
        return "repeated_action_result"
    if len(pairs) >= 6 and pairs[-6:-4] == pairs[-4:-2] == pairs[-2:]:
        return "alternating_action_result"
    return None


def analyze(data, baseline=None, now=None):
    now = now or datetime.now(timezone.utc)
    problems = list(data.get("coverage", []))
    if baseline and (baseline.get("schemaVersion") != 1 or baseline.get("companyId") != data["companyId"]
                     or elapsed(now, baseline.get("observedAt")) is None
                     or timestamp(baseline["observedAt"]) > now
                     or elapsed(now, baseline["observedAt"]) > 3600):
        problems.append("baseline_invalid_or_stale")
        baseline = None
    prior = {row["agentId"]: row for row in (baseline or {}).get("agents", [])}
    issues = [i for i in data.get("issues", []) if not report_issue(i, data["observerId"])]
    runs = {r["id"]: r for r in data.get("runs", [])}
    costs = {r["agentId"]: r for r in data.get("costs", [])}
    findings, rows = [], []

    def add(code, level, agent=None, issue=None, run=None):
        findings.append({"code": code, "severity": level, "agentId": agent, "issueId": issue, "runId": run})

    if baseline is None:
        problems.append("usage_trend_baseline_unavailable")
    for agent in data.get("agents", []):
        aid = agent["id"]
        assigned = [i for i in issues if i.get("assigneeAgentId") == aid]
        recent = sorted((r for r in runs.values() if r.get("agentId") == aid and r["id"] != data.get("observerRunId")),
                        key=lambda r: r.get("createdAt") or "", reverse=True)
        live = [r for r in recent if r.get("status") in ACTIVE]
        old = prior.get(aid, {})
        progress_times = [r.get("lastUsefulActionAt") for r in recent if timestamp(r.get("lastUsefulActionAt"))]
        progress_at = max(progress_times, default=None)
        for run in recent:
            if run.get("status") in ACTIVE and issue_id(run) is None:
                problems.append("run_issue_unavailable:" + run["id"])
        progress_age = elapsed(now, progress_at)
        usage = costs.get(aid)
        delta = None
        if usage and old.get("usage") and old.get("usageFrom") == data.get("usageFrom"):
            keys = ("costCents", "inputTokens", "outputTokens")
            if all(isinstance(usage.get(k), (int, float)) and isinstance(old["usage"].get(k), (int, float)) for k in keys):
                values = {k: usage[k] - old["usage"][k] for k in keys}
                if all(v >= 0 for v in values.values()):
                    delta = values
        consuming = delta is not None and any(v > 0 for v in delta.values())
        status = agent.get("status", "unknown")
        hb = (agent.get("runtimeConfig") or {}).get("heartbeat") or {}
        open_assigned = [i for i in assigned if i.get("status") in OPEN]
        expected_wait = status in {"paused", "terminated"} or (not live and bool(open_assigned) and all(i.get("status") == "blocked" for i in open_assigned))
        stalled = False
        repeating = False
        if status in {"paused", "terminated"} and live:
            add("paused_agent_with_active_run", "warning", aid)
        if status == "error":
            add("agent_error", "warning", aid)
        for run in live:
            target = next((i for i in assigned if i["id"] == issue_id(run)), None)
            waiting = target is not None and target.get("status") == "blocked"
            waiting = waiting or run.get("livenessState") == "blocked"
            # Inferred activity is a hint, not proof of meaningful progress.
            at = run.get("lastUsefulActionAt") or run.get("startedAt") or run.get("createdAt")
            age = elapsed(now, at)
            if age is None:
                problems.append("run_timestamp_unavailable:" + run["id"])
            elif age >= 1200 and not waiting and not expected_wait:
                add("suspected_stall", "warning", aid, issue_id(run), run["id"])
                stalled = True
            pattern = event_patterns(data.get("events", {}).get(run["id"], []))
            if pattern and not waiting and not expected_wait:
                add(pattern, "warning", aid, issue_id(run), run["id"])
                repeating = True
        relevant = [r for r in recent if r.get("status") not in ACTIVE][:3]
        # Compare only attempts for the same task; scheduled idle checks are not failures.
        if len(relevant) == 3 and len({issue_id(r) for r in relevant}) == 1 and any(i["id"] == issue_id(relevant[0]) and i.get("status") in {"todo", "in_progress"} for i in assigned):
            no_progress = all(r.get("livenessState") in {"empty", "planning_only", "no_progress", "stalled", "empty_response", "plan_only", "needs_followup", "failed"}
                              or r.get("status") in {"failed", "timed_out"} for r in relevant)
            newest_progress = max((timestamp(r.get("lastUsefulActionAt")) for r in relevant
                                   if timestamp(r.get("lastUsefulActionAt"))), default=None)
            if no_progress and newest_progress is None and not expected_wait:
                add("repeated_no_progress_attempts", "warning", aid, issue_id(relevant[0]), relevant[0]["id"])
                repeating = True
        if consuming and repeating:
            add("repetition_with_recorded_consumption", "critical", aid)
        for issue in assigned:
            age = elapsed(now, issue.get("updatedAt") or issue.get("createdAt"))
            if issue.get("status") in {"todo", "in_progress"} and age is not None and age >= 1200 and not live and not expected_wait:
                add("assignment_without_active_run", "warning", aid, issue["id"])
        if aid == data["observerId"]:
            older_open = [i for i in data.get("issues", []) if report_issue(i, aid) and i.get("status") in OPEN
                          and elapsed(now, i.get("createdAt")) is not None and elapsed(now, i["createdAt"]) >= 1200]
            for issue in older_open:
                add("unfinished_watchdog_report", "warning", aid, issue["id"])
        if agent.get("name") in {"CTO", "WatchDog"} and hb.get("enabled") and status not in {"paused", "terminated"}:
            timers = [r for r in recent if r.get("invocationSource") == "timer"]
            age = elapsed(now, timers[0].get("createdAt")) if timers else None
            if age is not None and age >= 1200:
                add("missing_scheduled_run", "warning", aid)
            elif age is None:
                problems.append("timer_history_unavailable:" + aid)
        hint = "expected_wait" if expected_wait else "active" if live else "idle"
        rows.append({"agentId": aid, "name": str(agent.get("name", ""))[:100], "status": status,
                     "activity": hint, "activeRunIds": [r["id"] for r in live][:10],
                     "assignedIssueIds": [i["id"] for i in assigned if i.get("status") in OPEN][:10],
                     "progressHintAt": progress_at, "progressHintAgeSec": progress_age,
                     "usageFrom": data.get("usageFrom"), "usage": usage, "usageDelta": delta,
                     "suspectedStall": stalled, "newProgressHint": bool(progress_at and progress_at != old.get("progressHintAt"))})
    active_puzzles = [i for i in issues if i.get("status") in {"todo", "in_progress", "in_review"} and puzzle(i)]
    for issue in issues:
        if issue.get("status") == "done" and puzzle(issue) and elapsed(now, issue.get("updatedAt")) is not None and elapsed(now, issue["updatedAt"]) >= 1200:
            source_agent = next((a for a in data.get("agents", []) if a["id"] == issue.get("assigneeAgentId")), {})
            recipient = {"Problem Gatherer": "Problem Solver", "Problem Solver": "Problem Submitter", "Problem Submitter": "Solution Reviewer"}.get(source_agent.get("name"))
            if recipient:
                target_ids = {a["id"] for a in data.get("agents", []) if a.get("name") == recipient}
                downstream = [i for i in issues if puzzle(i) == puzzle(issue) and i.get("assigneeAgentId") in target_ids and (i.get("createdAt") or "") >= (issue.get("createdAt") or "")]
                if not downstream:
                    add("handoff_not_observed_in_window", "warning", source_agent.get("id"), issue["id"])
    keys = {puzzle(i) for i in active_puzzles}
    if len(keys) > 1:
        add("multiple_active_puzzle_parts", "warning")
    for key in keys:
        grouped = [i for i in active_puzzles if puzzle(i) == key]
        owners = [i.get("assigneeAgentId") for i in grouped]
        if len(owners) != len(set(owners)):
            add("duplicate_active_stage", "warning")
    if not data.get("agents"):
        problems.append("agent_inventory_unavailable")
    outcome = max((f["severity"] for f in findings), key=LEVELS.get, default="unknown" if problems else "healthy")
    if problems and LEVELS[outcome] < LEVELS["unknown"]:
        outcome = "unknown"
    return {"schemaVersion": 1, "companyId": data["companyId"], "observerId": data["observerId"],
            "observerRunId": data.get("observerRunId"), "observedAt": now.isoformat(),
            "outcome": outcome, "coverage": sorted(set(problems)), "agents": rows, "findings": findings,
            "correctiveActionsTaken": False}
