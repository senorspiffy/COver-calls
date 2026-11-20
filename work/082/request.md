# Work item 082
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-20

## What we want
Small test and rule hardening found in today's per-item audits (075-079), in one item:
1. 076: a fixed `Suite:` label in templates/build-report.md; check_pipeline compares it whole-line with the I2 log `tests` field (today a dropped part, `411 passed` for `411 passed, 1 skipped`, passes). Add an RI-006 probe once it holds on main.
2. 077: test the fence-closer length rule (`{n,}` → `{n}` in `_md_lines` survives) and the left `\|` in `_logged` (dropping it survives).
3. 078: probe `recorded` field is never checked (deleting it survives); format assert in `test_shipped_probes_well_formed` and a "(live differs)" marker.
4. 079: `SHALLOW_LINE.fullmatch` → `.match` survives; add a case. a1-auditor.md job B has no unshallow sentence (grep 0) while both command files do.
5. Orchestrator commit subjects are copied from the step file, not reworded (e813e1f said "pin part order"; R15/R16 pin the `, ` separator).

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- logs/audit/2026-11-19-076.md P1, P2; logs/audit/2026-11-19-077.md P1, P2; logs/audit/2026-11-19-078.md P1; logs/audit/2026-11-19-079.md P3, P4.

## Recurring issue link (RI-#, if any)
RI-006 (1), RI-010 (2-4), RI-014 (4).

## Done looks like
Each sub-point has a fixture test and a mutation that fails it; the a1 text names unshallow.
