#!/usr/bin/env python3
"""Verify an aoc-review-result block before a review is marked done.

Mirrors the strict branch of the CTO gate (`aoc_cycle_gate.review_result`):
only a fenced JSON block whose identity fields match the review issue clears
advancement. Prose verdicts never clear the gate — a prose-only review left
Day09 part1 stalled for 5 hours on 2026-10-15.

Usage:
  verify_review_block.py --issue-id UUID --title "ISSUE TITLE"
      [--body-file PATH]   # comment body defaults to stdin
Exit 0 when the block is valid (accepted or repair verdict recorded),
exit 1 naming the exact defect otherwise.
"""

import argparse
import json
import re
import sys

BLOCK_RE = re.compile(r"```aoc-review-result\s*(\{.*?\})\s*```", re.S)
TITLE_PART_RE = re.compile(r"\bday\s*0*(\d+)\s*part\s*([12])\b", re.I)
ATTEMPT_RES_RE = re.compile(r"attempt\s+(?:commit\s+)?([0-9a-f]{7,40})", re.I)
ATTEMPT_SUFFIX_RE = re.compile(r"/\s*([0-9a-f]{7,40})\s*\)?\s*$")
SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")


def verify(issue_id, title, body):
    """Return (ok, detail). ok is True only for a well-formed block."""
    match = BLOCK_RE.search(body or "")
    if not match:
        return False, "missing aoc-review-result block"
    try:
        result = json.loads(match.group(1))
    except json.JSONDecodeError as error:
        return False, f"block is not valid JSON: {error}"
    if not isinstance(result, dict):
        return False, "block JSON is not an object"
    if result.get("reviewIssueId") != issue_id:
        return False, "reviewIssueId does not match this review issue"
    part_match = TITLE_PART_RE.search(title or "")
    if not part_match:
        return False, "cannot parse day/part from issue title"
    day, part = (int(part_match.group(1)), int(part_match.group(2)))
    if result.get("day") != day or result.get("part") != part:
        return False, (
            f"block day/part {result.get('day')}/{result.get('part')} "
            f"does not match issue day/part {day}/{part}"
        )
    commit = result.get("solutionCommit") or ""
    if not SHA_RE.match(commit):
        return False, "solutionCommit is missing or not a hex sha"
    # Suffix shape first ("... attempt <answer> / <commit>"): a bare
    # `attempt <digits>` match would grab the numeric answer instead.
    attempt = ATTEMPT_SUFFIX_RE.search(title or "") or ATTEMPT_RES_RE.search(title or "")
    if attempt and not commit.startswith(attempt.group(1)):
        return False, (
            f"solutionCommit does not start with attempt commit {attempt.group(1)}"
        )
    if not isinstance(result.get("accepted"), bool):
        return False, "accepted must be true/false"
    if not isinstance(result.get("repairRequired"), bool):
        return False, "repairRequired must be true/false"
    if result["repairRequired"]:
        return True, "valid block recording pending repair"
    if result["accepted"]:
        return True, "valid block recording acceptance"
    return True, "valid block with inconclusive verdict"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issue-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--body-file", default=None)
    args = parser.parse_args(argv)
    if args.body_file:
        with open(args.body_file) as handle:
            body = handle.read()
    else:
        body = sys.stdin.read()
    ok, detail = verify(args.issue_id, args.title, body)
    print(("OK: " if ok else "DEFECT: ") + detail)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
