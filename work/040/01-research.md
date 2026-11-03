# 01 Research brief - 040
Prepared 2026-11-03 for a FAST item (person's choice). Most of the facts come from 023 (`work/023/01-research.md`) and were re-read for this brief where marked.

## Question
What does the paper bot need to trade F, VALE and AAL on Webull sandbox data, and what is known about each ticker's earnings and dividends?

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- W1. Webull has a sandbox (test) environment, and its trading API host is `api.sandbox.webull.com`. [https://developer.webull.com/apis/docs/sdk]
- W2. Sandbox API applications are "approved automatically and typically" within a few minutes. [https://developer.webull.com/apis/docs/authentication/IndividualApplicationAPI]
- W3. In the sandbox, market data that needs a subscription is served as "15-minute delayed data" by default. [https://developer.webull.com/apis/docs/market-data-api/overview]
- W4. Whether the sandbox returns option chains/snapshots: UNVERIFIED (not stated on the overview page; the first VPS run will show it).
- F1. Ford reported Q3 2026 on Oct 28, 2026, and declared a $0.15 Q4 dividend, payable Dec 1, record date Nov 10. [https://www.businesswire.com/news/home/20261028111591/en/Ford-Reports-Third-Quarter-2026-Financial-Results/]
- F2. Ford's ex-dividend date = the record date (Nov 10) under T+1 settlement: UNVERIFIED as a Ford statement (the release gives no ex-date). Entered in tickers.json and labelled in its sources list.
- F3. Ford's next earnings date: not published (023). [https://stockanalysis.com/stocks/f/]
- V1. Vale's earnings date shown as Oct 29, 2026. Next: not published. Last ex-dividend Aug 13, 2026. Next ex-date: not found. [https://stockanalysis.com/stocks/vale/] [https://stockanalysis.com/stocks/vale/dividend/]
- A1. American Airlines' earnings date shown as Oct 22, 2026. No dividend since Feb 2020. [https://stockanalysis.com/stocks/aal/] [https://stockanalysis.com/stocks/aal/dividend/]
- E1. The 70-day earnings gap is a **house rule set by the person on 2026-11-03**, not a sourced fact. Reasoning: quarterly reports are about 91 days apart, and 70 days leaves a 3-week margin for an early report.

## Numbers used (show the math)
- F: Oct 28 + 70 days = Jan 6, 2027. VALE: Oct 29 + 70 = Jan 7, 2027. AAL: Oct 22 + 70 = Dec 31, 2026. The Dec 18, 2026 monthly expiry falls before all three, so no EARNINGS block for that expiry.
- Ford's dividend on 100 shares: 0.15 × 100 = $15.

## Fit for a ~$3k account
This changes no caps. Two single stocks, each ≤ 50% (item 024).

## Open questions
W4 (sandbox option data). F2 (Ford's exact ex-date).
