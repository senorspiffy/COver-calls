# 03 Research hand-off - 034
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| STUCK report for 009–016 was wrong | logs/audit/2026-11-01.md vs PR #7 tree | VERIFIED |  |
| PR #8 built without PR #7's scratch-copy rule | i3-verifier.md on both branches; 032/06 | VERIFIED |  |
| PR #7 conflicts with main | trial merge in scratch | VERIFIED | only recurring-issues.md vs main; plus i3-verifier.md vs main+PR #8 |
| merge-tree available | git --version 2.43.0 | VERIFIED |  |
**Totals:** 4 rows checked → **3 VERIFIED as-is**, **1 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | IN PR status for STUCK/not started/in progress items with more steps on an unmerged branch | git ls-tree, git diff HEAD...ref | status + IN PR line | test_item_built_on_open_branch_is_in_pr_not_stuck | 8 of 8 (009–016) on main today |
| 2 | OPEN BRANCHES line: items, merges cleanly / CONFLICTS, recurring-issues edit | git merge-tree | text | test_open_branch_conflict_is_reported | 2 branches today |
| 3 | a1 daily step: IN PR/OPEN BRANCHES on top; stack dependent fixes; i2 mutations in scratch copy | – | text | grep 'item 034' | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| git or remote refs (not a git repo, git missing) | absent | branch scan skipped; no OPEN BRANCHES line (tested: not a git repo) |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| IN PR | main: request only; branch: 01–07 → IN PR | 8 IN PR, STUCK: none | ✓ |
| Totals | 3+1+0=4 | 4 | ✓ |
`python3 scripts/check_handoff.py 034` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 4
totals line: 4 rows -> 3 as-is, 1 fixed, 0 removed
PASS
```
