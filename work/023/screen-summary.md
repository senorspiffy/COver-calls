# Covered-call candidate screen, $3,000 account

Screened 2026-10-31 (Saturday) for the 001 starter strategy. Research, not personal financial advice. No trades placed.

## Bottom line
- **Ford (F) is the clearest fit today.** It passes every test we could check: price, liquid options, earnings already out of the way, and a calm-ish volatility for a single stock.
- **Vale (VALE) is a close second**, with one caveat: its quote is from Oct 26 and the strike next to the one you'd sell had very low open interest.
- **American Airlines (AAL) is a maybe**: it fits on price and dates, but I couldn't see its option quotes near the strike you'd sell.
- Everything else either has earnings before the December expiry (Nu, Itaú), options that are too thin (JETS, Itaú), or quotes too stale or broken to judge (KWEB, Nokia).
- **Before you trade**, open the **Dec 18, 2026** calls in Webull and confirm the 0.25–0.30 delta strike has a bid-ask gap of $0.05 or less and open interest of 500 or more. I could not read the December chain for any ticker except Itaú (see "Data limits").

## The rules this screen used (from 001)
| Test | Limit at $3,000 |
|---|---|
| Price, single stock | 100 shares ≤ 50% of capital → **≤ $15/share** |
| Price, ETF | 100 shares ≤ $3,000 − $200 buffer → **≤ $28/share** |
| Expiry | Monthly, 30–45 days out (else up to 23–52) → **Dec 18, 2026** (49 days from Oct 30) |
| Strike | Delta nearest 0.275 (allowed 0.20–0.35) |
| Liquidity | Bid-ask ≤ $0.05 and open interest ≥ 500 at that strike |
| Earnings | None before the expiry |
| Stability | Prefer lower volatility (house rule) |

## Shortlist

### 1. Ford (F): fits
**Why it's good**
- Price $12.33 → 100 shares = $1,233 (41% of $3,000). [Cboe F quote, 2026-10-30]
- Liquid options: the Nov 6 $12.50 call was $0.12 / $0.15 (3¢ wide) with 4,873 open; the $13 call $0.03 / $0.05 with 5,824 open. [Cboe F chain, 2026-10-30]
- Earnings just happened (Q3 reported Oct 28), so the next report should fall after Dec 18. The next date isn't published yet. [Business Wire, Ford Q3 release]
- Dividend: $0.15/share, record date **Nov 10**, paid Dec 1. Buying before then gets you $15 per 100 shares. Under T+1 settlement the ex-date is normally the record date (my reasoning; the release gives no ex-date). [Business Wire]
- 30-day implied volatility 35.5%, one of the lowest of the stocks that fit. [Cboe F quote]
- **Estimated premium** (model, not a quote): Dec 18 $13.50 call ≈ **$0.24** at 0.26 delta → about $24 per contract, ≈ 1.9% of $1,233 for 49 days. Worked from Cboe's 30-day IV with the repo's Black-Scholes pricer.

**Risks**
- Beta 1.94: it moves almost twice as much as the market. [stockanalysis.com/stocks/f]
- 52-week range $11.11–$17.78, and it's near the low end now. A cyclical automaker exposed to car demand and tariffs.
- If your call is in the money right before the Nov 10 dividend, early assignment is possible (001 F3). At a $13.50 strike that's unlikely unless Ford jumps 10% first.

### 2. Vale (VALE): fits, check liquidity
**Why it's good**
- Price $12.00 → $1,200. **Quote is from Oct 26**, so re-check. [Cboe VALE quote]
- Beta 0.70, the calmest of the stocks that fit except Itaú. IV 36.8%. [stockanalysis.com/stocks/vale; Cboe]
- Earnings done Oct 29; next not published. [stockanalysis.com/stocks/vale]
- Options: Nov 6 $12.50 call $0.10 / $0.14 (4¢), 1,330 open, 0.25 delta. [Cboe VALE chain, 2026-10-27]
- **Estimated premium** (model): Dec 18 $13 call ≈ **$0.28** at 0.29 delta → ≈ 2.3% for 49 days.
- Pays a semi-annual dividend (last: $0.32 ex Aug 13). [stockanalysis.com/stocks/vale/dividend]

**Risks**
- The $12 call had only 28 open contracts, so liquidity is uneven strike to strike.
- Brazilian iron-ore miner (ADR): depends on commodity prices and the Brazilian real.
- Next ex-dividend date not found. Check it before selling a call that's near the money.

### 3. American Airlines (AAL): maybe
- Price $12.32 → $1,232. IV 46.6%, beta 1.38. Earnings done Oct 22. No dividend, so no early-assignment worry. [Cboe; stockanalysis.com/stocks/aal]
- **Estimated premium** (model): Dec 18 $14 call ≈ **$0.31** (0.26 delta), more than Ford because it's more volatile.
- **Couldn't confirm liquidity**: no near-the-money call quote was readable. Airlines swing with fuel prices and the economy (52-week $10.09–$18.79).

## Didn't make it (this month)
| Ticker | Price | Why not |
|---|---|---|
| Nu (NU) | $11.83 | Earnings **Nov 12**, before Dec 18. Revisit after for a January call. |
| Itaú (ITUB) | $7.13 | Earnings **Nov 3**; Dec 18 $8 call is $0.15 / $0.25 (10¢ wide, fails ≤ $0.05). |
| Nokia (NOK) | $8.54 | IV 54%; Nov 6 quotes showed $0 bids (unreadable); 52-week range $5.86–$17.45. |
| JETS (airline ETF) | $27.09 | Open interest 20–225 (needs 500); spreads up to 23¢. |
| KWEB (China internet ETF) | $23.19 | Quote from Oct 26; no usable strikes visible; one-country fund. |
| SoFi, Huntington | $16.74, $15.76 | Just over the $15 single-stock limit. Fit once you have about $3,400+. |
| BBD, SNAP, RIVN, CLF, LUMN, GRAB, UNG, MSOS | under limit | IV 51–86%: too jumpy for "steady income" (house rule). BITO is a bitcoin-only fund. |
| T, PBR, KGC, KEY, PFE, KMI, WBD, AMCR | $20–47 | Over $15 (single stock). |
| FXI, EWZ, SCHB, SCHD, XLF, SLV, ASHR, MCHI, EEM, VEA, IEFA, SPYM | $29–96 | Over $28 (ETF). |

So this week **17 of 39** priced tickers (40 tried; SPLG's quote failed) fit the price limits, **8** were checked further, and **1 (Ford)** passes every test we could see.

## Your decision: two companies (2026-10-31)
You chose to hold two companies. **Ford ($1,233) + Vale ($1,200) = $2,433**, leaving $567 in cash (the rule needs $200 or more). Each is under the 50% single-stock cap. Check both Dec 18 chains in Webull first (see the bottom line). If Vale's strike fails the liquidity check, American Airlines ($1,232) is the backup, and its chain needs the same check.

## Data limits
- Prices and IV are Cboe's delayed quotes. Most are from Oct 29–30, but VALE (Oct 26), KWEB (Oct 26), BBD, SNAP, T, KEY, LUMN, WBD and several ETFs were older; dates are in `work/023/01-research.md`.
- The Cboe chain file is cut off by the fetch tool partway through, so the **Dec 18 strikes weren't readable** except for ITUB. Liquidity above comes from the Nov 6 weekly, which is a proxy. Premiums marked "model" are Black-Scholes estimates, not quotes.
- Yahoo, Nasdaq, Barchart and OptionCharts were blocked or paywalled.

## Sources
- Cboe delayed quotes: `https://cdn-api.cboe.com/api/global/delayed_quotes/quotes/<TICKER>.json` and `.../options/<TICKER>.json`
- Ford Q3 2026 release: https://www.businesswire.com/news/home/20261028111591/en/Ford-Reports-Third-Quarter-2026-Financial-Results/
- StockAnalysis overview and dividend pages: `https://stockanalysis.com/stocks/<ticker>/` and `/dividend/`
