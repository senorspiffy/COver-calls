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
