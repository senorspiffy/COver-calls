# 03 Research hand-off - 038
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| PR #5 has request + 05 only | git ls-tree | VERIFIED |  |
| PR #5 estimates unpublished earnings | tickers.py on branch | VERIFIED |  |
| Main blocks unknown earnings | missing.py | VERIFIED |  |
| Check never applies Scope to branches | check_pipeline.py open_branches() | VERIFIED |  |
**Totals:** 4 rows checked → **4 VERIFIED as-is**, **0 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | classify each open-branch item from the branch's own files; `BRANCH SKIPPED:` line; exit code unchanged | git show per file, classify() | BRANCH SKIPPED line | test_open_branch_item_that_skips_steps_is_reported | 1 of 1 open-branch item today |
| 2 | a1-auditor: BRANCH SKIPPED is an error, at top of report; never push to a branch you didn't open | – | text | grep 'item 038' | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| git or remote refs (not a git repo, git missing) | absent | branch scan skipped; no OPEN BRANCHES, ID CLASH or BRANCH SKIPPED from branches |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Totals | 4+0+0=4 | 4 | ✓ |
`python3 scripts/check_handoff.py 038` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 4
totals line: 4 rows -> 4 as-is, 0 fixed, 0 removed
PASS
```
