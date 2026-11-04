# Work item 044
Type: EFFICIENCY
Scope: FULL
Opened by: A1
Date: 2026-11-04

## What we want
`check_handoff.py --all` prints `no hand-off` for items whose hand-off exists only on an open branch, which reads like an error. Say where the hand-off is instead.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- main 2026-11-04: `check_handoff.py --all` → `037: no hand-off`, `038: no hand-off`, `039: no hand-off`, while `check_pipeline.py` shows them IN PR (origin/daily-fixes/2026-11-03 has 01–07, PR #10). A1 had to cross-check by hand.

## Done looks like
Those lines read `037: IN PR (origin/daily-fixes/2026-11-03)`; items with no hand-off anywhere still say `no hand-off`.
