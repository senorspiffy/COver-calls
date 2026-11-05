# 01 Research brief - 046
## Question
Can the tickers.json enumeration test collect the keys itself, so an unlisted key fails?
## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- `TICKER_FIELDS = ("next_earnings", "ex_div_date", "dividend")` [ccbot/tickers.py L23]
- `enrich` reads `f.get("asset_type")`, `f.get("next_earnings")`, `f.get("last_earnings")`, `f["last_earnings"]`, `f.get("ex_div_date")`, `f.get("dividend")` [ccbot/tickers.py L46–55]
- config/tickers.json entries have keys asset_type, next_earnings, last_earnings, ex_div_date, dividend, sources [config/tickers.json]
- `sources` is documentation only: no code reads it [`grep -rn sources ccbot/` → none in tickers.py logic]
- A1 probe: extra `"foo_date": null` → tests/test_missing_inputs.py 20 passed [logs/audit/2026-11-05.md]
- No `asset_type` → `Day.asset_type` default `"stock"` [ccbot/rules.py L81]; a stock needs known earnings [ccbot/rules.py L296]
- No `last_earnings` and no `next_earnings` → `next_earnings None`, `earnings_known False` [tests/test_missing_inputs.py::drop_tickers_next_earnings]

Internal item: read `logs/recurring-issues.md` first (RI-002, RI-007, RI-009, RI-010).
## Numbers used (show the math)
Keys read by code or present in the file, minus `sources`: 5. In TICKER_FIELDS: 3. Missing: 2 (asset_type, last_earnings).
## Fit for a ~$3k account
Test and policy text only; trading behaviour unchanged.
## Open questions
None.
