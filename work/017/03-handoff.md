# 03 Research hand-off - 017
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| Step 1 formula is cash − $200 buffer | 03-handoff step 1 | VERIFIED |  |
| '2 at ≥ $5.6k' / 'one ≤ $55' pass that formula | arithmetic | WRONG | need $5,800 / $5,700; replaced with $5,000: 2×$24 or 1×$48; $5,600: 2×$27 or 1×$54; 2×$28 needs $5,800 |
| Step 9(a) 'single stocks only at ≥ $5.6k' | arithmetic | WRONG | tied to step 1 instead of a fixed number |
| Worked example $5,600 with two $27 positions passes | 5,400 ≤ 5,400 | VERIFIED |  |
**Totals:** 4 rows checked → **2 VERIFIED as-is**, **2 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it |
|---|---|---|---|---|
| 1 | Rewrite step 1 thresholds + outputs from formula | work/001/03-handoff.md | corrected step 1 | Self-check rows in 001 |
| 2 | Step 9(a) refers to step 1 | work/001/03-handoff.md | corrected 9(a) | Self-check row 9(a) |
| 3 | Guardrail: Self-check section in templates/research-handoff.md + R3 duty 5 + A1 spot-check | template, agent files | new section/duty | script fails when section missing |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Totals add up | as-is + fixed + removed = rows | 2 + 2 + 0 = 4 | ✓ |
| Guardrail present in map | BUG → guardrail step | step 3 | ✓ |
`python3 scripts/check_handoff.py 017` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 4
totals line: 4 rows -> 2 as-is, 2 fixed, 0 removed
PASS
```
