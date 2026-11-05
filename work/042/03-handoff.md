# 03 Research hand-off - 042
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| FAST read without who | check_pipeline.py read_request | VERIFIED |  |
| probe FAST (I2) → complete | A1 probe | VERIFIED |  |
| run-item format | run-item.md L10 | VERIFIED |  |
| A1 verdict not read | classify | VERIFIED |  |
| 040 decision 2026-11-03 | work/040/request.md | VERIFIED |  |
**Totals:** 5 rows checked → **5 VERIFIED as-is**, **0 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | FAST only as `FAST (person, YYYY-MM-DD)`; other FAST → SKIPPED | request.md | status | test_fast_needs_person_and_date | 1 FAST item (040) |
| 2 | last `A1 result:` FAIL → `A1 FAIL` status + `A1 FAIL:` line, exit 1 | 07 | status | test_a1_fail_is_not_complete | 1 (040) |
| 3 | 040 request: `Scope: FAST (person, 2026-11-03)`; run-item/a1 text names A1 FAIL | – | text | check_pipeline on repo | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| who/date on FAST | absent | SKIPPED: FAST needs (person, <date>) |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| 040 after fix | FAST (person, 2026-11-03) + last A1 FAIL | A1 FAIL | ✓ |
| Totals | 5+0+0=5 | 5 | ✓ |
Recurring issues checked (R3): RI-002, RI-007, RI-009, RI-010.
