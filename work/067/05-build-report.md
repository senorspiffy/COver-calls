# 05 Build report - 067
## Changes made (file: what changed)
- scripts/diff_reports.py (new, stdlib only): `load_json`, `diff_json`, `read_csv`, `KEYS` (+ trades_*.csv → open_date), `diff_csv`, `diff_dirs`, `main` as in 04 Files 1. Exit 0/1/2; TOTAL line with `not compared`; `MISSING DIR` / `EMPTY DIR` / `BAD JSON` / `BAD ROW` / `BAD CSV` / `DUPLICATE KEY` / `DUPLICATE COLUMN` go to stderr with exit 2 and nothing on stdout. Docstring states the two known limits (index-aligned JSON lists; NaN/None/'' indistinguishable in a CSV).
- tests/test_diff_reports.py (new): 04 tests (a)-(o), (p) `test_committed_reports_self_diff`, and `test_diff_dirs_importable` (sys.path pattern of tests/test_pipeline_check.py L495). 17 tests.
- templates/build-report.md: new `## Real-data effect (diff_reports output, pasted)` section after `## Test output`, with 04's trigger comment verbatim.
- templates/verification.md: same section after `## Tests re-run (output)`, plus the I3 TOTAL-line sentence.
- work/067/05-build-report.md: this file.

File counts (commands, run in the shared tree; 068's uncommitted edits are in it):
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
2
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
7
$ git status --porcelain -uall -- . ':!work' ':!logs'
 M .claude/agents/i2-builder.md
 M .claude/agents/i3-verifier.md
 M .claude/commands/run-item.md
 M ccbot/realtest.py
 M templates/build-report.md
 M templates/verification.md
 M tests/test_realtest.py
?? scripts/diff_reports.py
?? tests/test_diff_reports.py
$ git status --porcelain -uall -- scripts/diff_reports.py tests/test_diff_reports.py templates/ | grep -c '^??'
2
$ git status --porcelain -uall -- scripts/diff_reports.py tests/test_diff_reports.py templates/ | grep -c '^ M'
2
```
067's own: 2 new + 2 changed = 4 files (plus this 05). The other 5 modified files (.claude/*, ccbot/realtest.py, tests/test_realtest.py) are item 068's, built in parallel; 067 did not touch them and does not commit them.

## Connectivity check
- [x] every new function/rule is used: `load_json`, `diff_json`, `read_csv`, `key_for`, `diff_csv`, `_check_dir` are called from `diff_dirs`; `diff_dirs` from `main` and from `test_diff_dirs_importable`; `main` from `__main__`. `KEYS`/`TRADES_KEY` read by `key_for`. The template field is the consumer of the script output (this 05 uses it).
- [x] every input has a source, every output has a consumer: inputs = two report dirs (realtest `--out`); output = stdout block + exit code, pasted in 05/06 under the new field; errors on stderr with exit 2.
- [x] every branch ends in a defined result: missing/non-dir → `MISSING DIR` exit 2; no .json/.csv → `EMPTY DIR` exit 2; one-side file → `ONLY IN ...` exit 1; other file/subdir → `NOT COMPARED` (counted); bad JSON → exit 2; ragged row / row after empty header → `BAD ROW` exit 2; bad encoding/csv error → `BAD CSV` exit 2; duplicate header → exit 2; duplicate key → exit 2; key column missing / empty header / unknown name → `MATCH <f>: index (<why>)`; `--max-rows` < 0 → `BAD ARG` exit 2; no change → `no change` exit 0.
- [x] no leftover TODOs or unused files: `grep -n TODO scripts/diff_reports.py tests/test_diff_reports.py` → no hit. Scratch files (mutation worktree, diff output) are under the scratchpad only.

Missing-data grep (`grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/`): 37 hits in the shared tree, 37 in a clean HEAD worktree (`wt-067-mut` before my copy). 067 changes nothing in ccbot/, so no new or changed hit is 067's. Same grep on 067's files: one hit, `scripts/diff_reports.py:319: return 1 if _has_change(totals) else 0` - this is the exit code (1 changes / 0 none) computed from integer counts, not a default for absent data.
014 patterns: no dataclass in 067's files (`grep -nE ":\s*(float|int)\s*=\s*[0-9]" scripts/diff_reports.py` → no hit). Every `>`/`<` in scripts/diff_reports.py (L122, 149, 210, 237, 310) compares `len()` or int counts / argparse ints, never a value that can be NaN. JSON NaN leaves are handled only by `_is_nan` (equal iff both NaN); CSV cells are compared as strings.

Measured (04 Extra research, pandas empty-frame text):
```
$ python3 -c "import pandas as pd; print(repr(pd.DataFrame([]).to_csv(index=False)))"
'\n'
```
Test (l) covers a 0-byte file (trades_ZZZ.csv) and `'\n'` (trades_YYY.csv).

## Test output (pasted, not summarized)
```
$ python3 -m pytest tests/test_diff_reports.py -v
tests/test_diff_reports.py::test_a_nested_key_and_list_in_dict PASSED
tests/test_diff_reports.py::test_b_identical_with_nan_and_empty_cells PASSED
tests/test_diff_reports.py::test_c_type_changes PASSED
tests/test_diff_reports.py::test_d_file_only_in_after PASSED
tests/test_diff_reports.py::test_e_added_ticker_matched_by_key PASSED
tests/test_diff_reports.py::test_f_row_cap PASSED
tests/test_diff_reports.py::test_g_duplicate_key_exits_2 PASSED
tests/test_diff_reports.py::test_h_column_added PASSED
tests/test_diff_reports.py::test_i_missing_and_empty_dir PASSED
tests/test_diff_reports.py::test_j_list_length PASSED
tests/test_diff_reports.py::test_k_no_tolerance_on_csv_cells PASSED
tests/test_diff_reports.py::test_l_zero_trade_files PASSED
tests/test_diff_reports.py::test_m_bad_json PASSED
tests/test_diff_reports.py::test_n_key_column_one_side PASSED
tests/test_diff_reports.py::test_o_ragged_row PASSED
tests/test_diff_reports.py::test_committed_reports_self_diff PASSED
tests/test_diff_reports.py::test_diff_dirs_importable PASSED
17 passed in 0.71s
```
Full suite. Base = clean worktree at HEAD a6d6b39 (`scratchpad/wt-067-mut`), then the same worktree with only 067's 4 files copied in, then the shared repo tree (which also holds 068's uncommitted edits):
```
(wt-067-mut, HEAD a6d6b39, no 067 files)   $ python3 -m pytest -q   -> 324 passed, 1 skipped in 69.71s (0:01:09)
(wt-067-mut + 067's 4 files)              $ python3 -m pytest -q   -> 341 passed, 1 skipped in 61.18s (0:01:01)
(repo tree, 067 + 068 in progress)        $ python3 -m pytest -q   -> 342 passed, 1 skipped in 64.30s (0:01:04)
```
341 = 324 + 17 (067). The +1 in the repo tree is 068's test edit, not 067's.
```
$ python3 -m pytest -q tests/test_safety.py -k oldest
1 passed, 8 deselected in 0.10s
$ python3.11 -c "<compile each file>" scripts/diff_reports.py tests/test_diff_reports.py
ok scripts/diff_reports.py
ok tests/test_diff_reports.py
$ grep -nE "QUOTE_(STRINGS|NOTNULL)" scripts/diff_reports.py ; echo grep-exit $?
grep-exit 1
$ grep -n "Real-data effect (diff_reports output, pasted)" templates/build-report.md templates/verification.md
templates/build-report.md:9:## Real-data effect (diff_reports output, pasted)
templates/verification.md:7:## Real-data effect (diff_reports output, pasted)
```
(The compile test compiles tracked files only and no python3.10 is on PATH, so it used python3.11; the two new files are untracked until commit, hence the direct python3.11 compile above.)

Self-diff of the committed reports/real (feasibility: key uniqueness, 04 Guardrail tests):
```
$ python3 scripts/diff_reports.py reports/real reports/real ; echo "exit $?"
CSV bot_rule_by_ticker.csv: match key, rows 54 -> 54, matched 54, added 0, removed 0, changed 0; by column: none
CSV grid_in_sample.csv: match key, rows 1020 -> 1020, matched 1020, added 0, removed 0, changed 0; by column: none
JSON summary.json: NaN tokens: before 0, after 0; changes 0
CSV trades_AAL.csv: match key, rows 4 -> 4, matched 4, added 0, removed 0, changed 0; by column: none
CSV trades_BAC.csv: match key, rows 24 -> 24, matched 24, added 0, removed 0, changed 0; by column: none
CSV trades_BMY.csv: match key, rows 13 -> 13, matched 13, added 0, removed 0, changed 0; by column: none
CSV trades_CMCSA.csv: match key, rows 12 -> 12, matched 12, added 0, removed 0, changed 0; by column: none
CSV trades_CSX.csv: match key, rows 37 -> 37, matched 37, added 0, removed 0, changed 0; by column: none
CSV trades_F.csv: match key, rows 11 -> 11, matched 11, added 0, removed 0, changed 0; by column: none
CSV trades_HBAN.csv: match key, rows 15 -> 15, matched 15, added 0, removed 0, changed 0; by column: none
CSV trades_KEY.csv: match key, rows 13 -> 13, matched 13, added 0, removed 0, changed 0; by column: none
CSV trades_KMI.csv: match key, rows 16 -> 16, matched 16, added 0, removed 0, changed 0; by column: none
CSV trades_MDLZ.csv: match key, rows 34 -> 34, matched 34, added 0, removed 0, changed 0; by column: none
CSV trades_MO.csv: match key, rows 23 -> 23, matched 23, added 0, removed 0, changed 0; by column: none
CSV trades_OXY.csv: match key, rows 8 -> 8, matched 8, added 0, removed 0, changed 0; by column: none
CSV trades_PFE.csv: match key, rows 12 -> 12, matched 12, added 0, removed 0, changed 0; by column: none
CSV trades_PYPL.csv: match key, rows 13 -> 13, matched 13, added 0, removed 0, changed 0; by column: none
CSV trades_T.csv: match key, rows 1 -> 1, matched 1, added 0, removed 0, changed 0; by column: none
CSV trades_USB.csv: match key, rows 11 -> 11, matched 11, added 0, removed 0, changed 0; by column: none
CSV trades_VZ.csv: match key, rows 3 -> 3, matched 3, added 0, removed 0, changed 0; by column: none
CSV walkforward_by_ticker.csv: match key, rows 17 -> 17, matched 17, added 0, removed 0, changed 0; by column: none
CSV walkforward_picks.csv: match key, rows 10 -> 10, matched 10, added 0, removed 0, changed 0; by column: none
TOTAL: files 22, only-before 0, only-after 0, not compared 0, json changes 0, csv rows changed 0 added 0 removed 0, columns changed 0
no change
exit 0
```
Feasibility numbers: picks 10/10, by_ticker 17/17, bot_rule (ticker, config) 54/54, grid 1,020/1,020 all key-matched with no DUPLICATE KEY; trades open_date sum 4+24+13+12+37+11+15+13+16+34+23+8+12+13+1+11+3 = 250 (from the lines above), as R3 counted.

Mutations (I2 pre-check; scratch worktree `/tmp/claude-0/-home-claude/3184256a-8786-5c3c-8e7d-428ba8311b8c/scratchpad/wt-067-mut` at HEAD with 067's files copied in; script `/tmp/claude-0/-home-claude/3184256a-8786-5c3c-8e7d-428ba8311b8c/scratchpad/mut067.py`; original restored after each, final run 17 passed). The repo tree was not edited:
```
mutation 1 recursion cut to top level: 5 failed, 12 passed in 0.76s; target test_a_nested_key_and_list_in_dict failed: True
    FAILED tests/test_diff_reports.py::test_a_nested_key_and_list_in_dict
    FAILED tests/test_diff_reports.py::test_b_identical_with_nan_and_empty_cells
    FAILED tests/test_diff_reports.py::test_c_type_changes
    FAILED tests/test_diff_reports.py::test_j_list_length
    FAILED tests/test_diff_reports.py::test_diff_dirs_importable
mutation 2 key -> index for walkforward_by_ticker: 4 failed, 13 passed in 0.75s; target test_e_added_ticker_matched_by_key failed: True
    FAILED tests/test_diff_reports.py::test_e_added_ticker_matched_by_key
    FAILED tests/test_diff_reports.py::test_k_no_tolerance_on_csv_cells
    FAILED tests/test_diff_reports.py::test_n_key_column_one_side
    FAILED tests/test_diff_reports.py::test_committed_reports_self_diff
mutation 3 both-NaN check removed: 1 failed, 16 passed in 1.33s; target test_b_identical_with_nan_and_empty_cells failed: True
    FAILED tests/test_diff_reports.py::test_b_identical_with_nan_and_empty_cells
mutation 4 EMPTY DIR check removed: 1 failed, 16 passed in 0.71s; target test_i_missing_and_empty_dir failed: True
    FAILED tests/test_diff_reports.py::test_i_missing_and_empty_dir
mutation 5 type(a) is type(b) removed: 1 failed, 16 passed in 0.71s; target test_c_type_changes failed: True
    FAILED tests/test_diff_reports.py::test_c_type_changes
```
Mutation 1 = the RI-013 GUARDED probe ("fails with nested keys skipped"): it fails.

## Real-data effect (diff_reports output, pasted)
065's full effect (base `e129253^` vs head c659560). Runs made by the orchestrator, not re-run by I2 (04 Step 4).

Commands (from the orchestrator), scratchpad = `/tmp/claude-0/-home-claude/3184256a-8786-5c3c-8e7d-428ba8311b8c/scratchpad`:
```
before: cd scratchpad/wt-before && python3 -m ccbot.realtest --data /home/claude/cover-calls/data/real --out scratchpad/065-before
after:  cd scratchpad/wt-after  && python3 -m ccbot.realtest --data /home/claude/cover-calls/data/real --out scratchpad/065-after
```
Both runs read the same absolute `--data` dir (the repo's tracked data/real).

SHAs and diffs:
```
$ git rev-parse 'e129253^'
5883ba4fa70262646689ce74687f23e99d0f92eb
$ git -C scratchpad/wt-before rev-parse HEAD
5883ba4fa70262646689ce74687f23e99d0f92eb
$ git -C scratchpad/wt-after rev-parse HEAD
c6595609dd0f02f976ef824ba3ec83aa6accffe3
$ git rev-parse c659560
c6595609dd0f02f976ef824ba3ec83aa6accffe3
$ git diff --stat e129253 c659560 -- ccbot config
(empty)
$ git diff --stat 'e129253^' c659560 -- data/real
(empty)
$ git status --short data/real
(empty)
```
Data identity (`find . -type f | sort | xargs sha256sum | sha256sum`, run inside each dir):
```
/home/claude/cover-calls/data/real (the --data used by both runs): fa29a0e8ca1d448c424c6dc4041d98f7fae44e003b4e8517ee9c98ae337798ba  - files=135
scratchpad/wt-before/data/real (not read, for reference):         fa29a0e8ca1d448c424c6dc4041d98f7fae44e003b4e8517ee9c98ae337798ba  - files=135
scratchpad/wt-after/data/real (not read, for reference):          fa29a0e8ca1d448c424c6dc4041d98f7fae44e003b4e8517ee9c98ae337798ba  - files=135
$ find /home/claude/cover-calls/data/real -type f -newer scratchpad/065-before/trades_AAL.csv | wc -l
0
$ find /home/claude/cover-calls/data/real -type f -newer scratchpad/065-after/trades_AAL.csv | wc -l
0
```
Both output dirs have 22 files (`ls | wc -l` → 22, 22); summary.json written 23:41:51 (before) and 23:41:33 (after) UTC.
Interpreter (`/usr/local/bin/python3`, the `python3` both commands used):
```
$ python3 -c "import sys, pandas; print(sys.version, pandas.__version__)"
3.13.18 (main, Oct 26 2026, 14:08:19) [Clang 23.1.3 ] 3.0.5
```
Diff (whole output, exit 1):
```
$ python3 scripts/diff_reports.py scratchpad/065-before scratchpad/065-after ; echo "exit $?"
COLUMNS bot_rule_by_ticker.csv: added ['earnings_gap_days'] removed []
CSV bot_rule_by_ticker.csv: match key, rows 54 -> 54, matched 54, added 0, removed 0, changed 15; by column: cc_cagr=6, excess_cagr=6, calls_sold=6, called_away_pct=6, premium_yield_per_yr=6, option_pnl_per_share=6, option_win_rate=6, sold_iv=6, realized=6, iv_minus_rv=6, pct_iv_above_rv=6, rej_OK=6, rej_NO_EXPIRY=15, rej_EARNINGS_UNKNOWN=15, rej_EARNINGS_BLACKOUT=6, rej_NO_STRIKE_IN_TOLERANCE=15, rej_BASIS_ABOVE_BAND=15, in_window=6, slack=6, warnings=15
  (CMCSA, d0.275_dte30-45_noE_hold_bid): rej_NO_EXPIRY: '452' -> '418'; rej_EARNINGS_UNKNOWN: '21' -> '93'; rej_NO_STRIKE_IN_TOLERANCE: '110' -> '107'; rej_BASIS_ABOVE_BAND: '445' -> '410'; warnings: 'earnings: 1 gap(s) > 120 days between dates; options: 17 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-23 is 17 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN)' -> 'earnings: 1 gap(s) > 120 days between dates; options: 17 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-23 is 17 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN); earnings: gap(s) > 120 days between listed dates (2021-10-28→2022-04-28); no call sold inside them (EARNINGS_UNKNOWN)'
  (CMCSA, d0.275_dte30-45_noE_hold_quarter): rej_NO_EXPIRY: '452' -> '418'; rej_EARNINGS_UNKNOWN: '21' -> '93'; rej_NO_STRIKE_IN_TOLERANCE: '110' -> '107'; rej_BASIS_ABOVE_BAND: '445' -> '410'; warnings: 'earnings: 1 gap(s) > 120 days between dates; options: 17 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-23 is 17 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN)' -> 'earnings: 1 gap(s) > 120 days between dates; options: 17 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-23 is 17 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN); earnings: gap(s) > 120 days between listed dates (2021-10-28→2022-04-28); no call sold inside them (EARNINGS_UNKNOWN)'
  (CMCSA, d0.275_dte30-45_noE_hold_mid): rej_NO_EXPIRY: '452' -> '418'; rej_EARNINGS_UNKNOWN: '21' -> '93'; rej_NO_STRIKE_IN_TOLERANCE: '110' -> '107'; rej_BASIS_ABOVE_BAND: '445' -> '410'; warnings: 'earnings: 1 gap(s) > 120 days between dates; options: 17 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-23 is 17 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN)' -> 'earnings: 1 gap(s) > 120 days between dates; options: 17 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-23 is 17 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN); earnings: gap(s) > 120 days between listed dates (2021-10-28→2022-04-28); no call sold inside them (EARNINGS_UNKNOWN)'
  (MDLZ, d0.275_dte30-45_noE_hold_bid): cc_cagr: '0.07202865980914996' -> '0.07244935652478324'; excess_cagr: '0.014898850209082992' -> '0.015319546924716265'; calls_sold: '34' -> '31'; called_away_pct: '0.14705882352941177' -> '0.16129032258064516'; premium_yield_per_yr: '0.028820518165333552' -> '0.026692072489765715'; option_pnl_per_share: '5.940000000000009' -> '6.090000000000012'; option_win_rate: '0.8529411764705882' -> '0.8387096774193549'; sold_iv: '0.21869117647058825' -> '0.22428387096774194'; realized: '0.18070460419304357' -> '0.18285156304574118'; iv_minus_rv: '0.03798657227754468' -> '0.04143230792200076'; pct_iv_above_rv: '0.6176470588235294' -> '0.6451612903225806'; rej_OK: '34' -> '31'; rej_NO_EXPIRY: '255' -> '239'; rej_EARNINGS_UNKNOWN: '18' -> '87'; rej_EARNINGS_BLACKOUT: '32' -> '45'; rej_NO_STRIKE_IN_TOLERANCE: '37' -> '36'; rej_BASIS_ABOVE_BAND: '286' -> '259'; in_window: '13' -> '11'; slack: '21' -> '20'; warnings: 'earnings: 1 gap(s) > 120 days between dates; earnings: first listed date 2020-01-29 is 23 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN)' -> 'earnings: 1 gap(s) > 120 days between dates; earnings: first listed date 2020-01-29 is 23 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN); earnings: gap(s) > 120 days between listed dates (2021-11-02→2022-04-26); no call sold inside them (EARNINGS_UNKNOWN)'
  (MDLZ, d0.275_dte30-45_noE_hold_quarter): cc_cagr: '0.07702067829035619' -> '0.07722148436840226'; excess_cagr: '0.01989086869028922' -> '0.020091674768335288'; calls_sold: '34' -> '31'; called_away_pct: '0.14705882352941177' -> '0.16129032258064516'; premium_yield_per_yr: '0.03348617092836278' -> '0.03115047759485197'; option_pnl_per_share: '8.055000000000009' -> '8.105000000000013'; option_win_rate: '0.8529411764705882' -> '0.8387096774193549'; sold_iv: '0.21869117647058825' -> '0.22428387096774194'; realized: '0.18070460419304357' -> '0.18285156304574118'; iv_minus_rv: '0.03798657227754468' -> '0.04143230792200076'; pct_iv_above_rv: '0.6176470588235294' -> '0.6451612903225806'; rej_OK: '34' -> '31'; rej_NO_EXPIRY: '255' -> '239'; rej_EARNINGS_UNKNOWN: '18' -> '87'; rej_EARNINGS_BLACKOUT: '32' -> '45'; rej_NO_STRIKE_IN_TOLERANCE: '37' -> '36'; rej_BASIS_ABOVE_BAND: '286' -> '259'; in_window: '13' -> '11'; slack: '21' -> '20'; warnings: 'earnings: 1 gap(s) > 120 days between dates; earnings: first listed date 2020-01-29 is 23 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN)' -> 'earnings: 1 gap(s) > 120 days between dates; earnings: first listed date 2020-01-29 is 23 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN); earnings: gap(s) > 120 days between listed dates (2021-11-02→2022-04-26); no call sold inside them (EARNINGS_UNKNOWN)'
  (MDLZ, d0.275_dte30-45_noE_hold_mid): cc_cagr: '0.08201459063951222' -> '0.08199358894281428'; excess_cagr: '0.024884781039445247' -> '0.024863779342747305'; calls_sold: '34' -> '31'; called_away_pct: '0.14705882352941177' -> '0.16129032258064516'; premium_yield_per_yr: '0.038151823691391994' -> '0.03560888269993823'; option_pnl_per_share: '10.170000000000009' -> '10.120000000000013'; option_win_rate: '0.8529411764705882' -> '0.8387096774193549'; sold_iv: '0.21869117647058825' -> '0.22428387096774194'; realized: '0.18070460419304357' -> '0.18285156304574118'; iv_minus_rv: '0.03798657227754468' -> '0.04143230792200076'; pct_iv_above_rv: '0.6176470588235294' -> '0.6451612903225806'; rej_OK: '34' -> '31'; rej_NO_EXPIRY: '255' -> '239'; rej_EARNINGS_UNKNOWN: '18' -> '87'; rej_EARNINGS_BLACKOUT: '32' -> '45'; rej_NO_STRIKE_IN_TOLERANCE: '37' -> '36'; rej_BASIS_ABOVE_BAND: '286' -> '259'; in_window: '13' -> '11'; slack: '21' -> '20'; warnings: 'earnings: 1 gap(s) > 120 days between dates; earnings: first listed date 2020-01-29 is 23 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN)' -> 'earnings: 1 gap(s) > 120 days between dates; earnings: first listed date 2020-01-29 is 23 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN); earnings: gap(s) > 120 days between listed dates (2021-11-02→2022-04-26); no call sold inside them (EARNINGS_UNKNOWN)'
  (MO, d0.275_dte30-45_noE_hold_bid): cc_cagr: '0.15231626090720973' -> '0.14937009930748557'; excess_cagr: '0.003309217654912322' -> '0.0003630560551881601'; calls_sold: '23' -> '21'; called_away_pct: '0.17391304347826086' -> '0.19047619047619047'; premium_yield_per_yr: '0.022065434375594675' -> '0.01948837049884447'; option_pnl_per_share: '2.450000000000001' -> '1.5500000000000012'; option_win_rate: '0.8695652173913043' -> '0.8571428571428571'; sold_iv: '0.2693782608695653' -> '0.2733619047619048'; realized: '0.21038391287063452' -> '0.21263404823691107'; iv_minus_rv: '0.05899434799893072' -> '0.06072785652499368'; pct_iv_above_rv: '0.5652173913043478' -> '0.5714285714285714'; rej_OK: '23' -> '21'; rej_NO_EXPIRY: '311' -> '293'; rej_EARNINGS_UNKNOWN: '19' -> '90'; rej_EARNINGS_BLACKOUT: '68' -> '64'; rej_NO_STRIKE_IN_TOLERANCE: '96' -> '90'; rej_BASIS_ABOVE_BAND: '225' -> '217'; in_window: '5' -> '4'; slack: '18' -> '17'; warnings: 'earnings: 1 gap(s) > 120 days between dates; options: 4 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-30 is 24 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN)' -> 'earnings: 1 gap(s) > 120 days between dates; options: 4 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-30 is 24 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN); earnings: gap(s) > 120 days between listed dates (2021-10-28→2022-04-28); no call sold inside them (EARNINGS_UNKNOWN)'
  (MO, d0.275_dte30-45_noE_hold_quarter): cc_cagr: '0.1547931689840405' -> '0.15176730169493635'; excess_cagr: '0.005786125731743086' -> '0.002760258442638941'; calls_sold: '23' -> '21'; called_away_pct: '0.17391304347826086' -> '0.19047619047619047'; premium_yield_per_yr: '0.024218610726946102' -> '0.02157727677352933'; option_pnl_per_share: '3.215000000000001' -> '2.2925000000000013'; option_win_rate: '0.8695652173913043' -> '0.8571428571428571'; sold_iv: '0.2693782608695653' -> '0.2733619047619048'; realized: '0.21038391287063452' -> '0.21263404823691107'; iv_minus_rv: '0.05899434799893072' -> '0.06072785652499368'; pct_iv_above_rv: '0.5652173913043478' -> '0.5714285714285714'; rej_OK: '23' -> '21'; rej_NO_EXPIRY: '311' -> '293'; rej_EARNINGS_UNKNOWN: '19' -> '90'; rej_EARNINGS_BLACKOUT: '68' -> '64'; rej_NO_STRIKE_IN_TOLERANCE: '96' -> '90'; rej_BASIS_ABOVE_BAND: '225' -> '217'; in_window: '5' -> '4'; slack: '18' -> '17'; warnings: 'earnings: 1 gap(s) > 120 days between dates; options: 4 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-30 is 24 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN)' -> 'earnings: 1 gap(s) > 120 days between dates; options: 4 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-30 is 24 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN); earnings: gap(s) > 120 days between listed dates (2021-10-28→2022-04-28); no call sold inside them (EARNINGS_UNKNOWN)'
  (MO, d0.275_dte30-45_noE_hold_mid): cc_cagr: '0.15727000032223093' -> '0.154164133657555'; excess_cagr: '0.008262957069933519' -> '0.0051570904052575806'; calls_sold: '23' -> '21'; called_away_pct: '0.17391304347826086' -> '0.19047619047619047'; premium_yield_per_yr: '0.026371787078297543' -> '0.023666183048214186'; option_pnl_per_share: '3.980000000000001' -> '3.035000000000001'; option_win_rate: '0.8695652173913043' -> '0.8571428571428571'; sold_iv: '0.2693782608695653' -> '0.2733619047619048'; realized: '0.21038391287063452' -> '0.21263404823691107'; iv_minus_rv: '0.05899434799893072' -> '0.06072785652499368'; pct_iv_above_rv: '0.5652173913043478' -> '0.5714285714285714'; rej_OK: '23' -> '21'; rej_NO_EXPIRY: '311' -> '293'; rej_EARNINGS_UNKNOWN: '19' -> '90'; rej_EARNINGS_BLACKOUT: '68' -> '64'; rej_NO_STRIKE_IN_TOLERANCE: '96' -> '90'; rej_BASIS_ABOVE_BAND: '225' -> '217'; in_window: '5' -> '4'; slack: '18' -> '17'; warnings: 'earnings: 1 gap(s) > 120 days between dates; options: 4 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-30 is 24 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN)' -> 'earnings: 1 gap(s) > 120 days between dates; options: 4 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-30 is 24 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN); earnings: gap(s) > 120 days between listed dates (2021-10-28→2022-04-28); no call sold inside them (EARNINGS_UNKNOWN)'
  (T, d0.275_dte30-45_noE_hold_bid): rej_NO_EXPIRY: '523' -> '491'; rej_EARNINGS_UNKNOWN: '24' -> '95'; rej_NO_STRIKE_IN_TOLERANCE: '84' -> '81'; rej_BASIS_ABOVE_BAND: '567' -> '531'; warnings: 'earnings: 1 gap(s) > 120 days between dates; options: 13 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-29 is 23 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN)' -> 'earnings: 1 gap(s) > 120 days between dates; options: 13 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-29 is 23 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN); earnings: gap(s) > 120 days between listed dates (2021-10-21→2022-04-21); no call sold inside them (EARNINGS_UNKNOWN)'
  (T, d0.275_dte30-45_noE_hold_quarter): rej_NO_EXPIRY: '523' -> '491'; rej_EARNINGS_UNKNOWN: '24' -> '95'; rej_NO_STRIKE_IN_TOLERANCE: '84' -> '81'; rej_BASIS_ABOVE_BAND: '567' -> '531'; warnings: 'earnings: 1 gap(s) > 120 days between dates; options: 13 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-29 is 23 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN)' -> 'earnings: 1 gap(s) > 120 days between dates; options: 13 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-29 is 23 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN); earnings: gap(s) > 120 days between listed dates (2021-10-21→2022-04-21); no call sold inside them (EARNINGS_UNKNOWN)'
  (T, d0.275_dte30-45_noE_hold_mid): rej_NO_EXPIRY: '523' -> '491'; rej_EARNINGS_UNKNOWN: '24' -> '95'; rej_NO_STRIKE_IN_TOLERANCE: '84' -> '81'; rej_BASIS_ABOVE_BAND: '567' -> '531'; warnings: 'earnings: 1 gap(s) > 120 days between dates; options: 13 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-29 is 23 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN)' -> 'earnings: 1 gap(s) > 120 days between dates; options: 13 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-29 is 23 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN); earnings: gap(s) > 120 days between listed dates (2021-10-21→2022-04-21); no call sold inside them (EARNINGS_UNKNOWN)'
  (VZ, d0.275_dte30-45_noE_hold_bid): rej_NO_EXPIRY: '509' -> '475'; rej_EARNINGS_UNKNOWN: '22' -> '94'; rej_NO_STRIKE_IN_TOLERANCE: '88' -> '74'; rej_BASIS_ABOVE_BAND: '549' -> '525'; warnings: 'earnings: 1 gap(s) > 120 days between dates; options: 7 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-30 is 24 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN)' -> 'earnings: 1 gap(s) > 120 days between dates; options: 7 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-30 is 24 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN); earnings: gap(s) > 120 days between listed dates (2021-10-20→2022-04-22); no call sold inside them (EARNINGS_UNKNOWN)'
  (VZ, d0.275_dte30-45_noE_hold_quarter): rej_NO_EXPIRY: '509' -> '475'; rej_EARNINGS_UNKNOWN: '22' -> '94'; rej_NO_STRIKE_IN_TOLERANCE: '88' -> '74'; rej_BASIS_ABOVE_BAND: '549' -> '525'; warnings: 'earnings: 1 gap(s) > 120 days between dates; options: 7 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-30 is 24 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN)' -> 'earnings: 1 gap(s) > 120 days between dates; options: 7 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-30 is 24 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN); earnings: gap(s) > 120 days between listed dates (2021-10-20→2022-04-22); no call sold inside them (EARNINGS_UNKNOWN)'
  (VZ, d0.275_dte30-45_noE_hold_mid): rej_NO_EXPIRY: '509' -> '475'; rej_EARNINGS_UNKNOWN: '22' -> '94'; rej_NO_STRIKE_IN_TOLERANCE: '88' -> '74'; rej_BASIS_ABOVE_BAND: '549' -> '525'; warnings: 'earnings: 1 gap(s) > 120 days between dates; options: 7 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-30 is 24 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN)' -> 'earnings: 1 gap(s) > 120 days between dates; options: 7 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-30 is 24 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN); earnings: gap(s) > 120 days between listed dates (2021-10-20→2022-04-22); no call sold inside them (EARNINGS_UNKNOWN)'
COLUMNS grid_in_sample.csv: added ['earnings_gap_days'] removed []
CSV grid_in_sample.csv: match key, rows 1020 -> 1020, matched 1020, added 0, removed 0, changed 150; by column: cc_cagr=69, excess_cagr=69, cc_maxdd=15, called_away_pct=62, calls_sold=61, rej_OK=61, rej_NO_EXPIRY=90, rej_EARNINGS_UNKNOWN=150, rej_EARNINGS_BLACKOUT=56, rej_NO_STRIKE_IN_TOLERANCE=124, rej_BASIS_ABOVE_BAND=149, in_window=47, slack=60, sub_3c_sales=11
  (CMCSA, d0.150_dte14-24_noE_hold_bid): cc_cagr: '-0.052791829804666124' -> '-0.05340310181539476'; excess_cagr: '0.00147453873033343' -> '0.0008632667196047938'; cc_maxdd: '-0.5957723729879074' -> '-0.5975559523218654'; called_away_pct: '0.0967741935483871' -> '0.10344827586206896'; calls_sold: '31' -> '29'; rej_OK: '31' -> '29'; rej_EARNINGS_UNKNOWN: '21' -> '93'; rej_BASIS_ABOVE_BAND: '930' -> '880'; slack: '7' -> '5'
  (MDLZ, d0.150_dte14-24_noE_hold_bid): cc_cagr: '0.06510345171260945' -> '0.06598054394595732'; excess_cagr: '0.007973642112542478' -> '0.008850734345890343'; called_away_pct: '0.09433962264150944' -> '0.09090909090909091'; calls_sold: '53' -> '55'; rej_OK: '53' -> '55'; rej_EARNINGS_UNKNOWN: '18' -> '87'; rej_EARNINGS_BLACKOUT: '54' -> '56'; rej_NO_STRIKE_IN_TOLERANCE: '150' -> '143'; rej_BASIS_ABOVE_BAND: '574' -> '523'; in_window: '30' -> '37'; slack: '23' -> '18'
  (MO, d0.150_dte14-24_noE_hold_bid): cc_cagr: '0.14860685839267274' -> '0.1460217292304704'; excess_cagr: '-0.00040018485962467487' -> '-0.0029853140218270013'; called_away_pct: '0.08333333333333333' -> '0.09230769230769231'; calls_sold: '72' -> '65'; rej_OK: '72' -> '65'; rej_EARNINGS_UNKNOWN: '19' -> '90'; rej_EARNINGS_BLACKOUT: '64' -> '61'; rej_NO_STRIKE_IN_TOLERANCE: '23' -> '22'; rej_BASIS_ABOVE_BAND: '464' -> '444'; in_window: '61' -> '56'; slack: '11' -> '9'; sub_3c_sales: '22' -> '21'
  (T, d0.150_dte14-24_noE_hold_bid): rej_NO_EXPIRY: '1' -> '0'; rej_EARNINGS_UNKNOWN: '24' -> '95'; rej_BASIS_ABOVE_BAND: '1139' -> '1069'
  (VZ, d0.150_dte14-24_noE_hold_bid): rej_EARNINGS_UNKNOWN: '22' -> '94'; rej_NO_STRIKE_IN_TOLERANCE: '25' -> '24'; rej_BASIS_ABOVE_BAND: '1011' -> '940'
  (CMCSA, d0.150_dte14-24_noE_take50_bid): cc_cagr: '-0.05245748735274902' -> '-0.05306897512827913'; excess_cagr: '0.0018088811822505324' -> '0.0011973934067204262'; cc_maxdd: '-0.5957723729879075' -> '-0.5975559523218659'; called_away_pct: '0.09375' -> '0.1'; calls_sold: '32' -> '30'; rej_OK: '32' -> '30'; rej_EARNINGS_UNKNOWN: '21' -> '93'; rej_BASIS_ABOVE_BAND: '926' -> '876'; slack: '8' -> '6'
  (MDLZ, d0.150_dte14-24_noE_take50_bid): cc_cagr: '0.06510345171260945' -> '0.06598054394595732'; excess_cagr: '0.007973642112542478' -> '0.008850734345890343'; called_away_pct: '0.09433962264150944' -> '0.09090909090909091'; calls_sold: '53' -> '55'; rej_OK: '53' -> '55'; rej_EARNINGS_UNKNOWN: '18' -> '87'; rej_EARNINGS_BLACKOUT: '54' -> '56'; rej_NO_STRIKE_IN_TOLERANCE: '150' -> '143'; rej_BASIS_ABOVE_BAND: '574' -> '523'; in_window: '30' -> '37'; slack: '23' -> '18'
  (MO, d0.150_dte14-24_noE_take50_bid): cc_cagr: '0.15035167245215808' -> '0.14626122026372146'; excess_cagr: '0.0013446291998606696' -> '-0.002745822988575952'; called_away_pct: '0.07462686567164178' -> '0.09090909090909091'; calls_sold: '67' -> '66'; rej_OK: '67' -> '66'; rej_EARNINGS_UNKNOWN: '19' -> '90'; rej_EARNINGS_BLACKOUT: '62' -> '61'; rej_NO_STRIKE_IN_TOLERANCE: '24' -> '22'; rej_BASIS_ABOVE_BAND: '495' -> '439'; in_window: '54' -> '56'; slack: '13' -> '10'; sub_3c_sales: '20' -> '21'
  (T, d0.150_dte14-24_noE_take50_bid): rej_NO_EXPIRY: '1' -> '0'; rej_EARNINGS_UNKNOWN: '24' -> '95'; rej_BASIS_ABOVE_BAND: '1139' -> '1069'
  (VZ, d0.150_dte14-24_noE_take50_bid): rej_EARNINGS_UNKNOWN: '22' -> '94'; rej_NO_STRIKE_IN_TOLERANCE: '23' -> '22'; rej_BASIS_ABOVE_BAND: '1013' -> '942'
  (CMCSA, d0.150_dte14-24_noE_roll_bid): cc_cagr: '-0.052791829804666124' -> '-0.05340310181539476'; excess_cagr: '0.00147453873033343' -> '0.0008632667196047938'; cc_maxdd: '-0.5957723729879074' -> '-0.5975559523218654'; called_away_pct: '0.0967741935483871' -> '0.10344827586206896'; calls_sold: '31' -> '29'; rej_OK: '31' -> '29'; rej_EARNINGS_UNKNOWN: '21' -> '93'; rej_BASIS_ABOVE_BAND: '930' -> '880'; slack: '7' -> '5'
  (MDLZ, d0.150_dte14-24_noE_roll_bid): cc_cagr: '0.06510345171260945' -> '0.06598054394595732'; excess_cagr: '0.007973642112542478' -> '0.008850734345890343'; called_away_pct: '0.09433962264150944' -> '0.09090909090909091'; calls_sold: '53' -> '55'; rej_OK: '53' -> '55'; rej_EARNINGS_UNKNOWN: '18' -> '87'; rej_EARNINGS_BLACKOUT: '54' -> '56'; rej_NO_STRIKE_IN_TOLERANCE: '150' -> '143'; rej_BASIS_ABOVE_BAND: '574' -> '523'; in_window: '30' -> '37'; slack: '23' -> '18'
  (MO, d0.150_dte14-24_noE_roll_bid): cc_cagr: '0.14993973547116646' -> '0.1471437738391601'; excess_cagr: '0.0009326922188690467' -> '-0.0018632694131373029'; called_away_pct: '0.0641025641025641' -> '0.07042253521126761'; calls_sold: '78' -> '71'; rej_OK: '78' -> '71'; rej_EARNINGS_UNKNOWN: '19' -> '90'; rej_EARNINGS_BLACKOUT: '74' -> '71'; rej_NO_STRIKE_IN_TOLERANCE: '23' -> '22'; rej_BASIS_ABOVE_BAND: '416' -> '396'; in_window: '66' -> '61'; slack: '12' -> '10'; sub_3c_sales: '21' -> '20'
  (T, d0.150_dte14-24_noE_roll_bid): rej_NO_EXPIRY: '1' -> '0'; rej_EARNINGS_UNKNOWN: '24' -> '95'; rej_BASIS_ABOVE_BAND: '1139' -> '1069'
  (VZ, d0.150_dte14-24_noE_roll_bid): rej_EARNINGS_UNKNOWN: '22' -> '94'; rej_NO_STRIKE_IN_TOLERANCE: '25' -> '24'; rej_BASIS_ABOVE_BAND: '1011' -> '940'
  (CMCSA, d0.150_dte30-45_noE_hold_bid): cc_cagr: '-0.05539576483989872' -> '-0.05633381942137561'; excess_cagr: '-0.0011293963048991662' -> '-0.0020674508863760543'; cc_maxdd: '-0.5945140937771867' -> '-0.5972644549792423'; called_away_pct: '0.13333333333333333' -> '0.15384615384615385'; calls_sold: '15' -> '13'; rej_OK: '15' -> '13'; rej_NO_EXPIRY: '416' -> '402'; rej_EARNINGS_UNKNOWN: '21' -> '93'; rej_BASIS_ABOVE_BAND: '499' -> '482'; slack: '15' -> '13'
  (MDLZ, d0.150_dte30-45_noE_hold_bid): cc_cagr: '0.07191886634551614' -> '0.07322584148594724'; excess_cagr: '0.01478905674544917' -> '0.01609603188588027'; called_away_pct: '0.047619047619047616' -> '0.025'; calls_sold: '42' -> '40'; rej_OK: '42' -> '40'; rej_NO_EXPIRY: '177' -> '159'; rej_EARNINGS_UNKNOWN: '18' -> '87'; rej_EARNINGS_BLACKOUT: '79' -> '84'; rej_BASIS_ABOVE_BAND: '161' -> '140'; in_window: '14' -> '13'; slack: '28' -> '27'
  (MO, d0.150_dte30-45_noE_hold_bid): cc_cagr: '0.14337755436998978' -> '0.1424142583842818'; excess_cagr: '-0.005629488882307632' -> '-0.006592784868015622'; called_away_pct: '0.12903225806451613' -> '0.13793103448275862'; calls_sold: '31' -> '29'; rej_OK: '31' -> '29'; rej_NO_EXPIRY: '238' -> '224'; rej_EARNINGS_UNKNOWN: '19' -> '90'; rej_EARNINGS_BLACKOUT: '67' -> '63'; rej_BASIS_ABOVE_BAND: '196' -> '186'; slack: '27' -> '25'
  (T, d0.150_dte30-45_noE_hold_bid): rej_NO_EXPIRY: '519' -> '487'; rej_EARNINGS_UNKNOWN: '24' -> '95'; rej_BASIS_ABOVE_BAND: '635' -> '596'
  (VZ, d0.150_dte30-45_noE_hold_bid): rej_NO_EXPIRY: '445' -> '411'; rej_EARNINGS_UNKNOWN: '22' -> '94'; rej_NO_STRIKE_IN_TOLERANCE: '13' -> '9'; rej_BASIS_ABOVE_BAND: '528' -> '494'
  ... 130 more
JSON summary.json: NaN tokens: before 0, after 0; changes 67
ADDED counts_bot_rule_bid.AAL.earnings_gap_days = 0
ADDED counts_bot_rule_bid.BAC.earnings_gap_days = 0
ADDED counts_bot_rule_bid.BMY.earnings_gap_days = 0
ADDED counts_bot_rule_bid.CMCSA.earnings_gap_days = 72
counts_bot_rule_bid.CMCSA.rej_BASIS_ABOVE_BAND: 445 -> 410
counts_bot_rule_bid.CMCSA.rej_EARNINGS_UNKNOWN: 21 -> 93
counts_bot_rule_bid.CMCSA.rej_NO_EXPIRY: 452 -> 418
counts_bot_rule_bid.CMCSA.rej_NO_STRIKE_IN_TOLERANCE: 110 -> 107
counts_bot_rule_bid.CMCSA.warnings: 'earnings: 1 gap(s) > 120 days between dates; options: 17 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-23 is 17 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN)' -> 'earnings: 1 gap(s) > 120 days between dates; options: 17 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-23 is 17 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN); earnings: gap(s) > 120 days between listed dates (2021-10-28→2022-04-28); no call sold inside them (EARNINGS_UNKNOWN)'
ADDED counts_bot_rule_bid.CSX.earnings_gap_days = 0
ADDED counts_bot_rule_bid.F.earnings_gap_days = 0
ADDED counts_bot_rule_bid.HBAN.earnings_gap_days = 0
ADDED counts_bot_rule_bid.KEY.earnings_gap_days = 0
ADDED counts_bot_rule_bid.KMI.earnings_gap_days = 0
counts_bot_rule_bid.MDLZ.calls_sold: 34 -> 31
ADDED counts_bot_rule_bid.MDLZ.earnings_gap_days = 69
counts_bot_rule_bid.MDLZ.in_window: 13 -> 11
counts_bot_rule_bid.MDLZ.rej_BASIS_ABOVE_BAND: 286 -> 259
counts_bot_rule_bid.MDLZ.rej_EARNINGS_BLACKOUT: 32 -> 45
counts_bot_rule_bid.MDLZ.rej_EARNINGS_UNKNOWN: 18 -> 87
counts_bot_rule_bid.MDLZ.rej_NO_EXPIRY: 255 -> 239
counts_bot_rule_bid.MDLZ.rej_NO_STRIKE_IN_TOLERANCE: 37 -> 36
counts_bot_rule_bid.MDLZ.rej_OK: 34 -> 31
counts_bot_rule_bid.MDLZ.slack: 21 -> 20
counts_bot_rule_bid.MDLZ.warnings: 'earnings: 1 gap(s) > 120 days between dates; earnings: first listed date 2020-01-29 is 23 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN)' -> 'earnings: 1 gap(s) > 120 days between dates; earnings: first listed date 2020-01-29 is 23 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN); earnings: gap(s) > 120 days between listed dates (2021-11-02→2022-04-26); no call sold inside them (EARNINGS_UNKNOWN)'
counts_bot_rule_bid.MO.calls_sold: 23 -> 21
ADDED counts_bot_rule_bid.MO.earnings_gap_days = 71
counts_bot_rule_bid.MO.in_window: 5 -> 4
counts_bot_rule_bid.MO.rej_BASIS_ABOVE_BAND: 225 -> 217
counts_bot_rule_bid.MO.rej_EARNINGS_BLACKOUT: 68 -> 64
counts_bot_rule_bid.MO.rej_EARNINGS_UNKNOWN: 19 -> 90
counts_bot_rule_bid.MO.rej_NO_EXPIRY: 311 -> 293
counts_bot_rule_bid.MO.rej_NO_STRIKE_IN_TOLERANCE: 96 -> 90
counts_bot_rule_bid.MO.rej_OK: 23 -> 21
counts_bot_rule_bid.MO.slack: 18 -> 17
counts_bot_rule_bid.MO.warnings: 'earnings: 1 gap(s) > 120 days between dates; options: 4 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-30 is 24 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN)' -> 'earnings: 1 gap(s) > 120 days between dates; options: 4 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-30 is 24 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN); earnings: gap(s) > 120 days between listed dates (2021-10-28→2022-04-28); no call sold inside them (EARNINGS_UNKNOWN)'
ADDED counts_bot_rule_bid.OXY.earnings_gap_days = 0
ADDED counts_bot_rule_bid.PFE.earnings_gap_days = 0
ADDED counts_bot_rule_bid.PYPL.earnings_gap_days = 0
ADDED counts_bot_rule_bid.T.earnings_gap_days = 71
counts_bot_rule_bid.T.rej_BASIS_ABOVE_BAND: 567 -> 531
counts_bot_rule_bid.T.rej_EARNINGS_UNKNOWN: 24 -> 95
counts_bot_rule_bid.T.rej_NO_EXPIRY: 523 -> 491
counts_bot_rule_bid.T.rej_NO_STRIKE_IN_TOLERANCE: 84 -> 81
counts_bot_rule_bid.T.warnings: 'earnings: 1 gap(s) > 120 days between dates; options: 13 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-29 is 23 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN)' -> 'earnings: 1 gap(s) > 120 days between dates; options: 13 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-29 is 23 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN); earnings: gap(s) > 120 days between listed dates (2021-10-21→2022-04-21); no call sold inside them (EARNINGS_UNKNOWN)'
ADDED counts_bot_rule_bid.USB.earnings_gap_days = 0
ADDED counts_bot_rule_bid.VZ.earnings_gap_days = 72
counts_bot_rule_bid.VZ.rej_BASIS_ABOVE_BAND: 549 -> 525
counts_bot_rule_bid.VZ.rej_EARNINGS_UNKNOWN: 22 -> 94
counts_bot_rule_bid.VZ.rej_NO_EXPIRY: 509 -> 475
counts_bot_rule_bid.VZ.rej_NO_STRIKE_IN_TOLERANCE: 88 -> 74
counts_bot_rule_bid.VZ.warnings: 'earnings: 1 gap(s) > 120 days between dates; options: 7 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-30 is 24 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN)' -> 'earnings: 1 gap(s) > 120 days between dates; options: 7 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-01-30 is 24 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN); earnings: gap(s) > 120 days between listed dates (2021-10-20→2022-04-22); no call sold inside them (EARNINGS_UNKNOWN)'
monte_carlo_2_stocks_1yr.cc_dd.25: -0.30821899604741876 -> -0.30816879300609024
monte_carlo_2_stocks_1yr.cc_dd.50: -0.21453654399865668 -> -0.2143059515059909
monte_carlo_2_stocks_1yr.cc_dd.75: -0.15477574491595567 -> -0.15459623751896126
monte_carlo_2_stocks_1yr.cc_dd.95: -0.09856034927475943 -> -0.09864181450747239
monte_carlo_2_stocks_1yr.cc_ret.25: -0.10084448720474903 -> -0.10086427429997219
monte_carlo_2_stocks_1yr.cc_ret.5: -0.35617235782734163 -> -0.35565549351158093
monte_carlo_2_stocks_1yr.cc_ret.50: 0.06892661494702335 -> 0.06856080001083309
monte_carlo_2_stocks_1yr.cc_ret.75: 0.26239032513257615 -> 0.2617077642888577
monte_carlo_2_stocks_1yr.cc_ret.95: 0.642111386709187 -> 0.6411856183358186
walkforward_picks[0].train_excess_logret: 0.006637185029385485 -> 0.0068534573373431355
walkforward_picks[3].train_excess_logret: 0.014156459289882468 -> 0.01392386957036666
walkforward_picks[5].picked: 'd0.150_dte30-45_E_roll_bid' -> 'd0.450_dte30-45_noE_take50_bid'
walkforward_picks[5].train_excess_logret: 0.01716781281245508 -> 0.017290905057870412
walkforward_picks[9].picked: 'd0.200_dte14-24_noE_take50_bid' -> 'd0.200_dte14-24_noE_hold_bid'
walkforward_picks[9].train_excess_logret: 0.0025074499584488235 -> 0.0011575872613138038
CSV trades_AAL.csv: match key, rows 4 -> 4, matched 4, added 0, removed 0, changed 0; by column: none
CSV trades_BAC.csv: match key, rows 22 -> 22, matched 22, added 0, removed 0, changed 0; by column: none
CSV trades_BMY.csv: match key, rows 13 -> 13, matched 13, added 0, removed 0, changed 0; by column: none
CSV trades_CMCSA.csv: match key, rows 12 -> 12, matched 12, added 0, removed 0, changed 0; by column: none
CSV trades_CSX.csv: match key, rows 38 -> 38, matched 38, added 0, removed 0, changed 0; by column: none
CSV trades_F.csv: match key, rows 11 -> 11, matched 11, added 0, removed 0, changed 0; by column: none
CSV trades_HBAN.csv: match key, rows 15 -> 15, matched 15, added 0, removed 0, changed 0; by column: none
CSV trades_KEY.csv: match key, rows 13 -> 13, matched 13, added 0, removed 0, changed 0; by column: none
CSV trades_KMI.csv: match key, rows 16 -> 16, matched 16, added 0, removed 0, changed 0; by column: none
CSV trades_MDLZ.csv: match key, rows 34 -> 31, matched 28, added 3, removed 6, changed 17; by column: qty=17
  ADDED 2022-04-27
  ADDED 2022-07-27
  ADDED 2022-11-02
  2023-02-01: qty: '0.021230834486395483' -> '0.0212879725369058'
  2023-03-22: qty: '0.021341869790892098' -> '0.02139930666813204'
  2023-04-28: qty: '0.020937626647837295' -> '0.02099397559491881'
  2023-06-21: qty: '0.021087450491154146' -> '0.02114420265565665'
  2023-07-28: qty: '0.021286436651794253' -> '0.021343724343117654'
  2023-09-20: qty: '0.021442166628125373' -> '0.021499873431908026'
  2023-11-16: qty: '0.0217237597447898' -> '0.02178222439357066'
  2023-12-20: qty: '0.021861875539452534' -> '0.021920711896055652'
  2024-01-31: qty: '0.021827212004027284' -> '0.02188595507146462'
  2024-03-20: qty: '0.021870418823746556' -> '0.021929278172691767'
  2024-05-01: qty: '0.022171086567620405' -> '0.0222307550966639'
  2024-08-23: qty: '0.022330544372297118' -> '0.022390642046417494'
  2024-09-20: qty: '0.022345905460661574' -> '0.022406044475721393'
  2024-11-25: qty: '0.022533576984210785' -> '0.02259422107527215'
  2025-03-04: qty: '0.022728023824034632' -> '0.022789191225348476'
  2025-05-01: qty: '0.022902636941427888' -> '0.022964274274958844'
  2026-07-29: qty: '0.023923280740256455' -> '0.023987664908678322'
  ... 6 more
CSV trades_MO.csv: match key, rows 23 -> 21, matched 21, added 0, removed 2, changed 17; by column: qty=17
  2022-05-02: qty: '0.02490944131115388' -> '0.02447642991271941'
  2023-04-28: qty: '0.027508503226950972' -> '0.027030311231299613'
  2024-05-03: qty: '0.029431424929688043' -> '0.028919805969329554'
  2024-06-24: qty: '0.030088420939918835' -> '0.029565381138859734'
  2024-08-21: qty: '0.030094250621029533' -> '0.029571109480147566'
  2024-09-20: qty: '0.03069924007896582' -> '0.03016558214937122'
  2024-11-01: qty: '0.0307839214232938' -> '0.0302487914419229'
  2024-12-20: qty: '0.030869065201221943' -> '0.030332455129395055'
  2025-01-31: qty: '0.03163072908785217' -> '0.031080878689172226'
  2025-03-21: qty: '0.03046937171707175' -> '0.029939709686847043'
  2025-04-30: qty: '0.031022247668385083' -> '0.03048297476066824'
  2025-06-20: qty: '0.03179995386174577' -> '0.031247161756944104'
  2025-07-31: qty: '0.031948438832345466' -> '0.031393065550231844'
  2025-09-16: qty: '0.031370092736469464' -> '0.03082477309018918'
  2026-02-03: qty: '0.03218350187497321' -> '0.03162404239214809'
  2026-05-04: qty: '0.03298303746047879' -> '0.0324096793109733'
  2026-06-22: qty: '0.033767783186861494' -> '0.03318078346907867'
  REMOVED 2022-01-19
  REMOVED 2022-02-23
CSV trades_OXY.csv: match key, rows 7 -> 7, matched 7, added 0, removed 0, changed 0; by column: none
CSV trades_PFE.csv: match key, rows 12 -> 12, matched 12, added 0, removed 0, changed 0; by column: none
CSV trades_PYPL.csv: match key, rows 13 -> 13, matched 13, added 0, removed 0, changed 0; by column: none
CSV trades_T.csv: match key, rows 1 -> 1, matched 1, added 0, removed 0, changed 0; by column: none
CSV trades_USB.csv: match key, rows 10 -> 10, matched 10, added 0, removed 0, changed 0; by column: none
CSV trades_VZ.csv: match key, rows 3 -> 3, matched 3, added 0, removed 0, changed 0; by column: none
CSV walkforward_by_ticker.csv: match key, rows 17 -> 17, matched 17, added 0, removed 0, changed 16; by column: wf_cc_cagr=16, excess_cagr=16, wf_cc_maxdd=7
  AAL: wf_cc_cagr: '-0.056391114616391014' -> '-0.05639111461639068'; excess_cagr: '1.1102230246251565e-16' -> '4.440892098500626e-16'; wf_cc_maxdd: '-0.5514342235410485' -> '-0.5514342235410479'
  BAC: wf_cc_cagr: '0.03454526461640106' -> '0.02967570045375334'; excess_cagr: '-0.0008869038517691497' -> '-0.005756468014416871'
  BMY: wf_cc_cagr: '0.05330918655076' -> '0.05314412889943587'; excess_cagr: '0.010360857618343822' -> '0.010195799967019692'
  CMCSA: wf_cc_cagr: '-0.10417303770902997' -> '-0.10464855766021441'; excess_cagr: '0.00047551995118400026' -> '-4.440892098500626e-16'; wf_cc_maxdd: '-0.529157623328733' -> '-0.5303675523264872'
  CSX: wf_cc_cagr: '0.059514299020163586' -> '0.06394612689420498'; excess_cagr: '-0.02461860316320519' -> '-0.020186775289163794'
  F: wf_cc_cagr: '-0.07574235304180832' -> '-0.07638643618648133'; excess_cagr: '-0.002000693761512462' -> '-0.0026447769061854753'; wf_cc_maxdd: '-0.5680662716538296' -> '-0.5695229613589752'
  HBAN: wf_cc_cagr: '0.02321100585421232' -> '0.03128957518049824'; excess_cagr: '-0.014460545531108648' -> '-0.006381976204822726'
  KEY: wf_cc_cagr: '0.015485999235779202' -> '0.015485999235779868'; excess_cagr: '-0.004390650087893633' -> '-0.004390650087892967'
  KMI: wf_cc_cagr: '0.1795486487230331' -> '0.17340531544684934'; excess_cagr: '-0.025321859438513394' -> '-0.031465192714697165'
  MDLZ: wf_cc_cagr: '0.02015736564048698' -> '0.020514498992729946'; excess_cagr: '-0.004889391459004022' -> '-0.004532258106761056'; wf_cc_maxdd: '-0.27726589492411147' -> '-0.27199773406357386'
  MO: wf_cc_cagr: '0.13812856895918002' -> '0.14624886319406283'; excess_cagr: '-0.043643260231274406' -> '-0.0355229659963916'; wf_cc_maxdd: '-0.24848183531867984' -> '-0.24967624673445066'
  OXY: wf_cc_cagr: '0.15847439534900576' -> '0.15335737495177226'; excess_cagr: '0.012759900213192399' -> '0.007642879815958903'; wf_cc_maxdd: '-0.4471282212827309' -> '-0.45886230278161233'
  PYPL: wf_cc_cagr: '-0.20883911849890713' -> '-0.20883911849890702'; excess_cagr: '-7.771561172376096e-16' -> '-6.661338147750939e-16'; wf_cc_maxdd: '-0.7962707661255592' -> '-0.796270766125559'
  T: wf_cc_cagr: '0.0216749246819663' -> '0.021674924681966967'; excess_cagr: '-6.661338147750939e-16' -> '0.0'
  USB: wf_cc_cagr: '0.057637681786055994' -> '0.05739633393620314'; excess_cagr: '0.0051418731349131' -> '0.004900525285060242'
  VZ: wf_cc_cagr: '0.033209882320674344' -> '0.033209882320674566'; excess_cagr: '-2.220446049250313e-16' -> '0.0'
CSV walkforward_picks.csv: match key, rows 10 -> 10, matched 10, added 0, removed 0, changed 4; by column: picked=2, train_excess_logret=4
  (2020-01-06, 2022-01-06): train_excess_logret: '0.006637185029385485' -> '0.0068534573373431355'
  (2021-07-06, 2023-07-06): train_excess_logret: '0.014156459289882468' -> '0.01392386957036666'
  (2022-07-06, 2024-07-06): picked: 'd0.150_dte30-45_E_roll_bid' -> 'd0.450_dte30-45_noE_take50_bid'; train_excess_logret: '0.01716781281245508' -> '0.017290905057870412'
  (2024-07-06, 2026-07-06): picked: 'd0.200_dte14-24_noE_take50_bid' -> 'd0.200_dte14-24_noE_hold_bid'; train_excess_logret: '0.0025074499584488235' -> '0.0011575872613138038'
TOTAL: files 22, only-before 0, only-after 0, not compared 0, json changes 67, csv rows changed 219 added 3 removed 8, columns changed 2
exit 1
```

Comparison with A1's expected numbers (logs/audit/2026-11-15-065.md L80-92), computed from the diff above and the two scratch dirs:
| A1 expected | diff_reports / scratch result | Match |
|---|---|---|
| walkforward_picks: picked changes in 2 of 10 windows (2022-07-06..2024-07-06, 2024-07-06..2026-07-06) | `by column: picked=2` with the same two windows and labels | yes |
| walkforward_by_ticker excess_cagr changes for 11 of 17 | diff: `excess_cagr=16` (exact equality). 5 of the 16 (AAL, KEY, PYPL, T, VZ) are float noise below 1e-15; `abs(delta) > 1e-9` counts 11 | yes (11 real), see Deviations |
| tickers with positive excess 6 -> 5 | strict `> 0`: 6 -> 5 (AAL's +1.1e-16 / +4.4e-16 counts as positive). With `> 1e-9`: 5 -> 4 | yes as A1 counted; the real count is 5 -> 4 |
| monte_carlo cc_ret median 0.0689 -> 0.0686 | `monte_carlo_2_stocks_1yr.cc_ret.50: 0.06892661494702335 -> 0.06856080001083309` | yes |
| calls_sold MO 23 -> 21, MDLZ 34 -> 31 | `counts_bot_rule_bid.MO.calls_sold: 23 -> 21`, `MDLZ.calls_sold: 34 -> 31` | yes |
| (not in A1) | also changed: train_excess_logret in 4 of 10 windows, wf_cc_cagr 16, wf_cc_maxdd 7, trades/grid rows (csv rows changed 219, added 3, removed 8), 67 JSON values | new for the person |

## Deviations from plan
- 04 expected 16 new tests; there are 17 (`test_diff_dirs_importable` added for 068's reuse). Suite 324 -> 341.
- Exact equality (03/04 decision) also reports float noise (~1e-16) in walk-forward CSV cells, so a raw count can exceed a "meaningful" count (16 vs 11 above). Kept exact, as decided; the noise is visible per row, so the reader can see it. A tolerance option is left out on purpose (RI-013: nothing hidden).
- I2's session was interrupted by a container restart after the diff ran; the orchestrating session finished this file (comparison table, this section, RI lines), log line and commit from the outputs already on disk (scratchpad/067-diff.txt, 067-tests.txt). No step re-run was needed; the 17 tests re-pass (`17 passed in 0.67s`).

Recurring issues checked (logs/recurring-issues.md): RI-013 (OPEN): guardrail built (067). Mutation 1 (recursion cut to top level) fails test_a (5 failed, 12 passed). GUARDED when 067 is merged and that probe fails on main. RI-006: every count above is pasted from command output or computed by the shown script. RI-008: stdlib only, no 3.12-only csv options (grep exit 1), compiles on 3.11. RI-002: missing/empty dirs and bad input exit 2 with a reason, never `no change`. RI-007: Scope FULL, I2 step on 04; templates/ change makes this a RULES BRANCH for the person to review. RI-009: mutations in scratch worktrees only.
