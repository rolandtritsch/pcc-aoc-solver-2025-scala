"""Lifecycle integration tests with actual HTTP and realistic Paperclip log records."""
import copy
import io
import json
import os
import sys
import threading
import time
import unittest
import urllib.error
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import aoc_watchdog_runner as runner
from aoc_watchdog import collect
from aoc_watchdog_checks import analyze

NOW = datetime.now(timezone.utc)


def snapshot(findings=None):
    return {"schemaVersion": 1, "companyId": "company", "observerId": "watchdog", "observerRunId": "current",
            "observedAt": NOW.isoformat(), "outcome": "warning" if findings else "healthy", "coverage": [],
            "agents": [], "findings": findings or [], "correctiveActionsTaken": False}


def warning():
    return {"code": "provider_credit_rejection", "severity": "warning", "agentId": "solver", "issueId": None, "runId": "r1"}


class InterpretationTest(unittest.TestCase):
    def setUp(self):
        self.env = {"OPENROUTER_API_KEY": "secret-provider", "PAPERCLIP_API_KEY": "secret-paperclip"}
        self.calls = []

    def model(self, snap, env):
        self.calls.append(snap)
        return {"status": "completed", "text": "Inspect provider credits.", "usage": {"prompt_tokens": 30, "completion_tokens": 10, "cost": .001}}

    def test_healthy_never_calls_model(self):
        result = runner.optional_interpretation(snapshot(), None, self.env, NOW, self.model)
        self.assertEqual(result["reason"], "no_anomalies")
        self.assertFalse(self.calls)

    def test_changed_anomaly_calls_once_unchanged_does_not(self):
        snap = snapshot([warning()])
        first = runner.optional_interpretation(snap, None, self.env, NOW, self.model)
        snap["findings"][0]["runId"] = "different-retry"
        second = runner.optional_interpretation(snap, {"interpretation": first}, self.env, NOW, self.model)
        self.assertEqual(second["reason"], "unchanged_anomalies")
        self.assertEqual(len(self.calls), 1)
        snap["findings"][0]["code"] = "suspected_stall"
        runner.optional_interpretation(snap, {"interpretation": second}, self.env, NOW, self.model)
        self.assertEqual(len(self.calls), 2)

    def test_failed_provider_cooldown_survives_skipped_runs_then_recovers(self):
        snap = snapshot([warning()])
        failed = runner.optional_interpretation(snap, None, self.env, NOW,
                                                lambda *_: {"status": "unavailable", "reason": "model_http_402"})
        skipped = runner.optional_interpretation(snap, {"interpretation": failed}, self.env, NOW + timedelta(minutes=10), self.model)
        self.assertEqual(skipped["reason"], "provider_cooldown")
        self.assertFalse(self.calls)
        recovered = runner.optional_interpretation(snap, {"interpretation": skipped}, self.env, NOW + timedelta(minutes=61), self.model)
        self.assertEqual(recovered["status"], "completed")
        self.assertIsNone(recovered["cooldownUntil"])
        self.assertEqual(len(self.calls), 1)

    def test_model_exception_cannot_discard_findings(self):
        snap = snapshot([warning()])
        def fail(*_):
            raise TimeoutError()
        result = runner.optional_interpretation(snap, None, self.env, NOW, fail)
        self.assertEqual(result["status"], "unavailable")
        self.assertEqual(snap["findings"], [warning()])

    def test_wire_request_is_flash_bounded_and_tool_free(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *_): pass
            def read(self, _):
                return json.dumps({"choices": [{"message": {"content": "Inspect credits."}}],
                                   "usage": {"prompt_tokens": 20, "completion_tokens": 10, "cost": .002}}).encode()
        class Opener:
            def open(inner, request, timeout):
                body = json.loads(request.data)
                self.assertEqual(body["max_tokens"], 2048)
                self.assertEqual(body["model"], runner.MODEL)
                self.assertNotIn("tools", body)
                self.assertNotIn("secret-provider", request.data.decode())
                self.assertNotIn("secret-paperclip", request.data.decode())
                self.assertLessEqual(timeout, 30)
                return Response()
        with patch.object(runner.urllib.request, "build_opener", return_value=Opener()):
            result = runner.interpret(snapshot([warning()]), self.env)
        self.assertEqual(result["usage"]["cost"], .002)

    def test_empty_malformed_and_denied_model_responses(self):
        class Response:
            content = b'{"choices":[{"message":{"content":""}}],"usage":{"completion_tokens":12}}'
            def __enter__(self): return self
            def __exit__(self, *_): pass
            def read(self, _): return self.content
        with patch.object(runner.urllib.request, "build_opener") as factory:
            factory.return_value.open.return_value = Response()
            result = runner.interpret(snapshot([warning()],), self.env)
            self.assertEqual(result["reason"], "model_empty_output")
            self.assertEqual(result["usage"]["completion_tokens"], 12)
            Response.content = b'not-json'
            self.assertEqual(runner.interpret(snapshot([warning()]), self.env)["status"], "unavailable")
            factory.return_value.open.side_effect = urllib.error.HTTPError("url", 402, "denied", {}, None)
            self.assertEqual(runner.interpret(snapshot([warning()]), self.env)["reason"], "model_http_402")


class LifecycleTest(unittest.TestCase):
    def setUp(self):
        self.writes, self.reads, self.reports = [], [], []
        self.deny_post = False
        outer = self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_): pass
            def reply(self, body, status=200):
                raw = json.dumps(body).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)
            def do_GET(self):
                outer.assertEqual(self.headers.get("Authorization"), "Bearer paperclip-secret")
                url = urlsplit(self.path)
                params = parse_qs(url.query)
                outer.reads.append(url.path)
                if url.path.endswith("/issues"):
                    outer.assertIn(params.get("sortField", ["updated"])[0], ["updated", "id"])
                    rows = outer.reports
                    q = params.get("q", [None])[0]
                    if q: rows = [r for r in rows if q in r["description"]]
                    self.reply([{**r, "description": r["description"][:500]} for r in rows])
                elif url.path.startswith("/api/issues/"):
                    row = next((r for r in outer.reports if r["id"] == url.path.rsplit("/", 1)[-1]), None)
                    self.reply(row or {}, 200 if row else 404)
                elif url.path.endswith("/agents"):
                    self.reply([{"id": "watchdog", "companyId": "company", "name": "WatchDog", "status": "running",
                                 "runtimeConfig": {"heartbeat": {"enabled": True, "intervalSec": 600}}}])
                elif url.path.endswith("/heartbeat-runs"):
                    self.reply([{"id": outer.env["PAPERCLIP_RUN_ID"], "agentId": "watchdog", "companyId": "company", "status": "running",
                                 "invocationSource": "timer", "createdAt": NOW.isoformat()}] + [{"id": "prior-timer", "agentId": "watchdog", "companyId": "company", "status": "succeeded", "invocationSource": "timer", "createdAt": NOW.isoformat()}])
                elif url.path.endswith("/live-runs"):
                    self.reply([])
                elif url.path.endswith("/costs/by-agent"):
                    self.reply([{"agentId": "watchdog", "costCents": 1, "inputTokens": 10, "outputTokens": 5}])
                else: self.reply({}, 404)
            def do_POST(self):
                outer.assertEqual(self.path, "/api/companies/company/issues")
                outer.assertEqual(self.headers.get("X-Paperclip-Run-Id"), outer.env["PAPERCLIP_RUN_ID"])
                outer.assertEqual(self.headers.get("Authorization"), "Bearer paperclip-secret")
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                outer.writes.append(body)
                if outer.deny_post:
                    self.reply({"error": "forbidden"}, 403)
                    return
                outer.assertEqual(body["status"], "done")
                outer.assertEqual(body["assigneeAgentId"], "watchdog")
                outer.assertIsNone(body["parentId"])
                same = next((r for r in outer.reports if r.get("idempotencyKey") == body["idempotencyKey"]), None)
                if not same:
                    same = {**body, "id": "report-1", "identifier": "AOC-999", "companyId": "company", "createdAt": NOW.isoformat()}
                    outer.reports.insert(0, same)
                self.reply(same, 201)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.env = {"PAPERCLIP_API_URL": "http://127.0.0.1:" + str(self.server.server_port), "PAPERCLIP_API_KEY": "paperclip-secret",
                    "PAPERCLIP_COMPANY_ID": "company", "PAPERCLIP_AGENT_ID": "watchdog", "PAPERCLIP_RUN_ID": "current",
                    "PAPERCLIP_WAKE_REASON": "heartbeat_timer", "AOC_PAPERCLIP_UI_URL": "https://paperclip.example/AOC", "AOC_CYCLE_STARTED_AT": "2026-10-10T18:11:00Z"}

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def test_real_collector_creates_done_report_and_same_run_reuses(self):
        report, snap = runner.run(self.env, model=lambda *_: self.fail("no anomaly needs model"))
        self.assertEqual(report["status"], "done")
        self.assertEqual(snap["outcome"], "unknown")  # First check has no usage baseline.
        self.assertIn("completed_watchdog_report_unavailable", snap["coverage"])
        again, reused = runner.run(self.env)
        self.assertEqual(again["id"], report["id"])
        self.assertIsNone(reused)
        self.assertEqual(len(self.writes), 1)
        self.assertNotIn("paperclip-secret", report["description"])
        self.assertIn("watchdog-snapshot", report["description"])

    def test_next_run_reads_full_baseline_despite_list_preview(self):
        runner.run(self.env)
        self.env["PAPERCLIP_RUN_ID"] = "next"
        report, snap = runner.run(self.env)
        self.assertNotIn("usage_trend_baseline_unavailable", snap["coverage"])
        self.assertIn("Previous report", report["description"])
        self.assertIn("https://paperclip.example/AOC/issues/", report["description"])
        self.assertEqual(snap["outcome"], "healthy", snap["coverage"])

    def test_collection_failure_persists_partial_report(self):
        def fail(*_): raise TimeoutError()
        report, snap = runner.run(self.env, collector=fail)
        self.assertEqual(report["status"], "done")
        self.assertEqual(snap["outcome"], "unknown")
        self.assertIn("collection_deadline_or_failure", snap["coverage"])

    def test_model_failure_persists_warning_and_cooldown(self):
        def collector(client, observer, run_id, now, baseline):
            return {"companyId": "company", "observerId": observer, "observerRunId": run_id, "coverage": [],
                    "agents": [{"id": "solver", "name": "Problem Solver", "status": "error"}], "issues": [],
                    "runs": [{"id": "r1", "agentId": "solver", "status": "failed", "createdAt": now.isoformat(), "error": "Not enough credits"}], "costs": []}
        report, snap = runner.run(self.env, collector=collector, model=lambda *_: {"status": "unavailable", "reason": "model_http_402"})
        self.assertEqual(report["status"], "done")
        self.assertEqual(snap["outcome"], "warning")
        self.assertIn("provider_credit_rejection", report["description"])
        self.assertIn("model_http_402", report["description"])
        self.assertIsNotNone(snap["interpretation"]["cooldownUntil"])

    def test_lost_post_response_reconciles_without_duplicate(self):
        original = runner.Reports.post
        def lost(reports, body):
            original(reports, body)
            raise urllib.error.URLError("lost response")
        with patch.object(runner.Reports, "post", lost):
            report, _ = runner.run(self.env)
        self.assertEqual(report["status"], "done")
        self.assertEqual(len(self.writes), 1)
        self.assertEqual(len(self.reports), 1)

    def test_denied_post_is_not_retried_and_run_fails(self):
        self.deny_post = True
        output = io.StringIO()
        with patch.dict(os.environ, self.env), redirect_stdout(output):
            code = runner.main(["run"], self.env)
        self.assertEqual(code, 1)
        self.assertEqual(len(self.writes), 1)
        self.assertIn("failed to persist", output.getvalue())
        self.assertNotIn("paperclip-secret", output.getvalue())

    def test_non_timer_wake_has_no_calls(self):
        self.env["PAPERCLIP_WAKE_REASON"] = "issue_assigned"
        with redirect_stdout(io.StringIO()):
            self.assertEqual(runner.main(["run"], self.env), 0)
        self.assertFalse(self.reads)
        self.assertFalse(self.writes)


class EvidenceTest(unittest.TestCase):
    def test_cycle_filter_and_cto_review_wait(self):
        now = datetime.now(timezone.utc)
        data = {"companyId": "company", "observerId": "watchdog", "coverage": [], "cycleStartedAt": "2026-10-10T18:11:00Z",
                "agents": [{"id": "cto", "name": "CTO", "status": "idle"}, {"id": "reviewer", "name": "Solution Reviewer", "status": "idle"}],
                "issues": [{"id": "old", "title": "Day01 part1", "createdAt": "2026-10-09T00:00:00Z", "updatedAt": "2026-10-09T00:00:00Z", "status": "in_progress", "assigneeAgentId": "cto"},
                           {"id": "review", "title": "Day05 part1 review", "createdAt": now.isoformat(), "updatedAt": now.isoformat(), "status": "in_progress", "assigneeAgentId": "reviewer"}], "runs": []}
        result = analyze(data, now=now)
        self.assertEqual(result["agents"][0]["activity"], "expected_wait")
        self.assertEqual(result["agents"][0]["assignedIssueIds"], [])
        self.assertNotIn("multiple_active_puzzle_parts", [f["code"] for f in result["findings"]])

    def test_phase_deadline_interrupts_blocking_operation(self):
        started = time.monotonic()
        with self.assertRaises(TimeoutError), runner.bounded(.02):
            time.sleep(.5)
        self.assertLess(time.monotonic() - started, .2)

    def test_baseline_rejects_stale_future_and_wrong_observer(self):
        base = snapshot()
        base["observerRunId"] = "prior"
        report = {"id": "prior", "description": "```watchdog-snapshot\n" + json.dumps(base) + "\n```"}
        self.assertIsNotNone(runner.previous_snapshot([report], "company", "watchdog", "current", NOW)[0])
        for changes in [{"observerId": "other"}, {"observedAt": (NOW - timedelta(hours=2)).isoformat()}, {"observedAt": (NOW + timedelta(minutes=1)).isoformat()}]:
            changed = {**base, **changes}
            report["description"] = "```watchdog-snapshot\n" + json.dumps(changed) + "\n```"
            self.assertIsNone(runner.previous_snapshot([report], "company", "watchdog", "current", NOW)[0])


if __name__ == "__main__":
    unittest.main()
