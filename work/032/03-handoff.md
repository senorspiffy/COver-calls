# 03 Research hand-off - 032
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| python3.11 present here | ls /usr/bin | VERIFIED |  |
| i3 step is manual | i3-verifier.md | VERIFIED |  |
**Totals:** 2 rows checked → **2 VERIFIED as-is**, **0 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | test_every_py_compiles_on_oldest_python (skip with reason if no 3.10/3.11) | git ls-files *.py | pass/fail list | mutation: add `type X = int` → fails | – |
| 2 | i3 step 2 points at the test | – | text | grep | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| python3.10/3.11 on PATH | absent | test SKIPPED with reason; I3 says so in 06 |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Mutation | `type X = int` in a script → fail | check_pipeline.py:105 reported | ✓ |
| Totals | 2+0+0=2 | 2 | ✓ |
`python3 scripts/check_handoff.py 032` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 2
totals line: 2 rows -> 2 as-is, 0 fixed, 0 removed
PASS
```
