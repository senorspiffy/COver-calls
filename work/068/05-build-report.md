# 05 Build report - 068
## Changes made (file: what changed)
Base (branch head before any 068 commit): 0f11c306440b843529dc2a413f31c9731f737d5b.

File counts (from commands, 012):
- new: `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` -> `0`
- changed: `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` -> `5`

Plan said 5 files (0 new, 5 changed). Matches.

1. `ccbot/realtest.py`
   - `load_ticker`: deleted `if gaps:` / `warnings.append(f"earnings: {gaps} gap(s) > {EARNINGS_GAP_WARN} days between dates")`. Kept `gaps = len(_gap_pairs(earnings))` and `earnings_gaps=gaps`.
   - `simulate`: the kept line now reads `f"earnings: {len(gap_pairs)} gap(s) > {EARNINGS_GAP_WARN} days between listed dates ("`. The rest of the line is unchanged. It uses `len(gap_pairs)`, not `td.earnings_gaps`.
   - `_gap_pairs` docstring: added "(one warning line, from simulate; item 068)".
2. `tests/test_realtest.py`
   - New `test_one_gap_warning_with_count_and_dates`, with the 4 asserts from 04 Files 2. It counts `"gap(s)"` in the joined string (C2).
   - `test_interior_gap_180_blocks`: added the `w[0].startswith(f"earnings: 1 gap(s) > {rt.EARNINGS_GAP_WARN} days between listed dates (")` assert (C1).
3. `.claude/commands/run-item.md`: new last paragraph with the `--tickers <affected> --out <scratch>` iteration rule, one full run per publishing step, and the base-reuse-only-with-same-inputs clause (C6). Contains one `item 068`.
4. `.claude/agents/i2-builder.md` step 3: appended 03 step 5's sentence, using C6's wording "unless a full run with the same inputs exists (`git diff --stat <its commit> <base> -- ccbot/ config/` empty, same data dir; name its path and commit in 05)".
5. `.claude/agents/i3-verifier.md` step 2: appended 03 step 6's sentence, using C6's wording "if that run is gone or its inputs differ from the base's (same check as i2 step 3)".

## Connectivity check
- [x] every new function/rule is used. No new function. The edited f-string is reached when `gap_pairs` is non-empty (fixture: new test, `test_interior_gap_180_blocks`; real data: 5 tickers). The agent text is read by the run-item orchestrator, I2 step 3 and I3 step 2.
- [x] every input has a source, every output has a consumer. `len(gap_pairs)` comes from `_gap_pairs(td.earnings)` (same call as before). The warning goes to `df.attrs["warnings"]`, then `summarize`'s `warnings`, then summary.json `counts_bot_rule_bid.<tk>.warnings` and bot_rule_by_ticker.csv `warnings` (real-data diff below). `earnings_gaps` / `earnings_gaps_gt120` keep their source (load_ticker `gaps`) and consumer.
- [x] every branch ends in a defined result. No gaps: no line (unchanged; `test_drop_input[earnings]` and `test_empty_earnings_file_warns_and_lead_is_null` pass). ETF: `gap_pairs = []`, no line (unchanged). Gaps: one line with count and dates, plus EARNINGS_UNKNOWN or "earnings not checked by this rule".
- [x] no leftover TODOs or unused files. `git diff | grep -c TODO` adds none. No new committed files. The scratch scripts stay in the scratchpad (see below).

Plan greps (04 Tests 5):
```
$ grep -n 'between dates"' ccbot/realtest.py; echo "hits=$?"
hits=1                      # grep exit 1 = 0 hits
$ grep -c "item 068" .claude/commands/run-item.md .claude/agents/i2-builder.md .claude/agents/i3-verifier.md
.claude/commands/run-item.md:1
.claude/agents/i2-builder.md:1
.claude/agents/i3-verifier.md:1
$ git diff --numstat -- .claude/
1	1	.claude/agents/i2-builder.md
1	1	.claude/agents/i3-verifier.md
2	0	.claude/commands/run-item.md
```
Additions only. Each 1/1 pair is the old line with text appended. The only in-line rewording is the plan's C6 replacement of the trailing clause, and the run-item.md change is a blank line plus the new paragraph.

Missing-data grep:
```
$ grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/ | wc -l
37
$ git diff -U0 ccbot/ | grep -nE "<same pattern>"; echo rc=$?
rc=1
```
No new or changed hit. The 37 hits are all pre-existing, and none is in a line 068 touches. Patterns the grep can't see (014): `git diff -U0 ccbot/ | grep -E "^\+.*(: float = |[<>])"` matches only 2 lines. One is the docstring text `warned <=> blocked`. The other is the f-string literal `gap(s) > {EARNINGS_GAP_WARN}`, which is text, not a comparison. There is no new dataclass field and no new `>`/`<` test.

## Test output (pasted, not summarized)
Base suite at 0f11c30 (scratch worktree `/tmp/claude-0/-home-claude/3184256a-8786-5c3c-8e7d-428ba8311b8c/scratchpad/wt-068-mut2`, clean checkout):
```
$ python3 -m pytest -q -p no:cacheprovider
341 passed, 1 skipped in 54.31s
```
Repo tree with the 068 edits:
```
$ python3 -m pytest -q -p no:cacheprovider
342 passed, 1 skipped in 54.38s
$ python3 -m pytest -q -p no:cacheprovider tests/test_realtest.py
50 passed in 24.67s
$ python3 -m pytest -q -p no:cacheprovider tests/test_realtest.py::test_one_gap_warning_with_count_and_dates tests/test_realtest.py::test_interior_gap_180_blocks
2 passed in 4.27s
```
Expected was base + 1 passed, skipped unchanged, 0 failed. Result: 341 -> 342, 1 -> 1, 0 failed.

Mutations (04 Tests 4). All were run in the scratch worktree `wt-068-mut2` (0f11c30 + the 068 copies of realtest.py and test_realtest.py), never in the repo. realtest.py was restored from a saved copy after each mutation, and `cmp` with the repo file afterwards printed `restored`:
```
M1 (restore load_ticker "between dates" line)
FAILED tests/test_realtest.py::test_one_gap_warning_with_count_and_dates - As...
1 failed, 341 passed, 1 skipped in 55.51s
M2 (drop "{len(gap_pairs)} ")
FAILED tests/test_realtest.py::test_interior_gap_180_blocks - AssertionError:...
FAILED tests/test_realtest.py::test_one_gap_warning_with_count_and_dates - As...
2 failed, 340 passed, 1 skipped in 53.59s
M3 (len(gap_pairs) -> td.earnings_gaps)
FAILED tests/test_realtest.py::test_interior_gap_180_blocks - AssertionError:...
1 failed, 341 passed, 1 skipped in 51.65s
M4 (remove `if _is_gap(...): return "interior_gap"` in _earnings_state)
FAILED tests/test_realtest.py::test_interior_gap_180_blocks - AssertionError:...
FAILED tests/test_realtest.py::test_interior_gap_121_blocks - AssertionError:...
FAILED tests/test_realtest.py::test_drop_input[earnings_interior_gap] - asser...
FAILED tests/test_realtest.py::test_real_interior_gap_mo - AssertionError: as...
4 failed, 338 passed, 1 skipped in 54.09s
```
Expected was M1 >= 1, M2 >= 2, M3 >= 1, M4 >= 1. All four were met.

Feasibility numbers (real): fixture gap count `earnings_gaps_gt120 == 1 == td.earnings_gaps` (new test passes); real data: 5 of 17 published tickers changed (CMCSA, MDLZ, MO, T, VZ), 15 CSV rows, as listed below.

`python3 scripts/check_pipeline.py` (before 05): `068: in progress (FULL: next 05)`, `UNTRACKED CHANGE: none`; LOG TIME does not name 068.

## Real-data effect (diff_reports output, pasted)
- Before: `/tmp/claude-0/-home-claude/3184256a-8786-5c3c-8e7d-428ba8311b8c/scratchpad/065-after`, full run at c659560. Reuse precondition (04 Tests 1, C3): `git diff --stat c659560 0f11c30 -- ccbot/ config/` printed nothing (rc=0).
- After: `/tmp/claude-0/-home-claude/3184256a-8786-5c3c-8e7d-428ba8311b8c/scratchpad/068-after`, full run from worktree `wt-068-head` (a6d6b39 + the 068 edits). Its realtest.py and test_realtest.py are `cmp`-identical to the repo tree. `git diff --stat a6d6b39 0f11c30 -- ccbot/ config/` touches only tests/test_diff_reports.py, so ccbot/ and config/ are equal.
- Command: `python3 -m ccbot.realtest --data /home/claude/cover-calls/data/real --out <scratch>/068-after`. Wall clock: real 13m42.704s, user 13m33.668s (068-after.log).
- Data: `/home/claude/cover-calls/data/real` is git-tracked (135 files). `git diff --stat c659560 HEAD -- data/real` printed nothing, and `git status --porcelain -- data/real` printed nothing, so both runs used the same data. `find . -type f | sort | xargs sha256sum | sha256sum` gives `fa29a0e8ca1d448c424c6dc4041d98f7fae44e003b4e8517ee9c98ae337798ba` (135 files).
- Python 3.13.18, pandas 3.0.5.
- `python3 scripts/diff_reports.py --max-rows 0 065-after 068-after` exits 1 (differences found). The whole output is in `/tmp/claude-0/-home-claude/3184256a-8786-5c3c-8e7d-428ba8311b8c/scratchpad/068-diff.txt` (43 lines). Its per-file headers and the TOTAL line:
```
CSV bot_rule_by_ticker.csv: match key, rows 54 -> 54, matched 54, added 0, removed 0, changed 15; by column: warnings=15
  (15 rows: CMCSA, MDLZ, MO, T, VZ x bid/quarter/mid; each 'earnings: 1 gap(s) > 120 days between dates; ...; earnings: gap(s) > 120 days between listed dates (<a>→<b>); ...' -> '...; earnings: 1 gap(s) > 120 days between listed dates (<a>→<b>); ...')
CSV grid_in_sample.csv: match key, rows 1020 -> 1020, matched 1020, added 0, removed 0, changed 0; by column: none
JSON summary.json: NaN tokens: before 0, after 0; changes 5
  (counts_bot_rule_bid.{CMCSA,MDLZ,MO,T,VZ}.warnings: same transform)
TOTAL: files 22, only-before 0, only-after 0, not compared 0, json changes 5, csv rows changed 15 added 0 removed 0, columns changed 0
```
The 15 row lines and 5 JSON lines are pasted in full, with the exact strings, in 068-diff.txt. Each one deletes the count-only part and adds `1 ` to the listed-dates part. Nothing else changes.

Exact-transform check (04 Tests 6b, `fix(base)`), script `/tmp/claude-0/-home-claude/3184256a-8786-5c3c-8e7d-428ba8311b8c/scratchpad/compare_068.py` (uncommitted), output `068-compare.txt`:
```
files: base 22, head 22; byte-identical (excl. 2 compared below): 20 of 20
summary.json: leaves compared 487; warnings leaves changed by fix: 5 ['CMCSA', 'MDLZ', 'MO', 'T', 'VZ']
bot_rule_by_ticker.csv: rows compared 54; rows changed by fix: 15
RESULT: PASS
```
This matches 04's expected result: 5 warnings leaves, 15 CSV rows, and every other file, leaf and cell identical.

Timed `--tickers` run (04 Tests 6c), from `wt-068-head`:
```
$ time python3 -m ccbot.realtest --data /home/claude/cover-calls/data/real --tickers CMCSA,MDLZ,MO,T,VZ --out <scratch>/068-tk
real	3m57.339s
user	3m55.643s
sys	0m0.296s
```
Compared with 068-after by `/tmp/claude-0/-home-claude/3184256a-8786-5c3c-8e7d-428ba8311b8c/scratchpad/compare_068_tk.py` (uncommitted, 27 lines). It checks trades_<tk>.csv byte-for-byte, `counts_bot_rule_bid[tk]` by repr, `skipped` entries keyed by the 5 names, grid_in_sample.csv rows for the 5 names, and bot_rule_by_ticker.csv rows for the 5 names + SPY (C5). Output:
```
trades files byte-identical: 5 of 5
counts_bot_rule_bid compared: 5; skipped for 5 names: {}
grid_in_sample.csv: rows full 300, tickers-run 300, equal True
bot_rule_by_ticker.csv: rows full 18, tickers-run 18, equal True
RESULT: PASS
```
The first version of the script filtered `skipped` by substring, so `"T"` matched inside "ITUB". It printed `RESULT: FAIL skipped differs`. That was a bug in the script, not a data difference: full-run `skipped` = {ITUB, KGC, PBR, VALE}, none of them among the 5 names. I fixed it to match the dict keys exactly and reran (output above). Not compared (portfolio-wide, 03 F5-F10): walkforward_*, monte_carlo, period, bxm_vs_spy, tickers, fits_3k.

`git status --short reports` printed nothing.

## Deviations from plan
- A container restart cut off the previous I2 session after the code edits. The orchestrator then made both full real-data runs (c659560 base reused under C3, and the 068 head run in `wt-068-head` with the same edits), plus the diff_reports and compare_068 outputs. This session checked that the head worktree's two code files are `cmp`-identical to the repo tree. It did not re-run them.
- 04 Tests 6b: `scripts/diff_reports.py` exists on the branch (item 067), so its output is the whole-output comparison. The orchestrator's compare_068.py additionally checks 04's exact `fix(base)` transform. Its full text is in the scratchpad, not pasted here.
- 04 Tests 6c: the orchestrator's message suggested `--tickers MO --out scratchpad/068-mo`. 04 names `--tickers CMCSA,MDLZ,MO,T,VZ`, so the plan's run was made instead (`068-tk`).
- Mutations ran in a fresh worktree `wt-068-mut2` at 0f11c30, not in the older `wt-068-mut` (a6d6b39, with leftover edits). By mistake I created a stray symlink `data/real/real` in wt-068-mut2 and removed it before any mutation (`git status` there then showed only the 2 copied files).

## Recurring issues checked
Checked against every open or ESCALATED entry in logs/recurring-issues.md:
RI-001: ESCALATED, checked. The feasibility numbers are real and non-zero: fixture 1 gap; 5 of 17 tickers, 15 rows (diff above).
RI-002: ESCALATED, unchanged. No value is defaulted, and there is no new grep hit. M4 (interior-gap block removed) still fails 4 tests.
RI-004/RI-005: checked. The M1-M3 fail reasons match 04 (2 lines vs 1; "0 gap(s)" from `_tiny`'s `earnings_gaps=0`).
RI-007: checked. Scope is FULL. The `.py` comparison scripts are scratchpad only and are not under work/.
RI-009: checked. Mutations and runs were made only in scratch worktrees and dirs. The repo tree was never mutated, and `git status --short reports` is empty.
RI-010: checked. The log line is written with `check_pipeline.py --log` right after this file.
RI-013: OPEN. 068 does not build 067's guardrail. 068's own real-data check is whole-output (diff_reports TOTAL + compare_068 exact transform), with no hand-picked keys.
RI-003, RI-006, RI-008, RI-011, RI-012: not applicable (no calendar, no fact-check totals, a 3.10-safe f-string edit, no branch-diff logic, no text-classified errors).
