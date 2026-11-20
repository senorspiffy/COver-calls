# 05 Build report - 079
Built on HEAD 32b16fb (daily-fixes/2026-11-19; 075-078 built). Uncommitted; the orchestrator commits.

## Changes made (file: what changed)
- scripts/check_pipeline.py
  - New `SHALLOW_LINE` (40 or 64 lowercase hex, `fullmatch`), placed next to `UNTRACKED_FROM`.
  - New `_note(cutoff)`. `_walk` and `untracked_changes` call it instead of their inline copies; the text is unchanged.
  - New `_shallow_boundaries()`, placed just before `_walk`. It returns "full", "unreadable" or S (file order, no duplicates). It reads `Path.cwd() / <git rev-parse --git-common-dir> / "shallow"` and never uses a literal `.git/shallow` or `--shallow-file`.
    - `sure` = the flag exits 0 and prints "true".
    - If the common dir can't be found, or the file is missing or unreadable: "unreadable" when sure, else "full".
    - A malformed line gives "unreadable".
  - `_walk`:
    - The `known` / `--is-ancestor` block and its 053 text are unchanged. Every early return now has a third part, None.
    - After that block: "unreadable" gives `not checked (shallow clone; run git fetch --unshallow)`.
    - With S non-empty: `rev-list cutoff..HEAD` runs. If it fails, the result is `git rev-list failed` (failed True). If a boundary is in that range, the result is `not checked (shallow boundary <b7>; run git fetch --unshallow)`.
    - Then `merge-base --is-ancestor b cutoff` runs for each b. Exit 0 sets `below`. Exit 1 continues. Any other exit gives `git merge-base failed` (failed True).
    - Returns `(units, None, below)`.
  - New `_parts(walked)`, so 2-tuples still work (C2).
  - New `_below_text(below, n, cutoff)`.
  - `untracked_changes`: entries become `_below_text` when `below` is set (exit 0). "none" stays "none".
  - `research_code`:
    - The `files or []` default is gone.
    - If any unit has `files is None`, the result is `not checked (see UNTRACKED CHANGE)`.
    - `flagged and below` gives `_below_text`, {} (so 062 reports no SKIPPED).
  - `real_data_field`: `below = _parts(walked)[2]`. `names and below` gives `_below_text`, {}, False (so 070 reports no INCOMPLETE).
  - Module docstring: the 079 text is added under UNTRACKED CHANGE, RESEARCH CODE and REAL-DATA FIELD as the plan words it. The RESEARCH CODE and REAL-DATA FIELD paragraphs are re-wrapped around the insert, with no other word changes.
- tests/test_pipeline_check.py
  - Adds `from pathlib import Path` and the helpers `_shallow`, `_unshallow`, `_graph` (shapes a/b), `_below_graph` (d), `_lines`, `_shallow_text` and `_patched_git`.
  - C1 edit in `test_failed_diff_tree_is_an_entry_not_none` (f): its last assertion is now `"not checked (see UNTRACKED CHANGE)"`, and a 2-tuple `"none"` assertion is added.
  - New tests:
    - Fixtures: `test_shallow_boundary_inside_walk_not_checked` (a), `test_shallow_boundary_on_second_parent_not_checked` (b), `test_full_clone_same_graph_unchanged` (c1), `test_unrelated_root_in_full_clone_stays_loud` (c2), `test_shallow_boundary_below_cutoff_entries_unconfirmed` (d), `test_shallow_boundary_in_linked_worktree` (e).
    - Missing inputs: `test_shallow_flag_unknown_no_file_is_full`, `test_shallow_file_unreadable_not_checked`, `test_empty_shallow_file_is_today_path`, `test_shallow_rev_list_failure_is_loud`, `test_merge_base_failure_is_loud`.
    - Step 5: `test_below_rule_real_data_entries`.
  - That is 12 new tests and 1 changed.
- .claude/commands/daily-audit.md: the step 8 sentence is inserted just before "It runs `python3 scripts/check_pipeline.py` and ...". Additions only.
- .claude/commands/run-item.md: the step 8 sentence is inserted just before "Before starting, run `python3 scripts/check_pipeline.py` after `git fetch origin`". Additions only.

File counts:
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
0
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
4
```
Total: 4 files changed (as planned), 0 new.

## Connectivity check
- [x] Every new function or rule is used.
  - `_shallow_boundaries` is called by `_walk`.
  - `_note` is called by `_walk`, `untracked_changes` and `_below_text`.
  - `_parts` is called by `untracked_changes`, `research_code` and `real_data_field`.
  - `_below_text` is called by those three and checked directly in `test_below_rule_real_data_entries`.
  - `SHALLOW_LINE` is used by `_shallow_boundaries`.
  - The step 8 sentence is read by A1 (daily-audit) and by the orchestrator (run-item).
- [x] Every input has a source, and every output has a consumer.
  - Inputs: S comes from git's common dir. `--is-shallow-repository`, `rev-list` and `merge-base` are git.
  - Outputs: the three printed lines in `main()`. A failed flag reaches `main()`'s exit through `untracked[1]`. `main()` passes `walked` (now a 3-tuple) unchanged to all three.
- [x] Every branch ends in a defined result.
  - S branches:
    - full: today's path.
    - unreadable: not checked, exit 0.
    - []: today's path (git also treats an empty file as shallow; real git 2.43 test below).
    - inside: not checked, exit 0.
    - below: entries become unconfirmed, exit 0; "none" stays none.
    - neither: today's path.
  - Failure branches:
    - rev-list fails: error, exit 1.
    - merge-base exits other than 0/1: error, exit 1.
    - diff-tree fails on a commit not in S: still a 053 entry, exit 1 (c2). RESEARCH CODE shows not checked, never none (f).
  - A non-UTF-8 shallow file is caught as unreadable (see Deviations).
- [x] No leftover TODOs or unused files: `git diff -U0` has no TODO/FIXME, and there are no new files.
- Missing-data grep:
  - `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/ | wc -l` gives 37. All of them are lines that already existed: `git diff --stat -- ccbot/` is empty, and this item changes no ccbot/ file.
  - The same pattern plus `: float = ` / `: int = ` on the added lines (`git diff -U0 scripts/ tests/ | grep '^+'`) gives 0.
  - No dataclass is added.
  - The only new `>`/`<` is `len(walked) > 2`, which compares ints and cannot be NaN.
- Feasibility numbers (computed by the tests, real runs):
  - (a): S ∩ R = {B}, 1 of 1. The line is `not checked (shallow boundary <B7>; ...)`. The control without the shallow file gives none.
  - (b): {B2}, 1 of 1.
  - (d): S ∩ R = 0 of 1, below = 1 of 1, n = 2 (Y `scripts/y.py` plus Z's failed diff-tree). The full view gives none.
  - (e): S = {B}, 1 of 1, from the linked worktree. `<wt>/.git` is a file.
  - All of these pass (Test output below).

## Test output (pasted, not summarized)
Full suite, repo root, at the build (working tree on 32b16fb):
```
$ python3 -m pytest -q
...
.................................................................        [100%]
568 passed, 1 skipped in 90.93s (0:01:30)
```
Pipeline-check suites:
```
$ python3 -m pytest -q tests/test_pipeline_check.py tests/test_real_data_field.py
264 passed in 34.15s
```
These include the unchanged `test_cutoff_missing_in_shallow_clone_not_checked`, `test_t14_unusable_cutoff_is_not_checked`, `test_t15_git_log_failure_fails` and `test_shipped_probes_well_formed` (full suite).

RI-008:
```
$ python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py && echo "py311 ok"
py311 ok
```
Repo run. This clone is full (`git rev-parse --is-shallow-repository` prints `false`). The base script is `git show HEAD:scripts/check_pipeline.py`, and both runs use cwd = repo:
```
$ python3 <scratch>/base/check_pipeline.py > cp_before.txt   -> base exit 0
$ python3 scripts/check_pipeline.py > cp_after.txt           -> after exit 0
$ diff cp_before.txt cp_after.txt && echo IDENTICAL
IDENTICAL
(97 lines; UNTRACKED CHANGE: none, RESEARCH CODE: none, REAL-DATA FIELD: none, UNCOMMITTED STEP: none, SKIPPED: none)
```
Process check:
```
$ grep -c "fetch --unshallow" .claude/commands/daily-audit.md .claude/commands/run-item.md
.claude/commands/daily-audit.md:1
.claude/commands/run-item.md:1
$ git diff --word-diff=porcelain .claude/commands/ | grep -c '^-[^-]'
0      (additions only)
```
Mutations. All run in a scratch full clone (`git clone` of the repo into `/tmp/claude-0/-home-claude/13c4a4b3-cf85-50b9-b50f-3e762631e621/scratchpad/079-I2/clone`), never in the repo. Each one is restored with `git checkout`. Command: `pytest -q tests/test_pipeline_check.py -k "shallow or below or unrelated or full_clone or failed_diff_tree or merge_base"` (16 selected).
- m1 (`if inside:` → `if False:`): 3 failed, 13 passed. Failed: (a), (b), (e). Their lines show `<sha7> (git diff-tree failed) (item 053: ...)`.
- m2 (read `Path(".git/shallow")`): 1 failed, 15 passed. Failed: (e).
- m3 (untracked `below` return removed): 1 failed, 15 passed. Failed: (d), whose line shows `cb37083 (git diff-tree failed); 5b73863 scripts/y.py (item 053 ...`, which is 2 entries.
- m3b (real_data_field `below` return removed): 1 failed, 15 passed. Failed: `test_below_rule_real_data_entries`.
- m4 (`files or []` restored and the None guard removed): 2 failed, 14 passed. Failed: (f), with `'none' == 'not checked ...'`, and (d), with `RESEARCH CODE: none`.
  - The first attempt used an anchor that matched twice, so only the guard was removed. That gave 3 failed, a crash on None. It was re-run with the unique loop-line anchor; that re-run is the result above.
- m5 (unreadable → "full"): 1 failed, 15 passed. Failed: `test_shallow_file_unreadable_not_checked`.
- m6 (extra; merge-base exit other than 0/1 treated as 1): 1 failed, 15 passed. Failed: `test_merge_base_failure_is_loud`.

Probe run (078 anchors). None of the anchors moved, because none of the edited lines are probe anchors. It was run on the scratch clone, with my 4 files and a stub work/079/05 plus a scratch `--log` line committed there (detached commit), so the baseline has no UNTRACKED CHANGE:
```
$ python3 scripts/probe_guardrails.py --repo <scratch>/079-I2/clone --ref HEAD   (exit 0)
baseline tests/test_pipeline_check.py: 0 failed, 225 passed, 0 errors, 0 skipped; 26.4 s
TOTAL: 9 probes, 9 hold, 0 not held, 0 anchor missing, 0 error; 269.6 s
```
- First attempt: the scratch commit had code but no 079 step file. That gave `TOTAL: 9 probes, 5 hold, 0 not held, 0 anchor missing, 4 error`. The 4 errors were the check_pipeline probes, whose baseline failed `test_repo_pipeline_has_no_skipped_items` because UNTRACKED CHANGE flagged the scratch commit. That is correct checker behaviour and not a defect.
- Observation: the probe's printed `recorded` counts for test_pipeline_check.py (e.g. "1 failed, 89 passed") differ from today's totals (224 passed). `recorded` is printed only, so this changes nothing.

Real git behaviour checked in scratch (git 2.43.0):
- An empty shallow file gives `--is-shallow-repository` = true.
- A file holding `zz` makes `git merge-base --is-ancestor HEAD HEAD` fail with `fatal: bad shallow line: zz`, exit 128.

## Real-data effect (diff_reports output, pasted)
not required (.claude/commands/daily-audit.md, .claude/commands/run-item.md, scripts/check_pipeline.py, tests/test_pipeline_check.py)

## Deviations from plan
1. Malformed-line case in `test_shallow_file_unreadable_not_checked`. The plan expects `_walk` to give `not checked (shallow clone; ...)`. Real git dies on the bad line (`fatal: bad shallow line: zz`, exit 128, as 03 row 23 says), so the 053 `known` / `--is-ancestor` block answers first with `not checked (cutoff <c7> not in this shallow clone; run git fetch --unshallow)`, still failed False and exit 0.
   - The test asserts `_shallow_boundaries() == "unreadable"` (C3) and that the `_walk` text starts with `not checked (`, contains `run git fetch --unshallow`, and has failed False.
   - The missing-file case asserts the exact plan text.
   - The result is still never none. I3: please confirm this is acceptable.
2. `_shallow_boundaries` also catches `UnicodeDecodeError` as "unreadable"/"full". The plan names only OSError, and a non-UTF-8 file would otherwise crash. This is the same rule (Missing inputs row 1).
3. Small differences in form, same behaviour:
   - The S variable is named `shallow_s`, because `shallow` is already used in the block above.
   - A failed `--git-common-dir` is handled by raising OSError inside the same try block.
   - The test helper `_unshallow` removes the shallow file for the controls.
4. Placement in the two command files: the plan's "After `It runs ...`, insert ... just before `It runs`" is read as just before, as in the run-item.md instruction, so the line comes before the run.

For I3/A1 (C4): in a shallow clone deep enough to hold the cutoff, the boundaries are usually older than the cutoff. A real untracked change there shows as `not checked (... below the cutoff; n unconfirmed entries ...)` with exit 0. The step 8 line (unshallow first) is what keeps it loud.

Recurring issues checked (logs/recurring-issues.md):
- RI-001 (ESCALATED): every rule test pins a computed per-fixture count ((a) 1 of 1, (b) 1 of 1, (d) 0 of 1 inside, 1 of 1 below, n = 2, (e) 1 of 1). Nothing is asserted as "always".
- RI-014 (OPEN, this item): built, and m1-m5 each fail their target.
- RI-002: an unreadable or malformed S, a failed rev-list or merge-base, and a None diff never become none or a pass.
- RI-007: the full-clone loud path is kept ((c2): exit 1).
- RI-008: py_compile on 3.11 is OK.
- RI-010: the step 8 text is backed by the grep check, and the log line goes through `--log`.
- RI-012: boundary membership is a set test on full SHAs, and S lines use `fullmatch`.
- RI-006: every count above is from a command.
- RI-009: mutations and probes ran in a scratch clone, never in the repo.

RI-014: guardrail built (079); GUARDED when 079 is merged and m1 fails fixture (a) on main
