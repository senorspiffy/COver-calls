# 02 Improvements - 058
## What past logs say
Read first: RI-002 (no silent values), RI-007 (every change in a work item), TEST_LOG.md 100-trade rule.
## 3 ways FOR
1. Puts the two versions that beat buy-and-hold in 057 onto real Webull quotes.
2. Base and reserve are separate state dirs, the same model as the backtest's separate sleeve, so no shared-cash bug.
3. Both rules are config-only (per-ticker window, dip gate); no change for existing accounts.
## 3 ways AGAINST
1. 60-75 DTE monthlies may have wider spreads and get screened out more often.
2. The reserve waits 5 scans before it can enter, which is a startup gap the backtest didn't have.
3. With 7 stocks and $20k, the 100-trade bar may take months.
## Findings by language
Languages: N/A (internal design).
## Holes to watch out for (summary)
The dip rule must fail closed: with too little history it says so (NO_DIP) and never enters.
