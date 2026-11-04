# 04 Build plan - 042
Fit verdict: FIT
Fits a ~$3k account: Process only; no trading, no cost.
Built on `daily-fixes/2026-11-03` (PR #10), which changes `scripts/check_pipeline.py` too (item 034 rule).
## Extra research (with sources)
None needed; inputs are repo files and git.
## Files to create/change
scripts/check_pipeline.py; tests/test_pipeline_check.py; work/040/request.md; .claude/commands/run-item.md; .claude/agents/a1-auditor.md
## Tests and checks
pytest on the changed test files; full suite; `python3 scripts/check_pipeline.py` on the repo; mutation in a scratch copy
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | FAST only as `FAST (person, YYYY-MM-DD)`; other FAST → SKIPPED |
| Map 2 | last `A1 result:` FAIL → `A1 FAIL` status + `A1 FAIL:` line, exit 1 |
| Map 3 | 040 request: `Scope: FAST (person, 2026-11-03)`; run-item/a1 text names A1 FAIL |
## Guardrail tests
- test_fast_needs_person_and_date; test_a1_fail_is_not_complete; test_later_a1_pass_clears_fail
## Expected result
Every map step applied; full suite passes; `check_pipeline.py` → SKIPPED: none.
Recurring issues checked (I1): RI-002, RI-007, RI-009, RI-010.
