# 05 Build report - 086
Built on daily-fixes/2026-11-20 at HEAD b745738 (99a97f2 + I3's round-1 FAIL commits for 081 and 084), 2026-11-21 UTC. Nothing committed (the orchestrator commits). No brokerage connection; no ccbot/, config/ or data/ change.

**Sent back to I1 (Deviation 1): three existing tests conflict with the plan's LOG BATCH text.** The code is built as planned. The suite has 3 failures caused by 086, plus 1 that is not caused by 086 (see Test output).

## Changes made (file: what changed)
File counts (by command, 012):
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
0
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
3
```
- `scripts/check_pipeline.py`:
  - Docstring: a `--log` paragraph for rule D. A `LOG BATCH` entry directly after the LOG TIME entry, covering the formula, the whole-item window, the anchored summary rule, the two sections, the copy guard, "impossible under the run-item order on one steady clock (run-item L14, L16)", `LOG_BATCH_EXCEPT`, not computable / in progress, exit 1, "no git", and known gaps (w)-(z).
  - New constants after `LOG_TIME_EXCEPT`: `LOG_BATCH_EXCEPT = {"083": ...}` ("Never add a new item here"), `BATCH_ROUND = 0.005`, `SEND_BACK = {"R3": (2, "BLOCKED"), "I1": (1, "NOT A FIT"), "I3": (1, "FAIL")}`, and `SUMMARY_LINE` (the plan's regex, used with `.match` on the stripped line).
  - New `_item_lines(logs)`, `_run_seconds(path, heading)` and `batch_log_items(work, logs, excepted)` (rule C).
  - New `_sent_back(item, logs)`. `write_log` gets rule D, placed after the format and request.md refusals.
  - `main()` prints `LOG BATCH:` after the LOG TIME line and adds `or batch["flagged"]` to the exit expression.
  - Scope lock kept: `late_log_lines`, `LOG_TIME_EXCEPT`, `LOG_FORMAT`, `log_fields_ok`, `log_hint`, `incomplete` and `classify` are unchanged, and there is no new git call (`test_git_call_census` passes unchanged at 46).
- `tests/test_pipeline_check.py`:
  - 26 new test cases (611 + 1 skipped before, 637 + 1 skipped after): (a), (b), the pin test, N1-N12 (N2 has 2 cases), D1-D10 (D4/D5 are one parametrized test).
  - Helpers `_batch_item`, `_six`, `_impl`, `_bl`, `_steps`, `_log_line`, `_written`.
  - One added assert (c) in `test_repo_pipeline_has_no_skipped_items`. No existing assertion edited.
- `.claude/commands/run-item.md`: the L14 text ", and `LOG BATCH:` must not name it (item 086)" and the L16 D sentence, both worded as in 04. This is a RULE_PATHS change and needs the person's OK at PR review.

## Step 0 (read-only recount, scratch script `step0.py` in the session scratchpad, before any repo edit)
- (i) Lines in work/0[4-8]?/0[56]-*.md where an unanchored `SUMMARY_LINE.search` finds a time but the anchored `.match` on the stripped line does not: **213** (≥ 3 expected). These include 076/05 L39 and 076/06 L57 and L138, the `FAILED ...[... in 58.86s]` test IDs that change 2 names. Most of the others are backticked or bulleted runs (e.g. 075/05 L61-82, 077/05 L174-204). Not reading them only lowers Σ, the safe side.
- (ii) Items where the copy guard drops a 06 value: **3**. 072 drops [0.01, 0.02], 075 drops [0.04], 078 drops [6.37]. All are short partial runs and none is near a limit.
- (iii) The C table, one row per item. Only **083** is flagged with the exception emptied. No other item is flagged, so step 0 did not send the item back:
```
ID | start | end | delta | t05 | t06 | k | sum-0.005k | limit | ratio
045 | 11-05 22:20 | 11-05 22:24 | 4 | 16.96 | None | 1 | 16.955 | 300 | 0.057
046 | 11-05 22:20 | 11-05 22:24 | 4 | 16.96 | None | 1 | 16.955 | 300 | 0.057
047 | 11-06 22:18 | 11-06 22:20 | 2 | 18.64 | None | 1 | 18.635 | 180 | 0.104
048 | 11-07 20:40 | 11-07 20:40 | 0 | n/a | n/a | 0 | not computable
049 | 11-07 22:19 | 11-07 22:21 | 2 | 22.63 | None | 1 | 22.625 | 180 | 0.126
050 | 11-07 22:21 | 11-07 22:22 | 1 | 22.92 | None | 1 | 22.915 | 120 | 0.191
051 | 11-09 22:17 | 11-09 22:19 | 2 | 16.57 | None | 1 | 16.565 | 180 | 0.092
052 | 11-10 22:23 | 11-10 22:26 | 3 | 21.45 | None | 1 | 21.445 | 240 | 0.089
053 | 11-11 22:44 | 11-11 22:56 | 12 | 23.54 | 25.35 | 2 | 48.880 | 780 | 0.063
054 | 11-12 13:54 | 11-12 13:55 | 1 | n/a | n/a | 0 | not computable
055 | 11-12 14:09 | 11-12 14:09 | 0 | n/a | n/a | 0 | not computable
056 | 11-12 14:18 | 11-12 14:19 | 1 | n/a | n/a | 0 | not computable
058 | 11-12 14:49 | 11-12 14:49 | 0 | n/a | n/a | 0 | not computable
059 | 11-12 23:22 | 11-12 23:23 | 1 | n/a | n/a | 0 | not computable
060 | 11-12 23:24 | 11-12 23:26 | 2 | n/a | n/a | 0 | not computable
061 | 11-14 04:36 | 11-14 05:32 | 56 | 61.68 | 58.14 | 2 | 119.810 | 3420 | 0.035
062 | 11-13 23:37 | 11-13 23:49 | 12 | 26.61 | 24.32 | 2 | 50.920 | 780 | 0.065
063 | 11-14 23:37 | 11-15 00:29 | 52 | 55.09 | 51.95 | 2 | 107.030 | 3180 | 0.034
064 | 11-15 00:11 | 11-15 00:21 | 10 | 51.67 | 52.58 | 2 | 104.240 | 660 | 0.158
065 | 11-15 23:37 | 11-16 00:13 | 36 | 42.67 | 44.88 | 2 | 87.540 | 2220 | 0.039
066 | 11-15 23:33 | 11-15 23:42 | 9 | 47.65 | 46.44 | 2 | 94.080 | 600 | 0.157
067 | 11-16 23:31 | 11-16 23:52 | 21 | 0.71 | 53.01 | 2 | 53.710 | 1320 | 0.041
068 | 11-16 23:31 | 11-17 00:20 | 49 | 55.51 | 52.67 | 2 | 108.170 | 3000 | 0.036
069 | 11-17 23:37 | 11-18 00:25 | 48 | 63.33 | 63.76 | 2 | 127.080 | 2940 | 0.043
070 | 11-17 23:40 | 11-18 00:28 | 48 | 57.39 | 59.38 | 2 | 116.760 | 2940 | 0.040
071 | 11-18 23:45 | 11-19 00:08 | 23 | 62.74 | 64.0 | 2 | 126.730 | 1440 | 0.088
072 | 11-18 23:34 | 11-18 23:48 | 14 | 59.45 | 62.97 | 2 | 122.410 | 900 | 0.136
073 | 11-18 23:37 | 11-18 23:51 | 14 | 60.4 | 62.24 | 2 | 122.630 | 900 | 0.136
074 | 11-18 23:43 | 11-19 00:28 | 45 | 68.26 | 61.83 | 2 | 130.080 | 2760 | 0.047
075 | 11-19 23:46 | 11-19 23:57 | 11 | 69.79 | 64.91 | 2 | 134.690 | 720 | 0.187
076 | 11-19 23:41 | 11-20 00:31 | 50 | 85.49 | 85.42 | 2 | 170.900 | 3060 | 0.056
077 | 11-19 23:51 | 11-20 01:12 | 81 | 91.97 | 102.61 | 2 | 194.570 | 4920 | 0.040
078 | 11-19 23:45 | 11-20 01:45 | 120 | 92.66 | 113.36 | 2 | 206.010 | 7260 | 0.028
079 | 11-19 23:39 | 11-20 02:22 | 163 | 90.93 | 90.21 | 2 | 181.130 | 9840 | 0.018
080 | 11-20 23:41 | 11-20 23:53 | 12 | 78.18 | 79.0 | 2 | 157.170 | 780 | 0.202
081 in progress
083 | 11-20 10:15 | 11-20 10:15 | 0 | 48.51 | 47.57 | 2 | 96.070 | 60 | 1.601  FLAG
084 in progress
085 | 11-20 23:34 | 11-20 23:48 | 14 | 79.79 | 79.07 | 2 | 158.850 | 900 | 0.177
```
  At step 0, 081 and 084 had I2 lines but no I3 line yet, so they were in progress. Their I3 round-1 FAIL lines were written while I built, and they are now checked and not flagged (counts below). The largest ratio after 083 is 080 (0.202), then 050 (0.191) and 075 (0.187). Not computable: 7 items (048, 054, 055, 056, 058, 059, 060). Their runs are not written as anchored summary lines in the two sections (054's 22.90 s and 059's 0.55 s included), so they only lower Σ.

**Counts from `batch_log_items()` at the end of the build (working tree, 2026-11-21 00:3x UTC):**
```
excepted= None checked 39 flagged [] excepted ['083'] not_computable ['048', '054', '055', '056', '058', '059', '060'] in_progress []
excepted= {} checked 39 flagged ['083'] excepted [] not_computable ['048', '054', '055', '056', '058', '059', '060'] in_progress []
```
That is checked 39 = 35 + 080, 081, 084, 085 (each has I2 and a later I3 line), excepted 1 (083), flagged 0, not computable 7, in progress 0. With `excepted={}`, flagged is exactly {083} (RI-010's fixture (b) condition, on real data).

## Connectivity check
- [x] Every new function and rule is used:
  - `_item_lines` and `_run_seconds` are called by `batch_log_items`, which is called by `main()` (the LOG BATCH line and exit) and by tests (a), (b) and N1-N12.
  - `_sent_back` is called by `write_log` (rule D).
  - `SEND_BACK` is read by `_sent_back`; `SUMMARY_LINE` by `_run_seconds` and `batch_log_items`; `BATCH_ROUND` by `batch_log_items`.
  - `LOG_BATCH_EXCEPT` is the default for `batch_log_items` and is pinned by its test.
  - The docstring and run-item.md name the line and the refusal.
- [x] Every input has a source and every output a consumer:
  - Inputs: logs/research and logs/implementation `????-??-??.md`, work/<ID>/05 and 06 (C); work/<ID>/01-06, the log lines and 07 (D).
  - Outputs: the `LOG BATCH:` line and exit 1 (read by run-item L14, A1 and I3), and the `--log refused: ...` stderr message with exit 2 (run-item L16: a refusal goes back to the step).
- [x] Every branch ends in a defined result. In C:
  - no I2 line: skipped;
  - no I3 line after the last I2 line: `in_progress`;
  - excepted: counted and listed with its reason;
  - no line before the first I2: `not computable (no line before I2)`;
  - unreadable 05/06: `not computable (<file> unreadable)`;
  - unreadable log file: every item is `not computable (<file> unreadable)` (Deviation 3);
  - a line with an invalid time (e.g. 25:00): `not computable (log line with no valid time)`;
  - k = 0: `not computable (no pytest time in 05/06/I2 line)`;
  - otherwise flagged or not.

  In D:
  - later files present and no send-back: exit 2, nothing written;
  - otherwise the line is written.

  An unreadable log file or 07 adds no send-back, which is the refusal side.
- [x] No leftover TODOs or unused files. The scratch scripts (step0.py, batch_code.py, mutate.py, mut/) live only in the session scratchpad, outside the repo.

Missing-data policy:
- `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/` gives 38 hits. All are pre-existing (`git diff --stat -- ccbot/` is empty), so there is no new or changed hit.
- The same pattern over the changed lines of scripts/check_pipeline.py gives 2 hits:
  - `log file or 07 adds no send-back (the refusal side)."""`: docstring text ("or 07"), not code.
  - `... or batch["flagged"] else 0`: this is the exit-code expression, not a data default. A missing time can never reach it (k = 0 is not computable).
- No dataclass is added and no numeric default is set. A missing time is never 0 s or 60 s (N5, M4).
- The one `>=` test, `round(total - BATCH_ROUND * len(known), 3) >= limit`, runs only when `known` is non-empty. Every value comes from `float(r"\d+\.\d+")`, so it cannot be NaN.

Feasibility numbers from the plan, as measured:
- C on 083: 96.08 s Σ, 96.07 after rounding, limit 60, flagged.
- C on all items: 1 of 39 flagged with the exception emptied.
- Boundary: 30.00 + 30.01 flags; 29.99 + 30.01 does not.
- Δ1: 45.00 + 45.01 = 90.00 < 120.
- D: 083's batch shape (5 later files) is refused (D1).
- Send-back shapes I3 FAIL, R3 BLOCKED, I1 NOT A FIT and A1 FAIL are written (D3-D6).

## Test output (pasted, not summarized)
Full suite before any edit (HEAD 99a97f2, 2026-11-21):
```
611 passed, 1 skipped in 80.10s (0:01:20)
```
Full suite after the build (`python3 -m pytest -q`, repo root):
```
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_old_06_without_round_headers_unchanged
FAILED tests/test_pipeline_check.py::test_i3_fail_target_not_stated - Asserti...
FAILED tests/test_pipeline_check.py::test_pass_without_sent_back_none_is_incomplete
4 failed, 633 passed, 1 skipped in 77.47s (0:01:17)
```
- `test_repo_pipeline_has_no_skipped_items` is **not caused by 086** (item 071 rule). HEAD moved to b745738 during the build: I3 committed the round-1 FAIL 06 for 081 and 084. The HEAD worktree shows `I3 FAIL: 081, 084` and `INCOMPLETE: 081 (no log line for I3), 084 (no log line for I3)`, because their I3 log lines were not in HEAD at that moment. I confirmed this in a scratch copy with HEAD's own script and tests (no 086 code): `1 failed, 3 passed` on these four tests, and the failing one is this test, with the same two lines. The new (c) assert sits after the `code == 0` assert, so it does not run while this test fails. In the working tree, the LOG BATCH line holds the (c) text (below).
- The other 3 are **caused by 086** (Deviation 1, sent back to I1). Each asserts `"<ID> (" not in out.split("INCOMPLETE:")[1]`, which is all the output after INCOMPLETE. The planned not-computable text `<ID> (<reason>)` on the new LOG BATCH line puts fixture items 065, 066 and 067 (timeless `_item` fixtures with I2 and I3 lines) there. At base the same 3 tests pass (scratch run above).
- New tests alone (`-k "batch or log_"`): `46 passed, 227 deselected in 5.01s`. That is the 26 new cases plus 20 existing `log_` tests.
- `python3.11 -m py_compile scripts/check_pipeline.py`: ok (RI-008). `test_fstrings_parse_on_python_310` and `test_git_call_census` pass in the full run.

`python3 scripts/check_pipeline.py` (working tree). The `NNN: complete`/`LEGACY` lines are omitted from this paste:
```
081: I3 FAIL (FULL; sent back to I1, needs a later PASS round in 06 (item 071))
082: in progress (FULL: next 05)
084: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))
086: in progress (FULL: next 05)
...
I3 FAIL: 081, 084
A1 FAIL: none
INCOMPLETE: none
RULE NOT SEEN: 083 (05 added in cfc0634 without TESTS_FORMAT_FROM (076): judged by I2_BEFORE; 06 added in cfc0634 without VERDICT_FROM (071): judged by no Sent-back check; item 084)
LOG TIME: none (not checked: 048: built before 045's --log rule reached main; times typed by hand, not recoverable (item 049))
LOG BATCH: none (not checked: 083: six lines written in one batch at 10:15 after the build (commit cfc0634 10:15:48); real times not recoverable (item 086)); not computable: 048 (no pytest time in 05/06/I2 line), 054 (no pytest time in 05/06/I2 line), 055 (no pytest time in 05/06/I2 line), 056 (no pytest time in 05/06/I2 line), 058 (no pytest time in 05/06/I2 line), 059 (no pytest time in 05/06/I2 line), 060 (no pytest time in 05/06/I2 line)
UNTRACKED CHANGE: none
...
SKIPPED: none
exit 1
```
Exit code check: the exit code is unchanged by 086. HEAD's script (`git show HEAD:scripts/check_pipeline.py`) run on the same tree exits 1 (I3 FAIL 081, 084). `diff` of its whole output against the new output gives one added line, the LOG BATCH line:
```
98a99
> LOG BATCH: none (not checked: 083: six lines written ...)
```

Mutations (scratch copy of the repo in the session scratchpad, `tests/test_pipeline_check.py -k "batch or log_"`, never in the repo):
```
M1: 1 failed, 45 passed, 227 deselected in 4.21s  -> test_batch_boundary_delta0[30.00-30.01-True]
M1b: 5 failed, 41 passed, 227 deselected in 3.97s  -> test_batch_083_shape_is_flagged, test_batch_boundary_delta0[29.99-30.01-False], test_batch_delta1_limit_is_120, test_batch_copy_of_05_in_06_is_dropped, test_batch_summary_in_test_id_is_not_a_run
M2: 5 failed, 41 passed, 227 deselected in 2.80s  -> test_batch_083_shape_is_flagged, test_batch_083_flagged_on_repo_data, test_batch_boundary_delta0[30.00-30.01-True], test_batch_sections_and_largest_value, test_batch_research_line_at_i2_minute_is_before
M3: 1 failed, 45 passed, 227 deselected in 2.84s  -> test_batch_copy_of_05_in_06_is_dropped
M4: 1 failed, 45 passed, 227 deselected in 2.86s  -> test_batch_untimed_item_is_not_computable
M5: 2 failed, 44 passed, 227 deselected in 2.95s  -> test_log_refused_after_later_steps, test_log_verdict_words_in_free_text_are_not_send_backs
M6: 4 failed, 42 passed, 227 deselected in 3.04s  -> test_log_after_i3_fail_is_written, test_log_after_blocked_or_not_a_fit_is_written[research-R3-5, test_log_after_blocked_or_not_a_fit_is_written[implementation-I1-NOT, test_log_after_a1_fail_is_written
M6b: 1 failed, 45 passed, 227 deselected in 2.94s  -> test_log_after_blocked_or_not_a_fit_is_written[research-R3-5
M7: 1 failed, 45 passed, 227 deselected in 2.93s  -> test_log_verdict_words_in_free_text_are_not_send_backs
M8: 1 failed, 45 passed, 227 deselected in 2.89s  -> test_log_batch_except_is_pinned
M9: 1 failed, 45 passed, 227 deselected in 3.10s  -> test_batch_summary_in_test_id_is_not_a_run
M10: 2 failed, 44 passed, 227 deselected in 3.02s  -> test_batch_083_flagged_on_repo_data, test_batch_malformed_last_line_still_ends_the_window
M11: 1 failed, 45 passed, 227 deselected in 2.96s  -> test_batch_sections_and_largest_value
restored: 46 passed, 227 deselected in 2.88s
```
How each mutation was made:

| Mutation | Change |
|---|---|
| M1 | `>= limit` → `> limit` |
| M1b | `(delta + 1) * 60` → `delta * 60` |
| M2 | 06 values ignored |
| M3 | `kept06 = list(t06)` |
| M4 | k = 0 → `known = [60.0]` |
| M5 | D's later-file check off |
| M6 | `_sent_back` removed from D |
| M6b | R3 group 1 |
| M7 | `word in fields` |
| M8 | `"048"` added to `LOG_BATCH_EXCEPT` |
| M9 | `.search` |
| M10 | malformed lines skipped in `_item_lines` |
| M11 | section ends only at `## ` |

Every mutation fails at least one named test.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat`: .claude/commands/run-item.md, scripts/check_pipeline.py, tests/test_pipeline_check.py; no TRIGGER path or data/real/)

## Deviations from plan
1. **Sent back to I1: the plan's LOG BATCH text breaks 3 existing tests, and the plan says no existing assertion is edited.**
   - `test_old_06_without_round_headers_unchanged` (L2162), `test_i3_fail_target_not_stated` (L2272) and `test_pass_without_sent_back_none_is_incomplete` (L2329) each assert `"<ID> (" not in out.split("INCOMPLETE:")[1]` for a fixture item: 065, 066 and 067.
   - Those fixtures (`_item`) have I2 and I3 lines but no pytest time, so 04's rule makes them not computable. 04's print format `not computable: <ID> (<reason>)` then writes `065 (`, `066 (` or `067 (` on the LOG BATCH line, which `main()` prints after INCOMPLETE as 04 asks.
   - Every fix needs a decision 04 does not make, so per my rule 1 I kept 04's format as built and did not choose one myself:
     - (a) print not-computable entries as `<ID>: <reason>` joined by `; `, like the `not checked:` part of the same line. I probed this in the scratch copy: the 3 tests pass, and only my N5 assert, which pins 04's text, would change (`1 failed, 48 passed`). 04's Expected-result text would change with it.
     - (b) print LOG BATCH before INCOMPLETE, which changes 04's placement.
     - (c) let the 3 tests split on the INCOMPLETE line only, which edits existing assertions.
   - I1, please choose one. The rest of the build does not depend on the choice.
2. **N2 and N3 numbers changed because of the plan's own copy guard.** 04's N2 non-flag case (05 30.00, 06 30.00) and N3 (45.00 + 45.00) use equal values. 04's copy guard drops an equal 06 value, so k = 1. N2 would then pass for the wrong reason, and N3 would not kill M1b (45.00 − 0.005 < 60). I used two distinct values with the same boundary arithmetic:
   - N2: 30.00 + 30.01 → flag (60.01 − 0.01 = 60.00 ≥ 60, as 04); 29.99 + 30.01 → no flag (59.99 < 60).
   - N3: 45.00 + 45.01 → 90.00 < 120, no flag; under M1b the limit is 60 → flag.

   Both kill their mutations (M1, M1b above). I1/I3: please confirm.
3. **Additions to 04's branches, each on the not-flag side.**
   - (i) `in_progress` is "no I3 line after the item's *last* I2 line". 04 says "first I2 line and no later I3 line". A round-2 I2 run logged after the last I3 would lie outside the window and break the proof, so an open round is in progress until its I3 logs. N12 holds either way.
   - (ii) An unreadable log file makes **every** item not computable with `<file> unreadable`. 04 says "every item with lines of that date", but which items have lines in a file that can't be read is not knowable. A lost line could move start or end.
   - (iii) A LOG_LINE with an impossible time such as `25:00` gives `not computable (log line with no valid time)`, never a crash.
   - (iv) The flag test is `round(Σ − BATCH_ROUND·k, 3) >= limit`. Without it, float noise turns 30.00 + 30.01 − 0.01 into 60.00000000000001 and 45.00 + 45.01 − 0.01 into 89.99999999999999 (measured). The values have 2 decimals, so the rounding is exact.
   - (v) `_item_lines` tuples carry the fields as a 6th element, which the I2 seconds need. 04 lists 5 elements.
4. Test (a) also runs a spaced control (the same item with I1 10:20, I2 10:30, I3 10:40): `LOG BATCH: none`, exit 0. This shows the exit 1 comes from LOG BATCH.
5. D needs no 083 exception: it is checked at write time only, and 083's lines already exist. 083 is not added to `LOG_TIME_EXCEPT`, and the pin test asserts it.

Rule D and today's run: this item's own `--log I2 086` runs with 01-05 present and no 06, so there is no later file and nothing is refused. I3 writes 06 and 07 before its line, and neither counts for I3 (07 never counts). Round 2 of 081 and 084 (I1/I2 re-logs with 05/06 present) passes, because both items now have an `I3 | FAIL` line (D3).

RI-010: guardrail built (086); GUARDED when merged, fixture (b) gives 083 flagged on main, and the next items have LOG BATCH: none
RI-001: unchanged (every filter in 086 has a measured count above: step 0 (i)-(iii), 39 checked / 1 flagged with the exception emptied)
RI-014: unchanged (C and D make no git call; census 46 unchanged)

Recurring issues checked (item 013), open or ESCALATED:
- RI-001 (ESCALATED): each new filter has a code count (step 0).
- RI-010 (ESCALATED, this item): fixture (b) is met on real data. `LOG_BATCH_EXCEPT` is pinned, and 083 is not in `LOG_TIME_EXCEPT`.
- RI-014 (OPEN): there is no git call, so the results are the same with or without git (test (a) and N5 run in a no-git tmp tree).

Also checked:
- RI-002: no time defaults to 0 or 60 (N5, M4).
- RI-004/RI-005: the boundary arithmetic is re-derived (Deviation 2).
- RI-006: counts come from commands.
- RI-007: the RULE_PATHS change needs the person's OK.
- RI-008: py311 compile ok.
- RI-009: mutations ran in a scratch copy, never in the repo; built on 081 and 084.
- RI-012: verdicts are read from fullmatch groups and summaries are anchored (D7, N8, M7, M9).

## Round 2 (2026-11-21, I2)
Base: daily-fixes/2026-11-20 at fd2b139 (includes 081 r1+r2, 084 r1+r2 and 086 r1 416835f; their code was not touched). Built from 04 "## Round 2" (R2-1 to R2-4 and the round-2 build steps). Not committed (the orchestrator commits). No brokerage connection; every new fixture is a tmp_path tree. The round-1 text above is kept as written.

### Changes made (round 2)
File counts (by command, 012):
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
0
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
2
```
- `scripts/check_pipeline.py`:
  - R2-1: the `main()` print is now `"; not computable: " + "; ".join(f"{i}: {why}" for i, why in batch["not_computable"])`, which is format (a), the same `<ID>: <why>` shape as `not checked:`.
  - The docstring LOG BATCH entry now reads ``as `not computable: <ID>: <reason>` (entries joined by "; ")``, and the lines after it are rewrapped. No other code changed: `git diff --stat` shows `16 ++++++-------`, and the only non-docstring line is the print.
- `tests/test_pipeline_check.py`:
  - N5's assert (086's own test) is now `"LOG BATCH: none; not computable: 999: no pytest time in 05/06/I2 line"`.
  - N2 (`test_batch_boundary_delta0`) gets an `end` column and a third case, `("0.02", "119.99", "10:01", True)` (R2-3 (iv), see the search below).
  - New N12b `test_batch_open_round_keyed_on_last_i2`, N13 `test_batch_unreadable_log_file_makes_every_item_not_computable` and N14 `test_batch_invalid_log_time_is_not_computable`.
  - No existing (pre-086) assertion was edited. N2/N3 values are as built in round 1 (R2-2).
  - 086 cases: `pytest --collect-only` gives 30 (26 in round 1 + N2 third case + N12b + N13 + N14), which matches 04's "29 (+ 1 if the pair exists)".
- `.claude/commands/run-item.md`: unchanged in round 2. The round-1 total is still 3 files.

### R2-3 (iv) rounding search (scratch `r2_round_search.py`, never in the repo, 2026-11-21 00:5x UTC)
The search takes 2-decimal pairs a ≠ b with |a − b| > 0.01 and a + b − 0.01 == limit in decimal. It tests the code's own float expression `sum([a, b]) - 0.005 * 2 < limit`, without `round()`:
```
limit 60: pairs tried 6000, below-limit pairs 0, first []
limit 120: pairs tried 12000, below-limit pairs 6302, first [('0.02', '119.99', '119.99999999999999'), ('0.05', '119.96', '119.99999999999999'), ('0.07', '119.94', '119.99999999999999')]
```
The count is 0 at Δ0. It is 6302 at Δ1, so the first pair (0.02, 119.99) is added as N2's third case. That case runs at Δ1 (I1 10:00, I2/I3 10:01, limit 120), which is why N2 now has an `end` column. M15 was added as well, and it fails on that case (below). `round()` is therefore load-bearing at limit 120, not merely harmless.

### Connectivity check (round 2)
- [x] Every new function and rule is used. There is no new function. The changed print feeds the `LOG BATCH:` line, which run-item L14, I3 and A1 read. The new tests call `batch_log_items` through `_bl`.
- [x] Every input has a source and every output a consumer. This is unchanged from round 1.
- [x] Every branch ends in a defined result, and each not-computable branch now has an absent-case test:
  - k = 0: N5;
  - unreadable 05/06: N11;
  - no line before I2: N12;
  - open round: N12b, `in_progress`;
  - unreadable log file: N13, every item not computable with the file named;
  - invalid HH:MM: N14, `log line with no valid time`.
- [x] No leftover TODOs or unused files. The scratch scripts and copies live only in the session scratchpad.

Missing-data policy:
- `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/` gives 38 hits, all pre-existing (`git diff --stat -- ccbot/` is empty). There is no new or changed hit.
- The same pattern, plus `: float = ` and `: int = `, over the added lines of both changed files (`git diff -U0 ... | grep "^+"`) gives 0 hits.
- No dataclass and no new comparison were added. The one `>=` (`round(...) >= limit`) is unchanged and runs only on parsed `\d+\.\d+` values, so it never sees NaN.

### Recurring issues checked (round 2, item 013)
- RI-001 (ESCALATED): the R2-3 (iv) search has a dated count: 0 at 60 and 6302 at 120. N2/N3 are re-derived with k = 2, as round 1 built them.
- RI-010 (ESCALATED, this item): fixture (b) still gives 083 flagged on real data (`excepted={}` → `flagged ['083']`, below). `LOG_BATCH_EXCEPT` is pinned (M8). The real line keeps (c)'s text `LOG BATCH: none (not checked: 083: six lines written in one batch`.
- RI-014 (OPEN): no git call was added. `git diff scripts/check_pipeline.py | grep -c "^+.*_git"` gives 0, the census total is 47 as the orchestrator stated, and `test_git_call_census` passes.
- RI-002 (GUARDED): see the missing-data policy above. M4, M13 and M14 each fail a test.
- RI-004/RI-005 (GUARDED): N2's third case is re-derived as 0.02 + 119.99 − 0.01 = 120.00 ≥ 120 in decimal, and the float value is 119.99999999999999.
- RI-009: base and mutation runs were done in scratch copies (`i2-086-r2-base-005453`, `i2-086-r2-mut-<HHMMSS>` in the session scratchpad), never in the repo. After the mutations, `git diff --stat` in the repo still shows only the 2 files.
- RI-012 (GUARDED): unchanged (D7, N8, M7, M9 all still fail their tests).

RI-010: guardrail built (086); GUARDED when merged, fixture (b) gives 083 flagged on main, and the next items have LOG BATCH: none
RI-001: unchanged (R2-3 (iv) count 0 at limit 60, 6302 at limit 120, 2026-11-21)
RI-014: unchanged (no git call added; census total 47)

### Feasibility numbers (measured, round 2)
`batch_log_items()` on the repo (working tree, 2026-11-21 00:58 UTC):
```
excepted= None checked 39 flagged [] excepted ['083'] not_computable ['048', '054', '055', '056', '058', '059', '060'] in_progress ['081']
excepted= {} checked 39 flagged ['083'] excepted [] not_computable ['048', '054', '055', '056', '058', '059', '060'] in_progress ['081']
```
- 081 is in progress: its round-2 I2 line comes after its last I3 line, which is R2-3 (i) at work.
- 086 is now checked: its round-1 I2 line is followed by an I3 FAIL line. It goes back to in progress once this round's I2 line is logged.

### Test output (round 2, pasted)
Full suite before the round-2 edits (HEAD fd2b139, repo):
```
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_old_06_without_round_headers_unchanged
FAILED tests/test_pipeline_check.py::test_i3_fail_target_not_stated - Asserti...
FAILED tests/test_pipeline_check.py::test_pass_without_sent_back_none_is_incomplete
4 failed, 642 passed, 1 skipped in 87.65s (0:01:27)
```
Full suite after the round-2 edits (`python3 -m pytest -q`, repo root, final run):
```
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 649 passed, 1 skipped in 83.52s (0:01:23)
```
R2-4 bar:
- The 3 P1 tests pass. In the full run above, the only FAILED line is the allowed test. Run alone with N2, N5 and N12b-N14: `11 passed, 275 deselected in 0.46s`.
- The allowed failure, `test_repo_pipeline_has_no_skipped_items`, fails at `assert code == 0`. The only error line in the output is `I3 FAIL: 081, 086` (INCOMPLETE none, A1 FAIL none, SKIPPED none):
  - 084 passed I3 round 2 (fd2b139), so the reason changed from 04's `I3 FAIL: 081, 084` to `081, 086`.
  - 086's own I3 round-1 FAIL is correct while its round is open (item 071 rule).
- Base (1): a scratch copy of this working tree (`i2-086-r2-base-005453`) with `scripts/check_pipeline.py` and `tests/test_pipeline_check.py` from 129120b, the commit before 086's code (416835f). So it has no 086 code at all:
  ```
  FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
  1 failed, 246 deselected in 3.77s
  I3 FAIL: 081, 086
  A1 FAIL: none
  INCOMPLETE: none
  SKIPPED: none
  exit 1
  ```
  It is the same test ID with the same reason.
- Base (2): HEAD fd2b139 (086 r1 code), in the full run before the edits above, fails it too.
- No other test fails.

`-k "batch or log_"`: `51 passed, 235 deselected in 3.25s`.
`python3.11 -m py_compile scripts/check_pipeline.py`: `py311 compile ok`.
`-k "census or fstrings_parse"`: `1 passed, 285 deselected in 0.07s`. The full run also passes `test_fstrings_parse_on_python_310`.

`python3 scripts/check_pipeline.py` (repo, working tree). The LOG BATCH line is in format (a):
```
LOG BATCH: none (not checked: 083: six lines written in one batch at 10:15 after the build (commit cfc0634 10:15:48); real times not recoverable (item 086)); not computable: 048: no pytest time in 05/06/I2 line; 054: no pytest time in 05/06/I2 line; 055: no pytest time in 05/06/I2 line; 056: no pytest time in 05/06/I2 line; 058: no pytest time in 05/06/I2 line; 059: no pytest time in 05/06/I2 line; 060: no pytest time in 05/06/I2 line
exit 1
```
The exit code is unchanged by 086. I ran HEAD's script (`git show HEAD:scripts/check_pipeline.py`) and 129120b's (pre-086) script on the same tree. Both exit 1, and their whole outputs differ from the new one only on the LOG BATCH line:
```
$ diff r2_head_out.txt r2_new_out2.txt        # HEAD (086 r1) script vs round 2
99c99
< LOG BATCH: none (not checked: 083: ...); not computable: 048 (no pytest time in 05/06/I2 line), 054 (...), ...
---
> LOG BATCH: none (not checked: 083: ...); not computable: 048: no pytest time in 05/06/I2 line; 054: ...; ...
$ diff r2_pre086_out2.txt r2_new_out2.txt     # pre-086 script vs round 2
98a99
> LOG BATCH: none (not checked: 083: six lines written in one batch at 10:15 after the build (commit cfc0634 10:15:48); real times not recov...
```
Note: my first run of these diffs also showed `084: complete` / `084: awaiting A1` and `AWAITING A1: none` / `084`. A1 was writing work/084/07 and logs/audit/2026-11-21-084.md at the same time, in another thread. A re-run on the same tree (above) has only the LOG BATCH difference.

Mutations. They ran in a scratch copy of the repo (`i2-086-r2-mut-<HHMMSS>` in the session scratchpad, script `i2_086_r2_mutate.py`), never in the repo. The command was `tests/test_pipeline_check.py -k "batch or log_ or old_06_without_round_headers_unchanged or i3_fail_target_not_stated or pass_without_sent_back_none_is_incomplete"`:
```
unmutated: 54 passed, 232 deselected in 6.58s
M1: 2 failed, 52 passed, 232 deselected in 3.48s  -> test_batch_boundary_delta0[30.00-30.01-10:00-True], test_batch_boundary_delta0[0.02-119.99-10:01-True]
M1b: 5 failed, 49 passed, 232 deselected in 3.74s  -> test_batch_083_shape_is_flagged, test_batch_boundary_delta0[29.99-30.01-10:00-False], test_batch_delta1_limit_is_120, test_batch_copy_of_05_in_06_is_dropped, test_batch_summary_in_test_id_is_not_a_run
M2: 6 failed, 48 passed, 232 deselected in 3.91s  -> test_batch_083_shape_is_flagged, test_batch_083_flagged_on_repo_data, test_batch_boundary_delta0[30.00-30.01-10:00-True], test_batch_boundary_delta0[0.02-119.99-10:01-True], test_batch_sections_and_largest_value, test_batch_research_line_at_i2_minute_is_before
M3: 1 failed, 53 passed, 232 deselected in 3.48s  -> test_batch_copy_of_05_in_06_is_dropped
M4: 1 failed, 53 passed, 232 deselected in 3.44s  -> test_batch_untimed_item_is_not_computable
M5: 2 failed, 52 passed, 232 deselected in 4.46s  -> test_log_refused_after_later_steps, test_log_verdict_words_in_free_text_are_not_send_backs
M6: 4 failed, 50 passed, 232 deselected in 3.76s  -> test_log_after_i3_fail_is_written, test_log_after_blocked_or_not_a_fit_is_written[research-R3-5 verified, 0 fixed, 0 removed | BLOCKED-steps0], test_log_after_blocked_or_not_a_fit_is_written[implementation-I1-NOT A FIT | 0 files planned-steps1], test_log_after_a1_fail_is_written
M6b: 1 failed, 53 passed, 232 deselected in 3.54s  -> test_log_after_blocked_or_not_a_fit_is_written[research-R3-5 verified, 0 fixed, 0 removed | BLOCKED-steps0]
M7: 1 failed, 53 passed, 232 deselected in 3.50s  -> test_log_verdict_words_in_free_text_are_not_send_backs
M8: 1 failed, 53 passed, 232 deselected in 3.56s  -> test_log_batch_except_is_pinned
M9: 1 failed, 53 passed, 232 deselected in 3.47s  -> test_batch_summary_in_test_id_is_not_a_run
M10: 2 failed, 52 passed, 232 deselected in 3.56s  -> test_batch_083_flagged_on_repo_data, test_batch_malformed_last_line_still_ends_the_window
M11: 1 failed, 53 passed, 232 deselected in 3.88s  -> test_batch_sections_and_largest_value
M12: 4 failed, 50 passed, 232 deselected in 4.71s  -> test_old_06_without_round_headers_unchanged, test_i3_fail_target_not_stated, test_pass_without_sent_back_none_is_incomplete, test_batch_untimed_item_is_not_computable
M13: 1 failed, 53 passed, 232 deselected in 3.84s  -> test_batch_open_round_keyed_on_last_i2
M14: 1 failed, 53 passed, 232 deselected in 3.75s  -> test_batch_unreadable_log_file_makes_every_item_not_computable
M15: 1 failed, 53 passed, 232 deselected in 3.67s  -> test_batch_boundary_delta0[0.02-119.99-10:01-True]
restored: 54 passed, 232 deselected in 3.73s
```
M1-M11 are the same edits as round 1 (table above). The new ones:

| Mutation | Change |
|---|---|
| M12 | round-1 print `f"; not computable: {', '.join(f'{i} ({why})' ...)}"` restored |
| M13 | `order(end) < order(last_i2)` → `order(end) < order(first)` (in progress keyed on the first I2) |
| M14 | `unreadable.append(...)` in `_item_lines` → `pass` (unreadable log file skipped silently) |
| M15 | `round(total - BATCH_ROUND * len(known), 3) >= limit` → `total - BATCH_ROUND * len(known) >= limit` |

Every mutation fails at least one named test. M12 fails exactly the 3 existing tests plus N5, as R2-1 expects.

### Real-data effect (round 2)
not required (`git diff --stat`: scripts/check_pipeline.py, tests/test_pipeline_check.py; no TRIGGER path or data/real/)

### Deviations from plan (round 2)
1. **N13's `_run` part is not asserted, because of a pre-existing crash outside 086's scope.** R2-3 (ii) says "`_run` exit 0 when nothing else is wrong". Something else is wrong: `main()` reads every log file through older readers with no decode guard, and a non-UTF-8 log file raises UnicodeDecodeError there before LOG BATCH prints. The readers are `_log_text` (items 043/077, `"".join(f.read_text(encoding="utf-8") ...)`), `orphan_log_lines` (047) and the I3 last-line loop in `incomplete()` (071). They are in the scope lock (`incomplete`), or outside 086 entirely. So N13 asserts C in-process only: every item is not computable with the file named, nothing is flagged, and there is no traceback from `batch_log_items`. Probe (scratch tree `i2-086-r2-n13probe`: one item, one good log file and one `\xff\xfe` log file): `check_pipeline.py` ends in `UnicodeDecodeError` via `main` L1516 → `incomplete` L669 → `_log_text` L581, exit 1. This is loud, not silent (a traceback, exit ≠ 0), so it is not an RI-002 pass. **I1/A1: please consider a separate item** that gives these readers the `<file> unreadable` handling `_item_lines` already has.
2. **N2's third case runs at Δ1.** The R2-3 (iv) search found no pair at limit 60 and 6302 at limit 120. Following 04 ("If the count is 0 at Δ0, repeat at limit 120"; "If the count is ≥ 1, add the first pair as a third N2 case"), the case uses the limit-120 pair. It therefore needs I2/I3 at 10:01, so N2's parametrize gained an `end` column. The two round-1 cases keep `end = "10:00"`, with the same values and results.
3. 04 R2-4 names the allowed failure's reason as `I3 FAIL: 081, 084`. Today it is `I3 FAIL: 081, 086`, because 084 passed its I3 round 2 in fd2b139. The base copy shows the same reason, so the bar's "same stated reason at base" holds with today's set.
