import importlib.util
import json
import subprocess
import sys
from pathlib import Path
import unittest

SCRIPT = Path(__file__).parents[1] / "verify_review_block.py"
spec = importlib.util.spec_from_file_location("verify_block", SCRIPT)
verify_block = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify_block)

ISSUE = "317cbe1e-3397-44eb-b813-485eff820c9a"
TITLE = "AoC 2025 Day09 part1: review (submit attempt 4777967538 / 28c21aba)"
COMMIT = "28c21aba3d5f3bd9e79af256fa77111480d9c184"


def body(result):
    return "report text\n```aoc-review-result\n" + json.dumps(result) + "\n```\n"


def good(**over):
    result = {"reviewIssueId": ISSUE, "day": 9, "part": 1,
              "solutionCommit": COMMIT, "accepted": True, "repairRequired": False}
    result.update(over)
    return body(result)


class VerifyTest(unittest.TestCase):
    def check(self, issue_id, title, text):
        return verify_block.verify(issue_id, title, text)

    def test_valid_accepted(self):
        ok, detail = self.check(ISSUE, TITLE, good())
        self.assertTrue(ok)
        self.assertIn("acceptance", detail)

    def test_valid_repair_records_repair(self):
        ok, detail = self.check(
            ISSUE, TITLE, good(accepted=False, repairRequired=True))
        self.assertTrue(ok)
        self.assertIn("repair", detail)

    def test_missing_block_is_defect(self):
        # Shape of the 2026-10-15 Day09 part1 stall: prose verdict, no block.
        prose = ("Verdict: **accepted** · answer `4777967538` · commit "
                 f"`{COMMIT}` · `repairRequired: false`. Nothing to repair.")
        ok, detail = self.check(ISSUE, TITLE, prose)
        self.assertFalse(ok)
        self.assertIn("missing", detail)

    def test_bad_json_is_defect(self):
        ok, _ = self.check(ISSUE, TITLE, "```aoc-review-result\n{nope\n```")
        self.assertFalse(ok)

    def test_issue_id_mismatch_is_defect(self):
        ok, detail = self.check("other-id", TITLE, good())
        self.assertFalse(ok)
        self.assertIn("reviewIssueId", detail)

    def test_day_part_mismatch_is_defect(self):
        ok, _ = self.check(ISSUE, TITLE, good(day=9, part=2))
        self.assertFalse(ok)

    def test_commit_prefix_mismatch_is_defect(self):
        ok, detail = self.check(ISSUE, TITLE, good(solutionCommit="deadbeefcafe1234"))
        self.assertFalse(ok)
        self.assertIn("attempt commit", detail)

    def test_non_bool_flags_are_defect(self):
        ok, _ = self.check(ISSUE, TITLE, good(accepted="yes"))
        self.assertFalse(ok)

    def test_cli_exit_zero_on_valid(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--issue-id", ISSUE, "--title", TITLE],
            input=good(), capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_cli_exit_nonzero_on_missing(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--issue-id", ISSUE, "--title", TITLE],
            input="no block here", capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
