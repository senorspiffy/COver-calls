# 04 Build plan - 010
Fit verdict: FIT
Fits a ~$3k account: no trading, no new costs, no brokerage connection.
## Extra research (with sources)
None needed; inputs are repo files.
## Files to create/change
ccbot/walkforward.py; tests/test_cli.py
## Tests and checks
test_short_csv_reports_pbo_na_without_warnings asserts `| V0 | V0 (fixed) | -1.94% |` and `| V4 | not selected (no train years) | n/a |`
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | walk_forward chosen_h |
## Guardrail tests
- n/a (EFFICIENCY; no filter rule or optional input)
## Expected result
Every map step applied; full suite passes.
