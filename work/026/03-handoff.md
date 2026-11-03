# 03 Research hand-off - 026
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| 023 stopped after R1 | ls work/023 | VERIFIED |  |
| 024 has only 05 | ls work/024 | VERIFIED |  |
| UTF-8 fix had no item | git log, logs | VERIFIED |  |
| 024 tests cover a one-passing day | tests/test_portfolio.py | WRONG | added test |
| 024 broker guard tested | mutation: 0 failed | WRONG | added test |
**Totals:** 5 rows checked → **3 VERIFIED as-is**, **2 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | scripts/check_pipeline.py (SKIPPED/STUCK/complete) | work/* | status lines, exit 1 on SKIPPED | tests/test_pipeline_check.py | – |
| 2 | run-item FAST scope + Waived; a1, i3, daily-audit run the script; template Scope | agent files | instructions | grep | – |
| 3 | Complete 023 (03, 07; 02 waived) and 024 (06, 07; 01–04 waived) | work/023, 024 | step files | script: no SKIPPED | – |
| 4 | Two 024 tests from I3 | tests/test_portfolio.py | tests | mutation fails them | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| Scope line | absent | FULL |
| Date line | absent | never STUCK (no age) |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| FULL count | 01..07 | 7 files | ✓ |
| FAST keeps R3 + I3 | 03, 06 in FAST list | yes | ✓ |
| Totals | 3+2+0=5 | 5 | ✓ |
`python3 scripts/check_handoff.py 026` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 5
totals line: 5 rows -> 3 as-is, 2 fixed, 0 removed
PASS
```
