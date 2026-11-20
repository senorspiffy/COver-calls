# 04 Build plan - 083
Fit verdict: FIT
Fits a ~$5k account: unfreezes the main account; no rule change.
## Extra research (with sources)
None.
## Files to create/change
ccbot/bot.py; tests/test_held_quote.py
## Tests and checks
2 new tests; full suite; mutation: remove the widening → both new tests fail.
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | `BrokerMarket.chain` widens lo/hi to the held strike on the held expiry |
| Map 2 | both constructors pass `start.get(t).option` |
| Missing input row | unchanged: no fallback value |
## Guardrail tests
- test_window_widens_to_the_held_strike
- test_window_unchanged_without_a_held_option_or_on_another_expiry
## Expected result
Full suite passes.
Recurring issues checked (I1): RI-001, RI-002.
