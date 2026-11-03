# 04 Build plan - 036
Fit verdict: FIT
Fits a ~$3k account: no trading, no new costs, no brokerage connection.
## Extra research (with sources)
None needed; inputs are repo files and git.
## Files to create/change
.claude/commands/run-item.md; .claude/agents/i2-builder.md; .claude/agents/a1-auditor.md; scripts/check_pipeline.py (shared with 034)
## Tests and checks
pytest tests/test_pipeline_check.py; full suite; `python3 scripts/check_pipeline.py` on the repo; mutation in a scratch copy
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | run-item + i2: fix branches don't edit the file; status in 05/06 |
| Map 2 | a1 copies status on main |
| Map 3 | OPEN BRANCHES flags a branch that edits it (with 034) |
## Guardrail tests
- test_item_built_on_open_branch_is_in_pr_not_stuck (asserts the `edits logs/recurring-issues.md (item 036)` note)
## Expected result
Every map step applied; full suite passes; `check_pipeline.py` → SKIPPED: none.
