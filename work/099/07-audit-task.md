# 07 Audit task - 099
Item: 099 (BUG, FULL, RI-012 / RI-014 family near miss). tests/test_pipeline_check.py 092 block only: `_ok3` replaced by `_exact3` (whole stdout in order, exit code, `err == b""`), `_unread`, shared constants, `_no_claim` (fullmatch `no \S+; nothing else to check`), new single runs `151` and `003`, and new `test_check_all_unreadable_problem_call_site[n1|n2|p]` (fake `main` via monkeypatch). Code commit d8f8f58 on daily-fixes/2026-11-24-b, base 425094f. scripts/ and .claude/ unchanged. I3 PASS r1.

What A1 should look at:
1. Re-run A1-3 (delete `return _report(problems)` under `if why03:`) and A1-2 (`.search` for `.fullmatch` in check_all) on a scratch worktree of the head: A1-3 must fail test_handoff_bad_03, test_handoff_03_is_directory, test_handoff_all_one_bad_03, test_handoff_legacy_bad_03_is_fail; A1-2 must fail call_site[n1] and [n2] only. Both survive with the base test file (06).
2. The `err == b""` pin: it holds on Linux at 15 of 15 runs. Check that no other environment the suite runs in (e.g. a Python warning on stderr) would make it brittle; if so it is a maintenance cost, not a defect.
3. The call-site test imports check_handoff in-process; check that it does not leak `main` to later tests (monkeypatch undoes it) and that a cached `check_handoff` module from another path cannot make it pass vacuously (the `calls == ["003"]` assert should catch that).
4. Re-run M-a and M-b (05 forms) to confirm the 092 kills still hold; I3 re-ran only M-f and A1-1.
5. Step 7: `check_handoff.py --all` base vs head script, same cwd, byte-identical (105 lines); confirm on the merged branch.
6. RI status to copy on main: RI-012 GUARDED, holds (closes the 2026-11-24 "check_handoff tests check presence only" near miss). RI-014 OPEN, unchanged (no git read added). RI-001 / RI-010 ESCALATED, unchanged.
A1 result: PASS (2026-11-25, logs/audit/2026-11-25-099.md)
