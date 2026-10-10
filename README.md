# AoC Solver 2025

An agent company that works through [Advent of Code 2025](https://adventofcode.com/2025) part-1 puzzles, one day at a time, implementing tested Scala 3 solutions in [scala3-aoc-2025](https://github.com/rolandtritsch/scala3-aoc-2025).

## Org

| Agent | Role | Reports to |
| ----- | ---- | ---------- |
| CTO | Owns the day-loop and pipeline state | — (root) |
| ProblemGatherer | Fetches problem text + personal input | cto |
| ProblemSolver | Principal Scala engineer, implements part-1 | cto |
| ProblemSubmitter | Posts answers, routes verdicts | cto |

Skills: `aoc-gather`, `aoc-solve-scala`, `aoc-submit`.

## Getting started

```bash
npx paperclipai company import ./aoc-solver-2025 --dry-run
npx paperclipai company import ./aoc-solver-2025
```

Secrets (stored in paperclip's vault, never in this package): `OPENROUTER_API_KEY` (all agents), `AOC_SESSION` (gatherer, submitter), optional `GH_TOKEN` (solver, for pushing).

The CTO heartbeat starts paused — drive Day01 manually first, then enable it.

## Agent models

The following choices were applied to the live company on October 10, 2026:

| Agent | Model (`adapterConfig.model`) | Purpose |
| --- | --- | --- |
| Problem Solver | `deepseek/deepseek-v4-pro-0813` | Scala problem solving; selected after the controlled comparison with Kimi K2.7 Code. |
| CTO | `deepseek/deepseek-v4-flash-0731` | Pipeline coordination and blocker routing. |
| Problem Gatherer | `deepseek/deepseek-v4-flash-0731` | Downloading, checking, and committing problem and input files. |
| Problem Submitter | `deepseek/deepseek-v4-flash-0731` | Submitting answers, interpreting verdicts, and creating follow-up tasks. |

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
the models does not resume the pipeline; the recorded AoC 2025 season is complete.

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
