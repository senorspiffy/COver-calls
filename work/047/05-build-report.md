# 05 Build report - 047
## Changes made (file: what changed)
scripts/check_pipeline.py (`write_log` refuses an ID without `work/<ID>/request.md`, exit 2; new `orphan_log_lines()`; `main` prints `ORPHAN LOG:` after `LOG TIME:` and adds it to exit 1; docstring); tests/test_pipeline_check.py (`test_log_writes_utc_line` creates work/150/request.md; new `test_log_refuses_item_without_request`, `test_orphan_log_line_is_reported`); .claude/agents/a1-auditor.md (job B first bullet: `ORPHAN LOG:` is an error).
Branch `daily-fixes/2026-11-06` is built on `daily-fixes/2026-11-05` (PR #12: `write_log`, `LOG_LINE` are in that branch), with main's 2026-11-06 audit merged in.
Files: `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` → 0 new; `... | grep -c '^ M'` → 3 changed.
## Connectivity check
- [x] every new function/rule is used (`orphan_log_lines` from `main`; the refusal inside `write_log`, reached by `--log`)
- [x] every input has a source, every output has a consumer (A1's daily step reads ORPHAN LOG; agents get the refusal on `--log`)
- [x] every branch ends in a defined result (no request.md → exit 2, nothing written; no log folders → `ORPHAN LOG: none`)
- [x] no leftover TODOs or unused files
Missing-data grep: scripts only; ccbot/ unchanged by this item.
RI-010: no change to its status (047 is EFFICIENCY on the same log lines); still GUARDED when PR #12 is merged and `LOG TIME: none` on main.
## Test output (pasted, not summarized)
```
$ python3 -m pytest -q
196 passed, 1 skipped in 18.64s
$ python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py
py311 ok
$ python3 scripts/check_pipeline.py   (tail)
INCOMPLETE: none
LOG TIME: none
ORPHAN LOG: none
SKIPPED: none
```
Mutations (scratch copy, removed after): orphan condition → `if False` → 1 failed, 32 passed (tests/test_pipeline_check.py); request.md refusal → `if False:` → 1 failed, 32 passed.
## Deviations from plan
None.
