# Work item 031
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-01

## What we want
`run-item.md` says R3's fact check and I3's verification are never skipped, but `scripts/check_pipeline.py` accepts a `Waived:` line for any step, written by anyone. An item with no fact check and no verification shows `complete` and exit 0. Close that hole so the RI-007 guardrail can't be bypassed with one line.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `.claude/commands/run-item.md`: "R2 and I1 may be skipped; R3's fact check and I3's verification never are. Nobody else may shorten the pipeline."
- `scripts/check_pipeline.py::read_request` reads every two-digit number on the `Waived:` line and `classify` drops them from the required steps. It never looks at which steps or who waived them.
- A1 probe (scratch dir, 2026-11-01): item 999, `Scope: FULL`, `Waived: 03 06 (A1, 2026-11-01: test)`, files 01 02 04 05 07 only →
  `999: complete (FULL; Waived: 03 06 (A1, 2026-11-01: test))`, `SKIPPED: none`, exit 0.
- `tests/test_pipeline_check.py` L72 pins an A1-written waiver of 03 as `complete`; no test says a waiver of 03 or 06 needs the person.
- 024's waiver covers 03 and names A1. The person did approve it (PR #6 asked "Approve or ask for them to be redone"; senorspiffy merged it 2026-10-31 22:28 UTC), but the line in request.md does not say so, and the script could not tell the difference.

## Root cause and prevention guardrail (BUG only)
Root cause: item 026 added the `Waived:` escape hatch for work that ran before the check existed, but encoded only "which steps", not the run-item rule about which steps can never be dropped or who may drop them. The check trusts any line in the right shape.
Guardrail: in `check_pipeline.py`, a waiver that includes 03 or 06 counts only if its "who" is `person` (e.g. `Waived: 03 (person, 2026-11-01: ...)`); otherwise the item is SKIPPED with "03/06 can be waived only by the person". Tests: A1-written waiver of 03 → SKIPPED; of 06 → SKIPPED; person-written waiver of 03 → complete; A1-written waiver of 02 → complete. Update 024's line to record the person's approval (PR #6). run-item.md and templates/request.md say the same.

## Recurring issue link (RI-#, if any)
RI-007 (guardrail gap; no new occurrence: every waiver so far was approved by the person in PR #6)

## Done looks like
The probe above prints SKIPPED and exits 1; 024 still shows complete with the person named; the four tests pass.
