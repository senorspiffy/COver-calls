# Work item 063
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-14

## What we want
The real-quote test (`ccbot/realtest.py`) must not read "no earnings date known yet" as "no earnings". The stretch from a stock's first data day to its first listed earnings date is a data hole, like a gap between dates: it gets a warning in `reports/real/` and, if a call's life could hold an unknown earnings date, the sale is blocked (`EARNINGS_UNKNOWN`) or at least flagged, never silent.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `ccbot/realtest.py` L183: `gaps = sum((b - a).days > EARNINGS_GAP_WARN for a, b in zip(earnings, earnings[1:]))` counts only gaps between consecutive dates. `_earnings_known` (L372-374) checks only that a date on or after d exists. Nothing checks the edge before the first date.
- First rows of `data/real/earnings/*.csv` (A1, 2026-11-14): BAC 2020-04-15, CSX 2020-04-22, USB 2020-04-15, VALE 2020-04-28; the others start in Jan-Feb 2020. The quote data starts 2020-01.
- 061 A1 audit (logs/audit/2026-11-14-061.md): BAC, CSX and USB each sold a 2020-01-06 call expiring 2020-02-21 (trades_*.csv), across their real Jan 2020 earnings, with no warning in `reports/`. Measured impact in 061: 247 vs 250 calls, no A-row change (labelled in 061/01 only).

## Root cause and prevention guardrail (BUG only)
Root cause: the 061 data-hole check (realtest 1.4) looks only between known dates, not at the edges of the data window, so missing history before the first date passes as "no earnings". It is a new input path (data/real/earnings) outside the MISSING_POLICY enumeration that guards the bot (RI-002).
Guardrail:
1. `realtest`: count the leading edge (data start to first earnings date > EARNINGS_GAP_WARN days, or no date in the first EARNINGS_GAP_WARN days) as a gap with its own warning, and treat days inside it as earnings unknown for the call's life (no silent sale).
2. Test: a fixture whose first earnings date is more than 120 days after its first snapshot gives a warning and no sale in the hole; the same fixture with the edge check removed fails the test.
3. r3/i3 text (or the I1 plan) names "edges of the data window" next to "gaps between dates" for any data-hole check.

## Recurring issue link (RI-#, if any)
RI-002 (was GUARDED), occurrence 10 → ESCALATED.

## Done looks like
Fixture test passes, and fails when the edge check is removed (mutation in 05/06). Suite green. 061's numbers are not re-published as a new result here; I2 states in 05 how the BAC/CSX/USB call counts change (expected about 247, as 061's `diag_keep.py earn` measured) so the person can see the effect.
