# 03 Research hand-off - 051
Status: READY
Recurring issues checked (R3): RI-009 (open-branch view stays; only main and refs already in main leave it), RI-007 (no step skipped), RI-002 (no data path).
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| Both functions use `branch -r --no-merged HEAD` | scripts/check_pipeline.py L271, L330 | VERIFIED |  |
| main and the thread mirror were listed with the 036 note | A1 run 2026-11-09 on PR #15 branch | VERIFIED |  |
| Item 036: only A1's commit on main edits recurring-issues | run-item.md L12; check_pipeline.py docstring L39–40 | VERIFIED |  |
| `merge-base --is-ancestor` exits 0 when ref is in main | https://git-scm.com/docs/git-merge-base | VERIFIED |  |
| `rev-list --count HEAD..origin/main` counts main-only commits | https://git-scm.com/docs/git-rev-list | VERIFIED |  |
**Totals:** 5 rows checked → **5 VERIFIED as-is**, **0 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | `open_branches()` skips `origin/main` and refs whose tip is in `origin/main`, only when `origin/main` is not in HEAD | git refs | branch list | fixture: branch behind main lists neither | – |
| 2 | `MAIN AHEAD: origin/main has <n> commits not in HEAD; merge it before building (item 051)` | `rev-list --count` | report line | same fixture; on main no such line | – |
| 3 | `next_id()` unchanged | – | – | fixture: `--next-id` on the behind branch counts main's new ID | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| `origin/main` | ref missing | no MAIN AHEAD line; open branches as before |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Totals | 5 + 0 + 0 | 5 | ✓ |
| False lines today | 2 listed − 2 removed | 0 | ✓ |
`python3 scripts/check_handoff.py 051` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 2
fact-check rows: 5
totals line: 5 rows -> 5 as-is, 0 fixed, 0 removed
PASS
```
