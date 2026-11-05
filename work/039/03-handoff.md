# 03 Research hand-off - 039
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| %cs gives YYYY-MM-DD | git log run | VERIFIED |  |
| PR #5 last commit 2026-10-31 | git log | VERIFIED |  |
**Totals:** 2 rows checked → **2 VERIFIED as-is**, **0 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | append `; last commit <date> (<n> days)` to each OPEN BRANCHES line, n to --today | git log -1 --format=%cs | text | test_open_branch_line_shows_last_commit_age | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| git or remote refs (not a git repo, git missing) | absent | branch scan skipped; no OPEN BRANCHES, ID CLASH or BRANCH SKIPPED from branches |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Totals | 2+0+0=2 | 2 | ✓ |
`python3 scripts/check_handoff.py 039` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 2
totals line: 2 rows -> 2 as-is, 0 fixed, 0 removed
PASS
```
