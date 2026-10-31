# 04 Build plan - 003 to 008 (combined)
Fit verdict: FIT WITH CHANGES (003, 004, 005, 007) · FIT (006, 008)

I1 wrote this on 2026-10-30. Inputs: `work/00{3..8}/03-handoff.md` (all READY), the requests, `logs/recurring-issues.md` (RI-001 and RI-002 ESCALATED, RI-003 and RI-004 OPEN), and `ccbot/` + `tests/` on `claude/bugfixes-003-008` at `74cf949` (baseline 93 passed). One plan covers six items, because they touch the same files. Each of `work/004…008/04-build-plan.md` points here. This is research, not financial advice. No live orders are involved.

Rule for I2: make the smallest change that closes each bug, plus its guardrail test. Nothing else. If a step does not fit the code, stop and write back to I1.

## Extra research (with sources)
1. **007 would break an existing test (R3 missed this).** `tests/test_broker.py::test_bot_on_simbroker_matches_backtest_v0` runs `run_daily` on SYNTH_A dates from 2016. `run_daily` → `feasible_universe` → `scan_calendar`. After 007 step 3, that call raises, because 2016 is outside the holiday table. A series replay also has to use the same calendar as the backtest (`ModelMarket`: `expiries.extend(series dates, last + 70 d)`), or the bot and the backtest drift apart. Fix: add `Broker.calendar(asof)`. The default is `scan_calendar(asof)`; `SimBroker` in series mode returns the series calendar (§007). The same pattern, `fridays(business_days(exp, exp))` → `[]` on a Thursday, also sits in `broker/sim.py` L66 and gets the same one-line fix. Source: code read plus `grep -rn "scan_calendar\|business_days" ccbot tests`.
2. **005 would break an existing test.** `tests/test_backtest.py::test_no_option_sold_during_vol_warmup` writes a `date,close` CSV (stock, with no dividend or earnings column) and asserts that options get sold. Under the 005 policy every entry would be `EARNINGS_UNKNOWN`. The test CSV must supply `dividend,earnings` columns of 0. That is a test-input change, not a weaker test. `tests/test_cli.py::test_short_csv_reports_pbo_na_without_warnings` (`date,close`, RuntimeWarning raised as an error) will now go down the all-NaN B&H path. It must stay green, so it is also the no-warning check for 005 and 006.
3. **Re-computed the numbers the new tests pin** (scratch run, repo code, Mon–Fri): 2016–2025 has 2,609 days. Strict 30–45 = 1,440. With slack = 2,483. Longest no-candidate run = 3. Picks ≤ 30 DTE = 642 (24.6%). All match 004/03. Strike cases: on an explicit $0.50 grid, 0.25–0.30Δ is empty for (24, .25), (17, .35), (12, .25) and holds 26.5 and 27.0 for (24, .50). `pick_strike(…, 0.275, (0.20, 0.35))` finds a strike in all four cases. Note: `pricing.strike_grid` switches to $1 steps at ≥ $25, so the test must build the $0.50 grid itself.
4. **Wording fix (004 step 3):** the 24.6% is a share of *days*, not of *entry days*. The 001 text below says "days".

## 003 – Account-size rule (RI-001)
**Fit: FIT WITH CHANGES.** (a) 001 gets a dated correction section and is not rewritten (§001 docs). (b) Pass history is read from `state/scans/*.json` on every scan, not only on Fridays.
- **Files:** `ccbot/screen.py`, `ccbot/bot.py`, `ccbot/report.py`, `tests/test_screen_bot.py`, `tests/test_report.py`.
- **Functions:**
  - `screen.pass_history(scans, ticker, k=10) -> (n_passed, n_seen)`. It looks at the last ≤ k scan dicts (oldest → newest) and counts those whose `passing` contains `ticker`. It never blocks.
  - In `bot.run_daily`, before the scan dict is written: `prior` = the scans in `state/scans/` with `stem < date`, sorted. Set `scan["pass_history"] = {t: list(pass_history(prior + [this_scan_core], t)) for t in cfg["universe"]}`, where `this_scan_core = {"passing": passing}`.
  - In `report.daily_report` § Screen, add one line per ticker: `- <t>: passed n of last k logged scans`, plus ` (history short: k < 10)` when k < 10. Use `scan.get("pass_history", {})`, so old scan files still render.
- **Tests:**
  - `test_screen_bot.py::test_pass_history_counts_last_10`: 12 scan dicts, the last 10 holding 4 passes → (4, 10). 3 scans → (n, 3). A `run_daily` on DATE still places the SELL_CALL when today passes.
  - `test_report.py::test_daily_report_shows_pass_history`: the "(history short" text is present with 3 scans and absent with 10.
- **Expected:** both new tests pass, and orders are unchanged. Step 1 of 001 states a screen result with today's feasibility (§001 docs).

## 004 – Expiry and strike rules (RI-001)
**Fit: FIT WITH CHANGES.** The code is unchanged. 001 gets a correction section. The strike test uses an explicit $0.50 grid.
- **Files:** `tests/test_calendar.py`, `tests/test_pricing.py` (+ 001 docs).
- **Tests (guardrail):**
  - `test_calendar.py::test_monthly_coverage_2016_2025`. Inputs: `business_days(2016-01-01, 2026-03-31)` (no holidays) and `third_fridays`. Over the days ≤ 2025-12-31, assert: total == 2,609; strict == 1,440; slack == 2,483; longest no-candidate run ≤ 3. Keep `test_monthly_coverage_on_synth_a`.
  - `test_pricing.py::test_tolerance_finds_strike_on_bs_grid`. Four cases (S, σ) = (24, .25), (17, .35), (12, .25), (24, .50), with T = 35/365, r .04, q 0, and the grid `[round(0.7S) + 0.5i]`. `pick_strike(…, 0.275, (0.20, 0.35))` is not None in all four, and the 0.25–0.30 band is empty in exactly 3.
- **Expected:** both tests pass on today's code. With `monthly_slack_days = 0` the coverage test fails. 001 steps 4, 5, 8, 11 and Alt. 1 state the bot's rule and cite these tests.

## 005 – Unknown earnings / OI / dividend (RI-002)
**Fit: FIT WITH CHANGES.** (a) Put the unknown checks after `VOL_WARMUP`/`NO_EXPIRY` and before the blackout. (b) Fix the warm-up test CSV (research 2). (c) The B&H n/a for a missing `dividend` column goes through 006's `bh_na_reason`.
- **Files:** `ccbot/missing.py` (new), `ccbot/rules.py`, `ccbot/data.py`, `ccbot/backtest.py`, `ccbot/screen.py`, `ccbot/broker/sim.py`, `ccbot/broker/webull_sandbox.py` (comment only), `ccbot/report.py`, `tests/test_missing_inputs.py` (new), `tests/test_screen_bot.py`, `tests/test_backtest.py`, `tests/test_data.py`, `tests/test_webull_sandbox.py`, `tests/test_variants.py`.
- **Functions:**
  - `rules.Day.earnings_known: bool = False`. `REASONS` += `EARNINGS_UNKNOWN`, `DIVIDEND_UNKNOWN`. In `_option_entry`, just before L283: if `day.asset_type != "etf" and not day.earnings_known` → `EARNINGS_UNKNOWN`; if `math.isnan(day.q)` → `DIVIDEND_UNKNOWN`.
  - `data.py`: add `OPTIONAL_CSV_COLUMNS = ("iv", "dividend", "earnings")` and `OPTIONAL_SNAPSHOT_FIELDS = ("oi", "next_earnings", "ex_div_date", "iv")`. L78–79: an absent column becomes NaN, with no `else 0`. `PriceSeries.missing: tuple = ()` names the absent columns. The row checks and `astype(int)` run only on supplied columns.
  - `backtest.build_days`: `earnings_known = "earnings" not in series.missing or asset == "etf"`.
  - `screen._reject`: on L36, add `if pd.isna(q["oi"]): return "OI_UNKNOWN"` before the value test. On L39, for a non-ETF, add `if pd.isna(earn): return "EARNINGS_UNKNOWN"` before the blackout. Add both to `TESTS`.
  - `sim.py` L58: `earnings_known = asset_type == "etf" or next_earnings is not None`.
  - `webull_sandbox.py` L144: add the comment `# earnings unknown → blocked (ccbot/missing.py)`.
  - `missing.py::MISSING_POLICY`: the 005/03 table as data. Keys: `csv.earnings`, `csv.dividend`, `csv.iv`, `snapshot.oi`, `snapshot.next_earnings`, `snapshot.ex_div_date`, `snapshot.iv`, `bh_benchmark`, `broker.div_next`. Each value is `(effect, reason_or_text)`.
  - Report: the backtest report gets `## Missing inputs`, one line per `series.missing` ("earnings: not supplied (n days blocked)"), or `none`. Daily Context: for a stock whose earnings are unknown, show `Days to earnings: n/a (not supplied)`.
- **Tests:**
  - `test_screen_bot.py::test_blank_oi_is_rejected_oi_unknown`
  - `test_screen_bot.py::test_blank_earnings_stock_rejected_earnings_unknown`
  - `test_backtest.py::test_stock_csv_without_earnings_blocks_with_reason`: SYNTH_B with the column dropped gives `EARNINGS_UNKNOWN` > 0, `EARNINGS_BLACKOUT` == 0, and 0 option sales.
  - `test_webull_sandbox.py::test_sandbox_day_is_not_earnings_known`
  - `test_data.py::test_absent_optional_columns_are_flagged`: `date,close` → `missing == ("dividend", "earnings")`, with no zeros.
  - Guardrail: `test_missing_inputs.py::test_drop_each_input[<key>]`, parametrised over `MISSING_POLICY`. For each key, drop that input and assert the named reason or n/a, with no exception and no invented number.
  - Guardrail: `::test_policy_lists_every_optional_input`. Every `csv.*` and `snapshot.*` key built from the two `OPTIONAL_*` tuples is in `MISSING_POLICY`.
  - `test_variants.py` L62: add the two new reasons to the expected set.
  - `test_backtest.py::test_no_option_sold_during_vol_warmup`: the CSV gets `dividend,earnings` columns of 0.
- **Expected:** the first five tests fail on today's code and pass after. Mutation check: putting back `else 0` (data.py) or `pd.notna(q["oi"]) and` (screen.py) makes ≥ 1 test fail. `test_shipped_config_has_a_passing_ticker` and the CLI no-warning test still pass.

## 006 – B&H never borrows (RI-002)
**Fit: FIT.** The map is followed as written.
- **Files:** `ccbot/backtest.py`, `ccbot/report.py`, `ccbot/__main__.py`, `tests/test_backtest.py`, `tests/test_report.py`.
- **Functions:**
  - `backtest.bh_lots(series, cfg)` = `floor((cash − buffer) / (s0·100))`, with no `max(1,`.
  - `bh_na_reason(series, cfg)` returns `"100 shares cost more than cash − buffer"` if lots == 0, `"dividend: not supplied"` if `"dividend" in series.missing` (005), else None.
  - `buy_and_hold` returns an all-NaN series on the same index when `bh_na_reason` is set. `_bh_cash(series, cfg)` gives the cash path, for the test.
  - `__main__.py` L66: `bh_m = metrics(bh, None, cfg); bh_m["na_reason"] = bh_na_reason(series, cfg)`.
  - `backtest_report` prints `n/a (<reason>)` under § Buy and hold when the reason is set.
  - `report.py` L168: `lots = int(...)` with no `max(1,`. If lots < 1, `bh_text = "n/a (100 shares cost more than cash − buffer)"`.
- **Tests (guardrail):**
  - `test_backtest.py::test_benchmark_cash_never_negative[feasible, infeasible]`: SYNTH_A, and SYNTH_A[:600] × 1.5.
  - `test_backtest.py::test_all_variants_pass_account_invariants_infeasible_bh`
  - `test_report.py::test_bh_na_line_backtest`
  - `test_report.py::test_bh_na_line_weekly`
  - Infeasible case: equity all NaN, no RuntimeWarning, grid `excess_vs_bh` NaN.
- **Expected:** these tests fail on today's code and pass after. Putting back `max(1,` at either line makes a test fail. The shipped SYNTH_A report is unchanged ($24 start).

## 007 – Exchange holidays (RI-003)
**Fit: FIT WITH CHANGES.** Two changes: `Broker.calendar()` and the `sim.py` L66 fix (research 1).
- **Files:** `config/holidays.json` (new), `ccbot/expiries.py`, `ccbot/broker/base.py`, `ccbot/broker/sim.py`, `ccbot/broker/webull_sandbox.py`, `ccbot/bot.py`, `ccbot/screen.py`, `ccbot/report.py`, `tests/test_calendar.py`, `tests/test_webull_sandbox.py`, `tests/test_report.py`.
- **Functions:**
  - `config/holidays.json`: `source` = https://www.nyse.com/markets/hours-calendars, `release` "NYSE Group, 2025-12-23", `checked` 2026-10-30, `covers` ["2026-01-01", "2028-12-31"].
    - 29 `holidays`: 2026-01-01, 01-19, 02-16, 04-03, 05-25, 06-19, 07-03, 09-07, 11-26, 12-25; 2027-01-01, 01-18, 02-15, 03-26, 05-31, 06-18, 07-05, 09-06, 11-25, 12-24; 2028-01-17, 02-21, 04-14, 05-29, 06-19, 07-04, 09-04, 11-23, 12-25.
    - `early_closes`: 2026-11-27, 2026-12-24, 2027-11-26, 2028-07-03, 2028-11-24 (kept out of `holidays`).
  - `expiries.business_days(start, end, holidays=None)`: None keeps Mon–Fri, otherwise `pd.bdate_range(freq="C", holidays=…)`. `load_holidays()` is cached. Add a comment on `_move_back` (≤ 4-day look-back).
  - `expiries.scan_calendar(today, days=120)` uses the holidays. It raises `ValueError` naming the covered range and the NYSE source when `today − 35` or `today + days` falls outside `covers`. It never falls back to Mon–Fri.
  - `Broker.calendar(self, asof)` (base, not abstract) returns `expiries.scan_calendar(asof)`. `SimBroker.calendar` in series mode returns `expiries.extend(series dates, last + 70 d)`, the same calendar as `ModelMarket`.
  - `bot.BrokerMarket` L26: `cal = broker.calendar(asof)`.
  - `screen.feasible_universe(cfg, snapshots, cash, asof, calendar=None)` → `_reject(..., calendar)`. None → `scan_calendar(asof)`. The bot passes `broker.calendar(date)`.
  - `webull_sandbox.py` L165: `exps = [e for e in expiries.fridays(expiries.scan_calendar(exp_from, days=(exp_to - exp_from).days + 7)) if exp_from <= e <= exp_to]`.
  - `sim.py` L66: the same filter over `self.calendar(self.date)`.
  - `bot`: `scan["early_close"] = date.isoformat() in load_holidays()["early_closes"]`. `daily_report` prints `> Early close today: 1:00 p.m. ET (1:15 p.m. for eligible options); run the scan before then.` when `scan.get("early_close")` is set.
- **Tests (guardrail RI-003):**
  - `test_calendar.py::test_holiday_table_matches_nyse`: the exact 29 + 5 sets.
  - `::test_scan_calendar_raises_outside_table`: 2028-10-01 and 2025-12-15.
  - `::test_monthly_moves_to_thursday`: 2026-05-20 → (06-18, False). 2027-06-17 is in the 2027-05-20 third Fridays.
  - `::test_weekly_moves_to_thursday`: 12-16, 12-17, 12-18 → (2026-12-24, True). 12-23 → (2026-12-31, True). 12-21 → None.
  - `::test_table_matches_exchange_calendars`: `importorskip`; `start` 2025-01-01, `end` 2029-01-31.
  - `test_webull_sandbox.py::test_occ_fallback_builds_thursday_symbols`: exp 2026-06-18 gives a non-empty result, all `260618`.
  - `test_report.py::test_early_close_banner_2026_12_24`
- **Expected:** the Thursday tests fail on today's code and pass after. `test_bot_on_simbroker_matches_backtest_v0`, `test_live_scan_rule_2026_10_30` and `test_contract_list_fallback` stay green. A1 then sets RI-003 to GUARDED and checks the paper log for `…261224…` on 12-16 to 12-18.

## 008 – 50% worked example (RI-004)
**Fit: FIT.** The map is followed. The code is unchanged.
- **Files:** `tests/test_backtest.py` (+ 001 docs, + the R3 line in the systemic section).
- **Test (guardrail):** `test_backtest.py::test_worked_example_50pct_exit`. Setup: V1, `Short("C", K, sold_on + 35 d, 1, 0.47, sold_on)`, and a stub market that returns one quote.
  - Ask 0.23 on day 9 → `BUY_TO_CLOSE` at 0.23.
  - Ask 0.24 on day 9 → `HAS_POSITION`.
  - Ask 0.23 on day 11 → `BUY_TO_CLOSE`.
  - Ask 0.23 on day 12 → `HAS_POSITION`.
- **Expected:** the test passes on today's code and pins that the 001 example agrees with `decide_exit`.

## Systemic guardrails (RI-001, RI-002 ESCALATED) – process files
**Why:** both guardrails failed because the rule lived only in one item doc (002/03, 002/04), and the stages that made the errors never read it. So the rule goes into the template fields and agent steps that run on every item. The code tests above are the part that can actually be executed. These edits are short and get reviewed in the PR. 013 (every R/I agent reads `recurring-issues.md`) is a separate item: leave it out, and leave the text below unchanged when 013 lands.

1. **`templates/research-handoff.md`**
   - Add a 6th map column, `Feasibility`, with this comment: `<!-- Required for every filter or window rule (universe/price/asset cap, liquidity, DTE, delta, weekday): "<n pass> of <n checked>, <date range>, <command or test>". 0 or blank → Status BLOCKED. Other steps: "–". -->`
   - Add a section `## Missing inputs` with a table `| Input (where it enters) | When absent | Reason code / report text |` and this comment: `<!-- Every optional input a step reads. Absent never means none, 0, a default or a pass. -->`
2. **`templates/build-plan.md`**
   - Add `## Rule trace`: `| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |`.
   - Add `## Guardrail tests`: `- Feasibility: <rule> → <test pinning its count>` and `- Missing inputs: <input> → <absent-case test>`.
3. **`.claude/agents/r3-fact-checker.md`**
   - Add to the end of step 1: "For every filter or window rule, compute its feasibility yourself (how many tickers/days/strikes pass, over which dates, with which command or test) and write it in the Feasibility column. Never write "always" or "every" without that count. If the count is 0 or not computed, the item is BLOCKED. Prefer selectors that always have a candidate ("nearest X within limits"), or state the empty-day result (a reason code, counted in the report). For every worked example, check that each step meets the rule it shows (thresholds, tick size, limits), not only the arithmetic."
   - New step 3a: "Fill the Missing inputs table. If a value cannot be computed from the data available at that point, it blocks with a named reason or shows n/a with why. It is never filled, defaulted or tie-broken into a number, a default lot or a pass."
4. **`.claude/agents/i1-reviewer.md`**
   - New step 1a: "Fill the Rule trace: every rule in 03, including correction sections, maps to a plan line or `DROPPED: <reason>`. Every filter or window rule needs a non-zero dated count in 03 and a planned test that pins it. Every optional input needs a planned absent-case test (missing-data policy, as in r3 step 3a). When code changes a rule the person follows (001: slack, tolerance, cap), the same plan updates that rule text, or a request is opened for it."
5. **`.claude/agents/i2-builder.md`**
   - Add to the connectivity check: "Missing-data policy: no check passes and no value is defaulted on absent or uncomputable data (NaN, None, 0, a default lot, a pass); it blocks with a reason or shows n/a. Before writing 05, run `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/`. Give each new or changed hit a one-line reason in 05. Record the real numbers from every feasibility test the plan names."
6. **`.claude/agents/i3-verifier.md`**
   - Add to step 3: "RI-001: re-run each feasibility test, and check that the number the rule text cites matches it. RI-002: put back one removed default (e.g. `else 0`), show that ≥ 1 test fails, then restore it. Check the grep reasons in 05. If the code changes a rule the person follows (001), check that the rule text changed in the same item or that a request is open for it."

These need the person's OK in PR review, as the 03s say. I2 makes the edits, and the PR description lists them separately.

## 001 docs: `work/001/03-handoff.md` (003, 004, 008)
History is kept. The old lines stay as they are. Two additions only:
- **Pointer** (insert after the "Rules marked **[house rule]**…" line, L116): `> **Corrected 2026-10-30** (items 003, 004, 008): steps 1, 3, 4, 5, 6, 8, 9(a), 11, Alternative 1 and the worked example's 50% line are superseded by § Correction 2026-10-30 below.`
- **Section** (insert before `## Alternative strategy ideas`):

```
## Correction 2026-10-30 (items 003, 004, 008)
Found by A1/R3 on 2026-10-30. The rows above are kept as written; where they differ, this section wins.
- **Step 1 (003).** At $3,000, trade **one** underlying that passes today's step-3 screen at the step-5 strike of the step-4 expiry and fits both caps: 100 sh ≤ cash − $200 (≤ $28/share) and, for a single stock, ≤ 50% of capital (≤ $15/share). Prefer a diversified ETF if one passes. **Feasibility, 2026-10-30:** 0 tickers confirmed on monthly quotes; no diversified ETF ≤ $28 passes (002/03 L114); F ($11.94, 39.8% of capital) passes only on an 11-06 weekly quote (003/03). Unproven until the paper bot logs monthly scans. If none passes: no trade that day (**UNIVERSE EMPTY**); options are (a) a CSP within the caps on a passing ticker, (b) add funds (two names from about $5.3k), (c) a covered-call ETF. The daily report shows how many of the last 10 logged scans each ticker passed (information, not a gate). [house rule] Check: `screen.feasible_universe` each scan; tests `test_universe_empty_blocks_orders`, `test_shipped_config_has_a_passing_ticker` (SYNTH data only), `test_pass_history_counts_last_10`.
- **Step 3 (005).** If OI or the next earnings date is unknown, the test fails (`OI_UNKNOWN`, `EARNINGS_UNKNOWN`); an ETF has no earnings.
- **Step 4 (004).** Monthly expiry with **30–45 DTE**; if none, the monthly nearest that window within 7 days of its edges (**23–52 DTE**, ties → later), logged `in_window = False`; if none, no trade that day (`NO_EXPIRY`), retry next scan. Feasibility (2016–2025, Mon–Fri, repo `pick_expiry`): 30–45 alone 55.2% of days; with slack 95.2%; at most 3 business days in a row without one. Example: 2026-10-30 → 2026-12-18, 49 DTE. No 0DTE; weekly rule unchanged. Check: DTE 23–52 and `in_window` logged; tests `test_monthly_coverage_2016_2025`, `test_live_scan_rule_2026_10_30`.
- **Step 5 (004).** Sell the listed call with delta **nearest 0.275**, only if in **[0.20, 0.35]**, else no trade (`NO_STRIKE_IN_TOLERANCE`). Strike ≥ cost basis: if the nearest is below basis, take the lowest strike ≥ basis if its delta ≥ 0.20, else no trade (`BASIS_ABOVE_BAND`). Why: at 35 DTE on a $0.50 grid adjacent strikes are 0.07–0.16Δ apart, so 0.25–0.30 was empty in 3 of 4 cases; it is logged as `in_band`. Limit at the mid as before. Check: delta in [0.20, 0.35], `in_band`, strike ≥ basis, fill vs mid; test `test_tolerance_finds_strike_on_bs_grid`.
- **Step 6 (008).** "first third of its life" means days held × 3 ≤ days of life (e.g. day ≤ **11** of 35, as the bot checks). The GTC buy-to-close limit is 50% of the sale price rounded **down** to the tick.
- **Step 8, Alternative 1 (004).** "30–45 DTE, ~0.25–0.30 delta" → the step-4 expiry and step-5 strike rule (put delta nearest −0.275, |Δ| in [0.20, 0.35]).
- **Step 9(a) (003).** Max 50% of capital in one single stock (≤ $15/share at $3k; `max_single_name_frac: 0.5`), not "only at ≥ $5.6k".
- **Step 11 (004).** Replace "another reason for 30–45 DTE" with: on about 25% of days (2016–2025) the step-4 rule picks 23–30 DTE, and those calls are not QCCs.
- **Worked example, 50% line (008).** Penny class ($0.01 tick below $3, Cboe C2023122104): 50% of $0.47 = $0.235, so the GTC limit is **$0.23** (48.9%). Day 9 quote $0.21 / $0.23 → fills at $0.23; profit (0.47 − 0.23) × 100 − $0.20 = **$23.80**; sell next month's call the same day. On $0.22 / $0.24 it would **not** fill (a buy limit executes only at the limit or lower, SEC Investor.gov), and the bot would not exit either. Non-penny ($0.05 tick): the sale would be $0.45 or $0.50 and the limit $0.20 or $0.25. Test `test_worked_example_50pct_exit`.
```
Check: `git diff work/001/03-handoff.md` shows only `+` lines. Every test named there exists and passes.

## Files to create/change
29 files: 13 code/config (`ccbot/` 12 incl. new `missing.py`, `config/holidays.json`), 9 tests (`test_calendar`, `test_pricing`, `test_screen_bot`, `test_report`, `test_backtest`, `test_data`, `test_webull_sandbox`, `test_variants`, new `test_missing_inputs`), 1 doc (`work/001/03-handoff.md`), 2 templates, 4 agent files. `config/default.json` and `README.md` are unchanged.

## Tests and checks
1. `python -m pytest -q`. Record the real total (baseline 93), which must include every test named above. `test_table_matches_exchange_calendars` may skip offline.
2. Mutation checks (one at a time, then revert): `else 0` in data.py; `pd.notna(q["oi"]) and` in screen.py; `max(1,` in backtest.py L121 and in report.py L168; `monthly_slack_days: 0`; `scan_calendar` without holidays. Each one makes ≥ 1 test fail.
3. The review grep (systemic §5) is run and each hit is given a reason in 05.
4. `python -m ccbot scan --date 2026-10-30` (sim) still sells `SYNTH_A261218C…`.

## Rule trace
| 03 rule | Plan line |
|---|---|
| 003/03 steps 1–4 | §003, §001 docs |
| 003/03 step 5(a)–(e) | Systemic §1, §3, §4, §6 ((e) is in §3) |
| 003/03 step 6 (`config/paper.json`) | DROPPED: out of scope per 03; A1 backlog after monthly paper scans |
| 004/03 steps 1–5 | §004, §001 docs; step 6 → Systemic |
| 005/03 steps 1–5, 6(a)–(c) | §005; 6(d) → §006; 6(e) → Systemic §3–§6 |
| 005/03 table row `broker.div_next` | Kept as a known gap in `MISSING_POLICY` (as 03 says); A1 opens an item |
| 006/03 steps 1–3 | §006; step 4 → §005 / Systemic |
| 007/03 steps 1–6 | §007 |
| 007/03 step 7 | §007 (skip-if-absent test) |
| 007/03 step 8 | A1 after I3 PASS (RI-003 → GUARDED, paper-log check) |
| 008/03 steps 1–3 | §008, §001 docs; step 4 → Systemic §3 |
| RI-001/RI-002 status in `logs/recurring-issues.md` | A1 after I3 PASS (not I2) |

## Expected result
- 001 tells the person the rules the bot actually runs: feasibility is dated, the cited tests exist, and the history is kept.
- Unknown earnings, OI or dividend blocks the trade, or shows n/a with a named reason. B&H never goes below $0 cash.
- Holiday-moved expiries get Thursday dates and symbols. The scan refuses to run past the holiday table rather than guess.
- The 50% example fills at $0.23 for $23.80.
- R3, I1, I2 and I3 each have a written feasibility check and a missing-data check, so a rule with no candidate, or a value defaulted from missing data, gets caught at each of the four stages.
