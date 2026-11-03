# 04 Build plan - 013
Fit verdict: FIT
Fits a ~$3k account: no trading, no new costs, no brokerage connection.
## Extra research (with sources)
None needed; inputs are repo files.
## Files to create/change
.claude/agents/r3-fact-checker.md, i1-reviewer.md, i2-builder.md, i3-verifier.md; logs/recurring-issues.md
## Tests and checks
grep -l recurring-issues .claude/agents/*.md → 7 files (a1, r1, r2 + the 4 new)
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | 4 files + header |
## Guardrail tests
- n/a (EFFICIENCY; no filter rule or optional input)
## Expected result
Every map step applied; full suite passes.
