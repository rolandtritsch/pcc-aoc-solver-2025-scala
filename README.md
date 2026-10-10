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
| Model Tester | Manually assigned routing/model probe outside the pipeline | — (root) |

**CTO → gather if needed → solve → submit → review → wait.**

Each CTO wake-up authorizes one part: Day01 part1, Day01 part2, Day02 part1,
and so on. Accepted and rejected attempts both end at the reviewer. Only a later
manual or timer CTO wake-up starts the next part or a repair. Specialists do not
wake the CTO. Day12's finale follows the authenticated site's actual instructions.

The CTO runs `sbt run` and `sbt test` and checks implementations, active tests,
acceptance evidence, and completed reviews. Printed placeholders and green
unrelated tests cannot establish completion. Verified existing acceptances are
retained; historical accepted work can receive a retrospective review.

Skills: `aoc-workflow`, `aoc-gather`, `aoc-solve-scala`, `aoc-submit`, `aoc-review`.
See the [shared workflow][workflow], [review skill][review], and
[recursive improvement research][research] for the operating rules and evidence.
The reviewer puts and commits distilled `skills/<name>/SKILL.md` and reusable
`scripts/` in **scala3-aoc-2025**, makes them discoverable through its `AGENTS.md`,
and records validation and commit links on the review issue. Other agents consult
those local skills before repeating work. No scripts are bundled in this update;
a reviewer builds them when demonstrated repeated work justifies them.

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
SolutionReviewer uses this package's existing `opencode_local`/auto-model default;
no live reviewer model choice or deployment is implied by the historical settings.

## Agent models

The following choices were applied to the live company on October 10, 2026:

| Agent | Model (`adapterConfig.model`) | Purpose |
| --- | --- | --- |
| Problem Solver | `deepseek/deepseek-v4-pro-0813` | Scala problem solving; selected after the controlled comparison with Kimi K2.7 Code. |
| CTO | `deepseek/deepseek-v4-flash-0731` | Pipeline coordination and blocker routing. |
| Problem Gatherer | `deepseek/deepseek-v4-flash-0731` | Downloading, checking, and committing problem and input files. |
| Problem Submitter | `deepseek/deepseek-v4-flash-0731` | Submitting answers and interpreting verdicts. |

Pro solved all three actual puzzle inputs in the comparison and cost less than
Kimi. Flash was selected for the other roles because their work follows defined
HTTP, git, and task-coordination workflows and its listed token prices are
lower. Flash has not yet been tested in those roles. See the [test report][] and
[model selection record][] for the results and decisions.

These are **Paperclip agent settings**, managed with `paperclipai`, not Pulumi
configuration keys. The [infrastructure stack][] manages the infrastructure and
backing secret values. This package's agent definitions do not currently contain
these model pins or provider mappings; importing this package into a fresh
instance does not reproduce this setup. After an import or reset, restore the
settings below for each agent.

All four agents were left **paused**, with periodic heartbeats disabled. Changing
the models does not resume the pipeline. That historical model-selection record
does not establish completion of both parts under the workflow in this package.

### OpenRouter routing

All four agents use `opencode_local` and the existing company-vault
`OPENROUTER_API_KEY` secret reference. The `deepseek/...` model names require an
explicit OpenRouter provider mapping: without it, OpenCode can select the direct
DeepSeek provider and reject the OpenRouter key.

Set `adapterConfig.env.PAPERCLIP_OPENCODE_PROVIDERS` to a plain environment binding
whose value is the JSON below. It contains an environment reference, not a
credential value:

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

The mapping can contain just the selected model or both models as shown. Set
`PAPERCLIP_OPENCODE_SMALL_MODEL` as a plain binding in `adapterConfig.env` to the
same model as `adapterConfig.model`, so OpenCode's helper calls use the selected
model and routing too.

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
