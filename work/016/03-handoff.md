# 03 Research hand-off - 016
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| ETF shows n/a | A1 scan | VERIFIED |  |
| Header misses 005 | 001 L119/L147 | VERIFIED |  |
**Totals:** 2 rows checked → **2 VERIFIED as-is**, **0 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | `_earnings_text`: none (ETF) / none in data / n/a (not supplied) | ctx | report text | test_etf_earnings_shown_as_none_not_na, test_earnings_text_cases | – |
| 2 | 001 labels → (items 003, 004, 005, 008) | 001 | 2 labels | grep | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| next_earnings | unknown | n/a (not supplied) |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| ex-div days | 2026-12-18 − 2026-10-30 | 49 | ✓ |
| Totals | 2+0+0=2 | 2 | ✓ |
`python3 scripts/check_handoff.py 016` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 2
totals line: 2 rows -> 2 as-is, 0 fixed, 0 removed
PASS
```
