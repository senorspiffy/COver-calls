# 04 Build plan - 026
Fit verdict: FIT
Fits a ~$3k account: no trading, no new costs, no brokerage connection.
## Extra research (with sources)
None needed; inputs are repo files.
## Files to create/change
scripts/check_pipeline.py; tests/test_pipeline_check.py; tests/test_portfolio.py; .claude/commands/run-item.md, daily-audit.md; .claude/agents/a1-auditor.md, i3-verifier.md; templates/request.md; README.md; work/023/*, work/024/*
## Tests and checks
`pytest tests/test_pipeline_check.py tests/test_portfolio.py`; `python3 scripts/check_pipeline.py`
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | check_pipeline.py + 6 fixture tests + repo test |
| Map 2 | instruction edits |
| Map 3 | 023/024 files |
| Map 4 | 2 tests |
## Guardrail tests
- Repo test `test_repo_pipeline_has_no_skipped_items` fails while any item is SKIPPED
## Expected result
Every map step applied; full suite passes.
