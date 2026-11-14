# 01 Research brief - 060
## Question
Does `_dip` (058) measure the same 20-day high as the 057 B5 replay, when scans are missed?

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
Internal item: no outside facts.
- F1. 057/01 and 058/request: B5 opens one position "on a 5% dip below the 20-day high" [work/057/01-research.md, work/058/request.md].
- F2. `ccbot/bot.py` `_dip` keeps `past.tail(lookback - 1)` rows of paper_snapshots.csv plus today: a count of recorded scans, with no date limit [ccbot/bot.py].
- F3. Scans are missed in practice: the VPS rebooted 2026-11-12 and the daily task needs it signed in (project notes); every missed scan widens the window by one trading day.
- F4. `ccbot.expiries.business_days(start, end, holidays)` and `config/holidays.json` (NYSE, covers 2026-01-01 to 2028-12-31) already give the trading-day calendar [ccbot/expiries.py, config/holidays.json].

## Numbers used (show the math)
With 3 missed scans in a month, the last 19 recorded scans + today span 23 trading days, not 20: a high from 21–23 days back still counts, which can trigger an entry B5 would not have taken.

## Fit for a ~$3k account
Paper-only $4k reserve account (dip_reserve.json); main account unchanged.

## Open questions
None.
