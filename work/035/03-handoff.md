# 03 Research hand-off - 035
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| 009–016 would show complete unaudited | scratch merge PR #8 + PR #7 | VERIFIED |  |
| Only 002, 003, 017–022 lack an A1 line today | grep on main + PR #8 | VERIFIED |  |
| test pins item 112 (10-30, no line) as complete | tests/test_pipeline_check.py | VERIFIED |  |
**Totals:** 3 rows checked → **3 VERIFIED as-is**, **0 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | replace date cutoff with closed PRE_A1_LINE list | 07 text | status | test_complete_needs_a1_result (112 → awaiting, 017 → complete) | 8 of 8 (009–016) awaiting after PR #7 merge |
| 2 | test updated | – | – | pytest | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| Date line in request.md | absent | no longer used for the A1 check; the item needs an A1 line unless on the list |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| List | items with 07 and no A1 line today = list | 8 = 8 | ✓ |
| Totals | 3+0+0=3 | 3 | ✓ |
`python3 scripts/check_handoff.py 035` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 3
totals line: 3 rows -> 3 as-is, 0 fixed, 0 removed
PASS
```
