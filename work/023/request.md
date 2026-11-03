# Work item 023
Type: IDEA
Scope: RESEARCH ONLY
Waived: 02 (A1, 2026-10-31, item 026: the screen was already delivered; R3's fact check was run afterwards in 026; the person can ask for the R2 language search)
Opened by: person
Date: 2026-10-31
## What we want
Screen real tickers that fit 001's rules for a $3,000 covered-call account, and list for each why it fits (price, liquidity, option premium, volatility, earnings and dividend dates, stability) and its risks. Current market data, every number sourced, nothing made up.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
n/a (IDEA)
## Root cause and prevention guardrail (BUG only)
n/a
## Recurring issue link (RI-#, if any)
RI-001 (rule assumed to have candidates): this item computes the count.
## Done looks like
A dated shortlist with a pass/fail per 001 screen test (price caps: ETF <= $28, single stock <= $15 at $3k; monthly options; spread <= $0.05 and OI >= 500 at the ~0.275 delta strike; no earnings before expiry), sources for every number, and a plain list of reasons and risks per ticker.
