# 04 Build plan - 059
Fit verdict: FIT
No strategy or account change; paper scans only.
## Extra research (with sources)
None beyond 01 (SDK 3.0.4 source).
## Files to create/change
- ccbot/broker/webull_sandbox.py: `_rate_limited(exc)` reads `http_status`/`status_code` first; text fallback regex `HTTP Status:\s*429\b` or "too many requests"/"too_many_requests"; `_call` passes the exception.
- tests/test_webull_sandbox.py: `test_429_inside_other_text_is_not_retried` (a ServerException-like 500 with "429" in Msg and RequestID raises on try 1, no sleep); `test_rate_limit_status_attribute_is_retried` (exception with `http_status=429` and no "429" in text is retried).
- .claude/agents/i3-verifier.md: step 3 line for error-text matches.
## Tests and checks
Full suite; mutation in a scratch copy: restore `"429" in low` → new negative test fails.
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | `_rate_limited(exc)` status first, narrow text fallback |
| Map 2 | `_call` passes `exc` |
| Map 3 | negative test + i3-verifier.md line |
| Missing inputs row | text-only exception → fallback; else raise |
## Guardrail tests
- Feasibility: – (no filter or window rule)
- Missing inputs: exception without status attribute → existing `test_rate_limit_is_retried_then_succeeds` (RuntimeError text "HTTP Status: 429, ...") and `test_other_errors_are_not_retried`
## Expected result
Suite green; probe from request.md returns False.
Recurring issues checked (I1): RI-002, RI-007, RI-012.
