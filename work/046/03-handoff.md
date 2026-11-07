# 03 Research hand-off - 046
Status: READY
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| TICKER_FIELDS has 3 keys | ccbot/tickers.py L23 | VERIFIED |  |
| enrich reads asset_type, last_earnings too | `grep -o 'f\(\.get(\|\[\)"[a-z_]*"' ccbot/tickers.py` | VERIFIED |  |
| tickers.json keys | config/tickers.json | VERIFIED |  |
| sources not read by code | grep ccbot/ | VERIFIED |  |
| foo_date probe → 20 passed | A1 scratch run 2026-11-05 | VERIFIED |  |
| no asset_type → "stock" | ccbot/rules.py L81, L296 | VERIFIED |  |
| no last/next earnings → unknown | drop_tickers_next_earnings | VERIFIED |  |
**Totals:** 7 rows checked → **7 VERIFIED as-is**, **0 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None.
## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | `TICKER_FIELDS` += `asset_type`, `last_earnings`; `TICKER_NOTES = ("sources",)` (not an input) | – | tuple | step 3 | – |
| 2 | MISSING_POLICY rows `tickers.asset_type` (fallback: the broker's asset type, default "stock", so earnings must be known) and `tickers.last_earnings` (block: no estimate; EARNINGS_UNKNOWN when next_earnings is null too); drop tests | – | policy rows | test_drop_each_input[tickers.asset_type], [tickers.last_earnings] | – |
| 3 | `test_ticker_fields_cover_file_and_code`: keys of every config/tickers.json entry ∪ keys matched by `f\.get\("(\w+)"` / `f\["(\w+)"\]` in ccbot/tickers.py, minus TICKER_NOTES, ⊆ TICKER_FIELDS; the code set is non-empty | file, code | assertion | mutation: `foo_date` in the file → fails; a new `f.get("x")` → fails | 5 keys found (file 5 + sources, code 5) |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| tickers.asset_type | null/missing | Day's asset type (default "stock"): a stock needs known earnings, else EARNINGS_UNKNOWN |
| tickers.last_earnings | null/missing | no estimate; with no next_earnings → EARNINGS_UNKNOWN |
## Self-check
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| keys covered | {file keys} ∪ {code keys} − {sources} ⊆ TICKER_FIELDS | {asset_type, next_earnings, last_earnings, ex_div_date, dividend} ⊆ 5-tuple | ✓ |
| probe fails | foo_date ∉ TICKER_FIELDS | 1 extra key | ✓ test fails |
| Totals | 7+0+0 = 7 | 7 | ✓ |
Recurring issues checked (R3): RI-002 (its guardrail; both new rows fail safe, never 0 or a pass), RI-007, RI-009, RI-010 (each step logged when it ran).

`python3 scripts/check_handoff.py 046` output:
sources count (unique URLs in 01-research.md): 0
fact-check rows: 7
totals line: 7 rows -> 7 as-is, 0 fixed, 0 removed
PASS
