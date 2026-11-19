# Work item 077
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-19

## What we want
Small checker and test hardening found in today's per-item audits (071, 073), in one item:
1. t23 (073) pins the clause that carries the person's choice: "even if the same-inputs check passes" (i3) and "even when the same-inputs check passes" (run-item).
2. check_pipeline prints `BRANCH FAIL:` for I3 FAIL / A1 FAIL items on unmerged branches (071 gap x).
3. One rule for 06 FAIL + 07 ending in A1 PASS (I3 FAIL vs `_open_at` closed, 071 gap w), pinned by a test.
4. One shared comment/fence-strip helper for `i3_verdict` and `_field_gap` (covers `~~~` and longer fences).
5. check_pipeline flags step files in work/ that are not committed and have no log line (`UNCOMMITTED STEP:`; 074 resume near miss).

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- logs/audit/2026-11-18-073.md P1: changing ", even if the same-inputs check passes;" to ", unless ..." still passed t23 3/3.
- logs/audit/2026-11-18-071.md P1-P3; logs/audit/2026-11-18-074.md P4 (I3 round cut by a container restart left an uncommitted 06 that check_pipeline counted).

## Recurring issue link (RI-#, if any)
RI-010 (a step's result only in text no script checks).

## Done looks like
Each sub-point has a fixture test and a mutation that fails it.
