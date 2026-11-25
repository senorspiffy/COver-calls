# Work item 100
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-24
## What we want
`_build_waived` (item 062) accepts a person waiver only when the text after the step numbers is the anchored `(person, <date>: ...)` form; a quoted person form inside other text is refused.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
logs/audit/2026-11-24-093.md F1 (PR #37), reproduced by A1: `_build_waived` returns True for `Waived: 04 05 06 (person: x "(person, 2026-11-19: ok)")`. Also flagged by 093's R2, R3 and I1. F2: 093's N-g fixture (unreadable request.md) has no Waived text, so it cannot show an unreadable request.md is never excused.
## Root cause and prevention guardrail (BUG only)
Root cause: `WAIVE_BUILD_BY_PERSON.search` runs over the whole line instead of an anchored match (RI-012 pattern: classification by substring search).
Guardrail: use 093's `PERSON_DATED.match` on the text after the steps; in-text negative test like 093's N-d; mutation back to `.search` must fail it. N-g fixture becomes a valid person waiver plus a bad byte, asserting the strict reason.
## Recurring issue link (RI-#, if any)
RI-012. Found before merge; near miss, not counted.
## Done looks like
Quoted form refused; work/062 and work/024 unchanged; mutation fails a named test.
