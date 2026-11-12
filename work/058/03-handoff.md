# 03 Research hand-off - 058
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| F1 B4 windows | run_057.py via VPS session | VERIFIED |  |
| F2 B5 base | run_057.py via VPS session | VERIFIED |  |
| F3 dip rule | run_057.py via VPS session | VERIFIED |  |
| F4 reserve freed at call-away | run_057.py via VPS session | VERIFIED |  |
| F5 one window, no gate | ccbot/config.py, ccbot/bot.py | VERIFIED |  |
| F6 history in paper_snapshots.csv | ccbot/bot.py | UNSUPPORTED | "20 days" becomes "20 recorded scans", stated in config/dip_reserve.json |
**Totals:** 6 rows checked → **5 VERIFIED as-is**, **1 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | `monthly_dte_by_ticker` config + `for_ticker()`; used by screen, prefetch, entry | config | per-ticker window | test_for_ticker_uses_its_own_window, test_screen_checks_the_tickers_own_window | – |
| 2 | `dip_entry` config + `_dip()` gate on new entries only | paper_snapshots.csv, today's close | NO_DIP row or entry | test_no_dip_rule_until_enough_history, test_no_entry_without_a_5pct_dip, test_dip_opens_the_position, test_lookback_drops_old_highs | – |
| 3 | config/stagger.json, dip_base.json, dip_reserve.json | 057 rules | 3 accounts | test_budget_accounts_match_the_057_versions | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| Recorded closes (dip gate) | fewer than min_days | NO_DIP, "n of 5 closes recorded; dip rule not ready" |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Base + reserve | 16000 + 4000 | 20000 | ✓ |
| Base per stock | 16000 / 7 | 2285.71 | ✓ |
| Totals | 5+1+0=6 | 6 | ✓ |
