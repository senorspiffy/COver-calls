# 04 Build plan - 037
Fit verdict: FIT
Fits a ~$3k account: no trading, no new costs, no brokerage connection.
## Extra research (with sources)
None needed; inputs are repo files and git.
## Files to create/change
scripts/check_pipeline.py; tests/test_pipeline_check.py; .claude/agents/a1-auditor.md; README.md; templates/request.md
## Tests and checks
pytest tests/test_pipeline_check.py; full suite; `python3 scripts/check_pipeline.py` on the repo; mutation in a scratch copy
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | `ID CLASH:` line: both sides added request.md since merge base, texts differ |
| Map 2 | `--next-id` over HEAD and every unmerged remote branch |
| Map 3 | a1-auditor, README, templates/request.md: take IDs from --next-id; ID CLASH at top of report |
## Guardrail tests
- test_same_id_on_main_and_open_branch_is_a_clash; test_next_id_counts_open_branches
## Expected result
Every map step applied; full suite passes; `check_pipeline.py` → SKIPPED: none.
