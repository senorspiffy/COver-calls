# 05 Build report - 070
Built on daily-fixes/2026-11-17 at 8dc2c2d (069's build is in HEAD). 04's line numbers were written before 069 landed; every hunk was placed by content, per 04 C1. 069's lines are unchanged: INBOX_FROM..INBOX_HUB, the INBOX docstring paragraph, `inbox_section()` and the INBOX print/early return in main.

## Changes made (file: what changed)
File counts (run before 05 was written):
- new: `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` → 1 (tests/test_real_data_field.py)
- changed: `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` → 3 (scripts/check_pipeline.py, templates/build-report.md, templates/verification.md)
- 4 files in total.

1. `scripts/check_pipeline.py`
   - Constants after LOG_TIME_EXCEPT, before the RULE_PATHS comment: `WHOLE_DIFF_FROM = 70`, `TRIGGER` (8 paths), `TRIGGER_DIRS = ("data/real/",)`, `REAL_DATA_FIELD`, `TOTAL_LINE`. Each has an item-070 comment. The text matches 03 step 1.
   - Docstring: the `REAL-DATA FIELD (item 070, RI-010/RI-013)` entry goes after the RESEARCH CODE entry (gap (l)) and before the `--next-id` paragraph. It covers the rule, the cutoff, TRIGGER/TRIGGER_DIRS, each report text, and gaps (m)-(t). 069's INBOX paragraph stays below `--next-id`.
   - New functions after `research_code()` and before `MAIN =`:
     - `_triggers(files)`
     - `_field_gap(text)`: drops comments, tracks fences from the top, uses the section bounds, fails on an unclosed fence, and needs a TOTAL fullmatch.
     - `_item_triggers(cutoff)`: one `git log --no-merges --no-renames --name-only --format=%x01%H <cutoff>..HEAD`, split on `\x01`. It keeps IDs >= WHOLE_DIFF_FROM, takes the union of trigger files, and keeps the sha7 of the newest commit.
     - `real_data_field(cutoff, walked)` → None without git, or `(text, {ID: [entries]}, failed)`.
   - main:
     - `real = real_data_field(cutoff, walked)` after `research = ...`
     - `gaps = incomplete(d) + (real[1].get(d.name, []) if real else [])`
     - `REAL-DATA FIELD:` printed right after `RESEARCH CODE:`
     - the final return gets `or (real and real[2])`
2. `tests/test_real_data_field.py` (new): 18 functions, T1-T18. It imports the helpers from test_pipeline_check (04 C1). T10 is parametrized with 2 ids and T12 with 3, so 21 tests are collected.
3. `templates/build-report.md` (comment under `## Real-data effect`) and 4. `templates/verification.md` (the same comment): "(list in work/067/03-handoff.md)" is replaced with the 03 step 7 TRIGGER text. The rest of each comment is unchanged.

## Connectivity check
- [x] Every new function/rule is used:
  - `_triggers` is called by `_item_triggers`, which is called by `real_data_field`, which is called by main.
  - `_field_gap` is called by `real_data_field`.
  - The constants are used by those functions and by T9/T10.
  - The template comments name TRIGGER.
- [x] Every input has a source, and every output has a consumer.
  - Inputs: git history (`<cutoff>..HEAD`), `work/<ID>/request.md`, 05 and 06 from the working tree.
  - Outputs: the entries join INCOMPLETE (exit 1), the `REAL-DATA FIELD:` line is printed, and `failed` feeds the exit code.
- [x] Every branch ends in a defined result:
  - no git → `not checked (no git)` (T8)
  - `_walk` error → `not checked (see UNTRACKED CHANGE)` (T14)
  - git log fails → `git log failed (item 070)` with exit 1 (T15)
  - no request.md → `<ID> (no work/<ID>/request.md here)` with exit 1 (T16)
  - RESEARCH ONLY → skipped, since 062 reports it (T18)
  - no 05 → INCOMPLETE (T17)
  - heading missing, no TOTAL, or an unclosed fence → INCOMPLETE (T12b, T2/T4/T5, T12c)
  - 06 absent → not checked yet; classify shows `next 06` (T13)
  - filled → none (T1)
- [x] No leftover TODOs or unused files. `grep -nE "TODO|FIXME"` on both code files gives no output. The scratch worktree was removed (`git worktree list | grep -c wt070` → 0).
- Missing-data grep on `ccbot/`: 37 hits, all pre-existing. `git diff --stat -- ccbot/` is empty, so there are no new or changed hits. The same patterns run on the added lines of check_pipeline.py give:
  - `found.get(item, (sha[:7], []))`: the first sighting of an ID starts an empty file set, and the union then adds the commit's real trigger files. Nothing is defaulted to a pass.
  - `", ".join(names) or "none"`: this is "none" only when the check ran and found no entry. The no-git and cutoff cases return earlier with "not checked".
  - `real[1].get(d.name, []) if real else []`: an item with no trigger entry adds no gap. Without git, the line prints "not checked (no git)" instead.
  - `or (real and real[2]) else 0`: this is the exit formula, and `real` None means no git, which matches the existing UNTRACKED handling.
- 014 patterns: no dataclass and no numeric default were added. The only `<` test is `int(item) < WHOLE_DIFF_FROM`. `item` comes from STEP_FILE's `\d{3}`, so it is always an int and never NaN.

## Test output (pasted, not summarized)
Base, at 8dc2c2d before any edit, `python3 -m pytest -q -p no:cacheprovider`:
```
353 passed, 1 skipped in 52.79s
```
New file, `python3 -m pytest -q -p no:cacheprovider tests/test_real_data_field.py`:
```
.....................                                                    [100%]
21 passed in 2.93s
```
Full suite after the change, `python3 -m pytest -q -p no:cacheprovider`:
```
374 passed, 1 skipped in 57.39s
```
374 = 353 + 21. `test_repo_pipeline_has_no_skipped_items` is among the passes.

`python3.11 -m py_compile scripts/check_pipeline.py tests/test_real_data_field.py` → `py311 ok`, with no error (RI-008). The default interpreter is Python 3.13.18.

Real-repo probe, `python3 scripts/check_pipeline.py` after the change (exit 0), from `STUCK:` on:
```
STUCK: none
AWAITING A1: none
IN PR: none
OPEN BRANCHES (not merged into HEAD):
  origin/claude/project-thread-f64g3k: items none; merges cleanly; last commit 2026-11-17 (0 days)
RULES BRANCH: none
ID CLASH: none
A1 FAIL: none
INCOMPLETE: none
LOG TIME: none (not checked: 048: built before 045's --log rule reached main; times typed by hand, not recoverable (item 049))
UNTRACKED CHANGE: none
RESEARCH CODE: none
REAL-DATA FIELD: none
ORPHAN LOG: none
INBOX: not checked (no daily report from 2026-11-18)
SKIPPED: none
```
Before the change, the same output had no `REAL-DATA FIELD:` line and exit 0, with 069 `in progress (FULL: next 06)` and 070 `in progress (FULL: next 05)`.

`git rev-list --no-merges --count 694bf4d..HEAD` → `89`.

`time python3 scripts/check_pipeline.py`:

| | real | user | sys |
|---|---|---|---|
| before | 0m0.748s | 0m0.600s | 0m0.167s |
| after | 0m0.695s | 0m0.579s | 0m0.136s |

The extra `git log` call adds no measurable time.

Positive control. In a scratch worktree (`git worktree add --detach` under the scratchpad, with these 4 files copied in), `WHOLE_DIFF_FROM = 63` was set and `python3 scripts/check_pipeline.py` was run (exit 1):
```
INCOMPLETE: 063 (05 has no '## Real-data effect (diff_reports output, pasted)' section (addf948 changes ccbot/realtest.py; item 070); 06 has no '## Real-data effect (diff_reports output, pasted)' section (addf948 changes ccbot/realtest.py; item 070)), 065 (05 has no '## Real-data effect (diff_reports output, pasted)' section (e129253 changes ccbot/realtest.py; item 070); 06 has no '## Real-data effect (diff_reports output, pasted)' section (e129253 changes ccbot/realtest.py; item 070))
REAL-DATA FIELD: 063, 065
```
This is the expected result: 063 and 065 are named, and 067 (no trigger) and 068 (filled in both sections) are not. There is no difference to explain.

Mutations: scratch worktree, one mutation at a time, `pytest -q tests/test_real_data_field.py`. Each mutation was reverted after its run.
```
first-parent units: 1 failed, 20 passed in 3.20s -> test_t6_pr_merge_flags_only_the_item_whose_commit_triggers
file-wide TOTAL: 1 failed, 20 passed in 2.86s -> test_t5_total_outside_the_section_does_not_count
comments kept + substring: 1 failed, 20 passed in 2.91s -> test_t2_comment_only_field_is_incomplete
data/real/ removed: 2 failed, 19 passed in 3.13s -> test_t11_data_real_file_triggers, test_t9_trigger_matches_realtest_imports_and_config_reads
ccbot/pricing.py removed: 1 failed, 20 passed in 3.35s -> test_t9_trigger_matches_realtest_imports_and_config_reads
extra ccbot/data.py: 1 failed, 20 passed in 3.13s -> test_t9_trigger_matches_realtest_imports_and_config_reads
## in fence ends section: 1 failed, 20 passed in 3.32s -> test_t12_fences_and_headings[fenced-heading]
cutoff check removed: 1 failed, 20 passed in 3.25s -> test_t7_items_before_cutoff_are_not_checked
RESEARCH ONLY skip removed: 1 failed, 20 passed in 3.56s -> test_t18_research_only_item_is_062s
```
How each mutation was made:
- first-parent units: the `--no-merges` call was replaced with `--first-parent -m`.
- file-wide TOTAL: the TOTAL search ran over `lines` instead of `section`.
- comments kept + substring: the comment strip was removed, and the match became `"TOTAL" in line`.
- `data/real/` removed: `TRIGGER_DIRS = ()`.
- `## ` in a fence ends the section: the `not fence and` was dropped.
- cutoff check removed: `if int(item) < WHOLE_DIFF_FROM:` became `if False:`.
- RESEARCH ONLY skip removed: that `if` became `if False:`.

T9 is also caught when `data/real/` is removed, because it asserts `"data/real/" in TRIGGER_DIRS`.

Template greps:
- `grep -c "TRIGGER" templates/build-report.md templates/verification.md` → 1 and 1.
- `grep -c "work/067/03-handoff.md"` on the same files → 0 and 0.

Merge probe (04 Tests and checks): 069's build (8dc2c2d) is already in HEAD, and 070 is built on top of it. So the two merge as one branch and there is nothing to merge-tree. Every 070 hunk was placed in the spots 04 C1 reserved for it.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat` file list: scripts/check_pipeline.py, templates/build-report.md, templates/verification.md; new: tests/test_real_data_field.py). None of these is a TRIGGER path or under data/real/. The check's own run on this branch says `REAL-DATA FIELD: none`.

## Deviations from plan
- Placement was done by content, not by 04's line numbers, as 04 C1 and the orchestrator asked. The REAL-DATA FIELD print sits right after `RESEARCH CODE:`, which is 04's "after L650", and before 069's ORPHAN LOG and INBOX lines. The return hunk is on 069's final `return` line. 069's early `return 1` on a bad INBOX is unchanged and still exits 1.
- `real_data_field(cutoff=UNTRACKED_FROM, walked=None)` has the same default signature as `untracked_changes` and `research_code`. When it is called with git but no `walked`, it runs `_walk(cutoff)` itself. main always passes `walked`, so behaviour is unchanged.
- T2's comment-only body is a shortened copy of the template comment. It keeps the `down to TOTAL.` text and the `not required (...)` text, which are the parts that could fool a substring match.
- Helper functions in the new test file: `_rd_item`, `_check`, `_trigger_commit`, `_config_literals`, `_imports`. These are fixture plumbing, not tests.
- Nothing else deviates.

## Recurring issues
Recurring issues checked (item 013): RI-001, RI-002, RI-013, RI-010, RI-007, RI-008, RI-012, RI-011, RI-009.
- RI-001 (ESCALATED): every selector has a real count:
  - TRIGGER is 8, and T9 checks equality with the derived set.
  - The real repo gives `REAL-DATA FIELD: none`, an empty result stated as a result.
  - The positive control at cutoff 63 names 063 and 065, as expected.
- RI-002 (ESCALATED): every absent input has a named result and a test (T8, T13-T17, T12b/c). None of them passes silently.
- RI-013 (OPEN): the "nothing checks the 05/06 field → 070" gap is closed. Gap (o) remains: the check proves a paste exists, not that it is current.
- RI-010 (GUARDED): this is a script check plus an ID cutoff (WHOLE_DIFF_FROM = 70).
- RI-007 (GUARDED): the 053/062 code is untouched. RESEARCH ONLY items are left to 062 (T18).
- RI-008 (GUARDED): stdlib only, and `python3.11 -m py_compile` gives no error.
- RI-012 (GUARDED): TOTAL is a fullmatch tied to `diff_reports.diff_dirs` (T10). The substring mutation fails T2.
- RI-011 (GUARDED): no branch-diff code changed.
- RI-009 (GUARDED): mutations and probes ran only in a scratch `git worktree` under the scratchpad, which was removed afterwards. work/069 was not touched.

Guardrail status lines for A1 to copy on main:
- RI-013: guardrail built (070); the 05/06 field is now checked by check_pipeline.py from item 070. GUARDED when 067 and 070 are merged and the "file-wide TOTAL" mutation fails T5 on main.
- RI-010: 070 adds a script check with an ID cutoff; no check weakened.

## Round 2 (06 round 1 FAIL: problems 1-3)
Tests only. No code changed: `git diff --stat` shows only `tests/test_real_data_field.py | 74 +++` (74 insertions). No test exposed a code bug.

Files (commands run in /home/claude/df17, excluding work/ and logs/):
- new: `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` → 0
- changed: `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` → 1 (tests/test_real_data_field.py)

New tests in tests/test_real_data_field.py:
- T19 `test_t19_main_exits_1_when_git_log_fails` (problem 1): T1's clean fixture, `check_pipeline.main([...])` in-process, `_git("log", "--no-merges", ...)` patched to return `("", 128)`. It asserts `REAL-DATA FIELD: git log failed (item 070)`, that INCOMPLETE, SKIPPED, UNTRACKED CHANGE, RESEARCH CODE, A1 FAIL, LOG TIME and ORPHAN LOG are all `none`, and a return value of 1.
- T20 `test_t20_main_exits_1_for_triggered_id_without_request` (problem 1): item 160 (FULL) is committed open without its 07. The next commit adds 160's 07, edits 160's 05 (filled), and adds work/162/05-build-report.md and ccbot/realtest.py; 162 has no request.md. 053 stays quiet (160 is open at the parent) and so does 062 (gap (g): 160's 05 is in the unit). So `REAL-DATA FIELD: 162 (no work/162/request.md here)` is the only failing line, and the test asserts exit 1. Unlike T16, the exit 1 does not come from 062.
- T21 `test_t21_total_inside_prose_is_incomplete` (problem 2, RI-012), 4 cases, each a 05 section body outside any comment: `see 05: <TOTAL line> (copied)`, `TOTAL line below (<TOTAL line>)`, `TOTAL line below`, `the TOTAL: line is in the PR`. Each must give exactly `INCOMPLETE: 160 (05 Real-data effect has no diff_reports TOTAL line (<sha7> changes ccbot/realtest.py; item 070))` and exit 1.
- T22 `test_t22_total_line_inside_a_comment_does_not_count` (found by problem 3): with each mutation now changing one thing, "comments kept" on its own survived (27 passed). T2's comment holds no full TOTAL line, so fullmatch rejects it whether or not the comment is stripped. T22 puts a whole TOTAL line inside `<!-- ... -->` and expects the same INCOMPLETE entry and exit 1.

Mutations (problem 3): one change each, in a scratch `git worktree` at 7f5e345 with the new test file copied in, under /tmp/claude-0/-home-claude/4cc69c4f-899b-56b8-af6f-c0c8dcf01a44/scratchpad/wt070. A script applied each change to an exact pattern that occurs once, ran `python3 -m pytest -q -p no:cacheprovider tests/test_real_data_field.py`, and restored the original. The final check was `restored: True`. The worktree was then removed (`git worktree list | grep -c wt070` → 0). Output:
```
exit drops `or (real and real[2])`: 2 failed, 26 passed in 5.07s -> test_t19_main_exits_1_when_git_log_fails, test_t20_main_exits_1_for_triggered_id_without_request
no-request sets no `failed`: 1 failed, 27 passed in 4.98s -> test_t20_main_exits_1_for_triggered_id_without_request
"TOTAL" in line (comments still dropped): 4 failed, 24 passed in 5.06s -> test_t21_total_inside_prose_is_incomplete[quoted-total], test_t21_total_inside_prose_is_incomplete[total-colon], test_t21_total_inside_prose_is_incomplete[total-in-brackets], test_t21_total_inside_prose_is_incomplete[word-total]
"TOTAL:" in line: 3 failed, 25 passed in 5.13s -> test_t21_total_inside_prose_is_incomplete[quoted-total], test_t21_total_inside_prose_is_incomplete[total-colon], test_t21_total_inside_prose_is_incomplete[total-in-brackets]
TOTAL_LINE.search(line): 2 failed, 26 passed in 5.36s -> test_t21_total_inside_prose_is_incomplete[quoted-total], test_t21_total_inside_prose_is_incomplete[total-in-brackets]
comments kept (alone): 1 failed, 27 passed in 5.37s -> test_t22_total_line_inside_a_comment_does_not_count
first-parent units: 2 failed, 26 passed in 5.21s -> test_t19_main_exits_1_when_git_log_fails, test_t6_pr_merge_flags_only_the_item_whose_commit_triggers
file-wide TOTAL: 1 failed, 27 passed in 5.20s -> test_t5_total_outside_the_section_does_not_count
data/real/ removed: 2 failed, 26 passed in 5.09s -> test_t11_data_real_file_triggers, test_t9_trigger_matches_realtest_imports_and_config_reads
ccbot/pricing.py removed: 1 failed, 27 passed in 4.91s -> test_t9_trigger_matches_realtest_imports_and_config_reads
extra ccbot/data.py: 1 failed, 27 passed in 5.05s -> test_t9_trigger_matches_realtest_imports_and_config_reads
## in fence ends section: 1 failed, 27 passed in 4.75s -> test_t12_fences_and_headings[fenced-heading]
cutoff check removed: 1 failed, 27 passed in 4.11s -> test_t7_items_before_cutoff_are_not_checked
RESEARCH ONLY skip removed: 1 failed, 27 passed in 4.44s -> test_t18_research_only_item_is_062s
unclosed fence passes: 1 failed, 27 passed in 4.13s -> test_t12_fences_and_headings[unclosed]
no 05 passes: 1 failed, 27 passed in 5.07s -> test_t17_trigger_with_no_05_is_incomplete
06 not checked: 1 failed, 27 passed in 4.19s -> test_t2_comment_only_field_is_incomplete
restored: True
```
How each one-change mutation was made (check_pipeline.py):
- exit: `\` + `or (real and real[2]) else 0` became ` else 0`.
- no-request: the `failed = True` line after the no-request.md name was removed.
- `"TOTAL" in line`, `"TOTAL:" in line`, `TOTAL_LINE.search(line)`: each replaced `TOTAL_LINE.fullmatch(line.strip())` on its own. The comment strip was kept.
- comments kept (alone): `re.sub(r"<!--.*?-->", "", text, flags=re.S).splitlines()` became `text.splitlines()`. The match was kept.
- first-parent units: `"--no-merges"` became `"--first-parent", "-m"`. T19 also fails here, but only because its patch keys on `("log", "--no-merges")`. T6 is the real catch.
- file-wide TOTAL: `for line in section` became `for line in lines`.
- data/real/ removed: `TRIGGER_DIRS = ()`. pricing removed / extra data.py: edits to the TRIGGER tuple.
- `## ` in fence: `elif not fence and line.startswith("## ")` became `elif line.startswith("## ")`.
- cutoff, RESEARCH ONLY skip, no 05: each `if` became `if False:`.
- unclosed fence: `if fence:` in the for-else became `if False:`.
- 06 not checked: `("05", "06")` became `("05",)`.

The exit mutation was also run against the full suite in the scratch worktree: `2 failed, 382 passed, 1 skipped in 59.71s` (T19 and T20). In round 1 it gave 374 passed.

Test output (in /home/claude/df17):
```
python3 -m pytest -q -p no:cacheprovider tests/test_real_data_field.py
28 passed in 4.74s   (scratch copy, same file)
python3 -m pytest -q -p no:cacheprovider -rs
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items  (assert 1 == 0; output shows "A1 FAIL: 069")
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'
1 failed, 383 passed, 1 skipped in 58.86s
python3.11 -m py_compile tests/test_real_data_field.py → ok
```
The one failure does not come from 070. The concurrent A1 audit committed `e75703b Item 069: A1 result FAIL` on this branch during this round. test_repo_pipeline_has_no_skipped_items runs check_pipeline on HEAD, where 069 is now A1 FAIL, so it exits 1. The script is unchanged in this round, and the failure clears when 069 gets a later A1 PASS line. 385 tests total, counted by pytest (1 failed + 383 passed + 1 skipped). 7 of them are new in this round (T19, T20, T21 x4, T22), and the rest already ran in round 1 or come from 069 round 2 in HEAD. 383 passed.

`python3 scripts/check_pipeline.py` (in /home/claude/df17, exit 0): `070: in progress (FULL: next 07)`, `A1 FAIL: 069`, `INCOMPLETE: none`, `UNTRACKED CHANGE: none`, `RESEARCH CODE: none`, `REAL-DATA FIELD: none`, `ORPHAN LOG: none`, `SKIPPED: none`. It also prints `MAIN AHEAD: origin/main has 1 commits not in HEAD`. That is the orchestrator's merge, not this item's.

Missing-data grep (`grep -rnE "fillna|nan_to_num|or 0|else 0|..." tests/test_real_data_field.py`): no hits (exit 1). ccbot/ and scripts/ are unchanged. No numeric dataclass defaults and no new `>`/`<` tests were added.

Connectivity: T19-T22 are collected by pytest (28 in the file). Each new test feeds the INCOMPLETE line, the REAL-DATA FIELD line or the exit value of main. No TODOs and no new files. 069's INBOX code, its tests and work/069 were not touched.

Recurring issues checked (round 2): RI-002, RI-012, RI-009, RI-001, RI-007, RI-008, RI-013.
- RI-002 (ESCALATED): both exit-1 results for absent inputs (git log failed; triggered ID with no request.md) are now tested through main's exit value.
- RI-012 (GUARDED): substring, `"TOTAL:"` substring and `search` each fail T21 on their own, and comment-keeping fails T22 on its own.
- RI-009: mutations ran only in the scratch worktree.
- RI-001: mutation counts and test counts above come from real runs.
- RI-007: T20 also checks that 053 and 062 report none, so the exit 1 is REAL-DATA FIELD's alone.
- RI-008: the 3.11 compile passes.
- RI-013: unchanged from round 1.

RI-012: GUARDED (070 round 2: T21 kills "TOTAL" in line, "TOTAL:" in line and TOTAL_LINE.search one change at a time; T22 kills dropping the comment strip)
RI-002: ESCALATED (070 round 2: main's exit 1 for "git log failed" and "no request.md" now tested, T19/T20)

## Round 3 (after A1 FAIL)
A1 (logs/audit/2026-11-18-070.md) failed 070 because the cutoff edge was untested: `WHOLE_DIFF_FROM = 100` and `<` -> `<=` survived the full suite. Fix, tests only, in tests/test_real_data_field.py next to T7. scripts/, templates/, ccbot/ are unchanged (`git diff --stat`: `tests/test_real_data_field.py | 35 +++`).
- **T7b** `test_t7b_cutoff_edge_item_070_is_checked`: item `070` with a ccbot/realtest.py commit and no Real-data section -> `REAL-DATA FIELD: 070`, `INCOMPLETE: 070 (05 has no '...' section (<sha7> changes ccbot/realtest.py; item 070)`, exit 1.
- **T7c** `test_t7c_cutoff_edge_pair_in_one_repo`: 069 and 070 each with their own trigger commit -> only 070 named, exit 1.
- **T7d** `test_t7d_cutoff_constant_matches_template_comment` (x2): `WHOLE_DIFF_FROM == 70` and equals the "from item 070" in templates/build-report.md and templates/verification.md.
- T7 (069 not checked) is kept as is.

File counts (from commands, excluding work/ and logs/):
```
git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'   -> 0
git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'   -> 1
```

Mutations (scratch worktree `scratchpad/i2-070r3` at aace9dc with the new test file copied in; `python3 -m pytest -q tests/test_real_data_field.py`; worktree removed afterwards):

| Mutation | Result |
|---|---|
| `WHOLE_DIFF_FROM = 100` | killed: 4 failed, 28 passed (T7b, T7c, T7d x2) |
| `WHOLE_DIFF_FROM = 71` | killed: 4 failed, 28 passed (T7b, T7c, T7d x2) |
| `WHOLE_DIFF_FROM = 69` | killed: 4 failed, 28 passed (T7, T7c, T7d x2) |
| `int(item) < WHOLE_DIFF_FROM` -> `<=` | killed: 2 failed, 30 passed (T7b, T7c) |

Each mutation is also killed by a behaviour test alone (T7b or T7/T7c), not only by the T7d constant check.

A1's live probe replayed (scratch branch `scratch-i2-070r3-probe`, one commit cc1bd88 adding a comment to ccbot/costs.py and a line to work/070/05; branch deleted afterwards):
```
as built:              exit 1
A1 FAIL: 069, 070
INCOMPLETE: 070 (05 Real-data effect has no diff_reports TOTAL line (cc1bd88 changes ccbot/costs.py; item 070); 06 Real-data effect has no diff_reports TOTAL line (cc1bd88 changes ccbot/costs.py; item 070))
REAL-DATA FIELD: 070
WHOLE_DIFF_FROM = 100: exit 1
A1 FAIL: 069, 070
INCOMPLETE: none
REAL-DATA FIELD: none
```
Same as A1's result; the 100 mutation is now caught by T7b/T7c/T7d.

Test output (in /home/claude/df17):
```
python3 -m pytest -q tests/test_real_data_field.py
32 passed in 4.49s
python3 -m pytest -q
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 403 passed, 1 skipped in 63.04s (0:01:03)
python3.11 -m py_compile tests/test_real_data_field.py -> ok
```
The one failure is the known one: its output shows `069: A1 FAIL (FULL; sent back ...)`, `070: A1 FAIL (FULL; sent back ...)`, `A1 FAIL: 069, 070`. It clears when both get a later A1 PASS line. 405 tests total from pytest (1 + 403 + 1); 4 are new in this round (file 28 -> 32).

`python3 scripts/check_pipeline.py` (exit 1): `069: A1 FAIL`, `070: A1 FAIL`, `A1 FAIL: 069, 070`, STUCK, AWAITING A1, IN PR, RULES BRANCH, ID CLASH, INCOMPLETE, UNTRACKED CHANGE, RESEARCH CODE, REAL-DATA FIELD, ORPHAN LOG, SKIPPED all `none`; LOG TIME none (048 legacy note); `INBOX: not checked (2026-11-17.md added in b268a22; its templates/daily-audit.md has no ## Inbox)`. Exit 1 is from A1 FAIL alone.

Missing-data grep (`grep -rnE "fillna|nan_to_num|or 0|..." ccbot/`): 37 hits, all pre-existing; ccbot/ is unchanged in this round, so no new or changed hit. The new tests add no numeric dataclass defaults and no `>`/`<` tests on data.

Connectivity: T7b, T7c, T7d are collected (32 in the file); each asserts on the REAL-DATA FIELD line, the INCOMPLETE line, main's exit or the template text. No TODOs, no new files. 069's code, tests and work/069 were not touched; the I3-069 scratch worktree was left alone.

Recurring issues checked (round 3): RI-001, RI-002, RI-007, RI-008, RI-009, RI-012, RI-013.
- RI-001 (ESCALATED): every count above is from a real run.
- RI-002 (ESCALATED): no value defaulted; unchanged code.
- RI-007/RI-008: unchanged; 3.11 compile ok.
- RI-009: mutations and the probe ran only in the scratch worktree/branch, both removed.
- RI-012 (GUARDED): unchanged from round 2.
- RI-013 (OPEN): the cutoff that decides which items are checked is now pinned at the edge (070 checked, 069 not).

RI-013: OPEN (070 round 3: cutoff edge pinned; WHOLE_DIFF_FROM 100/71/69 and `<=` each fail a test; GUARDED when 070 is merged and the probe fails on main)
