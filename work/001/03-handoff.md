# 03 Research hand-off - 001
Status: READY (research-team-only item; the implementation map below is a rule-based starter strategy for the person, not a hand-off to Implementation)

Prepared by R3 on 2026-10-30. Research, not personal financial advice. No trades placed. Every price/premium in the worked example is **HYPOTHETICAL** (made up to show the arithmetic). Broker: **Webull (US)** per coordinator correction; all fee math below is redone for Webull.

## Fact check
R1 = 01-research.md, R2 = 02-improvements.md. "V" = VERIFIED (source opened today and the quote/number matches).

| Claim | Source | Result | Fix |
|---|---|---|---|
| R1 A1 max profit = strike − cost + premium | Fidelity CC deck (slide 8) | VERIFIED | – |
| R1 A2 risk = cost − premium; breakeven = cost − premium | Fidelity deck (slide 11) | VERIFIED | – |
| R1 A3 "continues to bear the downside risk…"; "some… though certainly not all" | Fidelity why-use page | VERIFIED | – |
| R1 A4 "stay steady or go up slightly"; not for "extremely optimistic" | Fidelity why-use | VERIFIED | – |
| R1 A5 ITM call "can be assigned at any time before the expiration" | Fidelity why-use | VERIFIED | – |
| R1 A6 AQR: CCs earn VRP + ERP; active equity exposure "uncompensated" | aqr.com Covered Calls Uncovered | VERIFIED | – |
| R1 A7 covered call ≈ short put (was UNVERIFIED) | economipedia.com/definiciones/call-cubierta.html: "estamos imitando el comportamiento de vender una opción put" ("we are imitating the behaviour of selling a put") | VERIFIED (now sourced) | Source added |
| R1 B1 BXM methodology (1-month, held to 3rd Friday, nearest strike above level before 10:00 CT) | SEC 34-57946 | VERIFIED | – |
| R1 B2 BXM 9.2%/11.4% vs S&P 9.2%/15.9%, 6/1986–1/2012 | HEK 2012 (Cboe) | VERIFIED | – |
| R1 B3 lags in sharp rallies; 2008 −29% vs −37% | HEK 2012 | VERIFIED | – |
| R1 B4 1988–2006 11.77%/9.29%/0.77 vs 11.67%/13.89%/0.51; drawdown −47.4% vs −32.5% | Callan (Cboe) | VERIFIED | – |
| R1 B5 BXM vs S&P calendar years 2006–2025 | ftportfolios.com 2026-03-24 table | VERIFIED (all 20 rows re-read) | – |
| R1 B6 / N6 compounded 6.1% vs 11.0%; BXM won 5/20 (2007, 08, 11, 15, 22) | R3 recalculation from table | VERIFIED | Precise products 3.257 and 8.055 → $3k grows to ≈$9,771 vs ≈$24,164 (R1 rounded to $9,780/$24,150; trivial) |
| R1 B7 BXM ≈1.7% gross premium per month since May 2006 | Cboe insights post | VERIFIED | Also verified: "BXMD generates less premium than BXM" |
| R1 B8 BXMD = monthly call nearest 30 delta | indexologyblog 2018-09-04 | VERIFIED | – |
| R1 B9 1990–2018 BXMD 9.59%/12.31%/β0.82; BXM 8.14%/10.11%/β0.62 | NB white paper | VERIFIED | – |
| R1 B10 BXMD "roughly doubled the performance of BXM" since Sept 2002 | Nasdaq Dorsey Wright 2025-05-27 | VERIFIED | – |
| R1 B11 "writing weekly or laddered (BXMW)… detracted over 180bps in 2018" | NB white paper | **WRONG** | NB says BXMW = "ladder monthly option writing across four Friday expirations", not weekly options. It is **not** evidence about weekly cadence. R2 table row F ("NB weekly lagged") also WRONG. Removed as cadence evidence. |
| R1 B12 index results exclude costs; single stock differs | Reasoning / methodology docs | VERIFIED (as a caveat) | – |
| R1 C1 steepest theta 5–7 DTE; "very little (or no) time left…" | tastylive time-decay article | VERIFIED | – |
| R1 C2 1–2 wk vs 1–2 mo trade-offs | Fidelity deck slide 14 | VERIFIED | – |
| R1 C3 4 weekly ATM SPY calls $21.92 vs one 30-day $11.37 (≈92% more) | Dorsey Wright | VERIFIED | Math: 4 × $5.48 = $21.92; 21.92/11.37 − 1 = 92.8% ✓ |
| R1 C4 0DTE theta "nearly 100x faster than a 45 day option" | tastylive theta-0dte | VERIFIED | – |
| R1 C5 Cboe 0DTE sensitivity; loss "can be substantial" | cboe.com/tradable-products/0dte | VERIFIED | – |
| R1 C6 "most stocks under $30 do not have daily expirations" | — | **WRONG / imprecise** | Correct fact: single-stock Mon/Wed expiries began 26 Jan 2026 for stocks with market cap > $700B, >10M monthly contracts, penny program (GOOGL, AMZN, AAPL, META, MSFT, NVDA, TSLA, AVGO; ETFs need AUM > $50B, e.g. XLF). [ibkrcampus.com "Sub-weekly equity options arrive Monday"]. No sub-$30 stock meets that, so 0DTE is not available for this account's universe. |
| R1 C7 tastytrade 45-DTE open / 21-DTE manage data | tastylive episode pages (5 tried today: what-happens-after-21-dte, enter-at-45-exit-at-21, short-put-management, managing-winners-earlier, managing-winners-varying-targets) | **UNSUPPORTED** (pages return show landing pages only) | 21-DTE kept only as an untested *option*, no numbers attributed to it. |
| R1 D1 tastylive "close our winners when we reach 50% profit" + 3 reasons | tastylive managing-winners | VERIFIED | Page also says "or lower for certain strategies". |
| R1 D2 warns about commissions when managing too early | same | VERIFIED | Exact: "We always want to ensure we're covering commissions and not managing too early." |
| R1 D3 no backtest on that page; no covered-call test of 50% | same + search today | VERIFIED (absence confirmed) | Searched again: ctranch.substack "Can covered call rules be tested" uses 50% in *both* arms, so it is not a test of 50% vs hold. Still no direct test. |
| R1 D4 shares uncapped after buy-back | Reasoning (mechanically true) | VERIFIED as logic | – |
| R1 E1 ITM/ATM/OTM trade-offs | Fidelity deck slide 13 | VERIFIED | – |
| R1 E2 "30 delta to be the sweet spot" | Dorsey Wright | VERIFIED | – |
| R1 E3 BXMD > BXM 1990–2018 | NB | VERIFIED | – |
| R1 F1 liquidity: narrow spreads; 50-cent spread illiquid; OI; no thresholds | tastylive options-liquidity | VERIFIED | – |
| R1 F2 earnings moves, IV elevated, "can sometimes collapse" | Schwab earnings article | VERIFIED | – |
| R1 F3 dividend > time value → "a good chance" of early exercise; day before ex-div | Fidelity dividends page | VERIFIED | – |
| R1 F4 "ok with keeping the stock" | Fidelity why-use | VERIFIED | – |
| R1 F5 numeric screens are house rules | – | VERIFIED (correctly labelled) | Kept as house rules only |
| R1 G1–G2 wheel steps and risks | schwab.com.sg wheel article | VERIFIED | – |
| R1 G3 CSP definition | OIC acquire-stock | VERIFIED | – |
| R1 G4 Fidelity Tier 1 / Tier 2 | Fidelity FAQ | VERIFIED but **not applicable** (Webull) | Webull: Level 1 = covered calls, buy-writes, CSPs; Level 3 (margin, ≥$2,000 margin equity) = spreads; cash accounts/IRAs max Level 2. [webull.com/help/faq/10980]. Calendars/diagonals need Level 3 in margin. [webull.com/help/faq/10981] |
| R1 H1 rolling definition; "further credits… more time value" | TradeStation 2025-10-29 | VERIFIED | – |
| R1 H2 up-and-out roll ≈ $0.50 debit; risk of extending time | TradeStation (INTC Nov 40 → Dec 43: buy $4.40, sell $3.90) | VERIFIED | Math: 4.40 − 3.90 = $0.50 debit ✓ |
| R1 H3 "roll only for a net credit" as sourced rule | none found | UNSUPPORTED | Used below only as a labelled house rule |
| R1 I1–I3 PMCC definition, 75% debit rule, max loss | tastylive PMCC page | VERIFIED | – |
| R1 I4 Saxo 6–12 mo, Δ0.70–0.80 long; 2–6 wk short | home.saxo it-it: "da 6 a 12 mesi", "delta di circa 0,70–0,80", "2-6 settimane" | VERIFIED (Italian checked) | – |
| R1 I5 PMCC gets no dividends | Saxo/tastylive don't say it | UNSUPPORTED | Removed. Tier 2 → Webull Level 3 margin. |
| R1 N5 PMCC math: debit $1,300, max profit $200, 86.7% of width | tastylive example | VERIFIED | Also fails the page's own extrinsic rule ($2 short < $5 long extrinsic) |
| R1 J1 Schwab $0.65/contract | schwab.com/pricing | VERIFIED for Schwab, **WRONG for this account** | Webull: "$0" commission on US-listed stock/ETF options; $0.50/contract on certain index options; $0.10/contract on oversized orders; SEC fee $0.0000206 × sale value on sells. [webull.com/pricing; webull.com/help/faq/10793] |
| R1 J2 regulatory/clearing fees small, amounts unknown | Webull pages say only "Relevant regulatory and exchange fees may apply" | UNSUPPORTED (amounts) | A third-party page (brokerage-review.com) lists exchange $0.0388 + FINRA $0.00244 + OCC $0.045 ≈ $0.086/contract, undated, not official. We use **$0.10/contract/fill as a conservative placeholder** and check it on the first trade confirmation (map step 2). |
| R1 K1 premium taxed at close; short-term; assignment adds premium to sale price | Fidelity tax page | VERIFIED | – |
| R1 K2 QCC > 30 days, not deep ITM; holding period; straddle rules | Fidelity + Schwab tax pages | VERIFIED | – |
| R1 K3 wash-sale applies to options | Schwab tax page | VERIFIED | – |
| R1 K4 85% floor example | 26 CFR 1.1092(c)-4 (Example 2) | VERIFIED (as limited by R1) | – |
| R1 K5 short-term gains taxed at ordinary rates (was UNVERIFIED) | blog.taxact.com: held "one year or less"; "taxed at the same rate as ordinary income" | VERIFIED (now sourced) | – |
| R1 N1 share-price limits $30/$50/$60 | math | VERIFIED | – |
| R1 N2 hypothetical: 1.76% flat, 8.91% called, BE $27.50, −18.2% on −20% | math | VERIFIED math; fee **WRONG for Webull** | With $0.10 fee: $49.90 → 1.78% flat; called $249.90 → 8.93% |
| R1 N3 50% exit $23.70; fees eat 26% of a $0.10 premium's 50% gain | math | VERIFIED math; **WRONG for Webull** | Webull: $25 − $0.20 = $24.80; on $0.10 premium $5.00 − $0.20 = $4.80, fees ≈ 4% not 26% |
| R1 N4 yearly commission drag (5.46% 0DTE, 2.25% weekly, 0.52% monthly) | math | VERIFIED math; **WRONG for Webull** | At $0.10/fill on $3k: weekly open+close 104 fills = $10.40 (0.35%); monthly open+close 24 fills = $2.40 (0.08%). 252-day count dropped (0DTE not available, C6). |
| R1 N7 1.7% × 12 = 20.4% premium vs ~6.1% total return | math | VERIFIED | (Compounded 1.017^12 − 1 = 22.4%; R1's simple figure is fine as stated) |
| R2 FOR1 ORATS: 16 stocks, back to 2007, ~3.5M combos, "Holding to expiration was better than exiting after profit", tested 75% | orats.com blog | VERIFIED | – |
| R2 FOR2 ORATS best 30 DTE, 0.10 delta, avoid earnings, IV pctile > 66% | orats.com blog | VERIFIED | – |
| R2 FOR2 moomoo Chinese quotes ("略微看涨至中性…", "近期深度虚值（OTM）") | moomoo hans page | VERIFIED; translation OK | "深度虚值" is literally "deep OTM"; R2's "far OTM" is acceptable |
| R2 FOR3 Commerzbank German quote "Stabile bis leicht positive Notierungen…" | commerzbank.de | VERIFIED; translation OK | – |
| R2 FOR3 / AGAINST1 FlashAlpha: 3 Jan 2022–19 Oct 2026; 0.10–0.50Δ, 1 wk–3 mo; 48 setups all lag; $774–$16,988 per 100 sh; held to expiry | flashalpha.com | VERIFIED | – |
| R2 AGAINST2 Monex JP, KB KR, Economipedia ES quotes | original pages | VERIFIED; translations OK | – |
| R2 AGAINST2 −$510 vs ~$49/mo ≈ 10 months | math | VERIFIED (510.65/49.35 = 10.3) | – |
| R2 AGAINST3 Commerzbank "vergleichsweise geringer Gewinn…" | commerzbank.de | VERIFIED | Fee part of this point is WRONG for Webull (see N4 fix) |
| R2 table: CME Chinese quote | cmegroup.com cn-s | VERIFIED; translation OK | – |
| R2 table: JPX Japanese quotes | jpx.co.jp column 04 | VERIFIED; translation OK | Full sentence of 2nd quote starts "もっと株を高く売れたかもしれない！と、…" ("thinking 'I could have sold higher!'") – meaning unchanged |
| R2 table: Commerzbank "rund 3.000 Euro" missed gain | commerzbank.de | VERIFIED | – |
| R2 table: Portuguese InfoMoney (`?p=381537`) | Resolves to infomoney.com.br/mercados/colunista-infomoney-venda-coberta-de-opcoes-de-compra-calls/ (Paulo C. Coimbra, 18/08/2009) | VERIFIED; all 3 quotes match; translations OK | URL replaced with canonical one; note the article is from 2009 |
| R2 table: Korean KB quotes | kbthink.com | VERIFIED; translations OK | KB page has no ETF fee data |
| R2 variation J: covered-call ETF fees UNVERIFIED | 247wallst.com 2026-07-18 | VERIFIED (secondary) | XYLD 0.60%/yr, JEPI 0.35% net. Check the fund's own page before buying. |
| R2 "50% rule doubles fee events" | math | VERIFIED logic; cost now ≈ $0.10 + spread per extra fill | See spread table below |
| NEW: Webull GTC options orders expire after 60 calendar days; auto-cancel at contract expiry; no fills outside regular hours | webullapp.com courseware "GTC for Options Trading" | VERIFIED (Webull learning page; confirm in the US app) | – |
| NEW: Webull option order types: Market, Limit, Stop Limit, Take-Profit/Stop-Loss, Trailing Stop | webull.com/help/faq/298 | VERIFIED | – |

**Totals:** 77 rows checked → **61 VERIFIED as-is**, **12 fixed** (corrected or newly sourced: A7, B11, C6, G4, J1, K5, N2, N3, N4, R2 AGAINST3 fee point, R2 Portuguese URL, R2 variation J), **4 removed** (C7 21-DTE data, H3 as a sourced rule, I5 dividend claim, J2 exact fee amounts).

## Removed claims
Definitions: *fixed* = claim kept with a correction or a new source; *removed* = claim dropped with nothing in its place. Entries 3, 4, 5 and 7 below are the 4 removed rows; entries 1, 2 and 6 were replaced by a corrected fact and are counted under *fixed*.
1. **R1 B11 / R2 row F** as evidence that weekly writing lags — BXMW is laddered *monthly* options, not weekly.
2. **R1 C6** "most sub-$30 stocks lack daily expiries" — replaced by the actual Jan-2026 eligibility rule (> $700B market cap).
3. **R1 C7** any numbers for tastytrade 45/21-DTE — still unfetchable.
4. **R1 H3** "roll for a net credit" as a sourced fact — kept only as a labelled house rule.
5. **R1 I5** "PMCC collects no dividends" — no source.
6. **R1 J1/N3/N4 + R2 AGAINST3** $0.65 fee drag (5.46% / 2.25% / 26%) — wrong broker for this person.
7. **R1 J2** exact ORF/OCC/TAF amounts — Webull's official pages do not state them.

## Key corrections for a Webull account
**Commissions are near zero; the bid-ask spread is now the real cost.** Each time you sell at the bid or buy back at the ask, you lose about half the spread versus the mid price. (tastylive liquidity page: a 50-cent-wide market costs half the premium on a round trip.) HYPOTHETICAL spread drag on a $3,000 account, one contract, paying half the spread per fill:

| Spread width | Monthly, hold to expiry (12 fills) | Monthly + 50% buy-back (24) | Weekly, hold (52) | Weekly + 50% buy-back (104) |
|---|---|---|---|---|
| $0.01 | $6 (0.2%) | $12 (0.4%) | $26 (0.9%) | $52 (1.7%) |
| $0.05 | $30 (1.0%) | $60 (2.0%) | $130 (4.3%) | $260 (8.7%) |
| $0.10 | $60 (2.0%) | $120 (4.0%) | $260 (8.7%) | $520 (17.3%) |

Math: half-spread × 100 shares × fills; e.g. $0.05/2 × 100 × 104 = $260; $260 / $3,000 = 8.7%. Pass-through fees at $0.10/fill add only $1.20–$10.40 a year (0.04%–0.35%). Also: a call that expires worthless has no closing fill, so hold-to-expiry saves one spread cost each cycle.

**What this changes:**
- *Cadence:* the fee case against weekly mostly goes away, but the spread case does not: weekly needs ~4× the fills, and on wider markets it eats most of the extra premium. Monthly still wins on evidence (ORATS best = 30 DTE; BXM/BXMD are monthly), on effort, and on spread cost. Weekly is allowed later only if the logged spread is ≤ $0.02.
- *50% rule:* the fee objection (R1 N3: 26%) is now ~4%, so that argument is weak. What's left: (a) it adds a buy-at-the-ask fill, (b) the only related test (ORATS, 75% target) found holding better, (c) there is still **no direct test of 50% on covered calls**. Verdict: allowed as a narrow exception, not the default.

## Implementation map (starter strategy — rules the person follows)
Rules marked **[house rule]** are judgment calls, not sourced facts. Everything else cites the fact check above.

> **Corrected 2026-10-30** (items 003, 004, 008): steps 1, 3, 4, 5, 6, 8, 9(a), 11, Alternative 1 and the worked example's 50% line are superseded by § Correction 2026-10-30 below.

| Step | Change (rule) | Inputs | Outputs | How we check it |
|---|---|---|---|---|
| 1 | **Account size.** $3,000 is enough to *start* with **one** position, but only on a diversified, liquid ETF priced ≤ $28 (keeps ≥ $200 cash for the 100 shares + buffer). Prefer **$5,000–6,000** before using single stocks: by the check in the last column, $5,000 allows two positions ≤ $24 or one ≤ $48; $5,600 allows two ≤ $27 or one ≤ $54; two positions ≤ $28 need **$5,800** (N1 + $200 buffer). Income % is about the same either way; the gain is diversification. [house rule on ETF-only at $3k; N1, R2 AGAINST2] | Cash balance, share price | Number of positions allowed: max price = (cash − $200) / (100 × positions) | Before each buy: (price × 100 × positions) ≤ cash − $200. |
| 2 | **Broker setup (Webull).** Apply for options **Level 1** (covered calls, buy-writes, CSPs). Cash account is fine; no margin needed. Do not apply for Level 3 unless doing PMCC (needs margin + $2,000 margin equity). | Webull account | Level 1 approval | Approval shown in app. After first trade, read the confirmation and record the real per-contract regulatory/clearing fees; replace the $0.10 placeholder. Also confirm whether Webull charges anything on assignment (not stated on its pages). |
| 3 | **Underlying selection.** Must meet all: (a) you'd hold it for a year anyway (F4); (b) monthly options listed; (c) option bid-ask ≤ $0.05 at the chosen strike and OI ≥ 500 [house rule; F1/F5]; (d) no earnings date before the call's expiry (ORATS; F2); (e) prefer lower volatility / broad ETF over one company (moomoo; R2 AGAINST2). | Option chain in Webull | Approved ticker | Screenshot/log of spread, OI and next earnings date at each entry. Reject if any test fails. |
| 4 | **Cadence & expiry.** Sell the **monthly expiry 30–45 DTE** (ORATS best 30 DTE; BXM/BXMD monthly). No 0DTE (not offered on this universe, C6). No weekly until 3 months of logs show spreads ≤ $0.02. | Calendar | One open call per 100 shares | Log DTE at entry: must be 30–45. |
| 5 | **Strike/delta.** Sell the strike nearest **0.25–0.30 delta**, and at or above your cost basis. (BXMD 30Δ beat ATM BXM, B9/B10; ORATS' 0.10Δ is too little premium on a sub-$30 stock.) Sell with a **limit at the mid**, step down $0.01 at a time; never a market order. | Delta from chain, cost basis | Short call | Log delta (0.25–0.30), strike ≥ basis, fill vs mid (target ≤ $0.01 below mid). |
| 6 | **Exit rule — default HOLD TO EXPIRY.** Let it expire or be assigned (ORATS; FlashAlpha and BXM method hold to expiry). **Exception:** if the call is worth ≤ 50% of what you sold it for *within the first third of its life* (e.g. day ≤ 11 of 35, since 35 / 3 = 11.7), buy it back and **sell the next month's call the same day** (R2 hybrid; untested — reasoning only). Put this on as a **GTC limit buy-to-close at 50% of the sale price, rounded down to the nearest price the order ticket accepts (the option's minimum tick)**, so a fill is always ≤ 50%, right after the sale (Webull supports GTC limit for options; 60-day GTC life; cancels at expiry). Cancel the GTC once the first third is over. **21-DTE close: not used** (data unverified, C7). | Sale price, date | Closed or expired call | Log: was the 50% exit taken; days held; next call sold same day (Y/N). After 12 cycles compare the P/L of exits taken vs hold. |
| 7 | **Rolling.** Roll only if the stock is above the strike with ≤ 7 DTE **and** you'd rather keep the shares: buy back, sell the next monthly at a higher strike (up-and-out). Only for a net credit or a debit ≤ 10% of the original premium [house rule; H1/H2 show debits happen]. Otherwise let the shares be called away — that's a max-profit outcome. Never roll down below cost basis. | Price, strike, chain | Rolled or assigned | Log net credit/debit of each roll; any roll breaking the rule is flagged. |
| 8 | **Assignment → the wheel.** When called away, sell a **cash-secured put** on the same ticker, 30–45 DTE, ~0.25–0.30 delta, strike ≤ the price you'd happily pay (G1–G3; Webull Level 1). If put assigned → back to step 5. Before ex-dividend, check if an ITM call's time value < dividend; if so expect early assignment (F3). | Cash = strike × 100 | CSP or new covered call | Cash ≥ strike × 100 before selling a put; log ex-div dates. |
| 9 | **Risk limits** [house rules]. (a) Max 100% of capital in one ETF, max 50% in one single stock (so single stocks only once two positions fit under step 1, e.g. two ≤ $27 at $5,600). (b) If the underlying closes ≥ 20% below cost basis, stop selling new calls below basis; reassess whether you'd still buy it today; if not, sell the shares (a 20% drop ≈ 11 months of premium, see example). (c) No margin, no naked options, no 0DTE. (d) Don't treat premium as spendable income until the call is closed. | Price, basis | Hold/exit decision | Monthly review log; any limit breach flagged. |
| 10 | **Expected returns — set the bar honestly.** Premium "income" ≠ return (N7). Index history: BXM ≈ 6.1%/yr vs S&P ≈ 11.0%/yr (2006–2025, gross); BXMD 9.59%/yr (1990–2018, gross); BXM −29% in 2008. Covered calls lagged buy-and-hold in all 48 FlashAlpha setups (2022–2026). Planning range for a typical year: **roughly 0–10% total return**, with a bad year of **−20% to −30%** possible, and **lagging the underlying in strong up years**. Gross premium at 30Δ will be below BXM's 1.7%/month ATM average (Cboe: BXMD collects less). Single ETF/stock results vary more (B12). | Index data above | Benchmark for review | Each quarter, compare account total return vs simply holding the same shares (log both). |
| 11 | **Taxes.** All closed/expired call premium is short-term = ordinary income rates (K1, K5). Use an IRA if available. Calls ≤ 30 DTE are never QCCs (K2) — another reason for 30–45 DTE. | Account type | Tax note | Year-end: realized short-term gains report from Webull. |
| 12 | **Journal.** One row per trade: date, ticker, price, strike, delta, DTE, bid/ask/fill, fees, exit type, result, account value vs buy-and-hold. | Each trade | Spreadsheet | 12 monthly rows before changing any rule. |

### Worked example (ALL NUMBERS HYPOTHETICAL — not quotes)
$3,000 account. A broad ETF "XYZ" at $27.00, monthly options, next earnings n/a.
- Buy 100 sh = **$2,700**; cash left $300.
- 35 DTE, $28 strike (~0.28Δ). Bid $0.45 / ask $0.50, mid $0.475; filled at **$0.47**. Premium $47.00; fee placeholder $0.10 → net **$46.90**.
- Flat at expiry: $46.90 / $2,700 = **1.74%** for the month. (×12 = 20.8% simple, but see step 10: that is not a return forecast.)
- Called away at $28: ($28 − $27) × 100 + $47 − $0.10 = **$146.90 = 5.44%**.
- Breakeven: $27.00 − $0.47 = **$26.53**.
- XYZ falls 20% to $21.60: (21.60 − 27.00) × 100 + $46.90 = **−$493.10 = −18.3%**. The −$540 stock loss equals ≈ 11.5 months of this premium (540 / 46.9).
- 50% exception: GTC limit = 50% × $0.47 = $0.235 → rounded down to **$0.23**. On day 9 the call is $0.21 bid / $0.23 ask; the GTC fills at $0.23 (48.9% of $0.47) → profit (0.47 − 0.23) × 100 − $0.20 = **$23.80**; sell next month's call the same day.
- At $5,600: two such positions → ≈ $93.80/month, same 1.74%, but a 20% drop in one ETF costs ≈ 9% of the account instead of 18%.

## Correction 2026-10-30 (items 003, 004, 008)
Found by A1/R3 on 2026-10-30. The rows above are kept as written; where they differ, this section wins.
- **Step 1 (003).** At $3,000, trade **one** underlying that passes today's step-3 screen at the step-5 strike of the step-4 expiry and fits both caps: 100 sh ≤ cash − $200 (≤ $28/share) and, for a single stock, ≤ 50% of capital (≤ $15/share). Prefer a diversified ETF if one passes. **Feasibility, 2026-10-30:** 0 tickers confirmed on monthly quotes; no diversified ETF ≤ $28 passes (002/03 L114); F ($11.94, 39.8% of capital) passes only on an 11-06 weekly quote (003/03). Unproven until the paper bot logs monthly scans. If none passes: no trade that day (**UNIVERSE EMPTY**); options are (a) a CSP within the caps on a passing ticker, (b) add funds (two names from about $5.3k), (c) a covered-call ETF. The daily report shows how many of the last 10 logged scans each ticker passed (information, not a gate). [house rule] Check: `screen.feasible_universe` each scan; tests `test_universe_empty_blocks_orders`, `test_shipped_config_has_a_passing_ticker` (SYNTH data only), `test_pass_history_counts_last_10`.
- **Step 1 and 9(a), person's decision 2026-10-31 (023).** At $3,000 you may hold **up to two different single stocks**, each ≤ 50% of capital (≤ $15/share at $3k), with (sum of price × 100) ≤ cash − $200. Each must pass today's step-3 screen on its own. Cap example from the 023 screen: F ($1,233) + VALE ($1,200) = $2,433 ≤ $2,800. On 2026-10-31 neither passes step 3: next earnings dates unpublished → `EARNINGS_UNKNOWN` (item 025). One ETF ≤ $28 alone is still allowed. The paper bot does the same since item 024 (`max_positions: 2`, `portfolio.entry_budget`). [house rule, set by the person]
- **Step 3 (005).** If OI or the next earnings date is unknown, the test fails (`OI_UNKNOWN`, `EARNINGS_UNKNOWN`); an ETF has no earnings.
- **Step 4 (004).** Monthly expiry with **30–45 DTE**; if none, the monthly nearest that window within 7 days of its edges (**23–52 DTE**, ties → later), logged `in_window = False`; if none, no trade that day (`NO_EXPIRY`), retry next scan. Feasibility (2016–2025, Mon–Fri, repo `pick_expiry`): 30–45 alone 55.2% of days; with slack 95.2%; at most 3 business days in a row without one. Example: 2026-10-30 → 2026-12-18, 49 DTE. No 0DTE; weekly rule unchanged. Check: DTE 23–52 and `in_window` logged; tests `test_monthly_coverage_2016_2025`, `test_live_scan_rule_2026_10_30`.
- **Step 5 (004).** Sell the listed call with delta **nearest 0.275**, only if in **[0.20, 0.35]**, else no trade (`NO_STRIKE_IN_TOLERANCE`). Strike ≥ cost basis: if the nearest is below basis, take the lowest strike ≥ basis if its delta ≥ 0.20, else no trade (`BASIS_ABOVE_BAND`). Why: at 35 DTE on a $0.50 grid adjacent strikes are 0.07–0.16Δ apart, so 0.25–0.30 was empty in 3 of 4 cases; it is logged as `in_band`. Limit at the mid as before. Check: delta in [0.20, 0.35], `in_band`, strike ≥ basis, fill vs mid; test `test_tolerance_finds_strike_on_bs_grid`.
- **Step 6 (008).** "first third of its life" means days held × 3 ≤ days of life (e.g. day ≤ **11** of 35, as the bot checks). The GTC buy-to-close limit is 50% of the sale price rounded **down** to the tick.
- **Step 8, Alternative 1 (004).** "30–45 DTE, ~0.25–0.30 delta" → the step-4 expiry and step-5 strike rule (put delta nearest −0.275, |Δ| in [0.20, 0.35]).
- **Step 9(a) (003).** Max 50% of capital in one single stock (≤ $15/share at $3k; `max_single_name_frac: 0.5`), not "only at ≥ $5.6k".
- **Step 11 (004).** Replace "another reason for 30–45 DTE" with: on about 25% of days (2016–2025) the step-4 rule picks 23–30 DTE, and those calls are not QCCs.
- **Worked example, 50% line (008).** Penny class ($0.01 tick below $3, Cboe C2023122104): 50% of $0.47 = $0.235, so the GTC limit is **$0.23** (48.9%). Day 9 quote $0.21 / $0.23 → fills at $0.23; profit (0.47 − 0.23) × 100 − $0.20 = **$23.80**; sell next month's call the same day. On $0.22 / $0.24 it would **not** fill (a buy limit executes only at the limit or lower, SEC Investor.gov), and the bot would not exit either. Non-penny ($0.05 tick): the sale would be $0.45 or $0.50 and the limit $0.20 or $0.25. Test `test_worked_example_50pct_exit`.

## Self-check
Every numeric threshold in the implementation map re-derived from its own check, and every worked example run against its rule's trigger (added by work items 017 and 018). Written against the original rows; where § Correction 2026-10-30 above changes a rule (e.g. step 4's DTE window is now 23–52), the Correction wins.

| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Step 1, $3,000, one position | (cash − 200) / 100 | (3,000 − 200) / 100 = $28.00 | ≤ $28 ✓ |
| Step 1, $5,000 | (cash − 200) / (100 × n) | 4,800 / 200 = $24.00; 4,800 / 100 = $48.00 | two ≤ $24 or one ≤ $48 ✓ |
| Step 1, $5,600 | same | 5,400 / 200 = $27.00; 5,400 / 100 = $54.00 | two ≤ $27 or one ≤ $54 ✓ |
| Step 1, two at $28 | 2 × 28 × 100 + 200 | 5,600 + 200 = $5,800 | needs $5,800 ✓ |
| Step 9(a), single stock ≤ 50% | 100 × price ≤ 50% of cash | at $5,600: $27 × 100 = $2,700 = 48% | ✓ |
| Example, $3,000 at $27 | 2,700 ≤ 3,000 − 200 | 2,700 ≤ 2,800 | ✓ |
| Example, $5,600, two at $27 | 5,400 ≤ 5,600 − 200 | 5,400 ≤ 5,400 | ✓ |
| Example, 30–45 DTE | 35 DTE | 30 ≤ 35 ≤ 45 | ✓ |
| Example, strike ≥ basis | $28 ≥ $27 | | ✓ |
| Example, 50% exit trigger | fill ≤ 0.50 × sale | 0.23 ≤ 0.235 (48.9%) | ✓ |
| Example, 50% exit timing | day ≤ ⅓ of life | day 9 ≤ 35 / 3 = 11.7 | ✓ |

`python3 scripts/check_handoff.py 001` output (pasted):
```
sources count (unique URLs in 01-research.md): 29
fact-check rows: 77
totals line: 77 rows -> 61 as-is, 12 fixed, 4 removed
PASS
```

## Alternative strategy ideas
1. **Wheel-first (CSP entry).** Start by selling a 30–45 DTE, 0.25–0.30Δ cash-secured put instead of buying shares; covered calls only after assignment. Same downside, gets paid while waiting to buy (G1–G3). Webull Level 1.
2. **Covered-call ETF instead of DIY.** E.g., JEPI (0.35% net) or XYLD (0.60%) per 247wallst (2026-07-18); check fund pages. No spreads, no decisions, works at any size; same capped-upside/full-downside profile (KB). Good benchmark to compare the DIY journal against.
3. **Poor man's covered call (later, ≥ Level 3 margin).** Long 6–12 mo, Δ0.70–0.80 call + short 2–6 wk call (Saxo; tastylive rules: debit ≤ 75% of width, short premium ≥ long extrinsic). Reaches pricier underlyings with less capital, but can lose the whole debit (I3). Not a starting strategy.

## Still open (not blocking)
- No direct test of the 50% rule on covered calls (searched again today).
- tastytrade 21-DTE data unfetchable.
- Webull's exact per-contract regulatory/clearing fees and any assignment fee — read off the first trade confirmation (step 2).
- Account type (IRA vs taxable) and whether money will be added (decides when step 1 allows a second position).
