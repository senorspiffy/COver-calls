# 01 Research brief - 019
## Question
Do the fact-check totals and log line match the table, and how do we stop count drift?
## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- `grep -c "^| R\|^| NEW" work/001/03-handoff.md` = 77 rows
- Totals line said 76 → 60/12/4 [work/001/03-handoff.md, main 0ca80e8]
- Removed list has 7 entries vs '4 removed'

Internal item: every source is a file in this repo (no web sources needed). Read `logs/recurring-issues.md` first (RI-006).
## Numbers used (show the math)
77 − 12 fixed − 4 removed = 61 as-is. 61 + 12 + 4 = 77.
## Fit for a ~$3k account
Process/rule-text fix; no trades, no new costs.
## Open questions
None.
