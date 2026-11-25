# 07 Audit task - 102
Audit should look at:
1. The diff at a733756: tests/test_commit_step.py (TB_ROWS/TB_IDS, `_objects`, T-b objects compare, `test_trailer_refusals_make_no_git_call`) and tests/test_pipeline_check.py (`test_from_cutoff_boundary` 10 rows, `test_from_values`). No change outside tests/.
2. The 15 mutants (M1 + 7 constants x 2) in 05 and 06: 15 killed, identical failing-ID sets in both runs. Re-run M1 if desired; `no-value` is a guard row by design (refused in `main`).
3. Residual (a): per-site operator mutants (14 sites) are not pinned; the cutoffs are pinned against shifts only. Candidate follow-up item.
4. Residual (b) / Part 3: the i1-reviewer sentence (RULE_PATHS) still waits for the person's OK.
5. RI-010 near miss "commit_step trailer-refusal order untested -> 102" can be noted as built in recurring-issues.md (A1, on main).
