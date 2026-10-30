# Work item 016
Type: EFFICIENCY
Opened by: A1
Date: 2026-10-30

## What we want
Two person-facing texts should say exactly what they mean:
1. For an ETF, the daily report shows "Days to earnings: none (ETF)" instead of "n/a".
2. The 001 correction pointer and section header name item 005 as well, since the section's step 3 bullet comes from 005.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- A1's scan on 2026-10-30 (scratch) wrote `daily_2026-10-30.md` L27: "- Days to earnings: n/a; days to ex-dividend: 49" for SYNTH_A, an ETF. Since 005, "n/a" in these reports means "cannot be computed or not supplied". A stock with unknown earnings shows "n/a (not supplied)" and is blocked. The ETF line uses the same word for a known "none", which is the unknown/none mix-up that RI-002 is about, here in the text only. The cause is `report.py` L165–166, which calls `_days_to(None)` when `earnings_known` is True and there is no date.
- `work/001/03-handoff.md` L118 and L146 say "(items 003, 004, 008)". The section's "Step 3 (005)" bullet, the `OI_UNKNOWN`/`EARNINGS_UNKNOWN` rule, comes from 005. A reader who follows the item links misses where step 3 changed.

## Done looks like
For an ETF (or any ticker with known-none earnings), the daily report prints "none (ETF)", or "none in data", and a test asserts it. The 001 pointer and header read "(items 003, 004, 005, 008)". Only that label changes; the rest of 001 stays as written.
