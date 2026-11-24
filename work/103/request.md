# Work item 103
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-24
## What we want
Measure, then decide, the broad LOG BATCH rule: a pytest summary line under any heading that LOG BATCH does not read (e.g. `## Round 2 (2026-11-21, I2)`) is flagged from a new cutoff.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
work/098/03 Scope note and Residual (a) (PR #37): 345 summary-like lines in 78 05/06 files, 14 in 076/05 alone, many outside read sections; R3 had no shell to measure, so 098 built only the `## Round N build` heading rule.
## Root cause and prevention guardrail (BUG only)
n/a (EFFICIENCY). Proposal: R1/R3 get the orchestrator to run `_section_flags` over 076-098 and paste counts; rule only if it flags no correctly-quoted run at or above the cutoff.
## Recurring issue link (RI-#, if any)
RI-010 (gap w), RI-001.
## Done looks like
Measured count in 03; either a rule with fixtures + mutation, or a documented no-go.
