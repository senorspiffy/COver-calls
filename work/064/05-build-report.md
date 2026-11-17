# 05 Build report - 064
Built from work/064/04-build-plan.md (FIT WITH CHANGES, C1-C7). No deviations in code. One deviation in what mutation (i) is expected to fail (see Deviations).

Recurring issues checked (item 013): RI-001 and RI-002 (the two ESCALATED entries) and RI-007, RI-008, RI-010, RI-011, RI-012 (named in 04). No other entry is open.
- RI-001: WORK_CODE has a dated non-zero count. The repo walk in `test_work_code_counts_repo_diagnostics` finds `work/061/diag_keep.py`. The step-0 count over first-parent units is real (0 of 19, below).
- RI-002: every absent input ends in a defined line. A failed diff-tree gives an `UNTRACKED CHANGE` entry, and 062 does not repeat it as "none". No git gives `not checked (no git)`. A missing request.md is flagged. A failed branch `git diff` hides the code, and that is pinned as gap (l). No value is defaulted.
- RI-007: this item. The gate below plus the real-repo test (`061: complete`, exit 0).
- RI-008: `python3.11 -m py_compile` passes on both changed .py files.
- RI-010: the log line is written only with `--log`.
- RI-011: branch changes come from `changed()` (merge-tree result).
- RI-012: the match runs on whole paths with `fullmatch`. The negatives `diag.py.md` and `.pyc` are tested, and mutation (iii) fails on them.

RI-007: guardrail extended (064). A `.py` under work/<ID>/ now counts as code for UNTRACKED CHANGE (053) and RESEARCH CODE (062). It moves to GUARDED again when merged and an A1 probe on main (a RESEARCH ONLY item with 01 plus work/<ID>/diag.py in one commit) gives `RESEARCH CODE: <ID>`.
RI-012: holds (064 adds a path pattern with negative cases; mutation (iii) caught).

## Changes made (file: what changed)
`git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` -> 0 new
`git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` -> 4 changed
- scripts/check_pipeline.py:
  - Added `WORK_CODE = re.compile(r"work/\d{3}/.+\.py")` after RESEARCH_CODE_PATHS.
  - Added `_is_code(f, paths)` (startswith or `WORK_CODE.fullmatch`). `_research_code` and `untracked_changes` now call it.
  - The branch unit is now changed code + changed work/ .py files (`WORK_CODE.fullmatch`) + the tip's step files only (`if f in STEPS.values()`). Classify's `files[i]` is unchanged.
  - Docstring: gap (e) extended (only .py under work/; other script types not checked); (f) applies under work/ too; the 053 paragraph has the item-064 sentence and the deletion/move sentence; the 062 paragraph has the 064 branch-unit text, the note on (i), and new gaps (k) and (l).
- tests/test_pipeline_check.py:
  - The real-repo test now asserts `061: complete`.
  - Added 4 asserts in `test_research_code_rules`.
  - New tests: `test_work_code_pattern` (8 parametrized cases), `test_work_code_counts_repo_diagnostics`, fixtures (a)-(f) (`test_research_only_work_py_is_research_code`, `test_py_added_to_completed_item_is_untracked`, `test_open_full_item_covers_its_work_py`, `test_research_only_branch_work_py_is_branch_skipped`, `test_research_only_branch_nested_py_is_seen`, `test_branch_unchanged_tip_py_not_counted`), `test_failed_diff_tree_is_an_entry_not_none`, `test_work_code_without_git` and `test_branch_diff_failure_hides_code_gap_l`.
  - That is 11 new functions and 18 new collected tests (70 -> 88 in this file).
- .claude/agents/a1-auditor.md L20: the UNTRACKED CHANGE path list now includes "or a `.py` file under work/<ID>/ (item 064)". The last sentence now reads "...only logs/ and work/ markdown."
- .claude/commands/run-item.md:
  - L8: the code list in "writes no code" now includes "or a `.py` file under work/<ID>/; item 064".
  - L16: added "A diagnostic `.py` under work/<ID>/ is code too: commit it together with that item's step file (item 064)."
- Both .claude files are RULE_PATHS and need the person's OK in PR review.

## Step 0 gate
- Baseline: `git fetch origin`, then `python3 scripts/check_pipeline.py` on the unedited tree. Exit 0. Lines: `061: complete (FULL)`, `UNTRACKED CHANGE: none`, `RESEARCH CODE: none`, `SKIPPED: none`.
- After applying file 1 in the working tree: exit 0. `diff base.txt after.txt` -> IDENTICAL (the whole output, not only these lines).
- First-parent unit count:
```
for c in $(git rev-list --first-parent 694bf4d..HEAD); do f=$(git diff-tree -r --name-only --no-renames $c^1 $c); w=$(echo "$f" | grep -cE '^work/[0-9]{3}/.+\.py$'); k=$(echo "$f" | grep -cE '^(ccbot|config|scripts|tests|\.claude|templates)/'); ...; done
9fcc76a788da5221fb6b107a56a5f1d4eb4deaab work=1 code=19
units with only work/*.py code: 0
git rev-list --first-parent --count 694bf4d..HEAD -> 19
```
  Result: 0 of 19 units, as expected. The only unit with a work/ .py is the PR #26 merge (9fcc76a). It also changes 19 CODE_PATHS files and was already judged under 053.
- After all changes (before commit): `python3 scripts/check_pipeline.py` exit 0. Lines: `061: complete (FULL)`, `063: in progress (FULL: next 06)`, `064: in progress (FULL: next 05)`, `INCOMPLETE: none`, `UNTRACKED CHANGE: none`, `RESEARCH CODE: none`, `SKIPPED: none`.

## Feasibility numbers (real)
- WORK_CODE on the repo's work/ files: includes `work/061/diag_keep.py`; no `.md` hit (test passes).
- Fixtures: (a) flagged 1/1, (b) flagged 1/1, (c) 0/1, (d) 1/1, (e) nested 1/1, (f) unchanged tip .py 0/1. All are as the plan states.

## Connectivity check
- [x] every new function/rule is used: `WORK_CODE` is used by `_is_code` and the branch unit. `_is_code` is called from `_research_code` and `untracked_changes`. The rule text is in a1-auditor L20 and run-item L8/L16.
- [x] every input has a source, every output has a consumer: paths come from diff-tree (HEAD) and from `changed()`/ls-tree (branch). Results go to the existing `UNTRACKED CHANGE:`, `RESEARCH CODE:`, `<ID>: SKIPPED` and `BRANCH SKIPPED:` lines.
- [x] every branch ends in a defined result: no git -> "not checked (no git)" (tested); diff-tree failed -> 053 entry (tested); branch diff failed -> empty list, named gap (l) and pinned by a test; missing request.md -> flag (tested).
- [x] no leftover TODOs or unused files: no new files. Scratch copies were removed (my base.txt/after.txt/post.txt too). Other folders in the scratchpad (wt063*, after063*) belong to 063 and were not touched.
- Missing-data grep `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/` gives 36 hits, all existing. 064 changes no file in ccbot/. On the changed files' added lines (`git diff -U0`), the only hits are the two comment lines "...code for 053 and 062": "or 0" matches inside "for 053", and these are comments, not code.
- 014 patterns: no new dataclass fields. No new `>`/`<` comparison on numbers.

## Test output (pasted, not summarized)
`python3 -m pytest -q -p no:cacheprovider tests/test_pipeline_check.py`
```
........................................................................ [ 81%]
................                                                         [100%]
88 passed in 10.94s
```
`python3 -m pytest -q -p no:cacheprovider` (full suite)
```
........................................................................ [ 90%]
.............................                                            [100%]
316 passed, 1 skipped in 51.67s
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'
```
`python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py` -> no output, exit 0.

Mutations, each run on a scratch copy at /tmp/claude-0/-home-claude/424ac23c-1465-5ba3-87e0-711114225e56/scratchpad/mut (removed afterwards). `python3 -m pytest -q -p no:cacheprovider tests/test_pipeline_check.py`:
- (i) `_is_code` returns `f.startswith(paths)` only:
```
FAILED tests/test_pipeline_check.py::test_research_code_rules
FAILED tests/test_pipeline_check.py::test_work_code_pattern[work/061/diag_keep.py-True]
FAILED tests/test_pipeline_check.py::test_work_code_pattern[work/160/sub/x.py-True]
FAILED tests/test_pipeline_check.py::test_work_code_pattern[work/160/diag.py.md-False]
FAILED tests/test_pipeline_check.py::test_work_code_pattern[work/.gitkeep-False]
FAILED tests/test_pipeline_check.py::test_work_code_pattern[work/tmp/x.py-False]
FAILED tests/test_pipeline_check.py::test_work_code_pattern[work/160/01-research.md-False]
FAILED tests/test_pipeline_check.py::test_work_code_pattern[work/1600/x.py-False]
FAILED tests/test_pipeline_check.py::test_work_code_pattern[work/160/x.pyc-False]
FAILED tests/test_pipeline_check.py::test_research_only_work_py_is_research_code
FAILED tests/test_pipeline_check.py::test_py_added_to_completed_item_is_untracked
FAILED tests/test_pipeline_check.py::test_research_only_branch_work_py_is_branch_skipped
FAILED tests/test_pipeline_check.py::test_research_only_branch_nested_py_is_seen
13 failed, 75 passed in 11.09s
```
- (ii) L417 step part back to unfiltered `files[i]`:
```
FAILED tests/test_pipeline_check.py::test_branch_unchanged_tip_py_not_counted
1 failed, 87 passed in 11.25s
```
- (iii) `WORK_CODE` without its end anchor (`work/\d{3}/.+\.py.*`):
```
FAILED tests/test_pipeline_check.py::test_research_code_rules
FAILED tests/test_pipeline_check.py::test_work_code_pattern[work/160/diag.py.md-False]
FAILED tests/test_pipeline_check.py::test_work_code_pattern[work/160/x.pyc-False]
3 failed, 85 passed in 10.91s
```

## Deviations from plan
- Mutation (i): the plan expects only the positive pattern cases to fail. All 8 parametrize cases fail, because each case also runs the shared `_is_code("work/160/diag.py", RESEARCH_CODE_PATHS)` assert, as the plan places it. This is stricter than planned. Every test the plan names fails.
- Mutation (iii) also fails `test_research_code_rules` (its `diag.py.md` assert). The plan did not list it. This is consistent with the plan's intent.
- 063 interaction 3: no red line from either item. 063 shows `in progress (FULL: next 06)`.
