# 04 Build plan - 032
Fit verdict: FIT
Fits a ~$3k account: no trading, no new costs, no brokerage connection.
## Extra research (with sources)
None needed; inputs are repo files.
## Files to create/change
tests/test_safety.py; .claude/agents/i3-verifier.md
## Tests and checks
pytest tests/test_safety.py; mutation `type X = int` in scripts/check_pipeline.py
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | test_every_py_compiles_on_oldest_python (skip with reason if no 3.10/3.11) |
| Map 2 | i3 step 2 points at the test |
## Guardrail tests
- Oldest Python: `test_every_py_compiles_on_oldest_python`
## Expected result
Every map step applied; full suite passes; `check_pipeline.py` → SKIPPED: none.
