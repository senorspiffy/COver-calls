# 05 Build report - 060
## Changes made (file: what changed)
- ccbot/bot.py: `_trading_window_start(date, lookback)` (NYSE trading days from `expiries.business_days` + holidays.json); `_dip` keeps past closes with `start <= ts < date`; detail text "below the 20-trading-day high ... (<n> closes)".
- tests/test_budget_paper.py: `test_missed_scans_do_not_stretch_the_window`.
- config/dip_reserve.json: `_about` says 20-trading-day high.
New files: `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` → 0. Changed: `... | grep -c '^ M'` → 3.
## Connectivity check
- [x] every new function/rule is used (`_trading_window_start` called by `_dip`)
- [x] every input has a source, every output has a consumer (snapshots + holidays.json → NO_DIP row or entry)
- [x] every branch ends in a defined result (thin window → NO_DIP with count; no dip → NO_DIP with %; dip → entry)
- [x] no leftover TODOs or unused files
Grep (missing-data policy) on the added lines: no hits.
## Test output (pasted, not summarized)
`python3 -m pytest -q tests/test_budget_paper.py` → `9 passed in 0.55s`
`python3 -m pytest -q` → `FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items` / `1 failed, 236 passed, 1 skipped` (`A1 FAIL: 056`, cleared when A1 re-audits 056 with 059).
Feasibility: 251 of 251 2026 trading days give a full 20-day window (03).
Mutation (scratch copy): date filter removed → `FAILED test_missed_scans_do_not_stretch_the_window`, 1 failed, 8 passed.
RI-002: 060 adds no default; a thin window still blocks.
## Deviations from plan
Detail text also updated ("scan" → "trading-day"), to match the new rule.
