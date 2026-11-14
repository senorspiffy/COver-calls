# 03 Research hand-off - 059
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| F1 ServerException keeps http_status | SDK 3.0.4 exceptions.py lines 31-46 | VERIFIED |  |
| F2 str() format holds Msg and RequestID | SDK 3.0.4 exceptions.py lines 51-53 | VERIFIED |  |
| F3 429 meaning | RFC 6585 §4 | VERIFIED |  |
| F4 SDK default retry list 500/502/503/504 | SDK 3.0.4 retry_condition.py line 140 | VERIFIED |  |
| F5 A1 probe → True | re-run on this branch | VERIFIED |  |
**Totals:** 5 rows checked → **5 VERIFIED as-is**, **0 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | `_rate_limited(exc)`: True if `getattr(exc, "http_status", None) == 429` (or `status_code`); else text fallback only on `HTTP Status: 429` as a whole token or "too many requests" / "too_many_requests" | SDK exception | bool | test_rate_limit_is_retried_then_succeeds (existing), new test_429_inside_other_text_is_not_retried | – |
| 2 | `_call` passes the exception, not `str(exc)` | – | – | same tests | – |
| 3 | Guardrail: test with "429" in RequestID and Msg of a 500 raises on try 1 with no sleep; i3-verifier.md step 3 line: every error-text match needs a negative test with the pattern inside other text | – | – | mutation: restore `"429" in low` → new test fails | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| exception `http_status` attribute | plain exception with text only | text fallback; anything else is not a rate limit and raises at once |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Max wait unchanged | 2+4+8+16+32 | 62 s | ✓ |
| False-match odds (01) | 30/4096 | 0.0073 | ✓ |
| Totals | 5+0+0 | 5 | ✓ |
`python3 scripts/check_handoff.py 059` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 2
fact-check rows: 5
totals line: 5 rows -> 5 as-is, 0 fixed, 0 removed
PASS
```
Recurring issues checked (R3): RI-002 (absent status → raises, never defaulted to a retry), RI-007 (own item), RI-012 (this item).
