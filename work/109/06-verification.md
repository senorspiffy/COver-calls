# 06 Verification - 109
Verdict: PASS (round 1)
Sent back to: none
Scratch dir: /tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i3-109-r1-skpodtqz

Made with `python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="i3-109-r1-", dir="/tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad"))'`. Inside it, four `git worktree add --detach` worktrees at a5b8edd (I2's build commit): `wt/` (full suite), `m1/` and `m2/` (mutants), `m3/` (probes, check_handoff). Every test run used PYTHONDONTWRITEBYTECODE=1, `-B` and a fresh PYTHONPYCACHEPREFIX under the scratch dir. No test ran in the main checkout (107 was being built there). No `git stash` anywhere. Every mutant or probe was restored with `git checkout HEAD -- <file>` inside its worktree; `git status --short | wc -l` printed 0 in wt, m1, m2 and m3 afterwards.

## I1 audit (plan vs research)
04's Rule trace has one row per 03 map step (1-9), per fact-check fix and per Missing-inputs row; I checked each against Files 1a-1l and Tests. Every 03 rule is carried or dropped with a reason (only the pytest-gremlins wording fix, which is nothing to build).
Changes to 03, each sourced:
- C1 (kill ids `<file>::<test>` checked by ast in the named file): needed, S17's kills are in tests/test_real_data_field.py (confirmed: `test_t7b_cutoff_edge_item_070_is_checked`, `test_t7_items_before_cutoff_are_not_checked` live there).
- C2 (`<module>` owner): sourced to the ast docs; no site exists today, the count stays 17 (re-counted below).
- C3 (pinned 18th-site probe instead of a manual one): strengthens 03 step 1.
- C4 (comment check rewritten so it is not vacuous): correct, 03's grep string spans a line break.
- C5 (`startswith("INCOMPLETE: 075 (")`): sound.
- C6 (cost of 34 runs; `-k` pre-check never the result): procedural.
Research 3 (S7 FROM-1 equivalent, S8 FROM-1 not): I re-traced it in `incomplete` at a5b8edd. At 089, `log_fields_ok` ignores `timed` (it only matters for IDs >= TIMED_FROM), and `bad` and `own_i2` read the same own I2 lines, so `"I2" in bad` makes `all(... timed=False)` False and the gate is never entered. The mutant is equivalent, and my S7(b) run passed (below).
One unsourced claim in 03/04: 04 1g (03 step 3, Self-check row 3) says `_defective(repo, "075", ...)` can build the fixture, but `_defective` only supported IDs >= 076. That is the cause of I2's Deviation 1 (judged below). Not a send-back to I1: the plan's intent is clear and the fixture fix is one line.

## I2 audit (build vs plan)
`git diff a5b8edd^ a5b8edd --stat`: tests/test_pipeline_check.py (+168/-10), plus work/109/05 and the I2 log line. scripts/, ccbot/, config/, templates/, .claude/ and tests/test_real_data_field.py are unchanged (also unchanged between 05's base a32037d and a5b8edd: `git diff --stat a32037d a5b8edd -- scripts/ tests/` lists only tests/test_pipeline_check.py).
Line by line against 04:
- 1l `import ast`, `from collections import Counter`: present at the top.
- 1a `_from_sites`: as planned (top-level `tree.body`, owner function name or `<module>`, Names from `ast.walk(compare)`, `_FROM` suffix, UNTRACKED_FROM excluded, counted once per name per Compare, operator not in the key).
- 1b `SITE_ROWS`: 17 rows in S1-S17 order with the planned functions and constants; ids `<CONST>@<check>`; S7 from1_kill is the EQUIVALENT text. Kill choices not fixed by 04 (S2(b), S4(a), S4(b)) are listed as Deviation 3; my S4(b) run confirms its kill is the only failure (below).
- 1c `test_from_site_census`: Counter equality, kill names checked by `ast.parse` of the named file, exactly 1 EQUIVALENT row (S7), `len == 17`.
- 1d `test_from_site_census_catches_new_site`: `_probe` function, module-level `X`, and `y = z != UNTRACKED_FROM`, as planned. Deviation 2 (`_site_want()` helper) is the same assertion.
- 1e `_timed_repo(item, i2)` with defaults; test_timed_gate unchanged and passing.
- 1f `test_rule_gate_cutoff_boundary`: both ids, rules and i2 as planned, exact RULE NOT SEEN and `INCOMPLETE: none`.
- 1g `test_tests_gate_not_entered_below_cutoff`: the four planned asserts (startswith, entry text, 06 no-file note, no `05 anchor`).
- 1h 090 row with the planned ids; strict assert uses `{item}`.
- 1i 045 log line, the new assert and the docstring.
- 1j `test_batch_log_check_cutoff_boundary`: both rows and their asserts as planned.
- 1k FROM_ROWS comment rewritten.
Deviation 1 (`_defective` finds the I2 line through `_field('I2', item)` instead of `FIELDS['I2']`): ACCEPTED, not a send-back. Reasons: (1) the plan cannot be built without it: probe P1 below puts the old line back and `test_tests_gate_not_entered_below_cutoff` fails at `assert old in text` (tests/test_pipeline_check.py:2800) before its body runs; (2) it is in the one planned file and is a test fixture, not checker code; (3) `_field` (L32-34) returns `FIELDS['I2']` for every ID >= 76, and every other caller passes 150, 151 or 153 (`grep -n "_defective(" tests/*.py`: 10 callers), so their fixtures are byte-identical; (4) it does not weaken any assert: the full suite passes with the same 1035 count as 05; (5) 05 names it openly. It is noted for Audit (07 item 2) as a plan feasibility gap.
Connectivity: re-done. `_from_sites`, `_site_want`, `SITE_ROWS`, `_PC`, `_RD`, `ast`, `Counter` and the new `_timed_repo` params each have a reader (grep in the diff). No TODO in the added lines (`git diff -U0 a5b8edd^ a5b8edd -- tests/ | grep '^+' | grep -c TODO` gives 0). No ccbot/ change, so 05's missing-data grep reasons (38 unchanged hits) need no re-justification; the added test lines hold no `else 0` / `: float = 0` default.
Comment check (04 C4), in m3: `grep -c "not against per-site operator mutants"` gives 0; `grep -c "SITE_ROWS / test_from_site_census (item 109)"` gives 1.
Census, independent count: a grep for `_FROM` comparison lines in scripts/check_pipeline.py at a5b8edd (comments and docstrings dropped by eye) gives code lines 845, 848, 858, 861, 1066, 1083, 1089, 1100, 1121, 1131, 1156, 1173, 1188, 1208, 1419, 1541, 2051 (17), plus 1845 (`_note`'s `cutoff != UNTRACKED_FROM`, excluded). Same 17 lines as 05.
Census probes (m3, `-k census`):
- P2: site S9 (L1121) `>= TIMED_FROM` replaced by `>= 90` (a site removed) → `1 failed, 4 passed, 537 deselected in 1.06s`, FAILED `test_from_site_census`.
- P3: kill name `test_tests_gate_not_entered_below_cutoff` misspelled in SITE_ROWS → `1 failed, 4 passed, 537 deselected in 1.08s`, FAILED `test_from_site_census`.
Gap (not a send-back, 04 did not ask for it): the census checks the test function name of each kill, not its `[<param id>]` part, so a misspelled param id passes. Noted in 07.
check_handoff (03 exists), run in m3:
```
sources count (unique URLs in 01-research.md): 3
fact-check rows: 62
totals line: 62 rows -> 52 as-is, 10 fixed, 0 removed
PASS
exit 0
```

## Tests re-run (output)
Full suite in `wt/` at a5b8edd: `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<scratch>/pyc-full python3 -B -m pytest -q -p no:cacheprovider -rs` (exit 0)
```
=========================== short test summary info ============================
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'
1035 passed, 1 skipped in 215.13s (0:03:35)
```
Same count as 05 (1035 passed, 1 skipped). The only skip is exchange_calendars, so none of the 4 git rows was skipped. python3.11 is on PATH (python3.10 is not), so `tests/test_safety.py::test_every_py_compiles_on_oldest_python` ran with 3.11 and passed (it is not in the skip list).

Probe P1 (Deviation 1 reverted in m3), `-k "defective or tests_gate or rule_anchor or 150 or test_tests_gate_not_entered_below_cutoff"`:
```
tests/test_pipeline_check.py:2800: AssertionError
FAILED tests/test_pipeline_check.py::test_tests_gate_not_entered_below_cutoff
1 failed, 8 passed, 533 deselected in 7.22s
```

Mutants: a sample of 12 of the 34, chosen as every site whose kill is new in this item (S7(a), S7(b) equivalent, S8(a), S8(b), S9(a), S9(b), S15(a), S15(b), S16(a), S16(b)), plus S4(b) (Deviation 3's kill choice) and S17(a) (the cross-file C1 kill). Not re-run: S1(a,b), S2(a,b), S3(a,b), S4(a), S5-S6, S10-S14, S17(b) (their kills are existing tests and 05's table shows them). Runner: <scratch>/mut.py, two worktrees (m1, m2), one line rewritten per mutant, each run `python3 -B -m pytest -q -p no:cacheprovider -rfEs tests/test_pipeline_check.py tests/test_real_data_field.py` with PYTHONDONTWRITEBYTECODE=1 and PYTHONPYCACHEPREFIX=<scratch>/pyc-<mutant>, then `git checkout HEAD -- scripts/check_pipeline.py` in that worktree. Raw output: <scratch>/run-<mutant>.txt; none has a `SKIPPED [` line.

| Mutant | Line | Mutated code | Summary line | Failing ids | Kill in ids | Census failed |
|---|---|---|---|---|---|---|
| S4(b) | 861 | `... and int(item) >= TIMED_FROM - 1:` | 1 failed, 580 passed in 123.61s | test_pipeline_check.py::test_timed_hint_fits_timed_format | yes | no |
| S7(a) | 1089 | `if "I2" in bad and int(item_dir.name) > TIMED_FROM \` | 1 failed, 580 passed in 137.91s | test_pipeline_check.py::test_rule_gate_cutoff_boundary[TIMED@incomplete_timed_gate-FROM] | yes | no |
| S7(b) | 1089 | `if "I2" in bad and int(item_dir.name) >= TIMED_FROM - 1 \` | 581 passed in 137.83s | none | n/a (EQUIVALENT, passed) | no |
| S8(a) | 1100 | `elif "I2" in bad and int(item_dir.name) > TESTS_FORMAT_FROM:` | 1 failed, 580 passed in 123.24s | test_pipeline_check.py::test_rule_gate_cutoff_boundary[TESTS_FORMAT@incomplete_tests_gate-FROM] | yes | no |
| S8(b) | 1100 | `elif "I2" in bad and int(item_dir.name) >= TESTS_FORMAT_FROM - 1:` | 1 failed, 580 passed in 123.51s | test_pipeline_check.py::test_tests_gate_not_entered_below_cutoff | yes | no |
| S9(a) | 1121 | `if nc in BATCH_STRICT and int(item_dir.name) > TIMED_FROM:` | 1 failed, 580 passed in 125.69s | test_pipeline_check.py::test_batch_not_computable_strict_from_090[TIMED@batch_strict-FROM] | yes | no |
| S9(b) | 1121 | `if nc in BATCH_STRICT and int(item_dir.name) >= TIMED_FROM - 1:` | 2 failed, 579 passed in 125.40s | test_pipeline_check.py::test_batch_untimed_item_is_not_computable, test_pipeline_check.py::test_batch_not_computable_strict_from_090[TIMED@batch_strict-FROM-1] | yes | no |
| S15(a) | 1419 | `if m and ctime and int(m[4]) > LOG_CHECK_FROM and ...` | 1 failed, 580 passed in 134.36s | test_pipeline_check.py::test_log_line_after_its_commit_is_flagged | yes | no |
| S15(b) | 1419 | `if m and ctime and int(m[4]) >= LOG_CHECK_FROM - 1 and ...` | 2 failed, 579 passed in 134.33s | test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items, test_pipeline_check.py::test_log_line_after_its_commit_is_flagged | yes | no |
| S16(a) | 1541 | `if not d.is_dir() or int(item) <= LOG_CHECK_FROM:` | 1 failed, 580 passed in 141.33s | test_pipeline_check.py::test_batch_log_check_cutoff_boundary[LOG_CHECK@log_batch-FROM] | yes | no |
| S16(b) | 1541 | `if not d.is_dir() or int(item) < LOG_CHECK_FROM - 1:` | 1 failed, 580 passed in 138.95s | test_pipeline_check.py::test_batch_log_check_cutoff_boundary[LOG_CHECK@log_batch-FROM-1] | yes | no |
| S17(a) | 2051 | `if int(item) <= WHOLE_DIFF_FROM:` | 2 failed, 579 passed in 126.11s | test_real_data_field.py::test_t7b_cutoff_edge_item_070_is_checked, test_real_data_field.py::test_t7c_cutoff_edge_pair_in_one_repo | yes | no |

All 12 match 05's rows exactly (same summary counts and the same failing ids). 11 killable mutants fail their SITE_ROWS kill; S7(b) passes as documented. Neither census test failed in any run.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat a5b8edd^ a5b8edd`: tests/test_pipeline_check.py, work/109/05-build-report.md, logs/implementation/2026-11-26.md; no TRIGGER or TRIGGER_DIRS file)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-014 (open/escalated); RI-002, RI-004, RI-005, RI-006, RI-009, RI-010, RI-012 (guarded, checked for a new occurrence)
- RI-001 (ESCALATED): the 17-site count is computed by `_from_sites` in a test, and I re-counted it by grep (17 lines + the excluded L1845). P2 shows a removed site fails the census; the C3 test shows an added one does. The 03/04 feasibility claim that `_defective` can build a 075 fixture was not computed (Deviation 1); not counted as an occurrence (caught at build, fixed in the same item), noted for Audit.
- RI-014 (OPEN): every new git row uses a fresh `git init` in tmp; nothing reads clone depth. No change.
- RI-002: no default added; an unreadable census input raises; `checked == 0` is asserted, not defaulted.
- RI-004/RI-005: S7 equivalence and S8 FROM-1 non-equivalence re-traced in the code, and confirmed by the S7(b)/S8(b) runs.
- RI-006: counts and summary lines here are copied from command output.
- RI-009: all runs in my own worktrees; no stash; main checkout not used for tests.
- RI-010: C4's comment check is non-vacuous (1 before per 05, 0 after); every step of my checklist is in this file.
- RI-012: this item adds no code that classifies text. The new tests assert exact lines or `startswith` plus the full entry text, and 1g has a negative (`"05 anchor" not in inc`).

## Pipeline line (step 2)
check_pipeline line: `109: awaiting A1 (FULL)` (run after this file and the --log line were written; exit 0)

## Sent back / sent to Audit
PASS, round 1. Sent to Audit: work/109/07-audit-task.md.
