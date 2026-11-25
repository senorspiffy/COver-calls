# 06 Verification - 084
Verdict: PASS (round 2; earlier rounds: FAIL round 1)
Sent back to: none

Head verified: 0583289 ("Item 084: I2 round 2 - negative test for the rule-constant match (RI-012)"), branch daily-fixes/2026-11-20, parent 6312f99. I checked it in the clean scratch worktree /tmp/claude-0/wt084b (`git rev-parse --is-shallow-repository`: false; `git status --short`: empty). Round 2 changes `scripts/check_pipeline.py` (docstring only, +4/-1) and `tests/test_pipeline_check.py` (+33), plus 05 and I2's log line (`git show --stat 0583289`). Mutations ran in a `cp -a` copy of the worktree at /tmp/claude-0/-home-claude/8f94cbd2-523d-52d1-8971-85df3e672dc0/scratchpad/i3-084-r2-mut/wt, using the mutation script mut.py in that folder. They never ran in /home/claude/cover-calls. Repo HEAD has since moved to 55893e5 (086's I1 plan, round 2), which touches no 084 file and no file under scripts/ or tests/. Nothing was committed or pushed, and nothing was connected to a brokerage.

## I1 audit (plan vs research)
No change to 04 in round 2. My round-1 audit still holds: the plan follows 03's steps 0-7 and every correction row, and it has no unsourced addition. The new test is the one F1 asked for (I3 round 1), and 05 records it as Deviation 6. I1 is not sent anything.

## I2 audit (build vs plan)
I checked round 2 against F1 line by line (`git diff 6312f99 0583289 -- scripts tests`):
- The test `test_rule_seen_ignores_constant_inside_other_text[form]` has 4 cases: `comment`, `longer name`, `string`, and `all three` (my round-1 probe text, verbatim). Each case builds a tmp repo. Its root commit's RULE_FILE has both constants only inside other text, and a second commit adds the defective item 150. The test asserts `_rule_seen(..., "05", "TESTS_FORMAT_FROM") == (False, sha7)` and `_rule_seen(..., "06", "VERDICT_FROM") == (False, sha7)`. It also asserts that the CLI's `RULE NOT SEEN:` line equals `SEEN_150` (both pairs, with that sha7), plus `INCOMPLETE: none` and exit 0. This covers everything F1 asked for: both constants, all three forms, the `(False, sha7)` result, the RULE NOT SEEN listing, and not INCOMPLETE.
- The docstring names the remaining gap, as F1 asked: a column-0 `<CONST> = ` line inside a triple-quoted string still reads as "seen". That direction is strict, because the new rule is kept.
- No code line changed in check_pipeline.py. The only `+`/`-` lines are in the docstring. The 086 code in the tree (LOG BATCH, rule D) is untouched.
- Connectivity: the new test is collected and runs (4 cases pass). It reaches `_rule_seen` both directly and through the CLI, and adds no new function or branch. `git diff -U0 6312f99 0583289 | grep '^+' | grep TODO` gives only 05's checklist line.
- One point for the record, not a defect: in the `all three` case TESTS_FORMAT_FROM appears only as the longer name. The `comment` and `string` cases cover it in those forms, and every case is checked on its own.

## Tests re-run (output)
Full suite at 0583289 in /tmp/claude-0/wt084b:
```
$ python3 -m pytest -q -p no:cacheprovider -rs
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_old_06_without_round_headers_unchanged
FAILED tests/test_pipeline_check.py::test_i3_fail_target_not_stated - Asserti...
FAILED tests/test_pipeline_check.py::test_pass_without_sent_back_none_is_incomplete
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'
4 failed, 637 passed, 1 skipped in 86.76s (0:01:26)
```
This matches 05's count (4 failed, 637 passed, 1 skipped). None of the 4 failures comes from 084. To show that, I put back 416835f's (pre-round-2) check_pipeline.py and test_pipeline_check.py in the scratch copy and got the same 4:
```
== HEAD~1 (416835f) files, whole tests/test_pipeline_check.py
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_old_06_without_round_headers_unchanged
FAILED tests/test_pipeline_check.py::test_i3_fail_target_not_stated
FAILED tests/test_pipeline_check.py::test_pass_without_sent_back_none_is_incomplete
4 failed, 269 passed in 32.46s
restored-identical
```
Three of them come from 086's not-computable text (086 is back with I1). `test_repo_pipeline_has_no_skipped_items` fails on the repo's pipeline state: `I3 FAIL: 081, 084, 086`. This PASS removes 084 from that list, but 081 and 086 still keep the test red.

`tests/test_safety.py::test_every_py_compiles_on_oldest_python` ran (python3.11 is on PATH; python3.10 is absent): `1 passed`. `python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py`: OK.

Mutations M1-M7, plus my own M8, ran in the scratch copy. Each one is a single exact-match replacement (asserted count 1) taken from the saved original. Afterwards I restored the file, and `cmp` with the worktree file says identical. The test filter was `-k "constant_inside or rule_not_seen or unseen or rule_anchor or rule_seen or write_log_stays or repo_pipeline"`. The unmutated baseline is `1 failed (test_repo_pipeline_has_no_skipped_items, pre-existing), 12 passed`.
```
== M1  (_rule_seen returns (None, "") at once)
FAILED repo_pipeline, rule_not_seen_item_merged_beside_rules_branch, rule_not_seen_still_checks_old_rule,
       rule_anchor_git_failure_is_incomplete, rule_anchor_without_rule_file, rule_not_seen_shallow_and_no_git,
       rule_seen_positive_control_on_head, constant_inside_other_text[all three|comment|longer name|string]
11 failed, 2 passed, 264 deselected in 3.73s
== M2  (rf"^{const}_X = ")
FAILED repo_pipeline, rule_not_seen_item_merged_beside_rules_branch, rule_not_seen_still_checks_old_rule,
       rule_seen_positive_control_on_head
4 failed, 9 passed, 264 deselected in 4.59s
== M3  (failed add-commit log -> (False, "x"))
FAILED repo_pipeline, rule_anchor_git_failure_is_incomplete
2 failed, 11 passed, 264 deselected in 4.57s
== M4  (--first-parent on the add-commit log)
FAILED repo_pipeline, rule_not_seen_item_merged_beside_rules_branch, rule_not_seen_still_checks_old_rule,
       rule_anchor_git_failure_is_incomplete, rule_not_seen_shallow_and_no_git, rule_seen_positive_control_on_head
6 failed, 7 passed, 264 deselected in 4.93s
== M5  (_anchor_env never reports shallow)
FAILED repo_pipeline, rule_not_seen_shallow_and_no_git
2 failed, 11 passed, 264 deselected in 4.59s
== M6  (re.search(rf"{const} = ", text): no ^ / re.M)
FAILED repo_pipeline, constant_inside_other_text[all three], [comment], [longer name], [string]
5 failed, 8 passed, 264 deselected in 4.52s
== M7  ((const in text))
FAILED repo_pipeline, constant_inside_other_text[all three], [comment], [longer name], [string]
5 failed, 8 passed, 264 deselected in 4.80s
== M8  (I3's own: rf"\b{const} = ", no ^ / re.M), -k constant_inside
FAILED constant_inside_other_text[all three], [comment], [string]
3 failed, 1 passed, 273 deselected in 0.68s
restored-identical
```
Every mutation fails at least one test besides the pre-existing repo_pipeline failure. M1-M5 fail the same tests as in round 1; under M1 the 4 new cases fail as well. M6 and M7 survived round 1 (247 passed) and now fail all 4 new cases, which closes F1. M8 is a word-boundary variant. It is not the same as M6: it correctly ignores `OLD_..._FROM`, but the comment and string cases still catch it.

Done check, in /tmp/claude-0/wt084b at 0583289 (before this 06):
```
$ python3 scripts/check_pipeline.py     # exit=1 (I3 FAIL: 081, 084, 086 -- open send-backs)
083: complete (FULL)
084: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))
I3 FAIL: 081, 084, 086
INCOMPLETE: none
RULE NOT SEEN: 083 (05 added in cfc0634 without TESTS_FORMAT_FROM (076): judged by I2_BEFORE; 06 added in cfc0634 without VERDICT_FROM (071): judged by no Sent-back check; item 084)
SKIPPED: none
```
083 is complete and its pair is listed by ID, so the request's original 083 false INCOMPLETE stays fixed.

RI-001: round 2 computes no new set. The gate sets from round 1 ({083} = the intersection) are unchanged: the RULE NOT SEEN line above is exactly 083's pair. RI-002: no default is removed in round 2, so there is no `else 0` to put back. The equivalent mutation (M3: a failed read read as "not seen") still fails (d1). The 38 hits from 05's grep are all pre-existing hits in ccbot/, which this item does not touch. RI-012 (i3 step 3, item 059): the constant match now has a negative test with the pattern inside other text, in a comment, a longer name and a string. M6, M7 and M8 each fail it.

check_handoff (/home/claude/cover-calls, exit 0):
```
sources count (unique URLs in 01-research.md): 4
fact-check rows: 30
totals line: 30 rows -> 25 as-is, 4 fixed, 1 removed
PASS
```

## Real-data effect (diff_reports output, pasted)
not required (git diff --stat 6312f99 0583289: logs/implementation/2026-11-21.md, scripts/check_pipeline.py, tests/test_pipeline_check.py, work/084/05-build-report.md; no TRIGGER path or TRIGGER_DIRS file)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-002, RI-010, RI-012, RI-014, RI-007, RI-008, RI-011 (RI-001 ESCALATED: no new set computed; the RULE NOT SEEN line is still exactly {083}; RI-002 GUARDED: no default removed, M3 still fails (d1), and the docstring gap is strict, reading as seen; RI-010 ESCALATED: 084's guardrail still lists 083 by ID, M1/M2/M4 fail; RI-012 GUARDED: the embedded-constant negative test now exists in 4 forms, and M6/M7/M8 fail it, so F1 is closed; RI-014 OPEN: shallow behaviour unchanged, M5 fails (e1), and the new test runs in a full tmp repo; RI-007: Scope FULL, 01-05 present, I2 round-2 log line present; RI-008: oldest-python compile test ran (3.11), and py_compile OK; RI-011: no --first-parent, M4 fails)

## Pipeline line (step 2)
check_pipeline line: `084: awaiting A1 (FULL)`
(I ran it after this file, 07 and the I3 log line were written, and got the same line twice. One run was in /home/claude/cover-calls, exit 1, which holds 081's uncommitted round-2 edits to scripts/ and tests/. The other was in the clean scratch copy of 0583289 with these three files copied in, also exit 1. Both runs show `I3 FAIL: 081, 086`, `INCOMPLETE: none`, `SKIPPED: none`, and the same `RULE NOT SEEN: 083 (...)` line. The exit 1 comes only from the open send-backs of 081 and 086. Before this round the line was `084: I3 FAIL (FULL; sent back to I2, ...)`.)

## Sent back / sent to Audit
PASS (round 2). Sent to Audit: work/084/07-audit-task.md. Nothing is sent back to I1 or I2.

## Round 1 (FAIL, kept for the record)
Round 1 verdict: FAIL, sent back to I2 (F1).


Verified at commit 99a97f2 (084's I2 build, on 081's d44b687) in the clean scratch worktree /tmp/claude-0/wt084. `git rev-parse --is-shallow-repository`: false. Mutations ran in a `cp -a` copy of that worktree under the I3 scratchpad, never in /home/claude/cover-calls. Nothing was committed or pushed, and nothing was connected to a brokerage.

### I1 audit (plan vs research)
- The plan follows 03's map steps 0-7. The Rule trace has a row for every 03 step, every correction row (R1 F13, R2 FOR 2, R2 FOR 3d, R2 AGAINST 3), the removed row R1 F15, and each request.md line. The three request lines the plan drops (the request.md anchor, the `not checked (<rule> reached main after <ID>)` text, and "same item after the rule merges -> flagged") are dropped with reasons taken from 03 (R1 F12, and 02 FOR 2). The fixture flags 151 instead, which keeps the request's intent.
- The six "Changes to 03" are each sourced: (1) `_shallow_boundaries()` from 079's tests; (2) no `--first-parent`, with a git-log doc quote, pinned by M4; (3) the separate no-file text, using ls-tree behaviour that was UNVERIFIED and is pinned by fixture (d2); (4) the `not checked (<env>)` form, which follows the LOG TIME/INBOX lines; (5) list a pair only when the gate removed a reason, from 03's Decision §3; (6) a loud skip of the self-test in a shallow clone (RI-014). I found no unsourced addition.
- Gap (not I1's duty under its agent file, but it is why this is a FAIL): the plan's test list has no negative test for the constant match `^<CONST> = ` with the constant name inside other text. See I2 audit, finding F1.

### I2 audit (build vs plan)
I checked the build against the plan line by line (`git diff d44b687 99a97f2`):
- `RULE_FILE`, `_anchor_env`, `_rule_seen`, `log_fields_ok(..., new_rule)`, `log_hint(..., new_rule)`, the `incomplete(..., env, not_seen)` TESTS and VERDICT gates, the `main()` print and the docstring paragraph all match the plan. The `git log` call has no `--first-parent`. Each constant is matched on its own. The git calls go through `_git_ok`, except the recorded `rev-parse --verify` (Deviation 4, in GIT_CENSUS). Items below the cutoffs make no git call, because the gates sit behind `int(ID) >= cutoff` and "would fire".
- Scope lock: in the diff, no `+`/`-` line touches CHECKLIST_FROM, LOG_CHECK_FROM, TESTS_FORMAT_FROM, VERDICT_FROM, LOG_TIME_EXCEPT, WHOLE_DIFF_FROM, LEGACY, PRE_A1_LINE, `write_log` or `late_log_lines` (grep over the diff for those names: 0 hits). The cross-check block is unchanged.
- run-item.md: one line was added, directly after the RULES BRANCH line, as planned.
- I accept Deviations 1-5. Deviation 1 is needed for M4 to be able to fail. Deviation 3 changes the census total 41 -> 46, as 081's census comment asks.
- Connectivity check (re-done): `_anchor_env` is called once in `main()`. `_rule_seen` is called by `incomplete()` (twice) and by tests (d1) and (f1). `not_seen` is filled by `incomplete()` and printed by `main()`. Every branch of `_rule_seen` ends in True/False/None plus a note. The `git diff | grep TODO` hit is only 05's own checklist line.
- Edge probes (a fresh tmp git repo, the built `_rule_seen`): unborn HEAD gives `(None, '')` with env None; a 05 that is not committed gives `(None, '')`. Both are strict, as planned. No test covers either one directly. They are information only and are not sent back.

**F1 (sent back to I2): no RI-012 negative test for the constant match.** `_rule_seen` decides seen or not seen by matching a code word (`^VERDICT_FROM = `, `^TESTS_FORMAT_FROM = `) in the text of RULE_FILE. i3 step 3 (item 059, RI-012) requires a negative test with the pattern inside other text, and says the item FAILs without one. No test has the constant name in a comment, in a longer name or in a string. The built code is correct, but nothing pins it. My probe and mutations:
```
# tmp repo; work/150/06 added in 5d64a17, whose scripts/check_pipeline.py is:
CHECKLIST_FROM = 41
# VERDICT_FROM = 71 is item 071
OLD_VERDICT_FROM = 71
x = "VERDICT_FROM = 71"
# _rule_seen(work/150, "06", "VERDICT_FROM", None):
cp_orig (False, '5d64a17')      # as built: correct
cp_m6   (True, '5d64a17')       # M6: re.search(rf"{const} = ", text)  (no ^ / re.M)
cp_m7   (True, '5d64a17')       # M7: (const in text)
== M6  (whole tests/test_pipeline_check.py)
247 passed in 32.20s
== M7
247 passed in 33.08s
```
Both mutations survive the whole file. Under either one, an item whose 05/06 was added under a rule file that only mentions the constant would be judged "seen", which is the 083 false INCOMPLETE again. What must change (I2, recorded as a Deviation in 05 because the plan does not list it): add a test that builds a tmp repo whose anchor-commit RULE_FILE has the constant only inside other text (at least a comment `# VERDICT_FROM = 71`, a longer name `OLD_TESTS_FORMAT_FROM = 76`, and a string `x = "VERDICT_FROM = 71"`). Assert that `_rule_seen` gives `(False, sha7)` for both constants and that the item is listed in `RULE NOT SEEN:`, not INCOMPLETE. Then show in 05 that M6 and M7 each fail it. Also name the remaining gap in the docstring: a column-0 line `<CONST> = ` inside a triple-quoted docstring would still read as seen (strict, fail-closed).

### Tests re-run (output)
Full suite at 99a97f2 in /tmp/claude-0/wt084:
```
$ python3 -m pytest -q -p no:cacheprovider
611 passed, 1 skipped in 86.05s (0:01:26)
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'
```
This matches 05 (611 passed, 1 skipped). `tests/test_safety.py::test_every_py_compiles_on_oldest_python` ran (python3.11 is on PATH): 1 passed. `python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py`: OK.

Mutations M1-M5, re-run (`-k "rule_not_seen or unseen or rule_anchor or rule_seen or write_log_stays or repo_pipeline"`, scratch copy, restored, `cmp` with the worktree file: identical):
```
== M1  (gate off: _rule_seen returns (None, "") at once)
FAILED test_repo_pipeline_has_no_skipped_items, test_rule_not_seen_item_merged_beside_rules_branch,
       test_rule_not_seen_still_checks_old_rule, test_rule_anchor_git_failure_is_incomplete,
       test_rule_anchor_without_rule_file, test_rule_not_seen_shallow_and_no_git,
       test_rule_seen_positive_control_on_head
7 failed, 2 passed, 238 deselected in 4.92s
== M2  (rf"^{const}_X = ")
FAILED test_rule_not_seen_item_merged_beside_rules_branch, test_rule_not_seen_still_checks_old_rule,
       test_rule_seen_positive_control_on_head
3 failed, 6 passed, 238 deselected in 4.16s
== M3  (failed add-commit log -> (False, "x"))
FAILED test_rule_anchor_git_failure_is_incomplete
1 failed, 8 passed, 238 deselected in 3.93s
== M4  (--first-parent on the add-commit log)
FAILED test_repo_pipeline_has_no_skipped_items, test_rule_not_seen_item_merged_beside_rules_branch,
       test_rule_not_seen_still_checks_old_rule, test_rule_anchor_git_failure_is_incomplete,
       test_rule_not_seen_shallow_and_no_git, test_rule_seen_positive_control_on_head
6 failed, 3 passed, 238 deselected in 5.10s
== M5  (_anchor_env never reports shallow)
FAILED test_rule_not_seen_shallow_and_no_git
1 failed, 8 passed, 238 deselected in 5.57s
```
These are the same counts as 05. Each mutation fails the test the plan names.

The guardrail would have caught the original error. M1 (cutoff back to the item number, the request's mutation) brings back the original behaviour: `test_repo_pipeline_has_no_skipped_items` fails because 083 is INCOMPLETE again.

Done check (request "Done looks like"). PR #33's head is `daily-fixes/2026-11-19` b2f11b9 (REST: open, base main), and main is 8f1e9f7. Both are ancestors of 99a97f2 (`merge-base --is-ancestor`: yes, yes), so HEAD is PR #33 + main + 081 + 084:
```
$ python3 scripts/check_pipeline.py      # /tmp/claude-0/wt084, exit=0
I3 FAIL: none
INCOMPLETE: none
RULE NOT SEEN: 083 (05 added in cfc0634 without TESTS_FORMAT_FROM (076): judged by I2_BEFORE; 06 added in cfc0634 without VERDICT_FROM (071): judged by no Sent-back check; item 084)
UNCOMMITTED STEP: none
SKIPPED: none
083: complete (FULL)
```
`test_repo_pipeline_has_no_skipped_items` passes in the full run above.

RI-001: I re-ran the feasibility numbers. 05's step-0 table gives TESTS gate (ID >= 76, 05 constant 0) = {083}, VERDICT gate (ID >= 71, 06 constant 0) = {072, 073, 083}, and today's failures = {083}. The intersection, {083}, is the set pinned by (f2) and printed above. I checked the 083 and 076 anchors directly: (f1) passes, `_rule_seen(083) == (False, "cfc0634")`, and 076 is True for both constants.

RI-002: this item removes no default, so there is no `else 0` to put back. The equivalent mutation is "a failed read is treated as not seen" (M3), and it fails (d1). 05's grep reasons: the 38 hits are all in ccbot/, which this item does not touch. Data-window edges (unborn HEAD before the first commit, an uncommitted 05 after the last): both strict, from the probes above.

check_handoff (/home/claude/cover-calls, exit 0):
```
sources count (unique URLs in 01-research.md): 4
fact-check rows: 30
totals line: 30 rows -> 25 as-is, 4 fixed, 1 removed
PASS
```

### Real-data effect (diff_reports output, pasted)
not required (git diff --stat d44b687 99a97f2: .claude/commands/run-item.md, logs/implementation/2026-11-21.md, scripts/check_pipeline.py, tests/test_pipeline_check.py, work/084/05-build-report.md; no TRIGGER path or TRIGGER_DIRS file)

### Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-002, RI-010, RI-012, RI-014, RI-007, RI-008, RI-011 (RI-001 ESCALATED: re-measured the gate sets, {083} = intersection, matches (f2); RI-002 GUARDED: unknown anchor or failed read is never "not seen" (M3 fails d1), unborn/uncommitted edges strict; RI-010 ESCALATED: every exemption printed by ID, exact set {083} pinned, positive control on 076 catches M2; RI-012 GUARDED: constant match has no embedded-pattern negative test, M6/M7 survive -> F1, FAIL; RI-014 OPEN: shallow -> not checked, strict (M5 fails e1), self-test and (f1) skip loudly in a shallow clone; RI-007: Scope FULL, 01-05 present, no step skipped; RI-008: python3.11 compile OK, oldest-python test ran; RI-011: no --first-parent on the add-commit lookup, M4 fails (a))

### Pipeline line (step 2)
check_pipeline line: `084: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))`
(run in /home/claude/cover-calls after the I3 log line, `INCOMPLETE: none`. That tree's scripts/check_pipeline.py has 086's uncommitted I2 edits; the worktree run at 99a97f2 above is the clean one. Before the log line it was `INCOMPLETE: 084 (no log line for I3)`.)

### Sent back / sent to Audit
Sent back to I2 (round 1). Not sent to Audit, and no 07 is written.
What must change (F1): add an RI-012 negative test for `_rule_seen`'s constant match. Use a tmp repo whose anchor-commit RULE_FILE has `VERDICT_FROM` / `TESTS_FORMAT_FROM` only inside other text (a comment, a longer name, a string). Assert `(False, sha7)` and the `RULE NOT SEEN:` listing, and show in 05 that M6 (no `^`/re.M) and M7 (plain `in`) each fail it. Record it as a Deviation in 05, and name the remaining docstring-at-column-0 gap in the module docstring. Then re-run the full suite and write the I2 log line. Nothing else needs to change; M1-M5, the done check and the suite already pass.
