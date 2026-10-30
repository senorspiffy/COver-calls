# 02 Improvements - 004
## What past logs say
- RI-001 ESCALATED. Three of its four occurrences are this item's windows: "30–45 DTE always found" (A1: 55.2% of days), the 0.25–0.30Δ band, and "5–9 DTE every Monday" (0 of 522).
- 002 patched the code only (`monthly_slack_days: 7`, tolerance [0.20, 0.35]). 001 still says 30–45 / 0.25–0.30. Today's paper trade is 49 DTE, `in_window=False`.
- `tests/test_calendar.py` already asserts strict coverage < 70% and slack coverage > 94%.

## 3 ways FOR
1. **"Monthly nearest 35 DTE, within 21–56" has a candidate on every day (R1 measured 2,514 of 2,514 NYSE sessions, 2016–2025).** It also gives the same expiry the bot traded today (2026-12-18, 49 DTE). It is the "nearest X" pattern used by the covered-call benchmarks: BXM sells the next one-month call (004/01 F2), and the Nikkei 225 covered-call index sells 「直近限月」, the nearest month (003 language table, Japanese). A selector that always has a candidate removes the RI-001 failure mode for this rule.
2. **A ~35 DTE target stays inside the sourced ranges.** tastylive targets 25–50 DTE (004/01 F1). The Montréal Exchange guide recommends 30–45 days because "Theta decays the value of an option faster in shorter dated options" (003 table, English). So the person keeps 001's evidence base, and only the edges change.
3. **Step 5 should state what the code does (nearest 0.275Δ, accept [0.20, 0.35], else `NO_STRIKE_IN_TOLERANCE`, log `in_band`).** This is the simplest fix: the code is unchanged, the rulebook is corrected, and each check column maps to an existing log field.

## 3 ways AGAINST
1. **The 21–56 limits let through DTEs far from the evidence.** The lower limit binds when one monthly is just under 21 DTE. The rule then picks the next monthly at 55–56 DTE, which is above tastylive's 50 and BXM's ~28–35. At the other end it can pick 21 DTE (when the alternative is 56), which sits in the faster-gamma zone that 001 C1 warns about. Measured share of days with DTE < 25 or > 50: not computed. R3 should compute it and print it next to the 100%.
2. **"100%" is proven only on 2016–2025.** The argument is that a 35-day window covers a ≤ 35-day gap, but a holiday move can make a 36-day gap (004/01 F4). R1 says it held anyway, but beyond 2025 it is not proven. The code must still handle `None` (fail-safe `NO_EXPIRY`), not assume it never happens. Otherwise the "always" claim gets written down without a test, which is RI-001 again.
3. **A simpler alternative exists: keep the code and write it into 001** (30–45 ± 7 = 23–52, 95.2%, "no trade that day" otherwise). It needs no code change and no new config keys, and it keeps closer to the 30–45 evidence. Its cost is about 1 in 20 days with no candidate. That costs nothing if the bot simply retries the next day. **Recommendation:** either option closes the bug. The nearest-35 change is worth making only if the person values "never skip". Both need 001 updated in the same item (request guardrail 3).

## Findings by language
Combined 7-language search for 003–008: see `work/003/02-improvements.md` § Findings by language (random: Arabic, Hindi, Turkish). Relevant here: English (Montréal Exchange 30–45 days, theta) and Japanese (Nikkei CC index sells the nearest month).

## Holes to watch out for (summary)
- The bot's `pick_expiry` is used for both monthly and weekly. Changing the monthly rule must not change V2's weekly logic, and that needs its own test.
- Ties go to the later expiry (today 21 vs 49 → 49). Say so in 001, or the person will expect 21.
- The delta tolerance can still miss when strikes are 0.16Δ apart (S = $12, σ 25%, 004/01). `NO_STRIKE_IN_TOLERANCE` days should be counted in the report, like the DTE coverage.
- Add a coverage test for the new rule (100% on 2016–2025) and cite the test name in 001. That is the RI-001 guardrail in executable form.
