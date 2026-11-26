# 05 Build report - 109
Scratch dir: /tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i2-109-r1-p9_rpy9e

Base: a32037d (daily-fixes/2026-11-25, after 108, 110 and 105). Mutant worktrees wt0, wt1, wt2 (`git worktree add --detach` at a32037d, with this build's tests/test_pipeline_check.py copied in) are inside the scratch dir above. Nothing was run in the main checkout except the unmutated full suite. No `git stash` was used.

## Changes made (file: what changed)
- tests/test_pipeline_check.py (the only file):
  - 1l: `import ast` and `from collections import Counter` at the top. Neither was imported before; 108 did not add them.
  - 1a: `_from_sites(source)` builds a Counter of (owner, NAME) over every `ast.Compare` in every top-level statement. Owner is the function name, or `"<module>"` for other statements. Names come from `ast.walk(compare)`, end in `_FROM`, and exclude UNTRACKED_FROM. A helper `_site_want()` returns the SITE_ROWS Counter and is used by both census tests.
  - 1b: `SITE_ROWS` has 17 rows (site id, function, constant, from_kill, from1_kill) in S1-S17 order. Kill strings are `<file>::<test>[<id>]`. S7's from1_kill is the EQUIVALENT text from 04.
  - 1c: `test_from_site_census` checks three things: Counter equality against the real scripts/check_pipeline.py; that each non-EQUIVALENT kill names a top-level FunctionDef in its file (by `ast.parse`, no import); and that there is exactly 1 EQUIVALENT kill (S7 FROM-1), with `len(SITE_ROWS) == 17`.
  - 1d: `test_from_site_census_catches_new_site` covers three cases. An appended `_probe` adds exactly `("_probe", "SUITE_FROM"): 1`. A module-level `X = int("1") >= SUITE_FROM` adds exactly `("<module>", "SUITE_FROM"): 1`. `y = z != UNTRACKED_FROM` adds nothing.
  - 1e: `_timed_repo(..., item="990", i2="1 files changed | tests 1 passed")` passes `i2=(i2,), item=item` to `_suite_item`, and its docstring is updated. test_timed_gate is unchanged and passes.
  - 1f: `@NO_GIT test_rule_gate_cutoff_boundary` has ids `TIMED@incomplete_timed_gate-FROM` (090) and `TESTS_FORMAT@incomplete_tests_gate-FROM` (076, rules without TESTS_FORMAT_FROM, i2 `tests 9/9`). It asserts the exact RULE NOT SEEN line and `INCOMPLETE: none`.
  - 1g: `@NO_GIT test_tests_gate_not_entered_below_cutoff` (075, `tests 10/9`, anchor with no rule file) asserts `startswith("INCOMPLETE: 075 (")`, the I2_BEFORE entry text, the 06 no-file note, and that `"05 anchor"` is absent.
  - 1h: `test_batch_not_computable_strict_from_090` gets the rows 990 / 090 / 089 with ids `990`, `TIMED@batch_strict-FROM` and `TIMED@batch_strict-FROM-1`. Its strict assert now uses `{item}`.
  - 1i: `test_log_line_after_its_commit_is_flagged` gets a 045 I2 line at 23:10 and the assert `"045 I2 (2026-11-04 23:10 after commit 2026-11-04 22:24 UTC)" in line`. Its docstring names `LOG_CHECK@log_time` at FROM (045) and FROM-1 (044).
  - 1j: `test_batch_log_check_cutoff_boundary` has ids `LOG_CHECK@log_batch-FROM` (045: flagged_ids ["045"], checked 1) and `LOG_CHECK@log_batch-FROM-1` (044: flagged_ids [], checked 0, not_computable [], in_progress []).
  - 1k: the FROM_ROWS comment is rewritten. It now says the 7 constants are pinned against shifts here, and that per-site operator and site-local FROM-1 mutants are pinned by `SITE_ROWS / test_from_site_census (item 109)`.
  - Deviation (see below): `_defective` now finds the I2 line through `_field('I2', item)` instead of `FIELDS['I2']`, so the 1g fixture at 075 can be built.

File counts (from commands):
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
0
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
1
```
`git diff --stat HEAD -- ccbot/ scripts/ config/ templates/ .claude/ tests/test_real_data_field.py` is empty, so this is a test-only change, as planned.

## Connectivity check
- [x] Every new function or rule is used. `_from_sites` and `_site_want` are used by both census tests. `SITE_ROWS` is read by test_from_site_census, and `_PC` / `_RD` are read only inside SITE_ROWS. The new `_timed_repo` params are used by test_rule_gate_cutoff_boundary. `Counter` and `ast` are used.
- [x] Every input has a source and every output has a consumer. The census reads scripts/check_pipeline.py and the two test files; a `read_text` or `ast.parse` failure raises, so the test fails and is never skipped. Each new row's result is a pytest pass or fail, pasted below. The mutant results are in the Mutations table.
- [x] Every branch ends in a defined result. The EQUIVALENT kill is the only branch that skips the name lookup, and the test pins it to exactly 1 row. The `evaluated` and `strict` branches each assert an exact result. With no git, the 4 git rows are reported as skipped by `-rs` and never count as a kill. None was skipped here.
- [x] No leftover TODOs or unused files. `git diff -U0 HEAD -- tests/ | grep '^+' | grep -c TODO` gives 0, and no new file was added.
- Missing-data policy grep on ccbot/: 38 hits, all unchanged (`git diff --stat HEAD -- ccbot/` is empty), so there are no new or changed hits to justify. The same grep on the added test lines (with `: float = 0` added) gives 0. `git diff -U0 HEAD -- tests/ | grep '^+' | grep -E " [<>] "` gives no output, so there is no new NaN-prone comparison. No new dataclass.
- Comment check (04 C4): `grep -c "not against per-site operator mutants"` gives 1 at HEAD (`git show HEAD:...`) and 0 after. `grep -c "SITE_ROWS / test_from_site_census (item 109)"` gives 1 after.
- Feasibility (real numbers): the census on scripts/check_pipeline.py at a32037d finds 17 sites. The site locator in the mutant runner prints the 17 code lines 845, 848, 858, 861, 1066, 1083, 1089, 1100, 1121, 1131, 1156, 1173, 1188, 1208, 1419, 1541, 2051. Per function: log_fields_ok 2, log_hint 2, incomplete 10, late_log_lines 1, batch_log_items 1, _item_triggers 1, total 17. That matches the planned count after 105's `_person_dated` (105 added no `*_FROM` comparison; `_note`'s `cutoff != UNTRACKED_FROM` at L1845 is excluded). Each boundary row runs at a computed non-zero ID: 090, 076, 075, 090/089, 045/044, 045/044.

## Test output (pasted, not summarized)
Unmutated full suite, repo root, main checkout:
`PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i2-109-r1-p9_rpy9e/pyc python3 -B -m pytest -q -p no:cacheprovider -rs` (exit 0)
```
=========================== short test summary info ============================
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'
1035 passed, 1 skipped in 205.83s (0:03:25)
```
Suite: 1035 passed, 1 skipped in 205.83s (0:03:25)

The `-rs` report shows only the exchange_calendars skip, so none of the 4 git rows (test_rule_gate_cutoff_boundary x2, test_tests_gate_not_entered_below_cutoff, test_log_line_after_its_commit_is_flagged) was skipped. Count: 105's build had 1027 passed, and this item adds 8 cases (census 2, rule gate 2, tests gate FROM-1 1, batch strict +1, batch LOG_CHECK 2), giving 1035. Added time: not separable from load. This run took 205.83 s against 138.84 s for 105's I2 run, but other agents' runs (I3 105) shared the 4 CPUs at the same time. The unmutated two-file run in wt0, made just before the mutants, is below.

Unmutated two-file baseline in wt0: `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i2-109-r1-p9_rpy9e/pyc-base python3 -B -m pytest -q -p no:cacheprovider -rs tests/test_pipeline_check.py tests/test_real_data_field.py`
```
581 passed in 125.83s (0:02:05)
```

Pre-check during the build (not the result): an initial `-k` run of the new and changed tests failed in `_defective` (`assert old in text`: at 075 `_item` writes `tests 1/1`), which led to the deviation below. After the fix the same `-k` run gave `21 passed, 521 deselected in 4.11s`.

## Mutations (04 Tests: 34 site mutants)
Runner: /tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i2-109-r1-p9_rpy9e/mutants.py, using 3 parallel worktrees (wt0-wt2). For each mutant it rewrites the one site line in scripts/check_pipeline.py and runs `python3 -B -m pytest -q -p no:cacheprovider -rs tests/test_pipeline_check.py tests/test_real_data_field.py` with `PYTHONDONTWRITEBYTECODE=1` and a fresh `PYTHONPYCACHEPREFIX=/tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i2-109-r1-p9_rpy9e/pyc-<wt>-<mutant>`. It then restores the file with `git checkout HEAD -- scripts/check_pipeline.py` in that worktree. (a) is the FROM-side operator flip (`>=`->`>`, `<`->`<=`); (b) is the site-local FROM-1 (`NAME - 1`). Failing ids come from each run's failure headers, and their count is checked against the summary line's `N failed`. Raw output: /tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i2-109-r1-p9_rpy9e/runs/<mutant>.txt. No run has a column-0 `SKIPPED [` line.

| Mutant | Line | Mutated code | Summary line | Failing ids | SITE_ROWS kill in failing ids | Census test failed |
|---|---|---|---|---|---|---|
| S1(a) | 845 | `if agent == "I2" and (int(item) <= TESTS_FORMAT_FROM or not new_rule):` | `3 failed, 578 passed in 134.02s (0:02:14)` | `test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items`<br>`test_pipeline_check.py::test_i2_tests_field_cutoff`<br>`test_pipeline_check.py::test_rule_gate_cutoff_boundary[TESTS_FORMAT@incomplete_tests_gate-FROM]` | yes | no |
| S1(b) | 845 | `if agent == "I2" and (int(item) < TESTS_FORMAT_FROM - 1 or not new_rule):` | `3 failed, 578 passed in 133.97s (0:02:13)` | `test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items`<br>`test_pipeline_check.py::test_i2_tests_field_cutoff`<br>`test_pipeline_check.py::test_old_i2_hint_fits_old_format` | yes | no |
| S2(a) | 848 | `if agent == "I2" and timed and int(item) > TIMED_FROM:` | `2 failed, 579 passed in 134.03s (0:02:14)` | `test_pipeline_check.py::test_rule_gate_cutoff_boundary[TIMED@incomplete_timed_gate-FROM]`<br>`test_pipeline_check.py::test_from_cutoff_boundary[TIMED-FROM]` | yes | no |
| S2(b) | 848 | `if agent == "I2" and timed and int(item) >= TIMED_FROM - 1:` | `6 failed, 575 passed in 131.42s (0:02:11)` | `test_pipeline_check.py::test_i2_summary_line_accepted[411 passed, 1 skipped]`<br>`test_pipeline_check.py::test_i2_summary_line_accepted[255 passed, 1 skipped (round 2: test case added)]`<br>`test_pipeline_check.py::test_i2_summary_line_accepted[1 passed]`<br>`test_pipeline_check.py::test_batch_untimed_item_is_not_computable`<br>`test_pipeline_check.py::test_log_i2_untimed_refused_from_090`<br>`test_pipeline_check.py::test_from_cutoff_boundary[TIMED-FROM-1]` | yes | no |
| S3(a) | 858 | `if agent in LOG_HINT_BEFORE and re.fullmatch(r"\d{3}", item) and (int(item) <= TESTS_FORMAT_FROM` | `2 failed, 579 passed in 133.77s (0:02:13)` | `test_pipeline_check.py::test_i2_tests_field_cutoff`<br>`test_pipeline_check.py::test_old_i2_hint_fits_old_format` | yes | no |
| S3(b) | 858 | `if agent in LOG_HINT_BEFORE and re.fullmatch(r"\d{3}", item) and (int(item) < TESTS_FORMAT_FROM - 1` | `3 failed, 578 passed in 131.24s (0:02:11)` | `test_pipeline_check.py::test_i2_tests_field_cutoff`<br>`test_pipeline_check.py::test_old_i2_hint_fits_old_format`<br>`test_pipeline_check.py::test_tests_gate_not_entered_below_cutoff` | yes | no |
| S4(a) | 861 | `if agent in LOG_HINT_TIMED and timed and re.fullmatch(r"\d{3}", item) and int(item) > TIMED_FROM:` | `2 failed, 579 passed in 137.98s (0:02:17)` | `test_pipeline_check.py::test_timed_hint_fits_timed_format`<br>`test_pipeline_check.py::test_from_cutoff_boundary[TIMED-FROM]` | yes | no |
| S4(b) | 861 | `if agent in LOG_HINT_TIMED and timed and re.fullmatch(r"\d{3}", item) and int(item) >= TIMED_FROM - 1:` | `1 failed, 580 passed in 137.93s (0:02:17)` | `test_pipeline_check.py::test_timed_hint_fits_timed_format` | yes | no |
| S5(a) | 1066 | `if not item_dir.name.isdigit() or int(item_dir.name) <= CHECKLIST_FROM:` | `1 failed, 580 passed in 139.33s (0:02:19)` | `test_pipeline_check.py::test_from_cutoff_boundary[CHECKLIST-FROM]` | yes | no |
| S5(b) | 1066 | `if not item_dir.name.isdigit() or int(item_dir.name) < CHECKLIST_FROM - 1:` | `6 failed, 575 passed in 138.63s (0:02:18)` | `test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items`<br>`test_pipeline_check.py::test_incomplete_06_and_missing_log_line`<br>`test_pipeline_check.py::test_uncommitted_step_without_logs_folder_is_listed`<br>`test_pipeline_check.py::test_06_verdict_disagrees_with_last_i3_log`<br>`test_pipeline_check.py::test_unreadable_log_consumers_say_not_checked`<br>`test_pipeline_check.py::test_from_cutoff_boundary[CHECKLIST-FROM-1]` | yes | no |
| S6(a) | 1083 | `if int(item_dir.name) > LOG_CHECK_FROM and not log_whys:` | `1 failed, 580 passed in 138.62s (0:02:18)` | `test_pipeline_check.py::test_from_cutoff_boundary[LOG_CHECK-FROM]` | yes | no |
| S6(b) | 1083 | `if int(item_dir.name) >= LOG_CHECK_FROM - 1 and not log_whys:` | `3 failed, 578 passed in 143.52s (0:02:23)` | `test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items`<br>`test_pipeline_check.py::test_malformed_log_line_is_incomplete`<br>`test_pipeline_check.py::test_from_cutoff_boundary[LOG_CHECK-FROM-1]` | yes | no |
| S7(a) | 1089 | `if "I2" in bad and int(item_dir.name) > TIMED_FROM \` | `1 failed, 580 passed in 134.91s (0:02:14)` | `test_pipeline_check.py::test_rule_gate_cutoff_boundary[TIMED@incomplete_timed_gate-FROM]` | yes | no |
| S7(b) | 1089 | `if "I2" in bad and int(item_dir.name) >= TIMED_FROM - 1 \` | `581 passed in 134.89s (0:02:14)` | none | n/a: EQUIVALENT row, run passed | no |
| S8(a) | 1100 | `elif "I2" in bad and int(item_dir.name) > TESTS_FORMAT_FROM:` | `1 failed, 580 passed in 141.87s (0:02:21)` | `test_pipeline_check.py::test_rule_gate_cutoff_boundary[TESTS_FORMAT@incomplete_tests_gate-FROM]` | yes | no |
| S8(b) | 1100 | `elif "I2" in bad and int(item_dir.name) >= TESTS_FORMAT_FROM - 1:` | `1 failed, 580 passed in 136.18s (0:02:16)` | `test_pipeline_check.py::test_tests_gate_not_entered_below_cutoff` | yes | no |
| S9(a) | 1121 | `if nc in BATCH_STRICT and int(item_dir.name) > TIMED_FROM:` | `1 failed, 580 passed in 136.14s (0:02:16)` | `test_pipeline_check.py::test_batch_not_computable_strict_from_090[TIMED@batch_strict-FROM]` | yes | no |
| S9(b) | 1121 | `if nc in BATCH_STRICT and int(item_dir.name) >= TIMED_FROM - 1:` | `2 failed, 579 passed in 140.34s (0:02:20)` | `test_pipeline_check.py::test_batch_untimed_item_is_not_computable`<br>`test_pipeline_check.py::test_batch_not_computable_strict_from_090[TIMED@batch_strict-FROM-1]` | yes | no |
| S10(a) | 1131 | `if int(item_dir.name) > SUITE_FROM and report.exists() and not log_whys:` | `4 failed, 577 passed in 138.31s (0:02:18)` | `test_pipeline_check.py::test_suite_line_dropped_middle_is_incomplete`<br>`test_pipeline_check.py::test_suite_line_part_of_field_is_incomplete[S3-tail]`<br>`test_pipeline_check.py::test_suite_line_part_of_field_is_incomplete[S4-note]`<br>`test_pipeline_check.py::test_from_cutoff_boundary[SUITE-FROM]` | yes | no |
| S10(b) | 1131 | `if int(item_dir.name) >= SUITE_FROM - 1 and report.exists() and not log_whys:` | `3 failed, 578 passed in 138.31s (0:02:18)` | `test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items`<br>`test_pipeline_check.py::test_suite_below_cutoff_not_checked`<br>`test_pipeline_check.py::test_from_cutoff_boundary[SUITE-FROM-1]` | yes | no |
| S11(a) | 1156 | `if int(item_dir.name) > ROUND_HEADING_FROM:` | `1 failed, 580 passed in 140.35s (0:02:20)` | `test_pipeline_check.py::test_stray_round_heading_is_incomplete[P1-at-cutoff-092]` | yes | no |
| S11(b) | 1156 | `if int(item_dir.name) >= ROUND_HEADING_FROM - 1:` | `1 failed, 580 passed in 132.83s (0:02:12)` | `test_pipeline_check.py::test_read_or_unnamed_heading_is_not_stray[N3-below-cutoff]` | yes | no |
| S12(a) | 1173 | `if int(item_dir.name) > ROUND_BUILD_FROM:` | `1 failed, 580 passed in 135.76s (0:02:15)` | `test_pipeline_check.py::test_round_build_heading_is_incomplete[099-at-cutoff]` | yes | no |
| S12(b) | 1173 | `if int(item_dir.name) >= ROUND_BUILD_FROM - 1:` | `1 failed, 580 passed in 138.69s (0:02:18)` | `test_pipeline_check.py::test_round_build_heading_is_incomplete[098-below-cutoff]` | yes | no |
| S13(a) | 1188 | `if int(item_dir.name) > SCRATCH_FROM:` | `1 failed, 580 passed in 129.10s (0:02:09)` | `test_pipeline_check.py::test_scratch_dir_cutoff_boundary[FROM]` | yes | no |
| S13(b) | 1188 | `if int(item_dir.name) >= SCRATCH_FROM - 1:` | `2 failed, 579 passed in 126.48s (0:02:06)` | `test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items`<br>`test_pipeline_check.py::test_scratch_dir_cutoff_boundary[FROM-1]` | yes | no |
| S14(a) | 1208 | `if int(item_dir.name) > VERDICT_FROM:` | `1 failed, 580 passed in 129.65s (0:02:09)` | `test_pipeline_check.py::test_from_cutoff_boundary[VERDICT-FROM]` | yes | no |
| S14(b) | 1208 | `if int(item_dir.name) >= VERDICT_FROM - 1:` | `2 failed, 579 passed in 136.01s (0:02:16)` | `test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items`<br>`test_pipeline_check.py::test_from_cutoff_boundary[VERDICT-FROM-1]` | yes | no |
| S15(a) | 1419 | `if m and ctime and int(m[4]) > LOG_CHECK_FROM and m[4] not in LOG_TIME_EXCEPT:` | `1 failed, 580 passed in 135.71s (0:02:15)` | `test_pipeline_check.py::test_log_line_after_its_commit_is_flagged` | yes | no |
| S15(b) | 1419 | `if m and ctime and int(m[4]) >= LOG_CHECK_FROM - 1 and m[4] not in LOG_TIME_EXCEPT:` | `2 failed, 579 passed in 134.55s (0:02:14)` | `test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items`<br>`test_pipeline_check.py::test_log_line_after_its_commit_is_flagged` | yes | no |
| S16(a) | 1541 | `if not d.is_dir() or int(item) <= LOG_CHECK_FROM:` | `1 failed, 580 passed in 154.96s (0:02:34)` | `test_pipeline_check.py::test_batch_log_check_cutoff_boundary[LOG_CHECK@log_batch-FROM]` | yes | no |
| S16(b) | 1541 | `if not d.is_dir() or int(item) < LOG_CHECK_FROM - 1:` | `1 failed, 580 passed in 149.94s (0:02:29)` | `test_pipeline_check.py::test_batch_log_check_cutoff_boundary[LOG_CHECK@log_batch-FROM-1]` | yes | no |
| S17(a) | 2051 | `if int(item) <= WHOLE_DIFF_FROM:` | `2 failed, 579 passed in 154.69s (0:02:34)` | `test_real_data_field.py::test_t7b_cutoff_edge_item_070_is_checked`<br>`test_real_data_field.py::test_t7c_cutoff_edge_pair_in_one_repo` | yes | no |
| S17(b) | 2051 | `if int(item) < WHOLE_DIFF_FROM - 1:` | `2 failed, 579 passed in 125.42s (0:02:05)` | `test_real_data_field.py::test_t7_items_before_cutoff_are_not_checked`<br>`test_real_data_field.py::test_t7c_cutoff_edge_pair_in_one_repo` | yes | no |

Result: 33 of 34 mutants fail their SITE_ROWS kill. S7(b) passes (581 passed), as expected for the documented EQUIVALENT row. Neither census test fails under any mutant. The table check script reported `mismatches: 0`. `test_repo_pipeline_has_no_skipped_items` also fails under several mutants: it runs the mutated checker on this repo's own work/ items. That is an extra kill and is not used as any row's kill.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat HEAD`: tests/test_pipeline_check.py only; no TRIGGER or TRIGGER_DIRS file)

## Deviations from plan
1. `_defective` (an existing helper, not named in 04): `old = f"12:00 | I2 | {item} | {FIELDS['I2']}\n"` became `{_field('I2', item)}`. 04 1g (and 03 step 3 / Self-check row 3) call `_defective(repo, "075", ...)`, but below 076 `_item` writes `I2_BEFORE_FIELD` (`tests 1/1`), so `assert old in text` failed before the test body ran. `_field` returns `FIELDS['I2']` for every ID >= 076, and every other caller uses 150, 151 or 153 (`grep -n "_defective(" tests/*.py`), so they are unchanged (the full suite passes). I made this one-line fixture fix instead of sending the plan back, because it is the only way to build 1g as written and it changes no other behavior. I3/I1 may reject it.
2. 04 1d writes the census comparison as `_from_sites(src) - want`. `want` comes from a helper `_site_want()` so that the two census tests share one definition. Same assertion.
3. Kill choices not fixed by 04, taken from 03's fact-check rows and confirmed by the table above. S2(b) uses `test_from_cutoff_boundary[TIMED-FROM-1]`. S4(a) uses `[TIMED-FROM]`. S4(b) uses `test_timed_hint_fits_timed_format` (03 L4475/4476): S4(b)'s only failure is that test, so `[TIMED-FROM-1]` would not have been a kill. S1 and S3 use the same test for both sides, as 03 says.

## Recurring issues checked (item 013)
logs/recurring-issues.md read first. Open or ESCALATED entries: RI-001, RI-014. GUARDED entries also checked: RI-002, RI-004, RI-005, RI-006, RI-007, RI-009, RI-010, RI-012.
RI-001: ESCALATED, unchanged. The 17-site count is measured by `_from_sites` in a test, not asserted by hand, and test_from_site_census_catches_new_site pins that an 18th site (function or module level) is caught.
RI-014: OPEN, unchanged. Every new git row uses a fresh `git init` in tmp. No clone-depth-dependent path was added, and no git call was added to scripts/.
RI-002: GUARDED, holds. An unreadable census input raises and the test fails. A git-less skip is shown by `-rs` and is never a kill. `checked == 0` is asserted, never defaulted.
RI-006: GUARDED, holds. File counts and the Suite line are copied from command output, and the mutant table is generated from the run files.
RI-009: GUARDED, holds. Mutants ran only in scratch worktrees inside this item's own scratch dir. Sites are found by name and code pattern, not by 03's old line numbers. No stash was used.
RI-010: GUARDED, holds. The C4 comment check is non-vacuous (1 before, 0 after).
RI-012: GUARDED, holds. Exact-line asserts are used, plus `startswith` and the full entry text in 1g.
check_pipeline.py before writing 05: exit 0. 106, 107 and 109 show as in progress, which is expected.
