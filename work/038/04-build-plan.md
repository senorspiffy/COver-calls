# 04 Build plan - 038
Fit verdict: FIT
Fits a ~$3k account: no trading, no new costs, no brokerage connection.
## Extra research (with sources)
None needed; inputs are repo files and git.
## Files to create/change
scripts/check_pipeline.py; tests/test_pipeline_check.py; .claude/agents/a1-auditor.md
## Tests and checks
pytest tests/test_pipeline_check.py; full suite; `python3 scripts/check_pipeline.py` on the repo; mutation in a scratch copy
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | classify each open-branch item from the branch's own files; `BRANCH SKIPPED:` line; exit code unchanged |
| Map 2 | a1-auditor: BRANCH SKIPPED is an error, at top of report; never push to a branch you didn't open |
## Guardrail tests
- test_open_branch_item_that_skips_steps_is_reported
## Expected result
Every map step applied; full suite passes; `check_pipeline.py` → SKIPPED: none.
