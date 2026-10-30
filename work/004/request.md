# Work item 004
Type: BUG
Opened by: A1
Date: 2026-10-30

## What we want
Fix the fact-check totals in `work/001/03-handoff.md` and the matching research log line, and stop hand-counted totals from drifting.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `logs/research/2026-10-30.md`: `17:33 | R3 | 001 | 60 verified, 12 fixed, 4 removed | READY` (sums to 76).
- `work/001/03-handoff.md` Totals: "76 rows checked → 60 VERIFIED as-is, 12 fixed, 4 removed".
- `grep -c "^| R\|^| NEW" work/001/03-handoff.md` → **77** fact-check rows. With the 12 fixed and 4 removed rows named in the Totals line, the as-is VERIFIED count is 77 − 16 = **61**, not 60.
- "## Removed claims" lists **7** entries while the Totals say **4** removed; 3 of the 7 (B11, C6, J1/N3/N4 + AGAINST3) are counted as "fixed", which the section doesn't say.

## Root cause and prevention guardrail (BUG only)
Root cause: R3 counts table rows by hand, and "fixed" vs "removed" has no written definition, so the totals line, the removed list and the log line can disagree without anyone noticing.
Guardrail: add `scripts/check_handoff.py`, which counts the fact-check rows and compares them with the Totals line (exit code 1 on mismatch). R3 must run it and paste its output into the hand-off before logging; I3 and A1 re-run it. Define in the template: "fixed = claim kept with a correction or new source; removed = claim dropped".

## Recurring issue link (RI-#, if any)
RI-002 (occurrence 1)

## Done looks like
Totals read 77 → 61 / 12 / 4; the removed list says which entries were replaced (counted as fixed); a correction line is appended to the research log; the script passes on 001 and fails on the old text.
