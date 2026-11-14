# 02 Improvements - 060
## What past logs say
058 (2026-11-12) built `_dip` on scan count; its test `test_lookback_drops_old_highs` writes one row per business day, so it can't tell scans from days. No recurring issue on this before.
## 3 ways FOR
1. The paper reserve then follows the same rule B5 was scored on (F1), which the 100-trade "matches the backtest" goal needs.
2. Missed scans (F3) no longer change which high counts.
3. Uses the calendar the bot already has (F4); no new data source.
## 3 ways AGAINST
1. Missed scans also mean fewer closes in the window; a dip high on a missed day is never seen. Keep `min_days` as a count of recorded closes so a thin window still blocks.
2. A date outside holidays.json would need the table; run_daily already raises there before any state changes (bot.py `broker.calendar`).
3. One more date filter to test; small.
## Findings by language
Languages: N/A (no new external claims): calendar arithmetic inside this repo.
## Holes to watch out for (summary)
Count trading days, not calendar days; today counts as day 1; keep `ts < today` for past rows.
