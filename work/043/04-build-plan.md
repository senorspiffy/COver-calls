# 04 Build plan - 043
Fit verdict: FIT
Fits a ~$3k account: Process only; no trading, no cost.
Built on `daily-fixes/2026-11-03` (PR #10), which changes `scripts/check_pipeline.py` too (item 034 rule).
## Extra research (with sources)
None needed; inputs are repo files and git.
## Files to create/change
scripts/check_pipeline.py; tests/test_pipeline_check.py; templates/verification.md; .claude/agents/i3-verifier.md; .claude/agents/a1-auditor.md
## Tests and checks
pytest on the changed test files; full suite; `python3 scripts/check_pipeline.py` on the repo; mutation in a scratch copy
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | templates/verification.md: `Recurring issues checked:` and `check_pipeline line:` fields |
| Map 2 | check_pipeline `INCOMPLETE:` for items ≥ 041: 06 without a `Recurring issues checked:` line naming RI-, or a step file without its `| <agent> | <ID> |` log line; exit 1 |
| Map 3 | i3 step 0/2 and a1 name the new line |
## Guardrail tests
- test_incomplete_06_and_missing_log_line; test_complete_item_with_logs_is_not_incomplete
## Expected result
Every map step applied; full suite passes; `check_pipeline.py` → SKIPPED: none.
Recurring issues checked (I1): RI-002, RI-007, RI-009, RI-010.
