# 04 Build plan - 055
Fit verdict: FIT
Fits a ~$5k account: main $5k account unchanged; quality and weekly are pretend-money practice accounts.
## Extra research (with sources)
None beyond 01.
## Files to create/change
config/tickers.json; config/quality.json; config/weekly.json; tests/test_practice.py
## Tests and checks
Full suite; check_handoff 055; check_pipeline; VPS scratch scans before the daily run changes.
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | 4 tickers.json entries |
| Map 2 | quality.json |
| Map 3 | weekly.json trimmed |
| Map 4 | VPS step after merge (run_daily.ps1) |
## Guardrail tests
- test_quality_account_14_names_8000_each
- test_weekly_account_gives_each_stock_8000_and_has_facts
## Expected result
Full suite passes; 055 awaiting A1.
Recurring issues checked (I1): RI-001, RI-002, RI-007.
