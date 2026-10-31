# 01 Research brief - 018
## Question
Does the 50% exit example obey the 50% rule, and can the rule be entered as an order?
## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- Rule: exit if worth ≤ 50% of sale price, GTC limit at 50% [work/001/03-handoff.md, step 6]
- Example sold at $0.47, filled at $0.24 [work/001/03-handoff.md, worked example, main 0ca80e8]
- Example timing 'day ≤ 12 of 35' as 'first third' [work/001/03-handoff.md, step 6] (found by R3 while checking: 35/3 = 11.7)

Internal item: every source is a file in this repo (no web sources needed). Read `logs/recurring-issues.md` first (RI-005).
## Numbers used (show the math)
0.50 × 0.47 = 0.235; 0.24/0.47 = 51.1% > 50%. Round down: $0.23 = 48.9%. Profit (0.47 − 0.23) × 100 − 0.20 = $23.80. 35/3 = 11.7 → last day in first third is day 11.
## Fit for a ~$3k account
Process/rule-text fix; no trades, no new costs.
## Open questions
None.
