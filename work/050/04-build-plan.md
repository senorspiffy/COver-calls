# 04 Build plan - 050
Fit verdict: FIT
Process only. Built on 049's commit on the same branch (both change scripts/check_pipeline.py).
## Extra research (with sources)
None beyond 01.
## Files to create/change
1. scripts/check_pipeline.py (LOG_HINT; incomplete and write_log messages)
2. tests/test_pipeline_check.py (2 tests)
## Tests and checks
Full suite; `check_pipeline.py` exit 0; `check_handoff.py 050`.
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | file 1 `LOG_HINT`; test `test_log_hints_match_formats` |
| Map 2 | file 1 `incomplete`; test `test_malformed_log_line_names_expected_format` |
| Map 3 | file 1 `write_log`; same test, stderr part |
## Guardrail tests
- `test_log_hints_match_formats` (keys equal; each example fits its regex)
- Missing inputs: unknown agent → existing `test_log_refuses_bad_fields[R9-x]`
## Expected result
Suite passes; old INCOMPLETE text kept as the message's start.
Recurring issues checked (I1): RI-010, RI-007.
