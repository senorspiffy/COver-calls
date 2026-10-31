# 03 Research hand-off - 015
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| Step 1 long line | awk length | VERIFIED |  |
| No location for mutations | i3 text | VERIFIED |  |
**Totals:** 2 rows checked → **2 VERIFIED as-is**, **0 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | r3 step 1b = moved feasibility + worked-example text | r3 | step 1b | grep '^1b' | – |
| 2 | i3 step 3 'in a scratch copy, never in the repo' | i3 | text | grep | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| – | – | – |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Wording unchanged | moved text = old tail of step 1 | diff shows a move | ✓ |
| Totals | 2+0+0=2 | 2 | ✓ |
`python3 scripts/check_handoff.py 015` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 2
totals line: 2 rows -> 2 as-is, 0 fixed, 0 removed
PASS
```
