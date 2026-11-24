# Work item 101
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-24
## What we want
Each shallow-clone `elif unsure` branch that 095 added (TIMED, LOG BATCH, Suite, round heading) has its own test.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
logs/audit/2026-11-24-095.md and work/095/06 (PR #37): replacing the TIMED branch with `elif False` leaves the test file green. Fails closed (entry goes back to INCOMPLETE, exit 1), so no wrong "none".
## Root cause and prevention guardrail (BUG only)
n/a (EFFICIENCY). Proposal: one shallow fixture per branch asserting the entry lands in INCOMPLETE NOT CHECKED; `elif False` mutation per branch fails a named test.
## Recurring issue link (RI-#, if any)
RI-014.
## Done looks like
Four mutations each fail a named test; full-clone output unchanged.
