# 01 Research brief - 008
## Question
What tick sizes apply to a sub-$3 option, how does a buy-to-close limit order fill, and what should 001's 50% buy-back example say?

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- F1. Penny Interval Program classes quote in "$0.01 for series trading below $3.00 and $0.05 for series trading at or above $3.00". Non-penny classes quote in "$0.05 for series trading below $3.00 and $0.10 for series trading at or above $3.00". (Cboe notice, effective Jan 2, 2024, ref C2023122104) [https://cdn.cboe.com/resources/product_update/2023/Penny-Interval-Program-Annual-Review-and-Rebalancing.pdf]
- F2. The program is in Cboe Rule 5.4(d). Eligibility depends on volume rank among multiply listed classes, for example "the 300 most actively traded multiply listed options", and classes are reassessed at rebalancing, for example the "December 2026 rebalancing". [https://www.sec.gov/files/rules/sro/cboe/2026/34-105045.pdf]
- F3. Whether a given ticker (SOFI, F, KWEB …) is in the program today: UNVERIFIED. Check each ticker against the current Cboe Penny class list.
- F4. SEC/Investor.gov: "A limit order is an order to buy or sell a security at a specific price." "A buy limit order can only be executed at the limit price or lower." [https://www.investor.gov/introduction-investing/investing-basics/glossary/limit-orders]
- F5. A resting buy limit below the displayed ask fills only if a seller trades at or below the limit. A $0.23 buy against a $0.24 ask does not fill on that quote. Fills inside the spread (price improvement) happen but are not guaranteed. UNVERIFIED (no source fetched for frequency).

## Numbers used (show the math)
- Rule: buy back if the call is worth ≤ 50% of the sale price. Sale $0.47 → 0.5 × 0.47 = $0.235.
- Penny class (F1, < $3): valid prices are whole cents. The highest limit at or below 50% is **$0.23**, which is 48.9% of $0.47. The example's $0.24 = 51.1% breaks the rule.
- Non-penny class (F1, < $3, $0.05 tick): $0.47 itself is not a valid price. The sale would be $0.45 or $0.50, and the 50% limit rounds down to $0.20 ($0.45 → 0.225 → 0.20; $0.50 → 0.25 → 0.25).
- Corrected example (penny class, hypothetical quote): day 9, bid $0.21 / ask $0.23. The GTC limit at $0.23 fills at $0.23. Profit (0.47 − 0.23) × 100 − $0.20 fees (two fills × $0.10 placeholder) = $24.00 − $0.20 = **$23.80**.
- Alternative wording: on the original quote ($0.22 / $0.24) the $0.23 limit **does not fill**. V1's check `ask ≤ 0.5 × premium` gives 0.24 > 0.235, so no exit, which agrees.
- Code note: `rules.py` L244 compares the ask with an unrounded 0.235. For a penny class that is the same as ask ≤ $0.23. A tick-aware `floor_to_tick(0.5 × premium, tick)` would make the limit price explicit and handle $0.05-tick classes.

## Fit for a ~$3k account
- Small premiums ($0.20–$0.50) make each tick 2–5% of the premium, so rounding decides whether a rule fires. Prefer penny-class underlyings ($0.01 tick); a $0.05 tick makes the 50% exit coarse.
- Guardrail (RI-004): the R3 instruction line from the request, plus "state the tick size used". For examples in code: a unit test that runs `decide_exit` on the worked example's numbers.

## Open questions
- Which candidate tickers are penny classes (F3)?
- Does Webull reject a limit price off the tick, or round it? UNVERIFIED.
