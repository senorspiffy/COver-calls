# 02 Improvements - 014
## What past logs say
See `logs/audit/2026-10-31.md` and `logs/recurring-issues.md` (RI-002 occ 5–6).
## 3 ways FOR
1. Unknown dividends are visible as events on the exact days they matter.
2. NaN capital can't pass a cap.
3. New Day fields with silent defaults fail a test.
## 3 ways AGAINST
1. Without an amount, the sim can't simulate early assignment; it only flags it.
2. q = 0 stays a labelled fallback for model marks.
3. More event types in the paper log.
## Findings by language
Languages: N/A (no new external claims). This fix changes code, counts, wording or process inside this repo only, so no outside source in any language could confirm or contradict it.
## Holes to watch out for (summary)
See AGAINST list.
