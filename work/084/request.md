# Work item 084
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-20
## What we want
A check rule that is still on an open branch never flags an item that was built and merged on main before that rule reached main. PR #33's head is green again.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `origin/daily-fixes/2026-11-19` b2f11b9 (main merged in): `INCOMPLETE: 083 (log line for I2 does not match its format (item 045): I2 wants "<n> files changed | tests <last line of python3 -m pytest -q, as printed>"; 06 Verdict is PASS but has no 'Sent back to: none' line (item 071))`; `tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items` fails (1 failed, 570 passed, 1 skipped; A1 run 2026-11-20).
- 083 was built on main (PR #34) under main's rules; the I2 format (076) and `Sent back to:` (071) rules exist only on PR #32/#33.
## Root cause and prevention guardrail (BUG only)
Root cause: the INCOMPLETE checks start at a fixed item number (`from 0xx on`), not at the commit where the rule reached main, so an item merged on main in parallel with an open rules branch is judged by rules it never saw. The 049 rule ("build on top of the RULES BRANCH") is the only guard, and an urgent bot fix (083) skipped it.
Guardrail: each format rule's cutoff is "items whose request.md first reached main after the rule's own commit reached main" (first-parent walk, like the 053 cutoff); items before it print `not checked (<rule> reached main after <ID>)`, never INCOMPLETE. Fixture: item merged on main while a rules branch is open -> not flagged; same item after the rule merges -> flagged. Mutation: cutoff back to the item number -> test fails. run-item.md: when an urgent fix goes on main beside a RULES BRANCH, say so in 05.
## Recurring issue link (RI-#, if any)
RI-010 family (check rule vs when it applies; precedent 049's LOG_TIME_EXCEPT for 048). Found before #33 merged; near miss, not counted (precedent 069/070).
## Done looks like
PR #33 + main merge: 083 not INCOMPLETE, test_repo_pipeline_has_no_skipped_items green; fixture and mutation as above.
