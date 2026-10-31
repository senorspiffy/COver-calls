# 05 Build report - 003 to 008 (combined)

I2 wrote this on 2026-10-30, on branch `claude/bugfixes-003-008` (base `74cf949`, working tree, **not committed**). Input: `work/003/04-build-plan.md`. Each of `work/004…008/05-build-report.md` points here. No live account was contacted. No order left the local sim. Every test runs offline (the `conftest.py` socket block is unchanged). This is research, not financial advice.

**Result:** 126 passed, 1 skipped (baseline 93 passed). The skip is the optional `exchange_calendars` cross-check. It passes when that package is installed in a scratch venv (below). 29 files changed, matching the plan's count.

## Changes made (file: what changed)

### 003 – Account-size rule (RI-001)
- `ccbot/screen.py`: new `pass_history(scans, ticker, k=10) -> (n_passed, n_seen)`. Information only.
- `ccbot/bot.py`: `run_daily` reads the earlier `state/scans/*.json` (`stem < date`, sorted) and stores `scan["pass_history"] = {t: [n, k]}` for each universe ticker, counting today's `passing` too.
- `ccbot/report.py`: § Screen prints `- <t>: passed n of last k logged scans`. When k < 10 it adds ` (history short: k < 10)`, with k filled in. It reads `scan.get("pass_history", {})`, so old scan files still render.
- Tests: `test_screen_bot.py::test_pass_history_counts_last_10` (12 dicts → (4, 10); 3 → (3, 3); a `run_daily` after 10 zero-pass scans still sends BUY_SHARES + SELL_CALL) and `test_report.py::test_daily_report_shows_pass_history`.

### 004 – Expiry and strike rules (RI-001), code unchanged
- `tests/test_calendar.py::test_monthly_coverage_2016_2025`. **Real numbers:** days = 2,609; strict 30–45 = 1,440 (55.2%); with 7-day slack = 2,483 (95.2%); longest run with no candidate ≤ 3. Fails with `monthly_slack_days: 0` (mutation 5).
- `tests/test_pricing.py::test_tolerance_finds_strike_on_bs_grid`, on a $0.50 grid the test builds itself. **Real deltas** (35 DTE, r .04, q 0):
  - S 24/σ .25: 25.0C 0.330, 25.5C 0.244, 26.0C 0.172
  - S 17/σ .35: 18.0C 0.331, 18.5C 0.245, 19.0C 0.174
  - S 12/σ .25: 12.5C 0.330, 13.0C 0.172
  - S 24/σ .50: 26.5C 0.295, 27.0C 0.255

  So the 0.25–0.30 band is empty in 3 of 4 cases, and nearest 0.275 within [0.20, 0.35] finds a strike in all 4. These match 004/03.

### 005 – Unknown earnings / OI / dividend (RI-002)
- `ccbot/missing.py` (new): `MISSING_POLICY`, with the 9 keys from the plan as `(effect, reason/text)`.
- `ccbot/rules.py`:
  - New `Day.earnings_known: bool = False` (last field, so positional callers are unchanged).
  - `REASONS` += `EARNINGS_UNKNOWN`, `DIVIDEND_UNKNOWN`.
  - `_option_entry` checks both just before the blackout (after `VOL_WARMUP` / `NO_EXPIRY` / up-day).
- `ccbot/data.py`:
  - New `OPTIONAL_CSV_COLUMNS` and `OPTIONAL_SNAPSHOT_FIELDS`.
  - An absent `dividend`/`earnings` column becomes NaN (no `else 0`) and is named in the new `PriceSeries.missing`.
  - Row checks and `astype(int)` run only on columns that were supplied.
- `ccbot/backtest.py`: `build_days` sets `earnings_known = "earnings" not in series.missing or asset == "etf"`.
- `ccbot/screen.py`:
  - Blank OI → `OI_UNKNOWN` (see Deviation 1).
  - A non-ETF with blank `next_earnings` → `EARNINGS_UNKNOWN`, checked before the blackout.
  - Both codes added to `TESTS`.
- `ccbot/broker/sim.py`: snapshot-mode `Day` gets `earnings_known = etf or next_earnings is not None`.
- `ccbot/broker/webull_sandbox.py` L144: comment only (`# earnings unknown → blocked (ccbot/missing.py)`).
- `ccbot/report.py`:
  - New `## Missing inputs` section, from `missing_lines`: one line per `series.missing`, counted on V0 at the base setting, or `- none`.
  - Daily Context shows `Days to earnings: n/a (not supplied)` for a stock whose earnings are unknown.
  - It shows `days to ex-dividend: n/a (not supplied)` when that date is blank (policy row `snapshot.ex_div_date`).
- `ccbot/bot.py`: the context carries `earnings_known`.
- `ccbot/__main__.py`: passes `series.missing` to `backtest_report`.
- New tests:
  - `test_screen_bot.py::test_blank_oi_is_rejected_oi_unknown`
  - `::test_blank_earnings_stock_rejected_earnings_unknown`
  - `test_backtest.py::test_stock_csv_without_earnings_blocks_with_reason`
  - `test_webull_sandbox.py::test_sandbox_day_is_not_earnings_known`
  - `test_data.py::test_absent_optional_columns_are_flagged`
  - `tests/test_missing_inputs.py`: `test_drop_each_input[9 keys]` and `test_policy_lists_every_optional_input`
- Changed tests (planned, research 2):
  - `test_backtest.py::test_no_option_sold_during_vol_warmup`: the CSV now supplies `dividend,earnings` columns of 0. This changes the test input, not the assertion. Without the columns, every entry is now correctly blocked.
  - `test_variants.py::test_every_reason_code_is_produced`: the two new reasons were added to the expected "not produced on SYNTH_A" set. SYNTH_A is an ETF with full columns. Where each reason is produced is noted in the test's comment.

### 006 – B&H never borrows (RI-002)
- `ccbot/backtest.py`:
  - `bh_lots` (floor, no `max(1,`).
  - `bh_na_reason`: "100 shares cost more than cash − buffer", or "dividend: not supplied" (005).
  - `_bh_cash`.
  - `buy_and_hold` returns all NaN on the same index when a reason is set.
- `ccbot/__main__.py`: `bh_m = metrics(bh, None, cfg); bh_m["na_reason"] = bh_na_reason(series, cfg)`.
- `ccbot/report.py`:
  - § Buy and hold prints `n/a (<reason>)` instead of the table.
  - Weekly report: `lots = int(...)` with no `max(1,`. lots < 1 → `n/a (100 shares cost more than cash − buffer)`.
- Tests:
  - `test_backtest.py::test_benchmark_cash_never_negative[feasible, infeasible]`
  - `::test_all_variants_pass_account_invariants_infeasible_bh`
  - `test_report.py::test_bh_na_line_backtest` (through the CLI, with RuntimeWarning raised as an error; grid `excess_vs_bh` all NaN)
  - `::test_bh_na_line_weekly`

### 007 – Exchange holidays (RI-003)
- `config/holidays.json` (new): source, release, checked date, covers 2026-01-01..2028-12-31, 29 holidays, 5 early closes (kept out of `holidays`).
- `ccbot/expiries.py`:
  - `business_days(start, end, holidays=None)`. None keeps Mon–Fri.
  - `load_holidays()`, cached.
  - Comment on `_move_back` (≤ 4-day look-back).
  - `scan_calendar` uses the holidays. Outside `covers` it raises `ValueError("holiday table covers 2026-01-01..2028-12-31; add NYSE dates for <year> to holidays.json (source https://www.nyse.com/…)")`. There is no Mon–Fri fallback.
- `ccbot/broker/base.py`: `Broker.calendar(asof)` (not abstract) → `scan_calendar(asof)`.
- `ccbot/broker/sim.py`:
  - `SimBroker.calendar`: in series mode, `extend(series dates, last + 70 d)` (same as `ModelMarket`). Otherwise the base calendar.
  - The series-mode `list_option_contracts` filters `fridays(self.calendar(self.date))` to [exp_from, exp_to].
- `ccbot/broker/webull_sandbox.py`: the OCC fallback uses `fridays(scan_calendar(exp_from, days=span + 7))` filtered to the window, so a holiday Friday becomes its Thursday.
- `ccbot/bot.py`:
  - `BrokerMarket` uses `broker.calendar(asof)`.
  - `feasible_universe(..., calendar)`.
  - `scan["early_close"]`.
  - The calendar is built before `broker.advance` (Deviation 2).
- `ccbot/screen.py`: `feasible_universe(cfg, snapshots, cash, asof, calendar=None, require_oi=True)`. `_reject` takes the calendar.
- `ccbot/report.py`: `> Early close today: 1:00 p.m. ET (1:15 p.m. for eligible options); run the scan before then.`
- Tests:
  - `test_calendar.py`: `test_holiday_table_matches_nyse`, `test_scan_calendar_raises_outside_table[2028-10-01, 2025-12-15]`, `test_monthly_moves_to_thursday`, `test_weekly_moves_to_thursday`, `test_table_matches_exchange_calendars` (importorskip).
  - `test_webull_sandbox.py::test_occ_fallback_builds_thursday_symbols`
  - `test_report.py::test_early_close_banner_2026_12_24`
  - `test_screen_bot.py::test_scan_outside_holiday_table_changes_nothing` (Deviation 2)
- Kept green: `test_bot_on_simbroker_matches_backtest_v0`, `test_live_scan_rule_2026_10_30`, `test_contract_list_fallback`.

### 008 – 50% worked example (RI-004), code unchanged
- `tests/test_backtest.py::test_worked_example_50pct_exit`: V1, `Short("C", 26, sold + 35 d, 1, 0.47, sold)`, and a stub market with one quote.
  - Day 9, ask 0.23 → `BUY_TO_CLOSE`/`PROFIT_TARGET_HIT` at 0.23.
  - Day 9, ask 0.24 → `HAS_POSITION`.
  - Day 11, ask 0.23 → `BUY_TO_CLOSE`.
  - Day 12, ask 0.23 → `HAS_POSITION`.
  - Also checks (0.47 − 0.23) × 100 − 0.20 = 23.80.

  It passes on today's code, as the plan expects.

### 001 docs (003, 004, 008)
- `work/001/03-handoff.md`: the pointer line goes after L116, and `## Correction 2026-10-30 (items 003, 004, 008)` goes before `## Alternative strategy ideas`. Both texts are copied verbatim from the plan.
- `git diff --stat`: 14 insertions, 0 deletions (only `+` lines).
- Every test the section names exists and passes: `test_universe_empty_blocks_orders`, `test_shipped_config_has_a_passing_ticker`, `test_pass_history_counts_last_10`, `test_monthly_coverage_2016_2025`, `test_live_scan_rule_2026_10_30`, `test_tolerance_finds_strike_on_bs_grid`, `test_worked_example_50pct_exit`.

### Systemic guardrails (RI-001, RI-002) – process files. These need the person's OK in PR review; list them separately in the PR
- `templates/research-handoff.md`: 6th map column `Feasibility` with the required comment, plus a `## Missing inputs` table with its comment.
- `templates/build-plan.md`: `## Rule trace` and `## Guardrail tests`.
- `.claude/agents/r3-fact-checker.md`: the feasibility and worked-example text at the end of step 1, plus a new step 3a (missing inputs).
- `.claude/agents/i1-reviewer.md`: new step 1a (rule trace).
- `.claude/agents/i2-builder.md`: a missing-data policy bullet and the review grep in the connectivity check.
- `.claude/agents/i3-verifier.md`: RI-001/RI-002 re-checks added to step 3.
- The text is the plan's, word for word. These are additions only: no tool, permission or model lines changed. 013's scope (every agent reads `recurring-issues.md`) was left out.

## Connectivity check
- [x] **Every new function/rule is used.**
  - `pass_history` → bot → report.
  - `load_holidays` → `scan_calendar`, bot `early_close`.
  - `Broker.calendar` / `SimBroker.calendar` → bot (`BrokerMarket`, screen), sim fallback.
  - `bh_lots` / `bh_na_reason` / `_bh_cash` → `buy_and_hold`, `__main__`, tests.
  - `missing_lines` → `backtest_report`.
  - `MISSING_POLICY`, `OPTIONAL_*` → `test_missing_inputs.py`. This is data for the guardrail, as planned. The module docstring points readers there.
  - `quotes_have_oi` → bot → screen.
- [x] **Every input has a source, and every output has a consumer.**
  - Pass history comes from `state/scans/*.json` and goes to the daily report.
  - The holiday table comes from `config/holidays.json` and goes to `scan_calendar`, the early-close banner and the Webull fallback.
  - `series.missing` goes to the rules (via `earnings_known` and NaN `q`), the `## Missing inputs` section, and the B&H n/a.
  - `bh_na_reason` goes to the report text, and its NaN goes into `excess_vs_bh`.
- [x] **Every branch ends in a defined result.**
  - Unknown earnings/dividend/OI → a reason code (counted in the report's no-trade table / the screen's rejects). With every ticker rejected → `UNIVERSE EMPTY` banner.
  - B&H infeasible → `n/a (reason)`.
  - Scan date outside the holiday table → `ValueError` → CLI `error: …`, exit 2, with **no** state written (Deviation 2; checked with `python -m ccbot scan --date 2028-10-01` → `exit 2`).
  - Holiday Friday → Thursday expiry and symbols.
  - Weekly report with an unaffordable lot → n/a.
- [x] **No leftover TODOs or unused files.** `grep -rn "TODO\|FIXME" ccbot tests config` → no hits. The checked-in `reports/backtest_SYNTH_A_2026-10-30.md` was not regenerated (see Deviation 3).
- [x] **Missing-data policy grep** (`grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/`), 21 hit lines. Reason for each:
  - `costs.py:31` `else 0.0`: SEC fee applies to sells only (rule).
  - `screen.py:44` `pd.notna(earn) and`: **changed.** It is reached only for an ETF (no earnings) or a stock with a known date, because a blank date on a stock already returned `EARNINGS_UNKNOWN` on L42–43.
  - `report.py:60` `.get(code, 0)`: **new.** It counts days in V0's reasons dict, and a reason that never occurred is truly 0 days.
  - `report.py:200`, `backtest.py:167/170/171` `if len(...) else 0.0`: sums over zero fills (empty sum = 0).
  - `backtest.py:51` `else 0.0`: last row's next-day dividend. This is the allow-list entry from 005/03. With a missing `dividend` column, options are blocked by `DIVIDEND_UNKNOWN`, so this value is never used.
  - `backtest.py:107` `.get(d.reason, 0) + 1`: counter init.
  - `rules.py:187/280/282`: date/None guards (idempotence, first day, roll).
  - `rules.py:289` `next_earnings is not None and`: **now guarded.** It is reached only when `earnings_known` (or the asset is an ETF), so None means "no earnings in the data", not unknown.
  - `pricing.py:28–29`: expiry delta (rule).
  - `base.py:76`: no open calls → 0 (rule).
  - `sim.py:152`: None guard.
  - `synth.py:41–42`: generator values (synthetic data, by definition).
  - `bot.py:132`: None guard.
- **Finding (not fixed, out of plan scope; for A1):** `screen._reject` L28/L30 compare `price * 100 > capital − buffer`. If `capital` is NaN, both cap tests *pass*. `capital` = `equity(...)` turns NaN only while an option is held and the snapshot `iv` is blank (`snapshot.iv` row). In that case the bot already holds the shares, so no buy follows. Writing the tests as `not (… <= …)` would close it. Suggest a follow-up item under RI-002.

## Test output (pasted, not summarized)
Full suite:
```
$ python -m pytest -q -rs
.......................................................                  [100%]
=========================== short test summary info ============================
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'
126 passed, 1 skipped in 17.36s
```
Optional XNYS cross-check (scratch venv, `exchange_calendars==4.13.2`):
```
$ venv/bin/python -m pytest -q tests/test_calendar.py::test_table_matches_exchange_calendars
1 passed, 4 warnings in 1.11s
```
New and kept-green tests, verbose:
```
tests/test_missing_inputs.py::test_drop_each_input[csv.earnings] PASSED
tests/test_missing_inputs.py::test_drop_each_input[csv.dividend] PASSED
tests/test_missing_inputs.py::test_drop_each_input[csv.iv] PASSED
tests/test_missing_inputs.py::test_drop_each_input[snapshot.oi] PASSED
tests/test_missing_inputs.py::test_drop_each_input[snapshot.next_earnings] PASSED
tests/test_missing_inputs.py::test_drop_each_input[snapshot.ex_div_date] PASSED
tests/test_missing_inputs.py::test_drop_each_input[snapshot.iv] PASSED
tests/test_missing_inputs.py::test_drop_each_input[bh_benchmark] PASSED
tests/test_missing_inputs.py::test_drop_each_input[broker.div_next] PASSED
tests/test_missing_inputs.py::test_policy_lists_every_optional_input PASSED
tests/test_calendar.py::test_monthly_coverage_2016_2025 PASSED
tests/test_calendar.py::test_holiday_table_matches_nyse PASSED
tests/test_calendar.py::test_scan_calendar_raises_outside_table[today0] PASSED
tests/test_calendar.py::test_scan_calendar_raises_outside_table[today1] PASSED
tests/test_calendar.py::test_monthly_moves_to_thursday PASSED
tests/test_calendar.py::test_weekly_moves_to_thursday PASSED
tests/test_calendar.py::test_table_matches_exchange_calendars SKIPPED
tests/test_pricing.py::test_tolerance_finds_strike_on_bs_grid PASSED
tests/test_screen_bot.py::test_blank_oi_is_rejected_oi_unknown PASSED
tests/test_screen_bot.py::test_blank_earnings_stock_rejected_earnings_unknown PASSED
tests/test_screen_bot.py::test_scan_outside_holiday_table_changes_nothing PASSED
tests/test_screen_bot.py::test_pass_history_counts_last_10 PASSED
tests/test_report.py::test_daily_report_shows_pass_history PASSED
tests/test_report.py::test_early_close_banner_2026_12_24 PASSED
tests/test_report.py::test_bh_na_line_backtest PASSED
tests/test_report.py::test_bh_na_line_weekly PASSED
tests/test_backtest.py::test_no_option_sold_during_vol_warmup PASSED
tests/test_backtest.py::test_benchmark_cash_never_negative[feasible] PASSED
tests/test_backtest.py::test_benchmark_cash_never_negative[infeasible] PASSED
tests/test_backtest.py::test_all_variants_pass_account_invariants_infeasible_bh PASSED
tests/test_backtest.py::test_stock_csv_without_earnings_blocks_with_reason PASSED
tests/test_backtest.py::test_worked_example_50pct_exit PASSED
tests/test_data.py::test_absent_optional_columns_are_flagged PASSED
tests/test_webull_sandbox.py::test_sandbox_day_is_not_earnings_known PASSED
tests/test_webull_sandbox.py::test_occ_fallback_builds_thursday_symbols PASSED
tests/test_broker.py::test_bot_on_simbroker_matches_backtest_v0 PASSED
tests/test_webull_sandbox.py::test_contract_list_fallback PASSED
tests/test_cli.py::test_short_csv_reports_pbo_na_without_warnings PASSED
tests/test_variants.py::test_every_reason_code_is_produced PASSED
```

### Guardrails against the OLD code (scratch copy of `74cf949` + the new tests; the repo was not touched)
```
19 failed, 96 passed, 1 skipped, 1 error in 14.27s
test_backtest.py::test_benchmark_cash_never_negative[feasible|infeasible]   ImportError: cannot import name '_bh_cash'
test_backtest.py::test_stock_csv_without_earnings_blocks_with_reason       AttributeError: 'PriceSeries' object has no attribute 'missing'
test_calendar.py::test_holiday_table_matches_nyse                         ImportError (load_holidays)
test_calendar.py::test_scan_calendar_raises_outside_table[x2]             Failed: DID NOT RAISE ValueError
test_calendar.py::test_monthly_moves_to_thursday                          assert 2026-06-18 in [2026-04-17, 2026-05-15, 2026-06-19, 2026-07-17, 2026-08-21]
test_calendar.py::test_weekly_moves_to_thursday                           At index 0 diff: 2026-12-25 != 2026-12-24
test_data.py::test_absent_optional_columns_are_flagged                    AttributeError (missing)
test_report.py::test_daily_report_shows_pass_history                      AssertionError (line absent)
test_report.py::test_early_close_banner_2026_12_24                        AssertionError (banner absent)
test_report.py::test_bh_na_line_backtest                                  AssertionError (B&H table printed)
test_report.py::test_bh_na_line_weekly                                    AssertionError (forced 1 lot)
test_screen_bot.py::test_blank_oi_is_rejected_oi_unknown                  KeyError: 'SYNTH_A' (blank OI passed)
test_screen_bot.py::test_blank_earnings_stock_rejected_earnings_unknown   KeyError: 'SYNTH_B' (blank earnings passed)
test_screen_bot.py::test_pass_history_counts_last_10                      ImportError (pass_history)
test_variants.py::test_every_reason_code_is_produced                      AssertionError (new reason names)
test_webull_sandbox.py::test_sandbox_day_is_not_earnings_known            AttributeError: 'Day' object has no attribute 'earnings_known'
test_webull_sandbox.py::test_occ_fallback_builds_thursday_symbols         assert ([])
ERROR tests/test_missing_inputs.py                                         ImportError: cannot import name 'bh_na_reason'
```
For the guardrails that fail on import, here is the old behaviour itself (scratch, old code):
```
old B&H x1.5: s0 36.0 cash after buy -600.0 equity[0] 3000.0
old date,close load: dividend [0.0, 0.0] earnings [0, 0]
old scan_calendar(2028-10-01) raises? no (Mon-Fri fallback)
```
Also on the old code: `test_stock_csv_…` SYNTH_B without `earnings` gave `EARNINGS_BLACKOUT` 69 → 0 with options sold (005/03). The coverage, strike and 50%-exit tests (004, 008) pass on old code, as planned: they pin numbers and rules that were already right.

### Mutation checks (new code, one at a time, in a scratch copy, then discarded)
```
== else 0 in data.py
FAILED tests/test_data.py::test_absent_optional_columns_are_flagged
FAILED tests/test_missing_inputs.py::test_drop_each_input[csv.dividend]
2 failed, 123 passed, 1 skipped
== pd.notna(oi) and in screen.py
FAILED tests/test_missing_inputs.py::test_drop_each_input[snapshot.oi]
FAILED tests/test_screen_bot.py::test_blank_oi_is_rejected_oi_unknown
2 failed, 123 passed, 1 skipped
== max(1, in backtest.bh_lots
FAILED tests/test_backtest.py::test_benchmark_cash_never_negative[infeasible]
FAILED tests/test_missing_inputs.py::test_drop_each_input[bh_benchmark]
FAILED tests/test_report.py::test_bh_na_line_backtest
3 failed, 122 passed, 1 skipped
== max(1, in report.weekly_report
FAILED tests/test_report.py::test_bh_na_line_weekly
1 failed, 124 passed, 1 skipped
== monthly_slack_days 0
17 failed, 108 passed, 1 skipped   (incl. test_monthly_coverage_2016_2025, test_live_scan_rule_2026_10_30)
== scan_calendar without holidays
FAILED tests/test_calendar.py::test_monthly_moves_to_thursday
FAILED tests/test_calendar.py::test_weekly_moves_to_thursday
FAILED tests/test_webull_sandbox.py::test_occ_fallback_builds_thursday_symbols
3 failed, 122 passed, 1 skipped
== calendar built after advance (Deviation 2)
FAILED tests/test_screen_bot.py::test_scan_outside_holiday_table_changes_nothing
1 failed, 125 passed, 1 skipped
```
(These runs predate the last added test, so their totals are out of 125 + 1.)

### CLI commands (outputs written to scratch; `data/sample`, `reports/` and `state/` untouched)
```
$ python -m ccbot make-sample --out <scratch>/new-sample      -> 6 files; diff -r against data/sample: identical
$ python -m ccbot backtest --asof 2026-10-30 --out <scratch>  -> 96 configs in 16.6 s; exit 0
$ python -m ccbot scan --date 2026-10-30 --state-dir <scratch> --out <scratch>
2026-10-30 V0 BUY_SHARES OK SYNTH_A limit=24.1 status=FILLED
2026-10-30 V0 SELL_CALL OK SYNTH_A261218C00026000 limit=0.34 status=FILLED
$ python -m ccbot report --date 2026-10-30 ...                -> daily + weekly rebuilt; exit 0
$ python -m ccbot scan --date 2028-10-01 ...
error: holiday table covers 2026-01-01..2028-12-31; add NYSE dates for 2029 to holidays.json (source https://www.nyse.com/markets/hours-calendars)
exit 2
```
**Backtest report numbers: unchanged.**
- The SYNTH_A report against the old code's output: the `.csv` is byte-identical. The `.md` diff is only the new section:
  ```
  > ## Missing inputs
  > - none
  ```
  This is because SYNTH_A supplies every column and starts at $24 (100 sh = $2,400 ≤ $2,800), so B&H is feasible.
- Daily report diff: only the three new pass-history lines (`passed 1 of last 1 logged scans (history short: 1 < 10)` etc.).
- Weekly report: identical.
- Where numbers *do* change, by design (A1's case, SYNTH_A[:600] × 1.5, `--quick`):
  - Old: B&H `13.30% | 50.44% | -54.77% | 0.1844`; V0 `excess_vs_bh` 0.0512.
  - New: `n/a (100 shares cost more than cash − buffer)`; `excess_vs_bh` NaN.
  - The old numbers came from a benchmark at −$600 cash.

## Deviations from plan
1. **`Broker.quotes_have_oi` (not in the plan; I1 to confirm).**
   - With the planned `OI_UNKNOWN` check, `test_bot_on_simbroker_matches_backtest_v0` fails (`got == []`, verified in a scratch probe). Series-mode SimBroker quotes come from `model_quote`, which has no OI field, so every scan was `UNIVERSE_EMPTY`.
   - The plan says this test stays green and did not cover this case. The old code's comment ("model quotes carry no OI") shows `pd.notna(q["oi"]) and` was doing double duty.
   - Smallest fix that invents no OI value: a class attribute `Broker.quotes_have_oi = True`. `SimBroker` sets it False only in series mode. The bot passes it to `feasible_universe(..., require_oi=…)`. With False, a blank OI skips the OI test (the old behaviour, limited to model replay).
   - Snapshot-mode sim and the Webull sandbox keep True. `test_drop_each_input[snapshot.oi]` (sim snapshot path → `UNIVERSE_EMPTY`) and an added line in `test_sandbox_day_is_not_earnings_known` (`b.quotes_have_oi is True`) pin this.
   - If I1 prefers another route (e.g. dropping the screen from the replay test), this is a 4-line revert.
2. **Calendar built before `broker.advance` in `run_daily` (connectivity fix).**
   - As planned, a scan past the holiday table raised only *after* `SimBroker.advance` had saved the ledger at the new date. Every later scan on an earlier date would then be refused ("cannot go back").
   - `run_daily` now calls `broker.calendar(date)` first and reuses it for the screen.
   - New test: `test_scan_outside_holiday_table_changes_nothing`. It fails when the call is moved back after `advance`.
3. **Checked-in `reports/backtest_SYNTH_A_2026-10-30.md` not regenerated.** It is not in the plan's file list. Its numbers are unchanged, and it lacks only the new `## Missing inputs - none` section. Regenerate it with `python -m ccbot backtest --asof 2026-10-30` if wanted.
4. **Small choices inside the plan's wording:**
   - `(history short: k < 10)` prints the real k (e.g. `3 < 10`).
   - `PriceSeries.missing` names only `dividend`/`earnings`, as the plan's test (`== ("dividend", "earnings")`) requires. An absent `iv` keeps its existing labelled fallback (`csv.iv` row).
   - The `## Missing inputs` line for an ETF without `earnings` says "ETF: no earnings, nothing blocked".
   - `MISSING_POLICY["snapshot.iv"]` and `["broker.div_next"]` had no effect text in 005/03's table. I wrote what the code does: equity n/a while an option is held; a known gap with 0.0, pinned by its drop test.
5. **Process files** (`.claude/agents/*.md`, `templates/*.md`) were edited as the plan says. They are uncommitted and need the person's OK in PR review.
