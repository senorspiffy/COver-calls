# Work item 071
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-18

## What we want
`scripts/check_pipeline.py` reads the verdict in 06-verification.md, so an item whose latest I3 round is FAIL shows "I3 FAIL (sent back to <step>)" instead of "in progress (FULL: next 07)".

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- daily-fixes/2026-11-17 at 652a320: work/069/06-verification.md round 1 = FAIL, yet check_pipeline printed `069: in progress (FULL: next 07)` (reported by I3 for 069, 2026-11-17 23:50 UTC; same for 070 at 7f5e345).
- A1 FAIL is already shown from 07's last line (item 042); 06 has no equivalent.

## Recurring issue link (RI-#, if any)
RI-010 (a step's result exists only in text no script reads).

## Done looks like
A FAIL verdict as the latest round in 06 gives an `I3 FAIL:` summary line (like `A1 FAIL:`), cleared by a later PASS round; fixture tests for FAIL, FAIL→PASS, and old items without round headers.
