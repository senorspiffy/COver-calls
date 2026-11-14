# 03 Research hand-off - 060
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| F1 B5 rule is a 20-day high | work/057/01, work/058/request.md | VERIFIED |  |
| F2 `_dip` counts scans | ccbot/bot.py `_dip` | VERIFIED |  |
| F3 scans get missed | project notes (VPS reboot 2026-11-12) | UNSUPPORTED | kept only as the reason; labelled "project notes", no number depends on it |
| F4 calendar exists | ccbot/expiries.py, config/holidays.json | VERIFIED |  |
**Totals:** 4 rows checked → **3 VERIFIED as-is**, **1 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | `_dip`: window = last `lookback` NYSE trading days ending today (`expiries.business_days` + holidays.json); past closes kept only if `ts` is in the window and before today | paper_snapshots.csv, date | closes list | new test_missed_scans_do_not_stretch_the_window; existing 058 tests | 251 of 251 trading days in 2026 give a full 20-day window (business_days over date−50 cal. days; command in 03 Self-check) |
| 2 | `min_days` still counts recorded closes in that window | closes | NO_DIP with count | test_no_dip_rule_until_enough_history (existing) | – |
| 3 | dip_reserve.json `_about`: "20-trading-day high" | – | – | test_budget_accounts_match_the_057_versions | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| paper_snapshots.csv rows in the window | fewer than min_days | NO_DIP "<n> of <min_days> closes recorded; dip rule not ready" |
| date outside holidays.json | – | run_daily raises at `broker.calendar(date)` before `_dip` |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Window 2026-10-30 | business_days(10-05..10-30) | 20 weekdays, no NYSE holiday | 20 ✓ |
| Window 2026-11-30 | business_days(11-02..11-30) − Thanksgiving 11-26 | 21 − 1 | 20 ✓ |
| Totals | 3+1+0 | 4 | ✓ |
Feasibility command: `python3 -c "...business_days(d-50d, d, holidays)[-20:]..."` over 2026 → `251 251`.
`python3 scripts/check_handoff.py 060` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 0
fact-check rows: 4
totals line: 4 rows -> 3 as-is, 1 fixed, 0 removed
PASS
```
Recurring issues checked (R3): RI-001 (window count computed: 251/251), RI-002 (thin window blocks, never passes), RI-012 (no text matching).
