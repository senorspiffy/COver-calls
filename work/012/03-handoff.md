# 03 Research hand-off - 012
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| '48 new' in log | log + breakdown | WRONG | 47 new + 1 changed; command in i2 |
| Sources undefined | r1 L19 | WRONG | already fixed by 020 |
**Totals:** 2 rows checked → **0 VERIFIED as-is**, **2 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | i2 step 4: new/changed counts from `git status --porcelain -uall` commands | git | numbers | grep i2 | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| git | absent | no count; say so |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| 2026-10-30 | 47 + 1 | 48 lines | ✓ |
| Totals | 0+2+0=2 | 2 | ✓ |
`python3 scripts/check_handoff.py 012` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 2
totals line: 2 rows -> 0 as-is, 2 fixed, 0 removed
PASS
```
