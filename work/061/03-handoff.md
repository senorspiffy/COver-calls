# 03 Research hand-off - 061
Status: READY
## Fact check
Each claim re-computed from `reports/real/*.csv` and `summary.json` (written by `python -m ccbot.realtest`).
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| Bot rule trails holding by a median 1.0 pt/yr | bot_rule_by_ticker.csv, bid rows, excess_cagr median -1.02 | VERIFIED |  |
| Drawdown cut by a median 1.7 pts | (cc_maxdd - bh_maxdd) median 1.69 | VERIFIED |  |
| BXM trailed SPY TR by 6.9 pts/yr | summary.json 7.93% - 14.80% = -6.87 | VERIFIED |  |
| Walk-forward median -1.1 pts/yr, beat holding on 8 of 17 | walkforward_by_ticker.csv median -1.13, 8 positive | VERIFIED |  |
| 942 calls, IV > RV on 59%, mean P&L -0.30% of price | trades_*.csv (SPY excluded) 942, 59.2%, -0.303% | VERIFIED |  |
| 20 early exercises | trades outcome early_assigned = 20 | VERIFIED |  |
| A2 8 of 17, A3 17 of 17, A4 0.062 vs 0.094 | bot_rule_by_ticker.csv | VERIFIED |  |
| Bot rule tested "exactly as configured" (A1 2026-11-13) | realtest._pick took the expiry nearest 37.5 DTE, delta +/-0.12 | WRONG | _pick now calls expiries.pick_expiry and pricing.pick_strike; test_pick_uses_the_bots_pickers |
| ATM IV beats next-30-day RV by ~1 vol pt | atm_iv_minus_next30d_rv median -0.001 | WRONG | 01 now says the average gap is about zero |
| "Sold IV" is per strike | DoltHub rows on one expiry share one `vol` | WRONG | relabelled "IV for the expiry" in 01 |
**Totals:** 10 rows checked → **7 VERIFIED as-is**, **3 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| – | No bot or config change. Rule ideas in 01 (0.15-0.20 delta, no rolling) wait for the person's decision | – | – | – | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| Option quotes for a ticker (load_ticker) | ticker skipped | summary.json `skipped`: "no option quotes" / "< 3.0 years" |
| BXM_History.csv (bxm_vs_spy) | benchmark not computed | summary.json bxm_vs_spy.error "BXM_History.csv missing" |
| volatility_history rows | ATM IV-vs-RV columns blank | column absent in bot_rule_by_ticker.csv |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| A2 needs half of 17 | ceil(17/2) | 9 > 8 → fail | ✓ |
| A3 needs 80% of 17 | 0.8 × 17 = 13.6 | 17 ≥ 14 → pass | ✓ |
| A5 limit -1.0 pt | -1.13 < -1.0 | fail | ✓ |
| Totals | 7 + 3 + 0 = 10 | 10 | ✓ |
