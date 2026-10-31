# 01 Research brief - 023
Prepared 2026-10-31 (R1 role, research-only item). R2's 7-language search skipped: this item is a market-data screen and makes no new strategy claims (in the spirit of item 022). Fact-check notes (R3 role) are inline: every value below was copied verbatim from the cited page by a fetch; F's quote was fetched twice independently and matched (12.33, iv30 35.485).

## Question
Which real tickers pass 001's screen (as corrected 2026-10-30) for a $3,000 account, and why?

## Findings: price and 30-day IV (Cboe delayed quotes, `https://cdn-api.cboe.com/api/global/delayed_quotes/quotes/<T>.json`)
| Ticker | Type | Quote timestamp | current_price | iv30 | Price cap ($15 stock / $28 ETF) |
|---|---|---|---|---|---|
| F | stock | 2026-10-30 13:19 | 12.33 | 35.485 | pass |
| SOFI | stock | 2026-10-30 21:28 | 16.74 | 45.45 | fail |
| NOK | stock | 2026-10-31 00:04 | 8.54 | 54.341 | pass |
| VALE | stock | 2026-10-27 00:05 | 11.9976 | 36.78 | pass |
| PBR | stock | 2026-10-31 00:04 | 22.0572 | 38.591 | fail |
| ITUB | stock | 2026-10-31 00:04 | 7.13 | 39.994 | pass |
| BBD | stock | 2026-10-22 00:04 | 4.05 | 75.526 | pass |
| AMCR | stock | 2026-10-30 14:30 | 47.1 | 32.769 | fail |
| KGC | stock | 2026-10-31 02:06 | 20.19 | 47.437 | fail |
| HBAN | stock | 2026-10-31 00:04 | 15.76 | 24.943 | fail |
| WBD | stock | 2026-09-26 00:16 | 30.87 | 6.178 | fail |
| AAL | stock | 2026-10-30 17:13 | 12.32 | 46.637 | pass |
| SNAP | stock | 2026-10-14 21:52 | 6.08 | 86.376 | pass |
| RIVN | stock | 2026-10-30 15:41 | 12.095 | 59.581 | pass |
| NU | stock | 2026-10-30 00:05 | 11.8279 | 45.062 | pass |
| GRAB | stock | 2026-10-31 00:04 | 2.73 | 51.097 | pass |
| CLF | stock | 2026-10-30 17:12 | 14.04 | 61.727 | pass |
| T | stock | 2026-10-26 18:34 | 20.775 | 28.136 | fail |
| KEY | stock | 2026-09-29 02:50 | 20.4 | 25.007 | fail |
| LUMN | stock | 2026-09-29 18:34 | 5.53 | 62.48 | pass |
| PFE | stock | 2026-10-30 14:28 | 30.405 | 26.938 | fail |
| KMI | stock | 2026-10-27 22:43 | 33.9 | 24.823 | fail |
| KWEB | ETF | 2026-10-26 21:41 | 23.19 | 28.757 | pass |
| BITO | ETF | 2026-10-20 01:22 | 10.92 | 38.967 | pass |
| UNG | ETF | 2026-10-30 18:38 | 9.085 | 61.385 | pass |
| MSOS | ETF | 2026-10-01 03:43 | 4.52 | 65.382 | pass |
| JETS | ETF | 2026-10-30 00:05 | 27.09 | 36.646 | pass |
| FXI | ETF | 2026-10-19 22:22 | 33.6 | 20.07 | fail |
| EWZ | ETF | 2026-10-29 00:05 | 33.38 | 35.152 | fail |
| SCHB | ETF | 2026-10-29 17:13 | 29.605 | 16.82 | fail |
| SCHD | ETF | 2026-10-30 16:01 | 35.79 | 12.212 | fail |
| XLF | ETF | 2026-10-30 14:01 | 56.71 | 15.343 | fail |
| SLV | ETF | 2026-10-30 21:24 | 44.38 | 43.406 | fail |
| ASHR | ETF | 2026-09-26 03:42 | 33.09 | 17.359 | fail |
| MCHI | ETF | 2026-09-27 00:08 | 52.0 | 19.187 | fail |
| EEM | ETF | 2026-10-30 21:09 | 61.08 | 27.845 | fail |
| VEA | ETF | 2026-10-28 15:51 | 70.075 | 18.001 | fail |
| IEFA | ETF | 2026-10-13 00:05 | 96.18 | 15.574 | fail |
| SPYM | ETF | 2026-10-28 23:14 | 90.539 | 13.748 | fail |
| SPLG | ETF | fetch failed | – | – | UNVERIFIED |

Feasibility count: 40 tried, 39 priced, **17 pass the price cap** (12 stocks, 5 ETFs). 8 lowest-volatility of those checked further (F, VALE, ITUB, NU, AAL, NOK, KWEB, JETS).

## Findings: option liquidity (Cboe chain `.../options/<T>.json`; fetch returns only the first ~39k of ~58k chars, so most Dec 18 rows are unreadable)
- F, 2026-10-30: 261106 C12.5 bid 0.12 ask 0.15 Δ0.3628 OI 4873; C13 bid 0.03 ask 0.05 OI 5824 (delta cut off).
- VALE, 2026-10-27: 261106 C12 0.26/0.30 Δ0.4478 OI 28; C12.5 0.10/0.14 Δ0.2471 OI 1330.
- ITUB, 2026-10-29: 261218 C8 0.15/0.25 Δ0.313 OI 1422 (spread 0.10, FAIL); C9 0.05/0.10 Δ0.146 OI 3882.
- JETS, 2026-10-30: 261106 C27 0.25/0.48 OI 225; C27.5 0.27/0.30 Δ0.3036 OI 190; C28 0.17/0.20 Δ0.2153 OI 100; C28.5 0.10/0.17 OI 20 (OI FAIL).
- NOK, 2026-10-27 13:33: 261106 C9 0/0.80 OI 3599; C9.5 0/2.23 OI 4386 (no bid; unusable snapshot).
- AAL (10-29), NU (10-27), KWEB (10-21): no call in Δ0.15–0.45 visible before the cutoff.

## Findings: earnings and dividends
- F: Q3 reported Oct 28 2026; Q4 dividend $0.15, record Nov 10, payable Dec 1 [https://www.businesswire.com/news/home/20261028111591/en/Ford-Reports-Third-Quarter-2026-Financial-Results/]. Ex-date not stated (T+1 → normally = record date; reasoning, UNVERIFIED). Next earnings NOT FOUND. Beta 1.94, 52w 11.11–17.78 [https://stockanalysis.com/stocks/f/].
- VALE: earnings Oct 29 2026; semi-annual dividend, last ex Aug 13 2026 $0.32284; next ex NOT FOUND; beta 0.70; 52w 11.43–17.94 [https://stockanalysis.com/stocks/vale/, /dividend/].
- ITUB: earnings Nov 3 2026 (before Dec 18 → FAIL); monthly dividend $0.00273, next ex Nov 4; beta 0.11 [https://stockanalysis.com/stocks/itub/].
- NU: earnings Nov 12 2026 (FAIL); no dividend; beta 0.96 [https://stockanalysis.com/stocks/nu/].
- AAL: earnings Oct 22 2026; no dividend; beta 1.38; 52w 10.09–18.79 [https://stockanalysis.com/stocks/aal/].
- NOK: earnings Oct 22 2026; ex-div Oct 27 2026 (amount NOT FOUND); 52w 5.86–17.45 [https://stockanalysis.com/stocks/nok/].
- KWEB: annual distribution, last ex Dec 22 2025 $2.09623 [https://stockanalysis.com/etf/kweb/dividend/].
- JETS: last ex Dec 24 2025 $0.2329 [https://stockanalysis.com/etf/jets/dividend/].
- "Next earnings after Dec 18" for F/VALE/AAL/NOK is reasoning from a quarterly cadence (just reported in late Oct), not a published date.

## Numbers used (show the math)
- Caps: 0.5 × 3000 / 100 = $15 (stock); (3000 − 200) / 100 = $28 (ETF). F: 1233 / 3000 = 41.1%.
- Expiry: 2026-10-30 → 2026-12-18 = 49 DTE (step 4 slack rule, as in 001 Correction).
- MODEL premiums (ccbot.pricing Black-Scholes, T = 49/365, r = 0.04, q = annual div / price, σ = Cboe iv30; not quotes): F K13.5 Δ0.259 $0.235; VALE K13 Δ0.290 $0.275; AAL K14 Δ0.264 $0.310; NU K13.5 Δ0.246 $0.264; NOK K10 Δ0.249 $0.230; KWEB K24.5 Δ0.293 $0.429; JETS K30 Δ0.254 $0.519.
- F yield: 0.235 / 12.33 = 1.9% per 49 days. VALE: 0.275 / 12.00 = 2.3%.

## Fit for a ~$3k account
F passes every test with data. VALE passes with a stale quote and uneven OI. AAL unconfirmed (no readable strike). Two names (F + VALE = $2,433) fit both caps but 001 step 1 says one position at $3k; person's call.

## Open questions
- Dec 18 chain (bid/ask/OI at Δ0.275) unreadable for all but ITUB: person checks in Webull before any trade.
- Exact ex-dates (F Q4, VALE next) and next earnings dates not published/found.
