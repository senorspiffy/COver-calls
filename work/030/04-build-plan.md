# 04 Build plan - 030
Fit verdict: FIT
Fits a ~$3k account: no trading, no new costs, no brokerage connection.
## Extra research (with sources)
None needed; inputs are repo files.
## Files to create/change
36 .pyc removed from the index; tests/test_pipeline_check.py
## Tests and checks
test_no_tracked_pycache
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | git rm --cached + test |
## Guardrail tests
- n/a (EFFICIENCY; no filter rule or optional input)
## Expected result
Every map step applied; full suite passes.
