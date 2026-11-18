# Work item 073
Type: IDEA
Scope: FULL
Opened by: person
Date: 2026-11-18

## What we want
I3 always makes its own full realtest run at the head commit; it never reuses I2's head run, even under a same-inputs check. The i3-verifier text and run-item.md say this in one clear line.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- Person's choice, 2026-11-18 02:31 UTC, decision card "Should the final checker (I3) always do its own full backtest run?" → "Always own run".
- Open question raised in logs/audit/2026-11-17-068.md ("For the person"): 068's I3 reused I2's head run (disclosed, no number changed).

## Done looks like
One-line clarification in .claude/agents/i3-verifier.md (and run-item.md if needed): I3's head run is its own; base-run reuse rules unchanged. If cheap, a check that 06 names a head-run output dir different from 05's.
