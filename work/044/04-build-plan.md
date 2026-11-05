# 04 Build plan - 044
Fit verdict: FIT
Fits a ~$3k account: Process only; no trading, no cost.
Built on `daily-fixes/2026-11-03` (PR #10), which changes `scripts/check_pipeline.py` too (item 034 rule).
## Extra research (with sources)
None needed; inputs are repo files and git.
## Files to create/change
scripts/check_handoff.py; tests/test_handoff_check.py (or existing handoff test file)
## Tests and checks
pytest on the changed test files; full suite; `python3 scripts/check_pipeline.py` on the repo; mutation in a scratch copy
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | `check_all`: if no local 03 but an open branch has it → `IN PR (<branch>)` |
## Guardrail tests
- test_all_names_branch_with_handoff
## Expected result
Every map step applied; full suite passes; `check_pipeline.py` → SKIPPED: none.
Recurring issues checked (I1): RI-002, RI-007, RI-009, RI-010.
