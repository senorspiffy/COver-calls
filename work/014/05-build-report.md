# 05 Build report - 014
## Changes made (file: what changed)
ccbot/rules.py; ccbot/broker/sim.py; ccbot/broker/webull_sandbox.py; ccbot/screen.py; ccbot/missing.py; tests/test_missing_inputs.py; .claude/agents/i2-builder.md; logs/recurring-issues.md
(One branch, `daily-fixes/2026-10-31-stuck`, carries items 009–016 together.)
## Connectivity check
- [x] every new function/rule is used (new events reach paper_trades rows via `broker.advance`; policy rows each have a drop test (`test_drop_each_input`).)
- [x] every input has a source, every output has a consumer
- [x] every branch ends in a defined result (see the Missing inputs table in 03)
- [x] no leftover TODOs or unused files
Missing-data grep (`grep -rnE "fillna|nan_to_num|or 0|else 0|..." ccbot/`): two new lines in sim.py match `else 0`: `dividend=… else 0.0` and `div_next=… else 0.0`. Reason: 0.0 only when the ex-date is known and is not today / the next trading day, so 'no dividend on that day' is known, not defaulted.
## Test output (pasted, not summarized)
```
Mutations (each in a scratch edit, restored):
- Day.q default back to 0.0 → FAILED test_day_float_defaults_are_nan (1 failed)
- remove CAPITAL_UNKNOWN guard → FAILED test_drop_each_input[derived.capital] (1 failed)
- cap test back to `>` → 1 failed (tests/test_missing_inputs.py)
- sim div_next=0.0 → FAILED test_drop_each_input[broker.div_next]
- remove EARLY_ASSIGN_CHECK_NA branch → FAILED test_drop_each_input[broker.div_next]
$ python3 -m pytest -q
159 passed, 1 skipped
```
## Deviations from plan
None.
