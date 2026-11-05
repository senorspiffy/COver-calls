# 03 Research hand-off - 041
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| enrich turns a past ex-date into 0.0 | A1 probe + tickers.py L48–52 | VERIFIED |  |
| earnings has a stale guard, ex-date doesn't | tickers.py L44–52 | VERIFIED |  |
| policy: 0.0 only for a known, not-next ex-date | missing.py broker.div_next | VERIFIED |  |
| Ford's next ex-date unpublished | businesswire release 2026-10-28 | VERIFIED |  |
| early-assign check needs div_next>0 or future ex-date | rules.py L209–219 | VERIFIED |  |
| enumeration test misses tickers.json | test_missing_inputs.py L198–201 | VERIFIED |  |
**Totals:** 6 rows checked → **6 VERIFIED as-is**, **0 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | `enrich`: `ex_div < day.date` → ex_div_date None, dividend/div_next stay NaN | tickers.json, day.date | Day fields | test_enrich_past_ex_div_is_unknown | F: 1 stale case on 2026-11-20 (probe) |
| 2 | `tickers.TICKER_FIELDS`; MISSING_POLICY rows `tickers.next_earnings`, `tickers.ex_div_date`, `tickers.dividend`; `snapshot.next_earnings` text names 040's estimate | – | policy | test_policy_lists_every_optional_input | 3 keys |
| 3 | drop tests for the 3 rows (incl. stale ex-date) | – | tests | test_drop_each_input[tickers.*] | 3 |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| tickers.ex_div_date past | stale | date None, dividend/div_next NaN; report 'n/a (not supplied)' |
| tickers.dividend null | absent | dividend/div_next NaN |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| stale ex-date | 2026-11-10 < 2026-11-20 | true → unknown | ✓ |
| Totals | 6+0+0=6 | 6 | ✓ |
Recurring issues checked (R3): RI-002, RI-007, RI-009, RI-010.
