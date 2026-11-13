# 061 Pre-registered pass criteria (written 2026-11-13, before any real-quote result was seen)

These are fixed now so the results can't move the goalposts. Change them only in a new dated
section that says why, never by editing this one.

## A. Backtest gate (real quotes, bid fills, all costs) - decides whether paper trading continues
Run on the bot rule exactly as configured (delta 0.25-0.30, 30-45 DTE, no call through earnings,
hold to expiry) with no parameter chosen from the results.

| # | Test | Pass if |
|---|---|---|
| A1 | Edge exists: sold IV vs realized vol over each call's life, pooled across stocks | sold IV > realized vol on >= 55% of calls AND mean option P&L per call > 0 after the bid fill and fees |
| A2 | Return vs holding, per stock | covered call CAGR >= buy-and-hold CAGR - 1.0 pt/yr on at least half the stocks |
| A3 | Risk vs holding, per stock | covered call max drawdown no worse than buy-and-hold on >= 80% of stocks |
| A4 | Risk-adjusted, pooled | median (CAGR / abs(max drawdown)) of covered calls >= buy-and-hold's |
| A5 | Walk-forward (24-month train, 6-month test, config picked across all stocks) | out-of-sample excess CAGR vs buy-and-hold >= -1.0 pt/yr, median across stocks |
| A6 | Benchmark sanity | report BXM vs SPY total return over the same dates (no pass/fail; tells us whether the market as a whole paid for selling calls in this window) |

A stock that fails A2 and A3 both is dropped from the lists. If A1 fails pooled, the strategy is
an income wrapper with no measured edge, and the scale-up gate below can't be passed.

## B. Scale-up gate: more than $5k (paper, then live)
All must hold at the same time, measured from the ccbot paper ledgers:

1. **100 closed paper calls** (expired, assigned or bought back) under the current rule, across at
   least 6 different stocks and at least 6 calendar months.
2. **Fills:** median paper sell fill >= bid + 25% of the spread, and logged slippage vs mid within
   what the backtest assumed (bid fills). If paper fills are only ever at mid, treat them as
   unproven and use bid in every comparison.
3. **Matches the backtest:** paper premium yield per month and call-away rate each within
   +/-30% (relative) of the 061 backtest's numbers for the same stocks.
4. **Beats holding:** paper account total return >= buy-and-hold of the same shares over the same
   dates minus 1 pt (annualised), and >= the BXM index over the same dates minus 2 pts.
5. **Drawdown:** paper max drawdown no worse than 1.2x the 061 Monte Carlo median for a 2-stock
   book, and no single stock > 50% of capital.
6. **Every number reproducible** from the committed ledgers and data with one command.

Step size if all pass: at most double (to $10k), then re-check after the next 50 closed calls.
Any single month with a loss > 2x the Monte Carlo 95th-percentile monthly loss pauses new
money until reviewed.
