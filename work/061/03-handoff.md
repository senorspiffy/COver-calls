# 03 Research hand-off - 061
Status: READY
## Fact check
Each claim re-computed from `reports/real/*.csv` and `summary.json` (written by `python -m ccbot.realtest`). Rows marked "after re-run" were VERIFIED on the first run and changed when I2 re-ran the build of 061/04 on 2026-11-14.
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| Bot rule trails holding by a median 1.0 pt/yr | bot_rule_by_ticker.csv, bid rows, excess_cagr median -1.02; re-run 2026-11-14 (I2, 061/04 build): +0.30 | WRONG (after re-run) | 01 now says it beat holding by a median +0.3 pt/yr [-1.0] |
| Drawdown cut by a median 1.7 pts | (cc_maxdd - bh_maxdd) median 1.69; re-run 2026-11-14 (I2, 061/04 build): 0.78 | WRONG (after re-run) | 01 now says 0.8 pt [1.7] |
| BXM trailed SPY TR by 6.9 pts/yr | summary.json 7.93% - 14.80% = -6.87 | VERIFIED |  |
| Walk-forward median -1.1 pts/yr, beat holding on 8 of 17 | walkforward_by_ticker.csv median -1.13, 8 positive; re-run 2026-11-14 (I2, 061/04 build): median -2.2e-16 (0.0), 8 positive | WRONG (after re-run) | 01 now says median 0.0 pt/yr [-1.1], 8 of 17 |
| 942 calls, IV > RV on 59%, mean P&L -0.30% of price | trades_*.csv (SPY excluded) 942, 59.2%, -0.303%; re-run 2026-11-14 (I2, 061/04 build): 250, 63.2%, -0.083% | WRONG (after re-run) | 01 now says 250 calls, 63%, -0.08% (A1 still fails) |
| 20 early exercises | trades outcome early_assigned = 20; re-run 2026-11-14 (I2, 061/04 build): 3 | WRONG (after re-run) | 01 now says 3 of 250 [20 of 942] |
| A2 8 of 17, A3 17 of 17, A4 0.062 vs 0.094 | bot_rule_by_ticker.csv; re-run 2026-11-14 (I2, 061/04 build): A2 13 of 17, A3 17 of 17, A4 0.099 vs 0.094 | WRONG (after re-run) | 01 re-scores A2 pass, A3 pass, A4 pass |
| Bot rule tested "exactly as configured" (A1 2026-11-13) | realtest._pick took the expiry nearest 37.5 DTE, delta +/-0.12 | WRONG | _pick now calls expiries.pick_expiry and pricing.pick_strike; test_pick_uses_the_bots_pickers |
| ATM IV beats next-30-day RV by ~1 vol pt | atm_iv_minus_next30d_rv median -0.001 | WRONG | 01 now says the average gap is about zero |
| "Sold IV" is per strike | DoltHub rows on one expiry share one `vol` | WRONG | relabelled "IV for the expiry" in 01 |
**Totals:** 10 rows checked → **1 VERIFIED as-is**, **9 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| – | No bot or config change. Rule ideas in 01 (0.15-0.20 delta, no rolling) wait for the person's decision | – | – | – | – |
## Missing inputs
_Replaced (I2, 2026-11-14, after 061/04 build): the 8 rows of `ccbot/realtest.py` `REALTEST_MISSING`,
each tested by `tests/test_realtest.py::test_drop_input[<input>]`._
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| prices/T.csv (load_ticker) | ticker skipped | summary.json `skipped`: "prices: not supplied" |
| options/T.csv.gz (load_ticker) | ticker skipped (an empty file: "no option quotes"; < 3 years: "option quotes only ... (< 3.0 years)") | summary.json `skipped`: "options: not supplied" |
| dividends/T.csv (load_ticker) | ticker skipped (a NaN amount also skips) | summary.json `skipped`: "DIVIDEND_UNKNOWN: not supplied" |
| splits/T.csv (load_ticker) | ticker skipped (a 0-byte file = no splits) | summary.json `skipped`: "splits: not supplied" |
| earnings/T.csv (load_ticker) | no call sold on a stock; an ETF is unaffected | entry code EARNINGS_UNKNOWN (`rej_EARNINGS_UNKNOWN`); warning "earnings: not supplied" |
| volhist/T.csv (load_ticker) | ATM IV-vs-RV not computed | `atm_iv_minus_next30d_rv` NaN, `atm_na_reason` "volhist: not supplied" |
| BXM_History.csv (bxm_vs_spy) | benchmark not computed | summary.json bxm_vs_spy.error "BXM_History.csv: not supplied" |
| asset_type (config/tickers.json; SPY → etf) | treated as a stock (earnings required) | warning "asset_type: not in config/tickers.json ..." |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| A2 needs half of 17 | ceil(17/2) | 13 ≥ 9 → pass (re-run 2026-11-14; was 9 > 8 → fail) | ✓ |
| A3 needs 80% of 17 | 0.8 × 17 = 13.6 | 17 ≥ 14 → pass | ✓ |
| A5 limit -1.0 pt | 0.0 ≥ -1.0 (re-run 2026-11-14; was -1.13 < -1.0) | pass | ✓ |
| Totals | 1 + 9 + 0 = 10 | 10 | ✓ |
