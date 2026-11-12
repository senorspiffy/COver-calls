# 04 Build plan - 054
Fit verdict: FIT
Fits a ~$5k account: no change to the $5k account; this is a separate pretend-money account.
## Extra research (with sources)
None beyond 01.
## Files to create/change
config/tickers.json; config/weekly.json; tests/test_practice.py
## Tests and checks
Full suite; `check_handoff.py 054`; `check_pipeline.py`; scratch scan on the VPS before scheduling.
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | 6 tickers.json entries with sources |
| Map 2 | weekly.json |
| Map 3 | run command in 05; VPS script change after merge |
## Guardrail tests
- test_weekly_account_gives_each_stock_8000_and_has_facts
## Expected result
Full suite passes; 054 awaiting A1.
Recurring issues checked (I1): RI-001, RI-002, RI-007.
