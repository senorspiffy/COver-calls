# Work item 047
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-06

## What we want
A1's first daily question ("Is every log line backed by a file in `work/`?") is answered by hand. Make the script answer it: `--log` refuses an ID that has no `work/<ID>/request.md`, and `check_pipeline.py` lists any committed log line whose ID has no work item.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- A1 probe 2026-11-06, scratch copy of `origin/daily-fixes/2026-11-05` (eb83eea, PR #12): `python3 scripts/check_pipeline.py --log I2 999 "1 file changed | tests 1/1"` → prints `22:15 | I2 | 999 | ...`, exit 0; `work/999` does not exist. `python3 scripts/check_pipeline.py` afterwards → `STUCK: none`, `INCOMPLETE: none`, `LOG TIME: none`, exit 0: the orphan line is not reported anywhere.
- `grep -n "orphan\|backed by" scripts/check_pipeline.py` → nothing. `.claude/agents/a1-auditor.md` job B, first bullet, asks this by hand every day.
- With 045, every step now logs through `--log`, so a typo'd ID (e.g. `--log R3 74 ...` for 047) would be the one way a log line lands without an item.

## Recurring issue link (RI-#, if any)
RI-010 (ESCALATED, 3): related check on the same log lines, no new occurrence.

## Done looks like
`--log I2 999 "1 file changed | tests 1/1"` with no `work/999/request.md` exits 2 and writes nothing. A committed log line (any item ID) with no `work/<ID>/` prints `ORPHAN LOG: 999 (logs/implementation/<date>.md)` and exit 1. Existing logs on main show `ORPHAN LOG: none`. Tests on fixtures. Built on top of `daily-fixes/2026-11-05` (PR #12), which changes the same file.
