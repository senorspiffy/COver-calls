# 03 Research hand-off - 018
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| Example fill $0.24 meets ≤ 50% | 0.24/0.47 | WRONG | limit $0.23 (48.9%) |
| $0.235 is enterable as a limit | order tickets use a minimum tick | WRONG | rule now says round down to the option's minimum tick |
| 'day ≤ 12 of 35' is the first third | 35/3 = 11.7 | WRONG | day ≤ 11 |
| Profit at $0.23 = $23.80 | arithmetic | VERIFIED |  |
**Totals:** 4 rows checked → **1 VERIFIED as-is**, **3 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it |
|---|---|---|---|---|
| 1 | Step 6: limit = 50% rounded down to minimum tick; day ≤ 11 of 35 | work/001/03-handoff.md | corrected rule | Self-check rows 'exit trigger', 'exit timing' |
| 2 | Worked example: $0.23 fill, $23.80 | work/001/03-handoff.md | corrected example | Self-check row |
| 3 | Guardrail: R3 duty 5 requires each example be run against its rule's trigger | r3-fact-checker.md | duty | I3/A1 check Self-check rows |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Totals add up | as-is + fixed + removed = rows | 1 + 3 + 0 = 4 | ✓ |
| Guardrail present in map | BUG → guardrail step | step 3 | ✓ |
`python3 scripts/check_handoff.py 018` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 4
totals line: 4 rows -> 1 as-is, 3 fixed, 0 removed
PASS
```
