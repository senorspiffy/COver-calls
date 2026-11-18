# 06 Verification - 070
Verdict: PASS (round 2; earlier rounds: FAIL round 1)

All test runs and mutations were done in a scratch worktree at 875158e (the 070 build commit), never in /home/claude/df17. The build diff checked is 652a320..875158e.

## I1 audit (plan vs research)
- 04 follows 03's map step by step. The Rule trace covers steps 1-9 and D1-D7, and nothing is DROPPED.
- The three changes have sources:
  - C1: placement around 069's hunks and a new test file. Source: 069/04 C1, tests/test_paper.py L8, and the pytest import-mode doc.
  - C2: T15-T18, tests for the 4 untested rows in 03's Missing inputs.
  - C3: T9 uses equality and a precise AST shape.
- Extra research: the git-log `--no-merges` doc, and BXM_History.csv being covered by the data/real/ prefix. Both are sourced.
- No unsourced additions.
- Gap that I1 carried over from 03: the mutation "comments kept + substring → T2 fails" changes two things at once, so it never isolates the fullmatch (see problem 2). 04 also lists the exit-1 result for `git log failed` and for "no request.md" without any test that checks main's exit code for them (see problem 1).

## I2 audit (build vs plan)
The build matches 04 line by line:
- Constants come after LOG_TIME_EXCEPT and match 03 step 1 exactly.
- The docstring entry comes after RESEARCH CODE and has gaps (m)-(t).
- `_triggers`, `_field_gap`, `_item_triggers` and `real_data_field` come after `research_code()`.
- main has the 4 hunks: `real =`, `gaps`, the print after RESEARCH CODE, and the return.
- Both template comments are replaced.
- The new file tests/test_real_data_field.py has 18 functions and 21 collected tests.

The deviations in 05 are stated and harmless.

069 is untouched:
- `git diff 652a320..875158e -- work/069` → 0 lines.
- 0 changed lines in check_pipeline.py mention INBOX.
- Every INBOX/inbox line is identical before and after (22 lines, `diff` empty).

Connectivity re-done:
- `_triggers` → `_item_triggers` → `real_data_field` → main (entries join INCOMPLETE, the print, and `real[2]` in the exit).
- `_field_gap` → `real_data_field`.
- Template greps: TRIGGER 1/1, `work/067/03-handoff.md` 0/0.

Not a BUG item, so the RI-002 default-restore mutation does not apply. The grep reasons in 05 (4 `.get`/`or "none"`/`else` sites) are correct: "none" is printed only after the check ran, and every no-git or bad-cutoff case returns earlier.

## Tests re-run (output)
Scratch worktree at 875158e, Python 3.13.18:
```
python3 -m pytest -q -p no:cacheprovider tests/test_real_data_field.py
21 passed in 3.06s
python3 -m pytest -q -p no:cacheprovider
374 passed, 1 skipped in 58.68s
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars'
```
- The count matches 05 (374 = 353 + 21).
- `test_every_py_compiles_on_oldest_python` ran and passed. python3.11 is on PATH; python3.10 is not.
- `python3.11 -m py_compile scripts/check_pipeline.py tests/test_real_data_field.py` → ok.

`python3 scripts/check_handoff.py 070`:
```
sources count (unique URLs in 01-research.md): 1
fact-check rows: 60
totals line: 60 rows -> 40 as-is, 20 fixed, 0 removed
PASS
```

Real-repo probe at 875158e: `REAL-DATA FIELD: none`, `INCOMPLETE: none`, `SKIPPED: none`, exit 0. Runtime is real 0m0.750s. `git rev-list --no-merges --count 694bf4d..HEAD` → 91. 05 had 89, before 652a320 and 875158e were added.

Positive control, scratch, `WHOLE_DIFF_FROM = 63` (exit 1). It is the same as 05's:
```
INCOMPLETE: 063 (05 has no '## Real-data effect ...' section (addf948 changes ccbot/realtest.py; item 070); 06 ... (addf948 ...)), 065 (05 ... (e129253 changes ccbot/realtest.py; item 070); 06 ... (e129253 ...))
REAL-DATA FIELD: 063, 065
```

Mutations: one at a time, each restored from a backup copy, `pytest -q tests/test_real_data_field.py`. The rows marked I3 are new ones I added.
```
first-parent units:            1 failed -> t6
file-wide TOTAL:               1 failed -> t5
substring "TOTAL" in line ALONE (comments still dropped): 21 passed   <- SURVIVES
substring "TOTAL:" in line:    21 passed                              <- SURVIVES
TOTAL_LINE.search(line) instead of fullmatch(strip): 21 passed; full suite 374 passed, 1 skipped  <- SURVIVES
data/real removed:             2 failed -> t9, t11
pricing removed:               1 failed -> t9
fence ends section:            1 failed -> t12[fenced-heading]
cutoff removed:                1 failed -> t7
RESEARCH ONLY skip removed:    1 failed -> t18
I3: unclosed fence passes:     1 failed -> t12[unclosed]
I3: no 05 passes:              1 failed -> t17
I3: 06 not checked:            1 failed -> t2
I3: exit drops `or (real and real[2])`: 21 passed; full suite 374 passed, 1 skipped  <- SURVIVES
I3: no-request sets no `failed`: 21 passed                            <- SURVIVES
```

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat 652a320..875158e`: logs/implementation/2026-11-17.md, scripts/check_pipeline.py, templates/build-report.md, templates/verification.md, tests/test_real_data_field.py, work/070/05-build-report.md). None of these is a TRIGGER path or under data/real/. The check's own run at 875158e says `REAL-DATA FIELD: none`.

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-002, RI-007, RI-008, RI-010, RI-011, RI-012, RI-013 (RI-003, RI-004, RI-005, RI-006, RI-009 not applicable or covered below)
- RI-001 (ESCALATED): I re-ran the counts. TRIGGER = 8 (T9 equality passes), the real repo gives `none`, and the cutoff-63 control gives 063 and 065, the same as 05.
- RI-002 (ESCALATED): every absent input has a named result. But two of them are meant to give exit 1, and nothing tests that: `git log failed`, and a triggered ID with no request.md. If the `real[2]` exit term is removed, both would exit 0 with all 374 tests green (problem 1).
- RI-012 (GUARDED): **FAIL.** "Filled" is decided by matching text, and no negative test puts the TOTAL pattern inside other text where the matcher can see it. T2's `TOTAL.` sits inside an HTML comment, and the comment is stripped before matching. So the substring and `search` mutations survive (problem 2). 05's sentence "The substring mutation fails T2" holds only when comment-keeping is mutated as well.
- RI-013 (OPEN): the "→ 070" gap is closed in substance. Gap (o) is stated: the check proves a paste exists, not that it is current.
- RI-010 (GUARDED): the change is a script check plus an ID cutoff, and no check is weakened.
- RI-007 (GUARDED): the 053/062 code is untouched, and T18 passes.
- RI-008: the 3.11 compile passes, and the oldest-Python test ran.
- RI-011: no branch-diff code changed.
- RI-009: all work was done in a scratch worktree, and 069's files and lines are unchanged.
- RI-003, RI-004, RI-005, RI-006: no calendar is involved. I re-checked the worked examples and counts in 03 (cutoff 69/70, T6 attribution, 14 − 2 + 2 + 3 = 17, plus C2 = 21) and they hold.

## Pipeline line (step 2)
check_pipeline line: `070: in progress (FULL: next 07)`
(Run in /home/claude/df17 after this file was written. 07 is not written because the verdict is FAIL.)

## Sent back / sent to Audit
Sent back to I2 (tests only; the code logic is right):
1. **The exit path for `failed` is untested.** If `or (real and real[2])` is removed from main's return, the full suite still passes (374 passed, 1 skipped). T15 calls `real_data_field` directly and never checks main's exit code. T16's exit 1 comes from 062 (`SKIPPED: 162`, `RESEARCH CODE: 162`), not from REAL-DATA FIELD. Fix: add a test that runs `check_pipeline.main([...])` in-process with `_git("log", ...)` patched to fail, in an otherwise clean fixture, and asserts `REAL-DATA FIELD: git log failed (item 070)` and a return value of 1. Then confirm that the exit mutation fails it.
2. **RI-012: there is no negative test with the TOTAL pattern inside other text.** Add a case whose section body, outside any comment, quotes the line inside prose, for example `see 05: TOTAL: files 1, only-before 0, ... columns changed 0 (copied)`, plus a plain `TOTAL line below` line. The case must give INCOMPLETE. Then confirm that the `"TOTAL" in line`, `"TOTAL:" in line` and `TOTAL_LINE.search(line)` mutations each fail a test.
3. Update 05's mutation list so that each mutation changes one thing, and paste the new results.

For I1 (note only, no re-plan needed): the plan copied 03's two-change mutation ("comments kept + substring"), and it listed exit-1 results without a test that checks the exit code. When a plan names a mutation, it should change a single thing.

Sent to Audit: no.

# Round 2
Verdict: PASS (round 2; earlier rounds: FAIL round 1)

All runs and mutations were done in a scratch worktree at a237da7 (`git worktree add .../scratchpad/i3-070r2 a237da7`), never in /home/claude/df17. The worktree was removed afterwards.

## I1 audit (round 2)
No re-plan. Round 1's note to I1 (single-change mutations, exit-1 results need an exit test) is met by I2's round-2 list in 05.

## I2 audit (round 2): diff 7f5e345..a237da7
- `git diff --stat 7f5e345 a237da7`: tests/test_real_data_field.py +74, work/070/05 +79, and 069's files (logs/audit/2026-11-18-069.md, work/069/07, logs/implementation/2026-11-18.md: e75703b, the A1 FAIL for 069). `git diff 7f5e345 a237da7 -- scripts` is empty: no code changed.
- New tests T19-T22 match 05's Round 2 text:
  - T19: main in-process, `_git("log","--no-merges",...)` patched to fail, asserts `REAL-DATA FIELD: git log failed (item 070)`, every other line `none`, return 1. Fixes problem 1.
  - T20: triggered ID 162 with no request.md, 053 and 062 quiet, exit 1 from REAL-DATA FIELD only. Fixes problem 1.
  - T21 (4 cases): TOTAL inside prose, outside comments, gives INCOMPLETE. Fixes problem 2 (RI-012).
  - T22: a whole TOTAL line inside an HTML comment gives INCOMPLETE. It was added because the one-change "comments kept" mutation survived (problem 3).
- 05's mutation list now changes one thing per mutation (problem 3).

## Tests re-run (round 2 output)
Scratch at a237da7, Python 3.13.18:
```
python3 -m pytest -q -p no:cacheprovider -rs
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items   (assert 1 == 0)
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars'
1 failed, 383 passed, 1 skipped in 59.38s
```
The failure is not a 070 defect:
- `check_pipeline.py` at a237da7 exits 1 with `A1 FAIL: 069` as its only failing line. INCOMPLETE, SKIPPED, UNTRACKED CHANGE, RESEARCH CODE, REAL-DATA FIELD and ORPHAN LOG are all `none`, and LOG TIME shows only 048's old exception.
- I committed a throwaway scratch commit (detached HEAD, 2bb50d1, discarded with the worktree) that drops 069's last 07 line (`A1 result: FAIL ...`). Then `069: awaiting A1 (FULL)`, `A1 FAIL: none`, check_pipeline exit 0, `test_repo_pipeline_has_no_skipped_items` 1 passed, and the full suite gives **384 passed, 1 skipped in 59.65s**. 384 + 1 = 385, the same as 05's count.
- `python3 -m pytest -q tests/test_real_data_field.py` → 28 passed (05: 28).
- python3.11 is on PATH, python3.10 is not. `test_every_py_compiles_on_oldest_python` ran and passed with 3.11. `python3.11 -m py_compile scripts/check_pipeline.py tests/test_real_data_field.py` → ok.

`python3 scripts/check_handoff.py 070` (scratch, a237da7):
```
sources count (unique URLs in 01-research.md): 1
fact-check rows: 60
totals line: 60 rows -> 40 as-is, 20 fixed, 0 removed
PASS
```

Mutations: one change each, done by a script with an exact pattern that occurs once (asserted). Each was restored, and the script printed `restored: True`. Run: `pytest -q -rf tests/test_real_data_field.py`.
```
exit drops `or (real and real[2])`: 2 failed, 26 passed -> t19, t20
"TOTAL" in line (strip kept):       4 failed, 24 passed -> t21[quoted-total, total-in-brackets, word-total, total-colon]
"TOTAL:" in line:                   3 failed, 25 passed -> t21[quoted-total, total-in-brackets, total-colon]
TOTAL_LINE.search(line):            2 failed, 26 passed -> t21[quoted-total, total-in-brackets]
comment strip removed (text.splitlines()): 1 failed, 27 passed -> t22
no-request `failed = True` removed: 1 failed, 27 passed -> t20
restored: True
```
These are the same counts and names as 05 Round 2. All 3 round-1 problems are fixed. Both round-1 survivors (the exit term, no-request) are now killed, and the three TOTAL-matcher swaps and the comment-strip removal each fail a test.

## Real-data effect (round 2)
not required (`git diff --stat 7f5e345 a237da7 -- . ':!work' ':!logs'`: tests/test_real_data_field.py only). Not a TRIGGER path and not under data/real/. `REAL-DATA FIELD: none` at a237da7.

## Recurring issues checked (round 2)
Recurring issues checked: RI-001, RI-002, RI-007, RI-008, RI-009, RI-010, RI-011, RI-012, RI-013 (RI-003 to RI-006 not applicable: no calendar, no worked example, and no hand total changed in round 2)
- RI-001 (ESCALATED): every count above comes from a run: 28 file tests, 385 suite tests, and the mutation counts. They match 05.
- RI-002 (ESCALATED): both absent-input exit-1 paths (git log failed; no request.md) are now tested through main's return value (T19, T20), and both mutations fail. No value is defaulted.
- RI-012 (GUARDED): there are now negative tests with the TOTAL pattern inside prose (T21) and inside a comment (T22). The substring, `TOTAL:` and `search` swaps and the strip removal each fail a test on their own. Problem 2 is fixed.
- RI-013 (OPEN): unchanged. 070 is the "→ 070" fix, and gap (o) is stated.
- RI-007 (GUARDED): T20 asserts that RESEARCH CODE and UNTRACKED CHANGE are `none`. The 069 A1 FAIL line is RI-007's own check working.
- RI-008: the 3.11 compile passes. python3.10 is not on PATH.
- RI-009: everything was done in a scratch worktree. 069's uncommitted edit to scripts/check_pipeline.py in /home/claude/df17 was not touched.
- RI-010: `--log` is used for the log line. No check is weakened.
- RI-011: no branch-diff code changed.

## Pipeline line (round 2)
check_pipeline line: `070: awaiting A1 (FULL)`
(Run in /home/claude/df17 after 06 and 07 were written. That tree also holds 069's uncommitted I2 edit to scripts/check_pipeline.py.)

## Sent back / sent to Audit (round 2)
Sent to Audit: yes (work/070/07-audit-task.md). Sent back: nothing.
Note for the orchestrator: `test_repo_pipeline_has_no_skipped_items` stays red on this branch until 069 gets a later A1 PASS line. It is not a 070 defect (see above).

## Round 3 (after A1 FAIL, logs/audit/2026-11-18-070.md)
Verdict: **PASS**. I2's fix is 4789b44 (tests only). All runs in scratch worktree `scratchpad/i3-070r3` at 4789b44 (removed afterwards); in /home/claude/df17 only this file and 07 were edited.

### I1 audit (round 3)
No new plan. The fix is the one A1 asked for (an item-070 edge test next to T7, keep T7's 069 case, optional constant-vs-template assert). Nothing unsourced added.

### I2 audit (round 3): diff aace9dc..4789b44
`git diff --stat aace9dc..4789b44`: `logs/implementation/2026-11-18.md | 1 +`, `tests/test_real_data_field.py | 35 +++`, `work/070/05-build-report.md | 64 +++`. No scripts/, templates/ or ccbot/ change. New: T7b (item 070 trigger, empty field -> `REAL-DATA FIELD: 070`, INCOMPLETE, exit 1), T7c (069 + 070 in one repo -> only 070), T7d x2 (`WHOLE_DIFF_FROM == 70` and matches "from item 070" in both templates). T7 unchanged. 05 Round 3 matches the diff.

### Mutations re-run by I3 (scripts/check_pipeline.py, one at a time, restored; `pytest -q tests/test_real_data_field.py` with T7d deselected so only behaviour tests count)
| Mutation | Result (behaviour tests only) |
|---|---|
| `WHOLE_DIFF_FROM = 100` | killed: 2 failed (T7b, T7c), 28 passed |
| `WHOLE_DIFF_FROM = 71` | killed: 2 failed (T7b, T7c), 28 passed |
| `WHOLE_DIFF_FROM = 69` | killed: 2 failed (T7, T7c), 28 passed |
| L645 `int(item) < WHOLE_DIFF_FROM` -> `<=` | killed: 2 failed (T7b, T7c), 28 passed |
Matches 05 (05's counts include T7d; with T7d the totals are 4/4/4/2 failed, as I2 reports).

### Tests re-run (round 3)
- `pytest -q tests/test_real_data_field.py`: `32 passed`.
- Full suite at 4789b44: `1 failed, 403 passed, 1 skipped in 63.55s`; failure `test_repo_pipeline_has_no_skipped_items`.
- Known-failure check: scratch commit 7084343 dropped the last `A1 result: FAIL` line of work/069/07 and work/070/07 -> that test `1 passed`, `check_pipeline.py` exit 0. So the only failure is `A1 FAIL: 069, 070`. Scratch commit discarded (`reset --hard 4789b44`).
- `test_every_py_compiles_on_oldest_python`: passed with python3.11; python3.10 not on PATH.
- `check_handoff.py 070`: `fact-check rows: 60`, `totals line: 60 rows -> 40 as-is, 20 fixed, 0 removed`, `PASS`.
- `check_pipeline.py` at 4789b44: exit 1; `A1 FAIL: 069, 070`; STUCK, IN PR, RULES BRANCH, ID CLASH, INCOMPLETE, UNTRACKED CHANGE, RESEARCH CODE, REAL-DATA FIELD, ORPHAN LOG, SKIPPED all `none`; LOG TIME none (048 legacy note).
- Connectivity: T7b/T7c/T7d are collected (28 -> 32) and each assert on output, exit code or template text.

### Real-data effect (round 3)
not required: only tests/, work/, logs/ changed; none is a TRIGGER path.

### Recurring issues checked (round 3)
Recurring issues checked: RI-001, RI-002, RI-007, RI-008, RI-009, RI-010, RI-011, RI-012, RI-013 (RI-003 to RI-006 not applicable: no calendar, worked example or hand total changed)
- RI-001 (ESCALATED): every number above is from a run in this round.
- RI-002 (ESCALATED): no code changed; no value defaulted.
- RI-007: the A1 FAIL lines are the check working; nothing used before its step.
- RI-008: 3.11 compile ok; 3.10 absent.
- RI-009: all runs in the scratch worktree; 069's files untouched.
- RI-010: log line written by `--log`.
- RI-011: no branch-diff code changed.
- RI-012 (GUARDED): unchanged from round 2 (T21/T22).
- RI-013 (OPEN): the cutoff is now pinned at the edge (070 checked, 069 not) by behaviour tests. GUARDED when 070 is merged and the probe fails on main.

### Pipeline line (round 3)
check_pipeline line: `070: A1 FAIL (FULL; sent back, needs a later A1 PASS line (item 042))`
(Not SKIPPED or INCOMPLETE; it clears when A1 writes a later PASS line. Run in /home/claude/df17 after 06 and 07 were written.)

### Sent back / sent to Audit (round 3)
Sent to Audit: yes (work/070/07-audit-task.md, round 3 section). Sent back: nothing.
