# 01 Research brief - 054
Prepared 2026-11-12. Snapshots dated Oct 26 – Nov 9, 2026; none are live quotes.

## Question
Which stocks ≤ $80 have weekly options, and what facts does the bot need for them?

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- W1. Cboe's weeklys page lists equities only in a client-rendered table (not readable here). [https://www.cboe.com/available_weeklys/]
- W2. Expiries Nov 13 and Nov 20, 2026 both appear in Cboe delayed option data for F, AAL, T, KGC, SOFI, PFE, VZ, CCL, BAC, CSX, OXY, PYPL (weekly + monthly). [https://cdn.cboe.com/api/global/delayed_quotes/options/BAC.json]
- P1. SOFI $16.76, last earnings Oct 27, 2026. [https://stockanalysis.com/stocks/sofi/]
- P2. BAC $50.52, last earnings Oct 14, 2026; ex-div Dec 4, 2026 $0.32. [https://stockanalysis.com/stocks/bac/] [https://stockanalysis.com/stocks/bac/dividend/]
- P3. CSX $51.31, last earnings Oct 21, 2026. [https://stockanalysis.com/stocks/csx/]
- P4. OXY $56.38, last earnings Nov 9, 2026. [https://stockanalysis.com/stocks/oxy/]
- P5. PYPL $59.24, last earnings Oct 27, 2026. [https://stockanalysis.com/stocks/pypl/]
- P6. CCL prev close $29.44; "Est. Earnings" Dec 18, 2026 (site estimate). [https://stockanalysis.com/stocks/ccl/]
- H1. Price history Aug–Oct 2026 (50 daily rows each): weekly high-low range 4–10%; after a down week the next was up about 1 in 3. [https://stockanalysis.com/stocks/bac/history/]
- X1. Over $80 or stale: KO $96.03, CSCO $93.85, CVS $83.85; WFC page from 2025. [https://stockanalysis.com/stocks/ko/]

## Numbers used (show the math)
- Cash = 12 × $8,000 + $200 = $96,200; frac = 1/12 → cap 0.083333 × 96,200 = $8,016.67 per stock.
- 100 sh of PYPL at $59.24 = $5,924 ≤ $8,016 (1 lot); F at $12.44 → floor(8,000 / 1,244) = 6 lots.
