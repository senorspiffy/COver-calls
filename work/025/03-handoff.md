# 03 Research hand-off - 025
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| Ford passes every test (023) | 001 step 3 + `_reject` | WRONG | EARNINGS_UNKNOWN |
| VALE fits (023) | same | WRONG | EARNINGS_UNKNOWN |
| Existing test pins blank earnings → EARNINGS_UNKNOWN | tests/test_missing_inputs.py | VERIFIED |  |
| Policy is enforced only in code | grep r1/r3 for MISSING_POLICY (0 hits before) | VERIFIED |  |
**Totals:** 4 rows checked → **2 VERIFIED as-is**, **2 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | Correction in 023 screen-summary; 001 decision example note | 025 evidence | corrected text | grep EARNINGS_UNKNOWN | 0 of 8 pass, 2026-10-30 quotes, `_reject` rule |
| 2 | r1 step 3a + r3 step 3a: reject code per ticker; unknown stays unknown | agent files | instructions | grep MISSING_POLICY in r1, r3 | – |
| 3 | Guardrail test: existing `test_drop_each_input[snapshot.next_earnings]` | tests | pass | pytest | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| Next earnings date (research screen) | not published | `EARNINGS_UNKNOWN`; reasoning shown as a note only |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Earnings test | stock, no published date → fail | F/VALE/AAL unpublished → fail | ✓ |
| Totals | 2+2+0=4 | 4 | ✓ |
`python3 scripts/check_handoff.py 025` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 4
totals line: 4 rows -> 2 as-is, 2 fixed, 0 removed
PASS
```
