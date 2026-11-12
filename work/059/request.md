# Work item 059
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-12

## What we want
Only a real Webull rate-limit reply (HTTP 429) is retried. Any other error, whatever digits its message holds, raises at once.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `ccbot/broker/webull_sandbox.py` `_rate_limited` (item 056, 914c243): `return "429" in low or ...` is a plain substring test on the whole error text.
- A1 probe on main 05a33fd: `_rate_limited('ServerException: http_status=500 error_code=INTERNAL msg=order 7a4291c failed')` → `True`. Such an error is retried 5 times (2+4+8+16+32 = 62 s) before it raises.
- `_call` also wraps `place_option` (line 254), whose payload carries a random hex `client_order_id` (line 70); a 32-hex id contains "429" about 0.7% of the time, so an order error that echoes its id can be resent.
- `tests/test_webull_sandbox.py::test_other_errors_are_not_retried` uses a message with no "429" in it, so the suite (218 passed) does not see this.

## Root cause and prevention guardrail (BUG only)
Root cause: the error is classified by searching free text for a short number instead of reading the status the SDK reports. The test only covers the messages the builder expected.
Guardrail: classify on the status first (`status_code` / `http_status` attribute of the exception or reply, == 429); fall back to text only as a whole token (`\b429\b` next to "http"/"status") or the phrase "too many requests". Add a test whose non-429 error text contains "429" inside an id and must raise at once with no sleep. Add to i3-verifier's checklist (06): any error-text match must have a negative test with the pattern embedded in other text.

## Recurring issue link (RI-#, if any)
RI-012 (new), occurrence 1.

## Done looks like
The probe above returns False; a 500 with "429" in an id raises on the first try (no retry_sleep call); a 429 status or "Too many requests" still retries; suite green.
