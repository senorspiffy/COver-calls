# 04 Build plan - 065
Fit verdict: FIT WITH CHANGES

Reviewed 2026-11-15 on branch daily-fixes/2026-11-15 (working tree carries 063's code; repo read only; no code changed, nothing committed; item 066 is in progress in the same tree, tests/test_pipeline_check.py and work/066/, and is not touched here). The prototype below ran in memory, with `rt._earnings_known` monkeypatched on the imported module, and no file was written. No brokerage contacted. Research, not financial advice.

Inputs read: work/065/request.md, 01-research.md, 02-improvements.md, 03-handoff.md (READY; `check_handoff.py 065` PASS pasted in 03), work/063/04-build-plan.md, logs/recurring-issues.md, ccbot/realtest.py, tests/test_realtest.py, work/061/diag_keep.py, pyproject.toml.

**Decision restated (for the person): block.** A stock day strictly inside an interior gap of more than EARNINGS_GAP_WARN (120) days between listed earnings dates is EARNINGS_UNKNOWN, so no call is sold that day. No label-only option and no cadence estimate (03 § Decision). I2 restates this in 05.

## Fit check
- **~$3k account:** fits. Only the research backtest changes (realtest uses fractional shares; MO/MDLZ lots are $5,009+ > $3,000, 03 Self-check). The live bot (rules, screen, missing, MISSING_POLICY) is not touched.
- **Strategy rules (001):** no rule the person follows changes. No slack, tolerance or cap is changed, so no 001 text edit and no new request is needed.
- **Existing code:** no conflict. `_earnings_known` has one caller (L497). work/061/diag_keep.py monkeypatches `rt._earnings_known`, so the sale path keeps calling `_earnings_known` for the decision (change 4). `bisect` is stdlib (requires-python >= 3.10, RI-008).
- **Changes to R3's map (why "WITH CHANGES"):**
  1. **REAL_BAC pins do change (03 step 5 says "no change").** `test_real_counts_bac` asserts `got == REAL_BAC[rule]` on the whole counts dict (tests L475-477), and for BOT_RULE `all(v > 0 for k, v in got.items() if k not in INFO)` (L480-481). A new `earnings_gap_days` key fails all 3 params, and BAC's real value is 0 (measured, below), which fails the `> 0` check. Plan: add `earnings_gap_days=0` to each of the 3 REAL_BAC dicts, and add `"earnings_gap_days"` to `INFO`, with a comment saying it is a data-hole count, not a window rule (RI-001's "every window rule has candidates" applies to window rules). This adds a key and keeps every existing value, so nothing is loosened. I3 checks the diff.
  2. **The warning gate must not read `td.earnings_gaps`.** `_tiny` builds TickerData with `earnings_gaps=0` hard-coded (tests L212-213). If simulate warns only "when `td.earnings_gaps > 0`" (03 step 2), T-gap180's warning assert fails even on correct code. Plan: one pure helper `_gap_pairs(earnings)` → list of `(a, b)` with `(b - a).days > EARNINGS_GAP_WARN`. load_ticker sets `gaps = len(_gap_pairs(earnings))` (same count and meaning as L185), and simulate builds its warning from `_gap_pairs(td.earnings)`. `_earnings_state` uses the same comparison, through a one-line `_is_gap(a, b)` that `_gap_pairs` also calls. Then "warned" ⇔ "blocked" holds by construction (03 step 3's intent), and `EARNINGS_GAP_WARN` is read only in `_is_gap`.
  3. **NaN `earnings_gap_days` in summary.json.** `run` writes summary.json with `json.dumps(..., default=str)`, which writes NaN as the bare token `NaN` (checked here: `json.dumps({'x': float('nan')})` → `{"x": NaN}`). 063 fixed this for `earnings_lead_days` only (L764-766). Plan: the same NaN → `null` conversion loops over both keys. The test at L315-321 (stock with 0 earnings rows) adds `s["counts_bot_rule_bid"]["AAA"]["earnings_gap_days"] is None`; `_no_nan` already makes a bare NaN fail the parse. No change to the L761 key tuple is needed: `*df.attrs["counts"]` already carries the new key into summary.json and grid_in_sample.csv.
  4. **How simulate gets the count.** The decision stays `not _earnings_known(td, d)` (diag_keep.py compatibility). Only when that is False, simulate calls `_earnings_state(td, d) == "interior_gap"` to add 1 to the count. `_earnings_known(td, d)` is `_earnings_state(td, d) == "known"`.
  5. **`earnings_gap_days` under a rule that skips the earnings check (`skip_earnings=False`).** 03 does not say. Plan: it counts attempts that were blocked, so it is 0 for such a rule when the stock has dates (nothing is blocked), and the warning says "earnings not checked by this rule". It is NaN for an ETF or a stock with no dates under any rule, as `earnings_lead_days` is. T-gap-noE pins it at 0, with `rej_EARNINGS_UNKNOWN == 0`.
  6. **Real-data pin added (RI-001).** 03's fixture tests pin the 120/121 bar, but no test pins the dated real-data count. BAC has no gap. Plan: a new test `test_real_interior_gap_mo` on committed data/real (MO, BOT_RULE, start 2020-01-01): `calls_sold == 21`, `earnings_gap_days == 71`, and no trade with `open_date` strictly inside (2021-10-28, 2022-04-28). I measured these values (below); I2 re-measures them and pastes the output in 05.

## Extra research (with sources)
1. **`bisect_right` semantics fit the helper.** "The returned insertion point ip partitions the array a into two slices such that all(elem <= x for elem in a[lo : ip]) is true and all(elem > x for elem in a[ip : hi]) is true" [https://docs.python.org/3/library/bisect.html, `bisect.bisect_right`]. So with `i = bisect_right(td.earnings, d)`, `td.earnings[i-1] <= d < td.earnings[i]`, and the order in 03 step 1 (i == 0 → before_first; `earnings[i-1] == d` → known; i == len → after_last; gap check) is complete. A listed date equal to d is checked before after_last, so d == the last date stays known, the same as today's `td.earnings[-1] >= d`. The precondition is a sorted list: load_ticker builds `sorted(set(...))` (L184), and `_tiny` calls `sorted(earnings)`.
2. **JSON and NaN.** Python's `json` docs say the NaN output "is not JSON specification compliant" [https://docs.python.org/3/library/json.html, § Infinite and NaN Number Values]. RFC 8259 §6: "Numeric values that cannot be represented in the grammar below (such as Infinity and NaN) are not permitted" [https://www.rfc-editor.org/rfc/rfc8259#section-6]. Hence change 3.
3. **Prototype on committed data/real (I1, 2026-11-15).** This is the 03 step-1 helper, monkeypatched in memory as `_earnings_known`, with BOT_RULE, CFG from tests, start 2020-01-01. Output (old → new):
   - MO: calls 23 → 21; rej_EARNINGS_UNKNOWN 19 → 90; interior-gap blocks 71; sales opened inside the hole: 2022-01-19, 2022-02-23 → none.
   - MDLZ: calls 34 → 31; UNKNOWN 18 → 87; interior-gap blocks 69; in-hole sales 2021-11-03, 12-22, 2022-01-24, 02-23 → none. The 2022-04-27 sale is after the gap end, 2022-04-26.
   - BAC: 22 calls, 60 UNKNOWN, 0 gap blocks, unchanged. The REAL_BAC values stay, plus the new key (change 1).
   These match 03's expectations (MO 21, MDLZ 31, deltas +71 / +69).
4. **Edge case: the `_make` drop fixture.** `_make` earnings are the last trading day ≥ 25 of Jan/Apr/Jul/Oct, 2019-01 → 2022-03 (90-94 d apart, 03 F6). Dropping AAA's Apr and Jul 2020 rows leaves one gap of about 270 d (Jan 2020 → Oct 2020) inside the quote window, so the drop case has a non-empty blocked stretch and sale days after it.
5. **Simpler method checked: no new constant, no per-ticker bar.** The ADR near-bar intervals (VALE 120 not flagged; PBR 118/119 not, 126 flagged) stay a known limit. A per-ticker bar would be a cadence guess (RI-002 038/040). All three are skipped today (< 3.0 years of quotes).

## Files to create/change
1. **ccbot/realtest.py**
   - `import bisect` (stdlib).
   - Module docstring L18: add "or strictly inside a gap > EARNINGS_GAP_WARN days between listed dates (item 065)" to the EARNINGS_UNKNOWN sentence.
   - Comment on `EARNINGS_GAP_WARN` (L62): "days between consecutive listed earnings dates above which the stretch between them is a data hole: EARNINGS_UNKNOWN inside it (065)".
   - `REALTEST_MISSING`: add the row `"earnings_interior_gap": "EARNINGS_UNKNOWN strictly inside a gap > 120 days between listed earnings dates; warning with the gap dates"`.
   - New `_is_gap(a, b)`: `(b - a).days > EARNINGS_GAP_WARN`. New `_gap_pairs(earnings)`: `[(a, b) for a, b in zip(earnings, earnings[1:]) if _is_gap(a, b)]`.
   - `load_ticker` L185-187: `gaps = len(_gap_pairs(earnings))`. The warning text is unchanged.
   - New `_earnings_state(td, d)` → `"known" | "before_first" | "after_last" | "interior_gap"`, as in 03 step 1 (bisect_right; no dates → before_first). The docstring names all three edges and items 063/065.
   - `_earnings_known(td, d)` → `return _earnings_state(td, d) == "known"`. Docstring updated.
   - `simulate`: `earnings_gap_days` starts at 0 for a stock with dates, otherwise NaN (`td.asset_type == "etf" or not td.earnings`). At L497, when `not _earnings_known(td, d)` and the counter is not NaN, add `_earnings_state(td, d) == "interior_gap"`. After the lead warning, if `td.asset_type != "etf"` and `_gap_pairs(td.earnings)`, append `"earnings: gap(s) > 120 days between listed dates (<a>→<b>, ...); no call sold inside them (EARNINGS_UNKNOWN)"` when `rule.skip_earnings`, otherwise `"...; earnings not checked by this rule"`. Use f-strings with `EARNINGS_GAP_WARN` and `str(date)`. Add `"earnings_gap_days": earnings_gap_days` to `df.attrs["counts"]`.
   - `run` L764-766: loop `for k in ("earnings_lead_days", "earnings_gap_days")`, NaN → None (change 3).
2. **tests/test_realtest.py**
   - New: `test_interior_gap_180_blocks` (T-gap180), `test_interior_gap_120_sells` (T-gap120), `test_interior_gap_121_blocks` (T-gap121), `test_interior_gap_not_checked_rule` (T-gap-noE), `test_real_interior_gap_mo` (change 6).
   - DROP_CASES += `"earnings_interior_gap"`, plus a branch in `test_drop_input`. In `test_realtest_missing_lists_every_input` (L376), add `"earnings_interior_gap"` to the literal set: extended, not loosened.
   - Fixture edits, assertions unchanged: `date(2024, 6, 1)` → `date(2024, 2, 20)` at L219, L274, L288 (220 d → 118 d, so each stays a control).
   - REAL_BAC: `earnings_gap_days=0` in all 3 dicts; `INFO` gets `"earnings_gap_days"` with a comment (change 1).
   - Added asserts in existing tests: L124 summary `["AAA"]["earnings_gap_days"] == 0`; L226 (no dates) and L237 (ETF): `math.isnan(...["earnings_gap_days"])`; L315-321: NaN in counts, and `is None` in summary.json; drop `earnings` branch: NaN; drop `earnings_before_first` branch: `== 0`.

## Tests and checks
All on `_tiny` (sale day 2024-01-02, expiry 2024-02-16, strike 11 picked when OK) unless named:
- **T-gap180** `earnings=[2023-10-25, 2024-04-22]` (180 d): `tr == []`, `rej_EARNINGS_UNKNOWN == 1`, `rej_EARNINGS_BLACKOUT == 0`, `rej_OK == 0`, `earnings_gap_days == 1`; the warning has `"2023-10-25→2024-04-22"` and `"EARNINGS_UNKNOWN"`.
- **T-gap120** `[2023-10-25, 2024-02-22]` (120 d): 1 trade, strike 11.0, `earnings_gap_days == 0`, no gap warning.
- **T-gap121** `[2023-10-25, 2024-02-23]` (121 d): `tr == []`, `rej_EARNINGS_UNKNOWN == 1`, `earnings_gap_days == 1`.
- **T-gap-noE**: T-gap180's dates with `Config(..., skip_earnings=False)` (built from BOT_RULE's delta/dte): 1 trade, `rej_EARNINGS_UNKNOWN == 0`, `earnings_gap_days == 0`, the warning has "earnings not checked by this rule".
- **test_drop_input[earnings_interior_gap]** (`_make` data): drop AAA rows dated Apr and Jul 2020. Asserts: `td.earnings_gaps == 1`; no trade with `open_date` strictly inside the new gap (a, b); at least one trade with `open_date >= b` (no over-blocking); `earnings_gap_days > 0`; the gap warning is in `td.warnings + df.attrs["warnings"]`; `"EARNINGS_UNKNOWN" in REALTEST_MISSING[kind]`.
- **test_real_interior_gap_mo** (data/real): `calls_sold == 21`, `earnings_gap_days == 71`, no `open_date` in (2021-10-28, 2022-04-28).
- Controls L219/L274/L288 with the 118-d pair: pass with assertions unchanged.
- REAL_BAC 3 params: pass with the added key.
- Mutations (scratch copy, I2 in 05 and I3 in 06; each must fail at least one test):
  (i) `i == 0` treated as known → 063's 6 leading-edge tests fail;
  (ii) `i == len` treated as known → `test_stock_without_earnings_sells_nothing` + REAL_BAC fail (R3: 4 failed on the old-code equivalent);
  (iii) gap check in `_earnings_state` removed → T-gap180, T-gap121, the drop case and the MO pin fail;
  (iv) `>` → `>=` in `_is_gap` → T-gap120 fails;
  (v) simulate's warning gated on `td.earnings_gaps` → T-gap180 fails (change 2);
  (vi) the NaN → None loop limited to the lead again → the L315-321 summary assert fails (change 3).
- Grep: `EARNINGS_GAP_WARN` is read only in `_is_gap` (plus the f-string texts).
- `python3 -m pytest -q tests/test_realtest.py`: 43 today → 49 passed (5 new tests + 1 drop param). Full suite: green, apart from any file owned by in-progress item 066, which I2 names if it is red.
- 05 report (03 step 6): I2 runs `python3 -m ccbot.realtest --out <scratch dir>` and pastes the per-ticker calls_sold before/after and `earnings_gap_days` for CMCSA, MDLZ, MO, T, VZ, plus ITUB/VALE/PBR "skipped, no change", and the total (expected 247 → 242). Each dropped/added sale is split into "blocked inside the gap" and "path effect" (MDLZ 2022-05-04, 2022-11-30 drops; 3 adds). Labelled "stock only, no sale (earnings unknown)". reports/real/ is not re-published.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Decision: block (option a), restated in 04/05 | Header "Decision restated"; Files 1 `_earnings_state`/L497; 05 report |
| Step 1: `_earnings_state` with 4 states, bisect_right order; `_earnings_known` = state == known; docstring names 3 edges | Files 1 (`_earnings_state`, `_earnings_known`); Extra research 1; mutations (i)-(iv) |
| Step 1 Feasibility: 5 of 5 tickers keep a window; MO 2 / MDLZ 4 in-hole sales blocked; calls 12/31/21/1/3 | `test_real_interior_gap_mo` (21, 71, none inside); 05 report pastes all 5; Extra research 3 |
| Step 2: `earnings_gap_days` count (int; NaN for ETF/no dates) | Files 1 simulate; change 5 (0 under skip_earnings=False); T-gap tests, ETF/no-dates asserts |
| Step 2: count reaches summary.json and grid_in_sample.csv "next to L762" | Changed: no tuple edit (already carried by `*df.attrs["counts"]`); NaN → null in summary.json (change 3) |
| Step 2: warning with gap dates, rule-dependent text | Files 1 simulate warning; gate on `_gap_pairs(td.earnings)`, not `td.earnings_gaps` (change 2); T-gap180, T-gap-noE, mutation (v) |
| Step 3: same constant and comparison in load_ticker and block; load warning text unchanged | Files 1 `_is_gap`/`_gap_pairs` shared; grep check |
| Step 4: T-gap180 / T-gap120 / T-gap121 / T-gap-noE | Tests and checks, same values |
| Step 4: REALTEST_MISSING row + DROP_CASES + literal set extended | Files 1 and 2; `test_drop_input[earnings_interior_gap]` |
| Step 5: 3 control fixtures → 118-d pair, assertions unchanged | Files 2 fixture edits |
| Step 5: "REAL_BAC no change expected" | Changed: `earnings_gap_days=0` added to 3 dicts and to INFO (change 1); values unchanged |
| Step 6: 05 report numbers, path-effect split, label, no re-publish | Tests and checks, 05 report |
| Notes: ADR near-bar known limit, not tuned | Extra research 5; I2 repeats it in 05 |
| Notes: no live-bot file, no 001 rule change | Fit check |
| Out of scope 1: refetch missing Q4 2021 rows | DROPPED: external data change; A1 may open a separate item (03) |
| Out of scope 2: committing regenerated reports/real/ | DROPPED: the person's call (as in 063) |
| Missing inputs: file missing | `test_drop_input[earnings]` + `earnings_gap_days` NaN |
| Missing inputs: 0 rows | L315-321 test + NaN in counts, `null` in summary.json |
| Missing inputs: leading edge (063) | existing `test_drop_input[earnings_before_first]` + `earnings_gap_days == 0`; mutation (i) |
| Missing inputs: trailing edge | existing `test_stock_without_earnings_sells_nothing`; mutation (ii) |
| Missing inputs: interior gap > 120 | T-gap180, T-gap121, drop case, MO pin; mutation (iii) |
| Missing inputs: gap ≤ 120 complete (exactly 120 complete) | T-gap120, 3 controls; mutation (iv) |
| Missing inputs: ETF | L237 test + `earnings_gap_days` NaN, no gap warning |
| Corrections in 03 fact check (PBR 13 intervals; 1301 unknown days; L419-420 cite) | No code effect; I2 uses the corrected figures if 05 quotes them |
| Request guardrail 3: one shared helper for all edges | `_earnings_state` (+ `_is_gap`), one mutation per edge (i)-(iv) |

## Guardrail tests
- Feasibility: interior-gap rule (> 120 d, dated 2026-11-15: MO 2, MDLZ 4 in-hole sales; 71 / 69 blocked attempt days, measured by I1) → `test_real_interior_gap_mo` pins 21 calls / 71 days; T-gap120/T-gap121 pin the bar; the drop case pins a non-empty blocked stretch with sales after it.
- Feasibility: the 3 controls (118 d ≤ 120) → existing control asserts (strike 11.0) still pass.
- Missing inputs: earnings file missing → `test_drop_input[earnings]` (`earnings_gap_days` NaN).
- Missing inputs: earnings file with 0 rows → L315-321 test (NaN in counts, `null` in summary.json).
- Missing inputs: history before the first date → `test_drop_input[earnings_before_first]` (`earnings_gap_days == 0`, lead 204).
- Missing inputs: history after the last date → `test_stock_without_earnings_sells_nothing`.
- Missing inputs: dates missing between two listed dates > 120 d apart → `test_drop_input[earnings_interior_gap]` + T-gap180/T-gap121.
- Missing inputs: asset_type etf → L237 test (`earnings_gap_days` NaN, no gap warning).

## Expected result
- In realtest, no call is sold on a stock day strictly inside an interior gap > 120 d between listed earnings dates (EARNINGS_UNKNOWN). Each such blocked attempt is counted in `earnings_gap_days`, and the gap dates are named in the warnings. Leading, trailing and interior edges are decided by one helper.
- `tests/test_realtest.py`: 49 passed; each of mutations (i)-(vi) fails at least one test. REAL_BAC values are unchanged apart from the new 0 key.
- Real data (05, not re-published): MO 23 → 21, MDLZ 34 → 31, CMCSA 12, T 1, VZ 3 unchanged; total 247 → 242 (expected); ITUB/VALE/PBR skipped, no change.
- Files: 2 (ccbot/realtest.py, tests/test_realtest.py). No live-bot file and no 001 rule text change.

Recurring issues checked (logs/recurring-issues.md; open or ESCALATED: RI-001, RI-002; the others are GUARDED and checked for contact):
- RI-001 (ESCALATED): the interior-gap filter has a dated, non-zero, measured count (MO 2 / MDLZ 4 sales; 71 / 69 days), and a real-data pin is added (change 6). Adding `earnings_gap_days` to INFO is justified as a data count, not a window rule.
- RI-002 (ESCALATED): unknown stays unknown. Interior-gap days are EARNINGS_UNKNOWN. `earnings_gap_days` is NaN (JSON null), never 0, with no dates or for an ETF. The bare-NaN JSON gap is closed for the new key (change 3). This is the remainder of occurrence 10, not a new count.
- RI-004 / RI-005: fixture arithmetic re-run here: 180, 120, 121, 118 d (python `date` differences).
- RI-006: counts are pasted from tool output, not hand-counted.
- RI-007: Scope FULL; the code goes through I2/I3.
- RI-008: stdlib `bisect` only; 3.10-compatible.
- RI-010: log line written with `check_pipeline.py --log`.
- RI-012: tests assert numeric counts; the warning gate is computed from data, not from text (change 2).
- RI-003, RI-009, RI-011: GUARDED, not touched.
