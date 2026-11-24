# 07 Audit task - 092
For A1 (per-item mode). Item 092 (BUG, FULL): scripts/check_handoff.py reads 01 and 03 through check_pipeline's `_read`, so a non-UTF-8 or directory 01/03 gives `FAIL: <path> unreadable (<detail>)` and exit 1, never a traceback. Built on daily-fixes/2026-11-24 (open PR #36), head c098a17; I3 PASS round 1.

What to look at:
1. The diff `git diff 138e0ce c098a17 -- scripts tests`: `_pipeline()`, `_report()`, `UNREADABLE_PROBLEM`, the two `cp._read(..., missing_ok=True)` calls in `main`, the LEGACY guard in `check_all`, and the check_pipeline.py L360 docstring. Both scripts are RULE_PATHS: the person's OK is needed at PR review.
2. Re-run one or more mutations on a scratch worktree (never the repo, no stash): M-a/M-b (strict `read_text(encoding="utf-8")` restored) must fail `test_handoff_read_census` and the matching fixtures; M-f (LEGACY guard removed) must fail `test_handoff_legacy_bad_03_is_fail`. I3's results are in 06.
3. RI-012: `test_unreadable_problem_fullmatch_only` has the in-text negative (`x unreadable (not UTF-8 at byte 0); y`). Check that no other new code classifies a problem by substring.
4. Same-output claim: for readable files the head prints exactly what the base did (I3: `--all` byte-identical; 98 single-item runs, 0 differ). Spot-check one item.
5. Known gaps in 05 (repeat in the audit): (1) check_handoff now depends on check_pipeline.py importing cleanly; (2) an unreadable 01 after R1 gives a `not computed` sources value that `--log R1` refuses, so the item stays INCOMPLETE until R1 is re-run; run-item.md L17 does not say this, and a `.claude/` edit needs the person's OK (A1 may open a request); (3) `--all` never reads the 01 of an item with no 03; (4) open_branches' unreadable request.md is silent in check_handoff; (5) `work.iterdir()`/`is_dir()` may still raise.
6. `test_unreadable_problem_fullmatch_only` inserts the scripts dir into the test process's sys.path and imports check_handoff there; harmless now (the suite is green), but note it if a later test depends on import order.
7. RI-014 status: 092 is a near miss in RI-014's family (not counted); copy guardrail status on main only (item 036).
