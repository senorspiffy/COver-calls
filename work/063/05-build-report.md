# 05 Build report - 063

Built 2026-11-14/15 (UTC) on branch daily-fixes/2026-11-14 from work/063/04-build-plan.md (FIT WITH CHANGES). Research backtest only. No brokerage was contacted and no order was placed. Data used: data/real (sample/historical) and synthetic test fixtures. reports/real/ was not regenerated in the repo (`git status --short reports` → empty). Research, not financial advice.

File counts (commands run before writing this file; work/ and logs/ excluded):
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` → **0** new
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` → **4** changed (ccbot/realtest.py, tests/test_realtest.py, .claude/agents/r3-fact-checker.md, .claude/agents/i3-verifier.md)
- Plus this file (work/063/05-build-report.md) and the log line in logs/implementation/.

## Changes made (file: what changed)
- **ccbot/realtest.py**
  - Module docstring: EARNINGS_UNKNOWN also "on a day before its first listed date (history not in the file, item 063)".
  - `REALTEST_MISSING`: new row `earnings_before_first`.
  - `load_ticker`: if `er is not None and not earnings and asset != "etf"`, it adds the warning `"earnings: no dates (EARNINGS_UNKNOWN for a stock)"` (plan change 1; no text matching). The missing-file branch is unchanged.
  - `_earnings_known`: `bool(td.earnings) and td.earnings[0] <= d and td.earnings[-1] >= d`, with a new docstring.
  - `simulate`:
    - `lead = (td.earnings[0] - days[0]).days` for a stock with dates, else None.
    - `earnings_lead_days = max(lead, 0)` (int), or NaN when lead is None.
    - The edge warning is written when `lead > 0`. It ends "; no call sold before it (EARNINGS_UNKNOWN)" when `rule.skip_earnings`, else "; earnings not checked by this rule" (change 2).
    - `earnings_lead_days` is added to `df.attrs["counts"]`, and `df.attrs["warnings"]` is set.
  - `summarize`: `"warnings": "; ".join(td.warnings + df.attrs.get("warnings", []))`.
  - `run`: a NaN `earnings_lead_days` in `counts[tk]` is written as `None` (JSON `null`) in summary.json (change 3).
- **tests/test_realtest.py**
  - New tests: `test_leading_edge_100_days_blocks` (T1), `test_leading_edge_151_days_blocks` (T2), `test_leading_edge_rule_without_earnings_check_still_sells` (T4), `test_empty_earnings_file_warns_and_lead_is_null`. Helpers `_edge` and `_no_nan` (the strict `parse_constant`). `import json`.
  - T3 in `test_run_end_to_end`: AAA `earnings_lead_days == 23` and `"first listed date 2019-01-25"` in the summary.json warnings.
  - `DROP_CASES` gains `earnings_before_first`, with a new branch in `test_drop_input`: first date 2019-07-25, no sale before it, at least one sale on or after it, UNKNOWN > 0, lead 204, warning text, reason contains EARNINGS_UNKNOWN.
  - `test_realtest_missing_lists_every_input`: the set gains `earnings_before_first`. The `files ==` line is unchanged.
  - NaN lead asserts added in `test_drop_input[earnings]`, `test_etf_without_earnings_sells` (also `warnings == []`) and `test_stock_without_earnings_sells_nothing`. The last one also asserts lead `== 0` for `[2023-10-01]`.
  - Fixture edits: in `test_earnings_today_blocks` (control), `test_take50_only_in_first_third` and `test_sales_under_3_cents_are_counted_not_blocked`, `[2024-06-01]` → `[2023-10-25, 2024-06-01]`. Their assert lines are unchanged. `test_premium_yield_na_zero_years` (old L380) is not changed.
  - `REAL_BAC`: all 3 rules re-measured on data/real (start 2020-01-01). New values are pinned, plus `earnings_lead_days=100`. The header comment says "re-measured by I2 for 063 on 2026-11-14".
  - No assert removed or loosened.
- **.claude/agents/r3-fact-checker.md** step 1b and **.claude/agents/i3-verifier.md** step 3 (after the RI-002 sentences): appended "For any data-hole check, check the edges of the data window (before the first value and after the last) as well as gaps between values."
  - `git diff --word-diff=porcelain .claude/agents | grep -c '^-[^-]'` → 0 (additions only).
  - `grep -rl "edges of the data window" .claude/agents` → 2 files.
  - **These need the person's OK in PR review** (03 step 7).

## Connectivity check
- [x] every new function/rule is used
  - `_edge` is used by T1, T2 and T4; `_no_nan` by the empty-file test.
  - The new `_earnings_known` clause has one caller (simulate's entry check).
  - The `earnings_before_first` row is enumerated by `test_realtest_missing_lists_every_input` and dropped by `test_drop_input[earnings_before_first]`.
- [x] every input has a source, every output has a consumer
  - Input: `td.earnings` comes from data/real/earnings/T.csv.
  - Outputs:
    - `earnings_lead_days` goes to summary.json `counts_bot_rule_bid` (T3, empty-file test), bot_rule_by_ticker.csv and grid_in_sample.csv (through `df.attrs["counts"]`).
    - The edge warning goes to the summary `warnings` field (T3, scratch run below).
    - The "no dates" warning goes to `td.warnings` and then to summary.json.
- [x] every branch ends in a defined result
  - No earnings file → old warning, lead NaN/null, every day UNKNOWN.
  - File present with 0 rows → "no dates" warning, lead NaN/null, every day UNKNOWN.
  - ETF → no edge, no warning, lead NaN/null.
  - lead ≤ 0 → lead 0, no edge warning; the trailing edge still applies.
  - lead > 0 → warning, plus UNKNOWN until the first date under `skip_earnings`.
  - First date after the period end → 0 sold, warning (T1, T2).
  - A rule without the earnings check → sells, and its warning says "not checked".
- [x] no leftover TODOs or unused files
  - `git diff | grep -c TODO` → 0.
  - The scratch mutation copy and both scratch report runs were removed (`rm -rf` of scratchpad/mut, before, after).

Missing-data grep (`grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/`). New or changed hits:
- realtest.py L226 `if er is not None and not earnings and asset != "etf"`: `er is not None` separates "file present, 0 rows" from "file absent". The absent case already has its own warning. The branch only adds a warning; nothing passes or gets a value.
- realtest.py L413 `if lead is not None and lead > 0`: `lead` is None only for an ETF or a stock with no dates. Then no edge warning is written and the lead stays NaN (unknown, shown as null). `lead` is an int day count otherwise, never NaN.

Patterns the grep can't see (014):
- `max(lead, 0)` runs only on an int that exists. The 0 is a measured "first date on or before day 1", not a default.
- No dataclass field was added.
- The only new `>` test is `lead > 0`, where lead is an int (no NaN).
- `df.attrs.get("warnings", [])` defaults to "no extra warning", not a pass or a value. Every summarize call in the repo gets a frame from simulate, which always sets it.

Feasibility numbers (the plan's named tests, real output):
- `test_real_counts_bac`, BAC on data/real from 2020-01-01:

| rule | calls_sold | rej_OK | NO_EXPIRY | UNKNOWN | BLACKOUT | NO_STRIKE | BASIS | in_window | slack | lead |
|---|---|---|---|---|---|---|---|---|---|---|
| BOT_RULE (before → after) | 24 → 22 | 24 → 22 | 369 → 365 | 20 → 60 | 104 → 104 | 11 → 11 | 296 → 290 | 11 → 11 | 13 → 11 | 100 |
| 0.15 / 14-24 | 70 → 68 | 70 → 68 | 0 → 0 | 20 → 60 | 52 → 52 | 4 → 0 | 529 → 513 | 61 → 61 | 9 → 7 | 100 |
| 0.45 / 30-45 | 19 → 18 | 19 → 18 | 397 → 388 | 20 → 60 | 57 → 57 | 37 → 36 | 367 → 355 | 10 → 10 | 9 → 8 | 100 |

  - The unchanged fields are the same in all 3 rules: open_at_end 0, snap_days 1271, snap_days_no_close 55. sub_3c_sales is 1 / 7 / 0 in the three rules, unchanged.
  - L418 (every non-INFO count > 0 for BOT_RULE) still passes.
- **Why BLACKOUT did not drop (plan said "lower").** I split BOT_RULE at the first listed date by re-running the old `_earnings_known` in a script:
  - 2020-01-06 → 04-14, old code: OK 2, NO_EXPIRY 4, BASIS 6, BLACKOUT 0.
  - Same period, new code: UNKNOWN 40, all else 0.
  - 2020-04-15 onward: identical for old and new code, field for field (OK 22, NO_EXPIRY 365, UNKNOWN 20, BLACKOUT 104, NO_STRIKE 11, BASIS 290).
  - So no blackout day existed before the edge to remove. The +40 UNKNOWN covers every attempt day before 04-15. There are more attempt days than before (40 vs 12) because no call is held over them.
- Fixtures: T1 lead 100, T2 lead 151, drop case lead 204, T3 lead 23.

## Test output (pasted, not summarized)
While building, `python3 -m pytest -q -p no:cacheprovider tests/test_realtest.py`:
```
...........................................                              [100%]
43 passed in 26.10s
```
Full suite, `python3 -m pytest -q -p no:cacheprovider`:
```
tests/test_pipeline_check.py:142: AssertionError
=========================== short test summary info ============================
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 297 passed, 1 skipped in 50.23s
```
- The failure is not from 063. `python3 scripts/check_pipeline.py` (exit 1) prints `INCOMPLETE: 064 (no log line for I1)`, caused by item 064's uncommitted work/064/04-build-plan.md, which has no I1 log line yet. Every other line: `SKIPPED: none`, `UNTRACKED CHANGE: none`, `LOG TIME: none (not checked: 048 ...)`, `RESEARCH CODE: none`, `ID CLASH: none`.
- Count check: plan expected 293 + 5 new = 298 passed + 1 skipped. Measured: 297 passed + 1 failed (064's) = 298, + 1 skipped.

RI-008: `python3 -m pytest -q -p no:cacheprovider tests/test_safety.py -k compiles` → `1 passed, 8 deselected in 0.12s`.

Mutations: done on a copied folder under the session scratchpad (`.../scratchpad/mut`, ccbot+tests+config copied, data symlinked), never in the repo. Each ran `pytest tests/test_realtest.py` and then restored the file.
- **M1**: delete `td.earnings[0] <= d and`.
  ```
  FAILED tests/test_realtest.py::test_leading_edge_100_days_blocks
  FAILED tests/test_realtest.py::test_leading_edge_151_days_blocks
  FAILED tests/test_realtest.py::test_drop_input[earnings_before_first]
  FAILED tests/test_realtest.py::test_real_counts_bac[d0.275_dte30-45_noE_hold_bid]
  FAILED tests/test_realtest.py::test_real_counts_bac[d0.150_dte14-24_noE_hold_bid]
  FAILED tests/test_realtest.py::test_real_counts_bac[d0.450_dte30-45_noE_hold_bid]
  6 failed, 37 passed in 55.09s
  ```
- **M2**: replace the clause with `(td.earnings[0] - d).days <= EARNINGS_GAP_WARN and`. T1 fails and T2 passes, as the plan expected.
  ```
  FAILED tests/test_realtest.py::test_leading_edge_100_days_blocks
  FAILED tests/test_realtest.py::test_drop_input[earnings_before_first]
  FAILED tests/test_realtest.py::test_real_counts_bac[d0.275_dte30-45_noE_hold_bid]
  FAILED tests/test_realtest.py::test_real_counts_bac[d0.150_dte14-24_noE_hold_bid]
  FAILED tests/test_realtest.py::test_real_counts_bac[d0.450_dte30-45_noE_hold_bid]
  5 failed, 38 passed in 51.04s
  ```
- **M3**: the "no call sold" text for every rule.
  ```
  FAILED tests/test_realtest.py::test_leading_edge_rule_without_earnings_check_still_sells
  1 failed, 42 passed in 24.58s
  ```
- **M4**: NaN → None line in `run` removed.
  ```
  FAILED tests/test_realtest.py::test_empty_earnings_file_warns_and_lead_is_null
  1 failed, 42 passed in 24.97s
  ```

Real-data scratch run (03 step 6). The before run used the code before this change (module loaded before the first edit). Both runs used `python3 -m ccbot.realtest --out <scratch>/{before,after} --mc-paths 200`, which takes about 15 min each. MC is not in the counted fields. summary.json (after) was parsed with a strict `parse_constant` with no error, and `skipped` is identical (ITUB, KGC, PBR, VALE).

Per-ticker calls_sold (bot rule, bid) from summary.json `counts_bot_rule_bid`:

| ticker | before | after | diff | earnings_lead_days |
|---|---|---|---|---|
| AAL | 4 | 4 | 0 | 17 |
| BAC | 24 | 22 | -2 | 100 |
| BMY | 13 | 13 | 0 | 31 |
| CMCSA | 12 | 12 | 0 | 17 |
| CSX | 37 | 38 | +1 | 107 |
| F | 11 | 11 | 0 | 29 |
| HBAN | 15 | 15 | 0 | 17 |
| KEY | 13 | 13 | 0 | 17 |
| KMI | 16 | 16 | 0 | 16 |
| MDLZ | 34 | 34 | 0 | 23 |
| MO | 23 | 23 | 0 | 24 |
| OXY | 8 | 7 | -1 | 52 |
| PFE | 12 | 12 | 0 | 22 |
| PYPL | 13 | 13 | 0 | 23 |
| T | 1 | 1 | 0 | 23 |
| USB | 11 | 10 | -1 | 100 |
| VZ | 3 | 3 | 0 | 24 |
| **total** | **250** | **247** | **-3** | |

- The total is 247, as expected. Leads for the other 13 tickers are 16-31 d. 03 said 16-37; the measured maximum among them is 31 (BMY).
- Per-ticker diff of trade open dates (trades_*.csv):
  - BAC: dropped 2020-01-06 and 2020-02-21.
  - USB: dropped 2020-01-06.
  - OXY: dropped 2020-01-06.
  - CSX: dropped 2020-01-06, 2020-02-21, 2020-05-27 and 2020-08-26; added 2020-04-29, 06-19, 07-24, 08-21 and 09-18. That is net +1: after the edge it starts from a different basis and path (02 FOR 3).
  - So 6 sales are blocked directly before the edge, matching 03.

Warning lines (summary.json, after):
```
BAC 100 | options: 10 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-04-15 is 100 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN)
CSX 107 | options: 17 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-04-22 is 107 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN)
USB 100 | options: 15 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-04-15 is 100 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN)
OXY 52 | options: 14 quote rows dropped (iv not finite/positive or delta not finite); earnings: first listed date 2020-02-27 is 52 days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN)
```

A-rows (061/01 criteria). These are computed from the scratch CSVs with diag_keep.py's formulas: bot rule at the bid, SPY excluded; A5 from walkforward_by_ticker.csv.

| row | before | after | verdict change |
|---|---|---|---|
| A1 | 250 calls, IV > RV 63.2%, mean P&L -0.083% | 247 calls, IV > RV 64.0%, mean P&L -0.095% | none (Fail: P&L < 0) |
| A2 | 13/17 | 13/17 | none (Pass) |
| A3 | 17/17 | 17/17 | none (Pass) |
| A4 | 0.0986 vs 0.0940 | 0.0986 vs 0.0940 | none (Pass) |
| A5 | median -2.2e-16 pt, 8/17 > 0 | median -7.8e-16 pt, 6/17 > 0 | none (Pass, limit -1.0) |

- Median bot-rule gap: +0.297 pt → +0.297 pt.
- Per-ticker excess CAGR changes (bid): BAC -0.24 → -0.45 pt, CSX +0.55 → +0.72, OXY -1.60 → -1.82, USB +1.25 → +1.11. The other 13 are unchanged.
- A5: one walk-forward pick moved. Block 0 (test 2022-01-06 → 07-06, trained on 2020-01-06 → 2022-01-06, which contains the blocked weeks) went from d0.350_dte14-24_noE_hold to d0.150_dte14-24_noE_take50. The other 9 blocks are unchanged.
- No A-row verdict changes for any ticker.

Label for the dropped Feb-Mar 2020 sales: **"stock only, no sale (earnings unknown)"**. This is a data effect (the earnings file starts in April 2020), not a strategy result.

reports/real/ was not touched: `git status --short reports` → empty.

## Deviations from plan
1. **r3-fact-checker.md: one sentence in step 1b only, not also in step 4.** The plan's Files 3 line reads "step 1b and 4". Three other places say one sentence per file:
   - 03 step 7: "r3 step 1b and i3 step 3 … 2 one-sentence additions".
   - The plan's own Expected result: "2 agent files gain one sentence each".
   - The plan's check: Grep → 2 files.

   I followed those and read "4" as a slip. If I1 meant step 4 as well, that is a one-sentence addition left for I3/I1 to raise.
2. **BAC EARNINGS_BLACKOUT stays at 104** (plan: "lower"). Explained above with the split at 2020-04-15: no blackout day existed before the edge. calls_sold is 22, as the plan expected.
3. **The other 13 tickers' leads are 16-31 d, not 16-37 d** (measured; information only).
4. **The full suite has 1 failure from item 064's uncommitted step file** (`INCOMPLETE: 064`), not from 063. It clears when 064's I1 log line is written.

No other deviation. Nothing was improvised beyond the plan.

## Recurring issues checked (item 013)
Recurring issues checked: RI-001, RI-002 (open/ESCALATED), plus RI-004, RI-005, RI-006, RI-007, RI-008, RI-009, RI-010, RI-011, RI-012 (guarded; scanned for what this build touches).
- RI-001: the edge rule's count is measured on data/real: BAC UNKNOWN 60, calls 22, lead 100, pinned with `==`. All 17 reported tickers still sell (min 1, T). L418 still passes.
- RI-002: unknown stays unknown. The lead is NaN in simulate and null in summary.json, never 0. The new REALTEST_MISSING row is enumerated and has a drop test. M1 fails 6 tests.
- RI-004: the fixture dates were checked against the trigger. T1 2024-04-11 > 01-02 → UNKNOWN. The controls 2023-10-25 ≤ 01-02 ≤ 2024-06-01, with no date in [01-02, 02-16], still sell (their tests pass). The drop case gives 204 = 2019-01-02 → 07-25, confirmed by the test.
- RI-005: 100, 151, 23 and 204 are asserted by tests. 247 is measured.
- RI-006: counts come from commands (git status counts, pytest lines, summary.json).
- RI-007: the I2 step is written before commit. The log uses `--log`.
- RI-008: the compile test passes.
- RI-009: mutations ran in a copied scratch folder, never in the repo. work/064's uncommitted file was not touched or staged.
- RI-010: the log line is written with `check_pipeline.py --log`.
- RI-011: not touched.
- RI-012: no new text classification. The "no dates" warning is keyed on data, and the tests pin the numeric `earnings_lead_days`.

RI-001: holds; edge rule feasibility measured on data/real and pinned (REAL_BAC, L418 passes).
RI-002: guardrail built (063); GUARDED when 063 is merged and its leading-edge tests fail with `td.earnings[0] <= d and` removed (I2 probe: 6 failed, 37 passed).
