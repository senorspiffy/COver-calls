# Work item 110
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-25
## What we want
Close the two LOG BATCH residuals 103's A1 named, or document them: (a) a suite line directly under a `## Round N (...)` wrapper with no read sub-heading; (b) `deselected` pytest runs not counted.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
logs/audit/2026-11-25-103.md and work/103/02 Holes (PR #38). 103 measured 0 instances of (a) at 092-098 beyond the 098 rule.
## Root cause and prevention guardrail (BUG only)
n/a (EFFICIENCY). Measure first (orchestrator runs R1's read-only script), then rule with fixtures + mutation or documented no-go.
## Recurring issue link (RI-#, if any)
RI-010 (gap w).
## Done looks like
Measured count in 03; rule or no-go with reason.
