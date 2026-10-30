# 06 Verification - 003 to 008 (combined)
Verdict: PASS (all six: 003 PASS · 004 PASS · 005 PASS · 006 PASS · 007 PASS · 008 PASS)

Written by I3 on 2026-10-30. Inputs: `work/00{3..8}/03-handoff.md`, `work/003/04-build-plan.md`, `work/003/05-build-report.md`, `logs/recurring-issues.md`, and the full `git status` and `git diff` on `claude/bugfixes-003-008` (base `74cf949`, uncommitted: the 29 planned files plus the 2 log files). Each of `work/004…008/06-verification.md` points here. I changed no code. Every old-code run and every mutation ran in scratch copies, never in the repo: `git status --porcelain` showed 61 lines before and after my runs. Nothing contacted a broker. This is research, not financial advice.

| Item | Bug / RI | Fix in place | Guardrail would have caught it | Verdict |
|---|---|---|---|---|
| 003 | 001 step 1 empty universe at $3k (RI-001) | 001 correction (dated feasibility: 0 confirmed), `pass_history` info line | Process: Feasibility column + R3/I1/I3 lines. Code: `UNIVERSE EMPTY` (002), pass count. See note | PASS |
| 004 | "30–45 always found", 0.25–0.30 band (RI-001) | 001 correction cites measured rule; code unchanged | `test_monthly_coverage_2016_2025` pins 1,440/2,483/2,609; the original "always" claim fails on old code | PASS |
| 005 | Missing earnings/OI/dividend → none/pass (RI-002) | `EARNINGS_UNKNOWN`, `OI_UNKNOWN`, `DIVIDEND_UNKNOWN`; `MISSING_POLICY` | 5 behaviour tests + `test_drop_each_input[9]` fail on old code; `else 0` / `pd.notna(oi) and` mutations fail | PASS |
| 006 | B&H forced 1 lot → cash −$600 (RI-002) | `bh_lots` (no `max(1,`), n/a with reason | `test_benchmark_cash_never_negative`, `test_bh_na_line_*`; `max(1,` mutation fails 3 tests | PASS |
| 007 | No holidays → 06-19/12-25 expiries, `[]` fallback (RI-003) | `config/holidays.json`, `scan_calendar` raises outside the table, `Broker.calendar`, Thursday fallback | 4 Thursday/table tests + OCC fallback test fail on old code; Mon–Fri mutation fails 3 | PASS |
| 008 | Worked example fill at $0.24, "day ≤ 12" (RI-004) | 001 correction ($0.23, $23.80, day ≤ 11) | `test_worked_example_50pct_exit`; the original example's two claims fail on old code | PASS |

## I1 audit (plan vs research)
The plan follows all six 03s. The rule trace (04 §Rule trace) maps every 03 step, including 003 step 6, which is `DROPPED` (out of scope per 03), and 007 step 8 (A1). I checked each addition. Each has a stated, sourced reason:
- **`Broker.calendar` and the sim.py L66 fix (research 1).** Correct: without them, `test_bot_on_simbroker_matches_backtest_v0` raises (2016 is outside the table).
- **Warm-up test CSV gets `dividend,earnings` = 0 (research 2).** This changes the test input, not the assertion. Accepted.
- **Explicit $0.50 grid in the strike test (research 3).** Correct: `strike_grid` switches to $1 at ≥ $25.
- **"entry days" → "days" (research 4).** Correct.
- **006 `bh_na_reason` adds "dividend: not supplied".** Sourced from the 005/03 policy table ("B&H n/a"). Accepted.
- **001 docs as a dated correction section, not a rewrite (FIT WITH CHANGES (a)).** This departs from the 03s' "replace L120", and it is stated with a reason (history kept). Accepted (see item 4 below).

**I1 miss (non-blocking, already handled by I2):** the plan said the replay test stays green under `OI_UNKNOWN`, but model quotes have no OI field. I2 caught it (Deviation 1).

## I2 audit (build vs plan)
I checked every file in `git diff` and the 3 new non-work files (`ccbot/missing.py`, `config/holidays.json`, `tests/test_missing_inputs.py`) against the plan's function list. They match apart from the deviations in 05, judged below. The 29-file count is right. The 001 correction section is byte-identical to the plan's block (`diff` → identical).

### (1) Deviation 1, `Broker.quotes_have_oi`: PASS
- **Where it can be False.** One assignment in `ccbot/`: `sim.py` L25, `self.quotes_have_oi = series is None`. The base class sets it True. `WebullSandboxBroker` never sets it, and it takes no constructor argument or config key for it. Nothing in `config/`, the CLI or `make_broker` touches it.
- **Series mode is not reachable from the CLI.** `cmd_scan` builds sim only with `snapshots=` (`__main__.py` L86–88). Webull's internal ledger is `SimBroker(cfg, ledger_path=…)`, with no series. So in every CLI/Webull/snapshot path, blank OI → `OI_UNKNOWN`. Series replay is used only by `tests/test_broker.py`.
- **Mutations (scratch, one at a time).** Each one makes a test fail:
  - base default `quotes_have_oi = False` → `test_sandbox_day_is_not_earnings_known` fails;
  - snapshot-mode SimBroker `= False` → `test_drop_each_input[snapshot.oi]` fails;
  - restoring `pd.notna(q["oi"]) and` → 2 tests fail.
- **Is it the RI-002 pattern?** It is still a pass on absent OI, but it is confined to BS model replay, where OI does not exist as a field. Those scans carry the MODELLED banner. It is not silent in code: it is named in `base.py` L109 and in the `feasible_universe` docstring. It is silent in the report, though: no line says "OI not checked". There is also no `MISSING_POLICY` row for it. Non-blocking; sent to A1 (07 §1).

### (2) Deviation 2, calendar before `advance`: PASS
- `run_daily` calls `broker.calendar(date)` (L106) before `broker.advance(date)` (L111), and passes that calendar to the screen. The only earlier branch is the already-scanned re-render, which changes no ledger.
- **Re-run myself.** I ran `scan --date 2026-10-30`, then `scan --date 2028-10-02` in the same scratch state dir. The second run printed `error: holiday table covers…` and exited 2. The ledger date stayed `2026-10-30`, and `scans/` still held only `2026-10-30.json`. A fresh state dir with 2028-10-01 → exit 2, and no state dir was created.
- **Mutation.** With the call moved to just after `advance`, `test_scan_outside_holiday_table_changes_nothing` fails (1 failed).
- **Later calls cannot raise mid-scan.** The Webull fallback's `scan_calendar(exp_from, span + 7)` stays inside the window that the top-level check already enforced (today − 35 … today + 120).

### (3) Agent and template edits: PASS (one style note)
- **Additions only.** No tool, permission or model lines changed. 013's scope (reading `recurring-issues.md`) was left out.
- **Names line up.** The Feasibility column, Missing inputs table, Rule trace and Guardrail tests exist in the templates that the agent lines name. The i2 grep is the exact pattern from 005/03 step 6(e).
- **The policy wording agrees** across r3 3a, i1 1a and i2.
- **The new i3 step 3 is workable.** I followed it in full for this item.
- **Style notes (non-blocking):**
  - r3 step 1 is now one 858-character paragraph, about 3.5× the longest line in r1/r2/a1. Splitting the feasibility and worked-example text into its own step 1b, like the new 1a/3a, would read better.
  - The i3 "put back one removed default" line should say "in a scratch copy", so nobody edits the repo.

### (4) `work/001/03-handoff.md`: PASS
- `git diff --numstat`: 14 added, 0 removed. The original rows, worked example and history are unchanged.
- One dated pointer line sits under the map header, plus `## Correction 2026-10-30 (items 003, 004, 008)`, which says "The rows above are kept as written; where they differ, this section wins".
- **Numbers re-computed** (repo `pick_expiry`, Mon–Fri 2016–2025): strict 55.2%, slack 95.2%, picks 23–52 DTE, ≤ 30 DTE on 24.6% of days ("about 25%"). Example 2026-10-30 → 2026-12-18 at 49 DTE (`test_live_scan_rule_2026_10_30`). All 7 tests the section names exist and pass.
- **The rule text matches the bot.** The section's 0.5 / [0.20, 0.35] / [30, 45] / 7 are the values in `config/default.json`. "day ≤ 11" matches `rules.py` (`days_held × 3 > life` → no exit). The step-3 text names the new `OI_UNKNOWN`/`EARNINGS_UNKNOWN` reasons, so the 005 code change to a 001 rule is reflected in the same item.

### (5) Safety: PASS
- **`--live` exits 3.** Re-run: exit 3 for `scan --live` (sim), for `--broker webull-sandbox --live`, and for webull-sandbox with `WEBULL_ENV` unset or set to `production` ("refused: …").
- **Sandbox only.** `dry_run=True` stays the default, and `cmd_scan` never passes it. `_assert_sandbox` still runs before any client is built and before every call. The diff touches `webull_sandbox.py` in only two places: a comment and the OCC fallback date filter. No host, endpoint, order path or `_DENY` line changed. The `conftest.py` socket block is unchanged.

### Deviations 3–5
Accepted. The checked-in `reports/backtest_SYNTH_A_2026-10-30.md` was not regenerated. My fresh run has a byte-identical `.csv`, and the `.md` differs only by `## Missing inputs / - none`.

### Review grep (i2 step)
The pattern gives 21 hit lines in `ccbot/`, the same 21 that 05 lists, each with a reason. I agree with each one. Two gaps sit outside the grep's reach (see 07 §2):
- broker `Day.q`/`dividend` default to 0.0, like `div_next`;
- NaN `capital` passes the cap tests (I2's finding).

## Tests re-run (output)
Full suite (repo, current tree):
```
$ python -m pytest -q -rs
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'
126 passed, 1 skipped in 17.70s
```
Optional XNYS cross-check (scratch venv, `exchange_calendars==4.13.2`, scratch copy of the tree):
```
$ venv/bin/python -m pytest -q tests/test_calendar.py
12 passed, 4 warnings in 0.71s
```
CLI (all output to scratch; `data/sample`, `reports/`, `state/` untouched):
```
make-sample --out <scratch>     -> exit 0; diff -r against data/sample: identical
backtest --asof 2026-10-30      -> 96 configs in 16.4 s; exit 0; .csv byte-identical to reports/; .md only + "## Missing inputs / - none"
scan --date 2026-10-30          -> BUY_SHARES OK SYNTH_A limit=24.1 FILLED; SELL_CALL OK SYNTH_A261218C00026000 limit=0.34 FILLED; exit 0
report --date 2026-10-30        -> daily + weekly; exit 0. Daily shows "SYNTH_A: passed 1 of last 1 logged scans (history short: 1 < 10)"
scan --date 2028-10-01          -> error: holiday table covers 2026-01-01..2028-12-31; add NYSE dates for 2029 ...; exit 2; no state dir
scan --date 2028-10-02 (after a 10-30 scan) -> exit 2; ledger date still 2026-10-30
scan --live / webull --live / WEBULL_ENV unset / =production -> "refused: ..."; exit 3 (x4)
```
### Guardrails against the OLD code (`git archive 74cf949` into scratch, plus the new tests)
```
20 failed, 96 passed, 1 skipped, 1 error in 14.58s
FAILED test_backtest.py::test_benchmark_cash_never_negative[feasible|infeasible]   (import _bh_cash)
FAILED test_backtest.py::test_stock_csv_without_earnings_blocks_with_reason
FAILED test_calendar.py::test_holiday_table_matches_nyse
FAILED test_calendar.py::test_scan_calendar_raises_outside_table[today0|today1]
FAILED test_calendar.py::test_monthly_moves_to_thursday
FAILED test_calendar.py::test_weekly_moves_to_thursday
FAILED test_data.py::test_absent_optional_columns_are_flagged
FAILED test_report.py::test_daily_report_shows_pass_history
FAILED test_report.py::test_early_close_banner_2026_12_24
FAILED test_report.py::test_bh_na_line_backtest
FAILED test_report.py::test_bh_na_line_weekly
FAILED test_screen_bot.py::test_blank_oi_is_rejected_oi_unknown
FAILED test_screen_bot.py::test_blank_earnings_stock_rejected_earnings_unknown
FAILED test_screen_bot.py::test_scan_outside_holiday_table_changes_nothing
FAILED test_screen_bot.py::test_pass_history_counts_last_10
FAILED test_variants.py::test_every_reason_code_is_produced
FAILED test_webull_sandbox.py::test_sandbox_day_is_not_earnings_known
FAILED test_webull_sandbox.py::test_occ_fallback_builds_thursday_symbols
ERROR  tests/test_missing_inputs.py   (import bh_na_reason)
```
This matches 05: 19 + 1 error, plus the ordering test that was added later. Some of these fail at import, so here is the old behaviour itself (`python -I` probe on the old copy):
```
006 old B&H: s0 36.0 cash after buy -600.0 equity0 3000.0
005 old SYNTH_B no earnings: EARNINGS_BLACKOUT 0 option sales 7
005 old blank OI: (['SYNTH_A'], {'SYNTH_B': 'SPREAD', 'SYNTH_C': 'PRICE_CAP'})     <- passes
007 old monthly June 2026: [2026-06-19]                                            <- a holiday
007 old weekly from 12-17: (2026-12-25, True)                                      <- a holiday
```
The 004 and 008 tests pass on old code by design, because they pin the code's real behaviour. To show they catch the original *doc* errors, I wrote each original claim as an assertion and ran it on the old code. All 3 fail, and the 3 real guardrail tests pass:
```
test_claim_004_30_45_always_found   assert False                       (55.2%, not "always")
test_claim_008_fill_at_024          'NONE' == 'BUY_TO_CLOSE'           (ask 0.24 > 0.235: no exit)
test_claim_008_day_12_allowed       'NONE' == 'BUY_TO_CLOSE'           (12 x 3 > 35)
3 failed, 3 passed
```
**003.** The 2026-10-30 universe claim is about real tickers, which the offline suite cannot test. Its guardrail is the process change (the Feasibility column is now required, with BLOCKED on a 0 or blank count) plus the existing `UNIVERSE EMPTY` gate. Had that column been in place, R3 would have had to write "0 of 11 diversified ETFs" next to step 1 and block the item. 001 now states 0 confirmed.

### Mutation checks (new code, scratch copy, one at a time, discarded)
```
else 0 (data.py)                         2 failed  (test_absent_optional_columns_are_flagged, drop_each_input[csv.dividend])
pd.notna(oi) and (screen.py)             2 failed  (drop_each_input[snapshot.oi], test_blank_oi_is_rejected_oi_unknown)
Broker.quotes_have_oi default False      1 failed  (test_sandbox_day_is_not_earnings_known)
SimBroker snapshot quotes_have_oi False  1 failed  (drop_each_input[snapshot.oi])
calendar after advance                   1 failed  (test_scan_outside_holiday_table_changes_nothing)
max(1, in bh_lots                        3 failed  (benchmark_cash_never_negative[infeasible], drop_each_input[bh_benchmark], bh_na_line_backtest)
scan_calendar Mon-Fri                    3 failed  (monthly/weekly_moves_to_thursday, occ_fallback_builds_thursday_symbols)
```

## Sent back / sent to Audit
Nothing is sent back. Sent to A1: `work/003/07-audit-task.md`, covering 003–008. It includes the non-blocking findings: the model-replay OI report line, the broker `q`/`dividend` gap, NaN capital, and the r3 step 1 length. None of these changes are committed; the process-file edits need the person's OK in PR review.
