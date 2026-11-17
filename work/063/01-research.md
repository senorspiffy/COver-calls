# 01 Research brief - 063
## Question
`ccbot/realtest.py` reads the stretch before a ticker's first listed earnings date as "no earnings". How long is that stretch for each ticker in `data/real/earnings/`, which real reports fall inside it, and what edge rule (request § Guardrail 1) actually catches BAC, CSX, USB and VALE without a silent sale?

Primary sources: repo code and data (paths below, read 2026-11-14 on branch daily-fixes/2026-11-14) and the companies' own Q4 2019 releases (URLs). Recurring issue: RI-002 (ESCALATED, occurrence 10 is this item). No brokerage contacted.

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
Code path (repo):
1. The only gap check is between consecutive dates: `gaps = sum((b - a).days > EARNINGS_GAP_WARN for a, b in zip(earnings, earnings[1:]))` (`ccbot/realtest.py` L183). `EARNINGS_GAP_WARN = 120` (L61). It only warns. It never blocks a sale, inside interior gaps either.
2. `_earnings_known(td, d)` is `bool(td.earnings) and td.earnings[-1] >= d` (L372-374). That covers the trailing edge (no future date leads to EARNINGS_UNKNOWN). The leading edge has no check: any day before the first listed date counts as "known".
3. `_earnings_between(td, a, b)` (L368-369) can only find listed dates. A real report before the first listed date can never produce EARNINGS_BLACKOUT.
4. The warnings reach `reports/real/` only through `td.warnings`, set in `load_ticker` (L139-185, L224-225), then `summarize` "warnings" (L595), then `summary.json` `counts_bot_rule_bid` (L745-747). `load_ticker` gets no `start`. The sale window is fixed later, in `simulate(start=...)`: its first day is the first snapshot on or after `start` (L397-400).
5. Today no report warns about the edge. The `reports/real/summary.json` "warnings" fields hold only "earnings: N gap(s) > 120 days between dates" and "options: N quote rows dropped" (grep, 18 rows).

Data (repo):
6. The prices start before the earnings file does. `data/real/prices/BAC.csv` row 1 is 2019-01-02. `scripts/fetch_real_data.py` L149 has the default `--start 2019-01-01`. The `realtest.py` CLI help (L797) says "DoltHub has one 2019 snapshot, then daily/MWF from 2020-01-06". The date of that 2019 snapshot is UNVERIFIED here (options are .csv.gz, not read).
7. The first listed earnings dates, from row 2 of each `data/real/earnings/*.csv`: AAL, CMCSA, HBAN, KEY 2020-01-23; KMI 01-22; PFE 01-28; MDLZ, PYPL, T 01-29; MO, VZ 01-30; F 02-04; BMY 02-06; ITUB 02-10; KGC 02-12; PBR 02-19; OXY 02-27; BAC, USB 04-15; CSX 04-22; VALE 04-28. `SPY.csv` is empty (ETF, exempt).
8. The listed cadence is quarterly: BAC 2020-04-15, then 07-16, then 10-14; CSX 04-22, 07-22, 10-21; USB 04-15, 07-15, 10-14 (rows 2-4 of each file).
9. VALE is not in the results. `summary.json` skipped: "option quotes only 2020-01-06 to 2020-12-02 (< 3.0 years)".

Real reports inside the hole:
10. Bank of America filed its Q4/FY2019 results 8-K on January 15, 2020 [https://www.businesswire.com/news/home/20200115005654/en/Bank-of-America-Corporation-Filed-a-Form-8-K].
11. U.S. Bancorp's "Reports Fourth Quarter 2019 Results" release is dated January 15, 2020 [https://ir.usbank.com/news-events/news/news-details/2020/U.S.-Bancorp-Reports-Fourth-Quarter-2019-Results-01-15-2020/default.aspx].
12. CSX's Q4/FY2019 results release is datelined January 16, 2020 [https://www.sec.gov/Archives/edgar/data/277948/000027794820000004/pressreleaseq42019.htm].
13. VALE's Q4 2019 report date is UNVERIFIED (not searched: VALE is skipped by min_years, finding 9).
14. The earnings source is DoltHub `post-no-preference/earnings`, table `earnings_calendar` [https://www.dolthub.com/repositories/post-no-preference/earnings] (`scripts/fetch_real_data.py` L7, L123). Why its history starts in 2020 is UNVERIFIED.

Effect in the current reports (repo):
15. These sales held a call through a report that is not in the file. `reports/real/trades_BAC.csv` 2020-01-06 to 2020-02-21, $37 strike, expired. `trades_USB.csv` 2020-01-06 to 2020-02-21, $60, expired. `trades_CSX.csv` 2020-01-06 to 2020-02-21, $77.5, assigned. Each life contains the report dated in findings 10-12.
16. These sales are also inside the hole, but no report is missing from their life: BAC 2020-02-21 to 2020-03-20 and CSX 2020-02-21 to 2020-03-20 (same files). Under any "unknown before first date" rule they become EARNINGS_UNKNOWN.
17. 061's measured "247 vs 250" (`work/061/01-research.md` L203-209) comes from a different rule. `work/061/diag_keep.py` L12 blocks unless a date lies in [d-120, d]. That also blocks inside interior gaps (OXY 8 to 7), and the path shifts (CSX 37 to 38). It is not the count for a leading-edge-only rule.

## Numbers used (show the math)
Lead = first listed date minus the first sale day, which is 2020-01-06 (the first snapshot at `--start 2020-01-01`, pinned by `tests/test_realtest.py` L415).
- BAC, USB: Jan 6 to Apr 15 = 25 (Jan 7-31) + 29 (Feb 2020) + 31 + 15 = **100 days**
- CSX: 25 + 29 + 31 + 22 = **107 days**. VALE: 25 + 29 + 31 + 28 = **113 days**
- OXY: 25 + 27 = 52. PBR: 25 + 19 = 44. KGC: 37. ITUB: 35. BMY: 31. F: 29. The other 11 are 16-24 days.
- **All 21 leads are under 120.** The rule written in request § Guardrail 1 ("data start to first earnings date > EARNINGS_GAP_WARN days") would therefore flag **none** of BAC/CSX/USB/VALE if "data start" is the first sale day.
- If "data start" were the price start (2019-01-02), every lead would be over 120. Example: AAL 2019-01-02 to 2020-01-23 = 386 days. All 21 stocks would warn, so the warning would carry no information. A start at `min(td.chain)` (the 2019 snapshot) has the same problem.
- Quarterly spacing in the file (finding 8): BAC 07-16 - 04-15 = 92 d, 10-14 - 07-16 = 90 d. CSX 91, 91. USB 91, 91. A lead longer than about one quarter (about 90 days) can hide a report, and a 120-day bar cannot see a lead of 100-113 days.
- Check against the sources: BAC lead 100 > 91, report Jan 15 inside it (finding 10). USB 100, Jan 15 (11). CSX 107, Jan 16 (12). OXY lead 52 < 90: no hidden quarter expected (its Q4 2019 report is not checked here, UNVERIFIED).

## Fit for a ~$3k account
- The live bot is not affected. It uses snapshot `next_earnings` with MISSING_POLICY `EARNINGS_UNKNOWN` (RI-002 entry, logs/recurring-issues.md L25). This is a research-only backtest path.
- A call held through an unlisted report carries earnings-gap assignment risk that the backtest scores as none. On a 1-lot account, that one call is the whole position. The CSX 2020-01-06 call was assigned (finding 15).
- For the person: fewer sales in early 2020 (2 BAC, 1 USB, 2 CSX at most, from findings 15-16). 061 says A1-A4 do not change (finding 17, different rule). The new count must be measured, not assumed.

## Open questions
1. **Threshold (for R3/I1).** The request's 120-day leading-edge bar misses every known case (Numbers). Options:
   - (a) Fail closed: every day before the first listed date is EARNINGS_UNKNOWN, with a warning showing the lead in days. A call whose expiry is on or after the first date is EARNINGS_BLACKOUT anyway, so this equals "no sale before the first listed date". It also blocks a few calls that are probably fine, e.g. any OXY call expiring before 02-27.
   - (b) Hole only when the lead is longer than the ticker's own shortest listed interval (about 90 d here). That is a labelled approximation.
   - (c) 061's lookback rule (a date must lie in [d-120, d]). It also blocks inside interior gaps, which is outside 063's scope.
   R1 sees (a) as the one that keeps "unknown" unknown (RI-002 root cause). This is not a decision.
2. **Where to compute it.** It must run in `simulate` against its first sale day, because `load_ticker` has no `start` (finding 4). The warning then needs a way into `summarize`/`summary.json`, e.g. `df.attrs` plus a `warnings` merge, so that it shows in `reports/real/` (request § What we want).
3. **Existing tests will move (for I1's plan, not a weakening).** `_tiny` fixtures (tests/test_realtest.py L193-210) start 2024-01-02 with earnings [2024-06-01], a lead of 151 d. Under any edge rule, the "control" sales in `test_earnings_today_blocks` L216, `test_take50_only_in_first_third`, `test_sales_under_3_cents_are_counted_not_blocked` and L380 become EARNINGS_UNKNOWN. They need a prior date such as 2023-10-25 added. `REAL_BAC` (L389-400: calls_sold 24, rej_EARNINGS_UNKNOWN 20 under BOT_RULE) must be re-measured by I2. `_make` fixtures (first earnings 2019-01-25, 23 d after 2019-01-02) should be unaffected (UNVERIFIED until run).
4. Interior gaps over 120 d (CMCSA, MDLZ, MO, T, VZ; 061/01 L199) still only warn and still sell. That is out of 063's scope as written. R3 should say so explicitly.
5. VALE's and OXY's Q4 2019 report dates: UNVERIFIED (not needed for the 17 tickers in results; OXY only matters for option (a)'s cost).
