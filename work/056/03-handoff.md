# 03 Research hand-off - 056
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| R1 per-endpoint limits | Webull market data overview | VERIFIED |  |
| R2 429 meaning | RFC 6585 §4 | VERIFIED |  |
| R3 observed 429 | VPS run only | UNSUPPORTED | kept as the bug report's evidence, labelled UNVERIFIED in 01 |
**Totals:** 3 rows checked → **2 VERIFIED as-is**, **1 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | `_call`: retry on 429 status or rate-limit error text, waits 2/4/8/16/32 s, then raise | SDK reply | data or error | test_rate_limit_is_retried_then_succeeds, test_rate_limit_gives_up_after_five_retries | – |
| 2 | Other errors raise at once | SDK error | error | test_other_errors_are_not_retried | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| – | – | – |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Max wait | 2+4+8+16+32 | 62 s | ✓ |
| Totals | 2+1+0=3 | 3 | ✓ |
`python3 scripts/check_handoff.py 056` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 2
fact-check rows: 3
totals line: 3 rows -> 2 as-is, 1 fixed, 0 removed
PASS
```
