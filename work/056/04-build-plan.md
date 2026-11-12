# 04 Build plan - 056
Fit verdict: FIT
Fits a ~$5k account: no trading change; scans stop crashing.
## Extra research (with sources)
None.
## Files to create/change
ccbot/broker/webull_sandbox.py; tests/test_webull_sandbox.py
## Tests and checks
Three new tests; full suite; mutation: remove the retry → the two retry tests fail.
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | `_call` loop over RETRY_WAITS with `_rate_limited` |
| Map 2 | non-429 re-raised |
## Guardrail tests
- test_rate_limit_is_retried_then_succeeds
- test_rate_limit_gives_up_after_five_retries
- test_other_errors_are_not_retried
## Expected result
Full suite passes.
Recurring issues checked (I1): RI-002, RI-010.
