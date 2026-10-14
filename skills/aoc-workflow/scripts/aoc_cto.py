#!/usr/bin/env python3
"""OpenCode command wrapper: gate a CTO run before starting model inference."""

import contextlib
import io
import json
import os
import sys

from aoc_cycle_gate import main as check_cycle


def run(args, check=check_cycle, launch=os.execv):
    if args and args[0] == "run":
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = check()
        try:
            result = json.loads(output.getvalue())
        except (ValueError, TypeError):
            result = {"mode": "unknown", "reason": "invalid gate result"}
            code = 2
        mode = result.get("mode")
        if mode not in ("ready", "repair") or code not in (0, 1):
            print(json.dumps({"type": "text", "part": {"type": "text",
                             "text": "CTO preflight: " + json.dumps(result)}}))
            return 0 if mode in ("wait", "complete") and code == 1 else 2
    binary = os.environ.get("AOC_OPENCODE_BINARY", "/usr/local/bin/opencode")
    launch(binary, [binary, *args])
    return 0


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
