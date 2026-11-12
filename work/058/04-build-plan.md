# 04 Build plan - 058
Fit verdict: FIT
Fits a ~$5k account: paper only; existing accounts untouched (new keys default off).
## Extra research (with sources)
None.
## Files to create/change
ccbot/config.py; ccbot/screen.py; ccbot/bot.py; ccbot/rules.py (NO_DIP reason); config/default.json; config/stagger.json; config/dip_base.json; config/dip_reserve.json; tests/test_budget_paper.py; tests/test_variants.py
## Tests and checks
8 new tests; full suite; mutations: dip gate off → dip tests fail; screen without for_ticker → screen test fails.
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | `for_ticker()` in config.py; screen, prefetch, `_manage`, `_would_act` |
| Map 2 | `_dip()` in bot.py before each new entry; held positions not gated |
| Map 3 | three config files |
| Missing input row | `_dip` returns "n of 5 closes recorded" → NO_DIP |
## Guardrail tests
- test_no_dip_rule_until_enough_history
- test_bad_windows_and_dip_rules_are_refused
## Expected result
Full suite passes.
Recurring issues checked (I1): RI-002, RI-007.
