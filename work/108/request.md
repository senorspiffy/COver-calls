# Work item 108
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-25
## What we want
101's timed05 shallow test reads its field from the fixture's log line, not the constant `SE_FIELD`.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
logs/audit/2026-11-24-101.md (PR #38) optional follow-up.
## Root cause and prevention guardrail (BUG only)
n/a (EFFICIENCY).
## Recurring issue link (RI-#, if any)
RI-014.
## Done looks like
Changing the fixture's field without the constant still passes; mutation of the TIMED branch still fails the test.
