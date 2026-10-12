#!/usr/bin/env python3
"""Verify a solution, commit/push it, then create its same-part handoff."""
import argparse
import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import urllib.request


class GateError(RuntimeError):
    pass


def command(repo, args, timeout=900):
    # No shell/pipeline: a failed sbt or Git process cannot be hidden by tail.
    with tempfile.NamedTemporaryFile(mode="w+", prefix="aoc-publish-",
                                     suffix=".log", delete=False) as log:
        try:
            result = subprocess.run(args, cwd=repo, stdout=log,
                                    stderr=subprocess.STDOUT, timeout=timeout)
        except subprocess.TimeoutExpired:
            raise GateError(f"{args[0]} timed out; private diagnostics: {log.name}; no handoff permitted") from None
        log.seek(0)
        output = log.read()
    if result.returncode:
        # Never echo arbitrary Git/API diagnostics containing auth material.
        raise GateError(f"{args[0]} exited {result.returncode}; private diagnostics: {log.name}; no handoff permitted")
    Path(log.name).unlink()
    return re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", output)


def git(repo, *args):
    return command(repo, ["git", *args], 60).rstrip("\n")


def clean(repo):
    if git(repo, "status", "--porcelain"):
        raise GateError("Checkout is dirty; preserve work and reconcile before handoff")


def parity(repo, commit):
    clean(repo)
    head = git(repo, "rev-parse", "HEAD")
    tracking = git(repo, "rev-parse", "refs/remotes/origin/main")
    remote = git(repo, "ls-remote", "--exit-code", "origin", "refs/heads/main").split()[0]
    if head != commit or tracking != commit or remote != commit:
        raise GateError("Solution HEAD/tracking/live remote mismatch; no handoff permitted")


def verify(repo, day, part, answer, commit):
    git(repo, "fetch", "origin", "main")
    parity(repo, commit)
    output = command(repo, ["sbt", f"scalafmtCheckAll; testOnly aoc2025.Day{day:02}Test; test; run"])
    check_answer(output, day, part, answer)
    parity(repo, commit)
    return receipt(day, part, answer, commit)


def check_answer(output, day, part, answer):
    suite = f"aoc2025.Day{day:02}Test:"
    if suite not in output:
        raise GateError("Assigned day test suite did not execute")
    suite_output = output.split(suite, 1)[1].split("[success]", 1)[0]
    if not re.search(r"Passed: Total [1-9]\d*, Failed 0, Errors 0", suite_output):
        raise GateError("Assigned day has no recorded passing active tests")
    lines = re.findall(rf"^Day{day:02} - part{part}:\s*(\S+)\s*$", output, re.M)
    if lines != [answer]:
        raise GateError("Runner answer missing, ambiguous, or mismatched")


def receipt(day, part, answer, commit):
    return {"schema": "aoc-solver-publication-v1", "day": day, "part": part,
            "answer": answer, "commit": commit, "remote": "origin/main",
            "formatting": "passed", "tests": "passed", "runner": "passed",
            "remoteParity": True,
            "verifiedAt": datetime.datetime.now(datetime.timezone.utc).isoformat()}


def publish(repo, day, part, answer, files):
    if git(repo, "branch", "--show-current") != "main":
        raise GateError("Publish requires the canonical main checkout")
    allowed = {f"src/main/scala/aoc2025/Day{day:02}.scala",
               f"src/test/scala/aoc2025/Day{day:02}Test.scala",
               f"src/main/resources/inputs/Day{day:02}Test.txt",
               "src/main/scala/aoc2025/Main.scala"}
    if not files or not set(files) <= allowed:
        raise GateError("Only assigned solution/test/sample/Main files may be committed")
    for name in files:
        path = repo / name
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(repo):
            raise GateError("Intended file is missing or escapes the canonical checkout")
    # Reject foreign dirty work rather than staging/discarding it accidentally.
    status = git(repo, "status", "--porcelain", "-uall")
    dirty = {line[3:] for line in status.splitlines()}
    if not dirty <= set(files):
        raise GateError("Unrelated dirty files present; preserve them and reconcile")
    git(repo, "fetch", "origin", "main")
    git(repo, "merge-base", "--is-ancestor", "origin/main", "HEAD")
    scala = [name for name in files if name.endswith(".scala")]
    # scalafmtOnly deliberately includes untracked files, even with project.git=true.
    tasks = f"scalafmtOnly {' '.join(scala)}; scalafmtAll; scalafmtCheckAll; "
    tasks += f"testOnly aoc2025.Day{day:02}Test; test; run"
    output = command(repo, ["sbt", tasks])
    check_answer(output, day, part, answer)
    dirty = {line[3:] for line in git(repo, "status", "--porcelain", "-uall").splitlines()}
    if not dirty <= set(files):
        raise GateError("Formatting changed unrelated files; reconcile before committing")
    git(repo, "add", "--", *files)
    if git(repo, "diff", "--cached", "--name-only"):
        git(repo, "diff", "--cached", "--check")
        git(repo, "commit", "-m", f"Day{day:02}: solve part {part}",
            "-m", "Co-Authored-By: Paperclip <noreply@paperclip.ing>")
    commit = git(repo, "rev-parse", "HEAD")
    # Recheck the committed tree now that every new file is Git tracked.
    command(repo, ["sbt", "scalafmtCheckAll"])
    clean(repo)
    git(repo, "push", "origin", "HEAD:refs/heads/main")
    git(repo, "fetch", "origin", "main")
    parity(repo, commit)
    return receipt(day, part, answer, commit)


class Board:
    def __init__(self):
        self.base = os.environ["PAPERCLIP_API_URL"].rstrip("/")
        self.company = os.environ["PAPERCLIP_COMPANY_ID"]
        self.source = os.environ["PAPERCLIP_TASK_ID"]
        self.agent = os.environ["PAPERCLIP_AGENT_ID"]
        self.headers = {"Authorization": "Bearer " + os.environ["PAPERCLIP_API_KEY"],
                        "Content-Type": "application/json",
                        "X-Paperclip-Run-Id": os.environ["PAPERCLIP_RUN_ID"]}

    def call(self, path, body=None):
        req = urllib.request.Request(self.base + path, headers=self.headers,
                                     data=json.dumps(body).encode() if body else None)
        with urllib.request.urlopen(req, timeout=30) as result:
            return json.load(result)

    def prepare(self, payload, day, part):
        source = self.call("/api/issues/" + self.source)
        if source["companyId"] != self.company:
            raise GateError("Source task belongs to another company")
        if source.get("assigneeAgentId") != self.agent or source.get("status") != "in_progress":
            raise GateError("Source task is not the current agent's in-progress assignment")
        expected = rf"Day\s*0?{day}\s*part\s*{part}\b"
        self.part_pattern = expected
        if not re.search(expected, source["title"], re.I):
            raise GateError("Source assignment does not match requested day/part")
        agents = self.call("/api/companies/" + self.company + "/agents")
        recipients = [a for a in agents if a["name"] == "Problem Submitter"]
        if len(recipients) != 1:
            raise GateError("Missing or ambiguous Problem Submitter")
        if not isinstance(payload.get("description"), str) or not payload["description"].strip():
            raise GateError("Handoff needs upstream material and independent test evidence")
        self.cycle_start = os.environ["AOC_CYCLE_STARTED_AT"]
        self.payload = {"title": f"AoC 2025 Day{day:02} part{part}: submit (verified solve handoff)",
                        "description": payload["description"], "status": "todo",
                        "assigneeAgentId": recipients[0]["id"], "parentId": None}

    def handoff(self, evidence, before_create):
        # Stable source task marker also recovers a lost POST acknowledgement.
        marker = f"aoc-solver-source:{self.source}"
        offset = 0
        matches = []
        while True:
            rows = self.call(f"/api/companies/{self.company}/issues?limit=100&offset={offset}")
            for row in rows:
                # List descriptions can be truncated: inspect candidate details.
                if (row.get("assigneeAgentId") == self.payload["assigneeAgentId"]
                        and re.search(self.part_pattern, row["title"], re.I)):
                    item = self.call("/api/issues/" + row["id"])
                    if marker in (item.get("description") or ""):
                        matches.append(item)
                    elif (item["status"] not in ("done", "cancelled")
                          and item["createdAt"] >= self.cycle_start):
                        description = item.get("description") or ""
                        if (evidence["commit"] in description
                                and re.search(rf"\b{re.escape(evidence['answer'])}\b", description)):
                            # Adopt an exact legacy handoff after verifying its
                            # commit/answer; publication repair must not duplicate it.
                            matches.append(item)
                        else:
                            raise GateError("Existing same-part handoff needs reconciliation; no duplicate")
            if len(rows) < 100:
                break
            offset += len(rows)
            if offset >= 10000:
                raise GateError("Issue pagination limit reached; reconcile before retry")
        if len(matches) > 1:
            raise GateError("Duplicate handoffs exist; reconcile before retry")
        if matches:
            item = matches[0]
            if item["status"] == "cancelled" or evidence["commit"] not in item["description"]:
                raise GateError("Existing handoff is cancelled or belongs to another commit")
            before_create()
            return item
        before_create()
        self.payload["description"] += "\n\n" + marker + "\n```aoc-solver-publication\n"
        self.payload["description"] += json.dumps(evidence, sort_keys=True) + "\n```\n"
        item = self.call("/api/companies/" + self.company + "/issues", self.payload)
        confirmed = self.call("/api/issues/" + item["id"])
        if (confirmed.get("assigneeAgentId") != self.payload["assigneeAgentId"]
                or marker not in (confirmed.get("description") or "")):
            raise GateError("Handoff confirmation failed; reconcile before retry")
        return confirmed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["publish", "verify"])
    parser.add_argument("--repo", default=os.environ.get("AOC_REPO_DIR"))
    parser.add_argument("--day", type=int, required=True)
    parser.add_argument("--part", type=int, choices=[1, 2], required=True)
    parser.add_argument("--answer", required=True)
    parser.add_argument("--commit")
    parser.add_argument("--handoff", type=Path)
    parser.add_argument("--files", nargs="+")
    args = parser.parse_args(argv)
    try:
        if not args.repo or not 1 <= args.day <= 12 or not re.fullmatch(r"\d+", args.answer):
            raise GateError("Canonical repo, day 1–12, and numeric answer required")
        repo = Path(args.repo).resolve()
        canonical = os.environ.get("AOC_REPO_DIR")
        if canonical and repo != Path(canonical).resolve():
            raise GateError("Use the canonical AOC_REPO_DIR checkout")
        if args.mode == "verify":
            if not args.commit or not re.fullmatch(r"[0-9a-f]{40}", args.commit):
                raise GateError("Verification requires the full solution commit hash")
            evidence = verify(repo, args.day, args.part, args.answer, args.commit)
        else:
            if not args.handoff:
                raise GateError("Publish requires a prepared handoff JSON file")
            board = Board()
            board.prepare(json.loads(args.handoff.read_text()), args.day, args.part)
            files = args.files or [f"src/main/scala/aoc2025/Day{args.day:02}.scala",
                                  f"src/test/scala/aoc2025/Day{args.day:02}Test.scala",
                                  f"src/main/resources/inputs/Day{args.day:02}Test.txt",
                                  "src/main/scala/aoc2025/Main.scala"]
            evidence = publish(repo, args.day, args.part, args.answer, files)
            # The only creation call is after checks, commit, push, and remote parity.
            parity(repo, evidence["commit"])
            item = board.handoff(evidence, lambda: parity(repo, evidence["commit"]))
            evidence["handoffIssue"] = item["identifier"]
            evidence["handoffId"] = item["id"]
        print(json.dumps(evidence, sort_keys=True))
        return 0
    except (GateError, KeyError, OSError, ValueError, IndexError) as error:
        message = str(error) if isinstance(error, GateError) else type(error).__name__
        print(json.dumps({"status": "blocked", "reason": message}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
