# Work item 086
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-20
## What we want
Step log lines written in one batch at the end of an item are caught by check_pipeline, not only lines timed after the commit.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- logs/research/2026-11-20.md and logs/implementation/2026-11-20.md: R1, R2, R3, I1, I2, I3 for 083 all `10:15`; commit cfc0634 at 10:15:48 UTC. work/083/05 and 06 report pytest runs of ~47 s each (I2 run, I3 run 47.57 s, I3 mutation re-run), so I2 -> I3 alone took over a minute.
- check_pipeline on main: `LOG TIME: none`, `INCOMPLETE: none`; the item-045 rule ("as soon as its file exists, never in a batch at the end") has no check for lines timed before the commit.
## Root cause and prevention guardrail (BUG only)
Root cause: `--log` stamps the current time but nothing ties the line to the moment its step file was written; LOG TIME only catches lines after the commit. A thread that writes all six files and then calls `--log` six times passes.
Guardrail (R1 to choose, measured on past items): e.g. `--log` refuses unless the previous step's line exists, and check_pipeline prints `LOG BATCH: <ID>` when a FULL item's I2 and I3 lines share one minute while 05/06 report a pytest time over 30 s; fixture of 083's lines; mutation. Precedent: 045, 049.
## Recurring issue link (RI-#, if any)
RI-010 (5th occurrence -> ESCALATED).
## Done looks like
083's lines fixture -> `LOG BATCH: 083` (or the chosen check); a correctly spaced fixture -> none; every past FULL item from 045 on checked and the count stated.
