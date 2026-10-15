# Code quality Days01–09: Scala vs Python (LLM-as-judge, 1–5)

Scope: **Days 01–09, part 1 + part 2 = 18 parts per language** (Day00 template excluded).
Method: **Option B, LLM-as-judge**, with Option A automated metrics as evidence.
Date: **2026-10-15**. Judge model: **Muse Spark (opencode)**. No rescoring loop was run;
scores are single-pass with evidence cited so they can be reproduced or challenged.

Outputs in this folder:

- `2026-10-15-code-quality-days01-09.csv`: 36 rows (day, part, lang, 5 dims, mean, band, loc)
- `2026-10-15-chart-quality-days01-09.{svg,png}`: grouped mean per part
- This file: framework doc + provenance + summary (how the rating came to be)

## Rating framework (documented)

No single industry 1–5 exists for AoC-style generated code, so this adapts
**ISO/IEC 25010 maintainability + SIG/SQALE** practice into 5 equally weighted
(20%) dimensions, each scored 1 (poor) to 5 (excellent):

1. **Correctness robustness** — input validation, edge/boundary handling beyond the happy path.
2. **Readability/structure** — naming, parse-vs-solve split (mandated by both `AGENTS.md`), function size.
3. **Idiomatic use** — Scala3: `enum/case class, foldLeft, require, Vector`; Python: typed `def`s +
   docstrings, `snake_case`, `NamedTuple/Sequence`, silent import (per repo conventions).
4. **Test depth** — sample + real-input + boundary banks; per-part `test_part1_*/test_part2_*`
   (Python) vs per-day suites (Scala).
5. **Simplicity/efficiency** — stated Big-O fit for the puzzle; no gratuitous deps.

`mean = avg(5 dims)`, rounded to 2 decimals; `band = round(mean)` to 1–5.
Scale: 1 poor (needs rewrite), 2 fair, 3 good, 4 very good, 5 excellent.
Both **independent** (absolute per language) and **head-to-head** (`python − scala` delta) views are reported.

## Provenance (how the rating came to be)

- Pinned sources: `python-aoc-2025 @ 1a7f1c1ceadfa0dfa305151a862ffd38ccf2168e`
  (Day10 solve p2; Days01–09 unchanged after), `scala3-aoc-2025 @ e3bec64ee402f38c433312a32506fdc0c0395918`.
- Files read fully: `src/aoc2025/day01.py–day09.py`, `Day01.scala–Day09.scala`
  (representative Day01 quoted below; all 18+18 judged the same way).
- Automated evidence: `wc -l` src+tests (see CSV `src_loc/test_loc`),
  Python `ruff check` clean / `ruff format --check` 56 files formatted,
  Python per-day `def test_` counts 20–33, Scala test files 45–101 lines;
  `sbt`/coverage not re-run (prior CI green: Python 377 passed ~99%, Scala Day01–09 green).
- Calibration: Day01 both langs scored first as anchor (both 5-class); spread rule (>0.5 triggers
  re-read) applied mentally; no second model used.
- Limits: single judge, no blinded multi-rater agreement; efficiency judged from stated/documented
  complexity + code reading, not benchmarks; test depth partly from counts, not mutation testing.

## Results summary

Averages over 18 parts: **Python 4.67, Scala 4.04, delta +0.62** in Python's favour.
Both solve everything; the gap is code shape, not correctness.

| Day | Python p1/p2 | Scala p1/p2 | Delta p1/p2 | Note |
| --- | --- | --- | --- | --- |
| 01 | 5.0 / 5.0 | 4.8 / 4.8 | +0.2 / +0.2 | Both exemplary; Python O(1) click math + more tests |
| 02 | 4.2 / 4.2 | 3.8 / 3.8 | +0.4 / +0.4 | Both brute-force scans; Python docs/tests stronger |
| 03 | 5.0 / 5.0 | 3.6 / 4.2 | +1.4 / +0.8 | Python suffix-max O(n); Scala p1 O(n²) |
| 04 | 5.0 / 5.0 | 4.6 / 3.6 | +0.4 / +1.4 | Python queue O(R·C); Scala rounds O((R·C)²) |
| 05 | 5.0 / 5.0 | 3.6 / 4.6 | +1.4 / +0.4 | Python merge+bisect; Scala p1 O(r·a) naive |
| 06 | 4.4 / 4.2 | 3.8 / 3.8 | +0.6 / +0.4 | Both imperative grid scans; Python tests deeper |
| 07 | 5.0 / 5.0 | 3.8 / 3.8 | +1.2 / +1.2 | Same asymptotics; Python set/dict + validation cleaner |
| 08 | 4.0 / 4.0 | 4.0 / 4.0 | 0.0 / 0.0 | Both heap/sorted DSU with duplicated helpers |
| 09 | 4.4 / 4.6 | 3.8 / 4.4 | +0.6 / +0.2 | Both strong p2 (prefix/compressed regions); Scala p1 thinner tests |

Largest gaps: Day03p1, Day04p2, Day05p1 (algorithm choice); smallest: Day08 (tie).
Per-part means and 5-dim breakdowns are in the CSV; see chart for visual deltas.

## Why Scala scores lower than Python

Scala is not failing — both languages solve all 18 parts. The gap is code shape,
not correctness. It concentrates in **efficiency + test depth**, which drag the
5-dim mean down:

- **Day03p1 (+1.4):** Python `src/aoc2025/day03.py:38-55` uses a suffix-max O(n)
  scan; Scala `src/main/scala/aoc2025/Day03.scala:53-56` enumerates all pairs O(n²).
- **Day04p2 (+1.4):** Python `src/aoc2025/day04.py:110-136` uses a single queue
  cascade O(R·C); Scala `src/main/scala/aoc2025/Day04.scala:112-126` re-scans the
  whole grid per round O((R·C)²).
- **Day05p1 (+1.4):** Python `src/aoc2025/day05.py:114-122` merges ranges plus
  `bisect` O(n log n); Scala `src/main/scala/aoc2025/Day05.scala:91` does a linear
  `exists` per ID O(r·a).
- **Day07 (+1.2 both parts):** same asymptotics, but Python `src/aoc2025/day07.py:59-84`
  set/dict plus strict `S`/ragged validation reads cleaner than Scala
  `src/main/scala/aoc2025/Day07.scala:59-73` `var` loops with thinner checks.
- **Tests:** Python `tests/test_dayNN.py` has 20–33 `def test_` per day with
  sample + real + boundary banks; Scala `DayNNTest.scala` is 45–101 lines total
  with fewer banks — loses 1–2 pts on the test-depth dim across Days 02, 05–09.

Day08 ties 4.0/4.0 — both use heap/sorted DSU with duplicated helpers.

Net: **Python 4.67 vs Scala 4.04**. Treat 0.2 gaps as noise, ≥0.8 as signal.

## Reproduce / challenge

1. Check out the two SHAs above.
2. Re-run `wc`, `ruff check`, per-day test counts; compare to CSV.
3. Re-score any part with the 5-dim rubric; cite lines (e.g. `day03.py:50-55` suffix-max
   vs `Day03.scala:53-56` O(n²) pairs; `day04.py:110-136` queue vs `Day04.scala:112-126` rounds;
   `day05.py:114-122` bisect vs `Day05.scala:91` linear `exists`).
4. If a dim changes by ≥1, file an issue against this report with the new evidence.

No human panel (Option C) was convened; treat 0.2 gaps as noise, ≥0.8 as signal.
