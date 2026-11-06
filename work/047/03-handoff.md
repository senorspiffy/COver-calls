# 03 Research hand-off - 047
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| `write_log` never looks at `work/` | scripts/check_pipeline.py L167–184 (`def write_log`) | VERIFIED |  |
| `--log I2 999 ...` exits 0 with no work/999 and the daily run says nothing | A1 probe 2026-11-06 (work/047/request.md) | VERIFIED |  |
| `LOG_LINE` parses agent lines with a 3-digit ID | scripts/check_pipeline.py L91 | VERIFIED |  |
| 0 orphan lines on main today | `LOG_LINE` over 15 log files → 257 agent lines, 0 IDs without `work/<ID>/` (R3 run 2026-11-06) | VERIFIED |  |
| request.md exists before R1 runs | .claude/commands/run-item.md ("one work item in work/<ID>/request.md"; r1-researcher.md Input) | VERIFIED |  |
| A1 checks "every log line backed by a file in work/" by hand | .claude/agents/a1-auditor.md L15 | VERIFIED |  |
| `test_log_writes_utc_line` writes for 150 with no work folder | tests/test_pipeline_check.py `test_log_writes_utc_line` | VERIFIED |  |
**Totals:** 7 rows checked → **7 VERIFIED as-is**, **0 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | `write_log` refuses (exit 2, nothing written) when `work/<ID>/request.md` does not exist; message names the missing file | agent, ID, fields | exit code | `--log I2 999 "1 file changed \| tests 1/1"` in an empty tmp dir → exit 2, no logs/ | – |
| 2 | `orphan_log_lines()`: every `LOG_LINE` in logs/research/????-??-??.md and logs/implementation/????-??-??.md (working tree) whose `work/<ID>/` folder is missing → `"<ID> (<path>)"`, one per ID and file | logs/, work/ | list | fixture with a line for 999 and no folder → listed; a line for an existing item → not listed | 0 of 257 lines on main (R3 run 2026-11-06) |
| 3 | `main` prints `ORPHAN LOG: <list or none>` after `LOG TIME:` and exits 1 when the list is non-empty | step 2 | stdout, exit | fixture → exit 1; repo → `ORPHAN LOG: none` (`test_repo_pipeline_has_no_skipped_items` keeps passing) | – |
| 4 | Docstring, `a1-auditor.md` (ORPHAN LOG is an error; replaces the hand check) | – | text | grep | – |
| 5 | `test_log_writes_utc_line` creates `work/150/request.md` first | – | test | suite passes | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| work/<ID>/request.md (`--log`) | missing | `--log refused: no work/<ID>/request.md`, exit 2 |
| logs/research or logs/implementation folder | missing | no lines read → `ORPHAN LOG: none` (nothing to check; the same as today's `LOG TIME`) |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| start value | orphans on main = lines with no folder | 257 lines, 0 without folder → `none` | ✓ |
| probe fails | 999 line, no work/999 → listed | 1 orphan → exit 1 | ✓ (planned test) |
| Totals | 7+0+0 = 7 | 7 | ✓ |
Recurring issues checked (R3): RI-010 (same log lines; the line is written by `--log`), RI-007 (out-of-order log before request.md is refused), RI-009 (ID from `--next-id`; built on open PR #12's branch), RI-002 (no data path; missing folder → refused, never passed).

`python3 scripts/check_handoff.py 047` output:
sources count (unique URLs in 01-research.md): 0
fact-check rows: 7
totals line: 7 rows -> 7 as-is, 0 fixed, 0 removed
PASS
