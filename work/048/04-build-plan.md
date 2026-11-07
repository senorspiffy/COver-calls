# 04 Build plan - 048
Fit verdict: FIT
Fits a ~$5k account: main account at $5,000 (2 stocks, ≤ $2,500 each); practice account is pretend money, $5,000 per stock.
## Extra research (with sources)
None beyond 01.
## Files to create/change
config/tickers.json; config/practice.json; config/paper.json; tests/test_practice.py
## Tests and checks
Full suite; `check_handoff.py 048`; `check_pipeline.py`; a scratch practice scan on the VPS.
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | tickers.json entries with sources |
| Map 2 | practice.json, frac 1/13, cash 65,200 |
| Map 3 | paper.json cash 5000 |
## Guardrail tests
- test_every_universe_ticker_has_sourced_facts
- test_earnings_known_for_dec_18_on_2026_11_09
## Expected result
Full suite passes; 048 awaiting A1.
Recurring issues checked (I1): RI-001, RI-002, RI-007.
