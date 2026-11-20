# 05 Build report - 083
## Changes made (file: what changed)
- ccbot/bot.py: `BrokerMarket` takes `held` (the ticker's open short option); `chain` widens the strike window to include its strike on its expiry; `run_daily` passes `start.get(t).option` at both constructions.
- tests/test_held_quote.py: 2 tests (2026-11-19 VALE case; no change without a held option or on another expiry).
## Connectivity check
- [x] every new function/rule is used
- [x] every input has a source, every output has a consumer
- [x] every branch ends in a defined result
- [x] no leftover TODOs or unused files
## Test output (pasted, not summarized)
```
344 passed, 1 skipped in 48.51s
```
Mutation (widening removed): `2 failed in 0.19s`.
## Real-data effect (diff_reports output, pasted)
not required (ccbot/bot.py, tests/test_held_quote.py; realtest.py and its inputs unchanged)
## Deviations from plan
None.
