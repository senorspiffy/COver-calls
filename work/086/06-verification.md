# 06 Verification - 086
Verdict: FAIL (round 1)
Sent back to: I1

Checked at build commit 416835f (clean worktree /tmp/claude-0/wt086), base 129120b (scratch worktree), 2026-11-21 UTC. No brokerage connection. Nothing committed.

## I1 audit (plan vs research)
- Every 03 map step and fact-check row is in the Rule trace, and the two dropped request rules give their reasons (03 #9, #18). Changes 1-7 have sources: change 1 comes from reading `LOG_FORMAT`, change 2 from 076's 05/06, and change 7 from the pytest and Python docs cited in Extra research 1-2. I found no unsourced addition.
- **Problem P1 (plan defect, blocking): the planned LOG BATCH text breaks 3 existing tests, and the plan forbids the edits that would fix them.** 04 Files 1 `main()` says to print `; not computable: <ID> (<reason>), ...` after the LOG TIME line, which comes after INCOMPLETE. 04 Files 2 also says "No existing assertion is edited". Three existing tests check that `"<ID> (" not in out.split("INCOMPLETE:")[1]` for fixture items 065, 066 and 067:
  - `test_old_06_without_round_headers_unchanged`
  - `test_i3_fail_target_not_stated`
  - `test_pass_without_sent_back_none_is_incomplete`

  Those `_item` fixtures have I2 and I3 lines but no pytest time, so rule C correctly makes them not computable. The planned format then puts `065 (`, `066 (` or `067 (` after `INCOMPLETE:`. The plan's Expected result ("the full suite passes") cannot be met as written. I reproduced it: at 416835f these 3 fail, and at base 129120b the same 3 pass (output below). I1 must choose one fix and write it into 04:
  - (a) print not-computable entries as `<ID>: <reason>` joined by `; `, like the `not checked:` part of the same line;
  - (b) move the LOG BATCH print before INCOMPLETE;
  - (c) allow those 3 assertions to change.

  I recommend (a). It keeps the placement and leaves existing assertions alone. It matches the format already used on the line. I2's scratch probe of (a) found that only I2's own N5 assert needs changing. 04's Expected result text (`not computable: 048 (...)`) must change with it.
- **Problem P2 (plan defect): 04's N2 non-flag case and N3 contradict 04's own copy guard.** N2 says "05 30.00, 06 30.00: not flagged" and N3 says "45.00 + 45.00". The copy guard drops a 06 value equal to a t05 candidate, so k = 1 in both. N2 then passes for the wrong reason, and N3 cannot kill M1b (45.00 - 0.005 < 60). 04's RI-004/RI-005 line claims "every fixture number re-derived", but these two were not. I2 used distinct values (Deviation 2: 30.00 + 30.01 flags, 29.99 + 30.01 does not, 45.00 + 45.01 < 120). I re-derived these values and they are correct: 60.01 - 0.01 = 60.00 >= 60, 59.99 < 60, and 90.00 < 120, while under M1b the limit is 60 and the case flags. I1 must put these numbers into 04's N2 and N3 so that the plan and the build agree.
- **P3 (confirm in 04, not a defect in the build): I2's Deviation 3 additions all sit on the not-flag side.** I1 must accept or reject each one in 04:
  - (i) in_progress is keyed on the last I2 line, not the first;
  - (ii) an unreadable log file makes every item not computable;
  - (iii) an invalid HH:MM is not computable;
  - (iv) the flag test is `round(..., 3) >= limit`, which removes float noise;
  - (v) the 6-tuple in `_item_lines`.

  I checked (i): with "first I2", a round-2 I2 run logged after the last I3 would fall outside the window. "Last I2" is the sound reading, and 04 L54 should say so. (iv) is needed: without it, 30.00 + 30.01 - 0.01 is 60.00000000000001.

## I2 audit (build vs plan)
I compared the diff (`git diff 129120b 416835f`, 5 files) with 04 item by item:
- `scripts/check_pipeline.py`:
  - The docstring LOG BATCH entry sits after LOG TIME and covers the formula, the window, the anchored summary rule, the copy guard, "one steady clock", `LOG_BATCH_EXCEPT`, not computable, exit 1, no git and gaps (w)-(z). The `--log` paragraph covers D.
  - `LOG_BATCH_EXCEPT`, `BATCH_ROUND`, `SEND_BACK` (R3 group 2) and `SUMMARY_LINE` are as planned.
  - `_item_lines`, `_run_seconds`, `batch_log_items`, `_sent_back`, the D block in `write_log` (placed after the format and request.md refusals), the `main()` print after LOG TIME, and `or batch["flagged"]` in the exit expression are all as planned.
  - Scope lock: `late_log_lines`, `LOG_TIME_EXCEPT`, `LOG_FORMAT`, `log_fields_ok`, `log_hint`, `incomplete` and `classify` are untouched, and the diff adds no `_git(` call.
- `tests/test_pipeline_check.py`: the 26 cases cover (a), (b), the pin test, N1-N12 and D1-D10. (c) is one added assert. No existing assertion is edited.
- `.claude/commands/run-item.md`: the L14 and L16 texts are as in 04. This is a RULE_PATHS change and needs the person's OK at PR review.
- The deviations are listed in 05 (1-5) and judged above (P1-P3). I found no unlisted deviation.
- Connectivity, re-done: `batch_log_items` is called by `main()` and by the tests. `_item_lines` and `_run_seconds` are called only by it. `_sent_back` is called by `write_log`. `SEND_BACK`, `SUMMARY_LINE` and `BATCH_ROUND` are each read. The `LOG BATCH:` output is read by run-item L14 and the exit expression. Nothing is orphaned.
- Missing data (RI-002): k = 0 goes to not computable, never 0 s or 60 s. An unreadable 05, 06 or log goes to not computable with the file named. The `else 0` hit in 05's grep is the exit-code expression, not a data default (checked).
- Data-window edges, for C's window:
  - before the first value: no line before I2 → `not computable (no line before I2)`, tested in `test_batch_open_round_and_no_line_before_i2`;
  - after the last value: no I3 after the last I2 → `in_progress`, same test;
  - interior: a malformed last line still ends the window (N10).
- RI-012 (text matching): there are negative tests with the pattern inside other text. D7 (`test_log_verdict_words_in_free_text_are_not_send_backs`: `READY (was BLOCKED)` and `PASS ... (FAIL fixed)`) and N8 (`test_batch_summary_in_test_id_is_not_a_run`: a summary inside a test ID).
- Item 062 (pickers) does not apply: no simulator or replay.
- Rule the person follows (001): unchanged.

**BUG: the fix and the guardrail are both present, and the guardrail catches 083.** With the exception emptied (scratch copy, `excepted = {}`), the real repo gives:
```
LOG BATCH: 083 (96.08 s of pytest runs between 2026-11-20 10:15 and 10:15 UTC, limit 60 s; impossible under the run-item order, item 086); not computable: 048 (...), 054 (...), 055 (...), 056 (...), 058 (...), 059 (...), 060 (...)
```
D1 (`test_log_refused_after_later_steps`) refuses 083's batch shape.

## Tests re-run (output)
Full suite at 416835f (worktree /tmp/claude-0/wt086, `python3 -m pytest -q`):
```
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_old_06_without_round_headers_unchanged
FAILED tests/test_pipeline_check.py::test_i3_fail_target_not_stated - Asserti...
FAILED tests/test_pipeline_check.py::test_pass_without_sent_back_none_is_incomplete
4 failed, 633 passed, 1 skipped in 81.18s (0:01:21)
```
The same 4 tests at base 129120b (scratch worktree):
```
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 3 passed, 243 deselected in 2.51s
```
- `test_repo_pipeline_has_no_skipped_items` is **not caused by 086**. It also fails at base. Its reason has changed since 05 was written: the 081/084 I3 log lines are now committed and INCOMPLETE is none. It now fails because HEAD has `I3 FAIL: 081, 084` (exit 1, and the assert `"I3 FAIL: none"`). That is the correct state of those items, not a defect, and it clears when 081 and 084 PASS. 086's new (c) assert is placed after `code == 0`, so it does not run while the test fails. In the tree, the LOG BATCH line holds the (c) text (see Pipeline line).
- The other 3 failures are caused by 086 (P1).

Mutations re-run by I3 in a scratch copy (`/tmp/claude-0/-home-claude/8f94cbd2-523d-52d1-8971-85df3e672dc0/scratchpad/i3_086_mut`, never the repo), with `-k "batch or log_"`:
```
M4  (RI-002: k=0 -> known = [60.0] put back)  1 failed, 45 passed, 227 deselected  -> test_batch_untimed_item_is_not_computable
M7  (verdict by substring `word in m[5]`)      1 failed, 45 passed, 227 deselected  -> test_log_verdict_words_in_free_text_are_not_send_backs
M9  (SUMMARY_LINE.search)                      1 failed, 45 passed, 227 deselected  -> test_batch_summary_in_test_id_is_not_a_run
restored: 46 passed, 227 deselected; script identical to 416835f (diff -q)
```
RI-008: `test_every_py_compiles_on_oldest_python` ran with python3.11 (python3.10 is not on PATH). tests/test_safety.py: `9 passed in 0.95s`.

`python3 scripts/check_handoff.py 086` (at 416835f):
```
sources count (unique URLs in 01-research.md): 2
fact-check rows: 44
totals line: 44 rows -> 34 as-is, 9 fixed, 1 removed
PASS
```
`python3 scripts/check_pipeline.py` at 416835f: exit 1, caused by `I3 FAIL: 081, 084`. The output also has `INCOMPLETE: none`, `SKIPPED: none` and `LOG TIME: none (not checked: 048: ...)`, and this LOG BATCH line:
```
LOG BATCH: none (not checked: 083: six lines written in one batch at 10:15 after the build (commit cfc0634 10:15:48); real times not recoverable (item 086)); not computable: 048 (no pytest time in 05/06/I2 line), 054 (no pytest time in 05/06/I2 line), 055 (no pytest time in 05/06/I2 line), 056 (no pytest time in 05/06/I2 line), 058 (no pytest time in 05/06/I2 line), 059 (no pytest time in 05/06/I2 line), 060 (no pytest time in 05/06/I2 line)
```
This matches 05's pasted line.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat 129120b 416835f`: .claude/commands/run-item.md, logs/implementation/2026-11-21.md, scripts/check_pipeline.py, tests/test_pipeline_check.py, work/086/05-build-report.md; no TRIGGER path or data/real/)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-010, RI-014, RI-002, RI-012
- RI-001 (ESCALATED): every new filter has a measured count (05 step 0 (i)-(iii): 213 / 3 / C table). I checked 083 = 96.08 s against a 60 s limit by running it. The plan's N2/N3 numbers were not re-derived against the copy guard (P2).
- RI-010 (ESCALATED, this item): fixture (b) holds on real data, D1 refuses the 083 shape, `LOG_BATCH_EXCEPT` = {083} is pinned, and 083 is not in `LOG_TIME_EXCEPT`.
- RI-014 (OPEN): C and D make no git call (the diff adds no `_git(`). Results do not depend on clone depth.
- RI-002 (GUARDED): M4 re-run, see above.
- RI-012 (GUARDED): M7 and M9 re-run, and the negative tests D7 and N8 exist.

## Pipeline line (step 2)
check_pipeline line: `086: I3 FAIL (FULL; sent back to I1, needs a later PASS round in 06 (item 071))` (run in /home/claude/cover-calls after this file and the I3 log line 00:39; `INCOMPLETE: none`, `SKIPPED: none`). Before this file, at 416835f, the line was `086: in progress (FULL: next 06)`.

## Sent back / sent to Audit
Sent back to I1 (round 1). Not sent to Audit; there is no 07. I1 must:
1. Choose the LOG BATCH not-computable format or placement (P1: (a), (b) or (c); I3 recommends (a)) and update 04's `main()` text and Expected result to match, so the full suite can pass with no existing assertion edited (or state explicitly which assertion may change).
2. Replace 04's N2 non-flag case and N3 values with values that survive the copy guard (P2; I2's 30.00 + 30.01, 29.99 + 30.01 and 45.00 + 45.01 are correct).
3. Accept or reject I2's Deviation 3 (i)-(v) in 04 (P3). 04 L54 should say "no I3 line after the last I2 line".
4. Note in 04's Expected result that `test_repo_pipeline_has_no_skipped_items` fails on this branch while 081/084 have open I3 FAIL rounds, so "full suite passes" is judged as "no failure caused by 086".

After that, I2 rebuilds the `main()` print (and N5's assert, if (a) is chosen) and re-runs the suite and M1-M11.
