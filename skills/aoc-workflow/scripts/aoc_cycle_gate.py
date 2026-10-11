#!/usr/bin/env python3
"""Read-only, fail-closed guard before CTO puzzle selection. No model or Git calls."""

import datetime as dt
import json
import os
import re
import sys
import time
import urllib.request

STAGES = {
    "Problem Gatherer": "gather", "Problem Solver": "solve",
    "Problem Submitter": "submit", "Solution Reviewer": "review",
}
OPEN = {"backlog", "todo", "in_progress", "in_review", "blocked"}


def timestamp(value):
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("cycle timestamp must include a timezone")
    return parsed


def part(issue):
    match = re.search(r"\bday\s*0*(\d+)\s*part\s*([12])\b", issue["title"], re.I)
    if not match:
        raise ValueError("unrecognized current pipeline task: " + issue["identifier"])
    return tuple(map(int, match.groups()))


def review_result(issue, comments):
    """Prefer an explicit result; accept completed legacy reports conservatively."""
    bodies = [c.get("body", "") for c in comments]
    for body in bodies:
        match = re.search(r"```aoc-review-result\s*(\{.*?\})\s*```", body, re.S)
        if match:
            result = json.loads(match.group(1))
            if result.get("reviewIssueId") != issue["id"]:
                raise ValueError("review result identity mismatch")
            if result.get("day") != part(issue)[0] or result.get("part") != part(issue)[1]:
                raise ValueError("review result part mismatch")
            if not result.get("solutionCommit"):
                raise ValueError("review result missing solution commit")
            attempt = re.search(r"attempt commit ([0-9a-f]{7,40})", issue["title"], re.I)
            if attempt and not result["solutionCommit"].startswith(attempt.group(1)):
                raise ValueError("review result solution commit mismatch")
            if result.get("accepted") is True and result.get("repairRequired") is False:
                return "accepted"
            if result.get("repairRequired") is True:
                return "repair"
            return "unknown"
    text = "\n".join(bodies).lower()
    accepted = re.search(r"(?:\*\*verdict:\*\*\s*accepted|review complete[^\n]*accepted)", text)
    no_repair = re.search(r"no puzzle repair(?: is)?(?: outstanding)?|no puzzle repair\." , text)
    return "accepted" if accepted and no_repair else "unknown"


def evaluate(issues, agents, since, comments, live_runs):
    start = timestamp(since)
    names = {a["id"]: a["name"] for a in agents}
    groups = {}
    for issue in issues:
        if timestamp(issue["createdAt"]) < start:
            continue
        stage = STAGES.get(names.get(issue.get("assigneeAgentId")))
        if not stage:
            continue
        groups.setdefault(part(issue), []).append((stage, issue))
    for selected in sorted(groups):
        entries = groups[selected]
        if all(i["status"] == "cancelled" for _, i in entries):
            continue
        open_issues = [i["identifier"] for _, i in entries if i["status"] in OPEN]
        if open_issues:
            return {"mode": "wait", "part": selected, "issues": open_issues,
                    "reason": "current cycle has unfinished stage tasks"}
        reviews = [i for stage, i in entries if stage == "review" and i["status"] == "done"]
        if not reviews:
            return {"mode": "wait", "part": selected, "reason": "completed review is missing"}
        latest = max(reviews, key=lambda i: timestamp(i["createdAt"]))
        result = review_result(latest, comments(latest["id"]))
        if result != "accepted":
            return {"mode": "repair" if result == "repair" else "wait", "part": selected,
                    "issues": [latest["identifier"]], "reason": "review has not cleared advancement"}
    running = [r["id"] for r in live_runs
               if names.get(r.get("agentId")) in STAGES]
    if running:
        return {"mode": "wait", "runs": running, "reason": "specialist run is still active"}
    return {"mode": "ready", "reason": "all current-cycle parts have successful completed reviews"}


def main():
    try:
        base = os.environ["PAPERCLIP_API_URL"].rstrip("/")
        company = os.environ["PAPERCLIP_COMPANY_ID"]
        token = os.environ["PAPERCLIP_API_KEY"]
        since = os.environ["AOC_CYCLE_STARTED_AT"]
        timestamp(since)
        deadline = time.monotonic() + 20

        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *args, **kwargs):
                return None

        opener = urllib.request.build_opener(NoRedirect)

        def get(path):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("gate telemetry deadline exceeded")
            request = urllib.request.Request(base + path, headers={"Authorization": "Bearer " + token})
            with opener.open(request, timeout=min(5, remaining)) as response:
                data = response.read(1024 * 1024 + 1)
                if len(data) > 1024 * 1024:
                    raise ValueError("gate response too large")
                result = json.loads(data)
                if not isinstance(result, list):
                    raise ValueError("gate response is not a list")
                return result

        prefix = "/api/companies/" + company
        agents = get(prefix + "/agents")
        issues = []
        for page in range(100):
            rows = get(prefix + "/issues?limit=100&offset=" + str(page * 100))
            issues.extend(rows)
            if len(rows) < 100:
                break
        else:
            raise ValueError("issue pagination exceeded bound")
        result = evaluate(issues, agents, since,
                          lambda id: get("/api/issues/" + id + "/comments"),
                          get(prefix + "/live-runs?minCount=0"))
        print(json.dumps(result))
        return 0 if result["mode"] == "ready" else 1
    except Exception as error:
        # Never echo request headers, credentials, or a provider response body.
        print(json.dumps({"mode": "unknown", "reason": type(error).__name__ + ": gate evidence unavailable"}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
