"""Offline checks of progress detection, API boundaries, and collection limits."""
import copy
import io
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.parse
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from aoc_watchdog import Client, NoRedirect, collect, encode, main
from aoc_watchdog_checks import analyze, event_patterns

NOW = datetime(2026, 10, 10, 16, 0, tzinfo=timezone.utc)


def ago(minutes):
    return (NOW - timedelta(minutes=minutes)).isoformat()


def sample():
    return {"companyId": "company", "observerId": "watchdog", "observerRunId": "current",
            "agents": [{"id": "solver", "name": "Problem Solver", "status": "running"},
                       {"id": "watchdog", "name": "WatchDog", "status": "running"}],
            "issues": [{"id": "issue", "title": "Solve day 01 part 1", "status": "in_progress",
                        "assigneeAgentId": "solver", "createdAt": ago(30), "updatedAt": ago(10)}],
            "runs": [{"id": "run", "agentId": "solver", "status": "running", "issueId": "issue",
                      "createdAt": ago(30), "startedAt": ago(30), "lastUsefulActionAt": ago(2)}],
            "events": {}, "coverage": [], "costs": [
                {"agentId": "solver", "costCents": 10, "inputTokens": 100, "outputTokens": 20}],
            "usageFrom": NOW.replace(hour=0).isoformat()}


def pairs(count=3, alternating=False):
    events = []
    for n in range(count):
        events.extend([
            {"seq": 2*n, "eventType": "tool.call", "payload": {"id": n, "command": "B" if alternating and n%2 else "A"}},
            {"seq": 2*n+1, "eventType": "tool.result", "payload": {"id": n, "output": "same"}},
        ])
    return events


class ChecksTest(unittest.TestCase):
    def setUp(self):
        self.data = sample()
        self.baseline = analyze(copy.deepcopy(self.data), now=NOW-timedelta(minutes=10))

    def check(self):
        return analyze(self.data, self.baseline, NOW)

    def codes(self):
        return {f["code"] for f in self.check()["findings"]}

    def test_productive_work_and_current_observer(self):
        self.data["runs"].append({"id": "current", "agentId": "watchdog", "status": "running", "createdAt": ago(30)})
        self.assertEqual(self.check()["outcome"], "healthy")
        self.assertFalse(self.check()["correctiveActionsTaken"])

    def test_quiet_build_with_recent_progress(self):
        self.data["runs"][0]["lastOutputAt"] = ago(30)
        self.assertNotIn("suspected_stall", self.codes())

    def test_twenty_minute_boundary(self):
        self.data["runs"][0]["lastUsefulActionAt"] = ago(19)
        self.assertNotIn("suspected_stall", self.codes())
        self.data["runs"][0]["lastUsefulActionAt"] = ago(20)
        self.assertIn("suspected_stall", self.codes())
        self.assertEqual(self.check()["outcome"], "warning")

    def test_missing_progress_timestamp_uses_run_start(self):
        self.data["runs"][0].pop("lastUsefulActionAt")
        self.assertIn("suspected_stall", self.codes())

    def test_legitimate_blocker_and_wait(self):
        self.data["issues"][0]["status"] = "blocked"
        self.data["runs"][0]["lastUsefulActionAt"] = ago(30)
        self.assertNotIn("suspected_stall", self.codes())
        self.data["issues"][0]["status"] = "in_progress"
        self.data["runs"][0]["livenessState"] = "blocked"
        self.assertNotIn("suspected_stall", self.codes())

    def test_paused_specialist_is_expected(self):
        self.data["runs"] = []
        self.data["agents"][0]["status"] = "paused"
        self.assertNotIn("assignment_without_active_run", self.codes())

    def test_paused_with_active_run_is_anomaly(self):
        self.data["agents"][0]["status"] = "paused"
        self.assertIn("paused_agent_with_active_run", self.codes())

    def test_stranded_assignment(self):
        self.data["runs"] = []
        self.data["issues"][0]["updatedAt"] = ago(20)
        self.assertIn("assignment_without_active_run", self.codes())

    def failed_attempts(self):
        self.data["runs"] = [{"id": f"r{n}", "agentId": "solver", "status": "succeeded", "livenessState": "plan_only",
                              "issueId": "issue", "createdAt": ago(n+1)} for n in range(3)]

    def test_three_attempts_same_issue(self):
        self.failed_attempts()
        self.assertIn("repeated_no_progress_attempts", self.codes())
        self.data["runs"].pop()
        self.assertNotIn("repeated_no_progress_attempts", self.codes())

    def test_completed_task_suppresses_old_failed_attempts(self):
        self.failed_attempts()
        self.data["issues"][0]["status"] = "done"
        self.assertNotIn("repeated_no_progress_attempts", self.codes())

    def test_different_tasks_are_not_retries(self):
        self.failed_attempts()
        self.data["runs"][0]["issueId"] = "other"
        self.assertNotIn("repeated_no_progress_attempts", self.codes())

    def test_actual_progress_breaks_retry_alert(self):
        self.failed_attempts()
        self.data["runs"][0]["lastUsefulActionAt"] = ago(1)
        self.assertNotIn("repeated_no_progress_attempts", self.codes())

    def test_identical_and_alternating_action_pairs(self):
        self.assertEqual(event_patterns(pairs()), "repeated_action_result")
        self.assertEqual(event_patterns(pairs(6, True)), "alternating_action_result")
        self.assertIsNone(event_patterns(pairs(2)))
        events = pairs()
        events[-1]["payload"]["output"] = "new result"
        self.assertIsNone(event_patterns(events))

    def test_chatter_is_not_a_loop(self):
        self.assertIsNone(event_patterns([{"eventType": "log", "payload": {"text": "thinking"}}]*10))

    def test_repetition_with_measured_spend_is_critical(self):
        self.data["events"]["run"] = pairs()
        self.data["costs"][0]["inputTokens"] += 50
        self.assertEqual(self.check()["outcome"], "critical")

    def test_missing_usage_not_zero_or_critical(self):
        self.data["events"]["run"] = pairs()
        self.data["costs"] = []
        self.assertEqual(self.check()["outcome"], "warning")
        self.assertIsNone(self.check()["agents"][0]["usageDelta"])

    def test_midnight_resets_delta_baseline(self):
        self.baseline["agents"][0]["usageFrom"] = ago(1440)
        self.assertIsNone(self.check()["agents"][0]["usageDelta"])

    def test_missing_and_cross_company_baseline(self):
        self.assertEqual(analyze(self.data, now=NOW)["outcome"], "unknown")
        self.baseline["companyId"] = "other"
        self.assertIn("baseline_invalid_or_stale", self.check()["coverage"])

    def test_partial_coverage_cannot_be_healthy(self):
        self.data["coverage"] = ["http_403:telemetry"]
        self.assertEqual(self.check()["outcome"], "unknown")

    def test_reports_do_not_block_puzzle_pipeline(self):
        self.data["issues"].append({"id": "report", "title": "WatchDog check day 02 part 2", "status": "in_progress",
                                    "assigneeAgentId": "watchdog", "createdAt": ago(1)})
        self.assertNotIn("multiple_active_puzzle_parts", self.codes())

    def test_duplicate_stage_and_multiple_parts(self):
        extra = dict(self.data["issues"][0], id="duplicate")
        self.data["issues"].append(extra)
        self.assertIn("duplicate_active_stage", self.codes())
        extra["title"] = "Solve day 02 part 1"
        self.assertIn("multiple_active_puzzle_parts", self.codes())

    def test_same_part_handoff_overlap_is_valid(self):
        self.data["issues"].append(dict(self.data["issues"][0], id="handoff", assigneeAgentId="submitter"))
        self.assertNotIn("multiple_active_puzzle_parts", self.codes())
        self.assertNotIn("duplicate_active_stage", self.codes())

    def test_missing_handoff_is_window_observation(self):
        self.data["issues"][0].update(status="done", updatedAt=ago(25))
        self.assertIn("handoff_not_observed_in_window", self.codes())

    def test_orphaned_report_no_correction(self):
        self.data["issues"].append({"id": "old", "title": "WatchDog check previous", "status": "in_progress",
                                    "assigneeAgentId": "watchdog", "createdAt": ago(25)})
        self.assertIn("unfinished_watchdog_report", self.codes())
        self.assertFalse(self.check()["correctiveActionsTaken"])

    def test_missing_timer_not_paused_heartbeat(self):
        agent = self.data["agents"][1]
        agent["runtimeConfig"] = {"heartbeat": {"enabled": True}}
        self.data["runs"].append({"id": "timer", "agentId": "watchdog", "status": "succeeded", "invocationSource": "timer", "createdAt": ago(25)})
        self.assertIn("missing_scheduled_run", self.codes())
        agent["status"] = "paused"
        self.assertNotIn("missing_scheduled_run", self.codes())


class TransportTest(unittest.TestCase):
    def client(self):
        client = Client("http://localhost:3100", "SECRET", "company")
        client.opener = Mock()
        return client

    def test_get_only_and_allowed_endpoints(self):
        client = self.client()
        client.opener.open.return_value = io.BytesIO(b"[]")
        self.assertEqual(client.get("/api/companies/company/agents"), [])
        request = client.opener.open.call_args.args[0]
        self.assertEqual(request.get_method(), "GET")
        self.assertIsNone(request.data)
        for path in ("/api/agents/x/pause", "/api/heartbeat-runs/x/cancel", "/api/companies/other/issues", "https://other/"):
            with self.assertRaises(ValueError): client.get(path)

    def test_no_redirect_credential_forwarding(self):
        self.assertIsNone(NoRedirect().redirect_request(None, None, 302, "redirect", {}, "https://other/"))

    def test_http_failure_no_retry_no_secret(self):
        client = self.client()
        client.opener.open.side_effect = urllib.error.HTTPError("http://local", 403, "SECRET", {}, None)
        self.assertIsNone(client.get("/api/companies/company/agents"))
        self.assertEqual(client.opener.open.call_count, 1)
        self.assertNotIn("SECRET", str(client.problems))

    def test_one_safe_network_retry(self):
        client = self.client()
        client.opener.open.side_effect = [TimeoutError(), TimeoutError()]
        self.assertIsNone(client.get("/api/companies/company/agents"))
        self.assertEqual(client.opener.open.call_count, 2)

    def test_deadline_prevents_requests(self):
        client = self.client()
        client.until = 0
        self.assertIsNone(client.get("/api/companies/company/agents"))
        client.opener.open.assert_not_called()

    def test_wrong_company_filtered(self):
        client = self.client()
        client.get = Mock(return_value=[{"id": "foreign", "companyId": "other"}])
        self.assertEqual(client.rows("/api/companies/company/agents"), [])
        self.assertTrue(client.problems)

    def test_bounded_body_and_wrong_response_shape(self):
        client = self.client()
        client.opener.open.return_value = io.BytesIO(b"x"*(1024*1024+1))
        self.assertIsNone(client.get("/api/companies/company/agents"))
        self.assertIn("response_too_large", str(client.problems))
        client.get = Mock(return_value={"items": []})
        self.assertEqual(client.rows("/api/companies/company/agents"), [])

    def test_bounded_valid_json_output(self):
        result = analyze(sample(), now=NOW)
        result["agents"][0]["name"] = "x"*100000
        encoded = encode(result)
        self.assertLessEqual(len(encoded.encode()), 32768)
        self.assertIn("output_truncated", json.loads(encoded)["coverage"])
        self.assertNotEqual(json.loads(encoded)["outcome"], "healthy")


class CollectionTest(unittest.TestCase):
    def test_malformed_nested_telemetry_is_unknown_json(self):
        data = sample()
        data["agents"][0]["runtimeConfig"] = "unexpected"
        env = {"PAPERCLIP_" + name: value for name, value in {
            "API_URL": "http://localhost", "API_KEY": "fixture-only", "COMPANY_ID": "company",
            "AGENT_ID": "watchdog", "RUN_ID": "current"}.items()}
        output = io.StringIO()
        with patch.dict(os.environ, env), patch.object(sys, "argv", ["watchdog"]), \
                patch("aoc_watchdog.collect", return_value=data), patch("sys.stdout", output):
            self.assertEqual(main(), 2)
        result = json.loads(output.getvalue())
        self.assertEqual(result["outcome"], "unknown")
        self.assertIn("telemetry_or_baseline_structure_unavailable", result["coverage"])
        self.assertNotIn("fixture-only", output.getvalue())

    def fake_client(self):
        client = Mock()
        client.company, client.problems = "company", []
        data = sample()
        def rows(path, params=None):
            if path.endswith("/agents"): return data["agents"]
            if path.endswith("/issues"): return data["issues"] if params["status"] != "done" else []
            if path.endswith("/live-runs") or path.endswith("/heartbeat-runs"):
                return data["runs"] if path.endswith("/live-runs") or params["agentId"] == "solver" else []
            if path.endswith("/costs/by-agent"): return data["costs"]
            return []
        client.rows.side_effect = rows
        return client, data

    def test_healthy_collection_summaries_only(self):
        client, _ = self.fake_client()
        result = collect(client, "watchdog", "current", NOW)
        client.get.assert_not_called()
        self.assertEqual(len(result["agents"]), 2)
        calls = [c for c in client.rows.call_args_list if c.args[0].endswith("/heartbeat-runs")]
        self.assertTrue(all(c.args[1]["summary"] == "true" for c in calls))

    def test_opencode_log_repetition_and_correct_event_cursor(self):
        client, data = self.fake_client()
        data["runs"][0].update(lastUsefulActionAt=ago(25), logBytes=40000)
        logs = "\n".join(json.dumps({"type": "tool_use", "part": {"tool": "bash", "state": {
            "status": "error", "input": {"cmd": "same"}, "error": "SECRET"}}}) for _ in range(3))
        def get(path, params=None):
            if path.endswith("/log"):
                self.assertEqual(params["limitBytes"], 32768)
                return {"content": logs}
            return {"companyId": "company", "nextEventSeq": 350}
        client.get.side_effect = get
        collected = collect(client, "watchdog", "current", NOW)
        self.assertEqual(event_patterns(collected["events"]["run"]), "repeated_action_result")
        self.assertNotIn("SECRET", encode(analyze(collected, now=NOW)))
        call = next(c for c in client.rows.call_args_list if c.args[0].endswith("/events"))
        self.assertEqual(call.args[1]["afterSeq"], 249)

    def test_pagination_truncation_explicit(self):
        client, _ = self.fake_client()
        original = client.rows.side_effect
        client.rows.side_effect = lambda p, q=None: [{"id": f"i{n}"} for n in range(100)] if p.endswith("/issues") else original(p, q)
        collect(client, "watchdog", "current", NOW)
        self.assertIn("issue_inventory_truncated:done", client.problems)


class HttpIntegrationTest(unittest.TestCase):
    def test_cli_collects_authenticated_gets_and_compares_baseline(self):
        now = datetime.now(timezone.utc)
        data = sample()
        data["runs"][0].update(createdAt=(now-timedelta(minutes=30)).isoformat(),
                               startedAt=(now-timedelta(minutes=30)).isoformat(),
                               lastUsefulActionAt=(now-timedelta(minutes=2)).isoformat())
        data["issues"][0]["updatedAt"] = now.isoformat()
        data["usageFrom"] = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        baseline = analyze(copy.deepcopy(data), now=now-timedelta(minutes=1))
        baseline["agents"][0]["usage"]["costCents"] = 5
        requests = []

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass

            def do_GET(self):
                requests.append((self.command, self.headers.get("Authorization"), self.path))
                parsed = urllib.parse.urlsplit(self.path)
                query = urllib.parse.parse_qs(parsed.query)
                path = parsed.path
                if path.endswith("/agents"):
                    body = data["agents"]
                elif path.endswith("/issues"):
                    body = [] if query["status"] == ["done"] else data["issues"]
                elif path.endswith("/live-runs"):
                    body = data["runs"]
                elif path.endswith("/heartbeat-runs"):
                    body = data["runs"] if query["agentId"] == ["solver"] else []
                elif path.endswith("/costs/by-agent"):
                    body = data["costs"]
                else:
                    self.send_error(404)
                    return
                encoded = json.dumps(body).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "baseline.json"
                path.write_text(json.dumps(baseline))
                env = {**os.environ, "PAPERCLIP_API_URL": f"http://127.0.0.1:{server.server_port}",
                       "PAPERCLIP_API_KEY": "fixture-only", "PAPERCLIP_COMPANY_ID": "company",
                       "PAPERCLIP_AGENT_ID": "watchdog", "PAPERCLIP_RUN_ID": "current"}
                process = subprocess.run([sys.executable, "-B", str(Path(__file__).resolve().parents[1] / "aoc_watchdog.py"),
                                          "--baseline", str(path)], env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(process.returncode, 0, process.stderr)
            result = json.loads(process.stdout)
            self.assertEqual(result["outcome"], "healthy")
            self.assertEqual(result["coverage"], [])
            self.assertEqual(result["agents"][0]["usageDelta"]["costCents"], 5)
            self.assertFalse(result["correctiveActionsTaken"])
            self.assertEqual(len(requests), 7)
            self.assertTrue(all(method == "GET" and auth == "Bearer fixture-only" for method, auth, _ in requests))
            self.assertNotIn("fixture-only", process.stdout)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
