# 03 Research hand-off - 048
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| T1 AT&T | stockanalysis t | VERIFIED |  |
| T2 Verizon | stockanalysis vz | VERIFIED |  |
| T3 Pfizer | stockanalysis pfe statistics | VERIFIED |  |
| T4 Kinder Morgan | stockanalysis kmi | VERIFIED |  |
| T5 Comcast | stockanalysis cmcsa statistics | VERIFIED |  |
| T6 KeyCorp | stockanalysis key | VERIFIED |  |
| T7 Huntington | stockanalysis hban | VERIFIED |  |
| T8 Petrobras | stockanalysis pbr | VERIFIED |  |
| T9 Itaú report happened | Oct 31 snapshot only | UNSUPPORTED | kept: date entered as last_earnings, labelled in sources |
| T10 Kinross amount | headline only | UNSUPPORTED | kept date, amount left null |
| X1 BAC/INTC price | stockanalysis | VERIFIED |  |
**Totals:** 11 rows checked → **9 VERIFIED as-is**, **2 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | config/tickers.json: 10 new entries | 01 facts | Day fields | test_every_universe_ticker_has_sourced_facts | – |
| 2 | config/practice.json: 13 stocks, $65,200, frac 1/13 | person's decision | config | test_practice_gives_each_stock_5000 | 12/13 clear Dec 18 on Nov 9 |
| 3 | config/paper.json cash 5000 | person's decision | config | test_main_paper_account_is_5000_two_stocks | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| PBR last_earnings after Nov 10 | not entered | EARNINGS_UNKNOWN (blocks PBR) |
| ex-div dates not listed | null | dividend NaN, never 0 |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Cash | 13×5000+200 | 65,200 | ✓ |
| Cap | 65,200/13 | 5,015.38 | ✓ |
| VZ fits | 43.10×100 ≤ 5,015 | 4,310 | ✓ |
| BAC out | 50.52×100 > 5,015 | 5,052 | ✓ |
| Totals | 9+2+0=11 | 11 | ✓ |
`python3 scripts/check_handoff.py 048` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 16
fact-check rows: 11
totals line: 11 rows -> 9 as-is, 2 fixed, 0 removed
PASS
```
