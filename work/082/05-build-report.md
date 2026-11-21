# 05 Build report - 082
## Changes made (file: what changed)
Plan: work/082/04-build-plan.md (FIT WITH CHANGES, 9 files planned). Built on daily-fixes/2026-11-20 at HEAD 1b42ee3 (base when I started: 91ade51; 425cd4a, 7eb51b0 and 1b42ee3 were committed by other agents during the build and touch only work/ and logs/). I re-read the built code of 081 (`_git_ok`, the call-site census `GIT_CALLS` in tests), 084 (`_rule_seen`, `_anchor_env`, `incomplete(item_dir, logs, env=None, not_seen=None)`, the TESTS and VERDICT gates, the RULE NOT SEEN print) and 086 (`_item_lines`, `_run_seconds`, `batch_log_items`, `write_log` rule D) before editing; none of their code was changed.

1. `scripts/check_pipeline.py` (RULE_PATHS):
   - `SUITE_FROM = 87` next to `TESTS_FORMAT_FROM`, with the plan's comment. 084's `_rule_seen` exists, so the "judged strictly" gap sentence was not needed.
   - New `_last_log_line(logs, agent, item)` and `_suite_lines(text)` (exact forms from the plan).
   - `incomplete()`: a new block after the log-format block (after 084's TESTS gate and its note), before the 071 verdict block. It runs when `int(ID) >= SUITE_FROM` and 05 exists, and uses the item's last I2 line. If that line is None or fails `log_fields_ok`, no entry. Otherwise one of three reasons: no Suite line / `<n> 'Suite:' lines, needs exactly 1` / mismatch with both values quoted. The probe anchor `            elif suites[0] != field:` is one line.
   - The 084 gate is one call, only when a reason fires: `_rule_seen(item_dir, "05", "SUITE_FROM", env)`. False → `not_seen.append((ID, "05", sha7, "SUITE_FROM", "082", "no Suite check"))`. True or None → the reason, plus any non-empty note as its own entry (the same shape as the VERDICT gate).
   - Module docstring: one paragraph after the item-076 `--log` paragraph. The `incomplete()` docstring gains one sentence. `log_fields_ok`, `log_hint`, `write_log`, `_logged`, `_md_lines`, `SHALLOW_LINE`, `FENCE_OPEN` and all 081/084/086 code are unchanged.
2. `tests/test_pipeline_check.py`:
   - `_item` writes 05 as `x` plus a `Suite:` line equal to the tests part of `_field('I2', item)`.
   - The 5 direct 05 rewrites for IDs >= 87 keep a `Suite: 1 passed` line: 150 ×3, 153 ×2.
   - `_batch_item(full=True)` writes a `Suite:` line too (see Deviations 3).
   - New tests: S0-S12 (S2 is the standalone `test_suite_line_dropped_middle_is_incomplete`; S3/S4 are one parametrized function; S11/S12 one function), S13/S13b (parametrized), `test_suite_label_in_template_and_i2_text`, `test_unshallow_sentence_same_in_three_files`, `test_run_item_commit_subject_rule`.
   - Added to existing tests: the `longer-close` T4 case, the `XR1` line in P5a2, and the 2 `.git/shallow` cases.
3. `tests/test_real_data_field.py`: `_rd_item` writes `# 05\nSuite: 1 passed\n{body05}`, and the `work/162/05-build-report.md` write keeps a Suite line. No assertion changed.
4. `scripts/probe_guardrails.py`:
   - `RECORDED` regex.
   - `_recorded_marker(p, results)` with the change-4 order, and the marker appended in `_probe_all`.
   - The comment now reads "printed and compared on its failed count only (item 082: information, never a verdict)".
   - New last PROBES entry `RI-006-082-suite`, with `recorded` `2026-11-21 (082/05): 5 failed, 299 passed` copied from probe run 1.
   - No old entry printed `(live differs)` in run 1, so no old `recorded` was refreshed.
5. `tests/test_probe_guardrails.py`:
   - `test_shipped_probes_well_formed`: 9 → 10 in both asserts, the `RECORDED.fullmatch` assert, and the new target in the list.
   - `test_holds_exits_0` asserts `(recorded unreadable)`.
   - `test_mixed_run_reports_every_probe` asserts that "b" has none of the three markers.
   - New tests X, Y, W and `test_a1_text_marks_probe_markers_as_information`.
6. `templates/build-report.md` (RULE_PATHS): the column-0 `Suite: <...>` line directly under `## Test output (pasted, not summarized)`.
7. `.claude/agents/i2-builder.md` (RULE_PATHS): the plan's sentence, after "never retyped, summed or shortened.".
8. `.claude/agents/a1-auditor.md` (RULE_PATHS):
   - Job B: run-item.md's two unshallow sentences, byte-for-byte, after "after `git fetch origin`.".
   - Guardrails paragraph: the marker clause.
9. `.claude/commands/run-item.md` (RULE_PATHS): the step-(5) subject sentence and the I2 sentence. The unshallow sentences are unchanged (pinned three times by the new test).

File counts (commands, run before writing this file):
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
0
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
9
```
`git diff --stat`: `9 files changed, 329 insertions(+), 24 deletions(-)` (before the `recorded` fill; the fill changed one line in place).

Files the person should review in the PR (RULE_PATHS): scripts/check_pipeline.py, templates/build-report.md, .claude/agents/i2-builder.md, .claude/agents/a1-auditor.md, .claude/commands/run-item.md. The probe is part of this item, as 03 decided (02 AGAINST 3(a)).

## Connectivity check
- [x] Every new function or rule is used.
  - `_last_log_line` and `_suite_lines` are called only by the new block in `incomplete()`.
  - `SUITE_FROM` is read by that block and by 084's `_rule_seen` text search (S13/S13b).
  - `RECORDED` is used by `_recorded_marker` and by `test_shipped_probes_well_formed`.
  - `_recorded_marker` is called in `_probe_all`.
  - The new PROBES entry runs in probe_guardrails (run 2: HOLDS).
- [x] Every input has a source and every output has a consumer.
  - Inputs: the 05 text (work/<ID>/05) and the last I2 log line (logs/implementation).
  - Outputs: the INCOMPLETE entry (exit 1), or a RULE NOT SEEN pair (information, printed by 084's existing loop).
  - The probe marker goes to the probe line, which A1 reads (the a1-auditor clause says it is information).
- [x] Every branch ends in a defined result.
  - No I2 line → 043's `no log line for I2` (S8).
  - Malformed last line → 045's entry, no fallback (S9).
  - Below SUITE_FROM → no entry (S10).
  - Zero, two or a mismatch → named reasons (S0/S5, S6, S2-S4/S7/S12).
  - Gate False → RULE NOT SEEN (S13). Gate None with a note → reason plus note. Gate None without a note → reason (strict; no-git fixtures S0-S12).
  - Marker: absent → none. Unparsable → `(recorded unreadable)`. No results → `(live n/a)`. Differs → `(live differs)`. Else nothing (X/Y/W, test_holds_exits_0, mixed "b").
- [x] No leftover TODOs or unused files. The `RECORDED_TBD` placeholder used before probe run 1 was replaced: grep `RECORDED_TBD` finds 0 hits in the repo. No new files.
- Missing-data policy:
  - The ccbot grep finds 38 hits, all pre-existing. `git diff --stat -- ccbot/ config/` is empty, so 082 adds or changes no hit.
  - The two patterns the grep can't see (014): no dataclass was added. The only new comparisons are on ints (`len(suites) > 1`, `int(ID) >= SUITE_FROM`, the failed count `!=`), which cannot be NaN.
  - An absent `recorded` gives no marker and an unparsable one gives `(recorded unreadable)`. Neither is ever read as 0.

```
$ grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/ | wc -l
38
$ git diff --stat -- ccbot/ config/
(empty)
```

Recurring issues checked (item 013), every open or ESCALATED entry plus the related GUARDED ones the plan names:
- RI-001 (ESCALATED): one selecting rule (Suite). In-scope count today: 0 of 82 05 files (`ls work/*/05-build-report.md | wc -l` → 82; none has ID >= 87). That empty set is pinned by the repo self-test staying green and by check_pipeline showing no Suite entry. The two new shallow lines: 0 of 2 `fullmatch`, 2 of 2 `.match` (run below). RECORDED: 10 of 10 shipped values fullmatch (the 9 old ones plus the new one).
- RI-010 (ESCALATED): two text duties became checks (the Suite compare; `recorded` format assert plus marker). Points 4b and 5 are text pins only, which is a partial guard: no check reads commit text (062, RI-012).
- RI-014 (OPEN): the unshallow sentence is in a1-auditor.md job B and pinned byte-for-byte in 3 files. The 2 new `.git/shallow` cases keep "unreadable". 082 adds no `_git`/`_git_ok` call, so 081's call-site census is unchanged (its test passes).
- RI-002: each absent input has a named result and a test (S0, S5, S6, S8, S9, S13, W, mixed "b", the format assert).
- RI-004/RI-005: every fixture was checked against the mutant it must kill (all 26 non-equivalent mutants fail their target; see Test output). One plan mutant is equivalent: see Deviations 2.
- RI-006: the Suite line, `recorded` and every count were copied from command output.
- RI-007: Scope FULL, nothing skipped.
- RI-009: mutations and probes ran in scratch clones outside the repo. The repo tree was never mutated.
- RI-012: whole-string `!=`, `RECORDED.fullmatch`, no reader of commit text.

Feasibility numbers (real):
```
$ python3 -c "...pg.RECORDED.fullmatch over PROBES..."
10 of 10 shipped recorded values fullmatch RECORDED
$ python3 - (SHALLOW_LINE on c+'x' and 'a'*41)
'aax' fullmatch False match True
'aaa' fullmatch False match True
$ ls work/*/05-build-report.md | wc -l
82
```

RI-006: guardrail built (082); the Suite compare is probed by RI-006-082-suite (HOLDS, run 2).
RI-010: 082 turns two text duties into checks (Suite, recorded); 4b and 5 are text pins.
RI-014: unshallow sentence pinned in three files (082).

## Test output (pasted, not summarized)
Suite: 1 failed, 672 passed, 1 skipped in 88.54s (0:01:28)
(Round 2 line. Round 1's line was `672 passed, 1 skipped in 90.14s (0:01:30)`. See Round 2 below for the one failure.)

The line above is the last line of the final full run below, copied as printed. 082 < SUITE_FROM, so this is voluntary; it shows the rule in use.

Step 0 (read-only, before any edit, at HEAD 91ade51):
```
$ python3 scripts/check_pipeline.py --next-id
087
exit 0
$ git log -1 --format=%s e813e1f
Item 076: I2 build round 2 - refuse cases R15/R16 pin part order
$ git rev-parse --is-shallow-repository
false
$ python3 -m pytest -q | tail -3
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 649 passed, 1 skipped in 88.31s (0:01:28)
```
SUITE_FROM = max(87, 087) = 87. Gate branch: `_rule_seen(item_dir, step, const, env)`, `incomplete(item_dir, logs=Path("logs"), env=None, not_seen=None)` and the `RULE NOT SEEN:` print all exist (grep, lines 625, 657, 1568 of the base file), so the one-call gate was built and S13 is included. The baseline failure was the known 081/086-open one. It passes at the final HEAD 1b42ee3, after 081/086 got their 06/07 and 081 its A1 line.

After the fixture-helper change alone (change 1, before the check), the suite was green apart from the known failure:
```
$ python3 -m pytest -q | tail -3
tests/test_pipeline_check.py:181: AssertionError
=========================== short test summary info ============================
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 649 passed, 1 skipped in 84.79s (0:01:24)
```
With the check and the new tests, 2 pre-existing 086 tests failed only because `_batch_item(full=True)` wrote a 05 with no Suite line (`INCOMPLETE: 999 (05 has no 'Suite:' line (item 082))`). Their fixture text got the line (Deviations 3). The other 2 failures in that run were the known repo test and the `RECORDED_TBD` placeholder before probe run 1:
```
$ python3 -m pytest -q | tail -4
FAILED tests/test_pipeline_check.py::test_batch_083_shape_is_flagged - Assert...
FAILED tests/test_pipeline_check.py::test_batch_untimed_item_is_not_computable
FAILED tests/test_probe_guardrails.py::test_shipped_probes_well_formed - Asse...
4 failed, 668 passed, 1 skipped in 91.49s (0:01:31)
```
Final full suite (repo root, HEAD 1b42ee3 plus these 9 files, `recorded` filled):
```
$ python3 -m pytest -q | tail -3
........................................................................ [ 96%]
.........................                                                [100%]
672 passed, 1 skipped in 90.14s (0:01:30)
```
That is 22 new test cases (673 - 651).

py_compile (RI-008):
```
$ python3.11 -m py_compile scripts/check_pipeline.py scripts/probe_guardrails.py && echo "py311 compile ok"
py311 compile ok
```

probe_guardrails. I may not commit in the repo, so both runs used `--repo <scratch clone>` (/tmp/claude-0/-home-claude/8f94cbd2-523d-52d1-8971-85df3e672dc0/scratchpad/i2-082-probe, cloned from the repo). Its single scratch commit on top of 7eb51b0 holds these 9 files, a placeholder work/082/05 and a scratch-only I2 line (written by `--log` in the clone), so its tests/test_pipeline_check.py baseline is green: an uncovered code commit would be UNTRACKED CHANGE and turn every check_pipeline probe into ERROR. Run 1 (scratch commit 0e8d533, `recorded` still the placeholder):
```
$ python3 scripts/probe_guardrails.py --ref HEAD --repo <scratch>
ref HEAD = 0e8d5334dbe5dd07f5ef1b38322d8c02a8d9c06a
baseline tests/test_realtest.py: 0 failed, 50 passed, 0 errors, 0 skipped; 23.9 s
RI-002-063-leading-edge (RI-002): 9 failed, 41 passed, 0 errors, 0 skipped; target tests/test_realtest.py::test_leading_edge_100_days_blocks failed: yes; HOLDS; recorded 2026-11-18: 9 failed, 41 passed; code check: ccbot.realtest is ccbot/realtest.py in the worktree; 73.5 s
    FAILED tests.test_realtest::test_drop_input[earnings]
    FAILED tests.test_realtest::test_drop_input[earnings_before_first]
    FAILED tests.test_realtest::test_empty_earnings_file_warns_and_lead_is_null
    FAILED tests.test_realtest::test_leading_edge_100_days_blocks
    FAILED tests.test_realtest::test_leading_edge_151_days_blocks
    FAILED tests.test_realtest::test_real_counts_bac[d0.150_dte14-24_noE_hold_bid]
    FAILED tests.test_realtest::test_real_counts_bac[d0.275_dte30-45_noE_hold_bid]
    FAILED tests.test_realtest::test_real_counts_bac[d0.450_dte30-45_noE_hold_bid]
    FAILED tests.test_realtest::test_stock_without_earnings_sells_nothing
RI-002-065-interior-gap (RI-002): 4 failed, 46 passed, 0 errors, 0 skipped; target tests/test_realtest.py::test_interior_gap_180_blocks failed: yes; HOLDS; recorded 2026-11-18: 4 failed, 46 passed; code check: ccbot.realtest is ccbot/realtest.py in the worktree; 24.4 s
    FAILED tests.test_realtest::test_drop_input[earnings_interior_gap]
    FAILED tests.test_realtest::test_interior_gap_121_blocks
    FAILED tests.test_realtest::test_interior_gap_180_blocks
    FAILED tests.test_realtest::test_real_interior_gap_mo
baseline tests/test_diff_reports.py: 0 failed, 17 passed, 0 errors, 0 skipped; 1.0 s
RI-013-067-1b (RI-013): 1 failed, 16 passed, 0 errors, 0 skipped; target tests/test_diff_reports.py::test_a_nested_key_and_list_in_dict failed: yes; HOLDS; recorded 2026-11-18: 1 failed, 16 passed; code check: n/a (tests/test_diff_reports.py runs scripts/diff_reports.py as REPO/scripts/diff_reports.py (SCRIPT), REPO from tests/conftest.py); 3.2 s
    FAILED tests.test_diff_reports::test_a_nested_key_and_list_in_dict
baseline tests/test_missing_inputs.py: 0 failed, 23 passed, 0 errors, 0 skipped; 1.2 s
RI-002-046-tickers-key (RI-002): 1 failed, 22 passed, 0 errors, 0 skipped; target tests/test_missing_inputs.py::test_ticker_fields_cover_file_and_code failed: yes; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 22 passed; code check: n/a (config/tickers.json is data: tests/test_missing_inputs.py test_ticker_fields_cover_file_and_code reads tickers.json from Path(__file__).resolve().parents[1]); 2.6 s
    FAILED tests.test_missing_inputs::test_ticker_fields_cover_file_and_code
baseline tests/test_pipeline_check.py: 0 failed, 304 passed, 0 errors, 0 skipped; 38.0 s
RI-007-064-work-py (RI-007): 8 failed, 296 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_research_only_work_py_is_research_code failed: yes; HOLDS; recorded 2026-11-20 (078/05): 8 failed, 82 passed; code check: n/a (tests/test_pipeline_check.py runs scripts/check_pipeline.py as REPO/scripts/check_pipeline.py (_run) and imports check_pipeline after sys.path.insert(0, REPO/scripts) (_cp), REPO from tests/conftest.py); 74.8 s
    FAILED tests.test_pipeline_check::test_is_code_examples
    FAILED tests.test_pipeline_check::test_py_added_to_completed_item_is_untracked
    FAILED tests.test_pipeline_check::test_research_code_rules
    FAILED tests.test_pipeline_check::test_research_only_branch_nested_py_is_seen
    FAILED tests.test_pipeline_check::test_research_only_branch_work_py_is_branch_skipped
    FAILED tests.test_pipeline_check::test_research_only_work_py_is_research_code
    FAILED tests.test_pipeline_check::test_work_code_pattern[work/061/diag_keep.py-True]
    FAILED tests.test_pipeline_check::test_work_code_pattern[work/160/sub/x.py-True]
RI-009-037-clash-line (RI-009): 1 failed, 303 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_same_id_on_main_and_open_branch_is_a_clash failed: yes; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 89 passed; code check: n/a (tests/test_pipeline_check.py runs scripts/check_pipeline.py as REPO/scripts/check_pipeline.py (_run) and imports check_pipeline after sys.path.insert(0, REPO/scripts) (_cp), REPO from tests/conftest.py); 34.8 s
    FAILED tests.test_pipeline_check::test_same_id_on_main_and_open_branch_is_a_clash
RI-010-049-rules-line (RI-010): 1 failed, 303 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_rules_branch_is_reported failed: yes; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 89 passed; code check: n/a (tests/test_pipeline_check.py runs scripts/check_pipeline.py as REPO/scripts/check_pipeline.py (_run) and imports check_pipeline after sys.path.insert(0, REPO/scripts) (_cp), REPO from tests/conftest.py); 36.7 s
    FAILED tests.test_pipeline_check::test_rules_branch_is_reported
RI-011-052-merge-tree (RI-011): 1 failed, 303 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_criss_cross_branch_lists_only_its_own_changes failed: yes; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 89 passed; code check: n/a (tests/test_pipeline_check.py runs scripts/check_pipeline.py as REPO/scripts/check_pipeline.py (_run) and imports check_pipeline after sys.path.insert(0, REPO/scripts) (_cp), REPO from tests/conftest.py); 35.7 s
    FAILED tests.test_pipeline_check::test_criss_cross_branch_lists_only_its_own_changes
baseline tests/test_webull_sandbox.py: 0 failed, 18 passed, 0 errors, 0 skipped; 2.0 s
RI-012-059-bare-429 (RI-012): 1 failed, 17 passed, 0 errors, 0 skipped; target tests/test_webull_sandbox.py::test_429_inside_other_text_is_not_retried failed: yes; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 17 passed; code check: ccbot.broker.webull_sandbox is ccbot/broker/webull_sandbox.py in the worktree; 4.2 s
    FAILED tests.test_webull_sandbox::test_429_inside_other_text_is_not_retried
RI-006-082-suite (RI-006): 5 failed, 299 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_suite_line_dropped_middle_is_incomplete failed: yes; HOLDS; recorded RECORDED_TBD (recorded unreadable); code check: n/a (tests/test_pipeline_check.py runs scripts/check_pipeline.py as REPO/scripts/check_pipeline.py (_run) and imports check_pipeline after sys.path.insert(0, REPO/scripts) (_cp), REPO from tests/conftest.py); 36.8 s
    FAILED tests.test_pipeline_check::test_suite_compared_with_last_i2_line
    FAILED tests.test_pipeline_check::test_suite_line_dropped_middle_is_incomplete
    FAILED tests.test_pipeline_check::test_suite_line_part_of_field_is_incomplete[S3-tail]
    FAILED tests.test_pipeline_check::test_suite_line_part_of_field_is_incomplete[S4-note]
    FAILED tests.test_pipeline_check::test_unfilled_template_suite_line_is_incomplete
TOTAL: 10 probes, 10 hold, 0 not held, 0 anchor missing, 0 error; 326.8 s
```
Run 2 (scratch commit df63481, the same plus the filled `recorded`):
```
$ python3 scripts/probe_guardrails.py --ref HEAD --repo <scratch>
ref HEAD = df63481e198fbaa9e73d070851848e60e2cce42b
baseline tests/test_realtest.py: 0 failed, 50 passed, 0 errors, 0 skipped; 24.7 s
RI-002-063-leading-edge (RI-002): 9 failed, 41 passed, 0 errors, 0 skipped; target tests/test_realtest.py::test_leading_edge_100_days_blocks failed: yes; HOLDS; recorded 2026-11-18: 9 failed, 41 passed; code check: ccbot.realtest is ccbot/realtest.py in the worktree; 73.6 s
    FAILED tests.test_realtest::test_drop_input[earnings]
    FAILED tests.test_realtest::test_drop_input[earnings_before_first]
    FAILED tests.test_realtest::test_empty_earnings_file_warns_and_lead_is_null
    FAILED tests.test_realtest::test_leading_edge_100_days_blocks
    FAILED tests.test_realtest::test_leading_edge_151_days_blocks
    FAILED tests.test_realtest::test_real_counts_bac[d0.150_dte14-24_noE_hold_bid]
    FAILED tests.test_realtest::test_real_counts_bac[d0.275_dte30-45_noE_hold_bid]
    FAILED tests.test_realtest::test_real_counts_bac[d0.450_dte30-45_noE_hold_bid]
    FAILED tests.test_realtest::test_stock_without_earnings_sells_nothing
RI-002-065-interior-gap (RI-002): 4 failed, 46 passed, 0 errors, 0 skipped; target tests/test_realtest.py::test_interior_gap_180_blocks failed: yes; HOLDS; recorded 2026-11-18: 4 failed, 46 passed; code check: ccbot.realtest is ccbot/realtest.py in the worktree; 24.7 s
    FAILED tests.test_realtest::test_drop_input[earnings_interior_gap]
    FAILED tests.test_realtest::test_interior_gap_121_blocks
    FAILED tests.test_realtest::test_interior_gap_180_blocks
    FAILED tests.test_realtest::test_real_interior_gap_mo
baseline tests/test_diff_reports.py: 0 failed, 17 passed, 0 errors, 0 skipped; 1.9 s
RI-013-067-1b (RI-013): 1 failed, 16 passed, 0 errors, 0 skipped; target tests/test_diff_reports.py::test_a_nested_key_and_list_in_dict failed: yes; HOLDS; recorded 2026-11-18: 1 failed, 16 passed; code check: n/a (tests/test_diff_reports.py runs scripts/diff_reports.py as REPO/scripts/diff_reports.py (SCRIPT), REPO from tests/conftest.py); 2.8 s
    FAILED tests.test_diff_reports::test_a_nested_key_and_list_in_dict
baseline tests/test_missing_inputs.py: 0 failed, 23 passed, 0 errors, 0 skipped; 1.4 s
RI-002-046-tickers-key (RI-002): 1 failed, 22 passed, 0 errors, 0 skipped; target tests/test_missing_inputs.py::test_ticker_fields_cover_file_and_code failed: yes; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 22 passed; code check: n/a (config/tickers.json is data: tests/test_missing_inputs.py test_ticker_fields_cover_file_and_code reads tickers.json from Path(__file__).resolve().parents[1]); 2.7 s
    FAILED tests.test_missing_inputs::test_ticker_fields_cover_file_and_code
baseline tests/test_pipeline_check.py: 0 failed, 304 passed, 0 errors, 0 skipped; 37.5 s
RI-007-064-work-py (RI-007): 8 failed, 296 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_research_only_work_py_is_research_code failed: yes; HOLDS; recorded 2026-11-20 (078/05): 8 failed, 82 passed; code check: n/a (tests/test_pipeline_check.py runs scripts/check_pipeline.py as REPO/scripts/check_pipeline.py (_run) and imports check_pipeline after sys.path.insert(0, REPO/scripts) (_cp), REPO from tests/conftest.py); 75.8 s
    FAILED tests.test_pipeline_check::test_is_code_examples
    FAILED tests.test_pipeline_check::test_py_added_to_completed_item_is_untracked
    FAILED tests.test_pipeline_check::test_research_code_rules
    FAILED tests.test_pipeline_check::test_research_only_branch_nested_py_is_seen
    FAILED tests.test_pipeline_check::test_research_only_branch_work_py_is_branch_skipped
    FAILED tests.test_pipeline_check::test_research_only_work_py_is_research_code
    FAILED tests.test_pipeline_check::test_work_code_pattern[work/061/diag_keep.py-True]
    FAILED tests.test_pipeline_check::test_work_code_pattern[work/160/sub/x.py-True]
RI-009-037-clash-line (RI-009): 1 failed, 303 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_same_id_on_main_and_open_branch_is_a_clash failed: yes; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 89 passed; code check: n/a (tests/test_pipeline_check.py runs scripts/check_pipeline.py as REPO/scripts/check_pipeline.py (_run) and imports check_pipeline after sys.path.insert(0, REPO/scripts) (_cp), REPO from tests/conftest.py); 38.4 s
    FAILED tests.test_pipeline_check::test_same_id_on_main_and_open_branch_is_a_clash
RI-010-049-rules-line (RI-010): 1 failed, 303 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_rules_branch_is_reported failed: yes; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 89 passed; code check: n/a (tests/test_pipeline_check.py runs scripts/check_pipeline.py as REPO/scripts/check_pipeline.py (_run) and imports check_pipeline after sys.path.insert(0, REPO/scripts) (_cp), REPO from tests/conftest.py); 37.6 s
    FAILED tests.test_pipeline_check::test_rules_branch_is_reported
RI-011-052-merge-tree (RI-011): 1 failed, 303 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_criss_cross_branch_lists_only_its_own_changes failed: yes; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 89 passed; code check: n/a (tests/test_pipeline_check.py runs scripts/check_pipeline.py as REPO/scripts/check_pipeline.py (_run) and imports check_pipeline after sys.path.insert(0, REPO/scripts) (_cp), REPO from tests/conftest.py); 40.2 s
    FAILED tests.test_pipeline_check::test_criss_cross_branch_lists_only_its_own_changes
baseline tests/test_webull_sandbox.py: 0 failed, 18 passed, 0 errors, 0 skipped; 1.9 s
RI-012-059-bare-429 (RI-012): 1 failed, 17 passed, 0 errors, 0 skipped; target tests/test_webull_sandbox.py::test_429_inside_other_text_is_not_retried failed: yes; HOLDS; recorded 2026-11-20 (078/05): 1 failed, 17 passed; code check: ccbot.broker.webull_sandbox is ccbot/broker/webull_sandbox.py in the worktree; 3.8 s
    FAILED tests.test_webull_sandbox::test_429_inside_other_text_is_not_retried
RI-006-082-suite (RI-006): 5 failed, 299 passed, 0 errors, 0 skipped; target tests/test_pipeline_check.py::test_suite_line_dropped_middle_is_incomplete failed: yes; HOLDS; recorded 2026-11-21 (082/05): 5 failed, 299 passed; code check: n/a (tests/test_pipeline_check.py runs scripts/check_pipeline.py as REPO/scripts/check_pipeline.py (_run) and imports check_pipeline after sys.path.insert(0, REPO/scripts) (_cp), REPO from tests/conftest.py); 37.8 s
    FAILED tests.test_pipeline_check::test_suite_compared_with_last_i2_line
    FAILED tests.test_pipeline_check::test_suite_line_dropped_middle_is_incomplete
    FAILED tests.test_pipeline_check::test_suite_line_part_of_field_is_incomplete[S3-tail]
    FAILED tests.test_pipeline_check::test_suite_line_part_of_field_is_incomplete[S4-note]
    FAILED tests.test_pipeline_check::test_unfilled_template_suite_line_is_incomplete
TOTAL: 10 probes, 10 hold, 0 not held, 0 anchor missing, 0 error; 337.9 s
```
Run 2: `TOTAL: 10 probes, 10 hold`, no `(live differs)`, no `(recorded unreadable)`. No old anchor went missing after 081/084/086.

Mutations. These ran in a second scratch clone (/tmp/claude-0/-home-claude/8f94cbd2-523d-52d1-8971-85df3e672dc0/scratchpad/i2-082-mut, cloned from the probe clone at df63481), with `git checkout -- .` before each. The script is /tmp/claude-0/-home-claude/8f94cbd2-523d-52d1-8971-85df3e672dc0/scratchpad/tools/mutate.py, holding exact anchor → replacement pairs. Each run is the whole named test file. Unmutated baseline in that clone: `tests/test_pipeline_check.py tests/test_probe_guardrails.py` → `318 passed in 41.11s`.
```
compare removed (scripts/check_pipeline.py): 5 failed, 299 passed in 35.59s; target test_suite_line_dropped_middle_is_incomplete failed: yes
field in suite (scripts/check_pipeline.py): 1 failed, 303 passed in 36.81s; target test_suite_line_part_of_field_is_incomplete[S3-tail] failed: yes
suite in field (scripts/check_pipeline.py): 1 failed, 303 passed in 35.50s; target test_suite_line_part_of_field_is_incomplete[S4-note] failed: yes
first wins (scripts/check_pipeline.py): 1 failed, 303 passed in 37.78s; target test_two_suite_lines_are_incomplete failed: yes
last wins (scripts/check_pipeline.py): 1 failed, 303 passed in 37.33s; target test_two_suite_lines_are_incomplete failed: yes
fence ignored (no state test) (scripts/check_pipeline.py): 1 failed, 303 passed in 39.44s; target test_suite_line_inside_fence_is_not_read failed: yes
fence: state != 'in' (plan's form) (scripts/check_pipeline.py): 304 passed in 34.73s; target test_suite_line_inside_fence_is_not_read failed: NO
fallback to earlier well-formed I2 (scripts/check_pipeline.py): 1 failed, 303 passed in 34.35s; target test_suite_with_malformed_last_i2_line_never_falls_back failed: yes
first I2 line (scripts/check_pipeline.py): 2 failed, 302 passed in 35.70s; target test_suite_compared_with_last_i2_line failed: yes
>= -> > (scripts/check_pipeline.py): 1 failed, 303 passed in 37.17s; target test_suite_line_dropped_middle_is_incomplete failed: yes
cutoff removed (scripts/check_pipeline.py): 2 failed, 302 passed in 38.10s; target test_suite_below_cutoff_not_checked failed: yes
084 gate removed (scripts/check_pipeline.py): 1 failed, 303 passed in 35.93s; target test_suite_gate_follows_rule_file_of_05_commit[S13-not-seen] failed: yes
{n,} -> {n} (scripts/check_pipeline.py): 1 failed, 303 passed in 37.70s; target test_i3_verdict_reader[longer-close] failed: yes
_logged no left pipe (scripts/check_pipeline.py): 1 failed, 303 passed in 36.84s; target test_uncommitted_step_with_lookalike_log_lines_is_listed failed: yes
SHALLOW fullmatch -> match (scripts/check_pipeline.py): 1 failed, 303 passed in 37.55s; target test_shallow_file_unreadable_not_checked failed: yes
SHALLOW fullmatch -> search (scripts/check_pipeline.py): 1 failed, 303 passed in 37.62s; target test_shallow_file_unreadable_not_checked failed: yes
{40} -> {40,} (scripts/check_pipeline.py): 1 failed, 303 passed in 35.69s; target test_shallow_file_unreadable_not_checked failed: yes
recorded deleted from a shipped entry (scripts/probe_guardrails.py): 1 failed, 13 passed in 8.37s; target test_shipped_probes_well_formed failed: yes
live-differs branch removed (scripts/probe_guardrails.py): 1 failed, 13 passed in 8.03s; target test_recorded_failed_count_differs_is_marked failed: yes
compare failed+passed (scripts/probe_guardrails.py): 1 failed, 13 passed in 7.99s; target test_recorded_failed_count_same_is_not_marked failed: yes
compare full string (scripts/probe_guardrails.py): 1 failed, 13 passed in 6.61s; target test_recorded_failed_count_same_is_not_marked failed: yes
live n/a branch removed (scripts/probe_guardrails.py): 1 failed, 13 passed in 6.57s; target test_recorded_without_live_results_is_na failed: yes
a1 marker clause deleted (.claude/agents/a1-auditor.md): 1 failed, 13 passed in 6.66s; target test_a1_text_marks_probe_markers_as_information failed: yes
a1 unshallow sentences deleted (.claude/agents/a1-auditor.md): 1 failed, 303 passed in 36.91s; target test_unshallow_sentence_same_in_three_files failed: yes
run-item step-5 sentence deleted (.claude/commands/run-item.md): 1 failed, 303 passed in 34.38s; target test_run_item_commit_subject_rule failed: yes
run-item I2 sentence deleted (.claude/commands/run-item.md): 1 failed, 303 passed in 34.46s; target test_run_item_commit_subject_rule failed: yes
template Suite line deleted (templates/build-report.md): 2 failed, 302 passed in 35.84s; target test_suite_label_in_template_and_i2_text failed: yes
```
26 of 27 mutants fail their named target. The survivor is the plan's `state != "in"` form of "fence ignored", which is an equivalent mutant (Deviations 2). The real "fence ignored" mutant (no state test) fails S5.

check_pipeline on the repo (before this 05 existed, exit 0):
```
$ python3 scripts/check_pipeline.py
001: LEGACY (RESEARCH ONLY before 07-audit-task existed (item 021))
002: complete (FULL)
003: complete (FULL)
004: LEGACY (07 is combined in work/003/07-audit-task.md)
005: LEGACY (07 is combined in work/003/07-audit-task.md)
006: LEGACY (07 is combined in work/003/07-audit-task.md)
007: LEGACY (07 is combined in work/003/07-audit-task.md)
008: LEGACY (07 is combined in work/003/07-audit-task.md)
009: complete (FULL)
010: complete (FULL)
011: complete (FULL)
012: complete (FULL)
013: complete (FULL)
014: complete (FULL)
015: complete (FULL)
016: complete (FULL)
017: complete (FULL)
018: complete (FULL)
019: complete (FULL)
020: complete (FULL)
021: complete (FULL)
022: complete (FULL)
023: complete (RESEARCH ONLY; Waived: 02 (A1, 2026-10-31, item 026: the screen was already delivered; R3's fact check was run afterwards in 026; the person can ask for the R2 language search))
024: complete (FULL; Waived: 01 02 03 04 (person, 2026-10-31: approved by merging PR #6, which asked for this waiver by name. Written by A1 in item 026: built and merged before the step check existed; the rule is the person's own decision in 001; I3 ran afterwards in 026. Who-field updated in item 031.))
025: complete (FULL)
026: complete (FULL)
027: complete (FULL)
028: complete (FULL)
029: complete (FULL)
030: complete (FULL)
031: complete (FULL)
032: complete (FULL)
033: complete (FULL)
034: complete (FULL)
035: complete (FULL)
036: complete (FULL)
037: complete (FULL)
038: complete (FULL)
039: complete (FULL)
040: complete (FAST)
041: complete (FULL)
042: complete (FULL)
043: complete (FULL)
044: complete (FULL)
045: complete (FULL)
046: complete (FULL)
047: complete (FULL)
048: complete (FULL)
049: complete (FULL)
050: complete (FULL)
051: complete (FULL)
052: complete (FULL)
053: complete (FULL)
054: complete (FULL)
055: complete (FULL)
056: complete (FULL)
057: complete (RESEARCH ONLY)
058: complete (FULL)
059: complete (FULL)
060: complete (FULL)
061: complete (FULL)
062: complete (FULL)
063: complete (FULL)
064: complete (FULL)
065: complete (FULL)
066: complete (FULL)
067: complete (FULL)
068: complete (FULL)
069: complete (FULL)
070: complete (FULL)
071: complete (FULL)
072: complete (FULL)
073: complete (FULL)
074: complete (FULL)
075: complete (FULL)
076: complete (FULL)
077: complete (FULL)
078: complete (FULL)
079: complete (FULL)
080: complete (FULL)
081: complete (FULL)
082: in progress (FULL: next 05)
083: complete (FULL)
084: complete (FULL)
085: complete (FULL)
086: complete (FULL)
STUCK: none
AWAITING A1: none
IN PR: none
OPEN BRANCHES (not merged into HEAD):
  origin/claude/project-thread-f64g3k: items none; merges cleanly; last commit 2026-11-20 (1 days)
RULES BRANCH: none
ID CLASH: none
I3 FAIL: none
A1 FAIL: none
INCOMPLETE: none
RULE NOT SEEN: 083 (05 added in cfc0634 without TESTS_FORMAT_FROM (076): judged by I2_BEFORE; 06 added in cfc0634 without VERDICT_FROM (071): judged by no Sent-back check; item 084)
LOG TIME: none (not checked: 048: built before 045's --log rule reached main; times typed by hand, not recoverable (item 049))
LOG BATCH: none (not checked: 083: six lines written in one batch at 10:15 after the build (commit cfc0634 10:15:48); real times not recoverable (item 086)); not computable: 048: no pytest time in 05/06/I2 line; 054: no pytest time in 05/06/I2 line; 055: no pytest time in 05/06/I2 line; 056: no pytest time in 05/06/I2 line; 058: no pytest time in 05/06/I2 line; 059: no pytest time in 05/06/I2 line; 060: no pytest time in 05/06/I2 line
UNTRACKED CHANGE: none
RESEARCH CODE: none
REAL-DATA FIELD: none
UNCOMMITTED STEP: none
ORPHAN LOG: none
INBOX: not checked (2026-11-20.md added in 8f1e9f7; its templates/daily-audit.md has no ## Inbox)
SKIPPED: none
```
No item has a Suite entry (none is >= 87). `RULE NOT SEEN:` is still exactly 083's line. 082 is listed as in progress.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat`: .claude/agents/a1-auditor.md, .claude/agents/i2-builder.md, .claude/commands/run-item.md, scripts/check_pipeline.py, scripts/probe_guardrails.py, templates/build-report.md, tests/test_pipeline_check.py, tests/test_probe_guardrails.py, tests/test_real_data_field.py; no TRIGGER path)

## Deviations from plan
1. **No commit in the repo.** The orchestrator said no commits, so the plan's "Commit, re-run" step ran in a scratch clone (see Test output). The scratch commit also holds a placeholder 05 and a scratch I2 line. Without them the clone's own repo self-test fails on UNTRACKED CHANGE, and every check_pipeline probe would be ERROR (baseline). The real I2 line is written in the repo by `--log` after this file.
2. **The plan's fence mutant is equivalent.** `state != "in"` differs from `state == "out"` only on "mark" rows. A fence opener or closer starts with 0-3 spaces and then a backtick or tilde, so it can never start with `Suite:`, and no fixture can kill this mutant (run: `304 passed`). I also ran "state ignored" (`if line.startswith("Suite:")`), and S5 kills it. No code change follows from this.
3. **One more fixture helper needed the Suite line.** `_batch_item(..., full=True)` (086, built after the plan was written) writes a 05 for ID 999, and that made `test_batch_083_shape_is_flagged` and `test_batch_untimed_item_is_not_computable` INCOMPLETE. With full=True it now writes `Suite: <tests part of the last I2 field in impl>` above `## Test output`. SUMMARY_LINE is matched from the line start, so rule C does not read it. The plan allows this ("gets the line in its fixture text"). No assertion changed.
4. **S13 shape.** This is a one-commit tmp repo, not 084's two-branch shape: the commit holds RULE_FILE (`TESTS_FORMAT_FROM = 76
VERDICT_FROM = 71
`, plus `SUITE_FROM = 87
` for S13b) and item 151 with a 05 that has no Suite line. It runs with `--untracked-from <that sha>`. Both cases are one parametrized function. The assertions are the plan's: S13 names 151 in `RULE NOT SEEN:` (exact text), not INCOMPLETE. S13b gives `INCOMPLETE: 151 (05 has no 'Suite:' line (item 082))` and `RULE NOT SEEN: none`.
5. **Docstring placement.** The Suite paragraph sits right after the item-076 `--log` paragraph, which means before 086's rule-D paragraph. The plan predates 086's paragraph.

Known limits (from the plan):
- Points 4b (the a1 unshallow sentence) and 5 (the commit-subject rule) are text pins only, which is a partial guard. No check reads commit text (062, RI-012).
- The unshallow sentence's list (UNTRACKED CHANGE, RESEARCH CODE, REAL-DATA FIELD) does not name 084's `RULE NOT SEEN` "not checked" form. Changing it would mean changing all three copies, so that is a separate item if wanted.
- No real item reaches the Suite rule before ID 87, so on this branch only the fixtures prove it.

## Round 2 (sent back by I3, 06 finding 1)
### Changes made (file: what changed)
- `tests/test_pipeline_check.py`: new `test_suite_inside_other_text_is_not_read` (S14), placed after S11/S12. Its 05 holds the column-0 line `Suite: 1 passed` plus a prose line ``the `Suite:` line above is copied as printed``, a list item ``- `Suite: 2 passed` was round 1`` and an indented line `   Suite: 2 passed`. The I2 field is `tests 1 passed` (the `_suite_item` default). The test expects `INCOMPLETE: none` and exit 0. This round changes no code and no other file.

File counts (this round's working tree, vs HEAD 8a9f32a):
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
0
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
1
```

### Mutation probes (scratch copies, python3 -B, never the repo)
I made three full copies of the repo with `cp -a` (made after the S14 edit), named `/tmp/claude-0/-home-claude/8f94cbd2-523d-52d1-8971-85df3e672dc0/scratchpad/i2-082r2-full-{ctl,in,lstrip}`. In `scripts/check_pipeline.py` `_suite_lines`, I replaced `if state == "out" and line.startswith("Suite:")]` with one mutant per copy (each replacement count asserted to be 1). The ctl copy is left unmutated.
Command in each copy: `python3 -B -m pytest -q -p no:cacheprovider tests/test_pipeline_check.py | tail -4`
```
== ctl
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 304 passed in 33.67s
== in            ("Suite:" in line)
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_suite_inside_other_text_is_not_read
2 failed, 303 passed in 34.68s
== lstrip        (line.lstrip().startswith("Suite:"))
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_suite_inside_other_text_is_not_read
2 failed, 303 passed in 35.58s
```
S14 kills both mutants, and in each copy it is the only test that the mutant alone breaks (compare ctl). In round 1, both mutants survived the whole file (06: `304 passed`).

An earlier try copied only scripts/tests/templates/.claude/config. It also failed `test_work_code_counts_repo_diagnostics` and `test_batch_083_flagged_on_repo_data`, because those tests need work/ and logs/. I discarded it and used the full copies above.

### The one failure in the suite (repo state, not this change)
`test_repo_pipeline_has_no_skipped_items` fails in the repo and in the unmutated copy. It runs check_pipeline on the repo, and 082 is now `I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))` until I3 re-verifies. The first line of the pytest message is `001: LEGACY (...)`, which is the start of check_pipeline's output, and the test asserts `code == 0`. Round 1's `672 passed` ran before the FAIL 06 existed. Earlier sent-back rounds logged this failure as printed in the same way (076, 077, 079, 080, 085 in logs/implementation/2026-11-20.md).

### Tests re-run (output)
```
$ python3 -B -m pytest -q -p no:cacheprovider tests/test_pipeline_check.py -k suite | tail -1
16 passed, 289 deselected in 3.07s
$ python3 -m pytest -q | tail -4
tests/test_pipeline_check.py:181: AssertionError
=========================== short test summary info ============================
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 672 passed, 1 skipped in 88.54s (0:01:28)
```
The column-0 `Suite:` line above (Test output section) is this last line, as printed.

### Connectivity / missing-data
- S14 runs under pytest (it is in the `-k suite` run above) and checks `_suite_lines` via `incomplete()`. No new function and no new branch in code.
- Missing-data grep (`grep -rnE "fillna|...|\.get\([^)]*, 0\)" ccbot/`): 38 hits, all unchanged. `git diff --stat HEAD -- ccbot/ config/` is empty, so there are no new or changed hits. No dataclass fields or `>`/`<` tests were added. The plan names no feasibility test. ccbot/realtest.py is unchanged, so no real-data run is needed.

### Recurring issues checked (step 0)
RI-001 (ESCALATED): n/a. No rule or window, tests only.
RI-010 (ESCALATED): this round's own checklist is followed. The step file is written first, then `--log`, then check_pipeline is confirmed.
RI-014 (OPEN): S14 uses `_suite_item` (no git) and does not depend on clone depth.
RI-006: the Suite line and the I2 field are copied from the printed pytest line, not counted by hand. File counts come from commands.
RI-012: S14 is the missing negative fixture for the column-0 line reader. Both substring/lstrip mutants are shown killed.
RI-009: probes ran in scratch copies only. The repo tree is untouched except the test file and this 05.
RI-002, RI-007, RI-008: no change in scope (no data handling, no use before steps, no new syntax).
RI-006: GUARDED (unchanged by this round; 082 extends it)
RI-012: GUARDED (S14 closes 06 finding 1)
