# 03 Research hand-off - 061
Status: READY
## Fact check
Each claim re-computed from `reports/real/*.csv` and `summary.json` (written by `python -m ccbot.realtest`).
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| Bot rule trails holding by a median 1.8 pts/yr | bot_rule_by_ticker.csv, bid rows, excess_cagr median -1.80 | VERIFIED |  |
| Drawdown cut by a median 1.8 pts | (cc_maxdd - bh_maxdd) median 1.81 | VERIFIED |  |
| BXM trailed SPY TR by 6.9 pts/yr | summary.json 7.93% - 14.80% = -6.87 | VERIFIED |  |
| Walk-forward median -2.7 pts/yr | walkforward_by_ticker.csv median -2.69 | VERIFIED |  |
| Walk-forward beat holding on 6 of 17 | excess_cagr > 0 on 5 tickers | WRONG | changed to 5 of 17 |
| 1,161 calls, IV > RV on 59%, mean P&L -0.31% of price | trades_*.csv (SPY excluded) 1161, 59.3%, -0.308% | VERIFIED |  |
| 38 early exercises | trades outcome early_assigned = 38 | VERIFIED |  |
| A2 6 of 17, A3 15 of 17 | bot_rule_by_ticker.csv | VERIFIED |  |
| "Sold IV" is per strike | DoltHub rows on one expiry share one `vol` | WRONG | relabelled "IV for the expiry" in 01 |
**Totals:** 9 rows checked → **7 VERIFIED as-is**, **2 fixed**, **0 removed**
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
| A2 needs half of 17 | ceil(17/2) | 9 > 6 → fail | ✓ |
| A3 needs 80% of 17 | 0.8 × 17 = 13.6 | 15 ≥ 14 → pass | ✓ |
| Totals | 7 + 2 + 0 = 9 | 9 | ✓ |
