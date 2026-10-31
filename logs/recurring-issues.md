# Recurring issues

Kept by A1. Read by R1 and R2 before every item. One entry per root cause.
Any entry with 3+ occurrences is ESCALATED: the guardrail didn't hold and the person is told.

<!-- Entry format:
## RI-001: <short name>
Status: OPEN | GUARDED | ESCALATED
Root cause:
Guardrail(s) added: <what, where, work item ID>
Occurrences: <count>
- <YYYY-MM-DD> | <work item ID> | <where found> | <evidence>
-->

## RI-005: Numbers in the hand-off not re-checked against the rule they belong to
Status: OPEN
Root cause: R3 changes a rule (adds a buffer, sets a % trigger) but does not re-derive the thresholds and worked-example numbers from that rule's own formula, so the text and the check disagree.
Guardrail(s) added: Self-check section in `templates/research-handoff.md` + R3 duty 5 + A1 spot-check (017, 018) - in PR daily-fixes/2026-10-30, GUARDED once merged
Occurrences: 2
- 2026-10-30 | 017 | work/001/03-handoff.md step 1, step 9(a) | "2 at ≥ $5.6k" / "one ≤ $55" fail step 1's own check `(price × 100 × positions) ≤ cash − $200` (need $5,800 / $5,700)
- 2026-10-30 | 018 | work/001/03-handoff.md worked example | 50% exit filled at $0.24 on a $0.47 sale = 51.1% (> 50% trigger)

## RI-017: Hand-counted totals in hand-off and logs
Status: OPEN
Root cause: R3 counts fact-check rows by hand and "fixed" vs "removed" is undefined, so totals, the removed list and the log line drift apart.
Guardrail(s) added: `scripts/check_handoff.py` run by R3, I3, A1 + fixed/removed definitions in template (019) - in PR daily-fixes/2026-10-30, GUARDED once merged
Occurrences: 1
- 2026-10-30 | 019 | work/001/03-handoff.md Totals + logs/research/2026-10-30.md 17:33 | 77 rows in table vs "76 rows → 60/12/4"; removed list has 7 entries vs "4 removed"
