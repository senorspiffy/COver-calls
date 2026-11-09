# 05 Build report - 051
## Changes made (file: what changed)
- scripts/check_pipeline.py: `MAIN = "origin/main"`; `main_ahead()` (commits on origin/main not in HEAD, 0 without origin/main); `open_branches()` skips origin/main and refs already in origin/main when HEAD is behind it; new `MAIN AHEAD: ... merge it before building (item 051)` line before OPEN BRANCHES; docstring entry. `next_id()` unchanged.
- tests/test_pipeline_check.py: `test_branch_behind_main_says_main_ahead`.
File counts: `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` → 0 new; `... | grep -c '^ M'` → 2 changed.
## Connectivity check
- [x] every new function/rule is used (`main_ahead` in `open_branches` and `main`)
- [x] every input has a source, every output has a consumer (MAIN AHEAD → the fixer and A1)
- [x] every branch ends in a defined result (no origin/main → 0, output as before)
- [x] no leftover TODOs or unused files
## Test output (pasted, not summarized)
```
$ python3 -m pytest -q
206 passed, 1 skipped in 16.57s
$ python3 scripts/check_pipeline.py   # on PR #15's head f74949a with this script (scratch)
MAIN AHEAD: origin/main has 2 commits not in HEAD; merge it before building (item 051)
(no OPEN BRANCHES block: origin/main and origin/claude/project-thread-rx7mt7 are left out)
$ python3 scripts/check_pipeline.py | tail -4   # this branch
INCOMPLETE: none
LOG TIME: none (not checked: 048: ... (item 049))
ORPHAN LOG: none
SKIPPED: none
$ python3.11 -m py_compile scripts/check_pipeline.py
ok
```
## Deviations from plan
None.
RI-009: 051 narrows OPEN BRANCHES to unmerged work only; IN PR, ID CLASH and --next-id unchanged.
