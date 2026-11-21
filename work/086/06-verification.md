# 06 Verification - 086
Verdict: PASS (round 2; earlier rounds: FAIL round 1)
Sent back to: none

Round 2 was checked at build commit 91ade51 (clean worktree /tmp/claude-0/wt086b; `git status` clean), against round-1 build 416835f / fd2b139 and pre-086 base 129120b, on 2026-11-21 UTC. No brokerage connection. Nothing committed. All mutations and probes ran in scratch dirs in the session scratchpad (`i3-086-r2-mut-<HHMMSS>`, `i3-086-r2-utf8probe-<HHMMSS>`), never in /home/claude/cover-calls.

## I1 audit (plan vs research)
04 "## Round 2" answers every round-1 send-back point:
- P1/point 1 -> R2-1: option (a) `<ID>: <reason>` joined by `; `. No existing assertion is edited, and M12 pins the format with the 3 existing tests.
- P2/point 2 -> R2-2: N2 is 30.00+30.01 (flagged) and 29.99+30.01 (not flagged); N3 is 45.00+45.01. I re-derived these in round 1, and they are what was built.
- P3/point 3 -> R2-3 (i)-(v): all accepted with reasons. N12b/M13, N13/M14 and N14 are added, and (iv) has a conditional pair search with M15.
- Point 4 -> R2-4: the "no failure caused by 086" bar has 3 conditions.
- The round-2 Rule trace maps every 06 point and every 05 deviation (Dev 4 and 5 accepted as built).
- Unsourced additions: none. The only new external claim (float noise, R2-3 (iv)) cites the Python tutorial URL. Everything else is a reading of the repo's own files.
- One plan fact went stale and is handled correctly. R2-4 names the allowed reason as `I3 FAIL: 081, 084`. 084 PASSed in fd2b139, so it is now `081, 086` (05 Dev 3). The bar is defined as "same reason at base", and base gives the same reason (below), so the bar holds.

## I2 audit (build vs plan)
I compared the round-2 diff with 04 R2-1 to R2-3 and the build steps, line by line (`git diff fd2b139 91ade51`). Code files changed: 2 (`scripts/check_pipeline.py` 16 +/- lines, `tests/test_pipeline_check.py` +54/-5). This matches "2 files planned".
- R2-1:
  - The `main()` print is now exactly `"; not computable: " + "; ".join(f"{i}: {why}" for i, why in batch["not_computable"])`.
  - The docstring says ``as `not computable: <ID>: <reason>` (entries joined by "; ")``. The rest is rewrapped only, with the text unchanged.
  - No other code line changed.
- R2-1, N5: the N5 assert is changed to the (a) text. It is 086's own test from round 1, not a pre-086 test.
- R2-2: N2/N3 values are unchanged from round 1, as planned.
- R2-3 (i)-(iii): N12b, N13 and N14 match the plan's fixtures and expectations. The code for (i)-(iii) was built in round 1 (Deviation 3), and I read it at 91ade51:
  - `order(end) < order(last_i2)` -> in_progress;
  - `bad_logs` -> every item not computable;
  - `stamp is None` -> `log line with no valid time`.
- R2-3 (iv): I2's search gave 0 at 60 and 6302 at 120. As planned, the first limit-120 pair (0.02, 119.99) became N2's third case at Δ1, with M15 added. I re-ran the search independently in decimal (scratch, no repo file): `60: 0 below-limit pairs`, `120: 6302, first ('0.02', '119.99', '119.99999999999999')`. For every pair, `round(..., 3) >= limit` holds. My `tried` totals (5998/11998) differ from 05's (6000/12000) only because the pairs are enumerated differently; the below-limit counts are the same.
  - Cosmetic: N2's test name `test_batch_boundary_delta0` now holds one Δ1 case. Its docstring says so. Not a defect (05 Dev 2).
- R2-3 (v): the 6-tuple is as stated.
- Scope lock unchanged: the round-2 diff touches no function other than the `main()` print. `late_log_lines`, `LOG_TIME_EXCEPT`, `LOG_FORMAT`, `incomplete` and `classify` are untouched, and no `_git(` call is added.
- Connectivity, re-done: there is no new function or constant. The changed print is the `LOG BATCH:` line, which run-item L14, I3, A1 and (c) read. N12b/N13/N14 call `batch_log_items` via `_bl`. Nothing is orphaned.
- 05's deviations, judged:
  - **Dev 1 (non-UTF-8 log file crashes `main()`): belongs in a new item, not 086.** My probe (scratch tree: one item and a log file of bytes `\xff\xfe`) gives a `UnicodeDecodeError` traceback, exit 1, with **both** the head script (91ade51) **and** the pre-086 base script (129120b). The crash is pre-existing and not caused by 086. 086's own reader handles the file correctly: `batch_log_items` -> `not_computable [('090', 'logs/implementation/2026-11-19.md unreadable')]`, nothing flagged. The crashing readers are `_log_text` (043/077), `orphan_log_lines` (047) and the I3 loop in `incomplete()` (071). `incomplete` is inside 086's scope lock, and none of them is in 086's request ("lines written in one batch are caught"). 081 does not cover it either: 081's scope is git output decoding (`_git`, `.git/shallow`), not log files. The failure is loud (traceback, exit != 0), not a silent value, so it is not an RI-002 pass today. The plan's N13 condition "`_run` exit 0 when nothing else is wrong" cannot be met while that crash exists. Asserting C in-process is therefore the right partial. **Recommendation: A1 opens a new BUG item (ID via `--next-id`)**: every log/step reader in `main()` gives the `<file> unreadable` handling `_item_lines` already has, plus an end-to-end non-UTF-8 fixture that asserts no traceback. Once that item lands, N13 can add the `_run` assert. Listed in 07.
  - Dev 2 (N2's third case at Δ1): follows 04 R2-3 (iv) literally. Accepted.
  - Dev 3 (allowed reason now `081, 086`): accepted, see the I1 audit.
- Missing data (RI-002): no new default. The round-2 code change is a print only. Every not-computable branch has an absent-case test (N5, N11, N12, N12b, N13, N14). M4 and M14 re-run below.
- Data-window edges (C's window): before the first value is N12 (`no line before I2`); after the last value is N12b (an open round after the last I3 -> in_progress, now keyed on the last I2) and N10 (a malformed last line still ends the window); interior is N14 (an invalid time anywhere -> not computable, never dropped).
- RI-012 (text matching): the negative tests D7 and N8 are unchanged, and M7 and M9 re-run below. Round 2 adds no text matching.
- Item 062 (pickers): does not apply.
- Rule the person follows (001): unchanged. The run-item.md change is from round 1 (RULE_PATHS) and still needs the person's OK at PR review.

**BUG: fix and guardrail both in place, and the guardrail catches 083.** At 91ade51 on the real tree, `batch_log_items(excepted={})` gives `flagged ['083 (96.08 s of pytest runs between 2026-11-20 10:15 and 10:15 UTC, limit 60 s; impossible under the run-item order, item 086)']`, and with the exception in place `excepted ['083']` and `flagged []`. Both runs: checked 39, not computable 048/054/055/056/058/059/060, in_progress ['086']. D1 refuses 083's batch shape (M5 kills it).

## Tests re-run (output)
Full suite at 91ade51, `python3 -m pytest -q` in /tmp/claude-0/wt086b:
```
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 649 passed, 1 skipped in 84.80s (0:01:24)
```
R2-4 bar:
1. Only `test_repo_pipeline_has_no_skipped_items` fails, and the 3 P1 tests pass (`test_old_06_without_round_headers_unchanged`, `test_i3_fail_target_not_stated`, `test_pass_without_sent_back_none_is_incomplete`; also in the 54-pass subset below).
2. Same reason at base. The test asserts exit 0 from `check_pipeline.py` on HEAD. I ran the pre-086 script (`git show 129120b:scripts/check_pipeline.py`) and round-1's script (fd2b139) read-only on the same tree. All three exit 1. Their whole outputs differ from 91ade51's only on the LOG BATCH line (pre-086: the line is added; round 1: `048 (...)` -> `048: ...`). The error lines at HEAD are `I3 FAIL: 081, 086` and `INCOMPLETE: 081 (06 Verdict says FAIL, last I3 log line says PASS (item 071))`:
   - The `INCOMPLETE: 081` entry is newer than 05's paste. The 081 I3 round-2 PASS log line (logs/implementation/2026-11-21.md L15, 01:00) was committed in 91ade51 before 081's round-2 06 was. This is the other thread's in-flight state, and the base script reports it identically, so it is not 086's.
3. No other test fails.

Subset (scratch copy, `-k "batch or log_ or old_06_without_round_headers_unchanged or i3_fail_target_not_stated or pass_without_sent_back_none_is_incomplete"`), mutations by `i3r2_mutate.py` in the scratchpad, with the script restored after each:
```
unmutated: 54 passed, 232 deselected in 4.14s
M1: 2 failed, 52 passed, 232 deselected in 5.38s -> test_batch_boundary_delta0[30.00-30.01-10:00-True], test_batch_boundary_delta0[0.02-119.99-10:01-True]
M1b: 5 failed, 49 passed, 232 deselected in 3.50s -> test_batch_083_shape_is_flagged, test_batch_boundary_delta0[29.99-30.01-10:00-False], test_batch_delta1_limit_is_120, test_batch_copy_of_05_in_06_is_dropped, test_batch_summary_in_test_id_is_not_a_run
M2: 6 failed, 48 passed, 232 deselected in 3.51s -> test_batch_083_shape_is_flagged, test_batch_083_flagged_on_repo_data, test_batch_boundary_delta0[30.00-30.01-10:00-True], test_batch_boundary_delta0[0.02-119.99-10:01-True], test_batch_sections_and_largest_value, test_batch_research_line_at_i2_minute_is_before
M3: 1 failed, 53 passed, 232 deselected in 3.30s -> test_batch_copy_of_05_in_06_is_dropped
M4: 1 failed, 53 passed, 232 deselected in 3.33s -> test_batch_untimed_item_is_not_computable
M5: 2 failed, 52 passed, 232 deselected in 3.55s -> test_log_refused_after_later_steps, test_log_verdict_words_in_free_text_are_not_send_backs
M6: 4 failed, 50 passed, 232 deselected in 3.64s -> test_log_after_i3_fail_is_written, test_log_after_blocked_or_not_a_fit_is_written[research-R3-5 verified, 0 fixed, 0 removed | BLOCKED-steps0], test_log_after_blocked_or_not_a_fit_is_written[implementation-I1-NOT A FIT | 0 files planned-steps1], test_log_after_a1_fail_is_written
M6b: 1 failed, 53 passed, 232 deselected in 3.48s -> test_log_after_blocked_or_not_a_fit_is_written[research-R3-5 verified, 0 fixed, 0 removed | BLOCKED-steps0]
M7: 1 failed, 53 passed, 232 deselected in 3.36s -> test_log_verdict_words_in_free_text_are_not_send_backs
M8: 1 failed, 53 passed, 232 deselected in 4.22s -> test_log_batch_except_is_pinned
M9: 1 failed, 53 passed, 232 deselected in 3.83s -> test_batch_summary_in_test_id_is_not_a_run
M10: 2 failed, 52 passed, 232 deselected in 3.64s -> test_batch_083_flagged_on_repo_data, test_batch_malformed_last_line_still_ends_the_window
M11: 1 failed, 53 passed, 232 deselected in 3.45s -> test_batch_sections_and_largest_value
M12: 4 failed, 50 passed, 232 deselected in 3.62s -> test_old_06_without_round_headers_unchanged, test_i3_fail_target_not_stated, test_pass_without_sent_back_none_is_incomplete, test_batch_untimed_item_is_not_computable
M13: 1 failed, 53 passed, 232 deselected in 3.52s -> test_batch_open_round_keyed_on_last_i2
M14: 1 failed, 53 passed, 232 deselected in 3.30s -> test_batch_unreadable_log_file_makes_every_item_not_computable
M15: 1 failed, 53 passed, 232 deselected in 3.67s -> test_batch_boundary_delta0[0.02-119.99-10:01-True]
restored: 54 passed, 232 deselected in 3.45s
```
Every mutation fails at least one named test, and the failing sets are identical to 05's. After the run, the scratch script is identical to 91ade51's (`diff -q`). M12 fails exactly the 3 pre-086 tests plus N5, as R2-1 expects.

RI-008: python3.10 is not on PATH, so `test_every_py_compiles_on_oldest_python` ran with python3.11 only. tests/test_safety.py: `9 passed in 1.00s`. Also `python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py` -> ok.

`python3 scripts/check_handoff.py 086` (91ade51):
```
sources count (unique URLs in 01-research.md): 2
fact-check rows: 44
totals line: 44 rows -> 34 as-is, 9 fixed, 1 removed
PASS
```
`python3 scripts/check_pipeline.py` at 91ade51 (wt086b): exit 1 (see R2-4 above), `SKIPPED: none`, and this LOG BATCH line (format (a); it contains (c)'s text):
```
LOG BATCH: none (not checked: 083: six lines written in one batch at 10:15 after the build (commit cfc0634 10:15:48); real times not recoverable (item 086)); not computable: 048: no pytest time in 05/06/I2 line; 054: no pytest time in 05/06/I2 line; 055: no pytest time in 05/06/I2 line; 056: no pytest time in 05/06/I2 line; 058: no pytest time in 05/06/I2 line; 059: no pytest time in 05/06/I2 line; 060: no pytest time in 05/06/I2 line
```

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat 129120b 91ade51 -- . ':!work' ':!logs'`: .claude/commands/run-item.md, scripts/check_pipeline.py, tests/test_pipeline_check.py; no TRIGGER path or data/real/)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-002, RI-010, RI-012, RI-014
- RI-001 (ESCALATED): the R2-3 (iv) pair count was re-measured independently (0 at 60, 6302 at 120, 2026-11-21). The N2/N3 numbers were re-derived in round 1. No filter is assumed to have candidates.
- RI-002 (GUARDED): the round-2 code is print-only, and no default was added. M4 and M14 fail their tests. The non-UTF-8 `main()` crash is loud and pre-existing -> a new item (Dev 1).
- RI-010 (ESCALATED, this item): (b) flags 083 on real data with the exception emptied, `LOG_BATCH_EXCEPT` = {083} is pinned (M8), and D1 refuses the batch shape (M5).
- RI-012 (GUARDED): D7 and N8 are present, and M7 and M9 fail them.
- RI-014 (OPEN): no `_git(` call was added in round 2. C/D results do not depend on clone depth.

## Pipeline line (step 2)
check_pipeline line: `086: awaiting A1 (FULL)` (run in /home/claude/cover-calls after this file, the I3 log line 01:07 and 07; exit 0, `I3 FAIL: none`, `INCOMPLETE: none`, `SKIPPED: none`, `LOG BATCH: none (not checked: 083: ...)`, so 086's own window, from I1 2026-11-20 23:46 to I3 01:07, is checked and not flagged). Before this file, at 91ade51, the line was `086: I3 FAIL (FULL; sent back to I1, needs a later PASS round in 06 (item 071))`.

## Sent back / sent to Audit
PASS (round 2). Sent to Audit: work/086/07-audit-task.md.

# Round 1 (FAIL, kept as written)

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
