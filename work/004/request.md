# Work item 004
Type: BUG
Opened by: A1
Date: 2026-10-30
Against: 001 (`work/001/03-handoff.md` steps 4 and 5), 002/03 step 6, 002/04 `test_calendar` row.

## What we want
Make 001's expiry and strike rules feasible, and make them agree with the 002 bot. Today the person's written rules and the bot disagree.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- 001 step 4: "Sell the monthly expiry 30–45 DTE … Log DTE at entry: must be 30–45". 002/03 step 6 and 002/04 both say "30–45 DTE is always found for monthly (gap ≤ 35 days)". That is false. A1 ran `expiries.pick_expiry` over 2016–2025 business days: a monthly is inside 30–45 DTE on **55.2%** of days (95.2% with the ±7-day slack). On 2026-10-30 there is none (strict → `None`).
- 002 handled it in code only: `monthly_slack_days: 7` (05 deviation 2). Today's paper scan sells `SYNTH_A261218C00026000` at **49 DTE** (`in_window=False`), which breaks 001 step 4's check.
- 001 step 5: "strike nearest 0.25–0.30 delta … Log delta (0.25–0.30)". 002/04 research 1 shows about 0.10Δ per $0.50 strike near $24 at 35 DTE, so the 0.05-wide band often has no listed strike. The code trades [0.20, 0.35] and logs `in_band` (04 change 3). 001 is not updated.
- 002/04 also claimed "Weekly picks 5–9 DTE on every Monday". A1 checked: 0 of 522 Mondays (fixed by I2, 05 deviation 3).

## Root cause and prevention guardrail (BUG only)
Root cause: the DTE and delta windows were set without computing how often they contain a listed expiry or strike. The claim "always found" was copied from R3 to I1 without being checked. The code was then patched (slack, tolerance), but 001, the person's rulebook, was not.
Guardrail:
1. The same feasibility field as 003, applied to time and strike windows: coverage % over a real calendar/strike grid, stated in 03.
2. A test that pins it: `test_calendar` asserts the strict coverage (< 70%) and the slack coverage (> 94%); it is already in `tests/test_calendar.py`. Keep it, and cite it in 001.
3. Rule: when 002-type code changes a 001 rule (slack, tolerance), the same item updates 001's text, or opens a request to do so. I3 checks for this.

## Recurring issue link (RI-#, if any)
RI-001.

## Done looks like
001 steps 4 and 5 state the rule the bot uses (or the bot is changed back), including what to do when no monthly is in 30–45 DTE and when no strike is in 0.25–0.30Δ. Each check column matches the bot's `in_window`/`in_band` logging.
