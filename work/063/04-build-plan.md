# 04 Build plan - 063
Fit verdict: FIT WITH CHANGES

Reviewed 2026-11-14 on branch daily-fixes/2026-11-14 (repo read only; no code changed, nothing committed, no log line written by I1; the orchestrator writes it with `check_pipeline.py --log`). No brokerage contacted. Research, not financial advice.

Inputs read: work/063/request.md, 01-research.md, 02-improvements.md, 03-handoff.md (READY, `check_handoff.py 063` PASS pasted in 03), logs/recurring-issues.md, ccbot/realtest.py, tests/test_realtest.py, .claude/agents/r3-fact-checker.md, .claude/agents/i3-verifier.md.

## Fit check
- **~$3k account:** fits. Only the research backtest changes. The live bot (rules/screen/missing, MISSING_POLICY `EARNINGS_UNKNOWN` for a blank `next_earnings`) is not touched. On a 1-lot account, one call held through an unlisted report is the whole position (01 Fit; the CSX 2020-01-06 call was assigned). After the fix the backtest no longer scores that risk as zero.
- **Strategy rules (001):** no rule the person follows changes. realtest is research only. `_earnings_known` gets the same fail-closed meaning the bot already uses (no known date means no sale). No slack, tolerance or cap changes, so no 001 text edit and no new request is needed.
- **Existing code:** no conflict. `_earnings_known` (L372-374) has one caller (L483). work/061/diag_keep.py wraps it with a lambda and still works with the new body. `df.attrs["counts"]` already reaches summary.json (L745) and grid_in_sample.csv (L764), so the new count needs no new plumbing.
- **Changes to R3's map (why "WITH CHANGES"):**
  1. Map step 2 says simulate adds `"earnings: no dates"` "when load_ticker has not already warned 'not supplied'". Doing that in simulate means reading the text of `td.warnings`, which is the RI-012 pattern (a type guessed from a substring). Plan: load_ticker adds that warning itself, keyed on `er is not None and not earnings and asset != "etf"`. No text matching. ETFs (SPY.csv is empty) get no warning, as in 03 § Missing inputs.
  2. Map step 2's warning says "no call sold before it (EARNINGS_UNKNOWN)" for every rule. Grid rules with `skip_earnings=False` ("E" variants) skip the earnings checks (L483) and still sell before the first date, so for them the text would be false. Plan: that clause is only used when `rule.skip_earnings` is set. Otherwise the warning ends "; earnings not checked by this rule". New test T4.
  3. `earnings_lead_days` NaN in `counts_bot_rule_bid` would be written to summary.json as the bare token `NaN`. That is not valid JSON (research 1), and summary.json has 0 NaN tokens today (Grep `NaN|Infinity` in reports/real/summary.json → 0). Plan: `run` writes a NaN lead as `null` in the counts it puts in summary.json. That keeps "unknown", never 0 (RI-002). The CSV files keep NaN (an empty cell).
  4. Both T1 and T2 put the first date after the `_tiny` period end (2024-03-29). That covers 03 § Missing inputs "first listed date after the period end", but no fixture shows a sale that is still allowed after the first date. Plan: the new drop case (first date 2019-07-25 inside the `_make` window) also asserts that at least one call is sold on or after that date. This pins that the edge does not over-block.

## Extra research (with sources)
1. **JSON and NaN.** Python's `json.dumps` writes `NaN` by default, and the docs say this "is not JSON specification compliant". RFC 7159 "does not permit the representation of infinite or NaN number values" [https://docs.python.org/3/library/json.html, § Infinite and NaN Number Values; `allow_nan`]. Hence change 3: write `null` for an unknown lead. A strict reader (a browser, jq) would otherwise fail on summary.json for any stock without dates. Today that is 0 of 17 reported stocks, but the drop test creates one.
2. **`DataFrame.attrs` is the right carrier, with one limit.** pandas: "attrs is experimental and may change without warning". "Many operations that create new datasets will copy attrs. Copies are always deep". `concat`/`merge` "will only copy attrs if all input datasets have the same attrs" [https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.attrs.html]. realtest already passes `counts` this way, and summarize reads `df.attrs` from the frame simulate returned (no concat in between), so `warnings` is safe on the same path. Do not rely on it surviving walk_forward's `pct_change`/`concat` (it does not need to).
3. **Edge case: rules that skip the earnings check.** The GRID holds `skip_earnings=False` variants (L274-275). Under option (a) they are unchanged by design (L483). Only the warning text needed a fix (change 2).
4. **Edge case: the first quote day has no close.** `days` is filtered to `d >= snaps[0]` (L400), so `days[0]` can be later than `snaps[0]` when a snapshot day has no close (BAC has 55 such days). The lead is measured from `days[0]`, the first day a sale can be tried, which is the right base. BAC's `days[0]` is pinned at 2020-01-06 (test L415), so the lead stays 100.
5. **Simpler method checked: no new constant.** `EARNINGS_GAP_WARN` stays for interior gaps only. The edge rule is `earnings[0] <= d` (03 Decision), so there is no threshold to tune.

## Files to create/change
1. **ccbot/realtest.py**
   - Module docstring L18: "EARNINGS_UNKNOWN for a stock with no known next earnings date" → "... with no known next earnings date, or on a day before its first listed date (history not in the file, item 063)".
   - `REALTEST_MISSING`: add the row `"earnings_before_first": "EARNINGS_UNKNOWN before a stock's first listed earnings date; warning with the lead in days"` (03 step 4).
   - `load_ticker`: after `asset, aw = _asset_type(...)` (L221), add: if `er is not None and not earnings and asset != "etf"`, append `"earnings: no dates (EARNINGS_UNKNOWN for a stock)"` (change 1). The missing-file branch (L178-180) is unchanged. load_ticker gets no edge logic (no `start`).
   - `_earnings_known(td, d)`: `return bool(td.earnings) and td.earnings[0] <= d and td.earnings[-1] >= d`. Docstring: "a listed date on or before d (no unlisted history) and one on or after d" (03 step 1).
   - `simulate`: after `days` is set (L400-402), compute `lead = (td.earnings[0] - days[0]).days if td.asset_type != "etf" and td.earnings else None`. Then:
     - `earnings_lead_days = max(lead, 0)` as an int, or `float("nan")` when `lead is None` (an ETF or no dates; never 0).
     - `edge_warn = []`. When `lead > 0`: `f"earnings: first listed date {td.earnings[0]} is {lead} days after the first quote day {days[0]}"` + (`"; no call sold before it (EARNINGS_UNKNOWN)"` if `rule.skip_earnings` else `"; earnings not checked by this rule"`).
     - At L515: add `"earnings_lead_days": earnings_lead_days` to `df.attrs["counts"]`, and set `df.attrs["warnings"] = edge_warn`.
   - `summarize` L595: `"warnings": "; ".join(td.warnings + df.attrs.get("warnings", []))` (03 step 3).
   - `run` L745-747: after building `counts[tk]`, if `earnings_lead_days` is a float NaN, set it to `None` (change 3). Nothing else in summary.json changes.
2. **tests/test_realtest.py** (new tests, extended sets, fixture edits; no assert removed or loosened)
   - New T1 `test_leading_edge_100_days_blocks`: `_tiny(earnings=[date(2024, 4, 11)])` → `tr == []`, `rej_EARNINGS_UNKNOWN == 1`, `rej_OK == 0`, `earnings_lead_days == 100`, and `"100 days"` plus `"EARNINGS_UNKNOWN"` in `df.attrs["warnings"][0]`.
   - New T2 `test_leading_edge_151_days_blocks`: `_tiny(earnings=[date(2024, 6, 1)])` → the same with lead 151 (the request's > 120 d fixture; its first date also lies after the period end, 03 § Missing inputs row 4).
   - New T4 `test_leading_edge_rule_without_earnings_check_still_sells`: the T1 fixture with `dataclasses.replace(rt.BOT_RULE, skip_earnings=False)` → `len(tr) == 1`, `earnings_lead_days == 100`, and the warning does not contain "no call sold" (change 2).
   - New `test_empty_earnings_file_warns_and_lead_is_null(data_root, tmp_path)`: `_copy`, then write AAA's earnings CSV with its header only. Then:
     - `load_ticker` → `td.earnings == []` and a warning equal to `"earnings: no dates (EARNINGS_UNKNOWN for a stock)"`.
     - `simulate(BOT_RULE)` → `tr == []` and `math.isnan(counts["earnings_lead_days"])`.
     - `run(root, out, ["AAA", "SPY"], CFG, grid=[rt.BOT_RULE], mc_paths=10, min_years=1, facts=FACTS)` → `json.loads((out / "summary.json").read_text(), parse_constant=<raise>)` parses, and `["counts_bot_rule_bid"]["AAA"]["earnings_lead_days"] is None`.
   - T3, in `test_run_end_to_end`: add `assert s["counts_bot_rule_bid"]["AAA"]["earnings_lead_days"] == 23` and `assert "first listed date 2019-01-25" in s["counts_bot_rule_bid"]["AAA"]["warnings"]`. This proves the path to summary.json without committing reports/real/.
   - `DROP_CASES` gains `"earnings_before_first"`. `test_realtest_missing_lists_every_input` L312 becomes `files | {"asset_type", "earnings_before_first"} == set(rt.REALTEST_MISSING) == set(DROP_CASES)`. The set is extended, and the `files ==` assert on L311 is unchanged.
   - `test_drop_input` gains a branch for `earnings_before_first`: rewrite AAA's earnings CSV without rows before 2019-07-01 (new first date 2019-07-25), load, then `simulate(BOT_RULE)` →
     - `not any(t.open_date < date(2019, 7, 25) for t in tr)`
     - `any(t.open_date >= date(2019, 7, 25) for t in tr)` (change 4)
     - `rej_EARNINGS_UNKNOWN > 0`
     - `earnings_lead_days == 204` (2019-01-02 → 07-25: 29 + 28 + 31 + 30 + 31 + 30 + 25 = 204)
     - `"first listed date 2019-07-25"` in the joined warnings
     - `"EARNINGS_UNKNOWN" in reason`
   - `test_drop_input` existing branch `earnings` (file missing): add `assert math.isnan(df.attrs["counts"]["earnings_lead_days"])` (03 § Missing inputs row 1).
   - `test_etf_without_earnings_sells`: add `math.isnan(df.attrs["counts"]["earnings_lead_days"])` and `df.attrs["warnings"] == []`.
   - `test_stock_without_earnings_sells_nothing`: add `math.isnan(...earnings_lead_days)` for `earnings=[]`. Also add `earnings_lead_days == 0` for `[date(2023, 10, 1)]`: lead = 10-01 − 01-02 < 0, so max(lead, 0) = 0, and it is still blocked by the trailing edge.
   - Fixture edits (03 step 5): L216, L237 and L251 change `earnings=[date(2024, 6, 1)]` to `earnings=[date(2023, 10, 25), date(2024, 6, 1)]` so each control stays a control. Their assert lines stay byte-identical. L380 is not changed (03 fact-check row 01 OQ3).
   - `REAL_BAC`: I2 re-measures all three rules on data/real with `start=2020-01-01` and pins the new values plus `earnings_lead_days=100` in each dict. The header comment (L387) gets "re-measured by I2 for 063 on <date>". Expected under BOT_RULE: calls_sold 22 (diag), rej_EARNINGS_UNKNOWN > 20, rej_EARNINGS_BLACKOUT lower. I2 explains any other calls_sold value. L417-418 (every non-INFO count > 0 for BOT_RULE) must still pass unchanged.
3. **.claude/agents/r3-fact-checker.md** step 1b and 4. **.claude/agents/i3-verifier.md** step 3 (RI-002 sentence): append one sentence each: "For any data-hole check, check the edges of the data window (before the first value and after the last) as well as gaps between values." These are additions only and need the person's OK in PR review (03 step 7; flagged in 05).

Not changed: reports/real/ (not regenerated in the repo, not committed; Open question 1 default), ccbot/rules.py, screen.py, missing.py, config/, 001 rule text, EARNINGS_GAP_WARN and the interior-gap warning.

## Tests and checks
- `python3 -m pytest -q` on the full suite: green. Expected count = 293 passed + 1 skipped (main, RI-002 note), + 3 new test functions (T1, T2, T4), + 1 empty-file test, + 1 new parametrized drop case. I2 pastes the real line.
- Mutation 1 (scratch copy, never in the repo): delete `td.earnings[0] <= d and` → T1, T2 and `test_drop_input[earnings_before_first]` fail, and `test_real_counts_bac[BOT_RULE]` fails too (counts revert). This is RI-002's GUARDED condition.
- Mutation 2 (scratch): replace the clause with `(td.earnings[0] - d).days <= rt.EARNINGS_GAP_WARN and` (the request's threshold) → T1 fails (lead 100 ≤ 120 sells). T2 may pass. That is expected, and it shows why the 100 d fixture is needed (02 FOR 1).
- Mutation 3 (scratch): use the `"; no call sold"` text for every rule → T4 fails.
- Mutation 4 (scratch): remove the NaN → None line in `run` → the empty-file test fails on the strict `parse_constant` load.
- `python3.10/3.11 -m py_compile` via `tests/test_safety.py::test_every_py_compiles_on_oldest_python` (RI-008): no 3.11+ syntax.
- `Grep "edges of the data window" .claude/agents` → 2 files. `git diff` of both agent files shows additions only.
- Scratch run, report in 05 only (03 step 6): `python3 -m ccbot.realtest --out <scratch dir>` (`--mc-paths` may be lowered; MC is not in the counted fields). In 05, I2 pastes:
  - per-ticker calls_sold before/after for the 17 tickers, and the total (expected 247: BAC 22, USB 10, OXY 7, CSX 38, others unchanged), with any difference explained per ticker
  - any A-row change per ticker
  - the summary.json warning lines for BAC, CSX, USB and OXY, with their `earnings_lead_days` (expected 100, 107, 100, 52)
  - the label for the dropped Feb-Mar 2020 sales: "stock only, no sale (earnings unknown)", a data effect and not a strategy result.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Map 1: `_earnings_known` gains `td.earnings[0] <= d`; no threshold constant | Files 1, `_earnings_known`; T1, T2, drop case; Mutation 1 |
| Map 1: second mutation with the request's 120 d threshold → T1 fails | Tests and checks, Mutation 2 |
| Map 2: `earnings_lead_days` in counts: `max(lead, 0)` int, NaN for ETF / no dates, never 0 | Files 1, `simulate`; T1/T2 (100/151), T3 (23), drop case (204), ETF / no-file / no-dates NaN asserts, `[2023-10-01]` → 0 |
| Map 2: edge warning text with the lead | Files 1, `simulate` (text per change 2); T1, T3, drop case |
| Map 2: "no dates" warning when load_ticker has not warned "not supplied" | Changed (change 1): emitted in load_ticker on `er is not None and not earnings and asset != "etf"`, no text matching (RI-012); empty-file test |
| Map 3: summarize joins `td.warnings + df.attrs["warnings"]`; load_ticker edge-free so L88 `not td.warnings` holds | Files 1, `summarize`; T3; L88 unchanged (AAA has dates, so change 1 adds nothing) |
| Map 4: T1, T2, REALTEST_MISSING row, DROP_CASES + L312 set, drop case | Files 2 (all listed) |
| Map 5: fixture edits L216/L237/L251 only; L380 unchanged; REAL_BAC re-measured with lead 100; L418 still passes | Files 2, fixture edits and REAL_BAC |
| Map 6: 05 reports per-ticker calls_sold, total (expected 247), A-row change, warning lines, "stock only" label; reports/real/ not re-published | Tests and checks, scratch run; Not changed: reports/real/ |
| Map 7: r3 step 1b and i3 step 3 sentence "edges of the data window"; person's OK in PR review | Files 3 and 4 |
| Out of scope: interior gaps > 120 d still warn and sell | DROPPED: out of scope (person-free default). Named follow-up for A1 to open: "realtest interior earnings gaps > 120 d (CMCSA, MDLZ, MO, T, VZ) still sell; decide block vs label" |
| Out of scope: no 001 change, live-bot code untouched | Fit check; Not changed list |
| Decision: option (a) fail closed; cost 1 OXY sale | Files 1 `_earnings_known`; OXY 8 → 7 expected in 05 |
| Request § Guardrail 1 "lead > EARNINGS_GAP_WARN days" as the rule | DROPPED: catches 0 of 4 real cases (03 Numbers, max lead 113). Kept only as Mutation 2, to prove the 100 d fixture catches it |
| Request § Guardrail 2: a > 120 d fixture warns and does not sell | T2 (151 d) |
| Request § Guardrail 3: r3/i3 text | Files 3 and 4 |
| Missing inputs 1: earnings file missing → unchanged code, lead NaN | `test_drop_input[earnings]` + NaN assert |
| Missing inputs 2: 0 rows → EARNINGS_UNKNOWN, "no dates" warning, lead NaN | empty-file test |
| Missing inputs 3: history before first date → UNKNOWN, warning, lead n | T1, T2, drop case |
| Missing inputs 4: first date after period end → 0 sold, warning | T1 and T2 (both first dates are after 2024-03-29) |
| Missing inputs 5: ETF → rule not applied, lead NaN, no warning | `test_etf_without_earnings_sells` + asserts |
| Missing inputs 6: interior gap → unchanged | DROPPED: out of scope (see the follow-up above); the existing L183-185 warning is untouched |
| Open question 1: commit regenerated reports/real/? | Default, no person decision needed: not committed; I2 reports the measured call-count change in 05 from a scratch run; T3 proves the summary.json path |
| Open question 2: interior-gap asymmetry | Default: named follow-up, out of scope (row above) |
| Correction 01 F5 / F17 / 02 Past logs 2: 247 is the expected total under (a) (BAC −2, USB −1, OXY −1, CSX +1) | Tests and checks, scratch run: expected 247, measured and explained per ticker |
| Correction 01 Fit / 02 FOR 3: 6 sales blocked directly; later sales can shift by path | 05 per-ticker table (scratch run) |
| Correction 01 OQ1(b): VALE shortest interval 54 d | DROPPED: option (b) not chosen |
| Correction 01 OQ3: L380 does not move | Files 2: L380 not changed |
| Correction 02 Holes 2: the block does not depend on "data start"; `days[0]` sets only the lead | Files 1, `simulate` lead from `days[0]`; Extra research 4 |
| Correction 02 AGAINST 2: OXY loses one sale that held no report; PBR skipped | Accepted cost; shown in 05 |
| Removed claims 1-3 (2019 snapshot date, VALE Q4 date, why DoltHub starts in 2020) | DROPPED: removed by R3; not used |

## Guardrail tests
- Feasibility: edge rule `d < earnings[0] → EARNINGS_UNKNOWN` (dated count in 03 map step 1: 17 of 17 reported tickers keep a non-empty sale window from 2020-01-06 to 2026-11-12; blocked leads 16-107 d; 6 bot-rule sales directly blocked) → `test_real_counts_bac[BOT_RULE]` pins BAC's re-measured `rej_EARNINGS_UNKNOWN` (> 0), `calls_sold` (> 0, expected 22) and `earnings_lead_days == 100` on data/real; L418 keeps every non-INFO count > 0. On fixtures: T1 (100 d), T2 (151 d), drop case (204 d, with sales after the edge still allowed).
- Feasibility: interior-gap warning (`EARNINGS_GAP_WARN`, unchanged) → no new pin; out of scope (follow-up).
- Missing inputs: earnings file absent → `test_drop_input[earnings]` (UNKNOWN, "not supplied", lead NaN).
- Missing inputs: earnings file with 0 rows → `test_empty_earnings_file_warns_and_lead_is_null` (UNKNOWN, "no dates" warning, lead NaN in simulate, `null` in summary.json).
- Missing inputs: history before the first listed date (new REALTEST_MISSING row `earnings_before_first`) → `test_drop_input[earnings_before_first]`, T1, T2. The enumeration `test_realtest_missing_lists_every_input` includes the key.
- Missing inputs: first date after period end → T1, T2.
- Missing inputs: asset_type etf → `test_etf_without_earnings_sells` (lead NaN, no warning). asset_type absent → existing `test_drop_input[asset_type]` (treated as stock, so the edge applies).
- RI-002 mutation (I2 in 05, I3 in 06, scratch copy only): delete `td.earnings[0] <= d and` → ≥ 1 test fails (expected T1, T2, the drop case, REAL_BAC BOT_RULE).
- RI-012: no new code classifies by text (change 1 removes the one place R3's map would have). The tests assert `earnings_lead_days`, the numeric field. The warning-text asserts are additional checks, not the only ones.

## Expected result
- On data/real from 2020-01-01: no stock sells a call on a day before its first listed earnings date (rule `skip_earnings=True`). The BAC/USB/CSX 2020-01-06 → 02-21 sales and the BAC/CSX 02-21 → 03-20 sales become `EARNINGS_UNKNOWN`, and so does OXY's 01-06 → 02-21 sale.
- `reports/real`-shaped output (scratch run only) shows, for every stock, `earnings_lead_days` and, when > 0, the warning "earnings: first listed date <date> is <n> days after the first quote day 2020-01-06; no call sold before it (EARNINGS_UNKNOWN)". Expected: BAC 100, USB 100, CSX 107, OXY 52; the other 13 are 16-37.
- Expected bot-rule total 247 calls (from 250): BAC 22, USB 10, OXY 7, CSX 38, others unchanged. I2 measures and explains any difference. This is a data effect, labelled "stock only, no sale (earnings unknown)", not a new strategy result. reports/real/ is not committed.
- Suite green. Mutation 1 fails ≥ 1 test, which meets RI-002's GUARDED condition once merged.
- 2 agent files gain one sentence each, flagged for the person's PR review.

Recurring issues checked (open or ESCALATED: RI-001, RI-002; GUARDED entries also scanned):
- RI-001 (ESCALATED): the edge rule has a dated non-zero count in 03 (17/17 windows, 6 sales, leads 16-107 d) and a pinning test (REAL_BAC + L418). The request's 120 d bar was measured (0 of 4) and dropped as a rule.
- RI-002 (ESCALATED): unknown stays unknown. The lead is NaN in simulate and `null` in JSON, never 0. The new REALTEST_MISSING row is in the enumeration with a drop test. The mutation is planned.
- RI-004: T1/T2/T4/control fixtures checked against the rule's trigger: T1 04-11 > 01-02 → UNKNOWN; controls 2023-10-25 ≤ 01-02 ≤ 2024-06-01 with no date in [01-02, 02-16] → sell. The drop-case lead of 204 is computed above.
- RI-005: plan numbers (100, 151, 23, 204, 247) re-derived from 03's Self-check or shown above.
- RI-006: no hand-counted totals; I2 pastes the pytest line.
- RI-007: Scope FULL, so I2/I3 follow. I1 changed no code and committed nothing.
- RI-008: 3.10-compatible syntax only; the compile test runs.
- RI-009, RI-011: not touched (no branch logic).
- RI-010: I1 wrote no log line by hand; the orchestrator uses `check_pipeline.py --log I1 063 "FIT WITH CHANGES | 4 files planned"`.
- RI-012: change 1 avoids a substring classification; the tests pin the numeric field.
- RI-003: not touched.
