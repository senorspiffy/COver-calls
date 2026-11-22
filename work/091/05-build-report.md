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
