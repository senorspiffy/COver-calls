# Work item 024
Type: IDEA
Scope: FULL
Waived: 01 02 03 04 (A1, 2026-10-31, item 026: built and merged before the step check existed; the rule is the person's own decision in 001; I3 ran afterwards in 026)
Opened by: person (via 023 thread)
Date: 2026-10-31
## What we want
Let the paper bot hold and manage up to two different single stocks at once, per the person's 2026-10-31 decision (001 Correction, Step 1 and 9(a)). Today `bot.py` keeps one `state.ticker` and picks `passing[0]`.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
n/a
## Root cause and prevention guardrail (BUG only)
n/a
## Recurring issue link (RI-#, if any)
RI-001: compute how often two names pass together before relying on it.
## Done looks like
Scan opens/holds up to two positions in different tickers, each <= max_single_name_frac x capital, total <= cash - cash_buffer; per-position calls, rolls and assignment; reports show both; tests cover the caps and a one-passing-ticker day.
