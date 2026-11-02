# 04 Build plan - 014
Fit verdict: FIT
Fits a ~$3k account: no trading, no new costs, no brokerage connection.
## Extra research (with sources)
None needed; inputs are repo files.
## Files to create/change
ccbot/rules.py; ccbot/broker/sim.py; ccbot/broker/webull_sandbox.py; ccbot/screen.py; ccbot/missing.py; tests/test_missing_inputs.py; .claude/agents/i2-builder.md; logs/recurring-issues.md
## Tests and checks
drop tests for broker.div_next, broker.dividend, broker.q, model.oi, derived.capital; test_every_day_default_is_listed; test_day_float_defaults_are_nan; test_broker_capability_flags_have_policy_rows
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1–5 | each built |
## Guardrail tests
- Missing inputs: broker.dividend/div_next/q, model.oi, derived.capital → `test_drop_each_input[...]`
- Enumeration: `test_every_day_default_is_listed`, `test_day_float_defaults_are_nan`
## Expected result
Every map step applied; full suite passes.
