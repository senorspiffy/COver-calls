# 04 Build plan - 051
Fit verdict: FIT
Process only. Built on PR #15's branch (`daily-fixes/2026-11-07`, RULES BRANCH: it changes scripts/check_pipeline.py too), with today's main merged in.
## Extra research (with sources)
None beyond 01.
## Files to create/change
1. scripts/check_pipeline.py (`open_branches` skip, `main_ahead()`, MAIN AHEAD line, docstring)
2. tests/test_pipeline_check.py (1 test)
## Tests and checks
Full suite; `check_pipeline.py` exit 0; `check_handoff.py 051`.
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | file 1 `open_branches`; test `test_branch_behind_main_says_main_ahead` |
| Map 2 | file 1 `main_ahead` + print; same test |
| Map 3 | `next_id` untouched; same test asserts `--next-id` |
## Guardrail tests
- `test_branch_behind_main_says_main_ahead` (main and a mirror branch not listed; MAIN AHEAD 1 commit; next-id counts main's ID; on main no MAIN AHEAD)
- Missing inputs: no `origin/main` → existing open-branch tests (their fixtures have origin/main merged into HEAD, so output unchanged)
## Expected result
Suite passes; on this branch before merging main, OPEN BRANCHES no longer lists origin/main.
Recurring issues checked (I1): RI-009, RI-007.
