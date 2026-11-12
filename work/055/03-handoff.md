# 03 Research hand-off - 055
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| S1 OXY 5/5 | oxy statistics | VERIFIED |  |
| S2 CSX 5/5 | csx statistics | VERIFIED |  |
| S3 BMY 5/5 | bmy statistics | VERIFIED |  |
| S4 4/5 names | statistics pages | VERIFIED |  |
| S5 weak names | statistics pages | VERIFIED |  |
| E1 earnings dates | overview pages | VERIFIED |  |
| K1 weekly expiries | Cboe JSON (truncated) | VERIFIED |  |
| Bank debt check | no interest cover shown | UNSUPPORTED | scored on debt/equity < 3 instead, stated in 01 checklist |
**Totals:** 8 rows checked → **7 VERIFIED as-is**, **1 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | tickers.json: BMY, USB, MO, MDLZ | E1 | Day fields | test_quality_account_14_names_8000_each | – |
| 2 | config/quality.json: 14 names, $112,200, frac 1/14 | S1–S4 | config | same | 14/14 earnings known Nov 13 |
| 3 | config/weekly.json trimmed to 7 | K1 | config | test_weekly_account_… | – |
| 4 | VPS daily run: quality replaces practice; weekly added | person's ask | reports | VPS scratch scan | after merge |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| next ex-div dates | null | dividend NaN, never 0 |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| quality cash | 14×8000+200 | 112,200 | ✓ |
| weekly cash | 7×8000+200 | 56,200 | ✓ |
| MO fits | 7,320 ≤ 8,014 | yes | ✓ |
| Totals | 7+1+0=8 | 8 | ✓ |
`python3 scripts/check_handoff.py 055` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 14
fact-check rows: 8
totals line: 8 rows -> 7 as-is, 1 fixed, 0 removed
PASS
```
