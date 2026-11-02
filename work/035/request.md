# Work item 035
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-02

## What we want
`awaiting A1` (item 033) should apply to every item that hasn't been audited, not only to items whose request is dated 2026-10-31 or later.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `scripts/check_pipeline.py` (PR #8): `A1_RESULT_FROM = dt.date(2026, 10, 31)`; an item asks for `A1 result:` only if `opened >= A1_RESULT_FROM`. `opened` is the request's Date, not when its 07 was written.
- Items 009–016 are dated 2026-10-30 but were built on 2026-10-31 in PR #7. None of their 07 files has an `A1 result:` line (grep, 0 of 8).
- A1 probe, 2026-11-02: PR #8 + PR #7 merged in scratch → `009: complete (FULL)`, `014: complete (FULL)`, `016: complete (FULL)`, `AWAITING A1: none`. Eight unaudited items would look finished.
- `tests/test_pipeline_check.py::test_complete_needs_a1_result` pins item 112 (dated 2026-10-30, no A1 line) as `complete`.

## Root cause and prevention guardrail (BUG only)
Root cause: 033 used the request date as a stand-in for "07 written after the A1-line rule existed". An item opened earlier and built later slips under the cutoff.
Guardrail: replace the date with a closed list of the items whose 07 was audited in a daily report before item 033 (002, 003, 017–022; "never add a new item here", like LEGACY). Every other item with all steps and no `A1 result:` line is `awaiting A1`, whatever its date. Test: an item dated 2026-10-30 that is not on the list → awaiting A1; 017 → complete.

## Recurring issue link (RI-#, if any)
RI-007 (guardrail gap in 033, no new occurrence: PR #7 isn't merged yet).

## Done looks like
On main + PR #8 + PR #7 (scratch), 009–016 show `awaiting A1` until A1 records them; on main + PR #8, 023–033 still show complete. The updated test passes.
