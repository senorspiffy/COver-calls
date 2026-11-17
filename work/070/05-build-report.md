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
