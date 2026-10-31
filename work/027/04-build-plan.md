# 04 Build plan - 027
Fit verdict: FIT
Fits a ~$3k account: no trading, no new costs, no brokerage connection.
## Extra research (with sources)
None needed; inputs are repo files and PEP 701 (https://peps.python.org/pep-0701/).
## Files to create/change
scripts/check_handoff.py; tests/test_safety.py; .claude/agents/i3-verifier.md
## Tests and checks
`pytest tests/test_safety.py`; `python3.11 scripts/check_handoff.py 001`
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | L49 split |
| Map 2 | 2 tests |
| Map 3 | i3 line |
## Guardrail tests
- `test_fstrings_parse_on_python_310` fails on the old line
## Expected result
Every map step applied; full suite passes.
