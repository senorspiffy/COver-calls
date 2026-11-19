# Work item 078
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-19

## What we want
probe_guardrails.py (074): close the skipped-target test gap, fix a wrong fixed message, and add the remaining GUARDED probes.
1. Fixture: mutated run skips the target → NOT HELD; baseline skips the target → `ERROR (baseline: target skipped)`.
2. `_run_probe` "code check: n/a (... conftest REPO ...)" text is true only for RI-013; move the reason into each probe entry.
3. Add probes: RI-002 046 (tickers.json key), RI-007 064, RI-009 037, RI-010 049, RI-011 052, RI-012 059 (anchor-shaped ones first; each must show HOLDS in 05).

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- logs/audit/2026-11-18-074.md: mutant `== "failed"` → `!= "passed"` (skipped target counts as HOLDS) survives the whole test file; shipped code is correct (A1 fixture gave NOT HELD, exit 1). P1, P3.

## Recurring issue link (RI-#, if any)
RI-010, RI-002 (a skipped result must never read as a pass).

## Done looks like
The surviving mutant dies; new probes HOLD on main with pasted output.
