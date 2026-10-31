# 05 Build report - 016
## Changes made (file: what changed)
ccbot/report.py; tests/test_report.py; work/001/03-handoff.md
(One branch, `daily-fixes/2026-10-31-stuck`, carries items 009–016 together.)
## Connectivity check
- [x] every new function/rule is used (`_earnings_text` is called by `daily_report`.)
- [x] every input has a source, every output has a consumer
- [x] every branch ends in a defined result (see the Missing inputs table in 03)
- [x] no leftover TODOs or unused files
Missing-data grep (`grep -rnE "fillna|nan_to_num|or 0|else 0|..." ccbot/`): no new hits from this item.
## Test output (pasted, not summarized)
```
Report line: - Days to earnings: none (ETF); days to ex-dividend: 49
$ grep -c 'items 003, 004, 005, 008' work/001/03-handoff.md
2
$ python3 -m pytest -q
159 passed, 1 skipped
```
## Deviations from plan
None.
