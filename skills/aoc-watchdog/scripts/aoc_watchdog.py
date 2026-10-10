#!/usr/bin/env python3
"""Collect bounded, read-only Paperclip telemetry; print a redacted JSON snapshot."""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

from aoc_watchdog_checks import analyze, elapsed

MAX_BODY = 1024 * 1024
MAX_OUTPUT = 32768


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Never forward authorization to another host.


class Client:
    def __init__(self, base, token, company, deadline=60):
        parsed = urllib.parse.urlsplit(base)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.username or parsed.query or parsed.fragment:
            raise ValueError("invalid_api_url")
        if not re.fullmatch(r"[A-Za-z0-9_-]+", company):
            raise ValueError("invalid_company_id")
        self.base, self.token, self.company = base.rstrip("/"), token, company
        self.until = time.monotonic() + min(60, max(0, deadline))
        self.problems = []
        self.opener = urllib.request.build_opener(NoRedirect())

    def get(self, path, params=None):
        company_path = "/api/companies/" + self.company
        allowed = {company_path + suffix for suffix in ("/agents", "/issues", "/live-runs", "/heartbeat-runs", "/costs/by-agent")}
        if path not in allowed and not re.fullmatch(r"/api/heartbeat-runs/[A-Za-z0-9_-]+(?:/events|/log)?", path):
            raise ValueError("endpoint_not_allowed")
        for attempt in range(2):
            remaining = self.until - time.monotonic()
            if remaining <= 0:
                self.problems.append("collection_deadline")
                return None
            url = self.base + path + ("?" + urllib.parse.urlencode(params) if params else "")
            req = urllib.request.Request(url, headers={"Authorization": "Bearer " + self.token}, method="GET")
            try:
                with self.opener.open(req, timeout=min(5, remaining)) as response:
                    chunks, total = [], 0
                    while True:
                        if time.monotonic() >= self.until:
                            raise TimeoutError()
                        chunk = response.read(min(65536, MAX_BODY + 1 - total))
                        if not chunk:
                            break
                        chunks.append(chunk)
                        total += len(chunk)
                        if total > MAX_BODY:
                            self.problems.append("response_too_large:" + path)
                            return None
                    return json.loads(b"".join(chunks))
            except urllib.error.HTTPError as error:
                self.problems.append("http_" + str(error.code) + ":" + path)
                return None
            except (TimeoutError, urllib.error.URLError, OSError):
                if attempt == 0 and self.until - time.monotonic() > 1:
                    continue  # One safe GET retry; no POSTs, redirects, or retry loops.
                self.problems.append("request_unavailable:" + path)
                return None
            except (ValueError, UnicodeError):
                self.problems.append("invalid_json:" + path)
                return None

    def rows(self, path, params=None):
        result = self.get(path, params)
        if not isinstance(result, list) or any(not isinstance(r, dict) for r in result):
            self.problems.append("list_unavailable:" + path)
            return []
        rows = []
        for row in result:
            if row.get("companyId", self.company) != self.company:
                self.problems.append("company_mismatch:" + path)
            else:
                rows.append(row)
        return rows


def collect(client, observer, run_id, now, baseline=None):
    base = "/api/companies/" + client.company
    agents = client.rows(base + "/agents")
    if len(agents) > 40:
        client.problems.append("agent_inventory_truncated")
        agents = agents[:40]
    issues = []
    for status in ("todo,in_progress,in_review,blocked", "done"):
        for offset in (0, 100):
            params = {"status": status, "limit": 100, "offset": offset, "sortDir": "desc", "sortField": "updated"}
            if status == "done":
                params["updatedSince"] = (now - timedelta(minutes=30)).isoformat()
            page = client.rows(base + "/issues", params)
            issues.extend(page)
            if len(page) < 100:
                break
            if offset == 100:
                client.problems.append("issue_inventory_truncated:" + status)
    live = client.rows(base + "/live-runs", {"limit": 100, "minCount": 0})
    if len(live) == 100:
        client.problems.append("active_runs_truncated")
    runs = {r["id"]: r for r in live if r.get("id")}
    for agent in agents:
        if not agent.get("id"):
            client.problems.append("agent_id_unavailable")
            continue
        recent = client.rows(base + "/heartbeat-runs", {"agentId": agent["id"], "summary": "true", "limit": 10})
        for row in recent:
            if row.get("id"):
                # Preserve live projections such as issueId and outputSilence.
                runs[row["id"]] = {**row, **runs.get(row["id"], {})}
    usage_from = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    costs = client.rows(base + "/costs/by-agent", {"from": usage_from, "to": now.isoformat()})
    safe_costs = [{k: r.get(k) for k in ("agentId", "costCents", "inputTokens", "outputTokens")} for r in costs]
    events, log_signals = {}, []
    suspects = []
    for row in runs.values():
        age = elapsed(now, row.get("lastUsefulActionAt") or row.get("startedAt") or row.get("createdAt"))
        if row["id"] != run_id and (row.get("status") in {"failed", "timed_out"}
                                    or row.get("status") == "running" and (age is not None and age >= 1200 or (row.get("continuationAttempt") or 0) >= 2)):
            suspects.append(row)
    suspects.sort(key=lambda r: (r.get("status") != "running", r.get("createdAt") or ""))
    for row in suspects[:3]:
        path = "/api/heartbeat-runs/" + row["id"]
        detail = client.get(path)
        if isinstance(detail, dict) and detail.get("companyId") == client.company:
            runs[row["id"]] = {**row, **detail}
        else:
            client.problems.append("run_detail_unavailable:" + row["id"])
        # afterSeq uses the observed high-water mark; this is a bounded recent tail.
        end = detail.get("nextEventSeq") if isinstance(detail, dict) else None
        cursor = max(0, end - 101) if isinstance(end, int) else (baseline or {}).get("eventCursors", {}).get(row["id"], 0)
        tail = client.rows(path + "/events", {"afterSeq": cursor, "limit": 100})
        if len(tail) == 100 or end is None:
            client.problems.append("event_window_partial:" + row["id"])
        events[row["id"]] = tail
        # Bounded log inspection exposes only pattern hints, never raw text.
        count = row.get("logBytes")
        if isinstance(count, int) and count > 0:
            log = client.get(path + "/log", {"offset": max(0, count - 32768), "limitBytes": 32768})
            if isinstance(log, dict):
                text = str(log.get("content", ""))
                structured = []
                for line in text.splitlines():
                    try:
                        item = json.loads(line)
                    except ValueError:
                        continue
                    if not isinstance(item, dict) or item.get("type") != "tool_use":
                        continue
                    part = item.get("part") or {}
                    if not isinstance(part, dict):
                        client.problems.append("log_structure_unavailable:" + row["id"])
                        continue
                    state = part.get("state") or {}
                    if not isinstance(state, dict):
                        client.problems.append("log_structure_unavailable:" + row["id"])
                        continue
                    if state.get("status") in {"completed", "error"} and "input" in state:
                        structured.extend([
                            {"eventType": "tool.call", "payload": {"tool": part.get("tool"), "input": state["input"]}},
                            {"eventType": "tool.result", "payload": {"status": state["status"], "output": state.get("output"), "error": state.get("error")}},
                        ])
                if structured and not any(e.get("eventType") in {"tool.call", "tool_call", "action"} for e in tail):
                    events[row["id"]] = structured
                if re.search(r"rate.?limit|too many requests|please wait", text, re.I):
                    log_signals.append({"runId": row["id"], "hint": "possible_rate_limit_wait"})
    if len(suspects) > 3:
        client.problems.append("anomaly_details_truncated")
    return {"companyId": client.company, "observerId": observer, "observerRunId": run_id,
            "agents": [a for a in agents if a.get("id")], "issues": list({i["id"]: i for i in issues if i.get("id")}.values()),
            "runs": list(runs.values()), "events": events, "costs": safe_costs,
            "usageFrom": usage_from, "coverage": client.problems, "logSignals": log_signals}


def encode(snapshot):
    raw = json.dumps(snapshot, sort_keys=True, separators=(",", ":"))
    if len(raw.encode()) > MAX_OUTPUT:
        # Keep outcome and coverage honest rather than printing invalid/truncated JSON.
        snapshot = {**snapshot, "agents": [], "findings": snapshot["findings"][:20],
                    "coverage": ["output_truncated"], "outcome": "unknown" if snapshot["outcome"] == "healthy" else snapshot["outcome"]}
        raw = json.dumps(snapshot, sort_keys=True, separators=(",", ":"))
    if len(raw.encode()) > MAX_OUTPUT:
        raw = json.dumps({"schemaVersion": 1, "outcome": "unknown", "coverage": ["output_truncated"], "correctiveActionsTaken": False})
    return raw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, help="previous completed report's JSON snapshot")
    args = parser.parse_args()
    try:
        env = {k: os.environ[k] for k in ("PAPERCLIP_API_URL", "PAPERCLIP_API_KEY", "PAPERCLIP_COMPANY_ID", "PAPERCLIP_AGENT_ID", "PAPERCLIP_RUN_ID")}
        baseline = json.loads(args.baseline.read_text()) if args.baseline else None
        if baseline is not None and not isinstance(baseline, dict):
            raise ValueError("invalid_baseline")
        client = Client(env["PAPERCLIP_API_URL"], env["PAPERCLIP_API_KEY"], env["PAPERCLIP_COMPANY_ID"])
        now = datetime.now(timezone.utc)
        data = collect(client, env["PAPERCLIP_AGENT_ID"], env["PAPERCLIP_RUN_ID"], now, baseline)
        snapshot = analyze(data, baseline, now)
        snapshot["logSignals"] = data["logSignals"]
        snapshot["eventCursors"] = {rid: max((e.get("seq", 0) for e in events), default=0) for rid, events in data["events"].items()}
        print(encode(snapshot))
        return 0 if not snapshot["coverage"] else 2
    except (KeyError, ValueError, OSError):
        print(json.dumps({"schemaVersion": 1, "outcome": "unknown", "coverage": ["configuration_or_baseline_unavailable"], "correctiveActionsTaken": False}))
        return 2
    except (TypeError, AttributeError):
        print(json.dumps({"schemaVersion": 1, "outcome": "unknown", "coverage": ["telemetry_or_baseline_structure_unavailable"], "correctiveActionsTaken": False}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
