# 06 Verification - 089
Verdict: PASS (round 1)
Sent back to: none

Method: I3 read the current rules file .claude/agents/i3-verifier.md and .claude/commands/run-item.md, templates/verification.md, logs/recurring-issues.md, work/089/request.md, 01-05, work/088/07-audit-task.md point 3, and `git diff 33add8e 0ad4d62` (both changed files, whole). Build commit verified: 0ad4d62 (I2). Every run below was made by me on 2026-11-22 between 00:14 and 00:40 UTC in my own worktrees of 0ad4d62 (`/tmp/claude-0/scratch/i3-089/wt` for the suite, check_handoff, the step 10 diff; `/tmp/claude-0/scratch/i3-089/mut` for mutations and probes), never in the main checkout (087's I2 is editing tests/test_agent_tools.py there). Both worktrees are removed after this file. HEAD of the branch moved to e4edcb0 (087 I2/I3) meanwhile; `git diff --stat 0ad4d62 e4edcb0` touches only logs/implementation/2026-11-22.md, tests/test_agent_tools.py, work/087/05 and 06, none of 089's files.

## I1 audit (plan vs research)
04 follows 03 (READY, 70 rows, check_handoff PASS) step by step; its Rule trace maps every 03 step 1-10, Q1-Q7 and the row 24/52/53/58/69/70 corrections to a Files line or a test. I checked each of the 7 "WITH CHANGES" points against 03 and the code:
1. Test (c) UNTRACKED CHANGE text: 03 step 5's text lacked `_note(c)`; 04's form with `(cutoff <c7> from --untracked-from)` matches the code and the existing L1649-1650 test. Correct fix, sourced from the repo.
2. ORPHAN LOG wording: 03's `none; not checked:` starts with `none` (RI-002 shape); 04's two forms are the right correction.
3. Probe anchors: both anchor lines exist verbatim once at 0ad4d62 (test_probe_guardrails C12 green, below).
4. Strict ID CLASH with unreadable mine: 03 (vii)'s "no clash compare" would have hidden a clash; 04's `theirs != None` keeps it listed. Correct (RI-002).
5. Missing-input fixtures: additions are all from 03's own Missing inputs table, not new scope.
6. real_data_field unreadable request treated as built: strict, follows from 03 (v).
7. `_shown`: sourced to the codecs page (backslashreplace) and 03 row 70.
Extra research (subprocess `_translate_newlines`, BOM, PermissionError not fixturable as root, `_UNREAD` shared module) each has a source or a repo line. No unsourced addition. The one wrong assumption in 04 (L10 "GIT_LINES already ends with RULE NOT SEEN", L157 "GIT_LINES unchanged") came from reading 088's working tree before 088's I3 deferred E1; I2 handled it (Deviation 1, below). Not a plan defect that changes the build.

## I2 audit (build vs plan)
Line by line against 04 "Files to create/change" (diff 33add8e..0ad4d62):
- Files 1-3 `_UNREAD`, `_shown`, `_read`: as planned (read_bytes + strict decode + the two `.replace`; `except (OSError, UnicodeDecodeError)`; missing_ok FileNotFoundError → (None, None) unrecorded; detail `not UTF-8 at byte {err.start}` or class name; why `<shown> unreadable`).
- 4 `read_request` deleted; Grep finds no caller in scripts/ or tests/. 5 `_i3_verdict_text` + `i3_verdict` wrapper. 6 classify: one request.md read (FAST uses it), 06 and both 07 sites → `("UNREADABLE", why)`.
- 7 `_log_text` → (text, whys). 8 uncommitted_steps not-checked form. 9 incomplete: 06 read once; log_whys entry gated on any 01-06 file; unlogged / format / Suite / I3-line checks gated `not log_whys`; Suite block keeps `            elif suites[0] != field:` byte-identical. 10-12 `_sent_back`, orphan_log_lines (orphans, whys), `_item_lines`, `_run_seconds` via `_read`, same results.
- 13 open_branches: `mine_text` via `_read`, `theirs != mine_text`, `                clashes.append(item)` unchanged. 14 `_shallow_boundaries` exactly as the 4 bullets. 15 research_code `unread` dict, detail replaced keyed by item. 16 real_data_field gaps. 17/18 inbox texts. 19 main: `_UNREAD.clear()` first statement, UNREADABLE line after `inbox_section()` and before INBOX, `or unreadable` in the final return only. 20 docstring paragraph matches the code.
- Read census, my Grep at 0ad4d62: `read_bytes` once (in `_read`), `log.open("a")` once (write_log), no `read_text(` call left (the 2 hits are docstring words, L290, L449).
- Tests: `_run3`, `_tree`, `_pick1`, the 20 tests named in 05, test (c) and N13 edits; all match 04's Tests table row by row (expected strings checked against the table).

Deviations (05) judged:
1. **E1 (GIT_LINES gains `"RULE NOT SEEN:"`): accepted, required.** 088/07 point 3 says "Check that 089's build adds E1 and that (a), (b) and (c) pass with it." Met: tests/test_pipeline_check.py L2365-2367 at 0ad4d62 ends GIT_LINES with `"RULE NOT SEEN:"`; (a) `test_all_git_fails_no_line_says_none`, (b) `test_malformed_shallow_real_git_nothing_none`, (c) `test_non_utf8_shallow_line_no_traceback` pass in my full run and alone (`-k`: 3 passed, 327 deselected). Teeth, my probe in `mut`: with M7 put back, (c) fails at `assert not any(l.rstrip().endswith(": none") for l in lines)` (the GIT_LINES loop, i.e. `RULE NOT SEEN: none`); with M7 and E1 both removed, (c) gets past that loop and fails only later at 089's UNTRACKED CHANGE assert. So E1 is what catches RULE NOT SEEN reading none. No follow-up item is needed for 088 point 3.
2. **6c second item 151: accepted.** I confirmed the reason: in 04's 6c tree 150 has only request.md + 06, so classify returns SKIPPED before reading 06, and M14 would survive. With 151 (complete, 06 bad) M14 fails `test_unreadable_06` (my run below). Test addition only, strengthens the plan's M14 row; no code change.
3. **6f inside N13: accepted.** It is what 04's N13 row says ("plus the 6f `_run3` assert"); the asserts are at L3173-3180.
4. T-sh resets with `.clear()` after one `monkeypatch.setattr`: follows 04's research note; accepted.

Connectivity check (redone): `_read` is called at every former read site (21); `_shown` by `_read`; `_i3_verdict_text` by i3_verdict, classify, incomplete; `_UNREAD` filled by `_read`, cleared/printed/turned into `unreadable` in main and into the exit. Every why reaches a printed line; my real-repo probe below shows each consumer line. Unreachable-in-practice branches (the `_last_log_line` / I3-loop skips) are documented as a race and the file is still on UNREADABLE. No TODO (`grep -n TODO scripts/check_pipeline.py`: none). Whole-output diff (step 10, RI-013), redone in my worktree: base = `git show 33add8e:scripts/check_pipeline.py`, head = 0ad4d62, same cwd, no args:
```
base exit 0
head exit 0
$ diff before.txt after.txt
109a110
> UNREADABLE: none
 111 before.txt
 112 after.txt
```
Same as 05: exactly one added line, between ORPHAN LOG and INBOX.

## Tests re-run (output)
Full suite, my worktree of 0ad4d62, 2026-11-22 ~00:15 UTC:
```
$ python3 -m pytest -q
........................................................................ [ 92%]
...................................................                      [100%]
698 passed, 1 skipped in 85.52s (0:01:25)
```
Same count as 05 (698 passed, 1 skipped). The skip (second run with `-rs`, 698 passed, 1 skipped in 82.61s): `SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars'`, unrelated.
Oldest Python: `tests/test_safety.py::test_every_py_compiles_on_oldest_python` ran and passed with python3.11 (python3.10 not on PATH; /usr/bin/python3.11 is). Also `python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py` → OK. `tests/test_safety.py tests/test_probe_guardrails.py` → 23 passed.

check_handoff (re-run in my worktree, 00:16 UTC):
```
$ python3 scripts/check_handoff.py 089
sources count (unique URLs in 01-research.md): 11
fact-check rows: 70
totals line: 70 rows -> 64 as-is, 5 fixed, 1 removed
PASS
exit 0
```

Mutations re-run by me (scratch worktree `mut`, one at a time, file restored after each; `git status --short` clean after), `python3 -m pytest -q tests/test_pipeline_check.py`:
| ID | Result | Failing tests (all) |
|---|---|---|
| M1 OSError only | 20 failed, 310 passed | incl. test_unreadable_log_exits_1_alone, test_read_contract, test_non_utf8_shallow_line_no_traceback |
| M2 UnicodeDecodeError only | 5 failed, 325 passed | test_read_contract, test_shallow_file_unreadable_not_checked, test_shallow_file_unreadable_whatever_the_flag, test_shallow_flag_unknown_no_file_is_full, test_unreadable_log_directory |
| M3 `or unreadable` dropped | 6 failed, 324 passed | test_unreadable_07, _cleared_between_runs, _log_directory, _log_exits_1_alone, _request, _request_still_clashes |
| M4 `_UNREAD.clear()` dropped | 2 failed, 328 passed | test_unreadable_cleared_between_runs, test_unreadable_printed_before_inbox_early_return |
| M5 classify request.md raw read_text | 3 failed, 327 passed | test_read_census, test_unreadable_request, test_unreadable_request_still_clashes |
| M6 UNREADABLE after the INBOX early return | 2 failed, 328 passed | test_unreadable_log_exits_1_alone, test_unreadable_printed_before_inbox_early_return |
| M7 shallow why → `"unreadable" if sure else "full"` | 2 failed, 328 passed | test_non_utf8_shallow_line_no_traceback, test_shallow_file_unreadable_whatever_the_flag |
| M8 shallow failure not recorded | 2 failed, 328 passed | same two |
| M9 orphan whys dropped | 2 failed, 328 passed | test_orphan_log_with_unreadable_file, test_unreadable_log_exits_1_alone |
| M10 incomplete computes from "" (log_whys forced []) | 1 failed, 329 passed | test_unreadable_log_consumers_say_not_checked |
| M11 newline normalisation dropped | 2 failed, 328 passed | test_cr_only_07_reads_as_lines, test_read_contract |
| M12 why text changed | 13 failed, 317 passed | incl. test_batch_unreadable_log_file_makes_every_item_not_computable (N13), test_batch_unreadable_06_is_not_computable (N11) |
| M13 clash skipped when mine unreadable | 1 failed, 329 passed | test_unreadable_request_still_clashes |
| M14 classify 06 → i3_verdict (verdict None) | 1 failed, 329 passed | test_unreadable_06 |
| M15 real_data_field skips unreadable request | 1 failed, 329 passed | test_real_data_field_unreadable_request_and_05 |
| M16 research_code drops the unread detail | 1 failed, 329 passed | test_research_code_unreadable_request |
Every count equals 05's table.

BUG checks (step 3):
- Fix and guardrail both in place: the shared reader + census (`test_read_census`), end-to-end no-traceback fixtures (6a-6m, T-*), N13's `_run3` assert, `_shallow_boundaries` change + test (c)'s three new asserts.
- The guardrail catches the original error: base script (33add8e) copied into `mut`, `-k "unreadable or read_contract or read_census or cr_only or non_utf8_shallow"` → `21 failed, 3 passed` (Tracebacks in 6c/6l stderr, `AttributeError` for `_read`, the census assert, test (c) at the new UNTRACKED CHANGE assert). Restored with `git checkout`.
- Real-repo probe (the request's "Done looks like"), `mut` at 0ad4d62: one `\xff` appended to logs/implementation/2026-11-21.md and to work/088/06-verification.md → exit 1, 0 Traceback lines in stderr, `088: UNREADABLE (work/088/06-verification.md unreadable)`, `UNCOMMITTED STEP: not checked (logs/implementation/2026-11-21.md unreadable; item 089)`, `ORPHAN LOG: not checked (logs/implementation/2026-11-21.md unreadable; item 089)`, INCOMPLETE `log lines not checked (...)` per item, `UNREADABLE: logs/implementation/2026-11-21.md (not UTF-8 at byte 1640), work/088/06-verification.md (not UTF-8 at byte 10234)`. The .git/shallow case is test (c) (byte 41). Restored.
- RI-001 feasibility re-run: census 22 → 2 (my Grep and test_read_census); offsets 0/5/12/41 asserted in passing tests; CHECKLIST_FROM edge 040 (< 41) gets no entry, 150 exactly one (6e passes); globs unchanged. No rule text the person follows cites a number here.
- RI-002 put-back: M10 restores the old "compute from what is left" default (log_whys forced to []), and fails test_unreadable_log_consumers_say_not_checked; M9/M13/M15/M16 put back the bare-none / drop forms, each fails a named test. 05's grep reasons: I checked each of the 5 hits in the diff; each `is not None and` guard is preceded by a branch that adds a not-checked entry for the unreadable case, as 05 says. ccbot/ untouched (`git diff --stat 33add8e 0ad4d62 -- ccbot/` empty).
- Data-hole edges: the reader set is the glob set, unchanged; lower edge of the checked item range (CHECKLIST_FROM) is pinned by 6e's 040; a log file outside `????-??-??.md` (only `_log_text` reads it) still lands in log_whys. No date-window data in this item.
- Rule the person follows (001): none changed.
- RI-012 text matching: no new code classifies by matching text. The detail comes from the exception class and `err.start`; consumers branch on `why` being set, and research_code's replacement is keyed by item ID in a dict, never by matching the detail string. N/A, no FAIL.
- Simulator/replay (item 062): N/A, no simulator.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat 33add8e 0ad4d62`: scripts/check_pipeline.py, tests/test_pipeline_check.py, work/089/05-build-report.md, logs/implementation/2026-11-22.md; none is in TRIGGER/TRIGGER_DIRS)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-010, RI-014, RI-002, RI-012, RI-013, RI-008, RI-009, RI-006
- RI-001 (ESCALATED): every count re-run (census, offsets, 040/150 bound, 16 mutations, 1-line diff); none taken from 05.
- RI-010 (ESCALATED): my log line is written only with `check_pipeline.py --log I3 089 ...` right after this file, before 07; committed with this file and 07.
- RI-014 (OPEN): this item's family. A non-UTF-8 or directory shallow file is "unreadable" whatever the flag (M7/M8 fail (c) and T-sh); E1 is in GIT_LINES and has teeth (probe above). 088/07 point 3 condition met.
- RI-002 (GUARDED): no bare none or "" computation for lost input (M9, M10, M13, M15, M16 fail named tests).
- RI-012 (GUARDED): no text-match classification added (above).
- RI-013 (GUARDED): whole-output diff redone, 1 line.
- RI-008 (GUARDED): oldest-python test ran with 3.11 (3.10 absent); py_compile OK.
- RI-009 (GUARDED): all runs in my own worktrees; HEAD moved to e4edcb0 (087) with no overlap with 089's files; I stage only my three files.
- RI-006 (GUARDED): the Suite line and mutation counts are copied from my pytest output.

Guardrail status (for A1 to copy on main, item 036): RI-014 guardrail extended by 089 (one reader, shallow decode error never "full", E1), stays OPEN until merged and probed; RI-002 unchanged, GUARDED.

## Pipeline line (step 2)
check_pipeline line: `089: awaiting A1 (FULL)`

Run 00:28 UTC in my worktree of the branch head f52ad15 (087's I1 commit; no 089 file changed since 0ad4d62) with this 06, 07 and my log line copied in; exit 1 comes only from `087: I3 FAIL (FULL; sent back to I1 I2, ...)` (087's own round). INCOMPLETE: none, SKIPPED: none, LOG TIME: none (048 note only), UNCOMMITTED STEP: none, UNREADABLE: none; LOG BATCH does not name 089.

## Sent back / sent to Audit
PASS, sent to Audit: work/089/07-audit-task.md. Follow-ups carried from 05 (not defects of 089): scripts/check_handoff.py L55/L62 still read strictly (A1 to open an item); 090's new reads must use `_read` (test_read_census enforces); 091 should not duplicate 6a/M3's `unreadable` exit-term test.
