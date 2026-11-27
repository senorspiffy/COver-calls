# Work item 116
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-27
## What we want
(a) Remove `who` from parse_request now (113 kept it on a stale reason); (b) pin 110's "as of 4404a28" docstring clause.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
logs/audit/2026-11-27-113.md F-1, F-3 (PR #40): the docstring reason "origin/main unpacks 3" is old text in merge base 94a20a5, so true new callers k = 0 after 917f522; A1 mutant M-4b (drop the "as of 4404a28" clause) survives.
## Root cause and prevention guardrail (BUG only)
n/a (EFFICIENCY).
## Recurring issue link (RI-#, if any)
RI-010.
## Done looks like
`who` gone with all unpack sites updated and suite green (or kept with a current reason); M-4b fails a named pin.
