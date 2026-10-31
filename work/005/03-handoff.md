# 03 Research hand-off - 005
Status: READY

Checked 2026-10-30 by R3. This is a code-review item. I reproduced A1's evidence with the repo code, using scratch copies; no repo files were changed. The baseline suite is 93 passed.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| `data.py` L78–79: an absent `dividend` → 0.0 and an absent `earnings` → 0 | code | VERIFIED | – |
| `screen.py` L36: missing OI passes; L39: missing `next_earnings` passes | code + re-run on SYNTH_SNAPSHOTS | VERIFIED: SYNTH_A with OI 100 → `OI`, OI blank → pass; earnings 2026-11-15 → `EARNINGS`, blank → pass | – |
| `rules.py` L283: the blackout runs only if `next_earnings is not None` | code | VERIFIED | – |
| `webull_sandbox.py` L144: `Day(self.date, price)` with no earnings or ex-div | code | VERIFIED (`Day.next_earnings` defaults to None, `rules.py` L78) | – |
| R1 F4: OI read as `_num(i, "open_interest", "oi")` | code | VERIFIED; it is at **L177** | – |
| Webull's real OI/earnings field names | – | UNVERIFIED (sandbox unreachable). Kept as an open item; the fix fails safe | – |
| R1 F5: `backtest.py` L50, next-day dividend on the last row = 0.0 | code | VERIFIED | Allow-listed with a reason (step 6) |
| R1 F6: 001 step 3 check asks for spread, OI and next earnings at each entry (001/03 L122) | doc | VERIFIED | – |
| A1: SYNTH_B (stock) V0 `EARNINGS_BLACKOUT` 69 → 0 when the column is dropped | re-run | VERIFIED | – |
| R1: "grep today: 20 hits in `ccbot/`" for the listed patterns | `grep -rnE "else 0\b\|else 0\.0\|pd\.notna\(.*\) and\|is not None and\|max\(1,\|min\(1,\|fillna\|nan_to_num\|or 0" ccbot/` | **WRONG** | **23** hit lines. **8** are defaults on missing data: data.py 78, 79; screen.py 36, 39; rules.py 283; backtest.py 50, 121; report.py 168. The rest are rules or guards (e.g. costs.py 31, SEC fee only on sells) |
| R2: "putting both old bugs back makes 7 tests fail" | `logs/recurring-issues.md` (A1) | Not re-run by R3 | Not used in the map |
| R2 table, Spanish/English sources (delisted instruments; "upper bound") | fetched | VERIFIED (see 003/03) | – |
| R2 AGAINST 1: an object sentinel in a DataFrame column breaks vectorised comparisons | reasoning | Accepted (no sentinel class in the map) | – |

## Removed claims
- None removed. The grep count was corrected (above).

## Decision (R1 vs R2)
**Missing-data policy:** unknown is never "none" and never a pass.
- **Representation:** NaN/None means unknown in frames and scalars. "Known none" is explicit: either `asset_type == "etf"` (no earnings), or the column or field was supplied. This follows R2 AGAINST 1. There is no `UNKNOWN` singleton, because pandas columns would turn object dtype. The one scalar that needs three states gets a flag: `Day.earnings_known`.
- **Policy table:** one dict, `ccbot/missing.py::MISSING_POLICY`, lists each optional input and what absence does. A drop-each-input test enumerates it (R2 FOR 2). The grep becomes a review aid in the agent files, not a test (R2 AGAINST 2).

| Input (where it enters) | When absent | Reason / report text |
|---|---|---|
| `earnings` column (CSV), stock | every option entry blocked | `EARNINGS_UNKNOWN`; "earnings: not supplied (n days blocked)" |
| `earnings`, ETF | known none | – |
| `next_earnings` (snapshot / broker `Day`), stock | screen and entry blocked | `EARNINGS_UNKNOWN` |
| `oi` (snapshot) | screen blocked | `OI_UNKNOWN` |
| `dividend` column (CSV) | every option entry blocked; B&H n/a | `DIVIDEND_UNKNOWN`; "dividend: not supplied" |
| `iv` column (CSV) | realised vol used (existing, labelled) | existing behaviour, listed so the test enumerates it |
| `bh_benchmark` (006) | n/a | "n/a (100 shares cost more than cash − buffer)" |
| `ex_div_date` (snapshot) | not a decision input today; shown as n/a | "days to ex-dividend: n/a (not supplied)" |
| broker `Day.div_next` (sim/webull, default 0.0) | **known gap:** the early-assignment warning is off on the broker path | allow-listed with this reason; A1 to open an item |

## Implementation map
| Step | Change | Inputs | Outputs | How we check it |
|---|---|---|---|---|
| 1 | `rules.py`: `Day` gains `earnings_known: bool = False` (the default is unknown, so a bare `Day(date, price)` fails safe). `REASONS` gains `EARNINGS_UNKNOWN`, `DIVIDEND_UNKNOWN`. In `_option_entry`, before L283: if `day.asset_type != "etf" and not day.earnings_known` → `EARNINGS_UNKNOWN`; if `math.isnan(day.q)` → `DIVIDEND_UNKNOWN`. Update the expected set in `tests/test_variants.py` L62 to add the two new reasons. | – | new reasons | Steps 5–6 tests |
| 2 | `data.py` L78–79: no `else 0`. An absent `dividend`/`earnings` column becomes a NaN column, and `PriceSeries` gains `missing: tuple = ()` naming it. Row checks L87–90 and `astype(int)` L91 run only for supplied columns. `backtest.build_days` sets `earnings_known = "earnings" not in series.missing or asset == "etf"`. NaN dividends give NaN `q`/`div`/`div_next`. | CSV | `PriceSeries.missing` | `tests/test_data.py`: `date,close` CSV → `missing == ("dividend", "earnings")`, no zeros in those columns. The existing error-message cases still pass |
| 3 | `screen.py` L36: `if pd.isna(q["oi"]): return "OI_UNKNOWN"` before the value test. L39: for `asset_type != "etf"`, `if pd.isna(earn): return "EARNINGS_UNKNOWN"`, then the blackout. Add both to `TESTS`. `broker/sim.py` L58–61: pass `earnings_known = asset_type == "etf" or pd.notna(next_earnings)`. `webull_sandbox.py` L144: unchanged (the default is unknown), plus a comment naming the policy. | snapshots | reject reasons | A1's cases (step 5). `test_shipped_config_has_a_passing_ticker` still passes (SYNTH_A is an ETF; SYNTH_B is already rejected for `SPREAD`) |
| 4 | Reports: the backtest report gets `## Missing inputs` with one line per `series.missing` entry ("earnings: not supplied (n days blocked)"), or "none". In the daily report, Context shows "Days to earnings: n/a (not supplied)" for a stock with unknown earnings. | step 2, scan | report lines | Step 6 test asserts the line |
| 5 | **Behaviour tests (A1's evidence as tests):** `tests/test_screen_bot.py::test_blank_oi_is_rejected_oi_unknown`; `::test_blank_earnings_stock_rejected_earnings_unknown` (on a copy of SYNTH_B's rows with a passing spread); `tests/test_backtest.py::test_stock_csv_without_earnings_blocks_with_reason` (SYNTH_B without the column → `EARNINGS_UNKNOWN` > 0, `EARNINGS_BLACKOUT` == 0, 0 option sales); `tests/test_webull_sandbox.py::test_sandbox_day_is_not_earnings_known`. | sample data | tests | Each fails on today's code and passes after steps 1–4 |
| 6 | **Guardrail (BUG; RI-002 ESCALATED, systemic, shared with 006):** (a) `ccbot/missing.py::MISSING_POLICY` = the table above, as data. (b) `tests/test_missing_inputs.py::test_drop_each_input[<input>]`, parametrised over `MISSING_POLICY`. It drops the input (CSV column, snapshot field, or Day field) and asserts the run reports the named reason or n/a, with no exception and no number. (c) `::test_policy_lists_every_optional_input` asserts that the optional columns the loaders accept (CSV: `dividend`, `earnings`, `iv`; snapshot: `oi`, `next_earnings`, `ex_div_date`, `iv`) are all keys of `MISSING_POLICY`. A new optional input with no row then fails. (d) The 006 account-invariant test (006/03 step 3). (e) Agent files (needs the person's OK; coordinate with 013): put the standing rule in `.claude/agents/i1-reviewer.md`, `i2-builder.md`, `i3-verifier.md` and `r3-fact-checker.md`, worded as "If a value cannot be computed from the data available at that point, it stays NaN/n/a or blocks, and the code says why — whatever the type (NaN, None, 0, a default lot, a pass). For every optional input, state what happens when it is absent and test it." Widen the review grep there to `fillna\|nan_to_num\|or 0\|else 0\|pd\.notna\(.*\) and\|is not None and\|max\(1,\|min\(1,\|\.get\([^)]*, 0\)`. Each hit needs a one-line reason in the review. | – | policy, 2 tests, agent text | Mutation check: put back `else 0` (data.py) or `pd.notna(q["oi"]) and` (screen.py), and at least one test fails |
