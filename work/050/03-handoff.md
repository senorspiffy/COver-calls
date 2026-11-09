# 03 Research hand-off - 050
Status: READY
Recurring issues checked (R3): RI-010 (helps writers hit the format; no check weakened), RI-007 (no step skipped), RI-002 (no data path).
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| INCOMPLETE names no format | scripts/check_pipeline.py `def incomplete`; main output 2026-11-07 | VERIFIED |  |
| `--log` refusal prints the regex | `def write_log`; A1 probe 2026-11-07 | VERIFIED |  |
| Agent files spell formats in words | .claude/agents/i1-reviewer.md, i2-builder.md (last paragraph) | VERIFIED |  |
| Test asserts the INCOMPLETE text | tests/test_pipeline_check.py `test_malformed_log_line_is_incomplete` | VERIFIED |  |
**Totals:** 4 rows checked → **4 VERIFIED as-is**, **0 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | `LOG_HINT` dict: one plain form per agent, from the agent files | agent files | dict | test: same keys as LOG_FORMAT; each example matches its regex | – |
| 2 | INCOMPLETE: `log line for I1 I2 does not match its format (item 045): I1 wants "…"; I2 wants "…"` | LOG_HINT | message | fixture test on the text | – |
| 3 | `--log` refusal: `--log refused: … does not match "<hint>"` (exit 2, nothing written) | LOG_HINT | stderr | test on stderr | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| unknown agent in `--log` | not in LOG_HINT | existing text `an agent R1 R2 R3 I1 I2 I3` |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Hints | one per LOG_FORMAT key | 6 = 6 | ✓ |
| Totals | 4 + 0 + 0 | 4 | ✓ |
`python3 scripts/check_handoff.py 050` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 4
totals line: 4 rows -> 4 as-is, 0 fixed, 0 removed
PASS
```
