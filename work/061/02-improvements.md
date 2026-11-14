# 02 Improvements - 061
## What past logs say
Read first: 057/03 ("Option prices match market: UNSUPPORTED"): every earlier replay used Black-Scholes
prices. RI-007 (every change in a work item). 057's kill rule: a variant that loses total return is parked.
## 3 ways FOR
1. Real quotes: bid/ask, IV and delta are what the market showed, so the spread cost is measured, not assumed.
2. Rules fixed in pass-criteria.md before any result; the bot rule uses the bot's own pickers (expiries.pick_expiry, pricing.pick_strike, tolerance [0.20, 0.35]) since the A1 fix of 2026-11-14. Not modelled: the cost-basis floor.
3. Walk-forward picks each 6-month block's variant from the prior 24 months, pooled across stocks (one pick, not 17).
## 3 ways AGAINST
1. Free data: Mon/Wed/Fri snapshots before Sep 2024 and one IV per expiry, not per strike.
2. 2020-2026 was mostly a rising market; covered calls are known to lag in rallies, so another period could differ.
3. 60 variants searched (weekly dropped: no 5-9 day expiries in the data); none beat holding on the median stock.
## Findings by language
Languages: N/A (internal backtest on downloaded data).
## Holes to watch out for (summary)
Spin-offs (T/WBD, PFE/Viatris) are not credited to either arm; daily drawdown curve uses Black-Scholes between snapshots. Both labelled in 01.
