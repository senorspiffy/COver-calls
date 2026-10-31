# Covered-call agent teams

Three teams of Claude Code agents that research, build, and audit your covered-call strategy and tools, with every hand-off written to a file so nothing is lost or made up.

## The flow

```
 You or A1 open a work item (work/<ID>/request.md)
        |
 RESEARCH   R1 Researcher -> R2 Improver -> R3 Fact Checker
        |                                  (writes the implementation map)
 IMPLEMENT  I1 Reviewer -> I2 Builder -> I3 Verifier
        |                                  (audits I1 + I2, sends audit task)
 AUDIT      A1 Auditor: per-item review + daily review of all logs
        |
        +--> bugs/errors       -> new BUG item + prevention guardrail -> back to R1
        |                         and logged in logs/recurring-issues.md
        +--> small improvements -> new EFFICIENCY item -> back to R1
```

| Agent | Job | Writes |
|---|---|---|
| R1 Researcher | Sourced research on the topic | `01-research.md` |
| R2 Improver | Past logs + 3 for, 3 against, pitfalls, searching English, Mandarin, Spanish, Japanese + 3 rotating spoken languages | `02-improvements.md` |
| R3 Fact Checker | Checks every claim and number, removes anything unsupported, maps the build | `03-handoff.md` |
| I1 Reviewer | Fit check for a ~$3k account, a bit more research, build plan | `04-build-plan.md` |
| I2 Builder | Builds it; checks every path leads somewhere | `05-build-report.md` |
| I3 Verifier | Audits I1 and I2, re-runs tests, sends audit task | `06-verification.md`, `07-audit-task.md` |
| A1 Auditor | Per-item audit; daily log review; sends bugs and efficiency ideas to Research | `logs/audit/`, `logs/efficiency/` |

## Layout

- `.claude/agents/` - the seven agent definitions
- `.claude/commands/run-item.md` - `/run-item <ID>` runs one item through all seven steps
- `.claude/commands/daily-audit.md` - `/daily-audit` runs the daily review
- `templates/` - the hand-off format for each step
- `scripts/check_handoff.py` - `python3 scripts/check_handoff.py <ID>` checks a hand-off's counts and self-check (run by R3, I3, A1); `--all` checks every item (A1)
- `scripts/check_pipeline.py` - lists each work item's missing steps for its Scope; SKIPPED exits 1, STUCK items are listed (run by A1 daily, I3 per item)
- `work/<ID>/` - every file for one item, numbered 01 to 07
- `logs/<team>/<date>.md` - one line per agent action, read by R2 and A1

## Safety rules built in

- No made-up facts: unsourced claims are marked UNVERIFIED and R3 strips them before build.
- No live trading: I2 uses sample or paper data only unless you say otherwise.
- Every error found goes back with a guardrail so it can't reappear. Repeats are tracked in `logs/recurring-issues.md`, and anything seen 3+ times is escalated to you.
- Loops stop after 3 send-backs on the same step and come to you.

## How to use

1. Put this folder in a GitHub repo and open it in Claude Code.
2. Create `work/001/request.md` from `templates/request.md`, e.g. "Build a strike picker for 30-45 day calls around 0.30 delta on stocks under $30".
3. Run `/run-item 001`.
4. Run `/daily-audit` once a day, or schedule it.

## Covered-call backtester and paper bot (ccbot)

Built in work item 002. Research, not financial advice. **Live trading is not built and needs the person's explicit go-ahead.**

### Install and test

```
pip install -e .[dev]            # numpy, pandas, pytest
python -m ccbot make-sample      # regenerate data/sample/ (deterministic; git diff stays empty)
python -m pytest -q              # all tests run offline (sockets are blocked)
```

### Commands

| Command | Writes |
|---|---|
| `python -m ccbot backtest --asof 2026-10-30` (add `--quick` for the base spread/k only) | `reports/backtest_SYNTH_A_2026-10-30.md` and `.csv` |
| `python -m ccbot scan --date 2026-10-30` (defaults: `--broker sim`, `--snapshots data/sample/SYNTH_SNAPSHOTS.csv`, `--variant V0`) | `reports/daily_<date>.md`, `reports/weekly_<date>.md` on Fridays or with `--weekly`, `state/paper_trades.csv`, `state/paper_snapshots.csv`, `state/sim_ledger.json` |
| `python -m ccbot report --date 2026-10-30 [--weekly]` | rebuilds the daily/weekly report from `state/` |

Exit codes: 0 ok, 2 bad input, 3 refused (live trading or a non-sandbox Webull setting).

**Two positions (item 024).** The scan holds up to `max_positions` (default 2) different underlyings that share one cash balance. Each day it manages open positions first, then opens new ones from the passing tickers in `universe` order. A single stock may use at most `max_single_name_frac` (50%) of capital, an ETF may use all the cash, and `cash_buffer` ($200) always stays back. Ledgers saved before item 024 load unchanged.

The backtest runs six pre-registered variants (V0 baseline monthly, V1 50% buy-back, V2 weekly, V3 after an up day, V4 IV-percentile filter with θ chosen walk-forward, V5 wheel) across spread × k sweeps, then a walk-forward with the last two years held out, and a PBO overfitting check. Rows are always in registry order.

### Use your own data

Put a CSV with `date,close[,iv][,dividend][,earnings]` (ISO dates ascending, `iv` annualised decimal, `dividend` = $ on the ex-date, `earnings` = 1 on report dates) anywhere and run `python -m ccbot backtest --data path/to/TICKER.csv`. An optional `TICKER.meta.json` sidecar holds `{"ticker","source","synthetic","asset_type","notes"}`; without it the file counts as user-supplied, non-synthetic, `asset_type "stock"`. The vol input is the `iv` column × k when there is one; without it, it is the trailing 20-day realised vol × k, built only from closes up to that day. k scales both. Without an `iv` column the first 20 rows have no vol yet, so no option is sold on them (reason `VOL_WARMUP`). Shares can still be bought.

### What the labels mean

- **MODELLED**: option prices come from Black-Scholes on a volatility input, not market quotes. The multiplier k is UNCALIBRATED until real snapshots exist (the bot logs every quote it reads to `state/paper_snapshots.csv` for that).
- **SYNTHETIC DATA**: the input is generated (`SYNTH_*` files), not a market history. Results from it say nothing about real markets.

### Safety rules

- No live trading. `--live` exits 3.
- The Webull adapter (`--broker webull-sandbox`, `pip install -e .[webull]`) is sandbox-only and dry-run by default: it checks the SDK resolves the sandbox host before it builds any client, refuses unless `WEBULL_ENV=sandbox`, and only validates (optionally previews) orders. Positions and cash stay in the local paper ledger.
- Credentials come only from environment variables (see `.env.example`); `.env`, `state/` and tokens are git-ignored. Whether the sandbox accepts options orders is UNVERIFIED: that smoke test runs on your own machine.
