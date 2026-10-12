# AoC 2025 current-run timing, tokens, and solver behavior

Snapshot: **October 11, 2026, 11:19:52 UTC / 12:19:52 Dublin**.
The company remains active; this report freezes the observed run at that cutoff.

**18 parts have finished their solver run; 17 have a completed accepted review.**
Day09 part2 has been solved and submitted, but its review was still running.
The solver used **40,200,481 recorded tokens**, including **37,712,439 cached
input tokens (93.8%)**. Median solver elapsed time was **5m 21s**; total solver
run time was **1h 49m 09s**. These are agent-run measurements, not pure algorithm
thinking time or a provider invoice.

The highest-token parts, counting cached context, are **Day08 part1, Day09
part2, Day04 part1, Day05 part1, and Day01 part1**. Repeated context reads and
build/workflow recovery explain much of the volume. If cached reads are
excluded, **Day09 part2** is the largest run by a wide margin.

The observable solver behavior is primarily local implementation and testing.
**No internet solution search was observed in any of the 18 solver logs.**
However, **Day01 part1 read an existing solution and tests from the old demo
branch**, so this run is not a clean from-scratch reasoning benchmark.

## Scope and measurement

Production activation was October 10 at 18:11 UTC; the first puzzle assignment,
[AOC-79][], was created at **18:20:28.381 UTC**. Historical AOC-1–78, model
comparison trials, and retained Day00 are excluded. The review covers all 193
returned tickets for classification, all seven agents' run histories (none
reached the 1,000-run cap), and full descriptions/comments for the 73 current-run
puzzle tasks. There are **86 task-associated specialist runs** across 18 parts,
including interrupted, cancelled, failed, and resumed attempts. Unrelated
monitoring tasks and unattributed CTO work are not allocated to puzzle parts.

Timing definitions:

- **Solver elapsed:** solver run `startedAt` to `finishedAt`. All 18 parts had
  one successful solver run. This includes reading, implementation, tools,
  compilation, tests, Git, and handoff administration; it excludes the initial
  gather stage and subsequent submission/review.
- **Gather → reviewed:** first valid gather-task creation to the first complete
  accepted review report comment. This includes queues, infrastructure waits,
  submission, review, and the reviewer's improvement pass. Day09 part2 shows
  elapsed time to the cutoff, with no completed-review timestamp.
- These clocks overlap between parts where the old CTO advanced prematurely.
  Do not sum them to infer the company's total wall-clock duration. They also
  exclude idle intervals between one review and the next CTO assignment.

Token definitions:

- **Fresh input** = Paperclip `usageJson.inputTokens`.
- **Cached input** = `usageJson.cachedInputTokens`, counted again whenever
  prior context is served to another model step. It is not unique information.
- **Output** = `usageJson.outputTokens`, already including recorded reasoning.
- **Total** = fresh input + cached input + output. For every solver, this equals
  the independently summed OpenCode `step_finish.tokens.total` in its log.
  The component sums also match Paperclip usage exactly across **809 steps**.
  Cache-write tokens were zero in those solver logs. Reasoning is a subset of
  output and is never added a second time.
- **Stage total** = recorded tokens from gather + solve + submit + review runs
  associated by task ID, including retries and the cancelled AOC-128 attempt.
  These totals exclude CTO, WatchDog, Model Tester, and this board analysis.
  They are not token counts for the algorithm alone.

This distinction matters: fresh input + output is only **2,488,042 tokens**;
reporting that as all consumption would omit 37.7 million cached reads. Cached
and fresh tokens have different prices, so the all-token ranking is **not a
cost ranking**. This report does not infer dollar charges from zero-valued
adapter cost fields.

## Every attempted day and part

Durations are rounded to the nearest second. Tokens are exact recorded counts.
Each part links to its solve task; the review column links to its review task.

| Part / solve task | Solver elapsed | Gather → reviewed | Fresh input | Cached input | Output incl. reasoning | Solver total | Review at cutoff |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [Day01 part1][AOC-81] | 8m 34s | 30m 53s | 108,028 | 2,391,040 | 24,810 | **2,523,878** | [Accepted][AOC-84] |
| [Day01 part2][AOC-87] | 3m 55s | 13m 54s | 78,476 | 1,672,881 | 14,231 | **1,765,588** | [Accepted][AOC-90] |
| [Day02 part1][AOC-92] | 6m 35s | 21m 31s | 86,724 | 1,580,032 | 24,806 | **1,691,562** | [Accepted][AOC-95] |
| [Day02 part2][AOC-98] | 7m 25s | 25m 52s | 77,918 | 2,075,392 | 14,609 | **2,167,919** | [Accepted][AOC-101] |
| [Day03 part1][AOC-104] | 3m 52s | 20m 56s | 59,423 | 1,438,464 | 10,856 | **1,508,743** | [Accepted][AOC-106] |
| [Day03 part2][AOC-108] | 4m 59s | 12m 08s | 65,981 | 1,422,336 | 10,856 | **1,499,173** | [Accepted][AOC-111] |
| [Day04 part1][AOC-114] | 8m 47s | 18m 36s | 121,851 | 3,183,104 | 22,093 | **3,327,048** | [Accepted][AOC-116] |
| [Day04 part2][AOC-119] | 4m 15s | 13m 47s | 92,959 | 1,239,808 | 14,303 | **1,347,070** | [Accepted][AOC-121] |
| [Day05 part1][AOC-124] | 9m 19s | 10h 42m 16s | 123,012 | 2,836,480 | 28,079 | **2,987,571** | [Accepted][AOC-127] |
| [Day05 part2][AOC-140] | 4m 05s | 13m 42s | 248,557 | 2,048,512 | 19,624 | **2,316,693** | [Accepted][AOC-143] |
| [Day06 part1][AOC-146] | 4m 43s | 17m 27s | 75,288 | 2,188,800 | 16,269 | **2,280,357** | [Accepted][AOC-148] |
| [Day06 part2][AOC-152] | 4m 55s | 15m 57s | 82,854 | 1,789,184 | 20,722 | **1,892,760** | [Accepted][AOC-155] |
| [Day07 part1][AOC-158] | 4m 42s | 15m 16s | 90,877 | 1,838,080 | 17,335 | **1,946,292** | [Accepted][AOC-161] |
| [Day07 part2][AOC-165] | 5m 43s | 14m 55s | 66,100 | 1,698,304 | 21,631 | **1,786,035** | [Accepted][AOC-168] |
| [Day08 part1][AOC-171] | 6m 50s | 15m 00s | 94,916 | 3,648,390 | 32,907 | **3,776,213** | [Accepted][AOC-174] |
| [Day08 part2][AOC-178] | 6m 38s | 13m 47s | 102,804 | 2,353,152 | 13,531 | **2,469,487** | [Accepted][AOC-181] |
| [Day09 part1][AOC-184] | 3m 33s | 10m 49s | 53,337 | 1,381,376 | 8,850 | **1,443,563** | [Accepted][AOC-186] |
| [Day09 part2][AOC-190] | 10m 21s | ≥ 20m 00s | 484,126 | 2,927,104 | 59,299 | **3,470,529** | [In progress][AOC-193] |

Day10–Day12 have no puzzle assignments in this snapshot. Their elapsed time and
tokens are **not yet measured**, rather than zero. Day00 is the retained template.

Day05 part1's **10h 42m 16s** end-to-end duration includes the overnight service
interruption, provider-credit failures, and morning recovery. Its solver itself
finished in **9m 19s** on October 10. The reviewer resumed after credits were
added and posted its accepted report at 07:45:43 UTC on October 11.

Day02 part2's accepted review report was posted at **20:09:00.869 UTC October
10**, although a stranded status write left the task formally open until board
reconciliation at 06:44 UTC October 11. The table uses the substantive report,
not that late administrative closure. Historical gate violations mean this
report timestamp should not be interpreted as proof that the then-current CTO
waited for review: it did not consistently do so.

Day05 part2 starts with the authorized replacement gather task **AOC-139 at
07:53:03 UTC October 11**. The prematurely created **AOC-128 at 21:24:10 UTC
October 10** was cancelled and is not treated as the valid stage-clock start.
Its recorded usage is nevertheless included in that part's stage total below.

## Recorded tokens across the four specialist stages

Usage exists for **78 of 86 runs**. Seven cancelled/failed/interrupted runs and
the running Day09 part2 review lack a usage object. Their missing consumption
is unknown: **it is not assumed to be zero**. An available usage object with
explicit zero counts is counted as covered. The figures marked “≥” are lower
bounds; other rows have complete recorded usage for the associated stage runs,
without claiming independent provider reconciliation.

| Part | Recorded stage tokens | Runs with usage / associated runs | Missing usage or scope note |
| --- | ---: | ---: | --- |
| Day01 part1 | ≥ 8,956,941 | 4 / 5 | AOC-79 cancelled |
| Day01 part2 | 6,176,632 | 4 / 4 | All associated runs recorded |
| Day02 part1 | 6,316,783 | 4 / 4 | All associated runs recorded |
| Day02 part2 | ≥ 3,177,681 | 5 / 6 | AOC-101 failed |
| Day03 part1 | ≥ 6,093,876 | 5 / 6 | AOC-102 failed |
| Day03 part2 | 4,271,054 | 4 / 4 | All associated runs recorded |
| Day04 part1 | 7,940,436 | 4 / 4 | All associated runs recorded |
| Day04 part2 | 5,656,597 | 4 / 4 | All associated runs recorded |
| Day05 part1 | ≥ 7,690,570 | 7 / 10 | AOC-125 cancelled, AOC-125 failed, AOC-127 interrupted |
| Day05 part2 | ≥ 5,283,488 | 6 / 7 | AOC-128 interrupted; includes cancelled AOC-128 |
| Day06 part1 | 10,181,532 | 4 / 4 | All associated runs recorded |
| Day06 part2 | 6,771,248 | 4 / 4 | All associated runs recorded |
| Day07 part1 | 6,394,877 | 4 / 4 | All associated runs recorded |
| Day07 part2 | 5,591,297 | 4 / 4 | All associated runs recorded |
| Day08 part1 | 8,212,888 | 4 / 4 | All associated runs recorded |
| Day08 part2 | 6,129,356 | 4 / 4 | All associated runs recorded |
| Day09 part1 | 5,715,875 | 4 / 4 | All associated runs recorded |
| Day09 part2 | ≥ 4,323,183 | 3 / 4 | AOC-193 running |

Across all parts these stages recorded **at least 114,884,314 tokens**. Of those,
40,200,481 belong to the solver and 74,683,833 to gathering, submission, and
review. The reviewer also builds and validates reusable scripts/skills, so its
work is deliberately broader than approving the numerical answer. Missing
usage prevents an exact final company-wide or full-pipeline consumption total.

### Top five parts when all specialist stages are included

The ranking below uses recorded stage totals. Missing usage means the true
ranking is not guaranteed; Day01 part1 and Day05 part1 are lower bounds.

| Recorded rank | Part | Recorded stage total | Largest contributor | Explanation supported by task evidence |
| ---: | --- | ---: | --- | --- |
| 1 | Day06 part1 | 10,181,532 | Review: 5,860,551 | Review went beyond acceptance: it built two worksheet parsers, a 1,000-case seeded generator, failure-mode tests, a skill, and discovery documentation ([AOC-148][]) |
| 2 | Day01 part1 | ≥ 8,956,941 | Review: 3,117,809 | Initial workflow setup; review created and validated `verify-day.sh` and its skill, while solver/submission also reconstructed the evidence chain ([AOC-84][]) |
| 3 | Day08 part1 | 8,212,888 | Solver: 3,776,213 | Solver build recovery plus gathering/submission/review; solver details below ([AOC-171][]) |
| 4 | Day04 part1 | 7,940,436 | Solver: 3,327,048 | Solver investigated test aliases; gathering also recorded 2,577,336 tokens; review added 1,470,113 ([AOC-114][]) |
| 5 | Day05 part1 | ≥ 7,690,570 | Solver: 2,987,571 | Solver cache/test recovery, followed by interrupted and resumed submission/review; review recorded another 2,555,520 tokens ([AOC-124][], [AOC-127][]) |

These are different questions: Day06 part1 is the largest recorded **delivery
pipeline**, while Day08 part1 is the largest **solver run**. Stage allocation
shows where tokens were recorded, but these counts cannot establish the exact
percentage spent on a particular action. The detailed causal inspection below
covers the five largest solver runs, which directly addresses solving behavior.

## Top five solver parts by all recorded tokens

This ranking includes cached context. Average input per step is
(fresh + cached input) / completed model steps; it describes repeated context
volume, not a unique prompt or the model's context-window limit.

| Rank | Part | Total tokens | Fresh + output | Model steps | Reasoning within output | Avg. input per step | Cached share of total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | [Day08 part1][AOC-171] | 3,776,213 | 127,823 | 64 | 18,681 | 58,489 | 96.6% |
| 2 | [Day09 part2][AOC-190] | 3,470,529 | 543,425 | 41 | 45,237 | 83,201 | 84.3% |
| 3 | [Day04 part1][AOC-114] | 3,327,048 | 143,944 | 50 | 11,257 | 66,099 | 95.7% |
| 4 | [Day05 part1][AOC-124] | 2,987,571 | 151,091 | 53 | 15,991 | 55,839 | 94.9% |
| 5 | [Day01 part1][AOC-81] | 2,523,878 | 132,838 | 43 | 15,385 | 58,118 | 94.7% |

### 1. Day08 part1 — 3,776,213 tokens

The solver implemented sorted squared-distance pairs and union-find, processed
exactly the first 1,000 pairs, and cross-checked the three largest circuit sizes
with Python. The computational work was real, but **96.6% of its tokens were
cached input** across 64 model steps and 69 tool calls.

Its build first hit a SemanticDB `AccessDeniedException` involving sbt's cached
artifacts. It inspected cache links/permissions, cleaned the build, and retried.
Compilation then failed under `-Werror` because an implicit argument needed
Scala 3 `using` syntax. Further work included inspecting prior Day07 code/tests,
validation, and submission-task discovery. These recovery and workflow steps
repeatedly carried earlier context. **Inference:** this is chiefly a large,
repeated-context/tooling run, rather than the hardest mathematical puzzle.
Evidence: [solver run][run-171], [task AOC-171][AOC-171].

### 2. Day09 part2 — 3,470,529 tokens

This is the clearest algorithmic outlier: **484,126 fresh input tokens** and
**59,299 output tokens**, including **45,237 reasoning tokens**. Its 543,425
fresh-plus-output tokens are twice the next largest run. Cached context still
accounts for 84.3%, but the run has the lowest cached share among the top five.

The solver modeled a closed rectilinear polygon, coordinate-compressed the
region, built a 2D prefix sum for rectangle containment, and enumerated pairs
of red corners. It cross-checked using two even-odd variants and a Pick's
theorem region-count check. The logged build commands show no failed build
in this run. It also spent tool calls discovering task identifiers and correcting
API lookup paths before handoff. **Inference:** geometry/containment design
and its validation contributed materially here; administration added overhead.
Tokens cannot be precisely partitioned between those causes from tool logs.
Evidence: [solver run][run-190], [task AOC-190][AOC-190].

### 3. Day04 part1 — 3,327,048 tokens

The actual puzzle is a local eight-neighbor count. The solver implemented it,
passed nine day tests, and obtained 1,356. It then repeatedly investigated why
`sbt test` reported “No tests to run”: this project's command alias selected
`testQuick`, whose unchanged tests were already green. It inspected aliases,
configuration and global sbt state, eventually using `testFull`, which ran
52 passing tests. It also ran Scalafix and restored unrelated source changes.

There are 50 model steps and 64 tool calls, with **95.7% cached input**. The
log supports a workflow/verification investigation as a major source of excess
work. There is no evidence of a prolonged failed puzzle algorithm here.
Evidence: [solver run][run-114], [task AOC-114][AOC-114].

### 4. Day05 part1 — 2,987,571 tokens

The algorithm tests ingredient IDs against inclusive intervals. The solver's
first compilation attempts hit SemanticDB `AccessDeniedException`; it inspected
cache ownership/links and cleaned before rebuilding. A boundary/overlap test
then failed and required correction. It repeated formatting, targeted/full
verification, cross-checking, and handoff operations.

The run used 53 model steps and 65 tool calls; **94.9% of tokens were cached
input**. Build recovery and a test correction explain extra interactions beyond
this straightforward membership problem. The later overnight credit outage
explains the part's long completion clock, **not this solver-token total**:
the solver had already succeeded before that outage.
Evidence: [solver run][run-124], [task AOC-124][AOC-124].

### 5. Day01 part1 — 2,523,878 tokens

The solver independently computed the answer in Python, but then explicitly
read `origin/aoc-demo-day01:src/main/scala/aoc2025/Day01.scala`, the corresponding
tests and sample, and the old Main. It also inspected historical Day11 code
and read historical submission task **AOC-4**, which already contained 1,129.
The newly written solution shares the modular-rotation approach in the old code.
The evidence establishes prior-solution exposure; it does not prove every new
line was copied verbatim.

A malformed shell invocation (`sbt scalafmtAll; test; scalafmtCheckAll; run`)
initially executed later names as shell commands. After correction, a
SemanticDB access failure required cache inspection and `sbt clean`. Git
authentication, commit metadata, historical ticket discovery, and handoff added
further work. Across 43 steps and 52 tool calls, **94.7% was cached input**.
This was an expensive bootstrap/reconstruction run, not evidence that modular
arithmetic itself required millions of reasoning tokens.
Evidence: [solver run][run-81], [task AOC-81][AOC-81], [old AOC-4][AOC-4].

### Ranking when cached reads are excluded

This view is useful alongside the all-token ranking, but is still not a dollar
ranking because fresh input and output have different rates.

| Rank | Part | Fresh input + output | All tokens |
| ---: | --- | ---: | ---: |
| 1 | Day09 part2 | 543,425 | 3,470,529 |
| 2 | Day05 part2 | 268,181 | 2,316,693 |
| 3 | Day05 part1 | 151,091 | 2,987,571 |
| 4 | Day04 part1 | 143,944 | 3,327,048 |
| 5 | Day01 part1 | 132,838 | 2,523,878 |

Day05 part2 enters this ranking with 248,557 fresh input tokens. Its interval
merge/count solution was implemented locally and tested; the log also contains
build-cache recovery and repeated verification. It is not in the top five when
cached reads are included. This demonstrates why specifying the token metric
changes the answer to “which part consumed the most?”

## Reasoning, reuse, or internet solutions?

I inspected **all 18 solver tool traces**, including shell commands and inputs
to non-shell tools, rather than relying only on final self-reports. The observed
tool set was `skill`, `bash`, `read`, `write`, `edit`, and `invalid`. No web-search,
web-fetch, browsing, search-engine query, external solution repository clone,
or fetched public solution was observed. AoC URLs embedded in handoff documents
are references, not evidence of requests to those URLs. Observed network work
was Paperclip task coordination and GitHub authentication/pushing the owned repo.

Reading cached official puzzle text or examples is normal problem acquisition;
it is different from looking up somebody else's algorithm. Likewise, building
with sbt may download dependencies without being a solution lookup. Only solver
behavior is assessed here: this is not an audit of every gatherer or reviewer
network request.

The positive evidence is implementation edits, sample/edge tests, real-input
execution, and independent local cross-checks. Examples include:

| Parts | Observable method and validation |
| --- | --- |
| Day01 part1 | Modular dial simulation and Python check, **with old same-part solution/test/answer exposure** |
| Day01 part2 | Counts zero crossings through complete rotations; boundary tests including multi-turn rotations |
| Day02 parts1–2 | Digit-pattern repetition checks; generalizes from exactly two repetitions to repeated substrings; Python checks |
| Day03 parts1–2 | Ordered digit selection for two- and twelve-digit joltage; sample/edge checks and independent cross-checks |
| Day04 parts1–2 | Neighbor counting, then repeated batched removal; independent grid simulation |
| Day05 parts1–2 | Inclusive-range membership, then union/merge and size counting; overlap, boundary and large-value tests |
| Day06 parts1–2 | Parses horizontal problems, then preserves column spacing for vertical numbers; sample/real checks |
| Day07 parts1–2 | Beam propagation with deduplicated positions, then timeline multiplicity counting; local Python checks |
| Day08 parts1–2 | Sorted pair distances and union-find; extends to the final component-merging edge; Python cross-checks |
| Day09 parts1–2 | Pairwise rectangle area, then compressed-region containment; geometry cross-checks and concavity tests |

**Assessment:** the logs support derivation, coding, and validation from local
statements and project artifacts for the later parts, with intentional reuse of
current-run code and reviewer-produced helpers. They provide **no evidence of
internet solution lookup**. They also demonstrate that Day01 part1 was exposed
to an old solved version, and the reset left Git history/demo refs accessible.
We therefore cannot call the entire run independent or blind. No other solver
trace showed an explicit read of a pre-reset same-part solution; other historical
reads were current-run preceding-part code or workflow scripts.

A reasoning-token count of zero on some runs does not mean “no reasoning”: it
only means no separate reasoning tokens were reported there. Tool traces cannot
establish what was recalled from model training, and this inspection cannot
prove that every dependency or invoked executable lacked hidden network activity.
Those limits qualify the conclusion without changing the observed absence of
solution searches in the agent's recorded tools.

## What the measurements suggest improving

1. **Keep the two token rankings.** Track fresh input, cached input, output,
   reasoning-within-output, and step count separately. Preserve usage for
   interrupted runs, and reconcile against provider records when available.
2. **Centralize build recovery and verification.** SemanticDB/cache failures
   recurred on multiple days. A bounded helper should recognize that exact
   failure, apply the approved clean/rebuild procedure, and return a concise
   result. Document `testQuick`/`testFull` semantics so “no tests to run” does
   not trigger another configuration investigation. Retain meaningful tests.
3. **Reduce coordination/context repetition.** Pass exact task IDs and specialist
   IDs in handoffs; use one deterministic task helper instead of repeatedly
   listing agents/issues or copying prior descriptions. Return bounded build
   summaries and fetch diagnostic detail only when a check fails.
4. **Separate performance from completion latency.** Record solver-run time,
   queue time, submit/review time, and outage time. Day05 part1's overnight wait
   should not make the puzzle appear to require ten hours of algorithm design.
5. **If independent solving is the objective, isolate old solutions.** Use a
   fresh shallow reset checkout without the demo branch and avoid handing the
   solver pre-reset same-part tasks/answers. This requires an explicit policy;
   it is a recommendation, not a change made by this report. Keep current-run
   part1 code available for part2 and retain appropriate project helpers.

## Evidence and reproducibility

- [Per-part CSV][part-csv] contains exact UTC start/end timestamps, durations in
  seconds, token components, solver run IDs, stage totals and coverage.
- [Per-run usage CSV][run-csv] contains all 86 task-associated specialist runs,
  status, UTC times and recorded token components. Missing values are blank,
  not zero; the running reviewer is a partial row at this cutoff.
- Task/run links below identify the live evidence. Live task state may advance
  after the report cutoff. API summaries suppress usage, so metrics were read
  from individual run details and checked against paginated solver logs.
- Raw API responses/logs remain outside the company repo; only sanitized
  metrics and this analysis are included. No credentials or personal puzzle
  input contents are reproduced.
- The [earlier operational audit][audit] and [WatchDog repair report][repair]
  explain activation, the overnight interruption, and recovery. This report's
  refreshed evidence takes precedence for later progression and measurements.

[part-csv]: 2026-10-11-part-performance.csv
[run-csv]: 2026-10-11-part-run-usage.csv
[audit]: 2026-10-11-audit.md
[repair]: 2026-10-11-watchdog-repair.md

[AOC-4]: https://paperclip.tritsch.org/AOC/issues/AOC-4
[AOC-79]: https://paperclip.tritsch.org/AOC/issues/AOC-79
[AOC-81]: https://paperclip.tritsch.org/AOC/issues/AOC-81
[AOC-84]: https://paperclip.tritsch.org/AOC/issues/AOC-84
[AOC-87]: https://paperclip.tritsch.org/AOC/issues/AOC-87
[AOC-90]: https://paperclip.tritsch.org/AOC/issues/AOC-90
[AOC-92]: https://paperclip.tritsch.org/AOC/issues/AOC-92
[AOC-95]: https://paperclip.tritsch.org/AOC/issues/AOC-95
[AOC-98]: https://paperclip.tritsch.org/AOC/issues/AOC-98
[AOC-101]: https://paperclip.tritsch.org/AOC/issues/AOC-101
[AOC-104]: https://paperclip.tritsch.org/AOC/issues/AOC-104
[AOC-106]: https://paperclip.tritsch.org/AOC/issues/AOC-106
[AOC-108]: https://paperclip.tritsch.org/AOC/issues/AOC-108
[AOC-111]: https://paperclip.tritsch.org/AOC/issues/AOC-111
[AOC-114]: https://paperclip.tritsch.org/AOC/issues/AOC-114
[AOC-116]: https://paperclip.tritsch.org/AOC/issues/AOC-116
[AOC-119]: https://paperclip.tritsch.org/AOC/issues/AOC-119
[AOC-121]: https://paperclip.tritsch.org/AOC/issues/AOC-121
[AOC-124]: https://paperclip.tritsch.org/AOC/issues/AOC-124
[AOC-127]: https://paperclip.tritsch.org/AOC/issues/AOC-127
[AOC-140]: https://paperclip.tritsch.org/AOC/issues/AOC-140
[AOC-143]: https://paperclip.tritsch.org/AOC/issues/AOC-143
[AOC-146]: https://paperclip.tritsch.org/AOC/issues/AOC-146
[AOC-148]: https://paperclip.tritsch.org/AOC/issues/AOC-148
[AOC-152]: https://paperclip.tritsch.org/AOC/issues/AOC-152
[AOC-155]: https://paperclip.tritsch.org/AOC/issues/AOC-155
[AOC-158]: https://paperclip.tritsch.org/AOC/issues/AOC-158
[AOC-161]: https://paperclip.tritsch.org/AOC/issues/AOC-161
[AOC-165]: https://paperclip.tritsch.org/AOC/issues/AOC-165
[AOC-168]: https://paperclip.tritsch.org/AOC/issues/AOC-168
[AOC-171]: https://paperclip.tritsch.org/AOC/issues/AOC-171
[AOC-174]: https://paperclip.tritsch.org/AOC/issues/AOC-174
[AOC-178]: https://paperclip.tritsch.org/AOC/issues/AOC-178
[AOC-181]: https://paperclip.tritsch.org/AOC/issues/AOC-181
[AOC-184]: https://paperclip.tritsch.org/AOC/issues/AOC-184
[AOC-186]: https://paperclip.tritsch.org/AOC/issues/AOC-186
[AOC-190]: https://paperclip.tritsch.org/AOC/issues/AOC-190
[AOC-193]: https://paperclip.tritsch.org/AOC/issues/AOC-193
[run-171]: https://paperclip.tritsch.org/AOC/agents/d8d59234-cd22-4647-b57b-49f1a5e701a5/runs/82185a57-d3aa-44a4-afe3-afc2ce8406af
[run-190]: https://paperclip.tritsch.org/AOC/agents/d8d59234-cd22-4647-b57b-49f1a5e701a5/runs/3cfc54de-6bc4-4118-9bf7-ffc3d92ad4cd
[run-114]: https://paperclip.tritsch.org/AOC/agents/d8d59234-cd22-4647-b57b-49f1a5e701a5/runs/17c3907e-707b-4005-ae38-91172d52f5a6
[run-124]: https://paperclip.tritsch.org/AOC/agents/d8d59234-cd22-4647-b57b-49f1a5e701a5/runs/8b7a5bef-a762-40c6-bf44-d2353ff0073c
[run-81]: https://paperclip.tritsch.org/AOC/agents/d8d59234-cd22-4647-b57b-49f1a5e701a5/runs/73db4c48-bf6e-4c85-b743-ddc279ef1735
