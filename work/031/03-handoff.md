# 03 Research hand-off - 031
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| Waiver of 03/06 by A1 shows complete | probe output | VERIFIED |  |
| run-item forbids skipping R3/I3 | run-item.md L10 | VERIFIED |  |
| 024's waiver was approved by the person | PR #6 body + merged_by senorspiffy | VERIFIED |  |
| Test L72 pins an A1 waiver of 03 as complete | tests/test_pipeline_check.py | VERIFIED | test changed to who=person |
**Totals:** 4 rows checked → **3 VERIFIED as-is**, **1 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | PERSON_ONLY = 03, 06; non-person waiver of them → SKIPPED | request.md Waived line | status line | test_fact_check_and_verification_waivable_only_by_person | – |
| 2 | 024 waiver who-field → person (PR #6) | PR #6 | request.md | check_pipeline → 024 complete | – |
| 3 | run-item.md, templates/request.md, README say it | – | text | grep 'only the person' / 'person (item 031)' | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| Who-field on a Waived line (request.md) | absent or not `person` | waiver of 03/06 → SKIPPED '03 06 can be waived only by the person' |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Probe | A1 waives 03 06 → SKIPPED | 999: SKIPPED, exit 1 | ✓ |
| 024 | who=person, waives 03 → complete | 024: complete | ✓ |
| Totals | 3+1+0=4 | 4 | ✓ |
`python3 scripts/check_handoff.py 031` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 4
totals line: 4 rows -> 3 as-is, 1 fixed, 0 removed
PASS
```
