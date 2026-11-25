# 07 Audit task - 108
Item: 108 (EFFICIENCY, FULL, RI-014). This item changes tests only: `tests/test_pipeline_check.py::test_shallow_elif_branch_goes_to_unchecked`. The timed05 setup and precondition now derive their values from `FIELDS["I2"]` through `_se_fields()` and read the I2 field back from the fixture log. `SE_FIELD` is deleted, and a new `timed05alt` case patches `FIELDS["I2"]`, giving 16 ids. Head 4619802 (+ the I3 commit) on daily-fixes/2026-11-25, code base f4f55a7. I3 PASS, round 1.

What A1 should look at:
1. Re-run M-timed (`elif False`) and K-timed (`unsure("06")`) on the `# item 095: anchor not read` line under `# item 090: TIMED gate` in a scratch worktree, with PYTHONDONTWRITEBYTECODE=1 and `__pycache__` cleared. Expected: `2 failed, 14 passed`, failing only `timed05-shallow` and `timed05alt-shallow`.
2. Done (a): change the shared `FIELDS["I2"]` (tests line 19) to another timed field that has ` | tests `, for example `4 files changed | tests 7 passed, 2 skipped in 3.25s`. I3 got `16 passed` at head and `2 failed` at base f4f55a7. Judge whether a field with an optional `(H:MM:SS)` tail or ` seconds` also flows through (the strip regex covers `s| seconds`).
3. `timed05alt` patches FIELDS with `monkeypatch.setitem`. Check that nothing outside this test sees the patched value (pytest undoes it), and that other tests reading `FIELDS["I2"]` are unaffected. The full suite at head gave 1013 passed, 1 skipped.
4. Overlap: 105, 109 and 110 are built today on the same branch and may edit tests/test_pipeline_check.py or scripts/check_pipeline.py. Check that the `_rh_item` / `I2_ENTRY` helpers and the TIMED gate line still match after those builds, and that a mismatch fails by name (`_se_edit` `old in text`, `len(own_i2) == 1`).
5. No scripts/, templates/, .claude/, config/ or ccbot/ change (`git diff --stat f4f55a7 4619802` lists only the test file). No RULE_PATHS file is touched.
6. RI status to copy: RI-014 OPEN, unchanged. RI-001 ESCALATED, unchanged.
