# 04 Build plan - 060
Fit verdict: FIT
Paper-only reserve account; main account unchanged.
## Extra research (with sources)
None.
## Files to create/change
- ccbot/bot.py `_dip`: trading-day window from `expiries.business_days(date − (2·lookback+10) days, date, NYSE holidays)[-lookback:]`; past rows filtered to `window[0] <= ts < date`; `min_days` unchanged.
- tests/test_budget_paper.py: `test_missed_scans_do_not_stretch_the_window` (a 30.00 close 25 trading days back plus 5 recent closes at 24.3: the old scan count would see 30.00 and open; now NO_DIP).
- config/dip_reserve.json: `_about` "20-trading-day high".
## Tests and checks
Full suite; mutation in a scratch copy: drop the date filter → new test fails.
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | `_dip` trading-day window |
| Map 2 | `min_days` unchanged (existing test) |
| Map 3 | dip_reserve.json `_about` |
| Missing inputs rows | existing NO_DIP count text; calendar raise upstream |
## Guardrail tests
- Feasibility: 20-day window → `test_missed_scans_do_not_stretch_the_window`, `test_lookback_drops_old_highs`
- Missing inputs: thin window → `test_no_dip_rule_until_enough_history`
## Expected result
Suite green except the known `A1 FAIL: 056` pipeline test until A1 re-audits 056.
Recurring issues checked (I1): RI-001, RI-002, RI-012.
