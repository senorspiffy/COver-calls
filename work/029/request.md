# Work item 029
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-10-31

## What we want
Items 009–016 were opened on 2026-10-30 and still have only `request.md`. Nothing lists them, and `.claude/commands/daily-audit.md` only runs items opened that day. Make the daily audit show stuck items, with age, at the top of the report.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
`ls work/009 ... work/016` → `request.md` only. 014 is the BUG that moves RI-002 to GUARDED, so RI-002 stays ESCALATED while it waits.

## Done looks like
`scripts/check_pipeline.py` (from 026) has a "stuck" section: items with only `request.md` and a request date at least 1 day old. daily-audit.md tells A1 to list them at the top of the report and ask the person which to run. A test covers it.
