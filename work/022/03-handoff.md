# 03 Research hand-off - 022
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| Rule applies to every item | r2-improver.md | VERIFIED |  |
| 017-021 fixes add no external fact | their 03-handoff files | VERIFIED |  |
**Totals:** 2 rows checked → **2 VERIFIED as-is**, **0 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it |
|---|---|---|---|---|
| 1 | Add N/A exception to r2-improver.md with conditions | r2-improver.md | rule | text present |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Totals add up | as-is + fixed + removed = rows | 2 + 0 + 0 = 2 | ✓ |
`python3 scripts/check_handoff.py 022` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 2
totals line: 2 rows -> 2 as-is, 0 fixed, 0 removed
PASS
```
