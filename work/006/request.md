# Work item 006
Type: BUG
Opened by: A1
Date: 2026-10-30
Against: 002 code (`ccbot/backtest.py::buy_and_hold` L121, `ccbot/report.py` weekly B&H L168). First noted by I3 (06, "Notes for later"); left unfixed in 05 Revision 2.

## What we want
The buy-and-hold benchmark must never borrow. If 100 shares cost more than cash − buffer, show B&H as n/a (with the reason), or start it on the strategy's first buy.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `shares = max(1, floor((cash − buffer) / (s0·100))) · 100`. A1 test: the first 600 rows of SYNTH_A × 1.5 (start $36). B&H buys 100 sh = $3,600 on $3,000, so cash = **−$600**. B&H vol 50.44%, MDD −54.77% (leveraged). The strategy waits instead (`INSUFFICIENT_CASH 92`), and the report prints V0 "Excess vs B&H" **+5.12%** against that margin benchmark.
- The weekly report uses the same `max(1, …)` (report.py L168).

## Root cause and prevention guardrail (BUG only)
Root cause: when the benchmark cannot be formed (cash too small), a default (1 lot) is used instead of n/a. This is the "defaulted into a number" case of the Revision 2 standing rule. I2 judged it "not NaN-to-number" and skipped it.
Guardrail: a test that B&H cash is ≥ 0 on every day for an input where 100 sh > cash − buffer, and that the report prints `n/a (100 shares cost more than cash − buffer)`. Add `max(1,` and `min(1,` to the review grep list.

## Recurring issue link (RI-#, if any)
RI-002, occurrence 4.

## Done looks like
No benchmark path has negative cash. Excess vs B&H is n/a or computed against a feasible benchmark, and the test is in the suite.
