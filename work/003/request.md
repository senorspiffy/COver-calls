# Work item 003
Type: BUG
Opened by: A1
Date: 2026-10-30

## What we want
Make the 50% early-exit rule say how to price the order, and make the worked example obey the rule.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `work/001/03-handoff.md` step 6: exit if "the call is worth ≤ 50% of what you sold it for", via a "GTC limit buy-to-close at 50%".
- Worked example: sold at $0.47; "GTC fills at $0.24". 50% of $0.47 = $0.235, and $0.24 / $0.47 = **51.1%**, which is above 50%, so the example's exit does not meet its own trigger.
- $0.235 is not a valid limit price (options trade in $0.01 or $0.05 ticks), so the rule as written cannot be entered without a rounding choice, and the doc doesn't make one.

## Root cause and prevention guardrail (BUG only)
Root cause: the rule was stated as a percentage with no tick-size rounding, and the worked example was written from a plausible quote rather than computed from the rule. Nothing asks R3 to check that each worked example satisfies the trigger of the rule it illustrates.
Guardrail: (1) state the rule as "limit = 50% of the sale price, rounded **down** to the option's tick" so the exit is always ≤ 50%; (2) the hand-off "Self-check" section (see 002) must show each worked example passing its rule's trigger.

## Recurring issue link (RI-#, if any)
RI-001 (occurrence 2)

## Done looks like
Step 6 defines the rounding; the worked example uses a limit of $0.23 (0.235 rounded down) with the profit recomputed: (0.47 − 0.23) × 100 − $0.20 = $23.80.
