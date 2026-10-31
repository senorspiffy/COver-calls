# 03 Research hand-off - 019
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| Table has 76 rows | script | WRONG | 77 |
| 60 VERIFIED as-is | 77 − 16 | WRONG | 61 |
| 12 fixed / 4 removed | names in Totals line | VERIFIED |  |
| Removed list (7) vs 4 removed | section text | WRONG | definitions + note which 3 entries are 'fixed' |
| Old file fails the new script | script run | VERIFIED |  |
**Totals:** 5 rows checked → **2 VERIFIED as-is**, **3 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it |
|---|---|---|---|---|
| 1 | Fix Totals + removed-list note | work/001/03-handoff.md | 77 → 61/12/4 | script PASS |
| 2 | Add scripts/check_handoff.py | work/<ID>/03-handoff.md | PASS/FAIL, exit code | fails on old 001, passes on new |
| 3 | R3 duty 7, I3 step 2, A1 daily run; definitions in template | agent files, template | duties | grep for check_handoff in agent files |
| 4 | Append correction line to logs/research/2026-10-30.md | — | log line | line present |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Totals add up | as-is + fixed + removed = rows | 2 + 3 + 0 = 5 | ✓ |
| Guardrail present in map | BUG → guardrail step | step 3 | ✓ |
`python3 scripts/check_handoff.py 019` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 5
totals line: 5 rows -> 2 as-is, 3 fixed, 0 removed
PASS
```
