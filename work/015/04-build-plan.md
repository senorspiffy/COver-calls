# 04 Build plan - 015
Fit verdict: FIT
Fits a ~$3k account: no trading, no new costs, no brokerage connection.
## Extra research (with sources)
None needed; inputs are repo files.
## Files to create/change
.claude/agents/r3-fact-checker.md; .claude/agents/i3-verifier.md
## Tests and checks
grep '^1b' r3; grep 'scratch copy' i3
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | r3 |
| Map 2 | i3 |
## Guardrail tests
- n/a (EFFICIENCY; no filter rule or optional input)
## Expected result
Every map step applied; full suite passes.
