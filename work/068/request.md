# Work item 068
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-16

## What we want
Fewer full real-quote backtest runs per item, and one warning per data hole instead of two.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- logs/audit/2026-11-15-065.md, Findings "Efficiency": one `python3 -m ccbot.realtest` run takes about 11 min, and item 065 ran it six times (I2 x2, I3 x2, A1 x2). `ccbot/realtest.py` already has `--tickers` (L860).
- Same file: MDLZ carries two warnings for one gap: the `load_ticker` count ("earnings: N gap(s) > 120 days between dates", ccbot/realtest.py L189-191) and simulate's named interior-gap list. They say the same thing twice.

## Done looks like
run-item.md / the I2 and I3 agent text say: iterate with `--tickers <affected names>` before/after, then run the full backtest once per step that publishes numbers (portfolio sections such as walk-forward and Monte Carlo need the full run; item 067's diff covers them). The duplicate gap warning is merged into one line that names the gap dates. Suite green; the real-data summary numbers do not change.
