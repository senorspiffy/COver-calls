# 04 Build plan - 006
Fit verdict: FIT
Fits a ~$3k account: text/process change only, no new costs, no trading.
## Extra research (with sources)
None needed; all inputs are repo files.
## Files to create/change
templates/request.md; .claude/commands/run-item.md; .claude/agents/r3-fact-checker.md; work/001/request.md
## Tests and checks
- `python3 scripts/check_handoff.py 001` → PASS
- `python3 scripts/check_handoff.py 006` → PASS
- Old 001 hand-off (main 0ca80e8) → FAIL (for 002-004)
- grep each new instruction in its file
## Expected result
Map steps in 03-handoff.md all applied.
