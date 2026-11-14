# 061 Results: covered calls vs buy-and-hold on real option quotes

Research only. Paper only. Nothing was bought; all data is free.

## Verdict
_Revision 2026-11-14 (I2, build of 061/04). The simulator now follows the bot's own entry rule: its
monthly-expiry calendar (the April 2022 Thursday monthly is found), the chosen expiry must be quoted
that day, the cost-basis floor, EARNINGS_UNKNOWN and earnings-day blocks, the config's fees and rate,
no $0.03 premium floor, and buy-back at 50% only in the first third of a call's life. All numbers
below are from the re-run (`python3 -m ccbot.realtest --out reports/real`); the value before this
revision is in brackets. `pass-criteria.md` is unchanged._

**The verdict flipped on A2, A4 and A5, but A1 still fails, so there is still no measured edge.**
On 17 candidate stocks, Jan 2020 to Nov 2026, the bot's rule (first monthly expiry in 30-45 days,
7-day slack, delta nearest 0.275 within 0.20-0.35, never below the share cost basis, no call held
through earnings, held to expiry, sold at the bid) **beat simply holding the shares by a median
+0.3 pt a year** [-1.0] and cut the worst drawdown by a median 0.8 pt [1.7]. The BXM index trailed
SPY by 6.9 pts a year over the same dates [6.9]. Walk-forward: median 0.0 pt a year vs holding [-1.1].

Why it moved: **the bot sold 250 calls, not 942.** The cost-basis floor (basis = the close the
shares were bought at, reset only by a re-buy after assignment) blocks a sale whenever the first
strike at or above the basis has delta below 0.20, i.e. while the stock trades well below its basis, and after the 2020 drop most stocks spent long stretches below their Jan-2020 basis:
BASIS_ABOVE_BAND was the reason on 7,333 entry days and NO_EXPIRY (the bot's monthly not quoted on
DoltHub that day) on 6,809, against 250 sales. T sold 1 call in almost 7 years, VZ 3, AAL 4. So the
passes on A2-A5 mostly show that the rule rarely sold calls, not that selling calls paid.

Against the pass criteria written before any result (`pass-criteria.md`): **A1 fail** (mean option
P&L -0.08% of the share price per call, needed > 0) [fail], **A2 pass** (13 of 17, needed 9) [fail,
8], **A3 pass** (17 of 17) [pass], **A4 pass** (0.099 vs 0.094) [fail, 0.062], **A5 pass** (0.0 vs
-1.0 allowed) [fail, -1.1]. Because A1 fails pooled, `pass-criteria.md` says the strategy is "an
income wrapper with no measured edge, and the scale-up gate below can't be passed". The "more than
$5k" gate stays closed. The person decides whether the flip changes anything; no bot change is made.
Fills now matter little: median gap +0.3 at the bid, +0.3 at bid + 25% of the spread, +0.4 at mid
[-1.0 / -0.5 / -0.1], because so few calls were sold.

_Earlier revision 2026-11-14 after the A1 audit: the first version used its own picker (expiry
nearest 37.5 days, delta within 0.12), which gave -1.8 pts/yr._

## Data
| What | Source | Notes |
|---|---|---|
| Call bid/ask, IV, delta, 5-80 days to expiry | DoltHub `post-no-preference/options` `option_chain` (https://www.dolthub.com/repositories/post-no-preference/options) | Mon/Wed/Fri snapshots Jan 2020 to mid-2024, daily from Sep 2024; gap 2024-07-29 to 08-12 |
| ATM IV and historical vol | same, `volatility_history` | |
| Daily prices (unadjusted), dividends, splits | DoltHub `post-no-preference/stocks` (https://www.dolthub.com/repositories/post-no-preference/stocks) | |
| Earnings dates | DoltHub `post-no-preference/earnings` (https://www.dolthub.com/repositories/post-no-preference/earnings) | |
| BXM | Cboe `BXM_History.csv` (https://cdn.cboe.com/api/global/us_indices/daily_prices/BXM_History.csv) | |

Dropped: **KGC** (no options on DoltHub: the file has no rows; `skipped` says "no option quotes"),
**VALE, PBR, ITUB** (options only Jan-Dec 2020).
Data hole: on 170 of HBAN's 1,270 snapshot days DoltHub lists only 1-3 HBAN expiries (1-2 on 169 of
them), none 7-31 days out, so the 14-24 day grid window finds no expiry there (113 NO_EXPIRY entry days at 0.15 delta; KEY 34,
T 1, the other 14 stocks 0). That is why HBAN had 67 calls in that grid row [old run]
against 101-152 for the others. It is a gap in the free data, not a rule effect.
141 quote rows (0-18 per stock) with no usable IV or delta are dropped and counted in `warnings`.
Paid sources (ORATS, OptionsDX, Cboe DataShop) would add per-strike IV and every trading day; not bought.

## Bot rule, bid fills, per stock (2020-01-06 to 2026-11-12)
CAGR includes dividends reinvested in both. "Called" = share of calls that ended in assignment.
"IV>RV" = share of calls whose sold IV beat the volatility that actually happened over the call's life.
Gap and Calls show [the value before this revision] in brackets. "Lot $" = 100 x the last close;
"Fits $3k" = one lot fits the default $3,000 account (100 x price <= cash - $200 buffer and
<= 50% of cash, as the screen requires).

| Stock | CC CAGR | Hold CAGR | Gap [old] | CC max DD | Hold max DD | Calls [old] | Called | Sold IV | Realized | IV>RV | Lot $ | Fits $3k |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AAL | -8.8% | -9.9% | **+1.1** [+1.1] | -69% | -70% | 4 [62] | 0% | 52% | 71% | 50% | 1,331 | yes |
| BAC | 7.6% | 7.8% | -0.2 [-3.7] | -48% | -48% | 24 [55] | 21% | 26% | 27% | 58% | 5,051 | no |
| BMY | 3.8% | 3.4% | **+0.4** [-0.2] | -47% | -48% | 13 [51] | 23% | 21% | 20% | 85% | 6,232 | no |
| CMCSA | -4.7% | -5.4% | **+0.8** [+0.7] | -60% | -60% | 12 [53] | 17% | 22% | 28% | 33% | 2,480 | no |
| CSX | 14.0% | 13.4% | **+0.6** [-4.2] | -39% | -41% | 37 [60] | 16% | 27% | 34% | 78% | 5,240 | no |
| F | 9.0% | 8.7% | **+0.3** [-2.1] | -56% | -57% | 11 [52] | 27% | 44% | 41% | 64% | 1,190 | yes |
| HBAN | 5.2% | 5.8% | -0.6 [-1.3] | -53% | -53% | 15 [53] | 20% | 38% | 28% | 80% | 1,573 | no |
| KEY | 7.1% | 6.1% | **+1.0** [-6.1] | -64% | -65% | 13 [61] | 8% | 29% | 27% | 62% | 2,133 | no |
| KMI | 10.1% | 12.0% | -1.9 [-1.3] | -55% | -55% | 16 [61] | 31% | 27% | 29% | 44% | 3,201 | no |
| MDLZ | 7.2% | 5.7% | **+1.5** [-0.2] | -29% | -30% | 34 [51] | 15% | 22% | 18% | 62% | 6,656 | no |
| MO | 15.2% | 14.9% | **+0.3** [-4.2] | -38% | -39% | 23 [52] | 17% | 27% | 21% | 57% | 7,792 | no |
| OXY | 4.3% | 5.9% | -1.6 [-1.0] | -80% | -80% | 8 [54] | 25% | 51% | 45% | 75% | 5,840 | no |
| PFE | -0.4% | 0.7% | -1.2 [+0.3] | -58% | -59% | 12 [51] | 17% | 27% | 28% | 67% | 2,883 | no |
| PYPL | -9.9% | -8.7% | -1.2 [-0.8] | -87% | -87% | 13 [53] | 38% | 34% | 37% | 54% | 5,830 | no |
| T | -2.3% | -2.3% | **+0.1** [+1.0] | -56% | -56% | 1 [60] | 0% | 16% | 83% | 0% | 2,218 | no |
| USB | 6.2% | 5.0% | **+1.3** [-3.0] | -52% | -52% | 11 [55] | 9% | 23% | 23% | 55% | 6,047 | no |
| VZ | 2.3% | 2.0% | **+0.3** [-0.1] | -40% | -41% | 3 [58] | 0% | 15% | 11% | 100% | 4,655 | no |
| *SPY (check)* | 15.9% | 14.8% | **+1.1** [-1.4] | -32% | -34% | 51 [74] | 37% | 13% | 15% | 53% | 75,712 | no |

Pattern: covered calls came out ahead on 11 of 17 stocks [4], mostly by small amounts, because the
cost-basis floor kept the rule out of the market while a stock was below its basis. Rows with 1-4
calls (AAL, T, VZ) are close to plain holding and their Called/IV columns rest on too few calls to
mean anything. **Only AAL and F fit a $3,000 account** at their last close (HBAN's lot, $1,573, is just
over the $1,500 single-name cap); the other results don't say what this account could hold.

## Pooled tests (bot rule, bid), re-scored 2026-11-14
| # | Result now [before this revision] | Pass now | Pass before |
|---|---|---|---|
| A1 | 250 calls [942]: sold IV > realized vol on 63% [59%], but mean option P&L **-0.08%** [-0.30%] of the share price per call after fills and fees | **Fail** (P&L < 0) | Fail |
| A2 | 13 of 17 stocks within 1 pt/yr of holding [8], needed 9 | Pass | Fail |
| A3 | Drawdown no worse than holding on 17 of 17 [17 of 17] | Pass | Pass |
| A4 | Median return / max drawdown: 0.099 covered calls [0.062] vs 0.094 holding [0.094] | Pass | Fail |
| A5 | Walk-forward Jan 2022-Nov 2026: median gap 0.0 pt/yr [-1.1] (limit -1.0); beat holding on 8 of 17 [8] | Pass | Fail |
| A6 | BXM 7.9%/yr, max DD -30%; SPY total return 14.8%/yr, max DD -34% [same] | (context) | (context) |

A5 note: 5 of the 17 walk-forward gaps are zero to rounding (|gap| < 1e-9: AAL, CMCSA, PYPL, T, VZ):
their covered-call and holding returns were equal in every test block, so no call was open there and
they just held. The median (0.0) is one of these.

At-the-money IV ran above the next 30 days' realized vol on 54-75% of days (median 64%), but the
average gap was about zero (-0.1 vol pt): the days realized vol jumped (2020, 2022) cancelled the rest.

## What the 60-variant grid says (in-sample, bid fills, median across 17 stocks), re-run 2026-11-14
Every variant now has the cost-basis floor. [Before this revision] in brackets.

| Choice | Gap vs holding per year | Drawdown saved | Called away |
|---|---|---|---|
| Delta 0.15 / 0.20 / 0.275 / 0.35 / 0.45 | +0.3 / +0.4 / +0.3 / +0.3 / +0.2 pts [-1.1 / -2.0 / -2.6 / -4.1 / -4.6] | 0.4 / 0.6 / 0.8 / 0.9 / 0.9 pts [0.8 / 1.4 / 1.8 / 2.5 / 3.9] | 8% / 12% / 18% / 25% / 37% [12% / 17% / 24% / 31% / 40%] |
| 14-24 / 30-45 days | +0.2 / +0.3 pts [-2.9 / -1.9] | 0.6 / 0.8 pts [2.0 / 2.1] | 17% / 14% [25% / 21%] |
| Hold through earnings / skip earnings | +0.2 / +0.3 pts [-2.8 / -2.0] | 0.8 / 0.6 pts [2.4 / 1.7] | 17% / 15% [23% / 22%] |
| Hold to expiry / buy back at 50% / roll when delta > 0.70 | +0.4 / +0.3 / +0.2 pts [-1.9 / -2.4 / -3.0] | 0.8 / 0.7 / 0.7 pts [2.4 / 2.4 / 1.6] | 17% / 17% / 13% [28% / 23% / 19%] |

57 of the 60 variants beat holding on the median stock [0 of 60]; the best (0.15 delta, 30-45 days,
hold through earnings, hold) was +0.7 pt/yr [-0.2, 0.15 delta skip earnings], the worst -0.4 [-8.3].
The spread between choices is now under 0.5 pt, so the grid no longer separates them. Grid-only
variants (not bot rules): the 14-24 day window, the +/-0.075 tolerance around targets other than
0.275, and rolling at delta > 0.70. A 5-9 day (weekly) window can't be tested: DoltHub keeps about 3
expiries per day (e.g. 16, 30 and 65 days), so it has a 5-9 day expiry on 1 of 1,272 BAC snapshot days.
The walk-forward still jumped between 0.15 and 0.45 delta with no stable winner (picks: 0.45 roll 4,
0.35 hold 3, 0.15 roll 2, 0.20 take50 1).

## Monte Carlo: a $5k account with 2 random stocks from the 17, one year (block bootstrap, 10,000 paths, all used)
| | 5th pct [old] | Median [old] | 95th pct [old] |
|---|---|---|---|
| Covered calls, 1-year return | -36% (-$1,776) [-34%, -$1,715] | +6.9% [+5.6%] | +64% [+53%] |
| Holding, 1-year return | -36% [-36%] | +6.7% [+6.7%] | +67% [+67%] |
| Covered calls, max drawdown | -49% [-47%] | -21% (-$1,073) [-19%, -$967] | -10% [-9%] |
| Holding, max drawdown | -50% [-50%] | -22% [-22%] | -10% [-10%] |

## Proposed rules (from the grid; change the bot only if you say so)
_Re-run 2026-11-14: with the bot's cost-basis floor in every variant the grid spread is under 0.5 pt,
so rules 1, 2, 4 and 4b below no longer have support from this data. They are kept with their new
numbers for the person to decide; I3 should check them._
1. **Strike:** the earlier case for 0.15-0.20 delta (-1.1 to -2.0 vs -2.6 pts/yr) is gone: 0.15 / 0.20 /
   0.275 now give +0.3 / +0.4 / +0.3 pts/yr.
2. **Rolling:** hold to expiry +0.4, buy back at 50% +0.3, roll +0.2 pts/yr: a weak lean to letting
   in-the-money calls be assigned.
3. **Assignment:** accept it, then re-buy or move on at the next scan. Expect it on ~18% of calls at
   0.275 delta, ~8% at 0.15 (grid medians; 44 + 3 of the bot rule's 250 calls).
4. **Earnings:** skipping earnings is now worth ~0.1 pt/yr (+0.3 vs +0.2); keep it because the bot does.
4b. **Fills:** bid vs mid is now worth ~0.1 pt/yr (+0.3 vs +0.4), because few calls were sold.
5. **Ex-dividend:** 3 of 250 calls (1.2%) [20 of 942] were exercised early, the day before ex-div,
   losing the dividend. When a call is in the money the day before ex-div and its time value is below
   the dividend, expect to lose the shares and the dividend.
6. **Sizing:** size for a ~50% drawdown on any one stock. Covered calls barely reduce it (table above).
7. **Scale-up:** the pass criteria in `pass-criteria.md` stand. On this backtest A1 fails and A2-A5 pass,
   and A1 failing pooled closes the scale-up gate by the criteria's own wording. The paper results would
   have to show a positive option P&L before adding money.
8. **Cost-basis floor (new, for the person):** it is the main driver of the re-run. It kept the rule out
   of the market for long stretches (T: 1 call in ~7 years). Whether that is wanted is a rule question
   for the person, not something this item changes.

## Which numbers are approximate
- **Daily curve and drawdowns:** on days without a quote for the open call, its value is
  Black-Scholes from that contract's last IV. Cash P&L, CAGR and call-away rates use real quotes only.
- **Early exercise** uses a Black-Scholes time-value estimate (approximate).
- **"Sold IV"** is DoltHub's IV for the expiry, not for each strike (rows on one expiry share it).
- **Spin-offs aren't credited** (T/WBD 2022, PFE/Viatris 2020, others). This lowers both arms equally,
  so the gap is fine but the absolute CAGRs for those names are understated.
- **Fractional shares, no 100-share lots:** both arms stay fully invested, like BXM. A real account
  trades 100-share lots; at $3,000 only AAL and F fit (`fits_3k` in `summary.json`), so the per-stock
  results are per-share edge, not what this account could hold. Lots would add cash drag.
- **Fees** come from `costs.fees` with the bot's config ($0 commission, $0.10/contract regulatory,
  SEC fee 0.00206% and CAT 0.0003% of notional; rate r = 4%). Two fee values are UNVERIFIED there; the
  config's assignment fee ($0) is not charged.
- **Earnings dates are treated as known in advance** (APPROXIMATE): DoltHub has no record of when each
  date was published. 5 stocks (CMCSA, MDLZ, MO, T, VZ) have one gap of more than 120 days between
  dates (counted in `warnings`). BAC, CSX and USB have no date before April 2020, so their January 2020
  quarterly report is missing from the file (its date UNVERIFIED here); each sold a 2020-01-06 call
  expiring 2020-02-21 that may have been held through it. The 120-day check doesn't see a gap before
  the first date.
- **Re-entry after assignment happens the same day** at the close + 1 cent; the bot waits for the next
  close (ASSIGNED_TODAY).
- **Cost basis** = the close the arm last bought shares at (the first close, then each re-buy after
  assignment), split-adjusted; reinvested premium and dividends don't change it.
- **Grid-only rules** (not the bot's): the 14-24 day window, the +/-0.075 tolerance around targets
  other than 0.275, and rolling at delta > 0.70.
- Before Sep 2024 calls can only be opened on Mon/Wed/Fri.
- Sales under $0.03 are allowed, like the bot (8 of 250 calls); they are counted in `sub_3c_sales`.

## Reproduce
`python scripts/fetch_real_data.py` (data is already committed in `data/real/`), then
`python -m ccbot.realtest` (about 12 minutes), which writes `reports/real/`.
