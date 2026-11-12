# 03 Research hand-off - 054
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| W1 Cboe list not readable | cboe.com/available_weeklys | VERIFIED |  |
| W2 weekly expiries seen for 12 names | Cboe delayed JSON (truncated reads) | VERIFIED |  |
| P1 SOFI | stockanalysis sofi | VERIFIED |  |
| P2 BAC incl. Dec 4 ex-div $0.32 | stockanalysis bac, bac/dividend | VERIFIED |  |
| P3 CSX | stockanalysis csx | VERIFIED |  |
| P4 OXY | stockanalysis oxy | VERIFIED |  |
| P5 PYPL | stockanalysis pypl | VERIFIED |  |
| P6 CCL earnings Dec 18 | site estimate only | UNSUPPORTED | kept as blackout date, labelled "estimate" in sources |
| H1 weekly ranges | stockanalysis history pages | VERIFIED |  |
| X1 excluded names | stockanalysis | VERIFIED |  |
**Totals:** 10 rows checked → **9 VERIFIED as-is**, **1 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | tickers.json: SOFI, BAC, CSX, OXY, PYPL, CCL | 01 facts | Day fields | test_weekly_account_gives_each_stock_8000_and_has_facts | – |
| 2 | config/weekly.json: 12 names, $96,200, frac 1/12, max 12 | person's ask | config | same test | 12/12 earnings known on Nov 13 |
| 3 | Run with --variant V2 --state-dir state_weekly --out reports_weekly | – | reports | scratch scan on the VPS | weekly Fridays 5–9 DTE |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| ex-div dates (most names) | null | dividend NaN, never 0 |
| CCL real earnings date | estimate used | EARNINGS_BLACKOUT from Dec 18 expiries |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Cash | 12×8000+200 | 96,200 | ✓ |
| Cap | 96,200/12 | 8,016.67 | ✓ |
| PYPL fits | 59.24×100 ≤ 8,016 | 5,924 | ✓ |
| Totals | 9+1+0=10 | 10 | ✓ |
`python3 scripts/check_handoff.py 054` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 11
fact-check rows: 10
totals line: 10 rows -> 9 as-is, 1 fixed, 0 removed
PASS
```
