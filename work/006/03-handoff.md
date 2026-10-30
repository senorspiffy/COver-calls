# 03 Research hand-off - 006
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| No Scope field in template | templates/request.md | VERIFIED |  |
| Only I3 writes 07 | i3-verifier.md | VERIFIED |  |
| A1 per-item needs 07 | a1-auditor.md | VERIFIED |  |
**Totals:** 3 rows checked → **3 VERIFIED as-is**, **0 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it |
|---|---|---|---|---|
| 1 | Add `Scope: FULL | RESEARCH ONLY` to request template | templates/request.md | field | file contains line |
| 2 | run-item.md: research-only path, default FULL | run-item.md | path | text present |
| 3 | R3 writes 07-audit-task.md for research-only | r3-fact-checker.md | duty | text present |
| 4 | 001 request uses the new value | work/001/request.md | Scope line | grep |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Totals add up | as-is + fixed + removed = rows | 3 + 0 + 0 = 3 | ✓ |
`python3 scripts/check_handoff.py 006` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 3
totals line: 3 rows -> 3 as-is, 0 fixed, 0 removed
PASS
```
