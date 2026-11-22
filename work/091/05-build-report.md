# 05 Build report - 091
Built on daily-fixes/2026-11-21 in three commits, (A) steps 1-3 (tests only), (B) steps 4, 5a, 5b and 7, (C) step 6, as 04 orders. This file grows with each commit; the final text is in commit (C).

## Base (step 0)
`git log --oneline -4` at the start of commit (A):
```
aab6b41 Item 090: A1 result PASS
eb57a85 Item 087: 01:04 | I3 | 087 | PASS | sent to audit: yes
b82ebb4 Item 090: 01:01 | I3 | 090 | PASS | sent to audit: yes
7389962 Item 087: 01:00 | I2 | 087 | 1 files changed | tests 1 failed, 761 passed, 1 skipped in 84.74s (0:01:24)
```
Head sha: aab6b41419b631df1f4d4f4b90cf0c72a3b044fa. 088 (4a6cdc8 and before), 089 (d3aa031 A1 PASS) and 090 (8caffda build, aab6b41 A1 PASS) are all committed below it. The two newest commits after b82ebb4 touch only work/087, work/090 and logs/ (`git diff --stat b82ebb4 eb57a85`: logs/implementation/2026-11-22.md, work/087/06, work/087/07).

Re-read by text (line numbers have moved; found by name):
- `open_branches`: the unrelated block runs `merge-base --all HEAD <ref>`; on exit 1 it runs `_git_ok("ls-tree", "-r", "--name-only", ref, "--", "work/", RECURRING, *RULE_PATHS, *RESEARCH_CODE_PATHS)`. 090 added a shallow-clone text for this case only when `shallow` is True; the non-shallow text is unchanged (`no common history with HEAD; <n> file(s) on checked paths (first: <path>) not checked (item 081)`), so step 1 uses it as planned.
- `main_ahead(shallow=False)` and `open_branches(today, shallow)`: 090 added a `shallow` argument, not `env`. The git args of the patched tuples in step 2 are unchanged (checked by text: `("branch", "-r", "--no-merged", "HEAD", "--format=%(refname:short)")`, `("for-each-ref", "--format=%(refname) %(objectname)", f"refs/remotes/{MAIN}")`, `("rev-list", "--count", f"HEAD..{sha}")`, `("ls-tree", "-d", "--name-only", ref, "--", "work/")`).
- `next_id`: returns `(None, why)` on the per-ref ls-tree failure; `main` prints `--next-id refused: <why>; ...` to stderr and returns 2.
- main's final exit expression (verbatim): `return 1 if skipped or failed or i3_failed or unfinished or late or orphans or (untracked and untracked[1]) or (real and real[2]) or (uncommitted and uncommitted[1]) or isinstance(branches, str) or branch_errors or isinstance(ahead, str) or batch["flagged"] or env_failed or unreadable else 0`, plus the earlier `if inbox_bad: ... return 1`.
- `_run_seconds(path, heading)`: opens on an "out" row with `re.match(heading, line)` (the opener row itself is not read), closes on an "out" row with `re.match(r"#{1,2} ", line)`; 090 did not change it. `batch_log_items` passes the openers `r"## Test output\b"` (05) and `r"## Tests re-run\b"` (06).
- `incomplete(item_dir, logs, env, not_seen, batch_nc)` and `_rule_seen(item_dir, step, const, env)`: as 04 describes; SUITE_FROM's gate is `fired` → `_rule_seen(..., "05", "SUITE_FROM", env)` → not_seen row on False, else `missing += [fired] + ([sha7] if seen is None and sha7 else [])`.
- 089's `_read(path, missing_ok=False)` and `_UNREAD`: present; `_read(..., missing_ok=True)` gives `(None, None)` for a missing file.
- GIT_CENSUS total as read: `assert sum(seen.values()) == 47                    # 41 (081) + 5 (084) + 1 (081 r2)` (088-090 left it at 47). 089's `test_read_census`: `assert sum(seen.values()) == 2`. 091 adds 0 to both.
- `UNSHALLOW` after 090 (test and 3 copies): `... report UNTRACKED CHANGE, RESEARCH CODE, REAL-DATA FIELD, LOG TIME, MAIN AHEAD and OPEN BRANCHES as 'not checked', never 'none' (items 079, 090).` 090 changed the list (added LOG TIME, MAIN AHEAD, OPEN BRANCHES) and does not name RULE NOT SEEN, so step 4 adds RULE NOT SEEN to 090's list.

### Exit-term table (step 0)
One row per term of main's final exit expression (plus the earlier `inbox_bad` return), each dropped alone (term replaced by `False`, or `return 1` → `return 0`) in the scratch worktree /tmp/claude-0/scratch/i2-091b/wt (8dec4f6 + the (C) files), running tests/test_pipeline_check.py and tests/test_real_data_field.py (the two test files that load check_pipeline). Every count includes `test_repo_pipeline_has_no_skipped_items`, which fails in every row for the transient reason in the whole-output diff below; it is left out of the killer lists. The table abridges long killer lists; the whole output, as printed, follows it.

| Term dropped | Result as printed | Killing test(s) (source) |
|---|---|---|
| `skipped` | 10 failed, 410 passed in 55.63s | test_build_without_research_is_skipped, test_result_before_fact_check_is_skipped, ... (9) |
| `failed` | 2 failed, 418 passed in 59.26s | test_a1_fail_is_not_complete |
| `i3_failed` | 6 failed, 414 passed in 60.37s (0:01:00) | test_i3_fail_shows_and_exits_1 and 4 more (071) |
| `unfinished` | 34 failed, 386 passed in 64.99s (0:01:04) | test_incomplete_06_and_missing_log_line, ..., test_stray_round_heading_is_incomplete[P1-P3] (091), 15 in test_real_data_field.py |
| `late` | 3 failed, 417 passed in 62.11s (0:01:02) | test_log_time_exception_is_named_and_closed, test_blame_failure_of_committed_log_is_an_entry |
| `orphans` | 2 failed, 418 passed in 58.52s | test_orphan_log_line_is_reported |
| `(untracked and untracked[1])` | 10 failed, 410 passed in 60.04s (0:01:00) | test_completed_item_note_with_config_is_untracked and 8 more (053) |
| `(real and real[2])` | 3 failed, 417 passed in 57.60s | test_t19_main_exits_1_when_git_log_fails, test_t20_main_exits_1_for_triggered_id_without_request |
| `(uncommitted and uncommitted[1])` | 2 failed, 418 passed in 59.20s | test_uncommitted_step_without_logs_folder_is_listed |
| `isinstance(branches, str)` | 2 failed, 418 passed in 58.97s | test_branch_list_failure_exits_1 (091 step 2, A8) |
| `branch_errors` | 7 failed, 413 passed in 61.70s (0:01:01) | test_branch_diff_failure_is_branch_error, ..., test_unrelated_branch_each_checked_group_is_branch_error (091 step 1) |
| `isinstance(ahead, str)` | 3 failed, 417 passed in 56.68s | test_main_ref_lookup_failure_exits_1, test_main_ahead_count_failure_exits_1 (091 step 2, A9a/A9b) |
| `batch["flagged"]` | 3 failed, 417 passed in 57.38s | test_batch_083_shape_is_flagged, test_round_bound_end_to_end (086, 090) |
| `env_failed` | 2 failed, 418 passed in 53.38s | test_anchor_env_failure_exits_1 (088/05 M-f) |
| `unreadable` | 7 failed, 413 passed in 53.09s | test_unreadable_log_exits_1_alone (089 6a/M3) and 5 more |
| `inbox_bad` → `return 0` | 16 failed, 404 passed in 55.07s | test_inbox_heading_missing_fails and 14 more |

```
== drop skipped: 10 failed, 410 passed in 55.63s
    FAILED tests/test_pipeline_check.py::test_build_without_research_is_skipped
    FAILED tests/test_pipeline_check.py::test_result_before_fact_check_is_skipped
    FAILED tests/test_pipeline_check.py::test_fast_scope_never_skips_verification
    FAILED tests/test_pipeline_check.py::test_fact_check_and_verification_waivable_only_by_person
    FAILED tests/test_pipeline_check.py::test_fast_needs_person_and_date
    FAILED tests/test_pipeline_check.py::test_research_only_head_commit_with_code_is_skipped
    FAILED tests/test_pipeline_check.py::test_second_waived_line_is_not_read
    FAILED tests/test_pipeline_check.py::test_rescoped_to_full_is_not_research_but_still_skipped
    FAILED tests/test_pipeline_check.py::test_research_only_work_py_is_research_code
== drop failed: 2 failed, 418 passed in 59.26s
    FAILED tests/test_pipeline_check.py::test_a1_fail_is_not_complete
== drop i3_failed: 6 failed, 414 passed in 60.37s (0:01:00)
    FAILED tests/test_pipeline_check.py::test_i3_fail_shows_and_exits_1
    FAILED tests/test_pipeline_check.py::test_i3_fail_beats_older_a1_fail
    FAILED tests/test_pipeline_check.py::test_i3_fail_after_a1_pass_is_a_new_item
    FAILED tests/test_pipeline_check.py::test_i3_fail_with_no_a1_line_keeps_old_detail
    FAILED tests/test_pipeline_check.py::test_i3_fail_with_a1_pass_only_inside_text_keeps_old_detail
== drop unfinished: 34 failed, 386 passed in 64.99s (0:01:04)
    FAILED tests/test_pipeline_check.py::test_incomplete_06_and_missing_log_line
    FAILED tests/test_pipeline_check.py::test_malformed_log_line_is_incomplete
    FAILED tests/test_pipeline_check.py::test_malformed_log_line_names_expected_format
    FAILED tests/test_pipeline_check.py::test_i2_tests_field_cutoff
    FAILED tests/test_pipeline_check.py::test_old_06_without_round_headers_unchanged
    FAILED tests/test_pipeline_check.py::test_06_verdict_disagrees_with_last_i3_log
    FAILED tests/test_pipeline_check.py::test_pass_without_sent_back_none_is_incomplete
    FAILED tests/test_pipeline_check.py::test_malformed_last_i3_line_is_not_replaced
    FAILED tests/test_pipeline_check.py::test_rule_anchor_without_rule_file
    FAILED tests/test_pipeline_check.py::test_rule_not_seen_shallow_and_no_git
    FAILED tests/test_pipeline_check.py::test_batch_untimed_item_is_not_computable
    FAILED tests/test_pipeline_check.py::test_suite_line_absent_is_incomplete
    FAILED tests/test_pipeline_check.py::test_suite_line_dropped_middle_is_incomplete
    FAILED tests/test_pipeline_check.py::test_batch_not_computable_strict_from_090[990-True]
    FAILED tests/test_pipeline_check.py::test_stray_round_heading_is_incomplete[P1]
    FAILED tests/test_pipeline_check.py::test_stray_round_heading_is_incomplete[P2]
    FAILED tests/test_pipeline_check.py::test_stray_round_heading_is_incomplete[P3]
    FAILED tests/test_real_data_field.py::test_t2_comment_only_field_is_incomplete
    FAILED tests/test_real_data_field.py::test_t4_not_required_on_trigger_is_incomplete
    FAILED tests/test_real_data_field.py::test_t5_total_outside_the_section_does_not_count
    FAILED tests/test_real_data_field.py::test_t6_pr_merge_flags_only_the_item_whose_commit_triggers
    FAILED tests/test_real_data_field.py::test_t7b_cutoff_edge_item_070_is_checked
    FAILED tests/test_real_data_field.py::test_t7c_cutoff_edge_pair_in_one_repo
    FAILED tests/test_real_data_field.py::test_t11_data_real_file_triggers
    FAILED tests/test_real_data_field.py::test_t12_fences_and_headings[no-heading]
    FAILED tests/test_real_data_field.py::test_t12_fences_and_headings[unclosed]
    FAILED tests/test_real_data_field.py::test_t12_fences_and_headings[4-space]
    FAILED tests/test_real_data_field.py::test_t17_trigger_with_no_05_is_incomplete
    FAILED tests/test_real_data_field.py::test_t21_total_inside_prose_is_incomplete[quoted-total]
    FAILED tests/test_real_data_field.py::test_t21_total_inside_prose_is_incomplete[total-in-brackets]
    FAILED tests/test_real_data_field.py::test_t21_total_inside_prose_is_incomplete[word-total]
    FAILED tests/test_real_data_field.py::test_t21_total_inside_prose_is_incomplete[total-colon]
    FAILED tests/test_real_data_field.py::test_t22_total_line_inside_a_comment_does_not_count
== drop late: 3 failed, 417 passed in 62.11s (0:01:02)
    FAILED tests/test_pipeline_check.py::test_log_time_exception_is_named_and_closed
    FAILED tests/test_pipeline_check.py::test_blame_failure_of_committed_log_is_an_entry
== drop orphans: 2 failed, 418 passed in 58.52s
    FAILED tests/test_pipeline_check.py::test_orphan_log_line_is_reported
== drop (untracked and untracked[1]): 10 failed, 410 passed in 60.04s (0:01:00)
    FAILED tests/test_pipeline_check.py::test_completed_item_note_with_config_is_untracked
    FAILED tests/test_pipeline_check.py::test_new_item_step_file_covers_code
    FAILED tests/test_pipeline_check.py::test_merge_bringing_untracked_commit_is_flagged
    FAILED tests/test_pipeline_check.py::test_cutoff_missing_in_full_repo_fails
    FAILED tests/test_pipeline_check.py::test_audit_file_never_covers_code
    FAILED tests/test_pipeline_check.py::test_rename_out_of_code_path_is_flagged
    FAILED tests/test_pipeline_check.py::test_research_code_cutoff_missing_not_checked
    FAILED tests/test_pipeline_check.py::test_py_added_to_completed_item_is_untracked
    FAILED tests/test_pipeline_check.py::test_unrelated_root_in_full_clone_stays_loud
== drop (real and real[2]): 3 failed, 417 passed in 57.60s
    FAILED tests/test_real_data_field.py::test_t19_main_exits_1_when_git_log_fails
    FAILED tests/test_real_data_field.py::test_t20_main_exits_1_for_triggered_id_without_request
== drop (uncommitted and uncommitted[1]): 2 failed, 418 passed in 59.20s
    FAILED tests/test_pipeline_check.py::test_uncommitted_step_without_logs_folder_is_listed
== drop isinstance(branches, str): 2 failed, 418 passed in 58.97s
    FAILED tests/test_pipeline_check.py::test_branch_list_failure_exits_1
== drop branch_errors: 7 failed, 413 passed in 61.70s (0:01:01)
    FAILED tests/test_pipeline_check.py::test_branch_diff_failure_is_branch_error
    FAILED tests/test_pipeline_check.py::test_branch_show_failure_skips_classify
    FAILED tests/test_pipeline_check.py::test_unrelated_branch_with_work_is_branch_error
    FAILED tests/test_pipeline_check.py::test_unrelated_branch_each_checked_group_is_branch_error
    FAILED tests/test_pipeline_check.py::test_merge_base_die_is_branch_error
    FAILED tests/test_pipeline_check.py::test_shallow_three_readers_not_checked
== drop isinstance(ahead, str): 3 failed, 417 passed in 56.68s
    FAILED tests/test_pipeline_check.py::test_main_ref_lookup_failure_exits_1
    FAILED tests/test_pipeline_check.py::test_main_ahead_count_failure_exits_1
== drop batch["flagged"]: 3 failed, 417 passed in 57.38s
    FAILED tests/test_pipeline_check.py::test_batch_083_shape_is_flagged
    FAILED tests/test_pipeline_check.py::test_round_bound_end_to_end
== drop env_failed: 2 failed, 418 passed in 53.38s
    FAILED tests/test_pipeline_check.py::test_anchor_env_failure_exits_1
== drop unreadable: 7 failed, 413 passed in 53.09s
    FAILED tests/test_pipeline_check.py::test_unreadable_log_exits_1_alone
    FAILED tests/test_pipeline_check.py::test_unreadable_log_directory
    FAILED tests/test_pipeline_check.py::test_unreadable_request
    FAILED tests/test_pipeline_check.py::test_unreadable_cleared_between_runs
    FAILED tests/test_pipeline_check.py::test_unreadable_07
    FAILED tests/test_pipeline_check.py::test_unreadable_request_still_clashes
== drop inbox_bad return 1: 16 failed, 404 passed in 55.07s
    FAILED tests/test_pipeline_check.py::test_inbox_heading_missing_fails
    FAILED tests/test_pipeline_check.py::test_inbox_hub_line_without_sha_fails
    FAILED tests/test_pipeline_check.py::test_inbox_project_inbox_line_missing_fails
    FAILED tests/test_pipeline_check.py::test_inbox_hub_line_outside_section_fails
    FAILED tests/test_pipeline_check.py::test_inbox_code_words_mid_line_fail
    FAILED tests/test_pipeline_check.py::test_inbox_heading_mid_line_fails
    FAILED tests/test_pipeline_check.py::test_inbox_unfilled_template_fails
    FAILED tests/test_pipeline_check.py::test_inbox_new_report_after_template_change_still_checked
    FAILED tests/test_pipeline_check.py::test_inbox_uncommitted_report_uses_working_template
    FAILED tests/test_pipeline_check.py::test_inbox_hub_value_not_a_sha_fails[116c68]
    FAILED tests/test_pipeline_check.py::test_inbox_hub_value_not_a_sha_fails[2026-11-18]
    FAILED tests/test_pipeline_check.py::test_inbox_hub_value_not_a_sha_fails[116c68c533cbd9d13bf3e81c1d833ab408102f84a]
    FAILED tests/test_pipeline_check.py::test_all_git_fails_no_line_says_none
    FAILED tests/test_pipeline_check.py::test_malformed_shallow_real_git_nothing_none
    FAILED tests/test_pipeline_check.py::test_unreadable_printed_before_inbox_early_return
```
No term has `none found`, so A1 has no exit-term follow-up to open. 091 added no test for `env_failed` or `unreadable` (088/089 asks).

## Changes made (file: what changed)
Commit (A), steps 1-3, tests only:
- tests/test_pipeline_check.py:
  - step 1: `UNRELATED_GROUPS` (the 8 orphans of 04's table) and `test_unrelated_branch_each_checked_group_is_branch_error` (one `_run`, exit 1, the 8 exact BRANCH ERROR lines, `merge-base --all HEAD origin/w` returncode 1); `test_rule_path_files_are_inside_research_code_dirs` (premise of the equivalent mutant, with its reason in the docstring). R2-c is unchanged.
  - step 2: `test_branch_list_failure_exits_1` (A8), `test_main_ref_lookup_failure_exits_1` (A9a), `test_main_ahead_count_failure_exits_1` (A9b), `test_next_id_branch_listing_failure_refuses` (A13). Each runs its unpatched control first with the same args (`cp.main([...]) == 0`, or `--next-id` printing `041\n`), then patches exactly one tuple via `_patched_git`.
- tests/test_probe_guardrails.py: `test_recorded_with_trailing_text_is_unreadable` (M11) and `test_recorded_trailing_newline_is_unreadable` (M11b). scripts/probe_guardrails.py is unchanged (`fullmatch`; no `prefixmatch`).

Commit (B), steps 4, 5a, 5b and 7 (plus the 088 A1 docstring wording):
- .claude/commands/run-item.md, .claude/commands/daily-audit.md, .claude/agents/a1-auditor.md and the `UNSHALLOW` test constant (step 4): 090's list becomes `... REAL-DATA FIELD, LOG TIME, MAIN AHEAD, OPEN BRANCHES and RULE NOT SEEN as 'not checked', never 'none' (items 079, 084, 090).` (04's text was written before 090; RULE NOT SEEN is added to 090's list as 04 says.) `test_unshallow_sentence_same_in_three_files` gains `assert "RULE NOT SEEN" in UNSHALLOW`. INBOX, 088's unborn/verify forms and 089's UNREADABLE stay out.
- templates/build-report.md, templates/verification.md (step 5a): the round-heading line directly under `## Test output (pasted, not summarized)` / `## Tests re-run (output)`. Test `test_round_heading_template_lines`.
- scripts/check_pipeline.py (step 5b):
  - `ROUND_HEADING_FROM = 92` (after TIMED_FROM, with its reason comment); `RUN_HEADING = {"05": r"## Test output\b", "06": r"## Tests re-run\b"}` (the openers, now read by `batch_log_items` from this dict, so the check and LOG BATCH share one source, "never retyped"); `STRAY_RUN_HEADING` as 04 gives it, used with `.match`.
  - `_section_flags(rows, heading)`: the open/close rule moved out of `_run_seconds`; `_run_seconds` now zips its rows with these flags (no behaviour change: the whole-output diff below is identical, and every LOG BATCH test passes).
  - `stray_run_headings(path, opener) -> (headings, why)` via `_read(path, missing_ok=True)`.
  - `incomplete()`: for ID >= ROUND_HEADING_FROM, 05 and 06 each give at most one entry `<step> heading '<h>'[, '<h>'] is not read by LOG BATCH; use '## Test output (round N, pasted)' / '## Tests re-run (round N)' (item 091)`, gated by `_rule_seen(item_dir, step, "ROUND_HEADING_FROM", env)` exactly as SUITE_FROM (not_seen row `(ID, step, sha7, "ROUND_HEADING_FROM", "091", "no round-heading check")`); an unreadable file is `<step> round headings not checked (<why>; item 091)`. The joined text is built outside the f-string (no backslash in an f-string expression: Python 3.10/3.11, RI-008).
  - Docstrings: module LOG BATCH paragraph (item 091, gap w, residuals), `incomplete()`, the RULE NOT SEEN cost note (5 pairs from 092), and `_anchor_env` (see the extra doc fix below). No `_git(` call and no raw read added: GIT_CENSUS stays 47, the read census stays 2 (both tests pass).
- tests/test_pipeline_check.py (5a, 5b, 7): `test_round_heading_template_lines`; `test_stray_round_heading_is_incomplete[P1,P2,P3]` (P1 also asserts `_run_seconds` reads no time under it); `test_stray_round_headings_one_entry_per_file`; `test_read_or_unnamed_heading_is_not_stray[N1,N2,N3,N4]` (N1 also asserts `_run_seconds` reads its time); `test_unreadable_05_round_headings_not_checked` (U); `test_round_heading_gate_follows_rule_file_of_05_commit[G-not-seen,G-seen]`; `test_section_flags_match_run_seconds_rule`; `SCRATCH` and `test_scratch_sentence_same_in_four_files`. Two 089 tests updated (Deviations 2).
- .claude/commands/run-item.md (end of the scratch/realtest paragraph), .claude/agents/i2-builder.md (after its scratch-copy line), .claude/agents/i3-verifier.md (after its RI-002 scratch-copy sentence), .claude/agents/a1-auditor.md (new line before "Write the daily report"): the SCRATCH sentence, once each (step 7). Text only: no check can see a real collision of two agents' dirs.
Commit (C), step 6 (made with scripts/commit_step.py itself):
- scripts/commit_step.py (new): `run`, `filter_log`, `_git`, `_log_blobs`, `commit`, `main`, as 04 step 6 (i)-(vi). Imports `LOG_LINE` from check_pipeline via `sys.path.insert`, as check_handoff does. Log files are read with `read_bytes()` and decoded strictly. The temp index is `tempfile.mkstemp(dir=<rev-parse --absolute-git-dir>)`, deleted in `finally`; `read-tree <old>` is its first command (t1009).
- tests/test_commit_step.py (new): T1, T2, T3 (8 parametrized refusals + HEAD-moved + 4 patched git failures + no git / not a repo + unborn HEAD), T4, T5, `test_filter_log_rule`, and `test_commit_rule_texts` (run-item sentence and the 2 pointers, count == 1 each). Real git, skipped without it, same identity env as test_pipeline_check's `_git`.
- .claude/commands/run-item.md: the step-6 sentence directly after the item-082 subject sentence (which stays byte-identical; its pin test passes).
- .claude/agents/i2-builder.md and .claude/agents/i3-verifier.md: one pointer line each, appended to the log-line paragraph.
- Review after the restart: the uncommitted versions of these 5 files (left by the cut-off I2 run) were re-read against 04 before this commit. They match 04, with the additions listed in Deviations 6; no edit was needed, and they were not trusted blindly: all 21 tests pass and every step-6 mutant below fails.

- Extra doc fix (088 A1, logs/audit/2026-11-21-088.md "New-item findings" 1): the `_anchor_env` docstring now says UNCOMMITTED STEP's `ls-tree HEAD` fails "non-zero; 128 measured on a corrupt ref and a dangling symbolic HEAD", and that both cases print `not checked (unborn HEAD)`, a label that is not accurate for the second. Wording only. The label change (`HEAD names no commit (unborn or unresolvable)`) and the corrupt-ref test pin A1 suggests are new output text, so they are left for a follow-up item (named in Deviations 4).

## Real-tree run of the stray-heading walker (step 5b, cutoff ignored; REPL on the working tree, 2026-11-22)
```
070/06: ### Tests re-run (round 3)
077/06: ### Tests re-run (output)
079/05: ### Test output (pasted, not summarized)
079/06: ### Tests re-run (output)
081/05: ### Test output (round 2, pasted)
082/05: ### Tests re-run (output)
082/06: ### Tests re-run (output)
084/05: ## Round 2 test output (pasted)
084/06: ### Tests re-run (output)
086/05: ### Test output (round 2, pasted)
087/05: ### Test output (round 2, pasted)
total 11 items 8 ['070', '077', '079', '081', '082', '084', '086', '087']
```
Matched to 03 by file and line (grep `-iE '^#{1,6} (round [0-9]+ )?(test output|tests re-run)'`, minus the two openers): 070/06 L209, 077/06 L115, 079/05 L45, 079/06 L140, 081/05 L320, 082/05 L461, 082/06 L181, 084/05 L205, 084/06 L150, 086/05 L320: exactly 03's 10 headings in 7 items. The 11th, 087/05 L237 `### Test output (round 2, pasted)`, is in a file R3 could not count: `git log -L` gives 7389962 (2026-11-22T01:00:20Z, 087's round-2 I2 commit), after 03's check_handoff run (2026-11-21 23:43 UTC). The expectation was not adjusted: this is reported as Deviations 1 for I3. 087 < 92, so it gets no entry.

## Whole-output diff of check_pipeline.py before and after (B) (RI-013)
Same working tree, same args (none), base script = `git show 8a8bd33:scripts/check_pipeline.py`:
```
before exit 1
after exit 1
IDENTICAL
 112 /tmp/claude-0/scratch/i2-091/cpB_after.txt
 112 /tmp/claude-0/scratch/i2-091/cpB_before.txt
```
Both exit 1 only because of `INCOMPLETE: 091 (no log line for I2)`: (A) committed 05 before the I2 log line, which is written right after this 05 is final (commit C). Probe: the same script with `ROUND_HEADING_FROM = 0` on the same tree changes exactly one line, RULE NOT SEEN, which gains 070, 077, 079, ... with `without ROUND_HEADING_FROM (091): judged by no round-heading check` (their anchors predate the constant), so `test_repo_pipeline_has_no_skipped_items`'s exact RULE NOT SEEN assert kills the cutoff-0 mutant on the real tree.

## Mutation probes, commit (B) (scratch worktree at 8a8bd33 + the (B) files; whole tests/test_pipeline_check.py each; one after another)
`test_repo_pipeline_has_no_skipped_items` fails in every row, mutant or not, because the scratch HEAD 8a8bd33 has 091's 05 and no I2 line (the same transient INCOMPLETE as above); the named tests are the killers.
```
== 4a old sentence in run-item only: 2 failed, 379 passed in 32.89s
    FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
    FAILED tests/test_pipeline_check.py::test_unshallow_sentence_same_in_three_files
== 4b RULE NOT SEEN removed from all 4: 2 failed, 379 passed in 32.31s
    FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
    FAILED tests/test_pipeline_check.py::test_unshallow_sentence_same_in_three_files
== 5a template line deleted (build-report): 2 failed, 379 passed in 33.37s
    FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
    FAILED tests/test_pipeline_check.py::test_round_heading_template_lines
== 5a template line deleted (verification): 2 failed, 379 passed in 36.23s
    FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
    FAILED tests/test_pipeline_check.py::test_round_heading_template_lines
== 5b check removed: 10 failed, 371 passed in 34.45s
    FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
    FAILED tests/test_pipeline_check.py::test_unreadable_06
    FAILED tests/test_pipeline_check.py::test_unreadable_05_at_suite_check
    FAILED tests/test_pipeline_check.py::test_stray_round_heading_is_incomplete[P1]
    FAILED tests/test_pipeline_check.py::test_stray_round_heading_is_incomplete[P2]
    FAILED tests/test_pipeline_check.py::test_stray_round_heading_is_incomplete[P3]
    FAILED tests/test_pipeline_check.py::test_stray_round_headings_one_entry_per_file
    FAILED tests/test_pipeline_check.py::test_unreadable_05_round_headings_not_checked
    FAILED tests/test_pipeline_check.py::test_round_heading_gate_follows_rule_file_of_05_commit[G-not-seen]
    FAILED tests/test_pipeline_check.py::test_round_heading_gate_follows_rule_file_of_05_commit[G-seen]
== 5b ### only: 3 failed, 378 passed in 33.35s
    FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
    FAILED tests/test_pipeline_check.py::test_stray_round_heading_is_incomplete[P2]
    FAILED tests/test_pipeline_check.py::test_stray_round_headings_one_entry_per_file
== 5b inside-section exemption removed: 2 failed, 379 passed in 33.58s
    FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
    FAILED tests/test_pipeline_check.py::test_read_or_unnamed_heading_is_not_stray[N1-inside-section]
== 5b .search: 2 failed, 379 passed in 35.81s
    FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
    FAILED tests/test_pipeline_check.py::test_read_or_unnamed_heading_is_not_stray[N2-not-at-start]
== 5b cutoff 0: 2 failed, 379 passed in 34.29s
    FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
    FAILED tests/test_pipeline_check.py::test_read_or_unnamed_heading_is_not_stray[N3-below-cutoff]
== 5b gate removed: 2 failed, 379 passed in 34.80s
    FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
    FAILED tests/test_pipeline_check.py::test_round_heading_gate_follows_rule_file_of_05_commit[G-not-seen]
== 5b _section_flags closer #{1,3}: 3 failed, 378 passed in 34.79s
    FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
    FAILED tests/test_pipeline_check.py::test_read_or_unnamed_heading_is_not_stray[N1-inside-section]
    FAILED tests/test_pipeline_check.py::test_section_flags_match_run_seconds_rule
== 5b opener not excluded: 18 failed, 363 passed in 34.01s
    (16 existing LOG BATCH / RULE NOT SEEN / Suite tests whose 150/151/990/999 fixtures have a `## Test output` opener, plus N1 and N4)
== 7 SCRATCH removed from a1-auditor: 2 failed, 379 passed in 36.03s
    FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
    FAILED tests/test_pipeline_check.py::test_scratch_sentence_same_in_four_files
== 7 SCRATCH removed from i3-verifier: 2 failed, 379 passed in 36.83s
    FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
    FAILED tests/test_pipeline_check.py::test_scratch_sentence_same_in_four_files
```
04's row "`_section_flags` closer `#{1,3} ` → N1 and an existing LOG BATCH test": N1 and the new `test_section_flags_match_run_seconds_rule` fail; no pre-existing LOG BATCH test failed (their fixtures have no `###` line inside a read section). Reported, not adjusted.

## Mutation probes, commit (A) (scratch worktree /tmp/claude-0/scratch/i2-091/wt at eb57a85 + the (A) test files; run one after another)
```
== A1 drop *RESEARCH_CODE_PATHS: 1 failed, 4 passed, 362 deselected in 1.79s
    FAILED tests/test_pipeline_check.py::test_unrelated_branch_each_checked_group_is_branch_error
== A2 drop *RULE_PATHS: 1 failed, 4 passed, 362 deselected in 1.70s
    FAILED tests/test_pipeline_check.py::test_unrelated_branch_each_checked_group_is_branch_error
== A3 drop RECURRING: 1 failed, 4 passed, 362 deselected in 1.85s
    FAILED tests/test_pipeline_check.py::test_unrelated_branch_each_checked_group_is_branch_error
== drop work/: 2 failed, 3 passed, 362 deselected in 1.89s
    FAILED tests/test_pipeline_check.py::test_unrelated_branch_with_work_is_branch_error
    FAILED tests/test_pipeline_check.py::test_unrelated_branch_each_checked_group_is_branch_error
== drop templates/ (RULE_PATHS): 1 failed, 4 passed, 362 deselected in 1.87s
    FAILED tests/test_pipeline_check.py::test_unrelated_branch_each_checked_group_is_branch_error
== drop scripts/ (RESEARCH_CODE_PATHS): 2 failed, 3 passed, 362 deselected in 1.87s
    FAILED tests/test_pipeline_check.py::test_unrelated_branch_each_checked_group_is_branch_error
    FAILED tests/test_pipeline_check.py::test_rule_path_files_are_inside_research_code_dirs
== drop scripts/check_pipeline.py from ls-tree (equivalent): 5 passed, 362 deselected in 1.74s
== A8 drop isinstance(branches, str): 1 failed, 366 passed in 38.82s
    FAILED tests/test_pipeline_check.py::test_branch_list_failure_exits_1
== A9 drop isinstance(ahead, str): 2 failed, 365 passed in 37.66s
    FAILED tests/test_pipeline_check.py::test_main_ref_lookup_failure_exits_1
    FAILED tests/test_pipeline_check.py::test_main_ahead_count_failure_exits_1
== A13 listing empty on failure: 1 failed, 366 passed in 38.61s
    FAILED tests/test_pipeline_check.py::test_next_id_branch_listing_failure_refuses
== M11 fullmatch -> match: 2 failed, 14 passed in 7.58s
    FAILED tests/test_probe_guardrails.py::test_recorded_with_trailing_text_is_unreadable
    FAILED tests/test_probe_guardrails.py::test_recorded_trailing_newline_is_unreadable
== M11b match + $: 1 failed, 15 passed in 6.68s
    FAILED tests/test_probe_guardrails.py::test_recorded_trailing_newline_is_unreadable
```
The `-k` filter for the step-1 rows was `each_checked_group or rule_path_files or unrelated`; step 2 and 3 rows ran the whole test file. The equivalent mutant (only `scripts/check_pipeline.py` dropped from the ls-tree) survives, as 04 expects; its premise is pinned by `test_rule_path_files_are_inside_research_code_dirs`, which the `scripts/` drop fails.

## Mutation probes, commit (C) (scratch worktree /tmp/claude-0/scratch/i2-091b/wt at 8dec4f6 + the (C) files; tests/test_commit_step.py each; one after another)
```
== M1 shared index (no GIT_INDEX_FILE): 3 failed, 18 passed in 1.40s
    FAILED tests/test_commit_step.py::test_t1_commits_only_own_line_and_named_path
    FAILED tests/test_commit_step.py::test_t3_head_moved_is_refused - assert ('0a...
    FAILED tests/test_commit_step.py::test_t3_git_failure_is_refused[write-tree]
== M2 whole log staged: 2 failed, 19 passed in 1.27s
    FAILED tests/test_commit_step.py::test_t1_commits_only_own_line_and_named_path
    FAILED tests/test_commit_step.py::test_t4_new_log_file_is_staged - AssertionE...
== M3 append instead of order: 1 failed, 20 passed in 1.53s
    FAILED tests/test_commit_step.py::test_t2_second_item_keeps_working_order - A...
== M4 update-ref without old: 1 failed, 20 passed in 1.31s
    FAILED tests/test_commit_step.py::test_t3_head_moved_is_refused - AssertionEr...
== M5 whole-file fallback: 2 failed, 19 passed in 1.60s
    FAILED tests/test_commit_step.py::test_t3_refusals_write_nothing[edited-head-line]
    FAILED tests/test_commit_step.py::test_filter_log_rule - Failed: DID NOT RAIS...
== M6 subject check off: 1 failed, 20 passed in 1.38s
    FAILED tests/test_commit_step.py::test_t3_refusals_write_nothing[wrong-subject]
== M7 update-index before read-tree: 7 failed, 14 passed in 1.53s
    FAILED tests/test_commit_step.py::test_t1_commits_only_own_line_and_named_path
    FAILED tests/test_commit_step.py::test_t2_second_item_keeps_working_order - a...
    FAILED tests/test_commit_step.py::test_t3_head_moved_is_refused - AssertionEr...
    FAILED tests/test_commit_step.py::test_t3_git_failure_is_refused[read-tree]
    FAILED tests/test_commit_step.py::test_t3_git_failure_is_refused[write-tree]
    FAILED tests/test_commit_step.py::test_t4_new_log_file_is_staged - AssertionE...
    FAILED tests/test_commit_step.py::test_t5_reset_failure_exits_1_after_commit
== 6 text: .claude/commands/run-item.md reverted: 1 failed, 20 passed in 1.54s
    FAILED tests/test_commit_step.py::test_commit_rule_texts - assert 0 == 1
== 6 text: .claude/agents/i2-builder.md reverted: 1 failed, 20 passed in 1.44s
    FAILED tests/test_commit_step.py::test_commit_rule_texts - AssertionError: i2...
== 6 text: .claude/agents/i3-verifier.md reverted: 1 failed, 20 passed in 1.59s
    FAILED tests/test_commit_step.py::test_commit_rule_texts - AssertionError: i3...
```
M7's T1 error, as printed: `commit_step refused: git update-index failed (exit 128); nothing committed (item 091)`; the same command by hand on an empty mktemp index: `fatal: /tmp/claude-0/scratch/i2-091b/tmp.BaGi4uJcmN: index file smaller than expected`, exit 128 (t1009's case). M1 (shared index) fails T1 on `x.txt` being committed, as 04 names.

## Connectivity check
- [x] every new function/rule is used: `_section_flags` (by `_run_seconds` and `stray_run_headings`), `stray_run_headings` (by `incomplete()`), `ROUND_HEADING_FROM`, `RUN_HEADING`, `STRAY_RUN_HEADING` (by `incomplete()` / `batch_log_items`); commit_step's `run`, `filter_log`, `_git`, `_log_blobs`, `commit`, `main` (by the CLI and tests/test_commit_step.py); commit_step is named by run-item.md and the 2 agent pointers, and makes this item's commit (C).
- [x] every input has a source, every output has a consumer: stray headings → INCOMPLETE entry (exit 1); unreadable 05/06 → `not checked (...)` entry + UNREADABLE line; gate → RULE NOT SEEN row; commit_step → the commit, its stdout `<sha7> <subject>`, or a stderr refusal with exit 2/1.
- [x] every branch ends in a defined result: absent 05/06 → no entry (nothing to read); unreadable → `not checked`; ID < 92 → not evaluated (cutoff, test N3); commit_step: no git / not top / unborn / bad ID / no path / missing / directory / log path / non-UTF-8 / changed HEAD lines / batch / wrong subject / any git failure / HEAD moved → exit 2, nothing written; reset failure → exit 1 naming the command; success → exit 0.
- [x] no leftover TODOs or unused files: `grep -n TODO scripts/commit_step.py tests/test_commit_step.py` prints nothing; the scratch worktree is removed after the probes.

Missing-data policy (grep run 2026-11-22 on this tree): `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/` gives 38 hits, none new or changed (`git diff --stat 7e537c2 -- ccbot/ config/ data/` is empty). The same grep over 091's new script: `scripts/commit_step.py:118: if (head is not None and new != head) or (head is None and mine):`. Reason: `head is None` means ls-tree answered "not in HEAD" (exit 0, empty), a real answer; that file is staged only if it gains this item's line, and a failed ls-tree is a refusal, never None. The `"100644"` mode is used only for a file not in HEAD (git's mode for a new regular file), never for a failed read. No dataclass is added. The only comparisons are `len(own) > 1` and `ptr < len(hl)` on ints (no NaN possible).

Feasibility numbers (04 Guardrail tests), as measured: step 1, 8 BRANCH ERROR lines in one run (test passes; A1/A2/A3 each fail it); step 2, A8 control exit 0 then 1; step 5b, 11 headings in 8 items at cutoff 0 (03 said 10/7; Deviations 1), 0 items >= 92, whole-output diff IDENTICAL; step 6 T1, 4 of 5 lines kept (test passes).

## Test output (pasted, not summarized)
Each later round's runs go under their own level-2 heading `## Test output (round N, pasted)`, never under a `###` heading or a `Round N ...` heading (item 091).

`python3 -m pytest -q` from the repo root, at 8dec4f6 (B) with the (C) files and this 05 in the working tree, before the I2 log line was written (whole output):
```
........................................................................ [  8%]
..................................................................s..... [ 17%]
........................................................................ [ 26%]
..........................F............................................. [ 35%]
........................................................................ [ 44%]
........................................................................ [ 53%]
........................................................................ [ 62%]
........................................................................ [ 71%]
........................................................................ [ 80%]
........................................................................ [ 89%]
........................................................................ [ 98%]
..............                                                           [100%]
=================================== FAILURES ===================================
___________________ test_repo_pipeline_has_no_skipped_items ____________________

tmp_path = PosixPath('/tmp/pytest-of-root/pytest-280/test_repo_pipeline_has_no_skip0')

    @NO_GIT
    def test_repo_pipeline_has_no_skipped_items(tmp_path):
        """The committed work/ folder: no item may skip a step (RI-007). Runs on a detached worktree of
        HEAD, so another item's uncommitted step files in this tree don't fail it (item 066); run
        check_pipeline.py in the tree for uncommitted files (run-item.md)."""
        flag = subprocess.run(["git", "rev-parse", "--is-shallow-repository"], cwd=REPO, capture_output=True,
                              text=True, encoding="utf-8")
        if flag.returncode != 0 or flag.stdout.strip() != "false":
            pytest.skip("REPO is a shallow clone: 083 is judged strictly (item 084); run git fetch --unshallow")
        code, out = _run_head(REPO, tmp_path, "check_pipeline.py")
>       assert code == 0, out
E       AssertionError: 001: LEGACY (RESEARCH ONLY before 07-audit-task existed (item 021))
E         002: complete (FULL)
E         003: complete (FULL)
E         004: LEGACY (07 is combined in work/003/07-audit-task.md)
E         005: LEGACY (07 is combined in work/003/07-audit-task.md)
E         006: LEGACY (07 is combined in work/003/07-audit-task.md)
E         007: LEGACY (07 is combined in work/003/07-audit-task.md)
E         008: LEGACY (07 is combined in work/003/07-audit-task.md)
E         009: complete (FULL)
E         010: complete (FULL)
E         011: complete (FULL)
E         012: complete (FULL)
E         013: complete (FULL)
E         014: complete (FULL)
E         015: complete (FULL)
E         016: complete (FULL)
E         017: complete (FULL)
E         018: complete (FULL)
E         019: complete (FULL)
E         020: complete (FULL)
E         021: complete (FULL)
E         022: complete (FULL)
E         023: complete (RESEARCH ONLY; Waived: 02 (A1, 2026-10-31, item 026: the screen was already delivered; R3's fact check was run afterwards in 026; the person can ask for the R2 language search))
E         024: complete (FULL; Waived: 01 02 03 04 (person, 2026-10-31: approved by merging PR #6, which asked for this waiver by name. Written by A1 in item 026: built and merged before the step check existed; the rule is the person's own decision in 001; I3 ran afterwards in 026. Who-field updated in item 031.))
E         025: complete (FULL)
E         026: complete (FULL)
E         027: complete (FULL)
E         028: complete (FULL)
E         029: complete (FULL)
E         030: complete (FULL)
E         031: complete (FULL)
E         032: complete (FULL)
E         033: complete (FULL)
E         034: complete (FULL)
E         035: complete (FULL)
E         036: complete (FULL)
E         037: complete (FULL)
E         038: complete (FULL)
E         039: complete (FULL)
E         040: complete (FAST)
E         041: complete (FULL)
E         042: complete (FULL)
E         043: complete (FULL)
E         044: complete (FULL)
E         045: complete (FULL)
E         046: complete (FULL)
E         047: complete (FULL)
E         048: complete (FULL)
E         049: complete (FULL)
E         050: complete (FULL)
E         051: complete (FULL)
E         052: complete (FULL)
E         053: complete (FULL)
E         054: complete (FULL)
E         055: complete (FULL)
E         056: complete (FULL)
E         057: complete (RESEARCH ONLY)
E         058: complete (FULL)
E         059: complete (FULL)
E         060: complete (FULL)
E         061: complete (FULL)
E         062: complete (FULL)
E         063: complete (FULL)
E         064: complete (FULL)
E         065: complete (FULL)
E         066: complete (FULL)
E         067: complete (FULL)
E         068: complete (FULL)
E         069: complete (FULL)
E         070: complete (FULL)
E         071: complete (FULL)
E         072: complete (FULL)
E         073: complete (FULL)
E         074: complete (FULL)
E         075: complete (FULL)
E         076: complete (FULL)
E         077: complete (FULL)
E         078: complete (FULL)
E         079: complete (FULL)
E         080: complete (FULL)
E         081: complete (FULL)
E         082: complete (FULL)
E         083: complete (FULL)
E         084: complete (FULL)
E         085: complete (FULL)
E         086: complete (FULL)
E         087: complete (FULL)
E         088: complete (FULL)
E         089: complete (FULL)
E         090: complete (FULL)
E         091: in progress (FULL: next 06)
E         STUCK: none
E         AWAITING A1: none
E         IN PR: none
E         OPEN BRANCHES (not merged into HEAD):
E           origin/claude/project-thread-f64g3k: items none; merges cleanly; last commit 2026-11-21 (1 days)
E         RULES BRANCH: none
E         ID CLASH: none
E         I3 FAIL: none
E         A1 FAIL: none
E         INCOMPLETE: 091 (no log line for I2)
E         RULE NOT SEEN: 083 (05 added in cfc0634 without TESTS_FORMAT_FROM (076): judged by I2_BEFORE; 06 added in cfc0634 without VERDICT_FROM (071): judged by no Sent-back check; item 084)
E         LOG TIME: none (not checked: 048: built before 045's --log rule reached main; times typed by hand, not recoverable (item 049))
E         LOG BATCH: none (not checked: 083: six lines written in one batch at 10:15 after the build (commit cfc0634 10:15:48); real times not recoverable (item 086)); not computable: 048: no pytest time in 05/06/I2 line; 054: no pytest time in 05/06/I2 line; 055: no pytest time in 05/06/I2 line; 056: no pytest time in 05/06/I2 line; 058: no pytest time in 05/06/I2 line; 059: no pytest time in 05/06/I2 line; 060: no pytest time in 05/06/I2 line
E         UNTRACKED CHANGE: none
E         RESEARCH CODE: none
E         REAL-DATA FIELD: none
E         UNCOMMITTED STEP: none
E         ORPHAN LOG: none
E         UNREADABLE: none
E         INBOX: not checked (2026-11-21.md added in 0d94a94; its templates/daily-audit.md has no ## Inbox)
E         SKIPPED: none
E         
E       assert 1 == 0

tests/test_pipeline_check.py:182: AssertionError
=========================== short test summary info ============================
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 804 passed, 1 skipped in 107.81s (0:01:47)
```
The one failure is `test_repo_pipeline_has_no_skipped_items`, from `INCOMPLETE: 091 (no log line for I2)`: the I2 line can only be written after this run, since its `tests` field is this run's last line (the same transient state as 087's I2 line `1 failed, 761 passed, 1 skipped`). No `I3 FAIL:` / `A1 FAIL:` item is open (`I3 FAIL: none`, `A1 FAIL: none`).

Round 1's `Suite:` line (replaced by round 2's below): 1 failed, 804 passed, 1 skipped in 107.81s (0:01:47)

Other checks:
```
$ for f in scripts/check_pipeline.py scripts/commit_step.py tests/test_pipeline_check.py tests/test_probe_guardrails.py tests/test_commit_step.py; do python3.11 -m py_compile $f && echo "ok $f"; done
ok scripts/check_pipeline.py
ok scripts/commit_step.py
ok tests/test_pipeline_check.py
ok tests/test_probe_guardrails.py
ok tests/test_commit_step.py
$ python3 -m pytest -q tests/test_commit_step.py
21 passed in 1.31s
$ python3 scripts/check_pipeline.py > out.txt; echo "exit $?"   (after the I2 --log line, before commit C)
exit 0
$ grep -nE "091|INCOMPLETE|FAIL:|UNTRACKED|LOG TIME|LOG BATCH|SKIPPED" out.txt
91:091: in progress (FULL: next 06)
99:I3 FAIL: none
100:A1 FAIL: none
101:INCOMPLETE: none
103:LOG TIME: none (not checked: 048: built before 045's --log rule reached main; times typed by hand, not recoverable (item 049))
104:LOG BATCH: none (not checked: 083: six lines written in one batch at 10:15 after the build (commit cfc0634 10:15:48); real times not recoverable (item 086)); not computable: 048: no pytest time in 05/06/I2 line; 054: no pytest time in 05/06/I2 line; 055: no pytest time in 05/06/I2 line; 056: no pytest time in 05/06/I2 line; 058: no pytest time in 05/06/I2 line; 059: no pytest time in 05/06/I2 line; 060: no pytest time in 05/06/I2 line
105:UNTRACKED CHANGE: none
112:SKIPPED: none
```
091 shows no INCOMPLETE or SKIPPED, and LOG TIME and LOG BATCH do not name it. Before the I2 line the same run gave exit 1 with only `INCOMPLETE: 091 (no log line for I2)`.

## Round 2 (I3 FAIL round 1: 06 F1, F2, F3)
Base of round 2: d39d811 (`Item 091: 02:28 | I3 | 091 | FAIL | sent to audit: no`), on daily-fixes/2026-11-21. Scratch dir made with `mktemp -d /tmp/claude-0/scratch/i2-091r2-XXXX` → `/tmp/claude-0/scratch/i2-091r2-LpYi` (worktree `wt` of d39d811 + the 2 round-2 files; removed after the probes, `git worktree list` shows only the main checkout, `git stash list | wc -l` gives 0). No `git stash` used.

### Changes made, round 2 (file: what changed)
- scripts/commit_step.py (F1): new `repo_relative(p, top)`: the named path is made absolute from the cwd (`os.path.abspath`), its parent directory resolved (`.resolve()`, the name itself is not, so a named symlink stays a symlink), then `relative_to(top)`; outside the top → Refused `<p> is outside the repo top; name files inside it (item 091)`. `commit()` keeps the resolved top (`topdir`) from `rev-parse --show-toplevel` and runs every named path through `repo_relative` before the log-dir, missing and directory checks; `update-index` and the closing `reset` get that relative form. Module text (i) says so.
- tests/test_commit_step.py (F1, F2): 6 new test cases:
  - `test_t3_absolute_log_path_is_refused[with-own-line]` and `[no-own-line]` (absolute log path refused, `rev-parse HEAD` and `.git/index` bytes unchanged; `no-own-line` is I3's probe B shape: the working log gains only 151's line);
  - `test_t3_absolute_named_path_is_committed_relative` (absolute non-log path accepted, committed as `work/150/05-build-report.md`, x.txt still staged and out of the commit);
  - `test_t3_absolute_path_through_symlinked_dir` (absolute path through a symlink to the repo: inside, committed relative);
  - `test_t3_path_outside_repo_is_refused[absolute]` and `[relative]` (`../outside.md`);
  - `test_filter_log_pattern_inside_other_text` (F2: `01:05 | I2 | 151 | see 150 | I3 | 150 | x` dropped and not 150's; `note: 01:06 | I2 | 151 | quoted` kept and not counted; `own == [L150]`).
- work/091/05-build-report.md (F3): this section, Deviations 9-11, round 1's `Suite:` line moved out of column 0.

### Mutation probes, round 2 (scratch worktree above; whole tests/test_commit_step.py each; one after another, file restored after each)
```
== F1-noresolve: 4 failed, 24 passed in 1.87s
    FAILED tests/test_commit_step.py::test_t3_absolute_log_path_is_refused[with-own-line]
    FAILED tests/test_commit_step.py::test_t3_absolute_log_path_is_refused[no-own-line]
    FAILED tests/test_commit_step.py::test_t3_path_outside_repo_is_refused[absolute]
    FAILED tests/test_commit_step.py::test_t3_path_outside_repo_is_refused[relative]
== F1-noparentresolve: 1 failed, 27 passed in 1.83s
    FAILED tests/test_commit_step.py::test_t3_absolute_path_through_symlinked_dir
== F2-search: 28 passed in 1.84s
== F2-search-noanchor: 1 failed, 27 passed in 1.99s
    FAILED tests/test_commit_step.py::test_filter_log_pattern_inside_other_text
== F2-substr: 1 failed, 27 passed in 2.03s
    FAILED tests/test_commit_step.py::test_filter_log_pattern_inside_other_text
```
- F1-noresolve: `n = repo_relative(p, topdir)` → round 1's `n = Path(os.path.normpath(p)).as_posix()` (06 F1's mutant row: "resolution removed → the absolute-log row fails"). Killed by both absolute-log rows.
- F1-noparentresolve: `(a.parent.resolve() / a.name).relative_to(top)` → `a.relative_to(top)`. Killed by the symlink row (before that row was added it survived: 27 passed; the row was added for it).
- F2-search: `LOG_LINE.match` → `LOG_LINE.search`. Survives, and is equivalent: LOG_LINE starts with `^` and has no `re.M`, so `.search` can match only at position 0, the same as `.match`.
- F2-search-noanchor: `LOG_LINE.search` with the leading `^` removed (the mutant 06 F2 means: a match anywhere in the line). Killed by the new test (the `note:` line is dropped as 151's).
- F2-substr: owner by `f"| {item} |" in line` instead of group 4. Killed by the new test (the 151 line with `| 150 |` is kept and counted as 150's).
The harness is at /tmp/claude-0/-home-claude/6b779538-e393-5b21-a85a-072369e659f6/scratchpad/i2-091r2-mut.py.

### Connectivity, round 2
- `repo_relative` is called by `commit()` for every named path and reached by the 6 new T3 cases; its Refused ends in exit 2 with nothing written (the T3 asserts check `.git/index` and HEAD).
- `topdir` is the resolved top that the cwd check already compared; no new input.
- `grep -n TODO scripts/commit_step.py tests/test_commit_step.py` prints nothing.
- Missing-data policy: `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/ | wc -l` gives 38, none new (`git diff --stat 7e537c2 -- ccbot/ config/ data/` is empty). The same grep on scripts/commit_step.py gives the round-1 L130 hit (unchanged, reason above). The new `topdir = ... if top[1] == 0 else None` is not a default: None is refused on the next line (`not the top of a git work tree`). No dataclass, no new `>`/`<`.
- `python3.11 -m py_compile` on scripts/commit_step.py and tests/test_commit_step.py: `ok scripts/commit_step.py`, `ok tests/test_commit_step.py`.
- Feasibility (06 F1): I3's probe B shape is the `no-own-line` row; it passes on the fix (exit 2, state unchanged) and fails on F1-noresolve.

## Test output (round 2, pasted)
`python3 -m pytest -q tests/test_commit_step.py`: `28 passed in 1.86s`.

`python3 -m pytest -q` from the repo root, at d39d811 with the 2 round-2 files and this 05 in the working tree, before the I2 log line (whole output, as printed):
```
........................................................................ [  8%]
..................................................................s..... [ 17%]
........................................................................ [ 26%]
.................................F...................................... [ 35%]
........................................................................ [ 44%]
........................................................................ [ 53%]
........................................................................ [ 61%]
........................................................................ [ 70%]
........................................................................ [ 79%]
........................................................................ [ 88%]
........................................................................ [ 97%]
.....................                                                    [100%]
=================================== FAILURES ===================================
___________________ test_repo_pipeline_has_no_skipped_items ____________________

tmp_path = PosixPath('/tmp/pytest-of-root/pytest-338/test_repo_pipeline_has_no_skip0')

    @NO_GIT
    def test_repo_pipeline_has_no_skipped_items(tmp_path):
        """The committed work/ folder: no item may skip a step (RI-007). Runs on a detached worktree of
        HEAD, so another item's uncommitted step files in this tree don't fail it (item 066); run
        check_pipeline.py in the tree for uncommitted files (run-item.md)."""
        flag = subprocess.run(["git", "rev-parse", "--is-shallow-repository"], cwd=REPO, capture_output=True,
                              text=True, encoding="utf-8")
        if flag.returncode != 0 or flag.stdout.strip() != "false":
            pytest.skip("REPO is a shallow clone: 083 is judged strictly (item 084); run git fetch --unshallow")
        code, out = _run_head(REPO, tmp_path, "check_pipeline.py")
>       assert code == 0, out
E       AssertionError: 001: LEGACY (RESEARCH ONLY before 07-audit-task existed (item 021))
E         002: complete (FULL)
E         003: complete (FULL)
E         004: LEGACY (07 is combined in work/003/07-audit-task.md)
E         005: LEGACY (07 is combined in work/003/07-audit-task.md)
E         006: LEGACY (07 is combined in work/003/07-audit-task.md)
E         007: LEGACY (07 is combined in work/003/07-audit-task.md)
E         008: LEGACY (07 is combined in work/003/07-audit-task.md)
E         009: complete (FULL)
E         010: complete (FULL)
E         011: complete (FULL)
E         012: complete (FULL)
E         013: complete (FULL)
E         014: complete (FULL)
E         015: complete (FULL)
E         016: complete (FULL)
E         017: complete (FULL)
E         018: complete (FULL)
E         019: complete (FULL)
E         020: complete (FULL)
E         021: complete (FULL)
E         022: complete (FULL)
E         023: complete (RESEARCH ONLY; Waived: 02 (A1, 2026-10-31, item 026: the screen was already delivered; R3's fact check was run afterwards in 026; the person can ask for the R2 language search))
E         024: complete (FULL; Waived: 01 02 03 04 (person, 2026-10-31: approved by merging PR #6, which asked for this waiver by name. Written by A1 in item 026: built and merged before the step check existed; the rule is the person's own decision in 001; I3 ran afterwards in 026. Who-field updated in item 031.))
E         025: complete (FULL)
E         026: complete (FULL)
E         027: complete (FULL)
E         028: complete (FULL)
E         029: complete (FULL)
E         030: complete (FULL)
E         031: complete (FULL)
E         032: complete (FULL)
E         033: complete (FULL)
E         034: complete (FULL)
E         035: complete (FULL)
E         036: complete (FULL)
E         037: complete (FULL)
E         038: complete (FULL)
E         039: complete (FULL)
E         040: complete (FAST)
E         041: complete (FULL)
E         042: complete (FULL)
E         043: complete (FULL)
E         044: complete (FULL)
E         045: complete (FULL)
E         046: complete (FULL)
E         047: complete (FULL)
E         048: complete (FULL)
E         049: complete (FULL)
E         050: complete (FULL)
E         051: complete (FULL)
E         052: complete (FULL)
E         053: complete (FULL)
E         054: complete (FULL)
E         055: complete (FULL)
E         056: complete (FULL)
E         057: complete (RESEARCH ONLY)
E         058: complete (FULL)
E         059: complete (FULL)
E         060: complete (FULL)
E         061: complete (FULL)
E         062: complete (FULL)
E         063: complete (FULL)
E         064: complete (FULL)
E         065: complete (FULL)
E         066: complete (FULL)
E         067: complete (FULL)
E         068: complete (FULL)
E         069: complete (FULL)
E         070: complete (FULL)
E         071: complete (FULL)
E         072: complete (FULL)
E         073: complete (FULL)
E         074: complete (FULL)
E         075: complete (FULL)
E         076: complete (FULL)
E         077: complete (FULL)
E         078: complete (FULL)
E         079: complete (FULL)
E         080: complete (FULL)
E         081: complete (FULL)
E         082: complete (FULL)
E         083: complete (FULL)
E         084: complete (FULL)
E         085: complete (FULL)
E         086: complete (FULL)
E         087: complete (FULL)
E         088: complete (FULL)
E         089: complete (FULL)
E         090: complete (FULL)
E         091: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))
E         STUCK: none
E         AWAITING A1: none
E         IN PR: none
E         OPEN BRANCHES (not merged into HEAD):
E           origin/claude/project-thread-f64g3k: items none; merges cleanly; last commit 2026-11-21 (1 days)
E         RULES BRANCH: none
E         ID CLASH: none
E         I3 FAIL: 091
E         A1 FAIL: none
E         INCOMPLETE: none
E         RULE NOT SEEN: 083 (05 added in cfc0634 without TESTS_FORMAT_FROM (076): judged by I2_BEFORE; 06 added in cfc0634 without VERDICT_FROM (071): judged by no Sent-back check; item 084)
E         LOG TIME: none (not checked: 048: built before 045's --log rule reached main; times typed by hand, not recoverable (item 049))
E         LOG BATCH: none (not checked: 083: six lines written in one batch at 10:15 after the build (commit cfc0634 10:15:48); real times not recoverable (item 086)); not computable: 048: no pytest time in 05/06/I2 line; 054: no pytest time in 05/06/I2 line; 055: no pytest time in 05/06/I2 line; 056: no pytest time in 05/06/I2 line; 058: no pytest time in 05/06/I2 line; 059: no pytest time in 05/06/I2 line; 060: no pytest time in 05/06/I2 line
E         UNTRACKED CHANGE: none
E         RESEARCH CODE: none
E         REAL-DATA FIELD: none
E         UNCOMMITTED STEP: none
E         ORPHAN LOG: none
E         UNREADABLE: none
E         INBOX: not checked (2026-11-21.md added in 0d94a94; its templates/daily-audit.md has no ## Inbox)
E         SKIPPED: none
E         
E       assert 1 == 0

tests/test_pipeline_check.py:182: AssertionError
=========================== short test summary info ============================
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 811 passed, 1 skipped in 111.62s (0:01:51)
```
The one failure is `test_repo_pipeline_has_no_skipped_items`. Its only failing lines are `091: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))` and `I3 FAIL: 091`: 091 is in I3 FAIL with its 06 committed (d39d811), so this is expected (item 071), not a defect of this build. `INCOMPLETE: none`, `A1 FAIL: none`, `SKIPPED: none` in the same output.

Suite: 1 failed, 811 passed, 1 skipped in 111.62s (0:01:51)

`python3 scripts/check_pipeline.py` after the I2 `--log` line, before the commit: exit 1; `091: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))`, `I3 FAIL: 091`, `A1 FAIL: none`, `INCOMPLETE: none`, `SKIPPED: none`, LOG TIME and LOG BATCH do not name 091. The exit 1 is the expected FAIL-round state (item 071). Before the line: the same plus `INCOMPLETE: 091 (05 Suite line does not equal the last I2 log tests field ...)`, gone once the line was written.

### File counts, round 2 (item 012)
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
0
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
2
```
The log field uses 2 (scripts/commit_step.py, tests/test_commit_step.py).

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat 7e537c2 -- ccbot/ config/ data/` is empty: no file under ccbot/, config/ or data/ changes)

## File counts (item 012)
Commit (C), from the working tree before it:
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
2
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
3
```
Whole item, (A)+(B)+(C): `git diff --name-only 7e537c2 -- . ':!work' ':!logs' | wc -l` gives 10 tracked files changed by (A)+(B) (none of the 3 (C) files is outside that list: i2-builder.md, i3-verifier.md, run-item.md are in it), plus the 2 new (C) files = 12, matching 04's 12-file table. The log field uses 12.

## Deviations from plan
1. Real-tree stray headings: 11 in 8 items, not 03's 10 in 7. The extra one, 087/05 `### Test output (round 2, pasted)`, was written after R3's count (above). Reported, expectation not adjusted. It gets no entry (087 < 92).
2. Two 089 tests (`test_unreadable_06`, `test_unreadable_05_at_suite_check`) assert the whole INCOMPLETE detail; their 150/151 fixtures are >= 92, so the new `<step> round headings not checked (...; item 091)` entry is now part of that text, and both asserts were extended by exactly that entry. 089's own `not checked (... item 089)` text is unchanged.
3. The two openers are kept in one dict `RUN_HEADING` that `batch_log_items` now reads, instead of the check reading them "from where batch_log_items defines them" (they were inline literals there, so there was nothing to import). Same strings; LOG BATCH output unchanged (whole-output diff IDENTICAL).
4. Extra: the `_anchor_env` docstring wording from 088's A1 finding 1 (commit B). The label change and the corrupt-ref test pin are new output text and are left for a follow-up item; A1 to open it.
5. Container restart: the first I2 run made commits (A) 8a8bd33 and (B) 8dec4f6 and left the 5 (C) files uncommitted when the container restarted. This second I2 run (same item, same round) reviewed those files against 04 (no change needed), ran the step-6 mutants, the exit-term table, the full suite and the remaining 05 sections, and made commit (C). While running the step-6 text mutants with `git stash -- <file>` in the scratch worktree, 3 stash entries were made in the shared refs/stash (stashes are shared across worktrees); `git stash list` showed only those 3, and all 3 (each `WIP on (no branch): 8dec4f6`, from the detached scratch worktree) were dropped at once, so `git stash list` is empty again. No file in the main checkout was touched by it.
6. commit_step additions beyond 04's text, all refusals (exit 2): an ID that is not 3 digits; no path named; `rev-parse --verify` exit other than 0/1. `ls-tree` and `read-tree` use `old` (the HEAD sha read once) instead of the name `HEAD`, so a HEAD that moves mid-run cannot change what is filtered; update-ref still refuses the move. T3's git-failure test also patches `read-tree` and `write-tree` (04 named ls-tree and cat-file). The HEAD-moved test calls `commit(..., old=<parent>)` after an extra commit, as 04 says.
7. 04 says commit_step's output for (C) is pasted in 05. 05 is inside commit (C), so the helper's output for that commit cannot be in it; it is in I2's hand-off, and `git show --stat <C>` (05, the 5 files and only 091's I2 log line) is the record for I3.
8. 04 row "`_section_flags` closer `#{1,3} ` → N1 and an existing LOG BATCH test": N1 and the new `test_section_flags_match_run_seconds_rule` fail; no pre-existing LOG BATCH test does (above).

9. (Round 1, 06 F3) Commit (C) was made by `scripts/commit_step.py` as 66f0fcf and then amended to 4990002 with `git commit --amend --only` to add the session trailers (the helper takes no trailer argument). Tree and parent are unchanged: `66f0fcf^{tree}` = `4990002^{tree}` = a6cdc2c..., both parents 8dec4f6 (I3 checked; reflog `66f0fcf commit_step: Item 091: 01:53 | I2 | ...` then `4990002 commit (amend)`). `--only` with no paths commits the same tree as HEAD and does not take the shared index; a plain `--amend` would. Round 1's helper output, as `commit()` prints it (`<sha7> <subject>`), rebuilt from the reflog entry because the terminal copy was not kept: `66f0fcf Item 091: 01:53 | I2 | 091 | 12 files changed | tests 1 failed, 804 passed, 1 skipped in 107.81s (0:01:47)`.
10. Round 2's commit is made the same way: `commit_step.py 091 "Item 091: <the --log line>" scripts/commit_step.py tests/test_commit_step.py work/091/05-build-report.md` (relative paths), then `git commit --amend --only` for the trailers only. Its own output cannot be in this file (it is inside that commit, Deviations 7); it is in I2's hand-off, and I3 can check the tree with `git rev-parse <helper sha>^{tree} <amended sha>^{tree}` from the reflog.
11. Round 2 extras beyond 06's list: an `outside the repo top` refusal for `../` and absolute paths (06 F1 asks for it in the fix text, with no row: rows added), and the symlinked-dir row with its mutant (F1-noparentresolve), so the parent `.resolve()` is pinned. F2-search (`.match` → `.search`) is equivalent and survives (above); the anchor-free form is the one killed.

## Residuals
- runs with no heading (076/05 L29-59) are not seen by the round-heading check;
- headings indented 1-3 spaces are not matched (`.match` at column 0);
- the template lines (5a) and SCRATCH (7) are text only: no check can see a real collision of two agents' scratch dirs;
- commit_step does not split one code file between items (run-item: build such items one after another), does not run hooks (.git/hooks has only `*.sample` files), and does not commit deletions.

## Recurring issues checked (item 013)
- RI-001 (ESCALATED): every count is measured, not assumed: 8/8 BRANCH ERROR lines, 11 headings / 8 items (03's 10/7 differs; Deviations 1), 0 items >= 92, 4 of 5 lines in T1, 16/16 exit terms killed.
- RI-010 (ESCALATED): new duties get a check where one can (5b INCOMPLETE; commit_step refuses a wrong subject or a batch, and makes this item's own commit). 5a and 7 are text only, stated above. The I2 log line is written with `--log`, never typed.
- RI-014 (OPEN): no new depth-dependent reader; 5b uses the 084 gate (strict when shallow); UNSHALLOW names RULE NOT SEEN.
- Also checked (GUARDED): RI-002 (missing-data grep above; no default on a failed read), RI-006 (file counts from commands), RI-008 (py_compile 3.11 on the 5 .py files; no prefixmatch; no backslash in an f-string expression), RI-009 (mutations only in the scratch worktree; stash incident in Deviations 5), RI-012 (anchored `.match`, N2 negative; commit_step classifies git results by exit code only), RI-013 (whole-output diff of check_pipeline before/after (B): IDENTICAL).
Round 2 re-check: RI-001 (counts measured: 6 new cases, 5 mutants, 4/1/0/1/1 failures as printed), RI-010 (the F1 bypass of commit_step is closed and pinned by a killed mutant), RI-012 (filter_log's owner match now has its negative test; equivalent `.search` noted), RI-009 (mutants in a mktemp scratch worktree only, no stash), RI-002 (grep above, no default), RI-008 (py_compile 3.11), RI-006 (file counts from commands), RI-014 (no git-depth reader added), RI-013 (no report effect: ccbot/config/data unchanged).
RI-001: ESCALATED, unchanged by 091.
RI-010: ESCALATED; 091 adds commit_step (086 F4) and the round-heading check (086 F3); GUARDED condition unchanged (086 merged and its 083 fixture flagged).
RI-014: OPEN, unchanged; UNSHALLOW now names RULE NOT SEEN.
