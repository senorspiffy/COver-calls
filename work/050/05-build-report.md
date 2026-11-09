# 05 Build report - 050
## Changes made (file: what changed)
- scripts/check_pipeline.py: `LOG_HINT` (6 agents: plain form + an example); INCOMPLETE adds `: I1 wants "…"; I2 wants "…"` after the old `does not match its format (item 045)` text; `--log` refusals print the plain form instead of the regex.
- tests/test_pipeline_check.py: `test_log_hints_match_formats`, `test_malformed_log_line_names_expected_format`; `test_malformed_log_line_is_incomplete` now asserts the old text as a prefix (see Deviations).
File counts: `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` → 0 new; `... | grep -c '^ M'` → 2 changed.
## Connectivity check
- [x] every new function/rule is used (`LOG_HINT` in `incomplete` and `write_log`)
- [x] every input has a source, every output has a consumer (INCOMPLETE → A1/I3; refusal → the step's agent)
- [x] every branch ends in a defined result (unknown agent → old `an agent R1 …` text, exit 2)
- [x] no leftover TODOs or unused files
## Test output (pasted, not summarized)
```
$ python3 -m pytest -q
205 passed, 1 skipped in 22.92s
$ python3 scripts/check_pipeline.py --log I2 048 "see 05"
--log refused: I2 | 048 | see 05 does not match "<n> files changed | tests <pass>/<total>"
$ python3 scripts/check_pipeline.py | tail -4
INCOMPLETE: none
LOG TIME: none (not checked: 048: ... (item 049))
ORPHAN LOG: none
SKIPPED: none
```
## Deviations from plan
`test_malformed_log_line_is_incomplete` asserted the whole old message including its closing `)`; it now asserts the old text up to `(item 045)`, as 02 said to keep (prefix). One assertion line; same file as planned.
RI-010: 050 adds hints only; no check weakened.
