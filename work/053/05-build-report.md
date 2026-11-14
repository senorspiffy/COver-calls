# 05 Build report - 053
## Changes made (file: what changed)
- scripts/check_pipeline.py: constants `CODE_PATHS` (ccbot/, config/, scripts/, tests/, .claude/, templates/), `UNTRACKED_FROM = "694bf4d0038e25bb82bd111018fbd67a94bbc74d"` (`git rev-parse HEAD` read right before this item's first code commit, comment "never move it forward"), `STEP_FILE` (work/<ID>/01-06 names). New `_open_at(parent, item)` (PRE_A1_LINE/LEGACY closed; 07 absent, no `A1 result:` line, or last FAIL → open) and `untracked_changes(cutoff)` (None without git; cutoff checks with shallow/full split; first-parent walk `<cutoff>..HEAD`; each commit vs its first parent by `diff-tree -r --name-only --no-renames`). `main()` parses `--today` and `--untracked-from` in any order, prints `UNTRACKED CHANGE:` after `LOG TIME:`, and the failed flag joins the exit condition. Docstring: usage line and an `UNTRACKED CHANGE` entry with known gaps (a)-(f).
- tests/test_pipeline_check.py: helper `_root`; the 14 git-fixture runs (L200, L214, L240, L261, L276, L417, L437, L446, L480, L497, L501, L542, L548, L584) pass `--untracked-from _root(...)`; `test_log_time_not_checked_outside_git` asserts `UNTRACKED CHANGE: not checked (no git)`. Helpers `_write`, `_commit`, `_commit_sha`, `_history`, `_untracked`. 12 new tests: (a) `test_completed_item_note_with_config_is_untracked`, (b) `test_new_item_step_file_covers_code`, (c) `test_merge_bringing_untracked_commit_is_flagged`, (d) `test_cutoff_missing_in_shallow_clone_not_checked`, (e) `test_cutoff_missing_in_full_repo_fails`, (f) `test_commits_before_cutoff_ignored`, (g) `test_audit_file_never_covers_code`, (h) `test_pr_merge_with_a1_pass_on_branch_is_covered`, (i) `test_a1_fail_item_covers_its_rework`, (j) `test_legacy_and_pre_a1_items_never_cover`, (k) `test_rename_out_of_code_path_is_flagged`, `test_untracked_from_is_fixed`.
- .claude/commands/run-item.md: new last paragraph (follow-up = new item, 053; I2 commits code with its 05; PRs merged with "Create a merge commit"; no `UNTRACKED CHANGE:` entry allowed).
- .claude/agents/a1-auditor.md L20: extended with the `UNTRACKED CHANGE:` rule, follow-up = new item (053), A1's daily commits change only logs/ and work/.
- config/tickers.json PBR: values unchanged (`last_earnings` 2026-11-10; `next_earnings`, `ex_div_date`, `dividend` null). `sources` replaced by the three strings of plan file 5 (Petrobras Agência results URL, Petrobras dividend URL, stockanalysis dividend URL). No new keys.
- ccbot/tickers.py `enrich`: estimate only when `_d(f["last_earnings"]) < day.date` (change 7, strict); docstring sentence added.
- ccbot/missing.py `tickers.last_earnings`: text appended "a last_earnings on or after the scan date is unknown on that date (053)"; effect stays `block`.
- tests/test_practice.py: shared `_blocked_for_dec_18(day)`; `test_earnings_known_for_dec_18_on_2026_11_09` → `{"PBR"}` (docstring "PBR reports 2026-11-10, after this day (053)"); new `test_earnings_known_for_dec_18_on_2026_11_11` → `set()`.
- tests/test_paper.py: new `test_enrich_future_last_earnings_is_unknown` (11-09 and 11-10 unknown; 11-11 → 2027-01-19, estimated).

File counts: `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` → 0 new; `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` → 9 changed. Plus this file (work/053/05-build-report.md) and the I2 log line.

## Connectivity check
- [x] every new function/rule is used (`untracked_changes` from `main()`; `_open_at` from `untracked_changes`; `CODE_PATHS`/`STEP_FILE`/`UNTRACKED_FROM` from `untracked_changes`; `--untracked-from` used by the fixtures; `UNTRACKED_FROM` also read by `test_untracked_from_is_fixed`)
- [x] every input has a source, every output has a consumer (git history and work/ at C^1 → `UNTRACKED CHANGE:` line and exit code → A1 daily run, I3, run-item end check, `test_repo_pipeline_has_no_skipped_items`; tickers.json PBR → `enrich` → screen EARNINGS/EARNINGS_UNKNOWN)
- [x] every branch ends in a defined result (no git → `not checked (no git)`; cutoff missing in shallow clone → `not checked (...)`, exit unchanged; cutoff missing/not ancestor in full clone → error, exit 1; `rev-list` or `diff-tree` failing → an error entry, exit 1 (see Deviations); no code files → commit skipped; no entries → `none`; last_earnings on/after the scan date → no estimate → EARNINGS_UNKNOWN when next_earnings is null)
- [x] no leftover TODOs or unused files
- Missing-data grep `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/` → 28 hits, none new or changed (no `+` line of `git diff -U0 ccbot/` matches). No new dataclass field. New comparison `_d(f["last_earnings"]) < day.date` compares two dates (no NaN possible; `_d` is only reached when the value is truthy); when False, no estimate is made, so it fails safe to EARNINGS_UNKNOWN.
- Feasibility numbers (real, from `enrich` on config/practice.json + config/tickers.json, Dec 18 expiry): 2026-11-09 → 12 of 13 clear, blocked ['PBR']; 2026-11-10 → 12 of 13, blocked ['PBR'] (report day, change 7); 2026-11-11 → 13 of 13, blocked []. PBR estimate on 2026-11-11: 2027-01-19. Commit filter on real history: 1 of 1 (de5406c, check 3 below).

## Test output (pasted, not summarized)
```
$ python3 -m pytest -q
........................................................................ [ 32%]
........................................................................ [ 65%]
........................................................................ [ 97%]
......                                                                   [100%]
221 passed, 1 skipped in 23.54s
```
(pre-build on this branch: `207 passed, 1 skipped in 21.14s`; +14 new tests.)
```
$ python3 -m pytest -q tests/test_pipeline_check.py tests/test_practice.py tests/test_paper.py -k "untracked or cutoff or completed_item or new_item or merge_bringing or audit_file or pr_merge or a1_fail_item or legacy_and or rename or dec_18 or future_last" -rA
PASSED tests/test_pipeline_check.py::test_check_handoff_all_legacy_and_fail
PASSED tests/test_pipeline_check.py::test_completed_item_note_with_config_is_untracked
PASSED tests/test_pipeline_check.py::test_new_item_step_file_covers_code
PASSED tests/test_pipeline_check.py::test_merge_bringing_untracked_commit_is_flagged
PASSED tests/test_pipeline_check.py::test_cutoff_missing_in_shallow_clone_not_checked
PASSED tests/test_pipeline_check.py::test_cutoff_missing_in_full_repo_fails
PASSED tests/test_pipeline_check.py::test_commits_before_cutoff_ignored
PASSED tests/test_pipeline_check.py::test_audit_file_never_covers_code
PASSED tests/test_pipeline_check.py::test_pr_merge_with_a1_pass_on_branch_is_covered
PASSED tests/test_pipeline_check.py::test_a1_fail_item_covers_its_rework
PASSED tests/test_pipeline_check.py::test_legacy_and_pre_a1_items_never_cover
PASSED tests/test_pipeline_check.py::test_rename_out_of_code_path_is_flagged
PASSED tests/test_pipeline_check.py::test_untracked_from_is_fixed
PASSED tests/test_practice.py::test_earnings_known_for_dec_18_on_2026_11_09
PASSED tests/test_practice.py::test_earnings_known_for_dec_18_on_2026_11_11
PASSED tests/test_paper.py::test_enrich_future_last_earnings_is_unknown
16 passed, 48 deselected in 2.74s
```
Check 2, `python3 scripts/check_pipeline.py` on this branch before the commit (last lines; full run exit 0):
```
053: in progress (FULL: next 05)
STUCK: none
AWAITING A1: none
IN PR: none
RULES BRANCH: none
ID CLASH: none
A1 FAIL: none
INCOMPLETE: none
LOG TIME: none (not checked: 048: built before 045's --log rule reached main; times typed by hand, not recoverable (item 049))
UNTRACKED CHANGE: none
ORPHAN LOG: none
SKIPPED: none
exit 0
```
Check 3, real-history probe (scratch worktree at de5406c outside the repo, removed afterwards):
```
$ git worktree add --detach <scratch>/wt-de5406c de5406c; cd <scratch>/wt-de5406c
$ python3 /home/claude/cover-calls/scripts/check_pipeline.py --untracked-from 96b7f94 | grep -E "UNTRACKED|SKIPPED:|INCOMPLETE:"
INCOMPLETE: none
UNTRACKED CHANGE: de5406c config/tickers.json tests/test_practice.py (item 053: code, config, tests or rules changed with no step file of an open work item; a follow-up to a completed item is a new item) (cutoff 96b7f94 from --untracked-from)
SKIPPED: none
exit 1
$ git diff --name-only de5406c^1 de5406c
config/tickers.json
tests/test_practice.py
work/048/05-build-report.md
```
Check 4:
```
$ git merge-base --is-ancestor 3ba835e 694bf4d0038e25bb82bd111018fbd67a94bbc74d; echo $?
0
$ git merge-base --is-ancestor 694bf4d0038e25bb82bd111018fbd67a94bbc74d HEAD; echo $?
0
$ git rev-parse --is-shallow-repository
false
```
Check 5 (scratch worktree at HEAD, removed afterwards):
```
$ git merge --no-edit origin/daily-fixes/2026-11-10
Already up to date.
$ git branch -r --merged HEAD | grep 11-10
  origin/daily-fixes/2026-11-10
```
PR #17's branch is already in this branch's history (052 was built under it), so the merge is a no-op and the check result is the check-2 result: `UNTRACKED CHANGE: none`.
Check 7:
```
$ python3.11 -m py_compile scripts/check_pipeline.py ccbot/tickers.py && echo ok
ok
```
Check 8:
```
$ grep -n "053" .claude/commands/run-item.md .claude/agents/a1-auditor.md | cut -c1-120
.claude/commands/run-item.md:16:A follow-up to a completed item (its 07 has `A1 result: PASS`) is a new item, never a no
.claude/agents/a1-auditor.md:20:   - Any commit since the last review that changes code or rules without a work item is
```
Check 6 (mutations) is I3's, in a scratch copy; not run here.

## Deviations from plan
- Two failure branches the plan did not name, added so no branch is a silent dead end: `rev-list` failing after the cutoff checks → `cutoff <c7>: git rev-list failed` (exit 1); `diff-tree` failing for one commit → entry `<c7> (git diff-tree failed)` (exit 1). Neither is reachable in the tests (both need a broken repo after the cutoff check passed).
- `main()` rejects an option without a value (e.g. a bare `--today`) with the usage text; before, `--today` alone raised IndexError.
- tests/test_practice.py: the 11-09 and 11-11 tests share a helper `_blocked_for_dec_18` instead of copying the loop.
- Plan "Expected result" says "same skips (12 in test_pipeline_check.py, 1 each ...)": read as the new git tests carrying `skipif` git missing; the suite's skip count stays 1.

## For the person (03 map step 9)
- Don't open a Jan 2027 PBR call without the ADR ex-date. The NYSE ADR record date is 2026-12-23 (Petrobras dividend notice); the ADR ex-date and amount per ADR are not published, so tickers.json keeps them null. No effect on Dec 18 calls (record date is 5 days after expiry).
- IDEA offered (separate item if wanted): "ADR ex = ADR record date (FINRA 11140), labelled", as a house rule like 040's estimate. Not built.
- Merge rule: merge this PR (and every later one) with "Create a merge commit", never squash or rebase. The cutoff 694bf4d must stay in main's history; a squash or rebase makes `check_pipeline.py` print `UNTRACKED CHANGE: cutoff 694bf4d not in HEAD's history` and exit 1.
- Report-day guard (change 7): a last_earnings on the scan date itself gives no estimate. PBR stays EARNINGS_UNKNOWN up to and including 2026-11-10 and clears Dec 18 from 2026-11-11 (estimate 2027-01-19).
- For A1: the look-ahead in `tickers.enrich` (an estimate from a last_earnings after the scan date, which 3ba835e's 11-09 test relied on) is a possible RI-002 occurrence; A1 decides.

## Recurring issues checked (I2)
RI-007 (this item: guardrail built and probed on real history, 1 of 1), RI-002 (missing-data grep, no new defaults; look-ahead guard fails safe; no PBR value filled), RI-001 (feasibility counts recorded above from real data), RI-008 (python3.11 py_compile ok; no 3.12-only syntax), RI-009 / RI-011 (first-parent walk, no merge-base; scratch worktrees only, outside the repo), RI-010 (log line written with `--log` right after this file, before the commit; code committed together with this 05), RI-006 (file counts from the commands above), RI-003 / RI-004 / RI-005 (no new dates or worked examples beyond R3's; fixtures (a), (h), (g) match R3's three examples).

RI-007: guardrail built (053); GUARDED when merged and a commit shaped like 3ba835e after the cutoff gives `UNTRACKED CHANGE:` and exit 1.
RI-002: 053 makes `enrich` ignore a last_earnings on or after the scan date (no estimate → EARNINGS_UNKNOWN); possible occurrence for A1 to judge (3ba835e's 11-09 expectation relied on the look-ahead).
