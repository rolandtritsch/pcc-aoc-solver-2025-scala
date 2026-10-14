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

The CTO first checks the current-cycle gate. While any current part is being
gathered, solved, submitted, or reviewed, it exits without looking for more work.
The next part starts only after a successful completed review of the preceding
part; an accepted answer or green build alone is insufficient. A rejection may
lead only to a same-part repair. A command wrapper checks the gate **before OpenCode/model inference starts**,
so a waiting CTO wake does not spend tokens or run builds. The company-owned
read-only helper at
`skills/aoc-workflow/scripts/aoc_cycle_gate.py` applies this gate, including
interrupted runs and stranded task statuses. It excludes WatchDog, Model Tester,
and pre-cycle history using the board-set `AOC_CYCLE_STARTED_AT` value.

After the gate clears, the CTO synchronizes the solution branch with origin:
fetch, fast-forward pull, push committed work, and verify a clean checkout whose
HEAD matches the live remote. It then selects the next part or code repair solely
from `sbt run` and `sbt test`. Day00-only output selects Day01 part1. Pre-cycle
tasks are informational; current-cycle reviews gate advancement. Submission
confirms existing acceptance without posting the same answer again.

The solver's publication helper explicitly formats new untracked Scala files,
verifies tests and the runner answer, commits intended files, rechecks committed
formatting, pushes, and verifies clean local/tracking/live-remote equality before
it creates the submitter task. Submitter independently checks that committed
handoff before site interaction. Failed checks block the part; shell pipelines
cannot hide process failures. See the [solver skill][solver-publication].

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
timer run collects evidence and creates one fresh self-assigned task already
marked done with the report and snapshot. Same-run retries reuse that task. It checks health, useful progress, suspected stalls, loops,
failures, missing handoffs, duplicate work, and recorded consumption. Reports
never advance or block the puzzle pipeline. V1 takes no corrective action.

Balanced defaults are 20 minutes without useful progress or three repeated
no-progress attempts. The agent has a two-minute timeout, one concurrent run,
and disabled non-timer wake-ups to prevent self-assignment loops. Its timer starts
disabled; deployment and activation are separate from this package update.

The [WatchDog skill][watchdog] bundles its deterministic runner, read-only collector,
and checks in `skills/aoc-watchdog/scripts/`. Code owns report persistence. Flash
interprets only new or changed anomalies in one tool-free request capped at 2,048
output tokens; provider failures trigger a one-hour interpretation cooldown.
Partial telemetry or unavailable interpretation still produces a completed report
with explicit evidence gaps. Its
[telemetry guide][watchdog-telemetry] documents usage and validation. See the
[design research][watchdog-design] for evidence, limits, and deployment checks.
Missing telemetry is unknown, and reporting alone does not stop token burn.

## Getting started

From the `pcc-aoc-solver-2025` checkout:

```bash
paperclipai company import . --target new --dry-run
paperclipai company import . --target new
```

For an existing company, preview with `--target existing --company-id <id>` and
an explicit collision strategy. The default `rename` strategy creates additional
agents and skills; it does not update the existing pipeline. Review a `replace`
preview before deployment and preserve its live model/routing/secret settings.
The CLI uses a safe import endpoint that can reject `replace` with HTTP 403.
For an authorized in-place replacement, use the authenticated board endpoints
`/api/companies/import/preview` and `/api/companies/import`, explicitly selecting
which resource types to include. Skill-only updates must exclude agents,
projects, and issues. Do not use the rejection as a reason to create duplicates.

This update changes the portable package only. Importing it is a separate live
operation. Preserve paused agents and disabled heartbeats when deploying. The CTO
heartbeat interval is five minutes (`intervalSec: 300`), initially disabled
(`enabled: false`); enable it only explicitly after validating the workflow.

Secrets stay in Paperclip's vault: `OPENROUTER_API_KEY` for all agents,
`AOC_SESSION` for gatherer and submitter, optional `GH_TOKEN` for CTO, gatherer,
solver, and reviewer. Bind existing vault references; never copy secret values.
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
lower. The live run rebuilt through Day05 part1, with Flash handling the
coordination roles and Pro completing nine solver assignments. The run also
exposed ownership, monitoring-timeout, and provider-credit failures; see the
[October 11 audit][audit]. See the [test report][] and
[model selection record][] for the results and decisions.

These are **Paperclip agent settings**, managed with `paperclipai`, not Pulumi
configuration keys. The [infrastructure stack][] manages the infrastructure and
backing secret values. The package's `.paperclip.yaml` contains the model pins,
OpenRouter provider mappings, and matching helper models. Credentials remain
vault-backed deployment inputs; preserve their live references during re-import.

The portable package starts with periodic heartbeats disabled; live activation
is a separate operation. The agents were activated on October 10. The October
11 audit pauses the CTO during reconciliation, then restores its timer behind
a pre-inference current-cycle guard, and records remaining live blockers. The package uses one concurrent run per agent to reduce
overlapping provider processes and issue-ownership conflicts. Historical model
selection does not establish puzzle completion.

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

The package pins these plain bindings for the installed ECS toolchain
(other deployments must override the paths):

- `HOME`: `/paperclip`.
- `PATH`: `/paperclip/.asdf/shims:/paperclip/.asdf/bin:/usr/local/bin:/usr/bin:/bin`,
  making the installed Java and sbt toolchain available.
- `AOC_REPO_DIR` and adapter `cwd`: the canonical shared Scala checkout. All
  pipeline agents use it; handoffs carry its exact path.
- `AOC_CYCLE_STARTED_AT`: the board-set reset-cycle timestamp. Update it on a
  deliberate reset; changing HEAD during solving never starts a new cycle.

The CTO adapter's `command` points to the company-managed workflow
`scripts/aoc_cto.py` wrapper. After importing, make that deployed file executable
(`chmod +x <workflow-source-directory>/scripts/aoc_cto.py`) and confirm the
configured command points to the imported workflow directory. The manifest pins
this deployment's path; another company/instance must override it. Skill imports
can recreate files, so repeat the executable-mode check after replacement.
The wrapper delegates to `/usr/local/bin/opencode` only when the cycle gate
permits a fresh selection or same-part repair. An unknown gate fails closed.
It is an execution guard, not an atomic server-side task-creation lock.

Serialize import YAML without anchors/aliases. The portability parser previously
interpreted generated `&id001`/`*id001` strings as environment values. Preview
plain bindings and provider JSON before import; API-redacted values are not
portable configuration. Use GitHub CLI authentication for HTTPS pushes.

WatchDog uses `scripts/aoc_watchdog_runner.py` in its deployed skill directory as
its adapter command. Make it executable after import and verify the configured
path, as for the CTO wrapper above. Set `AOC_PAPERCLIP_UI_URL` to the public
company UI root so reports do not link to the internal API address. Its phase limits are preparation 15 seconds,
collection 45, optional interpretation 30, and persistence 20, leaving ten seconds
under the 120-second adapter timeout. Creating an already completed report with
a run-specific idempotency key avoids the source-task context required for timer
run PATCHes. Verify both normal and provider-unavailable reporting, then three
scheduled checks. Failed report writes remain failed runs.

Design research belongs to setup. The report-only observer cannot pause agents or
fix funding. Independent external monitoring is deferred: a Paperclip outage
prevents task persistence, and this WatchDog cannot detect its own total absence.

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

[audit]: reports/2026-10-11-audit.md

[solver-publication]: skills/aoc-solve-scala/SKILL.md

## Repository and migration

This private repository contains the company package. The Scala solutions remain
in [scala3-aoc-2025][repo]. Its company slug remains `aoc-solver-2025`.

The package was extracted from `rolandtritsch/companies` at source commit
`61a249f43b572b954c9c100401880fbdddb38d67` on October 14, 2026. All 19 AoC
commits retain their authors, dates, and messages; extraction changed their hashes.
This repository starts with the package contents at its root. Repository migration
does not import the package or change the running Paperclip company.

The shared [company-creator skill][creator] and its reference files come from
[Paperclip's companies repository][upstream-companies], as present at the source
commit above. Relative symlinks in `.claude/skills/` and `.agents/skills/` make it
discoverable to local development agents. The multi-company `readme-updater` skill
and its packaged archive were omitted because they maintain the old catalogue.
The fork's additional [catalogue research][catalogues] is retained for reference.

Run the existing offline checks from this repository's root:

```bash
python3 -B -m unittest discover -s skills/aoc-workflow/scripts/tests -v
python3 -B -m unittest discover -s skills/aoc-solve-scala/scripts/tests -v
python3 -B -m unittest discover -s skills/aoc-watchdog/scripts/tests -v
```

[creator]: skills/company-creator/SKILL.md
[upstream-companies]: https://github.com/paperclipai/companies
[catalogues]: docs/CATALOGS.md

## Season completion

The 2025 edition ends at Day12. Once all 24 day/part reviews in the current
cycle are accepted with no repair required, the CTO gate returns `complete` and
the launcher exits successfully before inference. No further gatherer task or
Day13 work starts. The Day12 finale is verified through authenticated site
evidence and review, without requiring a fabricated numerical answer.
