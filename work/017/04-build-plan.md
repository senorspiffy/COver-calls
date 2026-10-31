# 04 Build plan - 017
Fit verdict: FIT
Fits a ~$3k account: text/process change only, no new costs, no trading.
## Extra research (with sources)
None needed; all inputs are repo files.
## Files to create/change
work/001/03-handoff.md (step 1, 9(a), Self-check); templates/research-handoff.md; .claude/agents/r3-fact-checker.md; .claude/agents/a1-auditor.md
## Tests and checks
- `python3 scripts/check_handoff.py 001` → PASS
- `python3 scripts/check_handoff.py 017` → PASS
- Old 001 hand-off (main 0ca80e8) → FAIL (for 017-019)
- grep each new instruction in its file
## Expected result
Map steps in 03-handoff.md all applied.
