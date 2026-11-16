# Work item 067
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-16

## What we want
When an item changes the real-quote backtest's decision path (ccbot/realtest.py), its build report and verification show the effect on every published output, not only the keys the builder picked. Then report 065's missing effects.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- logs/audit/2026-11-15-065.md, Findings "Reporting gap": 065/05, 065/06 and 065/07 report only `counts_bot_rule_bid` and `bxm_vs_spy`. A1's full before/after diff of summary.json shows that other sections also change:
  - `walkforward_picks`: 2 of 10 windows change (2024-07-06 `d0.150_dte30-45_E_roll_bid` -> `d0.450_dte30-45_noE_take50_bid`; 2026-07-06 `d0.200_dte14-24_noE_take50_bid` -> `d0.200_dte14-24_noE_hold_bid`).
  - `walkforward_by_ticker` excess_cagr changes for 11 of 17 tickers; tickers with positive excess go 6 -> 5.
  - `monte_carlo_2_stocks_1yr` cc_ret median 0.0689 -> 0.0686.
- 065/07: "Whether to commit regenerated reports/real/ is the person's call." The person cannot make that call from a partial effect list.
- Found in the 2026-11-16 daily review (logs/audit/2026-11-16.md) from A1's per-item audit of 065 on PR #29.

## Root cause and prevention guardrail (BUG only)
Root cause: the before/after comparison is written by hand, so the builder lists the keys they expect to move. Nothing compares the whole output, and no template field asks for it.
Guardrail (proposed): a small script (e.g. `scripts/diff_reports.py <before_dir> <after_dir>`) that walks every key of summary.json recursively and every CSV in reports/real/, and prints each changed value (or `no change`). Add a field to templates/build-report.md and templates/verification.md: "Real-data effect (diff_reports output, pasted)" required when ccbot/realtest.py's decision path changes. A test with two small report fixtures that differ in a nested key fails if the script skips nested keys.

## Recurring issue link (RI-#, if any)
RI-013 (new): effect of a change reported from hand-picked fields, not the whole output. Related to RI-006 (hand-counted totals).

## Done looks like
The diff script and its test exist; build-report/verification templates have the field; the person gets 065's full effect list (walk-forward, by-ticker, Monte Carlo) in the PR. Suite green.
