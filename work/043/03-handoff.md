# 03 Research hand-off - 043
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| 040 06 misses step 0/2 | work/040/06 | VERIFIED |  |
| 013–016 miss step 0 | grep | VERIFIED |  |
| i3 requires them | i3-verifier.md | VERIFIED |  |
| 040 log lines missing | grep logs | VERIFIED |  |
| template lacks fields | templates/verification.md | VERIFIED |  |
**Totals:** 5 rows checked → **5 VERIFIED as-is**, **0 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | templates/verification.md: `Recurring issues checked:` and `check_pipeline line:` fields | – | template | grep | – |
| 2 | check_pipeline `INCOMPLETE:` for items ≥ 041: 06 without a `Recurring issues checked:` line naming RI-, or a step file without its `| <agent> | <ID> |` log line; exit 1 | work/, logs/ | INCOMPLETE line | test_incomplete_06_and_missing_log_line | 4 items (041–044) must pass |
| 3 | i3 step 0/2 and a1 name the new line | – | text | grep 'item 043' | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| logs/ folder | absent | every step of a ≥041 item listed as unlogged |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| first checked ID | 041 > 040 | CHECKLIST_FROM = 41 | ✓ |
| Totals | 5+0+0=5 | 5 | ✓ |
Recurring issues checked (R3): RI-002, RI-007, RI-009, RI-010.
