# Work item 060
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-12

## What we want
The dip reserve (058, `dip_entry`) measures its high over the last 20 trading days, as the 057 B5 replay did, not over the last 20 recorded scans.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- 057/01 and 058/request: B5 opens "on a 5% dip below the 20-day high".
- `ccbot/bot.py` `_dip`: `past.tail(rule["lookback"] - 1)` takes the last 19 rows of this account's paper_snapshots.csv, so a skipped scan (the VPS reboot on 2026-11-12, or any missed 4:30 PM run) stretches the window past 20 trading days. config/dip_reserve.json `_about` says "20-scan high".
- The A/B paper test needs 100 trades matching the backtest; a different window drifts from what B5 was scored on.

## Done looks like
`_dip` keeps only closes whose `ts` falls in the last `lookback` trading days (`expiries.business_days` with config/holidays.json), `min_days` still counts recorded closes, and a test with a gap in the snapshots shows the old high drop out of the window. _about text updated.
