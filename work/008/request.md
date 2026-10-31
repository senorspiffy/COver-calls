# Work item 008
Type: BUG
Opened by: A1
Date: 2026-10-30
Against: 001 (`work/001/03-handoff.md`, worked example, "50% exception" line).

## What we want
Fix the worked example so that it obeys the 50% buy-back rule it illustrates.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- 001 step 6: buy back "if the call is worth ≤ 50% of what you sold it for", via a "GTC limit buy-to-close at 50%". The example sold at $0.47, so 50% = $0.235. A buy limit on the $0.01 tick at or below 50% is $0.23. The example then says the "GTC fills at $0.24" (bid 0.22 / ask 0.24), which is **51.1%** and would not fill at a $0.23 limit.
- The 002 code implements the rule as `ask ≤ 0.5 × premium` (`ccbot/rules.py` L244), so V1 would not trigger on that quote either. The example and the bot disagree.
- R3 checked the arithmetic ($22.80) but not whether the example meets the rule.

## Root cause and prevention guardrail (BUG only)
Root cause: worked examples are checked for arithmetic only, not against the rule they illustrate. Guardrail: add a line to `.claude/agents/r3-fact-checker.md` step 1: "For each worked example, also check that every step meets the rule it shows (thresholds, tick size, limits)."

## Recurring issue link (RI-#, if any)
RI-004 (new).

## Done looks like
The example uses a $0.23 limit and a quote that fills it (or states "would not fill"), and the P/L is recomputed. The R3 instructions carry the check.
