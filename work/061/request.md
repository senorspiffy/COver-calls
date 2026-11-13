# Work item 061
Type: IDEA
Scope: RESEARCH ONLY
Opened by: person ("Apply this to new thread", 2026-11-13, on the coordinator's rewritten prompt)
Date: 2026-11-13

## What we want
Using real historical option quotes (bid/ask/IV) and daily prices with dividends for the candidate
stocks, test whether selling covered calls has beaten buy-and-hold, and whether BXM has beaten SPY,
after realistic fills and costs, walk-forward with no lookahead. Per stock: implied vs realized vol,
worst drawdown, how often shares were called away. Propose rules for rolling, earnings and
assignment. Define, in advance, the paper results that would justify more than $5k.

## Evidence
- Every earlier replay (002, 057) priced options with Black-Scholes from recent volatility; none
  used real quotes (057/03: "Option prices match market: UNSUPPORTED").

## Done looks like
- `scripts/fetch_real_data.py` (free data: DoltHub post-no-preference options/stocks/earnings, Cboe BXM)
- `ccbot/realtest.py` + `tests/test_realtest.py`
- `work/061/pass-criteria.md` committed BEFORE any real-data result exists (pre-registration)
- `reports/real/` results and `work/061/01-research.md` with every approximate number labelled
