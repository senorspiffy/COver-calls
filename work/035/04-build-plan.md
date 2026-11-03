# 04 Build plan - 035
Fit verdict: FIT
Fits a ~$3k account: no trading, no new costs, no brokerage connection.
## Extra research (with sources)
None needed; inputs are repo files and git.
## Files to create/change
scripts/check_pipeline.py; tests/test_pipeline_check.py
## Tests and checks
pytest tests/test_pipeline_check.py; full suite; `python3 scripts/check_pipeline.py` on the repo; mutation in a scratch copy
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | replace date cutoff with closed PRE_A1_LINE list |
| Map 2 | test updated |
## Guardrail tests
- test_complete_needs_a1_result
## Expected result
Every map step applied; full suite passes; `check_pipeline.py` → SKIPPED: none.
