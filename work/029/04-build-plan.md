# 04 Build plan - 029
Fit verdict: FIT
Fits a ~$3k account: no trading, no new costs, no brokerage connection.
## Extra research (with sources)
None needed; inputs are repo files.
## Files to create/change
scripts/check_pipeline.py; tests/test_pipeline_check.py; .claude/commands/daily-audit.md; templates/daily-audit.md
## Tests and checks
test_stuck_after_one_day; script run
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | STUCK |
| Map 2 | docs |
## Guardrail tests
- n/a (EFFICIENCY; no filter rule or optional input)
## Expected result
Every map step applied; full suite passes.
