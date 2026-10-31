# 05 Build report - 002

Prepared by I2 on 2026-10-30. Input: `work/002/04-build-plan.md` (FIT WITH CHANGES). Research, not financial advice. Nothing connects to a brokerage and no order was placed. **Every number below is MODELLED (Black-Scholes) on SYNTHETIC data and says nothing about real markets.**

## Changes made (file: what changed)

48 new files and 1 changed file. The package is 2,232 lines.

| File | What changed |
|---|---|
| `pyproject.toml` | Package `ccbot`, Python >= 3.10, deps numpy + pandas, extras `dev = [pytest]` and `webull = [webull-openapi-python-sdk==3.0.4]`, pytest `testpaths`/`pythonpath = tests`. Verified with `pip wheel`, which builds `ccbot-0.1.0-py3-none-any.whl`. |
| `.gitignore` | Ignores `state/`, `conf/`, `.env`, `*.key`, `webull_*_sdk.log`, `reports/daily_*.md`, `reports/weekly_*.md`, `__pycache__/`, `.pytest_cache/`, `*.egg-info/`, `build/`. |
| `.env.example` | `WEBULL_ENV=sandbox` plus empty `WEBULL_APP_KEY`, `WEBULL_APP_SECRET` and `WEBULL_ACCOUNT_ID`. |
| `README.md` | New section "Covered-call backtester and paper bot (ccbot)": install, tests, the commands, how to use your own CSV, what MODELLED/SYNTHETIC mean, safety rules, and "Live trading is not built". |
| `config/default.json` | As in the plan, plus `monthly_slack_days: 7` (deviation 2). A test checks it equals `config.DEFAULTS`. |
| `ccbot/__init__.py` | `BANNER_MODELLED`, `BANNER_SYNTHETIC`, `__version__`. |
| `ccbot/__main__.py` | CLI `make-sample`, `backtest`, `scan`, `report`. `--live` exits 3. Exit codes are 0, 2 (bad input) and 3 (`LiveTradingDisabled`). |
| `ccbot/config.py` | `DEFAULTS`, `load_config(path, overrides)` (deep merge), `validate`, `ConfigError`. |
| `ccbot/pricing.py` | `norm_cdf` (math.erf), `bs_price`, `bs_delta` (Merton q; intrinsic at T<=0 or σ<=0), `grid_range`, `strike_grid`, `pick_strike(chain, target, tolerance)`. |
| `ccbot/costs.py` | `round_tick`, `half_spread` (fixed / pct_of_mid with floor), `fill_price`, `fees` (commission, reg, SEC on sells, CAT), `assignment_cost`. |
| `ccbot/data.py` | `PriceSeries` (+`scaled(k)`), `load_meta`, `realized_vol`, `load_prices` (each check raises `DataError` naming the row), `load_snapshots`, `SNAPSHOT_COLUMNS`. |
| `ccbot/synth.py` | Stdlib `random.Random(42)` two-regime GBM. `write_samples` writes SYNTH_A, SYNTH_B, SYNTH_SNAPSHOTS and their meta files. |
| `ccbot/expiries.py` | `business_days`, `extend`, `third_fridays`, `fridays` (both move to the prior trading day when Friday is missing), `pick_expiry(today, expiries, dte_range, slack)` (bisect), `scan_calendar`. |
| `ccbot/rules.py` | Shared by the backtest, SimBroker and the bot: `State`/`Short`/`Day`/`Quote`/`Decision`. Closed `REASONS`/`ACTIONS` lists, enforced in `Decision.__post_init__`. Also `Market` ABC, `model_quote`, `equity`, `settle_day` (dividend, ex-div early assignment, expiry/assignment), `apply_fill`, `decide_exit`, `decide_entry`. |
| `ccbot/backtest.py` | `build_days`, `ModelMarket`, `run_backtest` (daily loop with an invariant check each day), `buy_and_hold`, `metrics`, `Result`. |
| `ccbot/variants.py` | `Variant`, `REGISTRY` V0–V5, `expand` (V4 once per θ), `run_grid` (96 rows in registry order). |
| `ccbot/walkforward.py` | `yearly_returns`, `monthly_returns`, `folds` (asserts there is no overlap and no held-out year), `select`, `walk_forward`, `pbo_cscv`. |
| `ccbot/report.py` | `backtest_report`, `daily_report`, `weekly_report`. Plain tables, registry order. |
| `ccbot/screen.py` | `feasible_universe` (NO_QUOTES, PRICE_CAP, SINGLE_NAME_CAP, NO_EXPIRY, NO_STRIKE_IN_TOLERANCE, SPREAD, OI, EARNINGS), `universe_banner`. |
| `ccbot/bot.py` | `BrokerMarket`, `run_daily`, which is idempotent per (date, variant) and writes `state/paper_trades.csv`, `state/paper_snapshots.csv`, `state/scans/<date>.json` and the daily report, plus the weekly report on Fridays or with `--weekly`. Also `write_reports` and `regenerate`. |
| `ccbot/broker/__init__.py` | `make_broker` with lazy imports. Unknown names raise `ValueError`. |
| `ccbot/broker/base.py` | `Broker` ABC, `OptionOrder`, `OrderResult`, `validate` (LIMIT only, sell-to-open DAY only, GTC for BTC only, tick, NAKED_CALL, CSP_CASH, NO_POSITION_TO_CLOSE), `occ_symbol`/`parse_occ`, `chunk`, `LiveTradingDisabled`, `OrderRejected`, `NoQuote`. |
| `ccbot/broker/sim.py` | `SimBroker`: series (BS) or snapshot quotes. A limit fills at the limit when it crosses the bid or ask. DAY orders are cancelled the next day and GTC buy-to-close orders are re-checked. `advance` calls `rules.settle_day`. The JSON ledger is written atomically. |
| `ccbot/broker/webull_sandbox.py` | Sandbox-only, dry-run-default adapter. The SDK is imported lazily. Production hosts appear only in `_DENY`. The host is asserted before `TradeClient`/`DataClient` are built. The SDK's stdout/file loggers are suppressed and the token dir is forced to `state/webull_token`. Also `TokenBucket` (1 req/s), `to_sdk_payload`, and contract listing that falls back to OCC symbols. |
| `scripts/make_synthetic.py` | 3-line wrapper. |
| `data/sample/` (6 files, 124 KB) | `SYNTH_A.csv`/`.meta.json`, `SYNTH_B.csv`/`.meta.json`, `SYNTH_SNAPSHOTS.csv`/`.meta.json`. |
| `reports/backtest_SYNTH_A_2026-10-30.md`/`.csv` | Example report from the full 96-config run. |
| `tests/` (13 test files + `conftest.py` + `helpers.py`) | 87 tests. `conftest` blocks `socket.connect`, `connect_ex` and `getaddrinfo`. |

The demo scan's `state/` and `reports/daily_*`/`weekly_*` were deleted after the checks below (they are git-ignored), so the person's first scan starts from an empty paper ledger.

## Connectivity check
- [x] **Every new function/rule is used.** A grep found every `def`/`class` in `ccbot/` referenced from inside `ccbot/`. Two were removed for having no caller: `norm_pdf` (in the plan, never used) and `PriceSeries.head` (test-only, moved to `tests/conftest.py`). Every upper-case constant is referenced at least twice. `pyflakes ccbot tests scripts` is clean.
- [x] **Every input has a source and every output has a consumer.**
  - CSV, meta and snapshots come from the loaders. The config comes from `load_config`.
  - Backtest grid → report md/csv. Walk-forward → report.
  - Scan → `paper_trades.csv`, which feeds the idempotency check and the weekly report.
  - Snapshots → `paper_snapshots.csv`, kept for the deferred calibration step.
  - `scans/<date>.json` → the daily report and `report --date`.
  - Ledger → the next scan.
- [x] **Every branch ends in a defined result.**
  - Every no-trade is a `Decision("NONE", reason)` from the closed list. All 13 codes are produced, checked by `test_every_reason_code_is_produced`, `test_flat_keeps_premium` (EARNINGS_BLACKOUT) and `test_universe_empty_blocks_orders`, and the report has a "No-trade reasons" table.
  - Orders end FILLED, RESTING, CANCELLED, REJECTED (with a reason), DRY_RUN, SUBMITTED or SANDBOX_REJECTED.
  - Universe empty → banner + `UNIVERSE_EMPTY` row + 0 orders.
  - A missing quote for a held ticker → `DataError` → exit 2 (shown below).
  - A scan on an earlier date than the ledger → `ValueError` → exit 2.
  - A missing SDK → `ImportError` naming `ccbot[webull]`.
  - A non-sandbox host or env, or `--live` → exit 3.
  - Snapshot quotes missing bid, ask or delta are skipped, so that strike is never chosen.
- [x] **No leftover TODOs or unused files.** A grep for TODO/FIXME/XXX over `ccbot tests scripts README.md config` finds nothing. Docs reference only files that exist.

## Test output (pasted, not summarized)

`pip install pytest` → pytest 9.2.0 (already installed earlier this session).

```
$ python -m pytest -q
........................................................................ [ 82%]
...............                                                          [100%]
87 passed in 12.59s
```
Per file (`pytest --co`): test_backtest 8, test_broker 12, test_calendar 5, test_cli 5, test_costs 4, test_data 11, test_pricing 7, test_report 3, test_safety 5, test_screen_bot 6, test_variants 6, test_walkforward 4, test_webull_sandbox 11. The plan expected about 75. The difference is from parametrised cases.

```
$ python -m ccbot make-sample
data/sample/SYNTH_A.csv
data/sample/SYNTH_A.meta.json
data/sample/SYNTH_B.csv
data/sample/SYNTH_B.meta.json
data/sample/SYNTH_SNAPSHOTS.csv
data/sample/SYNTH_SNAPSHOTS.meta.json
data/sample/SYNTH_A.csv: OK          <- sha256sum -c against the pre-run checksums
data/sample/SYNTH_A.meta.json: OK
data/sample/SYNTH_B.csv: OK
data/sample/SYNTH_B.meta.json: OK
data/sample/SYNTH_SNAPSHOTS.csv: OK
data/sample/SYNTH_SNAPSHOTS.meta.json: OK
$ git diff --stat data/sample
124K	total                        <- (du; diff output empty)
```
Note: `data/sample/` is untracked until it is committed, so `git diff` is empty by construction. Determinism is shown by the checksums and by `test_samples_byte_identical`, which compares two fresh runs with each other and with the files on disk.

```
$ time python -m ccbot backtest --asof 2026-10-30
96 configs in 16.3 s -> reports/backtest_SYNTH_A_2026-10-30.md, reports/backtest_SYNTH_A_2026-10-30.csv

real	0m16.805s
```
(It was re-run once after a text-only edit, "Idle cash earns 0%": 96 configs in 16.7 s, identical numbers.)

**Backtest variant comparison**, copied from `reports/backtest_SYNTH_A_2026-10-30.md`. SYNTHETIC SYNTH_A, 2016-01-04 to 2025-08-29, 2,520 days, $3,000 start. The synthetic path ends at $195.76, which is far above $28 (seed 42 drew a strong uptrend).

Buy and hold:
| CAGR | Vol | Max DD | Sharpe |
|---|---|---|---|
| 21.22% | 31.54% | -44.34% | 0.5461 |

Base setting:
```
### spread $0.05, k 1.0
| Config | CAGR | Vol | Max DD | Sharpe | Fills | Premium | Spread paid | Fees | Excess vs B&H (CAGR) |
|---|---|---|---|---|---|---|---|---|---|
| V0 | 21.93% | 24.93% | -39.71% | 0.7191 | 69 | $9,139.00 | $174.47 | $7.12 | 0.71% |
| V1 | 12.63% | 18.80% | -27.76% | 0.4591 | 93 | $4,551.00 | $236.03 | $9.41 | -8.59% |
| V2 | 17.87% | 25.48% | -39.30% | 0.5442 | 129 | $6,664.00 | $323.30 | $13.06 | -3.35% |
| V3 | 22.08% | 25.11% | -38.00% | 0.72 | 67 | $8,965.00 | $168.11 | $6.91 | 0.86% |
| V4 θ50 | 21.12% | 26.38% | -41.86% | 0.649 | 55 | $7,125.00 | $138.76 | $5.67 | -0.10% |
| V4 θ66 | 21.87% | 27.06% | -39.22% | 0.6602 | 50 | $8,252.00 | $126.99 | $5.19 | 0.64% |
| V4 θ80 | 22.14% | 26.30% | -35.61% | 0.6898 | 51 | $8,562.00 | $127.25 | $5.30 | 0.92% |
| V5 | 11.52% | 16.57% | -28.25% | 0.4536 | 60 | $4,728.00 | $150.54 | $6.11 | -9.71% |
```
CAGR range across the 12 spread × k settings (from the CSV): V0 13.04–22.92%, V1 9.68–16.55%, V2 17.83–24.83%, V3 12.82–22.42%, V4θ50 13.02–22.15%, V4θ66 13.21–22.54%, V4θ80 13.22–22.61%, V5 6.87–20.27%.

Walk-forward and held-out (spread $0.05, k 1.0):
```
### Stitched out-of-sample
| Variant | OOS years | OOS CAGR | B&H OOS CAGR |
|---|---|---|---|
| V0 | 2019-2023 | 24.12% | 21.93% |
| V1 | 2019-2023 | 14.21% | 21.93% |
| V2 | 2019-2023 | 20.98% | 21.93% |
| V3 | 2019-2023 | 25.93% | 21.93% |
| V4 | 2019-2023 | 25.94% | 21.93% |
| V5 | 2019-2023 | 14.09% | 21.93% |

### Held-out years (2024, 2025), reported once
| Variant | Config | Held-out CAGR | B&H held-out CAGR | Excess |
|---|---|---|---|---|
| V0 | V0 | 46.75% | 49.57% | -2.82% |
| V1 | V1 | 17.16% | 49.57% | -32.41% |
| V2 | V2 | 21.61% | 49.57% | -27.96% |
| V3 | V3 | 42.32% | 49.57% | -7.25% |
| V4 | V4 θ80 | 41.65% | 49.57% | -7.92% |
| V5 | V5 | 8.44% | 49.57% | -41.13% |

## Overfitting check
- PBO (CSCV, S=8, monthly returns, held-out years excluded) across 96 configs: 0.357
- Configs tested: 96

No variant was selected for live use.
```
Walk-forward picked V4 θ = 80, 66, 66, 66, 66 in folds 2019–2023, and θ80 for the held-out run.

What I see in these numbers (MODELLED and SYNTHETIC, not evidence about markets):
- **Buy-and-hold has the higher return on this path.** Over the full period, V0, V3 and V4 θ66/θ80 are within ±1% of B&H CAGR at lower vol. In the held-out years every variant trails B&H.
- **V1 and V5 are the weakest.** They often sit in cash (`INSUFFICIENT_CASH` 760 and 613 days): after shares are called away in a rally, 100 shares no longer fit in the cash.
- **Results are very path-dependent.** V0 is 13.1% CAGR at k 0.8 and 22.2% at k 1.0 (spread $0.01), because a small pricing change moves assignment dates. Read single cells with care.
- **Wider spreads lower ending equity for V0 and V2** (tested). This is not strictly monotonic for every variant and k, for the same path-dependence reason.

Scan, report and refusal checks:
```
$ python -m ccbot scan --date 2026-10-30
2026-10-30 V0 BUY_SHARES OK SYNTH_A limit=24.1 status=FILLED
2026-10-30 V0 SELL_CALL OK SYNTH_A261218C00026000 limit=0.34 status=FILLED
reports in reports/ (daily_2026-10-30.md)
exit 0
$ python -m ccbot scan --date 2026-10-30        (2nd run, same date; after the "already scanned" message was added)
already scanned 2026-10-30 for V0: no new orders; reports re-rendered
2026-10-30 V0 BUY_SHARES OK SYNTH_A limit=24.1 status=FILLED
2026-10-30 V0 SELL_CALL OK SYNTH_A261218C00026000 limit=0.34 status=FILLED
reports in reports/ (daily_2026-10-30.md)
$ wc -l state/paper_trades.csv state/paper_snapshots.csv     (after both runs: header + 2 rows, not 4)
    3 state/paper_trades.csv
  128 state/paper_snapshots.csv
$ python -m ccbot report --date 2026-10-30 --weekly
reports/daily_2026-10-30.md
reports/weekly_2026-10-30.md
exit 0
$ python -m ccbot scan --date 2026-10-30 --live
refused: Live trading is not built.
exit 3
$ python -m ccbot scan --date 2026-10-30 --broker webull-sandbox     (WEBULL_ENV unset)
refused: WEBULL_ENV must be 'sandbox'; no other environment is supported.
exit 3
$ python -m ccbot scan --date 2026-11-02          (no snapshot for that date, position held)
error: cannot settle the paper ledger: no snapshot for SYNTH_A on 2026-11-02
exit 2
```
Daily report excerpt (`reports/daily_2026-10-30.md`, first run):
```
> **MODELLED with Black-Scholes from a volatility input — not market prices. Research, not financial advice.**
> **SYNTHETIC DATA — not a market history**
## Positions
- Ticker: SYNTH_A; shares 100; cost basis $24.10; cash $623.90; equity $2,997.97
- Open option: C 26.0 exp 2026-12-18 x1 sold at 0.34
## Screen
- Passing: SYNTH_A
- Rejected: SYNTH_B (SPREAD), SYNTH_C (PRICE_CAP)
## Today's decision
| BUY_SHARES | OK | SYNTH_A | 24.1 | DAY | n/a | None | None | FILLED | 24.1 |
| SELL_CALL | OK | SYNTH_A261218C00026000 | 0.34 | DAY | 0.258 | True | False | FILLED | 0.34 |
- Spread at the chosen strike: $0.03
- Days to earnings: n/a; days to ex-dividend: 49
```
Weekly report excerpt: `Paper P/L: $-2.03 (equity $2,997.97 vs start $3,000.00)`, `Fills: 2 (1 option fills); spread paid $1.50`, `Rule breaches (in_band False or order not filled): 0`.

```
$ git status --short   (excluding pre-existing work/ and logs/ changes)
 M README.md
?? .env.example  ?? .gitignore  ?? ccbot/... (19 modules)  ?? config/default.json  ?? data/sample/ (6)
?? pyproject.toml  ?? reports/backtest_SYNTH_A_2026-10-30.{md,csv}  ?? scripts/make_synthetic.py  ?? tests/ (15)
$ git status --short --ignored | grep '^!!'
!! .pytest_cache/  !! ccbot/__pycache__/  !! ccbot/broker/__pycache__/
!! reports/daily_2026-10-30.md  !! reports/weekly_2026-10-30.md  !! state/  !! tests/__pycache__/
$ git check-ignore -v state/sim_ledger.json reports/daily_2026-10-30.md .env conf/x webull_trade_sdk.log
.gitignore:2:state/  .gitignore:8:reports/daily_*.md  .gitignore:4:.env  .gitignore:3:conf/  .gitignore:6:webull_*_sdk.log
```
No `state/`, `conf/`, `.env` or `*.log` is tracked. `logs/research/2026-10-30.md` was already modified before I2 started and was not touched. Nothing was committed.

## Deviations from plan
All are small. None changes the goal or the safety rules.

1. **k scales the `iv` column too**, not only realised vol. Otherwise the k ∈ {0.8, 1.0, 1.2} sweep does nothing on SYNTH_A, which has an `iv` column.
2. **The monthly ±7-day slack rule applies to the backtest too**, not only the scan (config `monthly_slack_days`). The decision logic is shared, and the bot/backtest parity test needs one rule. The plan's "30–45 DTE is always found" is false: monthlies are 28 or 35 days apart, so strict 30–45 has a monthly on only 55% of SYNTH_A days, and even with slack ~4.8% of days (just before a 5-week gap) give `NO_EXPIRY`. The test now asserts > 94% coverage with slack and < 70% strict.
3. **Weekly 5–9 DTE has no expiry on Mondays and Tuesdays** (4/11 and 3/10 DTE). The test now asserts that Wed–Fri get one and Mon/Tue give `None` (→ `NO_EXPIRY`).
4. **V2 makes 1.9× V0's fills (129 vs 69), not 3–5×.** The causes are the Mon/Tue gap, `NO_STRIKE_IN_TOLERANCE` on 142 days (at 5–9 DTE, delta jumps more than 0.15 per $1 strike), and the cost-basis rule. The test bound is now 1.5–5×.
5. **New reason code `ASSIGNED_TODAY`.** It implements the plan's "re-buy at the next close" after an assignment. The closed reason/action lists are enforced in `Decision`.
6. **Interfaces.** `pick_strike(chain, target, tolerance)` takes (strike, delta) pairs, and `decide_entry`/`decide_exit` take a `market` object (expiries + chain) instead of `quote_fn`. This lets the backtest, screen and bot share them on model or snapshot quotes. `Broker` gained `advance(date)` and `buy_shares(...)`, which the bot needs for settlement and the buy-write. `norm_pdf` was not built (no caller).
7. **Test arithmetic fixes.** The SEC fee is 47 × 0.0000206 = 0.0009682 (the plan's 0.000968 ± 1e-9 was rounded). `strike_grid(30)` spans $21–39, so $1 steps are checked at ≥ $25 only.
8. **`SYNTH_SNAPSHOTS.meta.json` added** (6 sample files, not 5), so the snapshot file carries `synthetic: true`.
9. **Webull adapter.**
   - Positions and cash come from the local paper ledger (03: sandbox options support is UNVERIFIED). Dry-run leaves the ledger unchanged, and the bot logs `DRY_RUN` rows.
   - No fill is mirrored into SimBroker, and stock purchases are never sent (`buy_shares` returns `DRY_RUN`).
   - Underlying price uses `market_data.get_snapshot(..., "US_STOCK")`.
   - Response field names (`price`, `bid`, `ask`, `delta`, `open_interest`, `imp_vol`, `data`, `pagination_key`) are **UNVERIFIED**, taken from Webull's docs and the SDK source, not from a run.
   - `list_option_contracts` uses `start_date` for an exact expiry, per the SDK docstring ("start_date: Exact expiration date").
   - The SDK's logger flags `_stream_logger_set`/`_file_logger_set` are set directly, since that is how `TradeClient`/`DataClient` decide whether to add stdout and file logs (read from SDK 3.0.4).
10. **Screen.**
    - Added a `NO_QUOTES` reject for a universe ticker with no quotes.
    - The OI test is skipped for model quotes, which have no OI.
    - The cap uses account capital (cash + positions), not free cash. Otherwise holding 100 shares would fail `PRICE_CAP`.
11. **Secrets grep test** checks line by line and skips `work/` and `logs/`, because agent docs quote `WEBULL_APP_SECRET=` in prose.
12. **CLI extras needed for offline tests:** `--state-dir`, `--out`, `--config` and `--variant` on `scan`/`report`, and `--out` on `backtest`.
13. **Known limits (stated, not hidden):**
    - Share trades carry no fees, and idle cash earns 0% (both printed in the report).
    - Synthetic prices do not drop on ex-dividend dates.
    - Snapshot mode cannot run the ex-div early-assignment check (snapshots carry the date, not the amount).
    - The weekly report's B&H excludes dividends.
    - In the bot, V3's pending target expiry is not persisted between scans, so it shows `NOT_UP_DAY` where the backtest would show `WINDOW_CLOSED_ROLL`. Both are no-trade.
    - `INSUFFICIENT_CASH` at the start makes the backtest wait each day rather than stop.

## Revision (after I3 FAIL) - 2026-10-30
Prepared by I2 from the 04 revision of the same date. Research only. Nothing connected to a brokerage and no order was placed. Nothing committed.

### Changes
| File | Change |
|---|---|
| `ccbot/data.py` | `realized_vol` drops the `fillna` backfill. `vol[t]` uses the `rv_window` log returns ending at t, and is NaN for t < `rv_window`. |
| `ccbot/rules.py` | New closed-list reason `VOL_WARMUP`, and a `Day.vol_warmup` field (default False). `_option_entry` returns `NONE/VOL_WARMUP` first when it is set, before any option is priced (calls and wheel puts, every variant). |
| `ccbot/backtest.py` | `build_days` sets `vol_warmup = isnan(vol)`. SimBroker on a series reuses `build_days`, so the bot and the backtest share the rule. Snapshot and broker Days keep the default False. |
| `ccbot/report.py`, `README.md` | Wording (06 item 2): k multiplies the `iv` column when there is one, else trailing realised vol. The README also says the vol is past-only, and that the first 20 rows of a no-`iv` CSV give `VOL_WARMUP`. |
| `tests/test_data.py` | The old `iloc[0] == iloc[5]` assertion, which checked the backfill, is replaced: warm-up is NaN and the rest is finite. **New guardrail** `test_realized_vol_uses_only_past_closes`: a CSV with no `iv` column (asserted), 60 days, volatile then calm, k = 1.2, default `rv_window`. For every t it rewrites all closes after t, then checks that `vol[0..t]` is unchanged (exact or both NaN) and that the edit did change a later vol. |
| `tests/test_backtest.py` | New `test_no_option_sold_during_vol_warmup`: on a no-`iv` CSV, V0 and V5 sell no option before row `rv_window`, do sell one later, and count ≥ `rv_window`−1 `VOL_WARMUP` days. |
| `tests/test_variants.py` | `VOL_WARMUP` is added to the codes tested outside SYNTH_A (SYNTH_A has an `iv` column). **V2 fills test (06 deviation 4):** the fitted 1.5× lower bound is removed. The test now checks the rules directly: V0 < V2 fills < 5×V0 (5× is the plan's ceiling), every V2 sale is on a distinct weekly expiry at 5–9 DTE, and every V2 sale is on Wed–Fri. A code comment gives the reason there is no ratio band: Mon/Tue have no 5–9 DTE expiry, and short-dated delta skips the tolerance between strikes. |

Connectivity: `VOL_WARMUP` is produced in `rules._option_entry`, its input comes from `build_days`, it is counted in `Result.reasons`, and it shows in the report's reason table. It is tested in `test_backtest`. No TODOs were added.

**Mutation check of the guardrail:** I temporarily put the old `fillna(rv[first_valid])` line back. `test_realized_vol_uses_only_past_closes`, `test_no_option_sold_during_vol_warmup` and `test_realized_vol_of_constant_return_is_zero` all failed (3 failed, 18 passed). I then restored the fix (`grep -c fillna ccbot/data.py` → 0).

### Real output
```
$ python -m pytest -q
89 passed in 13.41s

$ python -m ccbot make-sample            # exit 0, 6 files (data/sample is untracked; test_data checks byte-identity)
$ time python -m ccbot backtest --asof 2026-10-30
96 configs in 17.0 s -> reports/backtest_SYNTH_A_2026-10-30.md, reports/backtest_SYNTH_A_2026-10-30.csv
$ diff <previous>.csv reports/backtest_SYNTH_A_2026-10-30.csv     # identical
$ diff <previous>.md  reports/backtest_SYNTH_A_2026-10-30.md
16c16
< - Volatility multiplier k = 1.0: k UNCALIBRATED (no real option snapshots yet).
---
> - Volatility multiplier k = 1.0: multiplies the vol input (the `iv` column when present, else trailing realised vol). k UNCALIBRATED (no real option snapshots yet).

$ python -m ccbot scan --date 2026-10-30 --broker sim --snapshots data/sample/SYNTH_SNAPSHOTS.csv --state-dir <tmp> --out <tmp>
2026-10-30 V0 BUY_SHARES OK SYNTH_A limit=24.1 status=FILLED
2026-10-30 V0 SELL_CALL OK SYNTH_A261218C00026000 limit=0.34 status=FILLED
exit 0   (daily_2026-10-30.md + weekly_2026-10-30.md)
$ python -m ccbot scan --date 2026-10-30 --live
refused: Live trading is not built.            exit 3
$ python -m ccbot scan --date 2026-10-30 --broker webull-sandbox   (no env vars)
refused: WEBULL_ENV must be 'sandbox'; no other environment is supported.   exit 3
$ python -m ccbot backtest --data nope.csv --quick
error: cannot read nope.csv: [Errno 2] No such file or directory: 'nope.csv'   exit 2

I3's look-ahead reproduction, re-run (80-row CSV, no iv, days 1–20 volatile then calm):
vol day0 = nan  vol day20 = 0.778
first option sale: 2026-02-02 (row 20, the first valid-vol day) K=30.0 @ 0.95   VOL_WARMUP days: 20
$ python -m ccbot backtest --data lookahead.csv --quick --asof 2026-10-30
8 configs in 0.1 s -> ...   exit 0   (reason table shows VOL_WARMUP 20)
```
**The headline backtest numbers are unchanged.** SYNTH_A has an `iv` column, so the CSV is byte-identical and the only change in the md is the k wording line. The 05 tables above still stand.

Note (existing behaviour, not changed): a 1-year user CSV has no walk-forward fold, so numpy prints "Mean of empty slice" RuntimeWarnings from `walkforward.py:98-99` during `--quick`. The run still exits 0. Left for I3/Audit to judge. It is outside this fix.

## Revision 2 (after I3 re-verification FAIL) - 2026-10-30
Prepared by I2 from 04 "Revision 2". Nothing connected to a brokerage, no order placed, nothing committed.

### Changes
| File | Change |
|---|---|
| `ccbot/walkforward.py` | `pbo_cscv` returns NaN when T < S, N < 2 or R has a non-finite value. It returns before any mean is taken, so the warning is avoided rather than filtered. `walk_forward` returns `pbo_months`. With no non-held-out years, the held-out config is `"not selected (no train years)"` and its held-out CAGR is NaN, not the tie-break winner. |
| `ccbot/report.py` | The PBO line prints `n/a (needs >= 8 non-held-out months and >= 2 configs; have T months)` when PBO is NaN. |
| `tests/test_walkforward.py` | `test_pbo_undefined_on_too_few_months[T=0,1,7]`: NaN for T×8 noise, and NaN for a 24×1 matrix. |
| `tests/test_cli.py` | `test_short_csv_reports_pbo_na_without_warnings`: a 1-year no-`iv` CSV through `main(["backtest", "--quick", ...])` with RuntimeWarning set to error. It exits 0, the PBO line has the n/a reason and no `0.000`, the report has "not selected (no train years)", and no RuntimeWarning is recorded. |

**Mutation check:** with the new guard disabled (`if False:`), 4 tests fail (the CLI test with a RuntimeWarning, and the 3 PBO cases). The guard was restored (`grep -c "if T < S"` → 1).

**Grep for other places that turn NaN, or no data, into a number** (`fillna`, `nan_to_num`, `or 0`, `.get(.., 0)`, `np.mean`, `.mean()`, `.sum()`, `int(`, empty `compound`):
- No `fillna`, `nan_to_num` or `or 0` is left in `ccbot/`.
- `metrics`: CAGR, vol and Sharpe are already NaN on empty, single-row or zero-vol input. `premium`, `spread_paid` and `fees_paid` give 0.0 only when there are no fills, which is a true zero.
- `walk_forward`: the stitched OOS and B&H CAGR use `compound([]) = 0` with `n_days = 0`, and `annualise` gives NaN, so they show `n/a`. The held-out excess is NaN when either side is NaN.
- `backtest.reasons.get(.., 0)` is a counter, and the weekly `spread_paid` 0.0 means no option fills.
- V4 `vol_pct` NaN → `IV_FILTER` (documented).
- Nothing else found. One related item is not NaN-to-number and is unchanged: the `max(1, …)` lots in `buy_and_hold` and the weekly B&H line. I3 already recorded it as a note for later.

### Real output
```
$ python -m pytest -q
93 passed in 14.82s
$ python -m ccbot backtest --asof 2026-10-30
96 configs in 18.3 s -> reports/backtest_SYNTH_A_2026-10-30.md, reports/backtest_SYNTH_A_2026-10-30.csv
diff vs previous: CSV-IDENTICAL, MD-IDENTICAL
- PBO (CSCV, S=8, monthly returns, held-out years excluded) across 96 configs: 0.357
$ python -W error::RuntimeWarning -m ccbot backtest --data SHORT1Y.csv --quick --asof 2026-10-30 --out <tmp>
8 configs in 0.1 s -> .../backtest_SHORT1Y_2026-10-30.md, ...csv        exit 0  (no warning)
- PBO (CSCV, S=8, monthly returns, held-out years excluded) across 8 configs: n/a (needs >= 8 non-held-out months and >= 2 configs; have 0 months)
| V0 | not selected (no train years) | n/a | -1.94% | n/a |
$ python -W error::RuntimeWarning -m ccbot backtest --data lookahead.csv --quick ...   -> 8 configs in 0.1 s (no warning)
$ python -m ccbot make-sample --out <tmp>/sample   exit 0; all 6 files byte-identical to data/sample/
$ python -m ccbot scan --date 2026-10-30 --broker sim --snapshots data/sample/SYNTH_SNAPSHOTS.csv --state-dir <tmp> --out <tmp>
2026-10-30 V0 BUY_SHARES OK SYNTH_A limit=24.1 status=FILLED
2026-10-30 V0 SELL_CALL OK SYNTH_A261218C00026000 limit=0.34 status=FILLED      exit 0
$ python -m ccbot scan --date 2026-10-30 --live                 -> refused: Live trading is not built.   exit 3
$ python -m ccbot scan ... --broker webull-sandbox (WEBULL_ENV unset) -> refused: WEBULL_ENV must be 'sandbox'; no other environment is supported.   exit 3
$ python -m ccbot backtest --data /nonexistent.csv --quick      -> error: cannot read /nonexistent.csv ...   exit 2
```
The headline backtest numbers are unchanged (SYNTH_A has 96 non-held-out months).
