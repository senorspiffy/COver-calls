# 03 Research hand-off - 027
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| L49 is 3.12-only | PEP 701 + python3.11 run | VERIFIED |  |
| Other files compile on 3.11 | py_compile | VERIFIED |  |
| UTF-8 commit was verified | no 06 / item | WRONG | 026 |
**Totals:** 3 rows checked → **2 VERIFIED as-is**, **1 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | Split L49 into two lines | check_handoff.py | 3.11 runs | python3.11 run → PASS | – |
| 2 | test_fstrings_parse_on_python_310 + self-test | tests/test_safety.py | test | fails on old line | – |
| 3 | i3: python3.11 -m py_compile when present | i3-verifier.md | instruction | grep | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| python3.11 on the machine | absent | i3 skips that step and says so; the token test still runs |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Old line fails | test on old file | ['check_handoff.py:49'] | ✓ |
| Totals | 2+1+0=3 | 3 | ✓ |
`python3 scripts/check_handoff.py 027` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 1
fact-check rows: 3
totals line: 3 rows -> 2 as-is, 1 fixed, 0 removed
PASS
```
