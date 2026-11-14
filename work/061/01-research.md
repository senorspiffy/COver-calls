# 061 Results: covered calls vs buy-and-hold on real option quotes

Research only. Paper only. Nothing was bought; all data is free.

## Verdict
**No edge found.** On 17 candidate stocks, Jan 2020 to Nov 2026, the bot's own rule (its own expiry
and strike pickers: first monthly expiry in 30-45 days, delta nearest 0.275 within 0.20-0.35, no call
held through earnings, held to expiry, sold at the bid) **trailed simply holding the shares by a
median 1.0 pt a year** and cut the worst drawdown by a median 1.7 pts. The BXM index trailed SPY
by 6.9 pts a year over the same dates. Walk-forward (picking the rule every 6 months from the prior
2 years) did about the same: median 1.1 pts a year behind holding.
Against the pass criteria written before any result (`pass-criteria.md`): **A1 fail, A2 fail (8 of 17,
needed 9), A3 pass, A4 fail, A5 fail (-1.1 vs -1.0 allowed).** So the "more than $5k" gate can't be passed
on this evidence. Fills decide a lot of it: at mid prices the gap is about zero.

_Revised 2026-11-14 after the A1 audit: the first version used its own picker (expiry nearest 37.5
days, delta within 0.12), which gave -1.8 pts/yr. The verdict is the same._

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
| AAL | -8.8% | -9.9% | **+1.1** | -67% | -70% | 62 | 23% | 53% | 50% | 66% |
| BAC | 4.1% | 7.8% | -3.7 | -48% | -48% | 55 | 35% | 27% | 28% | 53% |
| BMY | 3.1% | 3.4% | -0.2 | -41% | -48% | 51 | 29% | 24% | 23% | 67% |
| CMCSA | -4.7% | -5.4% | **+0.7** | -54% | -60% | 53 | 25% | 27% | 26% | 66% |
| CSX | 9.2% | 13.4% | -4.2 | -40% | -41% | 60 | 30% | 27% | 31% | 73% |
| F | 6.6% | 8.7% | -2.1 | -56% | -57% | 52 | 31% | 40% | 38% | 63% |
| HBAN | 4.5% | 5.8% | -1.3 | -51% | -53% | 53 | 26% | 34% | 35% | 60% |
| KEY | -0.0% | 6.1% | -6.1 | -62% | -65% | 61 | 33% | 34% | 36% | 56% |
| KMI | 10.7% | 12.0% | -1.3 | -55% | -55% | 61 | 26% | 26% | 27% | 52% |
| MDLZ | 5.6% | 5.7% | -0.2 | -28% | -30% | 51 | 24% | 21% | 20% | 55% |
| MO | 10.7% | 14.9% | -4.2 | -38% | -39% | 52 | 33% | 22% | 21% | 63% |
| OXY | 4.9% | 5.9% | -1.0 | -79% | -80% | 54 | 31% | 43% | 47% | 56% |
| PFE | 1.1% | 0.7% | **+0.3** | -52% | -59% | 51 | 22% | 25% | 25% | 63% |
| PYPL | -9.5% | -8.7% | -0.8 | -80% | -87% | 53 | 30% | 37% | 37% | 64% |
| T | -1.3% | -2.3% | **+1.0** | -53% | -56% | 60 | 23% | 23% | 23% | 53% |
| USB | 1.9% | 5.0% | -3.0 | -50% | -52% | 55 | 33% | 27% | 30% | 40% |
| VZ | 1.9% | 2.0% | -0.1 | -40% | -41% | 58 | 28% | 19% | 19% | 57% |
| *SPY (check)* | 13.4% | 14.8% | -1.4 | -32% | -34% | 74 | 42% | 16% | 16% | 55% |

Pattern: covered calls only came out ahead on stocks that fell or went nowhere (AAL, CMCSA, PFE, T).
On every stock that rose a lot (CSX, MO, KEY, BAC), giving up the upside cost more than the premium
brought in. **Fills matter:** the median gap is -1.0 pt at the bid, -0.5 at bid + 25% of the spread,
and -0.1 at mid.

## Pooled tests (bot rule, bid)
| # | Result | Pass? |
|---|---|---|
| A1 | 942 calls: sold IV > realized vol on 59%, but mean option P&L **-0.30% of the share price per call** after fills and fees | **Fail** (P&L < 0) |
| A2 | 8 of 17 stocks within 1 pt/yr of holding (needed 9) | **Fail** |
| A3 | Drawdown no worse than holding on 17 of 17 | Pass |
| A4 | Median return / max drawdown: 0.062 covered calls vs 0.094 holding | **Fail** |
| A5 | Walk-forward Jan 2022-Nov 2026: median gap -1.1 pts/yr (limit -1.0); beat holding on 8 of 17 | **Fail** (narrowly) |
| A6 | BXM 7.9%/yr, max DD -30%; SPY total return 14.8%/yr, max DD -34% | (context) |

At-the-money IV ran above the next 30 days' realized vol on 54-75% of days (median 64%), but the
average gap was about zero (-0.1 vol pt): the days realized vol jumped (2020, 2022) cancelled the rest.

## What the 60-variant grid says (in-sample, bid fills, median across 17 stocks)
| Choice | Gap vs holding per year | Drawdown saved | Called away |
|---|---|---|---|
| Delta 0.15 / 0.20 / 0.275 / 0.35 / 0.45 | -1.1 / -2.0 / -2.6 / -4.1 / -4.6 pts | 0.8 / 1.4 / 1.8 / 2.5 / 4.0 pts | 12% / 17% / 25% / 31% / 40% |
| 14-24 / 30-45 days | -2.9 / -1.9 pts | 2.0 / 2.1 pts | 25% / 21% |
| Hold through earnings / skip earnings | -2.8 / -2.0 pts | 2.4 / 1.7 pts | |
| Hold to expiry / buy back at 50% / roll when delta > 0.70 | **-1.9** / -2.4 / -3.0 pts | 2.4 / 2.4 / 1.6 pts | |

None of the 60 variants beat holding on the median stock; the best (0.15 delta, 30-45 days, skip
earnings, hold) was -0.2 pt/yr. A 5-9 day (weekly) window can't be tested: DoltHub keeps about 3
expiries per day (e.g. 16, 30 and 65 days), so it has a 5-9 day expiry on 1 of 1,272 BAC snapshot days.
The walk-forward jumped between 0.15 and 0.45 delta with no stable winner.

## Monte Carlo: a $5k account with 2 random stocks from the 17, one year (block bootstrap, 10,000 paths)
| | 5th pct | Median | 95th pct |
|---|---|---|---|
| Covered calls, 1-year return | -34% (-$1,715) | +5.6% | +53% |
| Holding, 1-year return | -36% | +6.7% | +67% |
| Covered calls, max drawdown | -47% | -19% (-$967) | -9% |
| Holding, max drawdown | -50% | -22% | -10% |

## Proposed rules (from the grid; change the bot only if you say so)
1. **Strike:** if calls are kept, sell further out: about 0.15-0.20 delta instead of 0.275. It gave up
   the least (-1.1 to -2.0 pts/yr vs -2.6 in the grid) for less income.
2. **Rolling:** don't roll and don't buy back at 50%. Both did worse than holding to expiry. Let
   in-the-money calls be assigned.
3. **Assignment:** accept it, then re-buy or move on at the next scan. Expect it on ~25-30% of calls at
   0.275 delta, ~12% at 0.15.
4. **Earnings:** keep skipping earnings (worth ~0.8 pt/yr).
4b. **Fills:** never sell at the bid if it can be helped: work a limit at mid first. Bid vs mid is worth ~1 pt/yr here.
5. **Ex-dividend:** 20 of 942 calls (2%) were exercised early, the day before ex-div, losing the
   dividend. When a call is in the money the day before ex-div and its time value is below the
   dividend, expect to lose the shares and the dividend.
6. **Sizing:** size for a ~50% drawdown on any one stock. Covered calls barely reduce it (bottom table).
7. **Scale-up:** the pass criteria in `pass-criteria.md` stand. On this backtest A1/A2/A4/A5 fail (A2 and A5 narrowly),
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
- The bot's cost-basis floor (never sell a call below the share basis) isn't modelled.

## Reproduce
`python scripts/fetch_real_data.py` (data is already committed in `data/real/`), then
`python -m ccbot.realtest` (about 12 minutes), which writes `reports/real/`.
