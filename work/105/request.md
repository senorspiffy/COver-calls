# Work item 105
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-25
## What we want
classify accepts a person waiver of 03/06 only in the dated form `(person, <YYYY-MM-DD>: <why>)`, same as 093/100; undated `Waived: 03 06 (person)` is SKIPPED.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
work/100/04-build-plan.md (I1 note, classify ~L753) and logs/audit/2026-11-25-100.md (A1 confirmed, low severity): undated `Waived: 03 06 (person)` is accepted. No real item uses it.
## Root cause and prevention guardrail (BUG only)
Root cause: the 031 who-check reads `<who>` only; the date part of the run-item form is never required (RI-012 pattern: loose match on free text).
Guardrail: reuse PERSON_DATED anchored match for 03/06 waivers; negative tests for undated and quoted forms; mutation back to the loose check fails a named test; real items' results unchanged.
## Recurring issue link (RI-#, if any)
RI-012. Found by A1 before merge; near miss, not counted.
## Done looks like
Undated person waiver of 03/06 is SKIPPED; existing dated waivers unchanged; mutation fails a named test.
