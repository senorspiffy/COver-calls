# 03 Research hand-off - 030
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| 36 tracked .pyc | git ls-files | VERIFIED |  |
| Ignored already | `.gitignore` | VERIFIED |  |
**Totals:** 2 rows checked → **2 VERIFIED as-is**, **0 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | git rm --cached all __pycache__ files | index | 0 tracked | test_no_tracked_pycache | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| git | absent | test would error, not pass silently |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Count | git ls-files | grep -c pycache | 0 | ✓ |
| Totals | 2+0+0=2 | 2 | ✓ |
`python3 scripts/check_handoff.py 030` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 2
totals line: 2 rows -> 2 as-is, 0 fixed, 0 removed
PASS
```
