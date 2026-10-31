# 03 Research hand-off - 029
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| 009–016 request only | ls | VERIFIED |  |
| daily-audit runs only new items | file text | VERIFIED |  |
**Totals:** 2 rows checked → **2 VERIFIED as-is**, **0 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | STUCK status in check_pipeline.py | request Date | STUCK lines | test_stuck_after_one_day | – |
| 2 | daily-audit.md + template: stuck list at top, ask the person | docs | instructions | grep | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| Date line | absent | never STUCK; shown as not started |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Age | today − Date ≥ 1 | 2026-10-31 − 2026-10-30 = 1 | ✓ |
| Totals | 2+0+0=2 | 2 | ✓ |
`python3 scripts/check_handoff.py 029` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 2
totals line: 2 rows -> 2 as-is, 0 fixed, 0 removed
PASS
```
