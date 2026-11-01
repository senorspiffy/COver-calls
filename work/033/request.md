# Work item 033
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-01

## What we want
Record A1's per-item result in the item, so `complete` in `check_pipeline.py` means "audited", not just "07 audit task written".

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `scripts/check_pipeline.py` marks an item `complete` once `07-audit-task.md` exists. 07 is written by I3 (or R3) as a request to A1.
- `a1-auditor.md` job A (per item) has no output file or line. The 023–030 07 tasks were written 2026-10-31 22:25; their checks were done only in today's daily report, and nothing in `work/` shows it.
- So an item whose audit never ran looks the same as an audited one.

## Done looks like
A1 per-item mode appends `A1 result: PASS | FAIL (<date>, <where>)` to `07-audit-task.md`. `check_pipeline.py` shows `awaiting A1` (not an error) for items dated 2026-10-31 or later that have every step but no A1 line, and lists them on an `AWAITING A1:` line. Today's A1 results for 023–030 are recorded. A test pins both cases.
