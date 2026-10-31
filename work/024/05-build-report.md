# 05 Build report - 024
Built 2026-10-31 in the 023 thread at the person's request ("we have to graduate everything from paper ... why would we do 1?"). Short path: no separate I1 plan file. The rule being built is the person's own decision (001 Correction, Step 1 and 9(a)), so there was no outside claim to research.

## What changed
| File | Change |
|---|---|
| `ccbot/portfolio.py` (new) | `Portfolio(cash, positions{ticker: State})`. `lend()` gives one sleeve a cash budget so the existing `rules` helpers run unchanged and books the change back. `entry_budget()`: ETF = all cash; stock = min(cash, 50% × capital + buffer). `portfolio_equity()`. `from_dict` loads a pre-024 single-State ledger. |
| `ccbot/bot.py` | `run_daily` manages held tickers first, then opens new ones from `passing` until `max_positions` is reached. An INSUFFICIENT_CASH ticker does not use a slot, so the next passing ticker is tried. Rows carry `ticker`. The scan has `contexts` (list), `would_act` per ticker and `max_positions`. |
| `ccbot/broker/sim.py` | Ledger is a Portfolio. Fills, settlement and GTC re-checks go through `lend`. `buy_shares` refuses a new ticker when `max_positions` are held. Events carry `ticker`. |
| `ccbot/broker/base.py` | `validate` accepts a Portfolio and checks the order's own sleeve (NAKED_CALL and NO_POSITION_TO_CLOSE are per ticker). |
| `ccbot/report.py` | Daily: one line per position, a Ticker column in the decisions and would-act tables, one context per ticker. Weekly B&H: tickers priced on both the first and last scan, bought in order with the same caps. Pre-024 scans (`context`) still read. |
| `config` | `max_positions: 2` (validated ≥ 1) in DEFAULTS and default.json. |

## Unchanged on purpose
- The backtest still runs one State on one series. `test_bot_on_simbroker_matches_backtest_v0` still passes, so the bot and the backtest still share every rule.
- The Webull sandbox stays dry-run, and stock orders are not sent.

## Behaviour change to note
A single stock is now capped at 50% of capital **when shares are bought**. Before this item, a $5 stock bought floor(2800/500) = 5 lots ($2,500, 83%), which broke 001 step 9(a). It now buys 3 lots ($1,500). This is test `test_cheap_stock_buys_only_up_to_half`.

## Tests
`python -m pytest -q` → 135 passed, 1 skipped (it was 126 passed, 1 skipped before). New: `tests/test_portfolio.py` (9 tests: two stocks opened within caps, max_positions 1, next day manages and opens nothing, the 50% cap on a cheap stock, entry budget, lend/prune, old ledger loads, config validation, two-stock weekly B&H).
Mutations: removing the stock cap in `entry_budget` → 4 failed; ignoring `max_positions` in the bot → the slot tests fail. Both were restored, and the suite passes.
`python -m ccbot scan --date 2026-10-30` on the sample still buys SYNTH_A and sells the Dec 18 $26 call, and the report shows the new layout.
