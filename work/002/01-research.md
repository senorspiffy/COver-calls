# 01 Research brief - 002
## Question
Do the account-size thresholds in 001 step 1 / 9(a) match step 1's own check `(price × 100 × positions) ≤ cash − $200`?
## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- Step 1 check formula is `(price × 100 × positions) ≤ cash − $200` [work/001/03-handoff.md, map step 1, last column]
- Step 1 text said two ≤ $28 or one ≤ $55 at $5,000–6,000, output '2 at ≥ $5.6k' [work/001/03-handoff.md, original text on main 0ca80e8]
- R1 N1 thresholds ($6,000/2 = $30 etc.) have no buffer [work/001/01-research.md N1]

Internal item: every source is a file in this repo (no web sources needed). Read `logs/recurring-issues.md` first (RI-001).
## Numbers used (show the math)
Two at $28: 2 × 2,800 + 200 = $5,800. One at $55: 5,500 + 200 = $5,700. At $5,600: (5,600 − 200)/200 = $27, /100 = $54. At $5,000: 4,800/200 = $24, /100 = $48.
## Fit for a ~$3k account
Process/rule-text fix; no trades, no new costs.
## Open questions
None.
