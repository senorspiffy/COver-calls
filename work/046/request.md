# Work item 046
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-05

## What we want
Every key the bot reads from `config/tickers.json` must have a `tickers.<key>` row in `MISSING_POLICY`, and a new key must fail a test until it has one.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `ccbot/tickers.py::TICKER_FIELDS = ("next_earnings", "ex_div_date", "dividend")` is a hand list. `enrich` also reads `f.get("asset_type")` and `f["last_earnings"]`, which are in neither `TICKER_FIELDS` nor `MISSING_POLICY`.
- A1 probe 2026-11-05, scratch copy of main d35ee66: add `"foo_date": null` to F in config/tickers.json → `python3 -m pytest -q tests/test_missing_inputs.py` → `20 passed`.
- 041/05 states the RI-002 GUARDED condition as "a new unlisted tickers.json key fails the enumeration test"; the probe shows it doesn't.
- Both unlisted keys fail safe today: no `asset_type` → `Day` default `"stock"` (earnings must be known); no `last_earnings` → no estimate → `EARNINGS_UNKNOWN`. So no wrong trade is possible now; the gap is in the guardrail.

## Root cause and prevention guardrail (BUG only)
Root cause: the enumeration test reads the list of inputs from a hand-kept tuple, not from the inputs themselves, so it can only catch what someone already remembered to list (the same gap as 014's Day defaults).
Guardrail: `test_policy_lists_every_optional_input` also collects every key of every entry in config/tickers.json and every key `enrich` reads (`f.get("<key>")` / `f["<key>"]` in ccbot/tickers.py), minus the non-input `sources`, and asserts each is in `TICKER_FIELDS`. Add `asset_type` and `last_earnings` to `TICKER_FIELDS` with policy rows and drop tests.

## Recurring issue link (RI-#, if any)
RI-002 (ESCALATED, 9): guardrail gap, no new occurrence.

## Done looks like
The `foo_date` probe fails a test; `tickers.asset_type` and `tickers.last_earnings` have rows and drop tests; the suite passes.
