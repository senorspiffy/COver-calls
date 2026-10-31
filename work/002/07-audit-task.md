# 07 Audit task - 002
For: A1. From: I3, 2026-10-30, after PASS on round 3 (see `06-verification.md`, "Re-verification 2").
Item: 002, Webull covered-call research bot (`ccbot/`). Offline, sim and sandbox only; live trading is not built. Research, not financial advice. Uncommitted, on branch `claude/webull-bot-002`.

## 1. Open as a BUG: 001 step 1, "ETF ≤ $28" gives an empty universe at $3k
- **Source:** R3, `work/002/03-handoff.md` §Error (L114). 001 step 1 allows one position "only on a diversified, liquid ETF priced ≤ $28" (($3,000 − $200)/100). On 2026-10-30 no diversified ETF ≤ $28 has liquid options at 0.25–0.30Δ. The ≤ $28 names that pass (KWEB, BITO, UNG, MSOS) are concentrated, and they pass only far OTM. So the rule as written yields an empty universe.
- **Guardrail (built in 002):** `screen.feasible_universe` runs on every scan and backtest. If it returns empty, the report shows a blocking "UNIVERSE EMPTY: rule X has no passing ticker" banner and no order is made. Tests: a $28-cap config with no passing ticker gives the banner and zero orders. The shipped default config must have ≥ 1 passing ticker on the bundled sample. `UNIVERSE_EMPTY` is covered in `tests/test_screen_bot`.
- **For A1:** open the BUG against 001. Check that the corrected step-1 rule carried in 03/04 has replaced the old wording in 001's docs, and that the guardrail test is listed with it.

## 2. recurring-issues: look-ahead in realised vol (fixed)
- **Bug:** the 04 plan said "first `rv_window` rows: forward-fill the first valid value". I2 built it as `rv.fillna(rv[first_valid])`, which filled rows 0..19 of any CSV without an `iv` column with a vol computed from later closes. The first trades on user data were priced with future data. It went untested because every backtest test fixture had an `iv` column.
- **Fix:** `data.realized_vol` is a trailing window only, NaN during warm-up. The new reason `VOL_WARMUP` blocks option entry on those days (shares can still be bought).
- **Guardrails:** `test_realized_vol_uses_only_past_closes` rewrites all closes after t, for every t, and `vol[0..t]` must not change. `test_no_option_sold_during_vol_warmup` also guards it. Reverting the fix makes 3 tests fail (shown in 06).

## 3. recurring-issues: PBO shown as 0.000 when it cannot be computed (fixed)
- **Bug:** with fewer than 8 non-held-out months (a user CSV shorter than about 2 years 8 months, because the last 2 years are held out), `pbo_cscv` took means of empty blocks. Those NaNs fell through `rank`/`log`, and `mean(nan <= 0)` became **0.0**, the best possible PBO, shown with only a numpy "Mean of empty slice" warning. The held-out config was also a tie-break pick made on zero train years.
- **Fix:** `pbo_cscv` returns NaN when T < S, N < 2 or R is non-finite. The report prints "n/a (needs …; have T months)". The held-out entry reads "not selected (no train years)", with n/a CAGR.
- **Guardrails:** `test_pbo_undefined_on_too_few_months[0,1,7]` (+ 24×1) and `test_short_csv_reports_pbo_na_without_warnings`, which runs with RuntimeWarning as an error. Reverting the fix makes 4 tests fail (shown in 06). The boundary is checked: 7 months → n/a, 8 months → 0.086.

## Shared root cause (record once in recurring-issues, linking 2 and 3)
**Missing data was silently turned into a value.** In #2, missing warm-up vol was filled with a later number. In #3, an empty sample became the score 0.0. Proposed standing rule (already in 04 Revision 2): *if a value or statistic cannot be computed from the data available at that point, it stays NaN/n/a and the code says why. It is never filled, defaulted or tie-broken into a number.* Proposed checks: grep for `fillna`/`bfill`/`nan_to_num`/`or 0` in review, and have each statistic tested on empty and too-short input. Fixtures should include a CSV without an `iv` column, and one shorter than the held-out window.

## Other things to look at (non-blocking)
- The PBO n/a reason text is fixed and doesn't name a non-finite R as the cause. Fixed variants (one config) also show "not selected"/n/a on short data, where a held-out CAGR could be reported.
- `buy_and_hold` uses `max(1, …)` lots, so the benchmark goes cash-negative when 100 shares cost more than the cash (the strategy waits instead).
- The Webull OCC-symbol fallback returns nothing for a holiday-moved Thursday expiry.
- The V2 fills test was reworked from a post-hoc ratio band to rule checks (Wed–Fri, unique weekly expiry, 5–9 DTE, V0 < V2 < 5×V0).
- Webull response field names are UNVERIFIED (05 deviation 9). k is UNCALIBRATED. Known limits are in 05 deviation 13.
