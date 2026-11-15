# 05 Build report - 066
Built on daily-fixes/2026-11-15 at 6c9aefb ("Item 066: I1 build plan (FIT WITH CHANGES)"). Item 065's step files (work/065/) were committed at 2cacdb7 before this build; at build start `git status --porcelain -uall` was empty, so no uncommitted 065 file was present during C2.

## Changes made (file: what changed)
- tests/test_pipeline_check.py (only file):
  1. `NO_GIT` moved from the item-053 block to just before `def _run` (plan Files 1). All existing `@NO_GIT` users resolve (90 collected, no NameError).
  2. New `_run_head(root, tmp, script, *args)` after `_run`: `git worktree add --detach -q <tmp>/head HEAD` with `cwd=root`, `assert add.returncode == 0, add.stderr`, `try: return _run(wt, ...)`, `finally: git worktree remove --force` (result not checked). The script stays `REPO/scripts` (working-tree copy), as the plan's research point 2 requires (Files 2).
  3. `test_repo_pipeline_has_no_skipped_items`: `@NO_GIT`, `tmp_path` param, body uses `_run_head(REPO, tmp_path, "check_pipeline.py")`, 3 asserts unchanged, new docstring (Files 3).
  4. New `test_head_run_ignores_uncommitted_item` right after `_history`: control run sees `INCOMPLETE: 151`; HEAD run shows `INCOMPLETE: none` and code 0; worktree list has no `<tmp>/head` (Files 4). The `code == 0` assert held, so nothing was dropped.
  5. The 3 constant `_is_code` asserts moved unchanged from `test_work_code_pattern` into new `test_is_code_examples`; the pattern test keeps 8 cases and 2 asserts (Files 5).

File counts (012):
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` → 0 new
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` → 1 changed

## Connectivity check
- [x] every new function/rule is used: `_run_head` is called by `test_repo_pipeline_has_no_skipped_items` and `test_head_run_ignores_uncommitted_item`; `NO_GIT` is used by both plus the existing 053+ tests.
- [x] every input has a source, every output has a consumer: input = HEAD of REPO (or fixture repo); output = check_pipeline stdout/code consumed by the asserts. Uncommitted files remain covered by the in-tree run-item.md L14 run (C9), as the docstring says.
- [x] every branch ends in a defined result: no git → skip "git not on PATH"; worktree add fails → AssertionError with git stderr (absent case measured below); removal fails → not asserted in `finally`, visible in `git worktree list` (C7). No fallback to REPO.
- [x] no leftover TODOs or unused files: `git diff | grep -nE "^\+.*(: float = 0|TODO)"` → no hits; scratch worktree /tmp/claude-0/wt066 and scratch dirs removed (`git worktree list` shows only the main tree).
- Missing-data grep (`grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/`): 36 hits, all pre-existing; `git diff --stat -- ccbot/` is empty, so 0 new or changed hits. No new dataclass field and no new `>`/`<` test (014).

## Test output (pasted, not summarized)
Base (before edits, at 6c9aefb):
```
316 passed, 1 skipped in 44.05s
88 tests collected in 0.02s
```
C1 `python3 -m pytest --collect-only -q tests/test_pipeline_check.py`:
```
90 tests collected in 0.10s
```
C2 full suite `python3 -m pytest -q -p no:cacheprovider` (target was base 316 + 2):
```
318 passed, 1 skipped in 47.65s
```
Pass count vs the request: +2 (one filter pin T2, one split test); 0 cases merged away.

C3 mutation A (scratch worktree /tmp/claude-0/wt066, `_run_head` body → `return _run(root, script, *args)`):
```
>       assert "INCOMPLETE: none" in out, out
E       AssertionError: 150: complete (FULL)
E         151: in progress (FULL: next 02)
E         INCOMPLETE: 151 (no log line for R1)
FAILED tests/test_pipeline_check.py::test_head_run_ignores_uncommitted_item
1 failed, 89 passed in 12.23s
```
C4 mutation (i) (`_is_code` → `return f.startswith(paths)`, scratch worktree):
```
FAILED tests/test_pipeline_check.py::test_research_code_rules - assert (0 == 1)
FAILED tests/test_pipeline_check.py::test_work_code_pattern[work/061/diag_keep.py-True]
FAILED tests/test_pipeline_check.py::test_work_code_pattern[work/160/sub/x.py-True]
FAILED tests/test_pipeline_check.py::test_is_code_examples - AssertionError: ...
FAILED tests/test_pipeline_check.py::test_research_only_work_py_is_research_code
FAILED tests/test_pipeline_check.py::test_py_added_to_completed_item_is_untracked
FAILED tests/test_pipeline_check.py::test_research_only_branch_work_py_is_branch_skipped
FAILED tests/test_pipeline_check.py::test_research_only_branch_nested_py_is_seen
8 failed, 82 passed in 13.19s
```
Matches the plan (8 failed / 82 passed); T2 did not fail.

C5 probe (b) in the scratch worktree (REPO = that tree), uncommitted `work/999/request.md` (Scope FULL) + `01-research.md`, no R1 line:
```
== C5 new body
1 passed, 89 deselected in 1.07s
== C5 old body (HEAD's test file)
E         INCOMPLETE: 999 (no log line for R1)
1 failed, 87 deselected in 0.59s
```
This also confirms research point 4: inside a linked worktree, `HEAD` is that worktree's HEAD.

C6 `git status --porcelain -uall` before vs after C2: `diff` → IDENTICAL (both: ` M tests/test_pipeline_check.py`).

C7 `git worktree list` after C2:
```
/home/claude/cover-calls  6c9aefb [daily-fixes/2026-11-15]
```
C8 durations:
```
0.59s call     tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
0.20s call     tests/test_pipeline_check.py::test_head_run_ignores_uncommitted_item
```
Both under 2 s.

Absent case (Guardrail tests): `_run_head(<empty dir /tmp/claude-0/empty066>, ...)`:
```
AssertionError: fatal: not a git repository (or any of the parent directories): .git
```
C9 in-tree `python3 scripts/check_pipeline.py` (after this file and its log line), rc=0:
```
066: in progress (FULL: next 06)
STUCK: none
INCOMPLETE: none
LOG TIME: none (not checked: 048: built before 045's --log rule reached main; times typed by hand, not recoverable (item 049))
UNTRACKED CHANGE: none
RESEARCH CODE: none
SKIPPED: none
```
Log line written: `23:38 | I2 | 066 | 1 files changed | tests 318/319` (319 = 318 passed + 1 skipped).

## Deviations from plan
None. The plan's line numbers were off by a few lines (e.g. `NO_GIT` was at L599, `_history` ended at L627), but every anchor text matched exactly once.

Recurring issues checked (item 013): RI-001 (ESCALATED): the new filter has a suite pin (T2) with a control assert proving the fixture triggers (count 1, not 0), and mutation A fails it (C3). RI-002 (ESCALATED): no missing input passes. No git → skip with a reason; git failure → AssertionError with stderr (measured); no REPO fallback. RI-006: all counts above come from commands. RI-008: 3.10-safe syntax, no new imports; `test_every_py_compiles_on_oldest_python` passed in C2. RI-009: mutations only in the scratch worktree /tmp/claude-0/wt066 (removed); in REPO, only `worktree add/remove` ran via the tests, and status was unchanged (C6). RI-010: this file was written before its `--log` line, which went through check_pipeline.py. RI-003, RI-004, RI-005, RI-007, RI-011, RI-012: not applicable (no calendar, price example, scope rule change, branch diff or error-text parsing).
RI-001: ESCALATED, unchanged (this item adds a pinned filter test; A1 decides any status change on main).
