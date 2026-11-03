# 03 Research hand-off - 028
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| 002–008 FAIL Totals/Self-check | script run | VERIFIED |  |
| All predate 77273f0 | git log | VERIFIED |  |
**Totals:** 2 rows checked → **2 VERIFIED as-is**, **0 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | `--all` mode + LEGACY dict (002–008) with 'never add' comment | work/* | one line per item, exit 1 on FAIL | test_check_handoff_all_legacy_and_fail | – |
| 2 | a1 + README use --all | docs | instructions | grep | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| 03-handoff.md | absent | 'no hand-off' |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| LEGACY count | 002..008 | 7 | ✓ |
| Totals | 2+0+0=2 | 2 | ✓ |
`python3 scripts/check_handoff.py 028` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 2
totals line: 2 rows -> 2 as-is, 0 fixed, 0 removed
PASS
```
