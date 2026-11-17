# 06 Verification - 067
Verdict: PASS (round 1; earlier rounds: none)

Verified against committed HEAD dbcec96 ("Item 067: I2 build") on branch daily-fixes/2026-11-16. Tests, mutations and the diff re-run used a clean detached worktree of HEAD, `/tmp/claude-0/-home-claude/3184256a-8786-5c3c-8e7d-428ba8311b8c/scratchpad/wt-067-i3`. The worktree was removed afterwards. The repo tree was not edited for any of this; its uncommitted 068 edits (.claude/*, ccbot/realtest.py, tests/test_realtest.py) were not touched. reports/real/ was not regenerated. scratchpad/065-before and 065-after were read only and are kept. No brokerage was contacted. This is research tooling, not financial advice.

## I1 audit (plan vs research)
- 04's Rule trace covers every 03 map step: 1 (a)-(d), 2, 3 and 4. It also covers every Missing-inputs row and the 03 corrections (type-strict leaves, key per file, bot_rule key (ticker, config), trades key open_date, exact compare, widened trigger). Nothing in 03 is silently left out.
- The two DROPPED rows (step 4: own realtest runs and own worktree removal) have a reason: the orchestrator already ran both 065 runs into scratchpad/065-before and 065-after from wt-before/wt-after. 04 replaces them with SHA, data-identity and `-newer` checks, which is stricter than 03's single hash.
- 04's 6 changes are each sourced, with no unsourced addition:
  1. The trigger is shortened to the caller's sentence. The 03 list is referenced by path. I re-checked that realtest.py L54-57 imports only costs, expiries, config and pricing, and that L60-61 reads default.json and tickers.json.
  2. Step 4 has no re-run (see the DROPPED rows above).
  3. Data identity is checked per worktree copy, because data/real is tracked.
  4. The 0-trade file case is test (l). Its pandas text was UNVERIFIED in 04. I2 measured it as `'\n'`, and I re-measured the same value: `python3 -c "import pandas as pd; print(repr(pd.DataFrame([]).to_csv(index=False)))"` gives `'\n'`.
  5. `not compared` is added to TOTAL.
  6. 068 reuse fixes the formats, and `diff_dirs()` is importable.
- No rule the person follows (001) changes. ccbot/ and config/ are untouched (`git diff --stat HEAD~1 -- ccbot config reports data` is empty).

## I2 audit (build vs plan)
I read `git show HEAD` line by line against 04 Files 1-5:
- **scripts/diff_reports.py**: stdlib only (argparse, csv, json, math, sys, pathlib).
  - `load_json`: uses parse_constant, counts NaN, and raises BAD JSON on a ValueError or UnicodeDecodeError.
  - `diff_json`:
    - Dicts take the sorted union of keys and print ADDED/REMOVED.
    - Lists are index-aligned, with LENGTH plus ADDED/REMOVED.
    - TYPE is printed when `type(a) is not type(b)`. A leaf is equal only if `a == b` or both are NaN.
    - It never uses `==` on a container. Containers recurse only when both sides are dicts or both are lists. A dict on one side and a list on the other is a TYPE line.
  - `read_csv`:
    - Uses `csv.reader` with `newline=''` and utf-8.
    - A duplicate header exits 2 with DUPLICATE COLUMN.
    - A row after an empty header, or a ragged row, exits 2 with BAD ROW.
    - A 0-byte file gives `([], [])`.
  - `KEYS` and `TRADES_KEY` match 04 exactly.
  - `diff_csv`:
    - The COLUMNS line comes first, including an `(order changed)` case.
    - The key is used only if all its columns are on both sides. Otherwise a `MATCH <f>: index (<why>)` line is printed.
    - The counts line is in 04's format.
    - Changed/added rows are listed in after-file order, then removed rows in before-file order. The cap prints `  ... k more`, and `--max-rows 0` prints all.
    - A duplicate key exits 2.
  - `diff_dirs`:
    - MISSING DIR / EMPTY DIR.
    - ONLY IN with the row count for a CSV.
    - NOT COMPARED for other files and subdirs, counted in TOTAL.
    - The TOTAL format is as in 04, and `no change` is printed only when every change count is 0.
  - `main`: exit 0/1/2. Errors go to stderr only, and BAD ARG covers a negative `--max-rows`.
- **tests/test_diff_reports.py**: tests (a)-(o), (p) `test_committed_reports_self_diff`, plus `test_diff_dirs_importable` = 17. 04 said 16. The 17th is the import test that 04 Files 2 asks for ("Also importable"), so this is a counting deviation, not a scope change. 05 Deviations states it.
- **templates/build-report.md** and **templates/verification.md**:
  - The section and comment are verbatim from 04 Files 3/4.
  - build-report has it after `## Test output`. verification has it after `## Tests re-run (output)`, with the TOTAL sentence.
  - `grep -n "Real-data effect"` gives 1 hit in each file.
- **Connectivity**:
  - Every function is reached from `main` or `diff_dirs`, and `diff_dirs` is also called by the import test.
  - The output's consumer is the new template field, which 05 uses.
  - `grep -n TODO` finds nothing in either file.
- **Edge probes (scratch dirs, not tests)**:
  - A blank header line followed by a row gives `BAD ROW trades_A.csv line 2: 2 fields, header has 0` and exit 2.
  - A stray run.log plus a subdir give `NOT COMPARED: run.log` and `NOT COMPARED: sub/`, then `not compared 2`, `no change` and exit 0. This is by design (04 change 5).
  - `--max-rows -1` gives `BAD ARG` and exit 2.
  - A header reorder gives `COLUMNS ... (order changed)`.
  - summary.json on one side only gives `ONLY IN AFTER: summary.json` and exit 1.
- **Missing-data grep**: 37 hits in ccbot/ at HEAD (same as 05). 067 changes nothing in ccbot/. On 067's files there is 1 hit, `scripts/diff_reports.py:319: return 1 if _has_change(totals) else 0`. That is the exit code computed from int counts, not a default for absent data. I agree with 05's reason.
- **BUG guardrail (step 3)**: the fix is the script plus the template field. The prevention guardrail is test (a), the nested-key fixture. It would have caught the original error: a top-level-only or hand-picked-key comparison of 065's dirs misses `monte_carlo_2_stocks_1yr.cc_ret.50` and `walkforward_picks[5].picked`. Mutations 1 and 1b below show that test (a) fails as soon as nested keys are skipped. The re-run on 065's real dirs prints all the effects that 065/05-07 left out.
- **RI-012 (item 059)**: the script classifies no error or reply by matching text. The only name test is `startswith("trades_")` on file names. Not applicable.
- **Item 062**: there is no simulator or picker. Not applicable.
- **Rule text (001)**: unchanged, and no rule the person follows changed.

## Tests re-run (output)
Clean worktree at HEAD dbcec96:
```
$ python3 -m pytest -q
341 passed, 1 skipped in 53.01s
$ python3 -m pytest -q -rs | grep SKIP
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'
$ python3 -m pytest -q tests/test_diff_reports.py -v
collected 17 items
tests/test_diff_reports.py .................                             [100%]
17 passed in 0.67s
$ python3 -m pytest -q tests/test_safety.py -k oldest
1 passed, 8 deselected in 0.10s
$ which python3.10 python3.11
/usr/bin/python3.11
$ python3.11 -c "<py_compile each>" scripts/diff_reports.py tests/test_diff_reports.py
ok 3.11
$ grep -nE "QUOTE_(STRINGS|NOTNULL)" scripts/diff_reports.py ; echo grep-exit $?
grep-exit 1
```
341 = 324 (base a6d6b39 in 05) + 17. `test_every_py_compiles_on_oldest_python` ran with python3.11, because python3.10 is not on PATH. It did not skip, and the new files are tracked at HEAD, so they are covered.

`python3 scripts/check_handoff.py 067`:
```
sources count (unique URLs in 01-research.md): 3
fact-check rows: 44
totals line: 44 rows -> 28 as-is, 16 fixed, 0 removed
PASS
```

Mutations (I3, my own script `/tmp/claude-0/-home-claude/3184256a-8786-5c3c-8e7d-428ba8311b8c/scratchpad/i3-067/mut_i3.py`, which edits only the scratch worktree's scripts/diff_reports.py and restores it after each):
```
mutation 1 recursion cut to top level: 5 failed, 12 passed in 0.72s; target test_a_nested_key_and_list_in_dict failed: True
    FAILED tests/test_diff_reports.py::test_a_nested_key_and_list_in_dict
    FAILED tests/test_diff_reports.py::test_b_identical_with_nan_and_empty_cells
    FAILED tests/test_diff_reports.py::test_c_type_changes
    FAILED tests/test_diff_reports.py::test_j_list_length
    FAILED tests/test_diff_reports.py::test_diff_dirs_importable
mutation 1b nested dict recursion skipped below root: 1 failed, 16 passed in 1.47s; target test_a_nested_key_and_list_in_dict failed: True
    FAILED tests/test_diff_reports.py::test_a_nested_key_and_list_in_dict
mutation 2 key -> index for walkforward_by_ticker: 4 failed, 13 passed in 0.73s; target test_e_added_ticker_matched_by_key failed: True
    FAILED tests/test_diff_reports.py::test_e_added_ticker_matched_by_key
    FAILED tests/test_diff_reports.py::test_k_no_tolerance_on_csv_cells
    FAILED tests/test_diff_reports.py::test_n_key_column_one_side
    FAILED tests/test_diff_reports.py::test_committed_reports_self_diff
mutation 3 both-NaN check removed: 1 failed, 16 passed in 0.72s; target test_b_identical_with_nan_and_empty_cells failed: True
    FAILED tests/test_diff_reports.py::test_b_identical_with_nan_and_empty_cells
mutation 4 EMPTY DIR check removed: 1 failed, 16 passed in 0.68s; target test_i_missing_and_empty_dir failed: True
    FAILED tests/test_diff_reports.py::test_i_missing_and_empty_dir
mutation 5 type check removed (plain ==): 1 failed, 16 passed in 0.68s; target test_c_type_changes failed: True
    FAILED tests/test_diff_reports.py::test_c_type_changes
restored: 17 passed in 0.68s
git diff after restore: (clean)
```
- Mutation 1 is 04's form: the dict branch prints only the key when `a[k] != b[k]`, at the root.
- Mutation 1b is mine: any dict below the root is skipped. Only (a) catches it. That makes (a) the RI-013 GUARDED probe.
- Mutations 1-5 match 05's counts exactly (5, 4, 1, 1, 1 failed).

## Real-data effect (diff_reports output, pasted)
not required for 067's own change (`git diff --stat HEAD~1`: logs/implementation/2026-11-16.md, scripts/diff_reports.py, templates/build-report.md, templates/verification.md, tests/test_diff_reports.py, work/067/05-build-report.md; nothing in ccbot/, config/ or data/real).

065's full effect (the item's deliverable, 05 § Real-data effect): I re-ran the script on the same dirs from the HEAD worktree.
```
$ python3 scripts/diff_reports.py scratchpad/065-before scratchpad/065-after > scratchpad/i3-067/diff-i3.txt ; echo "exit $?"
exit 1
$ tail -1 scratchpad/i3-067/diff-i3.txt
TOTAL: files 22, only-before 0, only-after 0, not compared 0, json changes 67, csv rows changed 219 added 3 removed 8, columns changed 2
$ cmp scratchpad/i3-067/diff-i3.txt scratchpad/067-diff.txt && echo identical
identical
$ (05's pasted block, extracted between the command line and `exit 1`) | cmp - scratchpad/i3-067/diff-i3.txt && echo identical
identical
sha256 (all three): d812fe218af4b634f230b0f520c3685dca0a86dc360185d2396f47457120c868, 188 lines
```
The TOTAL line equals 05's. The whole 188-line output is byte-identical to 05's paste and to scratchpad/067-diff.txt.

Inputs I re-checked:
- `git rev-parse e129253^` gives 5883ba4fa702…. `git worktree list` shows wt-before at 5883ba4 and wt-after at c659560.
- `git diff --stat e129253 c659560 -- ccbot config` and `git diff --stat e129253^ c659560 -- data/real` are both empty. `git status --short data/real` is empty.
- The data/real hash is `fa29a0e8ca1d448c424c6dc4041d98f7fae44e003b4e8517ee9c98ae337798ba`, 135 files, the same as 05. `find data/real -type f -newer <out>/trades_AAL.csv` finds 0 files for both outputs. Each dir has 22 files.
- The python/pandas version is the same as 05: 3.13.18, pandas 3.0.5.

05's comparison table, recomputed from the two dirs (scratch one-liner):
- excess_cagr changed with exact compare in 16 of 17 tickers, and with |Δ| > 1e-9 in 11 of 17. Positive count: strict `> 0` gives 6 -> 5, and `> 1e-9` gives 5 -> 4. These match 05 and A1.
- cc_ret.50 rounds to 0.0689 -> 0.0686. bxm_vs_spy is equal on both sides. picked=2, in windows 5 and 9 with A1's labels. MO calls_sold 23 -> 21 and MDLZ 34 -> 31.
- 05's table is accurate.

Container-restart note (05 Deviations), checked:
- scratchpad/067-diff.txt was written at 23:42:20 UTC and 067-tests.txt at 23:43:10. scratchpad/05-head.md (I2's partial 05, 189 lines) was written at 23:44:10.
- The machine booted at 23:44:40 UTC (`uptime -s`, PID 1 start). The commit is at 23:45:41.
- 05-head.md is identical to the first 189 lines of the committed 05 (`diff` is empty). The orchestrator only appended the pasted diff, the comparison table, Deviations and the RI line.
- The pasted diff is byte-identical to 067-diff.txt.
- The claim is accurate. The orchestrator's "17 passed in 0.67s" has no file behind it (067-tests.txt says 0.71s, I2's run). My own re-run gave 17 passed in 0.67s, so nothing depends on it.

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-002, RI-013 (also RI-006, RI-008, RI-010, RI-012)
- **RI-001 (ESCALATED)**: every key rule has a count.
  - Picks 10/10, by_ticker 17/17, bot_rule (ticker, config) 54/54, grid 1,020/1,020 and trades open_date 250/250 hold on the committed reports/real. That is test (p) plus 05's self-diff.
  - On 065's real dirs every keyed file is `match key` with no DUPLICATE KEY.
  - The cap rule (25 -> 20 + 5 more) is test (f). The no-tolerance rule (0.0003) is tests (a) and (k).
- **RI-002 (ESCALATED)**: no absent input becomes `no change`.
  - MISSING DIR and EMPTY DIR (mutation 4 fails (i)), BAD JSON, BAD ROW, a blank header then a row (my probe) and DUPLICATE KEY all exit 2. A one-side file is exit 1. NaN is counted, not dropped (mutation 3 fails (b)).
  - The edges of the data window are covered: an empty file and the `'\n'` file (l), a list that is shorter or longer (j), and a file on one side only (d).
  - A stray non-report file is counted as `not compared`, by design.
- **RI-013 (OPEN)**: this item. The guardrail is in place, and both nested-skip mutations (1, 1b) fail test (a). GUARDED when 067 is merged and mutation 1b fails on main.
- **RI-006**: every count here is pasted from command output.
- **RI-008**: compiles with python3.11 (no 3.10 on PATH), and the QUOTE_ grep finds nothing.
- **RI-010**: still a gap. Nothing checks that the new field is filled when the trigger files change (04's follow-up). It is passed on to A1.
- **RI-012**: not applicable, because the script does no substring classification.

## Pipeline line (step 2)
check_pipeline line: `067: awaiting A1 (FULL)` (run after 06, 07 and the I3 log line; exit 0, INCOMPLETE none, SKIPPED none, LOG TIME none)

## Sent back / sent to Audit
PASS, sent to Audit: work/067/07-audit-task.md.
