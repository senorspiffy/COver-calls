# 03 Research hand-off - 052
Status: READY
Recurring issues checked (R3): RI-011 (this item), RI-009 (open-branch view stays; only its file lists change), RI-007 (no step skipped), RI-002 (no data path).
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| `open_branches()` uses `HEAD...ref` and a single `merge-base` | scripts/check_pipeline.py `def open_branches` | VERIFIED |  |
| `A...B` diffs from one merge base to B | https://git-scm.com/docs/git-diff | VERIFIED |  |
| `merge-base --all` can print several bases | https://git-scm.com/docs/git-merge-base | VERIFIED |  |
| `merge-tree --write-tree` prints the result tree first, also on conflict | https://git-scm.com/docs/git-merge-tree | VERIFIED |  |
| Today: two bases, 3 items / 3 rule files listed; merge-tree diff gives 051 only | A1 run 2026-11-10 | VERIFIED |  |
**Totals:** 5 rows checked → **5 VERIFIED as-is**, **0 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | run merge-tree first; `changed(paths)` = `git diff --name-only HEAD <tree>`; fall back to `HEAD...ref` if merge-tree fails | git refs | items, recurring, rules | criss-cross fixture lists only the branch's item and rule file | – |
| 2 | ID CLASH: request absent from every `merge-base --all` base | git refs | clashes | existing clash test passes | – |
| 3 | docstring: changes = what a merge would bring in (item 052) | – | – | read | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| merge-tree tree (git < 2.38) | merge-tree fails | fall back to `HEAD...ref`; CONFLICTS shows unknown as today |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Totals | 5 + 0 + 0 | 5 | ✓ |
| Items today | 3 − 2 | 1 | ✓ |
| Rule files today | 3 − 2 | 1 | ✓ |
`python3 scripts/check_handoff.py 052` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 3
fact-check rows: 5
totals line: 5 rows -> 5 as-is, 0 fixed, 0 removed
PASS
```
