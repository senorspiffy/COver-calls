# 04 Build plan - 047
Fit verdict: FIT
Process change in `scripts/check_pipeline.py` only; no strategy rule or bot code touched. Built on `daily-fixes/2026-11-05` (PR #12), which adds `write_log` and `LOG_LINE` in the same file (item 034).

## Extra research (with sources)
- None needed. Checked: `late_log_lines()` globs `????-??-??.md` under the two log folders; the new function uses the same glob so both read the same files.

## Files to create/change
1. scripts/check_pipeline.py: `write_log` refuses a missing `work/<ID>/request.md` (exit 2); new `orphan_log_lines()`; `main` prints `ORPHAN LOG:` and adds it to the exit code; docstring.
2. tests/test_pipeline_check.py: `test_log_writes_utc_line` creates `work/150/request.md`; new `test_log_refuses_item_without_request`, `test_orphan_log_line_is_reported`.
3. .claude/agents/a1-auditor.md: the job B bullet names `ORPHAN LOG:` as an error, so the hand check is the script's line.

## Tests and checks
- `python3 -m pytest -q` (all pass); `python3 scripts/check_pipeline.py` → `ORPHAN LOG: none`, exit 0.
- Mutation (scratch copy): orphan condition `if not ...is_dir()` → `if False` → the orphan test fails; drop the request.md refusal → the refusal test fails.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| 1 refuse --log without request.md | File 1 (`write_log`), test_log_refuses_item_without_request |
| 2 orphan_log_lines | File 1, test_orphan_log_line_is_reported |
| 3 ORPHAN LOG line, exit 1 | File 1 (`main`), test_orphan_log_line_is_reported; repo run |
| 4 docstring, a1-auditor.md | Files 1, 3 |
| 5 fixture fix | File 2 |

## Guardrail tests
- Feasibility: ORPHAN LOG on main = 0 of 257 → `test_repo_pipeline_has_no_skipped_items` (repo run exit 0).
- Missing inputs: work/<ID>/request.md absent → test_log_refuses_item_without_request; log folders absent → `test_log_time_not_checked_outside_git` fixture (no orphan output beyond `none`).

## Expected result
`--log I2 999 ...` with no work/999/request.md → exit 2, nothing written; a fixture line for 999 → `ORPHAN LOG: 999 (logs/implementation/2026-10-31.md)`, exit 1; repo → `ORPHAN LOG: none`.
