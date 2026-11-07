# 05 Build report - 046
## Changes made (file: what changed)
ccbot/tickers.py (`TICKER_FIELDS` 5 keys, `TICKER_NOTES`); ccbot/missing.py (rows `tickers.asset_type`, `tickers.last_earnings`); tests/test_missing_inputs.py (imports; `drop_tickers_asset_type`, `drop_tickers_last_earnings` in DROPS; `test_ticker_fields_cover_file_and_code`).
Same branch as 045; file counts there (3 of the 13 changed).
## Connectivity check
- [x] every new function/rule is used (both drop functions in DROPS, run by test_drop_each_input; TICKER_NOTES read by the new test)
- [x] every input has a source, every output has a consumer
- [x] every branch ends in a defined result (no asset type → "stock"; no last report → no estimate → EARNINGS_UNKNOWN when next is null)
- [x] no leftover TODOs or unused files
Missing-data grep: `grep -rnE "<i2 pattern>" ccbot/tickers.py ccbot/missing.py` → tickers.py L54, L57, L61 (`is not None and`: the stale guards and the "both known" test, unchanged from 041) and L63–64 (`else 0.0`, unchanged: reached only with a known future/today ex-date and amount); missing.py L13 is a comment. No new hit.
RI-002: guardrail built (046); GUARDED when merged and an unlisted key in config/tickers.json or ccbot/tickers.py fails a test.
## Test output (pasted, not summarized)
```
$ python3 -m pytest -q
194 passed, 1 skipped in 16.96s
```
Mutations (scratch worktree): `"foo_date": null` in F → 1 failed, 22 passed; extra `f.get("special_dividend")` in enrich → 1 failed; TICKER_FIELDS back to the 041 list → 1 failed. The A1 probe that passed on main now fails.
## Deviations from plan
None.
