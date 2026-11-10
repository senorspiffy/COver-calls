# 04 Build plan - 052
Fit verdict: FIT
Process only. Built on PR #16's branch (`daily-fixes/2026-11-09`; RULES BRANCH, and it changes `open_branches()` too), with today's main (96b7f94) merged in.
## Extra research (with sources)
None beyond 01.
## Files to create/change
1. scripts/check_pipeline.py (`open_branches`: merge-tree first, `changed()` helper with fallback, clash against `merge-base --all`; docstring)
2. tests/test_pipeline_check.py (1 test)
## Tests and checks
Full suite; `check_pipeline.py` exit 0 on this branch; on main a30101c with the new script, the PR #16 line reads `items 051` and RULES BRANCH names only scripts/check_pipeline.py; `check_handoff.py 052`.
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | file 1 `changed()`; test `test_criss_cross_branch_lists_only_its_own_changes` |
| Map 2 | file 1 clash loop; existing `test_same_id_on_main_and_open_branch_is_a_clash` |
| Map 3 | file 1 docstring |
## Guardrail tests
- `test_criss_cross_branch_lists_only_its_own_changes`: branch A (item 041 + a .claude/ edit) open; branch B cut from A adds item 042 and merges main; main merges A. B must show `items 042`, no RULES BRANCH for B. With the old `HEAD...ref` diff it fails (I3 mutation).
- Missing inputs: merge-tree failure → fallback path (I3 mutation: force fallback, old tests still pass).
## Expected result
Suite passes (207 + 1 skipped); today's false lines gone.
Recurring issues checked (I1): RI-011, RI-009, RI-007.
