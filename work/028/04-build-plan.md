# 04 Build plan - 028
Fit verdict: FIT
Fits a ~$3k account: no trading, no new costs, no brokerage connection.
## Extra research (with sources)
None needed; inputs are repo files.
## Files to create/change
scripts/check_handoff.py; tests/test_pipeline_check.py; .claude/agents/a1-auditor.md; README.md
## Tests and checks
`python3 scripts/check_handoff.py --all`; test_check_handoff_all_legacy_and_fail
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | --all + LEGACY |
| Map 2 | a1, README |
## Guardrail tests
- n/a (EFFICIENCY; no filter rule or optional input)
## Expected result
Every map step applied; full suite passes.
