# 01 Research brief - 001

Prepared by R1 on 2026-10-30. This is research, not personal financial advice, and no trades were placed. Prices and premiums marked "hypothetical" are made up to show the arithmetic. They are not market quotes.

## Question
The person has about $3,000 and wants a rule-based way to sell covered calls for steady income while growing the account. This brief covers:
1. whether $3,000 is enough or whether $5,000-$6,000 is better,
2. which cadence fits (0DTE, weekly, monthly or 30-45 DTE),
3. whether the person's rule (sell a call, buy it back at 50% profit, repeat) holds up, and what the alternatives are,
4. stock selection, strike/delta, expiration, exit/roll rules, what to do on assignment, taxes, and realistic returns.

Logs checked first: `logs/recurring-issues.md` has no entries yet, and `logs/research|audit|efficiency|implementation` are empty, so there is no earlier work to reuse.

## Findings (one claim per line, each with [source URL] or UNVERIFIED)

### A. What a covered call is and what it does to risk
- A1. A covered call caps upside: the most you can make is (strike − stock cost) + premium. [https://www.fidelity.com/bin-public/060_www_fidelity_com/documents/learning-center/092321_Writing_Covered_Calls_Deck.pdf]
- A2. Risk is the stock's cost minus the premium received, so the premium is the only cushion against a drop. [same Fidelity deck]
- A3. The writer "continues to bear the downside risk of stock ownership if the stock price decreases more than the premium received". The premium offsets "some… though certainly not all" of the losses. [https://www.fidelity.com/learning-center/investment-products/options/why-use-a-covered-call]
- A4. Covered calls suit a view that the stock will "stay steady or go up slightly". They are probably not right for a stock you are extremely bullish on. [same Fidelity page]
- A5. An in-the-money call can be assigned at any time before expiration, which forces the sale. [same Fidelity page]
- A6. AQR finds covered calls earn the volatility risk premium on top of the equity risk premium. AQR also finds that much of their risk comes from uncompensated "active equity exposure". [https://www.aqr.com/insights/research/journal-article/covered-calls-uncovered?aqrPDF=1]
- A7. Some sources describe a covered call as economically similar to a cash-secured short put at the same strike. No primary source was fetched for this, so it is UNVERIFIED (the OIC page checked does not state it).

### B. Historical returns (index evidence)
- B1. BXM methodology: hold the S&P 500 and sell a one-month call held to expiration (generally the third Friday). The strike is the nearest listed one above the index level just before 10:00 a.m. CT, which is roughly at the money. [https://sec.gov/files/rules/sro/cboe/2008/34-57946.pdf]
- B2. From 6/30/1986 to 1/31/2012, BXM returned 9.2% a year with 11.4% standard deviation. The S&P 500 returned 9.2% a year with 15.9% standard deviation. [https://cdn.cboe.com/resources/education/research_publications/HewittEnnisKnupp-BXM-(2012).pdf]
- B3. Same study: BXM "tends to underperform the S&P 500 Index during periods of sharply rising markets". In 2008, BXM fell 29% while the S&P 500 fell 37%. [same]
- B4. From 6/1988 to 8/2006, BXM returned 11.77% a year with 9.29% standard deviation and a 0.77 Sharpe ratio. The S&P 500 returned 11.67% a year with 13.89% standard deviation and a 0.51 Sharpe ratio. The worst S&P 500 drawdown in that window (9/2000 to 10/2002) was −47.4%, versus −32.5% for BXM. [https://cdn.cboe.com/resources/education/research_publications/Callan_CBOE.pdf]
- B5. Calendar-year total returns for 2006-2025 (selected years, BXM vs S&P 500): 2008 −28.65% vs −37.00%; 2013 13.26% vs 32.39%; 2019 15.68% vs 31.49%; 2020 −2.75% vs 18.40%; 2022 −11.37% vs −18.13%; 2023 11.82% vs 26.26%; 2024 20.12% vs 25.00%; 2025 8.91% vs 17.86%. [https://www.ftportfolios.com/Commentary/MarketCommentary/2026/3/24/an-update-on-covered-call-returns]
- B6. Calculated from all 20 annual figures in B5 for 2006-2025: BXM compounded about 6.1% a year and the S&P 500 about 11.0% a year. BXM beat the S&P 500 in only 5 of the 20 years. See the math in N6. [calculation from the FT Portfolios table]
- B7. Since May 2006, BXM (writing at-the-money SPX calls) has collected about 1.7% gross premium a month on average. [https://www.cboe.com/insights/posts/benchmark-indices-series-income-generation-and-smoother-returns-with-cboes-bxm-bxmd-put-and-cmbo-indices]
- B8. BXMD sells the monthly SPX call nearest 30 delta, so it is out of the money. [https://www.indexologyblog.com/2018/09/04/strong-returns-over-32-years-for-bxmd-index-that-writes-otm-spx-options/]
- B9. From Jan 1990 to Dec 2018, gross of fees: BXMD returned 9.59% a year with 12.31% volatility and 0.82 beta. BXM returned 8.14% a year with 10.11% volatility and 0.62 beta. [https://www.nb.com/-/media/NB/Article-Assets/wp_index_option_writing_strategy_benchmarks.pdf]
- B10. Since September 2002, the 30-delta index (BXMD) has "roughly doubled the performance of BXM". [https://dorseywright.nasdaq.com/research/bigwire/2025/05/27/05-27-2025/optimizing-a-covered-call-strategy]
- B11. The NB paper says writing weekly or laddered (BXMW) instead of monthly (BXM) "detracted over 180bps of performance in 2018". That is a single year and not proof either way. [NB paper above]
- B12. These are index results on the S&P 500, with no commissions, taxes or bid/ask costs. A single-stock account will differ, possibly by a lot. Any precise single-stock return estimate is UNVERIFIED.

### C. Cadence (0DTE, weekly, monthly)
- C1. The rate of theta decay speeds up as expiration nears, and "the steepest theta decay generally occurs with 5-7 days until expiration". The same article warns there is "very little (or no) time left for a tested position to recover". [https://tastylive.com/news-insights/time-decay-tick-tock]
- C2. Shorter terms (1-2 weeks) give faster decay but smaller premiums. Longer terms (1-2 months) give higher premiums and more downside cushion but slower decay. [Fidelity deck, A1]
- C3. Example: four weekly at-the-money SPY calls brought in about 92% more premium than one 30-day call ($21.92 vs $11.37). The source notes this takes more effort and may reduce downside protection. [Nasdaq Dorsey Wright, B10]
- C4. 0DTE: "theta decay on a zero DTE option is nearly 100x faster than a 45 day option as a % of the total premium". The author adds that the higher return "must in some form carry the commiserate amount of risk". [https://tastylive.com/news-insights/theta-0dte-options]
- C5. Cboe on 0DTE: "As expiration approaches, options near the money are extremely sensitive to movements in the underlying index". The products carry risk of loss "which can be substantial". [https://www.cboe.com/tradable-products/0dte]
- C6. Daily expirations are mainly an index and large-ETF feature (Cboe cites SPX and XSP 0DTE volume). Most stocks under $30 do not have daily expirations. [Cboe 0DTE page; that sub-$30 stocks lack them is UNVERIFIED and should be checked per ticker]
- C7. tastytrade's general practice of opening around 45 DTE and managing around 21 DTE is widely cited. The study pages could not be fetched (landing pages only), so the supporting numbers are UNVERIFIED.

### D. The 50%-profit buy-back rule
- D1. tastylive: "We tend to close our winners when we reach 50% profit". The stated reasons are a higher win rate than the entry probability of profit, the remaining reward shrinking relative to the risk still held, and freeing capital to redeploy. [https://www.tastylive.com/definitions/managing-winners]
- D2. The same page warns that closing too early can mean gains that don't cover commissions. [same]
- D3. That page presents 50% as experience-based, with no backtest data. The tastylive Market Measures studies on managing winners (e.g., 12/04/2015 "managing winners varying profit targets") would not load beyond landing pages. They also mostly study strangles, not covered calls. Any specific claim that the 50% rule improves covered-call P/L is therefore UNVERIFIED. [https://www.tastylive.com/shows/market-measures/episodes/managing-winners-varying-profit-targets-12-04-2015]
- D4. A covered-call caveat (reasoning, not a source): buying back the call removes the cap while you still hold the shares. If no new call is sold right away, the account is just long stock with full downside. UNVERIFIED as an empirical effect.

### E. Strike / delta selection
- E1. In-the-money strikes give the most premium and downside protection but the least profit potential. At-the-money strikes have the most time value. Out-of-the-money strikes give the least premium but the most upside. [Fidelity deck, A1]
- E2. "Some option sellers find 30 delta to be the sweet spot between generating premium and preserving upside." [Nasdaq Dorsey Wright, B10]
- E3. Index evidence supports 30-delta over at-the-money writing for long-run return (BXMD 9.59% vs BXM 8.14% a year, 1990-2018) at the cost of more volatility (12.31% vs 10.11%). [NB paper, B9]

### F. Stock selection
- F1. Liquidity: "Narrow bid-ask spreads typically signal high liquidity". A 50-cent-wide spread "indicates an illiquid market". High open interest indicates "ample liquidity". No numeric thresholds are given. [https://www.tastylive.com/concepts-strategies/options-liquidity]
- F2. Earnings: "Stocks often see sharp moves around earnings announcements". Implied volatility "tends to be elevated before earnings" and "can sometimes collapse" afterward. [https://www.schwab.com/learn/story/trading-options-around-earnings-announcements]
- F3. Dividends and early assignment: if the call is in the money and "the dividend exceeds the remaining time value of the option" there is "a good chance" of early exercise, likely the day before the ex-dividend date. Fidelity's advice is to "Know if the stock or ETF pays a dividend and when it will start trading ex-dividend". [https://fidelity.com/learning-center/investment-products/options/dividends-options-assignment-risk]
- F4. Only write calls on a stock you are "ok with keeping" and willing to sell at the strike. [Fidelity why-use page, A3]
- F5. Any specific numeric screen (for example open interest ≥ 500 or spread ≤ $0.05) is a house rule, not a sourced fact: UNVERIFIED.

### G. Assignment and the wheel
- G1. The wheel: (1) sell an out-of-the-money cash-secured put on a stock you want to own; (2) if assigned, buy the shares; (3) write covered calls; (4) if called away, go back to step 1. [https://www.schwab.com.sg/story/three-things-to-know-about-wheel-strategy]
- G2. Wheel risks: being stuck with shares that "continue to fall in value", being assigned shares "in a troubled company", and cash being tied up in cash-secured puts. [same]
- G3. A cash-secured put means "writing a put option and simultaneously setting aside the cash to buy the stock if assigned". [https://www.optionseducation.org/strategies/acquire-stock]
- G4. At Fidelity, covered calls, rolling covered calls and cash-covered puts are Tier 1. Spreads (needed for a PMCC/diagonal) are Tier 2. [https://www.fidelity.com/options-trading/faqs]

### H. Rolling
- H1. Rolling means buying back the short call and selling another. Rolling to a later expiration may bring "further credits because the longer-dated contracts will have more time value". [https://www.tradestation.com/insights/2025/10/29/rolling-options-key-points/]
- H2. That article's up-and-out example cost a net debit of about $0.50. Rolling "may entail risk by extending the amount of time in a position, during which the underlier can lose value". [same]
- H3. A rule such as "roll only for a net credit" is a common heuristic, but no primary source was found for it: UNVERIFIED.

### I. Poor man's covered call (PMCC)
- I1. A PMCC is a diagonal: long a deep in-the-money call months to years out, short a 30-60 DTE out-of-the-money call. [https://www.tastylive.com/concepts-strategies/poor-man-covered-call]
- I2. tastylive rules: the short call's premium should be at least the long call's extrinsic value, and the total debit should be no more than 75% of the strike width. [same]
- I3. Max loss is the long call's cost minus the short premium. Early assignment is a risk when the stock moves well above the short strike. [same]
- I4. Saxo suggests a long call of 6-12 months with delta about 0.70-0.80 and a short call 2-6 weeks out. [https://www.home.saxo/it-it/learn/guides/options/understanding-the-poor-mans-covered-call]
- I5. A PMCC needs spread approval (Fidelity Tier 2, see G4). It does not collect dividends (the long call holder isn't a shareholder, UNVERIFIED as stated here). It can lose 100% of the long call if the stock falls hard (I3).

### J. Costs
- J1. Schwab: $0 base plus $0.65 per options contract online. $0 for online stock trades. $0 for exercise and assignment online. [https://www.schwab.com/pricing]
- J2. Exchange and regulatory fees (ORF, TAF, SEC fee) also apply per contract or per sale but are small. Exact current amounts were not confirmed: UNVERIFIED.

### K. Taxes (US)
- K1. A call premium is not income when the call is sold. If it expires or is bought back, the result is a short-term gain or loss no matter how long it was open. If assigned, strike plus premium becomes the stock's sale price. [https://www.fidelity.com/learning-center/investment-products/options/tax-implications-covered-calls]
- K2. Qualified covered calls (QCC) have more than 30 days to expiration when written and are not "deep in the money". Calls out of the money or at the money let the stock's holding period continue. In-the-money QCCs suspend it. Non-qualified covered calls fall under straddle rules. [Fidelity tax page above; https://www.schwab.com/learn/story/how-are-options-taxed]
- K3. Wash-sale rules apply to options. [Schwab tax page]
- K4. The exact "deep in the money" benchmark tables are in 26 CFR 1.1092(c)-4 (for example, the lowest qualified benchmark is no lower than 85% of the stock price in one example). Full thresholds were not extracted: UNVERIFIED beyond that. [https://govinfo.gov/content/pkg/CFR-2020-title26-vol13/pdf/CFR-2020-title26-vol13-sec1-1092c-4.pdf]
- K5. Implication: weekly and 0DTE calls (30 days or less) can never be qualified covered calls (K2). Practically all covered-call income in this account will be short-term and taxed at ordinary rates unless it is held in an IRA. The ordinary-rate point is UNVERIFIED in this brief (no IRS rate page fetched).

## Numbers used (show the math)

N1. Share price limit by account size (100 shares per contract):
- $3,000 / 100 = $30.00 maximum share price, with $0 left over.
- $5,000 / 100 = $50.00; or two positions at ≤ $25.
- $6,000 / 100 = $60.00; or two positions at ≤ $30.
- With $3,000 the account holds one position, so 100% of capital is in one stock. With $6,000 it can hold two sub-$30 positions at about 50% each.

N2. Hypothetical covered call (prices made up for illustration, not quotes). Buy 100 shares at $28.00 and sell one 30-DTE $30 call at $0.50, paying the Schwab fee of $0.65 per contract (J1).
- Cost = 100 × $28.00 = $2,800.00.
- Net premium = 100 × $0.50 − $0.65 = $49.35. Return if the stock is flat at expiry = $49.35 / $2,800 = 1.76% for the month.
- Return if called away = (30 − 28) × 100 + $50.00 − $0.65 = $249.35, or $249.35 / $2,800 = 8.91%.
- Breakeven at expiry = $28.00 − $0.50 = $27.50 per share (plus $0.0065 per share in fees).
- If the stock falls 20% to $22.40: (22.40 − 28.00) × 100 + $49.35 = −$560.00 + $49.35 = −$510.65, or −18.2% of $2,800.

N3. The 50% rule on the N2 trade. Buy back at $0.25:
- Profit = 100 × ($0.50 − $0.25) − 2 × $0.65 = $25.00 − $1.30 = $23.70.
- That is 48% of the $49.35 you would keep by holding to expiry, and it frees the shares to sell a new call sooner.
- Fees matter on small premiums. On a $0.10 premium, 50% is $5.00 gross and $5.00 − $1.30 = $3.70 net, so fees eat 26% of the gain.

N4. Yearly commission drag at $0.65 per contract on a $3,000 account (one contract per cycle):
- 0DTE, opening only, ~252 trading days: 252 × $0.65 = $163.80, or 5.46% of $3,000. (The 252 trading days per year is a standard assumption, UNVERIFIED here.) 0DTE on single stocks is mostly not available (C6).
- Weekly, open and close: 52 × $1.30 = $67.60, or 2.25%. Open only: 52 × $0.65 = $33.80, or 1.13%.
- Monthly, open and close: 12 × $1.30 = $15.60, or 0.52%.

N5. PMCC capital vs shares, using the tastylive example (I1-I3) with XYZ at $100:
- 100 shares cost $10,000.
- PMCC: long $90 call at $15.00 and short $105 call at $2.00. Net debit = ($15.00 − $2.00) × 100 = $1,300 = max loss. Max profit = (105 − 90 − 15 + 2) × 100 = $200. Debit as a share of width = $1,300 / ($105 − $90 = $15 × 100 = $1,500) = 86.7%. That is above the 75% guideline, so even the source's own example would fail that rule (I2).

N6. BXM vs S&P 500, 2006-2025 (20 annual returns from B5, compounded):
- S&P 500: product of (1 + r) = 8.05, so 8.05^(1/20) − 1 = 11.0% a year.
- BXM: product = 3.26, so 3.26^(1/20) − 1 = 6.1% a year.
- $3,000 at those rates for 20 years: S&P 500 about $3,000 × 8.05 = $24,150; BXM about $3,000 × 3.26 = $9,780. This is gross, before fees and taxes.
- BXM beat the S&P 500 in 5 of 20 years (2007, 2008, 2011, 2015, 2022).

N7. Average premium vs total return: about 1.7% a month gross premium (B7) × 12 = 20.4% a year in premium. Yet BXM's annualized total return was about 6.1% (N6). The gap is mostly upside given up when the market rises past the strike, plus drawdowns. Premium income is not the same as return.

## Fit for a ~$3k account
- $3,000 works mechanically but is concentrated. Only stocks at or under $30 qualify (N1), and all capital sits in one name, so one bad stock event dominates results (A2, A3, N2).
- $5,000-$6,000 is better for diversification, not for income rate. It allows two positions or a wider choice of stocks ($50-$60). The income percentage is about the same because premium scales with capital.
- Cadence: monthly (30-45 DTE) fits best. Fees are lowest (N4), it is the only cadence eligible for qualified-covered-call treatment (K2, K5), it needs the least monitoring, and the best-documented benchmarks (BXM, BXMD) are monthly (B1, B8). Weekly is possible but fees cost about 2% a year at this size (N4), and the one data point found shows weekly writing trailing (B11). 0DTE mostly doesn't exist on sub-$30 stocks (C6) and has the highest fee drag (N4).
- Strike: about 30 delta out of the money has the best index evidence (B9, B10, E2), and it leaves room for the account to grow with the stock.
- The 50% buy-back is reasonable but not proven for covered calls (D1-D3). At this size, check that 50% of the premium is well above the $1.30 round-trip fee (N3). Re-sell promptly or the shares are uncapped and unhedged (D4).
- Assignment: the wheel (sell a cash-secured put, then covered calls) works with Tier 1 approval (G1, G4). A cash-secured put on a $30 strike needs $3,000 cash (calculated: 30 × 100).
- PMCC lets $3k reach higher-priced stocks (N5), but it needs Tier 2 spread approval and can lose the whole debit. Not recommended as a starting point for this account (I3, I5).
- Realistic expectation: from index history, covered calls give lower volatility and smaller drawdowns, but in strong bull markets they lag buy-and-hold by a lot (B3, B5, B6). "Steady income" is not "steady growth". Single-stock results will vary more than the index (B12).

## Open questions
1. Account type: IRA or taxable? This changes the tax drag a lot (K5).
2. Which broker, and what options approval level is already granted? (G4)
3. Is a lower-cost, liquid ETF under $30 with monthly options acceptable instead of a single stock? Specific tickers and liquidity need live quotes (F1, F5).
4. Can R2 or anyone find a primary study of the 50% rule on covered calls specifically (D3), and the tastytrade 45/21 DTE data (C7)?
5. Exact current ORF/TAF/SEC fee amounts (J2) and the full QCC strike-benchmark table (K4).
6. Will the person add money over time? That decides when a second position (the $5-6k level) becomes possible.
