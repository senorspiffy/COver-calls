# 04 Build plan - 020
Fit verdict: FIT
Fits a ~$3k account: text/process change only, no new costs, no trading.
## Extra research (with sources)
None needed; all inputs are repo files.
## Files to create/change
.claude/agents/r1-researcher.md; scripts/check_handoff.py
## Tests and checks
- `python3 scripts/check_handoff.py 001` → PASS
- `python3 scripts/check_handoff.py 020` → PASS
- Old 001 hand-off (main 0ca80e8) → FAIL (for 017-019)
- grep each new instruction in its file
## Expected result
Map steps in 03-handoff.md all applied.
