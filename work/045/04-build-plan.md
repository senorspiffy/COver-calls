# 04 Build plan - 045
Fit verdict: FIT
Fits a ~$3k account: process only; no trading, no cost.
No open branch (check_pipeline: IN PR none, no OPEN BRANCHES); built on main 941a2b4.
## Extra research (with sources)
`git blame --line-porcelain` prints a header per line with `committer-time` and `committer-tz`, then the line prefixed by a tab; uncommitted lines have the all-zero hash (https://git-scm.com/docs/git-blame#_the_porcelain_format). Use the time (seconds, UTC), not the tz.
## Files to create/change
scripts/check_pipeline.py; tests/test_pipeline_check.py; .claude/agents/r1-researcher.md, r2-improver.md, r3-fact-checker.md, i1-reviewer.md, i2-builder.md, i3-verifier.md, a1-auditor.md; .claude/commands/run-item.md
## Tests and checks
New tests: test_log_writes_utc_line, test_log_refuses_bad_fields, test_malformed_log_line_is_incomplete, test_log_line_after_its_commit_is_flagged; full suite; check_pipeline on the repo (045/046 must pass the new checks); mutation in a scratch copy.
## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1 | `LOG_FORMAT`, `--log` in check_pipeline.py; 2 tests |
| Map 2 | `incomplete()` format check from `LOG_CHECK_FROM = 45`; test |
| Map 3 | `late_log_lines()` + `LOG TIME:` line, exit 1; temp-repo test |
| Map 4 | six agent files, a1, run-item text |
| Map 5 | `_item` fixture writes formatted lines |
## Guardrail tests
- Missing inputs: no git → `LOG TIME: not checked (no git)` (fixture runs outside git: every existing tmp_path test)
- Guardrail: test_log_line_after_its_commit_is_flagged; test_malformed_log_line_is_incomplete
## Expected result
Every map step applied; full suite passes; `check_pipeline.py` → INCOMPLETE none, LOG TIME none, exit 0.
Recurring issues checked (I1): RI-002, RI-007, RI-009, RI-010.
