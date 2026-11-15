# Work item 065
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-15

## What we want
In the real-quote test (`ccbot/realtest.py`), a call whose life falls inside an interior earnings gap of more than EARNINGS_GAP_WARN (120) days is no longer sold silently. Inside such a hole the next report date is unknown, so the sale is blocked (`EARNINGS_UNKNOWN`) or clearly labelled per trade; R1/I1 decide which, and say which in 05 so the person sees it.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `ccbot/realtest.py` (branch daily-fixes/2026-11-14, PR #28) L185-187: interior gaps > 120 d only add a warning. `_earnings_known` (L376-379) returns True whenever a listed date lies on or before and on or after d, so a day inside a 6-month hole is "known" and `_earnings_between` sees no date, so the call sells.
- Interior gaps > 120 d in `data/real/earnings/*.csv` (A1, 2026-11-15): CMCSA, MO, T 2021-10/2022-04 (182 d); MDLZ 2021-11-02→2022-04-26 (175 d); VZ 2021-10-20→2022-04-22 (184 d); ITUB 2 gaps; VALE 4 gaps; PBR 7 gaps (up to 246 d). Real companies report quarterly, so each hole hides at least one report.
- logs/audit/2026-11-15-063.md L65-67: A1 agreed it should be a follow-up ("realtest interior earnings gaps > 120 d still sell; decide block vs label") for this daily review to open. 063/04 put it out of scope.

## Root cause and prevention guardrail (BUG only)
Root cause: the data-hole check counts holes but does not feed them into the earnings decision; "a date exists on each side" is used as proof that nothing lies in between. Same root cause as RI-002 occurrence 10 (missing data read as "no earnings"); 063 fixed only the leading edge.
Guardrail:
1. `realtest`: days whose call life overlaps an interior gap > EARNINGS_GAP_WARN are earnings-unknown (block or labelled, per R1/I1), counted in the per-stock counts.
2. Test: a fixture with a 180-day interior gap gives no silent sale inside the hole; with the interior check removed the test fails (mutation in 05/06). Also cover the trailing edge (after the last listed date) if 063 does not already.
3. One shared helper decides "earnings known" for leading edge, interior gap and trailing edge, so a future data-hole check cannot cover one edge only.

## Recurring issue link (RI-#, if any)
RI-002, same occurrence as 10 (remainder of 063's scope; not a new count).

## Done looks like
Fixture test passes and fails with the interior check removed. Suite green. 05 states how the call counts change for CMCSA, MDLZ, MO, T, VZ, ITUB, VALE, PBR (with data/real present) without re-publishing 061's result. Built on top of daily-fixes/2026-11-14 (RULES BRANCH, and it changes the same file).
