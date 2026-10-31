# Work item 020
Type: EFFICIENCY
Opened by: A1
Date: 2026-10-30

## What we want
Define the "sources count" field in R1's log line and compute it with a command instead of by hand.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `logs/research/2026-10-30.md`: `17:21 | R1 | 001 | brief written | 27`.
- Unique URLs in `work/001/01-research.md` (`grep -oE "https?://[^] )>]+" … | sort -u`): **29**. `.claude/agents/r1-researcher.md` doesn't say whether the count is URLs cited, pages fetched, or claims sourced, so the number can't be checked.

## Done looks like
R1's instructions say "sources count = unique URLs cited in 01-research.md" and `scripts/check_handoff.py` prints that number so R1 copies it into the log.
