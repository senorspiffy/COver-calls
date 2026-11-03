# 03 Research hand-off - 040
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| W1 sandbox host api.sandbox.webull.com | https://developer.webull.com/apis/docs/sdk | VERIFIED |  |
| W2 sandbox apps approved automatically | https://developer.webull.com/apis/docs/authentication/IndividualApplicationAPI | VERIFIED |  |
| W3 sandbox data 15-minute delayed by default | https://developer.webull.com/apis/docs/market-data-api/overview | VERIFIED |  |
| W4 sandbox option data availability | – | VERIFIED (stated as an open question; first VPS run shows it) |  |
| F1 Ford Q3 on Oct 28; $0.15 dividend, record Nov 10 | businesswire release 2026-10-28 | VERIFIED |  |
| F2 Ford ex-date = Nov 10 | release gives record date only | UNSUPPORTED | kept as a labelled input in tickers.json sources ("ex-date taken = record date, T+1") |
| F3 Ford next earnings not published | https://stockanalysis.com/stocks/f/ | VERIFIED |  |
| V1 Vale last report Oct 29; next ex-date not found | https://stockanalysis.com/stocks/vale/ | VERIFIED |  |
| A1 AAL last report Oct 22; no dividend since 2020 | https://stockanalysis.com/stocks/aal/dividend/ | VERIFIED |  |
| E1 70-day gap is the person's house rule | person's decision 2026-11-03 (request.md) | VERIFIED |  |
| N1/N2 date math and $15 dividend | arithmetic + enrich() run | VERIFIED |  |
**Totals:** 11 rows checked → **10 VERIFIED as-is**, **1 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | `ccbot/tickers.py`: load_facts + enrich (asset type, earnings date or last+gap estimate, ex-div) | config/tickers.json, earnings_gap_days | Day fields | test_paper.py enrich tests | F/VALE/AAL all pass the earnings test for Dec 18 on 2026-11-03 |
| 2 | webull-paper broker: Webull quotes, fills in local SimBroker ledger | sandbox quotes | ledger, scan | test_paper end-to-end (0 order calls) | needs keys on VPS |
| 3 | `_capital` marks a held call at its quoted mid, NaN if no quote and no vol | snapshot | equity | test_paper `_capital` tests | – |
| 4 | Report labels an estimated earnings date | earnings_estimated | daily report | test_paper | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| next_earnings (tickers.json) | no date and no last_earnings, or estimate already past | EARNINGS_UNKNOWN (blocks) |
| ex_div_date / dividend (tickers.json) | either missing | dividend fields stay NaN (never 0) |
| option quote for held call | no quote and no vol | equity n/a |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| F estimate after expiry | Oct 28 + 70 > Dec 18 | Jan 6 2027 > Dec 18 2026 | ✓ |
| VALE estimate after expiry | Oct 29 + 70 > Dec 18 | Jan 7 2027 > Dec 18 2026 | ✓ |
| AAL estimate after expiry | Oct 22 + 70 > Dec 18 | Dec 31 2026 > Dec 18 2026 | ✓ |
| Dividend | 0.15 × 100 | 15 | ✓ |
| Totals | 10+1+0=11 | 11 | ✓ |
`python3 scripts/check_handoff.py 040` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 9
fact-check rows: 11
totals line: 11 rows -> 10 as-is, 1 fixed, 0 removed
PASS
```
