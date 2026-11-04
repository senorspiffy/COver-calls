# Work item 043
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-04

## What we want
I3 step 0 (name the recurring issues checked, item 013) and step 2 (paste this item's `check_pipeline.py` line) are skipped in 06 files, and steps run with no log line. Nothing checks either.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `work/040/06-verification.md` (written 2026-11-03): no RI entry named, no `check_pipeline.py` line, no Python 3.10/3.11 compile note.
- `work/013..016/06-verification.md` (built in a95a51a, the commit that added step 0 to i3): `grep -ci 'recurring\|RI-'` → 0 in each. 037–039 (PR #10) do name them, as "Recurring issues checked: ...".
- 040's R1, R3 and I3 (2026-11-03) have no line in `logs/research/` or `logs/implementation/` (`grep -rn "040" logs/` → only `15:48 | I2 | 040`, filed under 2026-10-31).
- `templates/verification.md` has no field for step 0 or the pipeline line.

## Root cause and prevention guardrail (BUG only)
Root cause: the step-0 and step-2 duties live only in the agent text; the template a step follows has no field for them, and no script checks that the field or the step's log line exists. Files written outside run-item (040) skip them first.
Guardrail: `templates/verification.md` gets `Recurring issues checked:` and `check_pipeline line:` fields. `check_pipeline.py` reports `INCOMPLETE:` (exit 1) for an item from 041 on whose 06 has no `Recurring issues checked:` line naming an RI-, or whose step files have no `| <agent> | <ID> |` line in logs/. Tests on fixtures.

## Recurring issue link (RI-#, if any)
New RI-010 (2 occurrences).

## Done looks like
A fixture item missing the field or a log line shows INCOMPLETE; items 041–044 pass it.
