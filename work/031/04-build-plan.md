# 04 Build plan - 031
Fit verdict: FIT
Fits a ~$3k account: no trading, no new costs, no brokerage connection.
## Extra research (with sources)
None needed; inputs are repo files.
## Files to create/change
scripts/check_pipeline.py; tests/test_pipeline_check.py; work/024/request.md; .claude/commands/run-item.md; templates/request.md; README.md
## Tests and checks
pytest tests/test_pipeline_check.py; probe in a scratch dir; check_pipeline on the repo
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | PERSON_ONLY = 03, 06; non-person waiver of them → SKIPPED |
| Map 2 | 024 waiver who-field → person (PR #6) |
| Map 3 | run-item.md, templates/request.md, README say it |
## Guardrail tests
- Waiver author: `test_fact_check_and_verification_waivable_only_by_person` (A1 waives 03+06, I3 waives 06 → SKIPPED); `test_waived_steps_are_excused_and_printed` (person waives 03; A1 waives 02 → complete)
## Expected result
Every map step applied; full suite passes; `check_pipeline.py` → SKIPPED: none.
