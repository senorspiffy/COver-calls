# 07 Audit task - 041
A1, please check:
- `python3 scripts/check_handoff.py 041` → PASS; `python3 scripts/check_pipeline.py` → complete, not INCOMPLETE.
- The changed files in 05 match `git diff` on the PR branch.
- The 2026-11-20 probe gives NaN; 2026-11-09 still 0.15.
- MISSING_POLICY has 3 `tickers.*` rows, each with a drop test.
- Removing the stale guard fails a test (mutation in a scratch copy).

A1 result: PASS (2026-11-04, re-run by A1 on daily-fixes/2026-11-04: check_handoff PASS, check_pipeline complete / INCOMPLETE none, mutation re-checked in a scratch copy, 05 files match git diff)
