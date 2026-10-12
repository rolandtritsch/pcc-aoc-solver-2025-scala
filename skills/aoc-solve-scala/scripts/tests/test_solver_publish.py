import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

spec = importlib.util.spec_from_file_location("gate", Path(__file__).parents[1] / "aoc_solver_publish.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class PublicationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.remote = self.root / "remote.git"
        self.repo.mkdir()
        self.run_git(self.root, "init", "--bare", str(self.remote))
        self.run_git(self.repo, "init", "-b", "main")
        self.run_git(self.repo, "config", "user.name", "Gate Test")
        self.run_git(self.repo, "config", "user.email", "gate@example.invalid")
        (self.repo / "README.md").write_text("baseline\n")
        self.run_git(self.repo, "add", ".")
        self.run_git(self.repo, "commit", "-m", "baseline")
        self.run_git(self.repo, "remote", "add", "origin", str(self.remote))
        self.run_git(self.repo, "push", "-u", "origin", "main")
        self.base = gate.git(self.repo, "rev-parse", "HEAD")
        self.files = ["src/main/scala/aoc2025/Day10.scala",
                      "src/test/scala/aoc2025/Day10Test.scala",
                      "src/main/scala/aoc2025/Main.scala"]
        for name in self.files:
            file = self.repo / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text("unformatted\n")
        self.events = []
        self.real_command = gate.command

    def run_git(self, cwd, *args):
        subprocess.run(["git", *args], cwd=cwd, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def builder(self, repo, args, timeout=900):
        if args[0] != "sbt":
            if args[1] == "push":
                self.events.append("push")
            return self.real_command(repo, args, timeout)
        self.events.append(args[1])
        if args[1].startswith("scalafmtOnly "):
            explicit = args[1].split(";", 1)[0].split()[1:]
            # Regression: simulate a git-only formatter ignoring untracked files,
            # except those deliberately supplied via scalafmtOnly.
            tracked = gate.git(repo, "ls-files").splitlines()
            for name in set(tracked + explicit):
                if name.endswith(".scala"):
                    (repo / name).write_text("formatted\n")
        else:
            for name in gate.git(repo, "ls-files").splitlines():
                if name.endswith(".scala") and (repo / name).read_text() != "formatted\n":
                    raise gate.GateError("Tracked source is unformatted")
        return "aoc2025.Day10Test:\n[info] Passed: Total 6, Failed 0, Errors 0, Passed 6\n[success]\nDay10 - part1: 417\n"

    def test_untracked_sources_are_formatted_and_committed_before_push(self):
        with patch.object(gate, "command", self.builder):
            evidence = gate.publish(self.repo, 10, 1, "417", self.files)
        self.assertNotEqual(evidence["commit"], self.base)
        for name in self.files:
            self.assertEqual(gate.git(self.repo, "show", f"HEAD:{name}"), "formatted")
        self.assertEqual(self.events[-1], "push")
        gate.parity(self.repo, evidence["commit"])

    def test_failed_build_neither_commits_nor_pushes(self):
        def failing(repo, args, timeout=900):
            if args[0] == "sbt":
                raise gate.GateError("sbt failed")
            return self.real_command(repo, args, timeout)
        with patch.object(gate, "command", failing), self.assertRaises(gate.GateError):
            gate.publish(self.repo, 10, 1, "417", self.files)
        self.assertEqual(gate.git(self.repo, "rev-parse", "HEAD"), self.base)
        self.assertEqual(gate.git(self.remote, "rev-parse", "main"), self.base)

    def test_foreign_work_is_preserved_and_blocks_commit(self):
        (self.repo / "other.txt").write_text("another agent's work\n")
        with self.assertRaises(gate.GateError):
            gate.publish(self.repo, 10, 1, "417", self.files)
        self.assertTrue((self.repo / "other.txt").exists())
        self.assertEqual(gate.git(self.repo, "rev-parse", "HEAD"), self.base)

    def test_wrong_answer_blocks_publication(self):
        with patch.object(gate, "command", self.builder), self.assertRaises(gate.GateError):
            gate.publish(self.repo, 10, 1, "999", self.files)
        self.assertEqual(gate.git(self.remote, "rev-parse", "main"), self.base)

    def test_live_remote_mismatch_fails_closed(self):
        with patch.object(gate, "command", self.builder):
            evidence = gate.publish(self.repo, 10, 1, "417", self.files)
        gate.git(self.remote, "update-ref", "refs/heads/main", self.base)
        with self.assertRaises(gate.GateError):
            gate.parity(self.repo, evidence["commit"])

    def test_direct_subprocess_preserves_nonzero_exit(self):
        with self.assertRaises(gate.GateError):
            gate.command(self.repo, ["sh", "-c", "echo failure; exit 7"])

    def test_no_executed_day_tests_is_not_success(self):
        with self.assertRaises(gate.GateError):
            gate.check_answer("Passed: Total 0, Failed 0, Errors 0\nDay10 - part1: 417", 10, 1, "417")

    def test_handoff_cannot_run_until_push_and_parity_succeed(self):
        payload = self.root / "handoff.json"
        payload.write_text(json.dumps({"description": "source and evidence"}))
        board = Mock()
        def handoff(evidence, before_create):
            before_create()
            gate.parity(self.repo, evidence["commit"])
            self.assertIn("push", self.events)
            return {"id": "task", "identifier": "AOC-202"}
        board.handoff.side_effect = handoff
        args = ["publish", "--repo", str(self.repo), "--day", "10", "--part", "1",
                "--answer", "417", "--handoff", str(payload), "--files", *self.files]
        with patch.dict(os.environ, {"AOC_REPO_DIR": str(self.repo)}), \
                patch.object(gate, "Board", return_value=board), \
                patch.object(gate, "command", self.builder), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(gate.main(args), 0)
        board.handoff.assert_called_once()

    def test_failed_push_never_creates_a_handoff(self):
        payload = self.root / "handoff.json"
        payload.write_text(json.dumps({"description": "source and evidence"}))
        board = Mock()
        def fail_push(repo, args, timeout=900):
            if args[:2] == ["git", "push"]:
                raise gate.GateError("push failed")
            return self.builder(repo, args, timeout)
        args = ["publish", "--repo", str(self.repo), "--day", "10", "--part", "1",
                "--answer", "417", "--handoff", str(payload), "--files", *self.files]
        with patch.dict(os.environ, {"AOC_REPO_DIR": str(self.repo)}), \
                patch.object(gate, "Board", return_value=board), patch.object(gate, "command", fail_push), \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(gate.main(args), 1)
        board.handoff.assert_not_called()
        self.assertEqual(gate.git(self.remote, "rev-parse", "main"), self.base)

class HandoffRecoveryTest(unittest.TestCase):
    def board(self, rows, details):
        board = object.__new__(gate.Board)
        board.company = "company"
        board.source = "source"
        board.cycle_start = "2026-10-10"
        board.part_pattern = r"Day\s*0?10\s*part\s*1\b"
        board.payload = {"title": "AoC 2025 Day10 part1: submit", "description": "evidence",
                         "assigneeAgentId": "submitter", "parentId": None}
        def call(path, body=None):
            if body is not None:
                self.fail("Unexpected duplicate/unsafe task creation")
            return details[path.split('/')[-1]] if path.startswith('/api/issues/') else rows
        board.call = Mock(side_effect=call)
        return board

    def test_retry_recovers_lost_handoff_acknowledgement(self):
        item = {"id": "task", "title": "AoC 2025 Day10 part1: submit",
                "assigneeAgentId": "submitter", "status": "todo",
                "description": "aoc-solver-source:source commit-hash"}
        board = self.board([item], {"task": item})
        before = Mock()
        self.assertEqual(board.handoff({"commit": "commit-hash"}, before), item)
        before.assert_called_once()

    def test_legacy_active_handoff_blocks_duplicate_creation(self):
        item = {"id": "task", "title": "Submit day 10 part 1 answer: 417",
                "assigneeAgentId": "submitter", "status": "in_progress",
                "createdAt": "2026-10-11", "description": "legacy handoff"}
        board = self.board([item], {"task": item})
        with self.assertRaises(gate.GateError):
            board.handoff({"commit": "commit-hash", "answer": "417"}, Mock())

    def test_changed_remote_at_last_check_prevents_post(self):
        board = self.board([], {})
        before = Mock(side_effect=gate.GateError("remote changed"))
        with self.assertRaises(gate.GateError):
            board.handoff({"commit": "commit-hash"}, before)

    def test_exact_legacy_handoff_is_reused_after_publication_repair(self):
        item = {"id": "task", "title": "Submit day 10 part 1 answer: 417",
                "assigneeAgentId": "submitter", "status": "blocked",
                "createdAt": "2026-10-11", "description": "commit-hash answer 417"}
        board = self.board([item], {"task": item})
        before = Mock()
        self.assertEqual(board.handoff({"commit": "commit-hash", "answer": "417"}, before), item)
        before.assert_called_once()


if __name__ == "__main__":
    unittest.main()
