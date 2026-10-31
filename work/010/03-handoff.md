# 03 Research hand-off - 010
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| V0 row 'not selected', n/a | short CSV run on main | VERIFIED |  |
| Only V4 needs selection | variants.expand | VERIFIED |  |
**Totals:** 2 rows checked → **2 VERIFIED as-is**, **0 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | One config → chosen = it, label '(fixed)' | configs | held-out row | test_short_csv_reports_pbo_na_without_warnings | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| train years (V4) | none | 'not selected (no train years)', n/a |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| V0 held-out | compound of 2025 return | −1.94% (same as the full-period CAGR on a 1-year file) | ✓ |
| Totals | 2+0+0=2 | 2 | ✓ |
`python3 scripts/check_handoff.py 010` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 2
totals line: 2 rows -> 2 as-is, 0 fixed, 0 removed
PASS
```
