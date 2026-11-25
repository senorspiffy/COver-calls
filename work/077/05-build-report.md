# 05 Build report - 077

# Round 2 (I3 FAIL round 1 -> I2, tests only)
Base: HEAD d703779 (`Item 077: I3 verification FAIL (round 1), sent back to I2`), on top of the round-1 build 3006b73. Not committed.

Status: BUILT (round 2). 06 problem 1 is fixed with the two negative tests I3 named. scripts/check_pipeline.py is not changed (06: "No change to scripts/check_pipeline.py is needed"). The three RI-012 probe mutations that survived round 1 now each fail a new test. The full suite has one failure, `test_repo_pipeline_has_no_skipped_items`, and it is expected (item 071, see below).

## Changes made, round 2
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
0
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
1
$ git diff --stat
 tests/test_pipeline_check.py | 28 ++++++++++++++++++++++++++++
 1 file changed, 28 insertions(+)
```
1. **tests/test_pipeline_check.py**, 2 new tests (211 -> 213 in this file):
   - (06 1a) `test_i3_fail_with_a1_pass_only_inside_text_keeps_old_detail` (T-P3c). Item 186's 07 is `x\nsee A1 result: PASS (quoted)\n` and item 187's 07 is `x\n  A1 result: PASS (indented)\n`, both with 06 FAIL. Each line must equal `<ID>: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))` and `I3 FAIL: 186, 187` must be printed with exit 1.
   - (06 1b) `test_uncommitted_step_with_lookalike_log_lines_is_listed` (P5a2). It is P5a (151 01-research.md, `logged=False`) plus logs/research/2026-11-11.md with `12:00 | R1 | 1510 | x`, `12:00 | R2 | 151 | see R1 notes` and `12:00 | I2 | 151 | R1 x`. The line must equal `P5A` and exit 1.

## Connectivity check, round 2
- The two new tests are collected by pytest (they are in the full run below). No new function, file or rule. No TODO.
- Missing-data grep on ccbot/: `grep -rnE "fillna|...|\.get\([^)]*, 0\)" ccbot/ | wc -l` gives 37. Round 2 changes no ccbot/ file (diff above), so there are no new or changed hits. There is no new dataclass field and no new `>`/`<` test.
- No feasibility test is named in the plan for round 2.

## Mutations, round 2 (scratch worktree)
They ran in a detached worktree of HEAD d703779 at `scratchpad/077-I2/wt`, with the new tests/test_pipeline_check.py copied in. Each mutation was applied alone to scripts/check_pipeline.py and restored after its run (`scratchpad/077-I2/mut.py`). Selection: `-k "lookalike or inside_text or uncommitted or i3_fail"`. Output:
```
_a1_results unanchored | 1 failed, 20 passed, 192 deselected in 6.55s
   ['FAILED tests/test_pipeline_check.py::test_i3_fail_with_a1_pass_only_inside_text_keeps_old_detail']
_logged substring | 1 failed, 20 passed, 192 deselected in 5.05s
   ['FAILED tests/test_pipeline_check.py::test_uncommitted_step_with_lookalike_log_lines_is_listed']
_logged no trailing pipe | 1 failed, 20 passed, 192 deselected in 3.46s
   ['FAILED tests/test_pipeline_check.py::test_uncommitted_step_with_lookalike_log_lines_is_listed']
```
The mutations are 06's three probes:
- `re.findall(r"A1 result:\s*(\w+)", text)`;
- `return item in text and agent in text`;
- `rf"\|\s*{agent}\s*\|\s*{item}"`.

All three are now killed. On the unmutated code both new tests pass (`-k "lookalike or inside_text"`: `2 passed, 211 deselected in 3.80s`). `git -C wt status --short` afterwards shows only the copied test file (` M tests/test_pipeline_check.py`).

## Test output, round 2 (pasted)
`python3 -m pytest -q` from the repo root:
```
=========================== short test summary info ============================
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 554 passed, 1 skipped in 91.97s (0:01:31)
```
Expected, not a defect of this build (item 071). 06 round 1 (FAIL, sent back to I2) is committed in d703779, so `check_pipeline.py` exits 1. The assertion's only failing lines are:
```
077: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))
I3 FAIL: 077
A1 FAIL: none
INCOMPLETE: none
UNCOMMITTED STEP: none
SKIPPED: none
```
Round 1 had 553 passed + 1 skipped. Round 2 has 554 passed + 1 failed (the expected one) + 1 skipped, which is 556, i.e. 553 + 1 + 2 new tests. The skip is the same exchange_calendars import.

## Real-data effect, round 2
Not required: only tests/test_pipeline_check.py changes, so there is no TRIGGER path and no ccbot/realtest.py change.

## Recurring issues checked, round 2
- RI-012: guardrail extended (077 round 2). Both shared text readers now have a negative test with the pattern inside other text, and the three probe mutations each fail one.
- RI-001 (ESCALATED): the new fixtures have non-zero counts (2 items, 3 lookalike lines). No trading window.
- RI-014 (OPEN): `_walk` is not touched. The new P5a2 uses a full (non-shallow) repo, as P5a does.
- RI-002: the new tests assert that lookalike text never counts as logged or as A1 PASS (no default pass).
- RI-009: mutations ran only in the scratch worktree.
- RI-007, RI-008, RI-010, RI-013: unchanged from round 1 (no checker, Python-version or diff-report change).
- RI-003 to RI-006, RI-011: not applicable.

RI-012: guardrail extended (077 round 2); negative tests for `_a1_results` and `_logged`, 3 probe mutations killed.

## Deviations from plan, round 2
None. Only the two tests that 06 named were added.

# Round 1
Base: HEAD 1a925b0 (076 I3 PASS round 2). While I built, the orchestrator committed f96aa5e (`Item 076: A1 result PASS`). It changes only logs/audit/2026-11-19-076.md and work/076/07-audit-task.md (`git diff --stat 1a925b0 HEAD`: 2 files, 103 insertions), and none of this build's files. Built in the working tree, not committed. Every anchor in 04 was re-read on 076's tree. 076's `log_fields_ok`/`log_hint` lines in `incomplete()` are unchanged. `_walk` is neither called nor changed.

Status: BUILT. Every change in 04 is made. All 31 planned mutations fail their named tests. The full suite is green. The real-tree check output differs from the old checker only by the new `UNCOMMITTED STEP: none` line, and the exit code is 0 for both.

## Changes made (file: what changed)
File counts (working tree against HEAD, work/ and logs/ excluded, so A1's 076 files are not counted):
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
0
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
4
$ git diff --stat
 .claude/agents/a1-auditor.md  |   4 +-
 scripts/check_pipeline.py     | 172 +++++++++++++++++++++++++---------
 tests/test_pipeline_check.py  | 208 +++++++++++++++++++++++++++++++++++++++++-
 tests/test_real_data_field.py |  14 ++-
 4 files changed, 348 insertions(+), 50 deletions(-)
```
This matches 04's "4 files". Two of them are in RULE_PATHS (scripts/check_pipeline.py and .claude/agents/a1-auditor.md), so they need the person's OK in PR review.

1. **scripts/check_pipeline.py**
   - Step 2: `open_branches` collects `failed` [(item, status, detail)] for I3 FAIL / A1 FAIL right after `classify`. After the 062 merge loop it drops every item that is in `skipped`. It adds `"failed"` to the branch dict, and the docstring lists the new key. `main` prints `BRANCH FAIL: <ID> (<ref>: <status>; <detail>)` in a loop over the branches after the `BRANCH SKIPPED:` loop. The exit expression is unchanged. In the module docstring, "Two more lines" becomes "Three more lines", the `BRANCH FAIL` entry is added after `BRANCH SKIPPED` (03's text), and gap (x) is removed.
   - Step 3: `_a1_results(text)` (L347) is the single `A1 result:` reader. It is used by `classify` (the I3 FAIL branch L436 and the `len(have) == len(need)` block L443) and by `_open_at` (L717). In classify's `verdict == "FAIL"` branch, a 07 whose last A1 word is not FAIL returns `I3 FAIL` with `<scope>; <where>; 06 FAIL after A1 PASS in 07: a follow-up to a completed item is a new item (run-item, items 053, 077)<extra>`. Otherwise the old detail is returned unchanged. Gap (w) is rewritten in the docstring with the PRE_A1_LINE/LEGACY known gap (04 change 3).
   - Step 4: `FENCE_OPEN` (L321) and `_md_lines(text)` (L324) follow 03 "Exact rules". Comments are stripped first, the opener uses `fullmatch`, a backtick opener with a backtick in its info string is not an opener, and the closer is `" {0,3}C{n,}[ \t]*"` with `fullmatch`. `i3_verdict` reads only `out` rows. `_field_gap` finds the heading on an `out` row and takes rows until an `out` row starting with `## `. Its for-else returns the unchanged "unclosed ``` fence" message only when `open_at_end` is True. Both docstrings and the REAL-DATA FIELD entry are updated, and gap (t) gets the two fence known gaps.
   - Step 5: `_log_text(logs)` (L469) and `_logged(text, agent, item)` (L476) are factored out of `incomplete()`, which now calls both. `uncommitted_steps(logs)` (L481) follows 03 "Exact rules". It makes one `ls-tree -r --name-only HEAD -- work/` call with no `--full-tree`. A non-zero exit returns `("git ls-tree HEAD failed (item 077)", True)`. It never calls `_walk`. `main` sets `uncommitted = uncommitted_steps()` (L982), prints `UNCOMMITTED STEP:` after `REAL-DATA FIELD:`, and adds `or (uncommitted and uncommitted[1])` to the exit expression. The module docstring gets the `UNCOMMITTED STEP` entry with gaps (a)-(c).
2. **tests/test_pipeline_check.py**
   - `_branch_adds` gains `bodies=None`. The default body is unchanged.
   - New tests: BF1 `test_branch_i3_fail_is_listed`, BF2 `test_branch_a1_fail_is_listed`, BF3 `test_branch_skipped_wins_over_branch_fail`, T-P3 `test_i3_fail_after_a1_pass_is_a_new_item` (full-line equality for 180 and 185), T-P3b `test_i3_fail_with_no_a1_line_keeps_old_detail`, P5a-P5h (`test_uncommitted_unlogged_step_is_listed`, `..._without_logs_folder_is_listed`, `test_uncommitted_but_logged_steps_are_quiet`, `test_committed_unlogged_step_is_incomplete_not_uncommitted`, `test_staged_step_is_still_uncommitted`, `test_uncommitted_step_in_shallow_clone`, `test_uncommitted_step_without_git`, `test_uncommitted_step_ls_tree_failure_fails`) and `test_a1_text_names_077_lines`.
   - Added asserts: the 038 test (`BRANCH FAIL: 060`/`040` absent), T5 (full old detail), T8 (`BRANCH FAIL: 177 (origin/fix: I3 FAIL; `), `test_head_run_ignores_uncommitted_item` (the tree run lists 151, the head run shows `none`) and `test_repo_pipeline_has_no_skipped_items` (`UNCOMMITTED STEP: none`).
   - T4 gains 9 `pytest.param` ids (tilde, longer, 4-space, tab, info, 4-space-close, backtick-info, tilde-info, mixed). The old cases are unchanged.
3. **tests/test_real_data_field.py**
   - t23: the two whole clauses are added to the i3 and run-item `must` lists. There are still 3 ids.
   - t12 gains 4 ids (tilde, longer, 4-space, info).
4. **.claude/agents/a1-auditor.md**, job B: the check_pipeline bullet names "`UNCOMMITTED STEP:` entry" (an error), and the open-PR bullet names "`BRANCH FAIL:` line" (information, noted with the branch's age), with 04's exact text.

## Connectivity check
- [x] every new function/rule is used
  - `FENCE_OPEN` is used by `_md_lines`.
  - `_md_lines` is used by `i3_verdict` L357 and `_field_gap` L805.
  - `_a1_results` is used at L436, L443 and L717.
  - `_log_text`/`_logged` are used by `incomplete` and `uncommitted_steps`.
  - `uncommitted_steps` is called by `main` L982.
  - `b["failed"]` is printed by `main`.
- [x] every input has a source, every output has a consumer
  - The `BRANCH FAIL:` and `UNCOMMITTED STEP:` lines are read by A1 job B (a1-auditor.md, pinned by `test_a1_text_names_077_lines`, RI-010).
  - The new I3 FAIL detail is on the item line and in `I3 FAIL:`, which A1 already reports.
- [x] every branch ends in a defined result
  - No git: `not checked (no git)` (P5g).
  - ls-tree fails: `git ls-tree HEAD failed (item 077)`, exit 1 (P5h). The real git exit is 128 (`fatal: Not a valid object name HEAD`, probe in scratch/unborn).
  - No logs/ folder: the file is listed (P5b).
  - No 07, or a 07 with no A1 line: old detail (T6, T-P3b).
  - Branch 06 unreadable: no BRANCH FAIL (BF2).
  - Unclosed fence: `(None, None)` / "unclosed ``` fence" (existing ids).
  - PRE_A1_LINE: old detail, documented as a known gap (T-P3b 017).
- [x] no leftover TODOs or unused files. Scratch files are only under scratchpad/077-I2/, and the worktree `077-I2/wt` was removed (`git worktree list` no longer shows it. `scratchpad/wt32` is another agent's worktree and was left alone).
- Missing-data grep over ccbot/ (`grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/`): 37 hits, all old. `git diff --stat -- ccbot/ config/` is empty, so there are no new or changed hits.
- Patterns the grep can't see (014), in the changed code:
  - There are no dataclasses and no numeric comparisons.
  - `"; ".join(entries) or "none"` gives `none` only after ls-tree succeeded and every file was checked, never for absent data.
  - `(bodies or {}).get(f, default)` is a test helper that keeps today's default body.

## Test output (pasted, not summarized)
Full suite, repo root, final run on the current tree (f96aa5e + this build):
```
$ python3 -m pytest -q
553 passed, 1 skipped in 77.79s (0:01:17)
```
(0 `FAILED` lines.) Before any new test was added (steps 1-5 code only), the suite gave `526 passed, 1 skipped in 76.62s (0:01:16)`, so no existing git test needed a fixture fix for UNCOMMITTED STEP. 553 - 526 = 27 new ids: 3 BF + 2 T-P3 + 9 T4 + 4 t12 + 8 P5 + 1 A1 text. t23: `python3 -m pytest -q tests/test_real_data_field.py -k t23`, `3 passed, 32 deselected in 0.06s`.

Python 3.10 syntax: `python3.11 -m py_compile scripts/check_pipeline.py`, no output, exit 0 (Python 3.11.18; there is no python3.10 on PATH). No possessive quantifiers and no 3.12 f-strings.

Shared A1 reader (Grep `A1 result:\s*(\w+)` over scripts/check_pipeline.py): 1 hit, `350:    return re.findall(r"^A1 result:\s*(\w+)", text, re.M)`, inside `_a1_results`.

Real tree, whole output, old checker (scratchpad/077-I2/check_pipeline_old.py = 1a925b0's) vs the build, same tree:
```
$ python3 check_pipeline_old.py > before2.txt   # exit 0
$ python3 scripts/check_pipeline.py > after2.txt  # exit 0
$ diff before2.txt after2.txt
93a94
> UNCOMMITTED STEP: none
```
`BRANCH FAIL:` lines on the real tree: 0 (`grep -c`). The new tail lines are `REAL-DATA FIELD: none`, `UNCOMMITTED STEP: none`, `ORPHAN LOG: none` and `SKIPPED: none`. The first baseline (taken before f96aa5e) showed the same one-line diff.

Step 4 alone: the build vs a scratch copy of the build with `i3_verdict` and `_field_gap` restored to 1a925b0's bodies (check_pipeline_pre4.py), on the real tree. `diff pre4.txt after2.txt`: no output, `IDENTICAL (97 lines)`, both exit 0.

Fence feasibility (04 change 5), on work/*/0[56]-*.md today:
- `^\s*```\S`: 0.
- `^\s*(```|~~~)[ \t]+\S`: 0.
- `^\s*~~~`: 0.
- ``` lines: 590 in 79 files, out of 146 05/06 files. 03 counted 548 lines in 75 files on 2026-11-19. The tree has grown since (075/076 05 and 06).
- Scratch old-vs-new reader comparison over all 146 files (scratchpad/077-I2/compare.py, `python3 -I`): `files 146; i3_verdict on 06: same 73, differ 0; _field_gap on 05/06: same 146, differ 0`. Over the 79 fenced files: 79 the same.

Mutations, each made alone in a scratch worktree (`scratchpad/077-I2/wt`, detached at f96aa5e, with the 4 built files copied in; RI-009). Each file was restored after its run. Only the named test ids were run (`scratchpad/077-I2/mutate.py`). "KILLED" means pytest exit != 0 and every named id FAILED:
```
KILLED | t23 i3 even if->unless | 1 failed in 0.24s | failed 1/1 named
KILLED | t23 i3 never use->you may use | 1 failed in 0.03s | failed 1/1 named
KILLED | t23 run-item even when->unless | 1 failed in 0.03s | failed 1/1 named
KILLED | t23 run-item never give->you may give | 1 failed in 0.03s | failed 1/1 named
KILLED | BF keep only SKIPPED | 2 failed in 2.19s | failed 2/2 named
KILLED | BF in exit expression | 2 failed in 1.01s | failed 2/2 named
KILLED | BF skipped filter dropped | 1 failed in 0.49s | failed 1/1 named
KILLED | P3 new branch dropped | 1 failed in 0.17s | failed 1/1 named
KILLED | P3 if a1: | 1 failed in 0.16s | failed 1/1 named
KILLED | P3 a1[0] | 1 failed in 0.16s | failed 1/1 named
KILLED | fence any-length closer | 2 failed in 0.30s | failed 2/2 named
KILLED | fence ~ dropped | 3 failed in 0.34s | failed 3/3 named
KILLED | fence opener lstrip | 3 failed in 0.34s | failed 3/3 named
KILLED | fence opener \s{0,3} | 1 failed in 0.10s | failed 1/1 named
KILLED | closer allows trailing text | 2 failed in 0.31s | failed 2/2 named
KILLED | closer uses lstrip | 1 failed in 0.10s | failed 1/1 named
KILLED | backtick-info rule dropped | 1 failed in 0.09s | failed 1/1 named
KILLED | backtick-info rule applied to ~ | 1 failed in 0.10s | failed 1/1 named
KILLED | closer accepts either char | 1 failed in 0.09s | failed 1/1 named
KILLED | i3_verdict old loop | 9 failed in 0.36s | failed 9/9 named
KILLED | _field_gap old loop | 4 failed in 0.86s | failed 4/4 named
KILLED | P5 no HEAD test | 1 failed in 0.25s | failed 1/1 named
KILLED | P5 no log test | 1 failed in 0.24s | failed 1/1 named
KILLED | P5 CHECKLIST_FROM cutoff | 1 failed in 0.23s | failed 1/1 named
KILLED | P5 index (ls-files) for HEAD | 1 failed in 0.24s | failed 1/1 named
KILLED | P5 porcelain ?? only | 1 failed in 0.25s | failed 1/1 named
KILLED | P5 no exit term | 1 failed in 0.22s | failed 1/1 named
KILLED | P5 ls-tree failure as empty set | 1 failed in 0.19s | failed 1/1 named
KILLED | P5 ls-tree failure as none | 1 failed in 0.19s | failed 1/1 named
KILLED | A1 UNCOMMITTED clause removed | 1 failed in 0.08s | failed 1/1 named
KILLED | A1 BRANCH FAIL clause removed | 1 failed in 0.07s | failed 1/1 named
31/31 mutations killed (every named test failed)
```
Named ids per mutation (04 Tests):
- t23 [i3] / [run-item].
- BF1+BF2 for "keep only SKIPPED" and "exit term". BF3 for the filter.
- T-P3 for "new branch dropped" and `a1[0]`. T5 for `if a1:`.
- Fences:
  - any-length closer: T4/t12 `longer`.
  - `~` dropped: T4/t12 `tilde`, T4 `mixed`.
  - opener `lstrip()`: T4 `4-space`, `tab`, t12 `4-space`.
  - `\s{0,3}`: T4 `tab`.
  - closer allows trailing text: T4/t12 `info`.
  - closer `lstrip()`: T4 `4-space-close`.
  - backtick-info rule dropped: T4 `backtick-info`.
  - backtick-info rule applied to `~`: T4 `tilde-info`.
  - closer accepts either char: T4 `mixed`.
  - old `i3_verdict` loop: the 9 new T4 ids.
  - old `_field_gap` loop: the 4 new t12 ids.
- P5d for no HEAD test, P5c for no log test, P5b for the cutoff and for the exit term, P5e for `ls-files` and for porcelain `??`, and P5h for both ls-tree-failure mutations.
- The A1 text test for either clause removed.

03 F39 (UNVERIFIED until P5f ran) is now settled. In a `--depth 1` clone from `file://` (`--is-shallow-repository` = `true`), `ls-tree -r HEAD` sees the whole tip tree. The committed 039 01, which has no log line, is not listed (`UNCOMMITTED STEP: none`, exit 0). The uncommitted 151 01 is listed (exit 1).

Item 071 note: no item is in I3 FAIL or A1 FAIL on this tree (`I3 FAIL: none`, `A1 FAIL: none`), and `test_repo_pipeline_has_no_skipped_items` passes.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat`: .claude/agents/a1-auditor.md, scripts/check_pipeline.py, tests/test_pipeline_check.py, tests/test_real_data_field.py; no TRIGGER or data/real/ path)

## Deviations from plan
None in behaviour. Small choices where 04 left the detail open:
1. P5f: 04 says "`_history` plus a commit" and does not say what the commit holds. Its commit adds item 039 with a 01 that has no log line. The ID is below CHECKLIST_FROM, so it is not INCOMPLETE and the exit stays 0. A missed tip-tree entry in the shallow clone would therefore list it, so the test settles F39 rather than assuming it. P5f also asserts `UNTRACKED CHANGE: not checked (cutoff `, which shows the clone really lacks the cutoff.
2. `uncommitted_steps` skips a glob match that is not a directory (`if not d.is_dir()`). 04 says "walks ... dirs".
3. BRANCH FAIL lines are printed in their own loop over the branches, after all BRANCH SKIPPED lines, so the two kinds are not interleaved per branch.
4. T-P3 checks whole-line equality, which is stronger than 04's "want ... detail".
5. The fence counts today are 590 lines in 79 files, not 03's 548/75 (the tree has grown). The comparison covered all 146 05/06 files.

RI-001: no trading filter or window. Every count above was measured today: 0 BRANCH FAIL, 0 UNCOMMITTED STEP, 590/79 fence lines, 0 of 146 files changed by step 4. Each detector has non-zero fixture counts.
RI-014: OPEN, unchanged by 077. Nothing calls or changes `_walk`, and P5f asserts shallowness rather than assuming it (079 owns the fix).
RI-010: guardrail extended (077). UNCOMMITTED STEP is the first working-tree-vs-HEAD check. Both new lines have an A1 duty pinned by `test_a1_text_names_077_lines`. It can count as GUARDED when merged and an A1 probe on main (an uncommitted, unlogged 01) gives `UNCOMMITTED STEP: <ID> 01-research.md (` with exit 1.
RI-002: GUARDED, unchanged. A failing ls-tree and a missing logs/ folder are never `none` (P5h, P5b).

Recurring issues checked: RI-001 (ESCALATED), RI-014 (OPEN), RI-002, RI-004, RI-005, RI-007, RI-008, RI-009, RI-010, RI-012, RI-013 (each against this build's output above: dated counts, traced test ids with 31/31 mutations killed, SKIPPED wins over BRANCH FAIL, py_compile on 3.11, scratch worktree only, A1 duty for new lines, fullmatch fences and one shared A1/log reader, whole-output diffs for the whole build and for step 4 alone).
