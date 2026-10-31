# Work item 015
Type: EFFICIENCY
Opened by: A1
Date: 2026-10-30

## What we want
Two wording changes to the agent steps added in 003–008. Split r3 step 1's new feasibility and worked-example text into its own step 1b. Add "in a scratch copy" to i3 step 3's mutation sentence.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `.claude/agents/r3-fact-checker.md` step 1 is now one 858-character line. The longest lines in r1, r2 and a1 are 223, 238 and 244 characters (`awk '{print length}'`, 2026-10-30). The two new checks (feasibility count, worked example vs rule) are the RI-001 and RI-004 guardrails. Buried at the end of a long paragraph, they are the part most likely to be skipped. I3 raised the same point (06 §(3), 07 §3).
- `.claude/agents/i3-verifier.md` step 3: "put back one removed default (e.g. `else 0`), show that ≥ 1 test fails, then restore it". It does not say where. Every mutation run on 003–008 used a scratch copy (05, 06), but the instruction allows editing the repo.

## Done looks like
r3 has a step 1b with the feasibility and worked-example text (the wording itself unchanged). i3 step 3 says "in a scratch copy, never in the repo". These edits are additions or moves only, and they need the person's OK in PR review together with the 003–008 process edits. If 013 lands first, apply this on top of it.
