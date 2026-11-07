# 04 Build plan - 049
Fit verdict: FIT
Process only; no strategy rule or account number changes. Does not conflict with open branches (none open; `check_pipeline.py` after `git fetch origin`: OPEN BRANCHES none).
## Extra research (with sources)
- `open_branches` computes `git diff --name-only HEAD...ref -- work/`; the same call with the rule paths gives the rules list (repo: scripts/check_pipeline.py). No new source needed.
## Files to create/change
1. logs/implementation/2026-11-07.md (048's I1/I2 fields; map 1)
2. scripts/check_pipeline.py (LOG_TIME_EXCEPT, RULES BRANCH, docstring; map 2, 3, 5)
3. tests/test_pipeline_check.py (3 tests; map 2, 3, 5)
4. .claude/commands/run-item.md (map 4)
5. .claude/agents/a1-auditor.md (map 4)
## Tests and checks
Full suite; `check_pipeline.py` on the branch (INCOMPLETE none, LOG TIME none with 048 named, exit 0); `check_handoff.py 049`.
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | file 1 |
| Map 2 | file 2 `LOG_TIME_EXCEPT`; test `test_log_time_exception_is_named_and_closed` |
| Map 3 | file 2 `open_branches` rules + `RULES BRANCH:` line; test `test_rules_branch_is_reported` |
| Map 4 | files 4, 5 |
| Map 5 | file 2 docstring; test `test_recommitted_log_line_is_checked_against_new_commit` |
## Guardrail tests
- RULES BRANCH: `test_rules_branch_is_reported` (branch editing `.claude/agents/x.md` → named; work/-only branch → none)
- LOG TIME exception: `test_log_time_exception_is_named_and_closed` (048 not flagged, named with reason; 150 still flagged; dict == {"048"})
- Missing inputs: git absent → existing `test_log_time_not_checked_outside_git` (no RULES BRANCH line)
## Expected result
Main after merge: `check_pipeline.py` exit 0; suite passes.
Recurring issues checked (I1): RI-010, RI-009, RI-007, RI-002.
