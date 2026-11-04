# 04 Build plan - 041
Fit verdict: FIT
Fits a ~$3k account: Changes no caps; makes the paper bot fail safe on a stale date.
Built on `daily-fixes/2026-11-03` (PR #10), which changes `scripts/check_pipeline.py` too (item 034 rule).
## Extra research (with sources)
None needed; inputs are repo files and git.
## Files to create/change
ccbot/tickers.py; ccbot/missing.py; tests/test_missing_inputs.py; tests/test_paper.py
## Tests and checks
pytest on the changed test files; full suite; `python3 scripts/check_pipeline.py` on the repo; mutation in a scratch copy
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | `enrich`: `ex_div < day.date` → ex_div_date None, dividend/div_next stay NaN |
| Map 2 | `tickers.TICKER_FIELDS`; MISSING_POLICY rows `tickers.next_earnings`, `tickers.ex_div_date`, `tickers.dividend`; `snapshot.next_earnings` text names 040's estimate |
| Map 3 | drop tests for the 3 rows (incl. stale ex-date) |
## Guardrail tests
- test_enrich_past_ex_div_is_unknown; test_policy_lists_every_optional_input (tickers keys); test_drop_each_input[tickers.next_earnings, tickers.ex_div_date, tickers.dividend]
## Expected result
Every map step applied; full suite passes; `check_pipeline.py` → SKIPPED: none.
Recurring issues checked (I1): RI-002, RI-007, RI-009, RI-010.
