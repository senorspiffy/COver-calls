# 03 Research hand-off - 037
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| Two items numbered 025 | git show on both refs | VERIFIED |  |
| Both added since merge base | git cat-file at 8d5c9b8 | VERIFIED |  |
| Check hides PR #5's item | check_pipeline.py output | VERIFIED |  |
**Totals:** 3 rows checked → **3 VERIFIED as-is**, **0 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | `ID CLASH:` line: both sides added request.md since merge base, texts differ | git merge-base, git show, cat-file | ID CLASH line | test_same_id_on_main_and_open_branch_is_a_clash | 1 of 1 open branch today (025) |
| 2 | `--next-id` over HEAD and every unmerged remote branch | work/, git ls-tree | next ID | test_next_id_counts_open_branches | – |
| 3 | a1-auditor, README, templates/request.md: take IDs from --next-id; ID CLASH at top of report | – | text | grep 'item 037' | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| git or remote refs (not a git repo, git missing) | absent | branch scan skipped; no OPEN BRANCHES, ID CLASH or BRANCH SKIPPED from branches |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Totals | 3+0+0=3 | 3 | ✓ |
`python3 scripts/check_handoff.py 037` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 3
totals line: 3 rows -> 3 as-is, 0 fixed, 0 removed
PASS
```
