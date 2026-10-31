# 04 Build plan - 025
Fit verdict: FIT
Fits a ~$3k account: no trading, no new costs, no brokerage connection.
## Extra research (with sources)
None needed; inputs are repo files.
## Files to create/change
work/023/screen-summary.md; work/001/03-handoff.md; .claude/agents/r1-researcher.md; .claude/agents/r3-fact-checker.md
## Tests and checks
`pytest tests/test_missing_inputs.py -k next_earnings`; grep both agent files; grep EARNINGS_UNKNOWN in 023 summary and 001
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | 023 Correction + 001 note |
| Map 2 | r1 3a, r3 3a |
| Map 3 | existing test, re-run |
## Guardrail tests
- Missing inputs: next_earnings → `test_drop_each_input[snapshot.next_earnings]` (exists)
## Expected result
Every map step applied; full suite passes.
