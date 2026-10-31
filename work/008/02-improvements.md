# 02 Improvements - 008
## What past logs say
- RI-004 (new, 1). A1 confirmed the 001 math is right; the error is the rule, not the arithmetic. V1 (`rules.py` L244: `quote.ask > 0.5 * o.premium` → no exit) agrees that $0.24 would not fill.

## 3 ways FOR
1. **Fix the example to a $0.23 limit with a quote that fills (bid $0.21 / ask $0.23 → P/L $23.80), and add the line "on $0.22/$0.24 it would not fill".** This is the simplest fix that closes the bug, and it teaches both cases. The math: (0.47 − 0.23) × 100 − 0.20 = $23.80 (008/01).
2. **State the tick size in the example.** In a penny class the tick is $0.01 below $3 (Cboe, 008/01 F1). The R3 check is then concrete: each price is on the tick, and each threshold is met after rounding.
3. **Make the guardrail executable: a unit test that runs `decide_exit` on the worked example's numbers (R1).** That is stronger than an R3 instruction line alone. The same lesson came from 002: behaviour tests held, while docs rules did not (RI-001/002 history). Keep the R3 line as well, because examples in 001 have no code of their own.

## 3 ways AGAINST
1. **`floor_to_tick` in code is scope creep for this bug.** For a penny class, `ask ≤ 0.235` and `ask ≤ 0.23` behave the same (008/01). It only matters for $0.05-tick classes, and no candidate has been shown to be one (F3 UNVERIFIED). Defer it to a separate item unless a non-penny ticker enters the universe.
2. **A hypothetical "fills at $0.23" quote can mislead in the other direction.** On thin names the ask may sit at $0.24 for days. The example should say the fill is not guaranteed (008/01 F5, UNVERIFIED frequency). Otherwise it suggests the 50% exit fires reliably.
3. **The R3 instruction line overlaps RI-001's feasibility check.** Both ask whether a rule's condition can actually be met with real prices and grids. Two separate lines in r3-fact-checker.md risk drift. Better as one R3 step: "for every rule, compute that it can be met (feasibility count) and that each example meets it (tick, thresholds)."

## Findings by language
See `work/003/02-improvements.md` § Findings by language (random: Arabic, Hindi, Turkish). No language source was specific to buy-back limits or tick rounding.

## Holes to watch out for (summary)
- The penny-class status of F, SOFI and KWEB is UNVERIFIED. It decides whether $0.47 is even a valid sale price ($0.05 tick → $0.45/$0.50).
- Update the example's day count/annualised figures if they are quoted elsewhere in 001.
- Webull's handling of an off-tick limit (reject or round) is UNVERIFIED. The bot should send prices already on the tick.
