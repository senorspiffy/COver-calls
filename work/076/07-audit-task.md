# 07 Audit task - 076
Build commits: 266a6a2 (round 1: scripts/check_pipeline.py, .claude/agents/i2-builder.md, tests/test_pipeline_check.py) and e813e1f (round 2: R15/R16 in tests/test_pipeline_check.py). I3: FAIL round 1, PASS round 2 (06).

What Audit should look at:
1. Re-run m1 (`_END` -> `(?:, )?`), m2 (pass <= total removed), m8 (failed/passed swapped in `_STATS_PARTS`) and m9 (`\d{3}` guard removed from `log_hint`) on a scratch worktree of the branch head. Each must fail its named test (I3 round 2: m1 -> R15+R16, m8 -> A3/A13+R3, m9 -> T6; m2 -> `test_i2_tests_field_cutoff`, round 1).
2. RI-006 GUARDED condition (05): after merge, m2 or m3 fails `test_i2_tests_field_cutoff` on main. Carry it to logs/recurring-issues.md when that holds.
3. Known limits, accepted in 04 and still open: (a) the new field can't prove the run was the full suite (05's Test output is the record); (b) a free-text note `(...)` after the stats is allowed and could hold anything; (c) an old-form `411/411` for an item < 076 is still accepted. Follow-up from 04: option C, or an I3 duty to compare I2's log field with 05 Test output using a fixed `Suite:` label. Decide whether to open an item.
4. I2's round 2 line for 076 records a red suite (`1 failed, 525 passed, 1 skipped`). The failure is the expected item-071 one (06 was I3 FAIL), but `--log` accepts any `N failed`. Decide whether a failing I2 field should need a reason (e.g. a required note), or whether 05 is enough.
5. The round 2 commit message (e813e1f) says R15/R16 "pin part order". They pin the `, ` separator (`_END`); order is held by the group sequence (m8). The commit text is the only place it is wrong, since 04 and 05 are correct.
6. RULES change: .claude/agents/i2-builder.md L25 (round 1) needs the person's OK in PR review.
7. 077 and 079 build on this checker code. Confirm that any new reader of I2 lines calls `log_fields_ok` and not `re.fullmatch(LOG_FORMAT["I2"], ...)`, and that 077/079's own I2 lines use the new form.
8. Re-run the whole suite (I3 at e813e1f: 1 failed, 525 passed, 1 skipped; the failure is `test_repo_pipeline_has_no_skipped_items` because 06 was FAIL there. With this PASS 06 it should pass) and `python3.11 -m py_compile scripts/check_pipeline.py`.
