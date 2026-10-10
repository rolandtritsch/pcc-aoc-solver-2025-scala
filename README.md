# AoC Solver 2025

An agent company that implements tested Scala 3 solutions for both parts of
[Advent of Code 2025][aoc] in [scala3-aoc-2025][repo], through Day12.

## Org and workflow

| Agent | Role | Reports to |
| --- | --- | --- |
| CTO | Selects one part or repair per manual/timer wake-up | — (root) |
| ProblemGatherer | Gathers missing statement text and cached personal input | cto |
| ProblemSolver | Implements and tests the assigned Scala 3 part | cto |
| ProblemSubmitter | Submits answers and hands final verdicts to reviewer | cto |
| SolutionReviewer | Reviews evidence and commits reusable project improvements | cto |
| WatchDog | Independent report-only health and progress observer | — (root) |
| Model Tester | Manually assigned routing/model probe outside the pipeline | — (root) |

**CTO → gather if needed → solve → submit → review → wait.**

Each CTO wake-up authorizes one part: Day01 part1, Day01 part2, Day02 part1,
and so on. Accepted and rejected attempts both end at the reviewer. Only a later
manual or timer CTO wake-up starts the next part or a repair. Specialists do not
wake the CTO. Day12's finale follows the authenticated site's actual instructions.

The CTO synchronizes the solution branch with origin before each decision:
fetch, fast-forward pull, push committed work, and verify a clean checkout whose
HEAD matches the live remote. It then selects the next part or code repair solely
from `sbt run` and `sbt test` results. Day00-only output selects Day01 part1.
Historical tasks, acceptance records, and reviews provide context; their statuses
never choose or block the next part. Current-cycle work is checked for duplicate
execution after selection. Submission still confirms existing acceptance without
posting the same answer again, and reviewer examines the current artifacts.

Skills: `aoc-workflow`, `aoc-gather`, `aoc-solve-scala`, `aoc-submit`, `aoc-review`,
`aoc-watchdog`.
See the [shared workflow][workflow], [review skill][review], and
[recursive improvement research][research] for the operating rules and evidence.
The reviewer puts and commits distilled `skills/<name>/SKILL.md` and reusable
`scripts/` in **scala3-aoc-2025**, makes them discoverable through its `AGENTS.md`,
and records validation and commit links on the review issue. Other agents consult
those local skills before repeating work. Solution scripts live in
scala3-aoc-2025; company monitoring scripts are bundled with `aoc-watchdog`.
A reviewer builds further solution scripts when repeated work justifies them.

## WatchDog monitoring

WatchDog reports to nobody and checks all company agents every ten minutes. Each
run creates a fresh task assigned to itself, documents evidence, completes the
report, and exits. It checks health, useful progress, suspected stalls, loops,
failures, missing handoffs, duplicate work, and recorded consumption. Reports
never advance or block the puzzle pipeline. V1 takes no corrective action.

Balanced defaults are 20 minutes without useful progress or three repeated
no-progress attempts. The agent has a two-minute timeout, one concurrent run,
and disabled non-timer wake-ups to prevent self-assignment loops. Its timer starts
disabled; deployment and activation are separate from this package update.

The [WatchDog skill][watchdog] bundles its tested, read-only telemetry collector
in `skills/aoc-watchdog/scripts/`. The collector provides bounded telemetry and
a structured snapshot; the agent interprets it and writes the report. Its
[telemetry guide][watchdog-telemetry] documents usage and validation. See the
[design research][watchdog-design] for evidence, limits, and deployment checks.
Missing telemetry is unknown, and reporting alone does not stop token burn.

## Getting started

From the `companies` checkout:

```bash
paperclipai company import ./aoc-solver-2025 --target new --dry-run
paperclipai company import ./aoc-solver-2025 --target new
```

For an existing company, preview with `--target existing --company-id <id>` and
an explicit collision strategy. The default `rename` strategy creates additional
agents and skills; it does not update the existing pipeline. Review a `replace`
preview before deployment and preserve its live model/routing/secret settings.

This update changes the portable package only. Importing it is a separate live
operation. Preserve paused agents and disabled heartbeats when deploying. The CTO
heartbeat interval is five minutes (`intervalSec: 300`), initially disabled
(`enabled: false`); enable it only explicitly after validating the workflow.

Secrets stay in Paperclip's vault: `OPENROUTER_API_KEY` for all agents,
`AOC_SESSION` for gatherer and submitter, optional `GH_TOKEN` for the solver.
Reviewer commits improvements locally; pushing needs separate authorization.
All six non-solver agents use Flash; Problem Solver uses Pro. The package pins
these models and their OpenRouter mappings for subsequent imports.

## Agent models

The following choices were applied to the live company on October 10, 2026:

| Agent | Model (`adapterConfig.model`) | Purpose |
| --- | --- | --- |
| Problem Solver | `deepseek/deepseek-v4-pro-0813` | Scala problem solving; selected after the controlled comparison with Kimi K2.7 Code. |
| CTO | `deepseek/deepseek-v4-flash-0731` | Pipeline coordination and blocker routing. |
| Problem Gatherer | `deepseek/deepseek-v4-flash-0731` | Downloading, checking, and committing problem and input files. |
| Problem Submitter | `deepseek/deepseek-v4-flash-0731` | Submitting answers and interpreting verdicts. |
| Solution Reviewer | `deepseek/deepseek-v4-flash-0731` | Reviewing evidence and reusable improvements. |
| WatchDog | `deepseek/deepseek-v4-flash-0731` | Independent health and progress monitoring. |
| Model Tester | `deepseek/deepseek-v4-flash-0731` | Default for manually assigned model probes. |

Pro solved all three actual puzzle inputs in the comparison and cost less than
Kimi. Flash was selected for the other roles because their work follows defined
HTTP, git, and task-coordination workflows and its listed token prices are
lower. Flash has not yet been tested in those roles. See the [test report][] and
[model selection record][] for the results and decisions.

These are **Paperclip agent settings**, managed with `paperclipai`, not Pulumi
configuration keys. The [infrastructure stack][] manages the infrastructure and
backing secret values. The package's `.paperclip.yaml` contains the model pins,
OpenRouter provider mappings, and matching helper models. Credentials remain
vault-backed deployment inputs; preserve their live references during re-import.

The pipeline agents and WatchDog remain **paused**; Model Tester remains idle.
Periodic heartbeats are disabled for every agent. Changing the models does not
resume the pipeline. That historical model-selection record does not establish
completion of both parts under the workflow in this package.

### OpenRouter routing

All seven agents use `opencode_local` and the existing company-vault
`OPENROUTER_API_KEY` secret reference. The `deepseek/...` model names require an
explicit OpenRouter provider mapping: without it, OpenCode can select the direct
DeepSeek provider and reject the OpenRouter key.

The package sets `adapterConfig.env.PAPERCLIP_OPENCODE_PROVIDERS` as a plain
environment binding using the selected model. The full two-model mapping below
references `OPENROUTER_API_KEY` without storing its credential value:

```json
{
  "deepseek": {
    "npm": "@ai-sdk/openai-compatible",
    "name": "OpenRouter DeepSeek",
    "options": {
      "baseURL": "https://openrouter.ai/api/v1",
      "apiKey": "{env:OPENROUTER_API_KEY}"
    },
    "models": {
      "deepseek-v4-pro-0813": { "id": "deepseek/deepseek-v4-pro-0813" },
      "deepseek-v4-flash-0731": { "id": "deepseek/deepseek-v4-flash-0731" }
    }
  }
}
```

The mapping can contain just the selected model or both models as shown. The
package also sets `PAPERCLIP_OPENCODE_SMALL_MODEL` as a plain binding to the same
model as `adapterConfig.model`, so helper calls use the selected routing too.

On the deployed ECS instance, also set these plain bindings for its installed
toolchain (other deployments may need different paths):

- `HOME`: `/paperclip`.
- `PATH`: `/paperclip/.asdf/shims:/paperclip/.asdf/bin:/usr/local/bin:/usr/bin:/bin`,
  making the installed Java and sbt toolchain available.

Use `paperclipai agent get` to read the current configuration before applying
changes with `paperclipai agent update`, then read it again to verify the model
and routing bindings. Preserve the existing secret references, instructions,
workspace, and paused/heartbeat settings.

[infrastructure stack]: https://github.com/rolandtritsch/pulumi-paperclip
[test report]: https://paperclip.tritsch.org/AOC/issues/AOC-70#document-report
[model selection record]: https://paperclip.tritsch.org/AOC/issues/AOC-70#document-model-selection

[aoc]: https://adventofcode.com/2025
[repo]: https://github.com/rolandtritsch/scala3-aoc-2025
[workflow]: skills/aoc-workflow/SKILL.md
[review]: skills/aoc-review/SKILL.md
[research]: skills/aoc-review/references/recursive-self-improvement.md

[watchdog]: skills/aoc-watchdog/SKILL.md
[watchdog-design]: skills/aoc-watchdog/references/watchdog-design.md

[watchdog-telemetry]: skills/aoc-watchdog/references/telemetry.md
