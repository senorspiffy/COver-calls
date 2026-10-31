# 03 Research hand-off - 008
Status: READY

Checked 2026-10-30 by R3. Tick sizes were checked against Cboe's notice C2023122104 and the SEC filing 34-105045. Limit-order behaviour was checked against SEC Investor.gov.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| F1: Penny classes quote "$0.01 for series trading below $3.00 and $0.05 for series trading at or above $3.00"; non-Penny "$0.05 … below $3.00 and $0.10 … at or above $3.00"; effective Jan 2, 2024; ref C2023122104 | cdn.cboe.com PDF (fetched) | VERIFIED | – |
| F2: Cboe Rule 5.4(d); "the 300 most actively traded multiply listed options"; "December 2026 rebalancing" | SEC 34-105045 (fetched) | VERIFIED (the phrases appear in footnotes 18 and 28 and in §III.A) | – |
| F3: whether F/SOFI/KWEB are penny classes | – | UNVERIFIED (kept open). The example is labelled "penny class" | – |
| F4: "A limit order is an order to buy or sell a security at a specific price." "A buy limit order can only be executed at the limit price or lower" | investor.gov (fetched) | VERIFIED | – |
| F5: a $0.23 buy against a $0.24 ask does not fill on that quote; price improvement is possible but not guaranteed | follows from F4; frequency UNVERIFIED | VERIFIED for "does not fill on that quote"; the frequency was not used | – |
| 50% of $0.47 = $0.235; highest cent ≤ that = $0.23 = 48.9%; $0.24 = 51.1% | math | VERIFIED (48.94%, 51.06%) | – |
| Non-penny: $0.47 is not a valid price; $0.45 → $0.20, $0.50 → $0.25 | math | VERIFIED | – |
| Corrected P/L: (0.47 − 0.23) × 100 − $0.20 = $23.80 | math | VERIFIED (2 fills × $0.10 placeholder, as in 001) | – |
| `rules.py` L244: `quote.ask > 0.5 * o.premium` → no exit; at 0.24 > 0.235 there is no exit | code | VERIFIED | – |
| 001 worked example (001/03 L141): "GTC fills at $0.24 … $22.80" | doc | VERIFIED as the bug | Step 1 |
| **New:** 001 step 6 (L125) "within the first third of its life (e.g. day ≤ 12 of 35)" | `rules.py` L240–242: no exit if `days_held × 3 > life` | **WRONG** (the same RI-004 pattern) | 12 × 3 = 36 > 35, so the bot does **not** allow day 12. The last allowed day is **11** (35/3 = 11.67). Day 9 in the example is fine (27 ≤ 35) |

## Removed claims
- None. One new error was found and fixed (step 6 "day ≤ 12").

## Decision
- Fix the example and keep the code. Follow R2 FOR 1 and FOR 3; skip `floor_to_tick` (R2 AGAINST 1). For a penny class, `ask ≤ 0.235` is the same as `ask ≤ 0.23`. No candidate has been shown to be non-penny.
- Merge the R3 instruction line with RI-001's feasibility line into one R3 step (R2 AGAINST 3). The text is in 003/03 step 5(b).

## Implementation map
| Step | Change | Inputs | Outputs | How we check it |
|---|---|---|---|---|
| 1 | **Docs: replace 001/03 L141** with: "50% exception (a **penny-class** option: $0.01 tick below $3, Cboe C2023122104). 50% of $0.47 = $0.235, so the GTC buy-to-close limit is **$0.23** (48.9%, the highest whole cent ≤ 50%). On day 9 the call is $0.21 bid / $0.23 ask, so the $0.23 limit fills at $0.23. Profit (0.47 − 0.23) × 100 − $0.20 = **$23.80**; sell next month's call the same day. On a $0.22 / $0.24 quote the limit would **not** fill (a buy limit executes only at the limit or lower, SEC Investor.gov), and the bot (`ask ≤ 0.5 × premium`) would not exit either. A fill at the limit is never guaranteed. In a non-penny class ($0.05 tick below $3) the sale would be $0.45 or $0.50 and the limit $0.20 or $0.25." | 001/03 | edited 001 | Each price is on the $0.01 tick; $0.23 ≤ $0.235; P/L recomputes to $23.80 |
| 2 | **Docs: 001/03 step 6 (L125):** "(e.g. day ≤ 12 of 35)" → "(days held × 3 ≤ days of life; e.g. day ≤ 11 of 35, as the bot checks)". "GTC limit buy-to-close at 50%" → "GTC limit buy-to-close at 50% of the sale price, rounded **down** to the tick". | 001/03; `rules.py` L240–244 | edited 001 | The text matches the code |
| 3 | **Guardrail test (BUG, RI-004):** `tests/test_backtest.py::test_worked_example_50pct_exit` (or `test_variants.py`). Use V1, a call sold at $0.47 on day 0 with 35 days of life, and a stub market. Ask $0.23 on day 9 → `BUY_TO_CLOSE` at $0.23. Ask $0.24 on day 9 → `HAS_POSITION`. Ask $0.23 on day 12 → `HAS_POSITION`. Ask $0.23 on day 11 → `BUY_TO_CLOSE`. | `rules.decide_exit` | test | Passes on today's code. It pins that 001's example and the bot agree |
| 4 | **Guardrail (process, RI-004):** the merged R3 line in `.claude/agents/r3-fact-checker.md` step 1 (text in 003/03 step 5(b)). It needs the person's OK; coordinate with 013. A1 then sets RI-004 to GUARDED. | – | agent file | Re-read the file |
