# Work item 090
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-21
## What we want
Step log lines written in a batch are caught even when the item has no pytest time or was sent back once, and shallow clones never answer LOG TIME / MAIN AHEAD / unrelated-branch from cut history.
## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- logs/audit/2026-11-21-086.md finding 2: the I2 time is optional (`log_fields_ok('I2','086','1 file changed | tests 5 passed')` is True); an untimed item is only "not computable" (exit 0); after one send-back, rule D is off for the item (gap (y)).
- logs/audit/2026-11-21-081.md F2: in a `--depth 1` clone a late log line gives `LOG TIME: none` (full clone flags it); MAIN AHEAD reports a false "1 commits not in HEAD" and drops origin/main from OPEN BRANCHES; a branch sharing history is called "no common history".
## Root cause and prevention guardrail (BUG only)
Root cause: 086's rule C needs a time and D stops after a send-back; `late_log_lines`, `main_ahead` and the unrelated-branch check don't ask whether the clone is shallow (UNTRACKED CHANGE and RULE NOT SEEN do).
Guardrail: from a cutoff (via 084's rule-seen gate) require ` in <s>s` in the I2 field or make "not computable" INCOMPLETE; keep D's order check inside a send-back round from the send-back line on; depth-1 fixture asserting all three lines say `not checked (shallow clone; run git fetch --unshallow)`.
## Recurring issue link (RI-#, if any)
RI-010 (ESCALATED), RI-014. Found by A1 probes before merge; near miss, not counted.
## Done looks like
Untimed batch fixture past the cutoff is flagged; depth-1 fixture prints the three not-checked lines; mutations fail named tests.
