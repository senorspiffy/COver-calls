# 04 Build plan - 046
Fit verdict: FIT
Fits a ~$3k account: test and policy text only; trading behaviour unchanged.
No open branch; built on main 941a2b4, same branch as 045 (no shared files).
## Extra research (with sources)
None needed.
## Files to create/change
ccbot/tickers.py; ccbot/missing.py; tests/test_missing_inputs.py
## Tests and checks
test_ticker_fields_cover_file_and_code; test_drop_each_input[tickers.asset_type], [tickers.last_earnings]; full suite; foo_date and new-`f.get` mutations in a scratch copy.
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | TICKER_FIELDS 5 keys, TICKER_NOTES |
| Map 2 | 2 policy rows + 2 drop functions in DROPS |
| Map 3 | test_ticker_fields_cover_file_and_code |
## Guardrail tests
- Missing inputs: tickers.asset_type → drop test (stock, earnings unknown → earnings_known False); tickers.last_earnings → drop test (no estimate)
## Expected result
Suite passes; the foo_date probe fails the new test.
Recurring issues checked (I1): RI-002, RI-007, RI-009, RI-010.
