# 03 Research hand-off - 009
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| One text for three causes | report.py L122 | VERIFIED |  |
| NaN R with T ≥ 8 gets the months text | code reading | VERIFIED |  |
**Totals:** 2 rows checked → **2 VERIFIED as-is**, **0 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | `pbo_na_reason(R)`; `pbo_cscv` uses it; `walk_forward` stores `pbo_na` | R matrix | reason text or None | test_pbo_na_names_each_cause | – |
| 2 | Report prints `n/a (<reason>)` | wf['pbo_na'] | report line | test_short_csv_reports_pbo_na_without_warnings | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| wf['pbo_na'] (older result dict) | absent | 'n/a (reason not recorded)' |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Short CSV | T=0 < 8; N=8 ≥ 2; R empty | 'needs >= 8 non-held-out months, have 0' | ✓ |
| Totals | 2+0+0=2 | 2 | ✓ |
`python3 scripts/check_handoff.py 009` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 2
totals line: 2 rows -> 2 as-is, 0 fixed, 0 removed
PASS
```
