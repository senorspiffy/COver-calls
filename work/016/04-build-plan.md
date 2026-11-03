# 04 Build plan - 016
Fit verdict: FIT
Fits a ~$3k account: no trading, no new costs, no brokerage connection.
## Extra research (with sources)
None needed; inputs are repo files.
## Files to create/change
ccbot/report.py; tests/test_report.py; work/001/03-handoff.md
## Tests and checks
two report tests; `grep -c 'items 003, 004, 005, 008' work/001/03-handoff.md` → 2
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | report |
| Map 2 | 001 |
## Guardrail tests
- n/a (EFFICIENCY; no filter rule or optional input)
## Expected result
Every map step applied; full suite passes.
