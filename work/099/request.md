# Work item 099
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-24
## What we want
check_handoff.py tests catch a wrong extra line when 01 or 03 is unreadable: the whole stdout of each bad fixture is pinned, not just the expected lines.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
logs/audit/2026-11-24-092.md (PR #37): A1 removed `return _report(problems)` on the why03 path of check_handoff.py; the run then printed "no work/150/03-handoff.md; nothing else to check" for a file that exists, and all 13 targeted tests still passed. Minor: `.search` in place of `.fullmatch` in check_all also survives.
## Root cause and prevention guardrail (BUG only)
Root cause: the `_ok3` helper asserts only that expected lines are present, never the whole output (RI-012 pattern: tests cover expected text only).
Guardrail: bad fixtures (b)-(e) compare the whole stdout and assert no "no <path>; nothing else to check" line; mutations (return removed, `.search` for `.fullmatch`) each fail a named test.
## Recurring issue link (RI-#, if any)
RI-012 / RI-014 family. Found by A1 before merge; near miss, not counted.
## Done looks like
Both mutations fail named tests; shipped output unchanged.
