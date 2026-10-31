# 04 Build plan - 009
Fit verdict: FIT
Fits a ~$3k account: no trading, no new costs, no brokerage connection.
## Extra research (with sources)
None needed; inputs are repo files.
## Files to create/change
ccbot/walkforward.py (pbo_na_reason, pbo_na key); ccbot/report.py (PBO line); tests/test_walkforward.py; tests/test_cli.py
## Tests and checks
test_pbo_na_names_each_cause (4 cases); test_short_csv_reports_pbo_na_without_warnings; existing PBO tests
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | pbo_na_reason + key |
| Map 2 | report line |
## Guardrail tests
- n/a (EFFICIENCY; no filter rule or optional input)
## Expected result
Every map step applied; full suite passes.
