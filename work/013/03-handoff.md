# 03 Research hand-off - 013
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| Only r1/r2 read it | grep | VERIFIED |  |
| Errors arose at R3/I1/I2 | RI entries | VERIFIED |  |
**Totals:** 2 rows checked → **2 VERIFIED as-is**, **0 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | Step 0 in r3, i1, i2, i3; header 'every R and I agent' | agent files | instructions | grep -l recurring-issues | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| recurring-issues.md | absent | agent says so |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Files | r3, i1, i2, i3 | 4 | ✓ |
| Totals | 2+0+0=2 | 2 | ✓ |
`python3 scripts/check_handoff.py 013` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 2
totals line: 2 rows -> 2 as-is, 0 fixed, 0 removed
PASS
```
