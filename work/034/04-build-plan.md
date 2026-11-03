# 04 Build plan - 034
Fit verdict: FIT
Fits a ~$3k account: no trading, no new costs, no brokerage connection.
## Extra research (with sources)
None needed; inputs are repo files and git.
## Files to create/change
scripts/check_pipeline.py; tests/test_pipeline_check.py; .claude/agents/a1-auditor.md; .claude/agents/i2-builder.md; .claude/commands/run-item.md; README.md
## Tests and checks
pytest tests/test_pipeline_check.py; full suite; `python3 scripts/check_pipeline.py` on the repo; mutation in a scratch copy
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | IN PR status for STUCK/not started/in progress items with more steps on an unmerged branch |
| Map 2 | OPEN BRANCHES line: items, merges cleanly / CONFLICTS, recurring-issues edit |
| Map 3 | a1 daily step: IN PR/OPEN BRANCHES on top; stack dependent fixes; i2 mutations in scratch copy |
## Guardrail tests
- test_item_built_on_open_branch_is_in_pr_not_stuck; test_open_branch_conflict_is_reported
## Expected result
Every map step applied; full suite passes; `check_pipeline.py` → SKIPPED: none.
