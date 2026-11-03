# 04 Build plan - 039
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
| Map 1 | append `; last commit <date> (<n> days)` to each OPEN BRANCHES line, n to --today |
## Guardrail tests
- test_open_branch_line_shows_last_commit_age
## Expected result
Every map step applied; full suite passes; `check_pipeline.py` → SKIPPED: none.
