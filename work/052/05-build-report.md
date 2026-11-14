# 05 Build report - 052
## Changes made (file: what changed)
- scripts/check_pipeline.py `open_branches()`: merge-tree now runs first; new `changed(*paths)` = `git diff --name-only HEAD <merge-tree tree>`, falling back to `HEAD...ref` when merge-tree fails (git < 2.38); items, the item-036 note and RULES BRANCH use it. ID CLASH checks the request against every `merge-base --all` base. Docstring: OPEN BRANCHES items are what a merge would change (item 052).
- tests/test_pipeline_check.py: `test_criss_cross_branch_lists_only_its_own_changes` (two merge bases, commit dates as on 2026-11-07..10).
File counts: `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` → 0 new; `... | grep -c '^ M'` → 2 changed.
## Connectivity check
- [x] every new function/rule is used (`changed` for items, recurring, rules; `bases` in the clash loop)
- [x] every input has a source, every output has a consumer (OPEN BRANCHES / RULES BRANCH → A1 and the fixer)
- [x] every branch ends in a defined result (no merge tree → old `HEAD...ref` diff; no merge base → no clash, as before)
- [x] no leftover TODOs or unused files
## Test output (pasted, not summarized)
```
$ python3 -m pytest -q
207 passed, 1 skipped in 21.45s
$ python3 scripts/check_pipeline.py   # on origin/main 96b7f94 with this script (scratch worktree)
OPEN BRANCHES (not merged into HEAD):
  origin/daily-fixes/2026-11-09: items 051; merges cleanly; last commit 2026-11-09 (1 days)
RULES BRANCH: origin/daily-fixes/2026-11-09 changes scripts/check_pipeline.py; build new items on top of it (item 049)
ID CLASH: none
$ python3.11 -m py_compile scripts/check_pipeline.py
ok
```
## Deviations from plan
The first test version passed with the old diff too: its commits shared one timestamp, so git picked the other merge base. Commit dates were set like the real history (main's daily commit newer), and the test then fails with the old diff (06).
RI-011: guardrail built (052); GUARDED when merged and the criss-cross test fails with the old diff.
RI-009: OPEN BRANCHES still lists every unmerged branch; only its file lists are now taken from the merge result.
