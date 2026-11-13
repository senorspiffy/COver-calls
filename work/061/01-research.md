# 061 Results: covered calls vs buy-and-hold on real option quotes

Research only. Paper only. Nothing was bought; all data is free.

## Verdict
**No edge found.** On 17 candidate stocks, Jan 2020 to Nov 2026, the bot's own rule (0.25-0.30
delta, 30-45 days, no call held through earnings, held to expiry, sold at the bid) **trailed simply
holding the shares by a median 1.8 pts a year** and cut the worst drawdown by only a median 1.8 pts.
The BXM index trailed SPY by 6.9 pts a year over the same dates. Walk-forward (picking the
rule every 6 months from the prior 2 years) did no better: median 2.7 pts a year behind holding.
Against the pass criteria written before any result (`pass-criteria.md`): **A1 fail, A2 fail,
A3 pass, A4 fail, A5 fail.** So the "more than $5k" gate can't be passed on this evidence.

## Data
| What | Source | Notes |
|---|---|---|
| Call bid/ask, IV, delta, 5-80 days to expiry | DoltHub `post-no-preference/options` `option_chain` (https://www.dolthub.com/repositories/post-no-preference/options) | Mon/Wed/Fri snapshots Jan 2020 to mid-2024, daily from Sep 2024; gap 2024-07-29 to 08-12 |
| ATM IV and historical vol | same, `volatility_history` | |
| Daily prices (unadjusted), dividends, splits | DoltHub `post-no-preference/stocks` (https://www.dolthub.com/repositories/post-no-preference/stocks) | |
| Earnings dates | DoltHub `post-no-preference/earnings` (https://www.dolthub.com/repositories/post-no-preference/earnings) | |
| BXM | Cboe `BXM_History.csv` (https://cdn.cboe.com/api/global/us_indices/daily_prices/BXM_History.csv) | |

Dropped: **KGC** (no options on DoltHub), **VALE, PBR, ITUB** (options only Jan-Dec 2020).
Paid sources (ORATS, OptionsDX, Cboe DataShop) would add per-strike IV and every trading day; not bought.

## Bot rule, bid fills, per stock (2020-01-06 to 2026-11-12)
CAGR includes dividends reinvested in both. "Called" = share of calls that ended in assignment.
"IV>RV" = share of calls whose sold IV beat the volatility that actually happened over the call's life.

| Stock | CC CAGR | Hold CAGR | Gap | CC max DD | Hold max DD | Calls | Called | Sold IV | Realized | IV>RV |
|---|---|---|---|---|---|---|---|---|---|---|
| AAL | -4.4% | -9.9% | **+5.5** | -67% | -70% | 71 | 20% | 52% | 51% | 63% |
| BAC | 0.4% | 7.8% | -7.4 | -48% | -49% | 73 | 40% | 27% | 28% | 53% |
| BMY | 6.5% | 3.4% | **+3.1** | -41% | -48% | 66 | 26% | 23% | 22% | 62% |
| CMCSA | -4.7% | -5.4% | **+0.7** | -52% | -60% | 75 | 21% | 27% | 24% | 71% |
| CSX | 10.2% | 13.4% | -3.2 | -39% | -41% | 67 | 31% | 26% | 30% | 69% |
| F | 2.2% | 8.7% | -6.5 | -56% | -57% | 69 | 26% | 41% | 39% | 58% |
| HBAN | 3.0% | 5.8% | -2.9 | -51% | -53% | 62 | 24% | 33% | 34% | 58% |
| KEY | 0.3% | 6.1% | -5.8 | -61% | -65% | 71 | 25% | 34% | 37% | 58% |
| KMI | 10.3% | 12.0% | -1.7 | -55% | -55% | 71 | 27% | 25% | 26% | 52% |
| MDLZ | 7.3% | 5.7% | **+1.6** | -32% | -30% | 63 | 24% | 20% | 20% | 57% |
| MO | 11.6% | 14.9% | -3.3 | -37% | -39% | 68 | 34% | 21% | 21% | 62% |
| OXY | -2.1% | 5.9% | -8.0 | -79% | -80% | 58 | 35% | 45% | 48% | 64% |
| PFE | 0.0% | 0.7% | -0.7 | -51% | -59% | 64 | 23% | 25% | 25% | 61% |
| PYPL | -9.2% | -8.7% | -0.4 | -80% | -87% | 64 | 25% | 37% | 39% | 53% |
| T | -3.4% | -2.3% | -1.1 | -51% | -56% | 72 | 19% | 22% | 22% | 57% |
| USB | -0.3% | 5.0% | -5.3 | -49% | -52% | 73 | 30% | 28% | 30% | 55% |
| VZ | 0.2% | 2.0% | -1.8 | -46% | -41% | 74 | 27% | 19% | 19% | 55% |
| *SPY (check)* | 11.4% | 14.8% | -3.4 | -32% | -34% | 82 | 49% | 16% | 17% | 49% |

Pattern: covered calls only won on stocks that fell or went nowhere (AAL, CMCSA, PYPL, PFE) or
had one sharp reversal (BMY). On every stock that rose, giving up the upside cost more than the
premium paid. Fill quality matters but doesn't change the answer: bid to mid adds ~0.5-1 pt/yr.

## Pooled tests (bot rule, bid)
| # | Result | Pass? |
|---|---|---|
| A1 | 1,161 calls: sold IV > realized vol on 59%, but mean option P&L **-0.31% of the share price per call** after fills and fees | **Fail** (P&L < 0) |
| A2 | 6 of 17 stocks within 1 pt/yr of holding (needed 9) | **Fail** |
| A3 | Drawdown no worse than holding on 15 of 17 (88%) | Pass |
| A4 | Median return / max drawdown: 0.005 covered calls vs 0.094 holding | **Fail** |
| A5 | Walk-forward Jan 2022-Nov 2026, median gap -2.7 pts/yr; it beat holding on 5 of 17 | **Fail** |
| A6 | BXM 7.9%/yr, max DD -30%; SPY total return 14.8%/yr, max DD -34% | (context) |

At-the-money IV did run above the next 30 days' realized vol on 54-75% of days (median ~64%), but
by only about 1 vol point. The 0.25-0.30 delta strikes we sell carry less of that premium.

## What the 90-variant grid says (in-sample, bid fills, median across 17 stocks)
| Choice | Gap vs holding per year | Drawdown saved | Called away |
|---|---|---|---|
| Delta 0.15 / 0.20 / **0.275** / 0.35 / 0.45 | -1.1 / -2.0 / **-3.4** / -3.9 / -4.1 pts | 0.7 / 1.2 / 1.8 / 2.3 / 4.4 pts | 13% / 17% / 25% / 31% / 40% |
| 5-9 / 14-24 / 30-45 days | -2.3 / -2.9 / -2.2 pts | ~2 pts each | 26% / 26% / 20% |
| Hold through earnings / skip earnings | -2.7 / -2.2 pts | same | |
| Hold to expiry / buy back at 50% / roll when delta > 0.70 | **-2.1** / -2.7 / -2.4 pts | 2.1 / 2.3 / 1.7 pts | |

Only 1 of 90 variants beat holding on the median stock (0.15 delta, 30-45 days, through earnings,
+0.1 pt/yr), which is what chance alone would give. The walk-forward also jumped between
variants (0.15 to 0.45 delta) with no stable winner.

## Monte Carlo: a $5k account with 2 random stocks from the 17, one year (block bootstrap, 10,000 paths)
| | 5th pct | Median | 95th pct |
|---|---|---|---|
| Covered calls, 1-year return | -34% (-$1,690) | +4.8% | +50% |
| Holding, 1-year return | -36% | +6.7% | +67% |
| Covered calls, max drawdown | -47% | -19% (-$960) | -9% |
| Holding, max drawdown | -50% | -22% | -10% |

## Proposed rules (from the grid; change the bot only if you say so)
1. **Strike:** if calls are kept, sell further out: about 0.15-0.20 delta instead of 0.275. It gave up
   the least (-1.1 to -2.0 pts/yr vs -3.4) for slightly less income.
2. **Rolling:** don't roll and don't buy back at 50%. Both did worse than holding to expiry. Let
   in-the-money calls be assigned.
3. **Assignment:** accept it, then re-buy or move on at the next scan. Expect it on ~25% of calls at
   0.275 delta, ~13% at 0.15.
4. **Earnings:** keep skipping earnings (worth ~0.5 pt/yr).
5. **Ex-dividend:** 38 of 1,161 calls (3%) were exercised early, the day before ex-div, losing the
   dividend. When a call is in the money the day before ex-div and its time value is below the
   dividend, expect to lose the shares and the dividend.
6. **Sizing:** size for a ~50% drawdown on any one stock. Covered calls barely reduce it (bottom table).
7. **Scale-up:** the pass criteria in `pass-criteria.md` stand. On this backtest A1/A2/A4/A5 fail,
   so the paper results would have to beat this history clearly before adding money.

## Which numbers are approximate
- **Daily curve and drawdowns:** on days without a quote for the open call, its value is
  Black-Scholes from that contract's last IV. Cash P&L, CAGR and call-away rates use real quotes only.
- **Early exercise** uses a Black-Scholes time-value estimate (approximate).
- **"Sold IV"** is DoltHub's IV for the expiry, not for each strike (rows on one expiry share it).
- **Spin-offs aren't credited** (T/WBD 2022, PFE/Viatris 2020, others). This lowers both arms equally,
  so the gap is fine but the absolute CAGRs for those names are understated.
- **Fractional shares:** both arms stay fully invested, like BXM. A real $5k account trades 100-share lots.
- **Fees** use the bot's config ($0 commission, $0.12/contract regulatory, SEC fee). Two fee values are UNVERIFIED there.
- Before Sep 2024 calls can only be opened on Mon/Wed/Fri.

## Reproduce
`python scripts/fetch_real_data.py` (data is already committed in `data/real/`), then
`python -m ccbot.realtest` (about 16 minutes), which writes `reports/real/`.
