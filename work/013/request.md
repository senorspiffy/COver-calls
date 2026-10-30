# Work item 013
Type: EFFICIENCY
Opened by: A1
Date: 2026-10-30

## What we want
Have R3, I1, I2 and I3 read `logs/recurring-issues.md` at the start of every item, as R1 and R2 already do. Each should confirm it checked its output against each open/ESCALATED entry.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
Only `.claude/agents/r1-researcher.md` (step 1) and `r2-improver.md` (step 1) mention it. The file header says "Read by R1 and R2". Today's RI-001 and RI-002 occurrences were introduced at the R3, I1 and I2 stages (002/03 step 6, 002/04 data.py row, `ccbot/data.py`, `ccbot/screen.py`), which never read the file.

## Done looks like
The four instruction files have the step, and the recurring-issues header says "Read by every R and I agent".
