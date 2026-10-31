# 05 Build report - 025
| File | Change |
|---|---|
| `ccbot/tickers.py` (new), `config/tickers.json` (new) | Facts per ticker: asset_type, next/last earnings, ex-div date and amount, with sources (from 023). **House rule:** when no next earnings date is published, it is estimated as last report + `earnings_gap_days` (70). The Day is flagged `earnings_estimated` and the report says "(estimated …)". Once that date passes with nothing new entered, earnings are unknown again and the stock is blocked. The dividend is credited on the ex-date. |
| `config/paper.json` (new) | universe F, VALE, AAL; tickers_file; earnings_gap_days 70. |
| `ccbot/broker/webull_sandbox.py`, `broker/sim.py`, `broker/__init__.py`, `__main__.py` | `--broker webull-paper`: the WebullSandboxBroker with `paper=True`. Its SimBroker ledger takes quotes from Webull (`SimBroker(quotes=…)`) and fills locally (sell at limit ≤ bid, buy at limit ≥ ask). Order endpoints are never called, and no account ID is needed. All the sandbox-only guards still apply. |
| `ccbot/bot.py` | Capital and equity mark each open call at its **quoted mid**, falling back to BS on the day's vol, else NaN (never 0). The Webull feed has no vol, so without this, equity was NaN while a call was open. |
| `ccbot/missing.py`, `tests/test_missing_inputs.py` | `snapshot.iv` is now a fallback (marked at the quote), not n/a. |
| `tests/test_paper.py` (new) | Estimate, its expiry → blocked, given date wins, quote mark / NaN, and an end-to-end webull-paper scan on a fake SDK: buys 100 F, sells the 13.5C at the bid, 0 order calls to Webull. |

Tests: 141 passed, 1 skipped. The sample sim scan is unchanged. `scan --broker webull-paper` without keys → exit 3 (refused).
Not verified: whether the Webull sandbox returns option chains (Webull docs: market data that needs a subscription is 15-min delayed in the sandbox; options need OPRA). The first VPS run will show it.
