# 03 Research hand-off - 036
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| Only conflict PR #7 vs main is recurring-issues.md | git merge-tree | VERIFIED |  |
| A1 edits the file daily on main | git log -- logs/recurring-issues.md | VERIFIED |  |
**Totals:** 2 rows checked → **2 VERIFIED as-is**, **0 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | run-item + i2: fix branches don't edit the file; status in 05/06 | – | text | grep 'item 036' | – |
| 2 | a1 copies status on main | – | text | grep | – |
| 3 | OPEN BRANCHES flags a branch that edits it (with 034) | git diff HEAD...ref | text | test_item_built_on_open_branch_is_in_pr_not_stuck | PR #7 flagged today |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| – | – | – |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Flag | PR #7 edits file → flagged | flagged | ✓ |
| Totals | 2+0+0=2 | 2 | ✓ |
`python3 scripts/check_handoff.py 036` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 2
totals line: 2 rows -> 2 as-is, 0 fixed, 0 removed
PASS
```
