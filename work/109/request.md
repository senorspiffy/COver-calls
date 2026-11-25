# Work item 109
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-25
## What we want
Every `*_FROM` cutoff comparison site (14 found by 102's A1) has a FROM / FROM-1 boundary test, not only the 7 constants 102 pinned.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
logs/audit/2026-11-25-102.md residual (a) (PR #38).
## Root cause and prevention guardrail (BUG only)
n/a (EFFICIENCY). Proposal: parametrized test over each comparison site; `>=`→`>` mutant per site fails a named id.
## Recurring issue link (RI-#, if any)
RI-001, RI-010.
## Done looks like
Each site's off-by-one mutant fails a named test.
