# Work item 045
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-05

## What we want
Log lines must be written when their step runs, in the agent's own format. Today a batch of lines typed at the end passes the 043 check.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `logs/research/2026-11-04.md` and `logs/implementation/2026-11-04.md`: all 12 lines for 041–044 read `23:10`. They were added in a975744, committed `2026-11-04T22:24:41+00:00` (`git log -1 --format=%cI a975744`), 46 minutes before the time they state.
- The I1 lines read `FIT | see 04` (i1-reviewer.md: `<verdict> | <n> files planned`); the I2 lines read `see 05 | tests 182/184 (1 skipped, 1 repo check pending)` (i2-builder.md: `<files changed> | tests <pass>/<total>`).
- `work/043/06-verification.md`: "Repo run before the 041–044 log lines were written: `INCOMPLETE: 041 (no log line for R1 R2 R3 I1), ...` (seen in I2's run)". So R1–I1's lines did not exist when I2 ran; they were written afterwards in one go. 041–044/05 each paste "+1 failed: test_repo_pipeline_has_no_skipped_items ... until the 041–044 log lines ... exist".
- `python3 scripts/check_pipeline.py` on main → `INCOMPLETE: none`: the check passes these lines.

## Root cause and prevention guardrail (BUG only)
Root cause: each agent types its own log line, time included, and 043's check (`incomplete()`) only looks for a `| <agent> | <ID> |` line. Nothing ties the line to the moment the step ran or checks its fields, so lines can be written at the end with any time and placeholder fields.
Guardrail:
1. `python3 scripts/check_pipeline.py --log <agent> <ID> "<fields>"` appends the line to the right log file with the current UTC time, and refuses (exit 2) fields that don't match the agent's format. Every agent file says to log with it, right after writing its step file, never by hand.
2. For items from 045 on, `INCOMPLETE` also lists a log line whose fields don't match its agent's format.
3. `LOG TIME:` line (exit 1): a committed log line for an item from 045 on whose `<date> <HH:MM>` (UTC) is later than the commit that added it (`git blame`).
Tests on fixtures for each, including a temp git repo with a back-dated commit.

## Recurring issue link (RI-#, if any)
RI-010, occurrence 3 (ESCALATED).

## Done looks like
A fixture line `see 05` for I2 shows INCOMPLETE; `--log I2 900 "see 05"` exits 2; a line timed after its commit shows `LOG TIME:`; 041–044 (before 045) are not re-checked.
