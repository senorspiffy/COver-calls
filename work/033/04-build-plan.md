# 04 Build plan - 033
Fit verdict: FIT
Fits a ~$3k account: no trading, no new costs, no brokerage connection.
## Extra research (with sources)
None needed; inputs are repo files.
## Files to create/change
scripts/check_pipeline.py; tests/test_pipeline_check.py; .claude/agents/a1-auditor.md; README.md; work/023–030/07-audit-task.md
## Tests and checks
pytest tests/test_pipeline_check.py; check_pipeline on the repo
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | `awaiting A1` status + AWAITING A1 line for items dated ≥ 2026-10-31 whose 07 lacks `A1 result:` |
| Map 2 | a1 job A appends the line; daily mode audits AWAITING items |
| Map 3 | A1 result lines for 023–030 |
## Guardrail tests
- Audit recorded: `test_complete_needs_a1_result`
## Expected result
Every map step applied; full suite passes; `check_pipeline.py` → SKIPPED: none.
