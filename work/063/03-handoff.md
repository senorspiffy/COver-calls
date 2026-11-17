# 03 Research hand-off - 063
Status: READY (step 7 run by the orchestrator with a shell on 2026-11-14 after R3 finished: `check_handoff.py 063` PASS, counts match the Totals line; output pasted below.)

Checked 2026-11-14 on branch daily-fixes/2026-11-14 (repo read only; no code changed by R3). No brokerage contacted. Research, not financial advice.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| 01 F1: the only gap check is between consecutive dates (L183); `EARNINGS_GAP_WARN = 120` (L61); it only warns, never blocks | ccbot/realtest.py L61, L183-185, L482-488 | VERIFIED | - |
| 01 F2: `_earnings_known` = `bool(td.earnings) and td.earnings[-1] >= d`, so only the trailing edge is checked | ccbot/realtest.py L372-374 | VERIFIED | - |
| 01 F3: `_earnings_between` can only find listed dates | ccbot/realtest.py L368-369 | VERIFIED | - |
| 01 F4: warnings reach reports only through `td.warnings` (load_ticker), then summarize "warnings" (L595), then summary.json (L745-747). load_ticker has no `start`. simulate's first day is the first snapshot on or after `start` | ccbot/realtest.py L134-227, L397-402, L595, L745-747 | VERIFIED | - |
| 01 F5: summary.json "warnings" hold only the interior-gap and dropped-rows texts "(grep, 18 rows)" | Grep `"warnings"` in reports/real/summary.json → 17 | WRONG | There are 17 "warnings" fields, one per reported ticker. F (L202) and KEY (L246) are empty. None mentions a first date or edge (Grep `first listed|leading|before first|edge` in reports/real → 0). The rest of the claim holds |
| 01 F6: BAC prices start 2019-01-02; fetch default `--start 2019-01-01`; CLI help text about the 2019 snapshot | data/real/prices/BAC.csv row 2; scripts/fetch_real_data.py L149; ccbot/realtest.py L797 | VERIFIED | - |
| 01 F6: the date of the single 2019 option snapshot | none (R1 labelled it UNVERIFIED) | UNSUPPORTED | Removed. The map does not need it: the edge rule is `d < earnings[0]`, and the lead is measured from simulate's first day |
| 01 F7: first listed dates of the 21 stocks (AAL...VALE as listed) and SPY.csv empty | row 2 of each data/real/earnings/*.csv (read); Grep `,(19\|200\|201)\d-` → 0 rows and `,2019-\|,2020-0[1-3]-` → only the row-2 lines, so no earlier row is hidden lower in a file | VERIFIED | - |
| 01 F8: BAC/CSX/USB rows 2-4 are quarterly (04-15/07-16/10-14; 04-22/07-22/10-21; 04-15/07-15/10-14) | data/real/earnings/{BAC,CSX,USB}.csv rows 2-4 | VERIFIED | - |
| 01 F9: VALE skipped "option quotes only 2020-01-06 to 2020-12-02 (< 3.0 years)" | reports/real/summary.json L25 (ITUB, KGC, PBR also skipped, L22-24) | VERIFIED | - |
| 01 F10: BAC Q4/FY2019 8-K filed January 15, 2020 | https://www.businesswire.com/news/home/20200115005654/en/Bank-of-America-Corporation-Filed-a-Form-8-K | VERIFIED | - |
| 01 F11: U.S. Bancorp Q4 2019 results release dated January 15, 2020 | https://ir.usbank.com/news-events/news/news-details/2020/U.S.-Bancorp-Reports-Fourth-Quarter-2019-Results-01-15-2020/default.aspx | VERIFIED | - |
| 01 F12: CSX Q4/FY2019 release datelined January 16, 2020 | https://www.sec.gov/Archives/edgar/data/277948/000027794820000004/pressreleaseq42019.htm ("JACKSONVILLE, Fla. - January 16, 2020") | VERIFIED | - |
| 01 F13: VALE's Q4 2019 report date | none (R1 labelled it UNVERIFIED) | UNSUPPORTED | Removed. VALE is skipped by min_years (F9), and the rule choice does not depend on it |
| 01 F14: earnings source is DoltHub post-no-preference/earnings, table earnings_calendar | https://www.dolthub.com/repositories/post-no-preference/earnings (repo exists); table name from scripts/fetch_real_data.py L7, L91, L123 | VERIFIED | - |
| 01 F14: why the DoltHub history starts in 2020 | none (R1 labelled it UNVERIFIED) | UNSUPPORTED | Removed. Not used: the rule treats any day before the first listed date as unknown, whatever the cause |
| 01 F15: BAC $37, USB $60 and CSX $77.5 calls sold 2020-01-06 to 2020-02-21 (expired / expired / assigned). Each life holds the F10-F12 report | reports/real/trades_{BAC,USB,CSX}.csv row 2; Jan 15 and Jan 16 lie in [01-06, 02-21] | VERIFIED | - |
| 01 F16: BAC and CSX 2020-02-21 to 2020-03-20 sales are inside the hole, with no report missing from their life | trades_BAC.csv / trades_CSX.csv row 3; next real reports are the listed 04-15 / 04-22 | VERIFIED | - |
| 01 F17: 061's 247 comes from a different rule (diag_keep.py L12 lookback [d-120, d]) that "also blocks inside interior gaps (OXY 8 to 7)" and "is not the count for a leading-edge-only rule" | work/061/diag_keep.py L12-13; logs/audit/2026-11-14-061.md L40-41; summary.json L334 (OXY warnings: no gap text); work/061/01-research.md L199 (gaps > 120 d: CMCSA, MDLZ, MO, T, VZ only); trades_OXY.csv row 2 | WRONG | OXY has no interior gap over 120 d. Its 8 → 7 is its 2020-01-06 → 2020-02-21 sale, which falls before OXY's first listed date (2020-02-27). That is a leading-edge block. The lookback rule blocks everything the fail-closed edge rule (option a) blocks, plus days more than 120 d after the latest listed date inside an interior gap. diag shows no calls_sold change for the five interior-gap stocks, so 247 (250 − 2 BAC − 1 USB − 1 OXY + 1 CSX) is the expected total under option (a). It is an expectation that I2 measures, not a result |
| 01 Numbers: leads from 2020-01-06: BAC/USB 100 d, CSX 107 d, VALE 113 d | arithmetic (Self-check row 1) | VERIFIED | - |
| 01 Numbers: OXY 52, PBR 44, KGC 37, ITUB 35, BMY 31, F 29; the other 11 are 16-24 d | arithmetic: KMI 01-22 = 16; AAL/CMCSA/HBAN/KEY 01-23 = 17; PFE 01-28 = 22; MDLZ/PYPL/T 01-29 = 23; MO/VZ 01-30 = 24 (11 stocks) | VERIFIED | - |
| 01 Numbers: all 21 leads are under 120, so request § Guardrail 1 flags none of BAC/CSX/USB/VALE | arithmetic. Max lead 113 < 120. The request's second clause ("no date in the first 120 days") also flags none: BAC's first 120 days run to 2020-05-05 and hold 04-15 | VERIFIED | - |
| 01 Numbers: measured from the price start (2019-01-02), every lead is over 120 (AAL 386 d) | arithmetic: 2019-01-02 → 2020-01-02 = 365, + 21 = 386; the shortest lead (KMI) is 365 + 20 = 385 | VERIFIED | - |
| 01 Numbers: quarterly spacing BAC 92/90, CSX 91/91, USB 91/91 d | arithmetic on F8 dates (Self-check row 3) | VERIFIED | - |
| 01 Numbers: OXY lead 52 < 90, so no hidden quarter is expected (OXY Q4 2019 date UNVERIFIED) | https://app.researchpool.com/company/oxy-us6745991058-occidental-petroleum-corp/press/occidental-petroleum-corp-oxy-occidental-to-announce-fourth-quarter-results-thursday-february-27-202 ("fourth quarter 2019 results on Thursday, February 27, 2020, after the close") | UNSUPPORTED | Kept with a new source: OXY's Q4 2019 report was 2020-02-27, the same as its first listed date. Its 2020-01-06 → 02-21 sale held no report |
| 01 Fit: the live bot is not affected (snapshot next_earnings → EARNINGS_UNKNOWN by MISSING_POLICY) | ccbot/missing.py L9, L13; logs/recurring-issues.md L25 | VERIFIED | - |
| 01 Fit: the CSX 2020-01-06 call was assigned | trades_CSX.csv row 2 (outcome assigned, close_cost 2.06) | VERIFIED | - |
| 01 Fit: "fewer sales in early 2020 (2 BAC, 1 USB, 2 CSX at most)" | trades_{BAC,USB,CSX,OXY}.csv; data/real/earnings first dates; audit L40-41 (CSX 37 → 38) | WRONG | Under option (a), 6 sales are blocked directly: BAC 2, USB 1, CSX 2, OXY 1 (expiry 02-21 < first date 02-27). "At most" is also wrong. Later sales can shift by path: CSX's blocked 02-21 assignment leaves its cost basis at the first close, and diag shows CSX net +1. The other 13 lose no sale, because every sale from 2020-01-06 on expires on or after 2020-02-21 (01-17 is 11 DTE, outside 30-45 ± 7), which is on or after their first date. I2 measures the change |
| 01 OQ1(a): fail-closed equals "no sale before the first listed date"; it also blocks some calls that are probably fine (OXY) | ccbot/realtest.py L482-488; OXY source above | VERIFIED | - |
| 01 OQ1(b): "the ticker's own shortest listed interval (about 90 d here)" | data/real/earnings/VALE.csv rows 4-5 (2021-03-04 → 04-27 = 54 d) | WRONG | About 90 d holds for BAC/CSX/USB (90-92 d). VALE's shortest interval is 54 d at most. Option (b) is not chosen (map step 1) |
| 01 OQ2: the edge must be computed in simulate (load_ticker has no start), and the warning needs a path into summarize/summary.json | ccbot/realtest.py L134, L385-402, L577-596, L745-747 | VERIFIED | - |
| 01 OQ3: `_tiny` lead 151 d; the control sales in L216, take50, sub-3c "and L380" become EARNINGS_UNKNOWN | tests/test_realtest.py L193-210, L213-254, L379-383; ccbot/realtest.py L429, L482 | WRONG | L216, L237 and L251 move. L380 (`test_premium_yield_na_zero_years`) does not: with `end=2024-01-02` there is one day, `nxt` is None, and no sale is attempted (L482), so its asserts (years 0, yield NaN) are unchanged. 151 d verified (Self-check row 4) |
| 01 OQ3: REAL_BAC (calls_sold 24, rej_EARNINGS_UNKNOWN 20 under BOT_RULE) must be re-measured | tests/test_realtest.py L389-414; summary.json L97, L107 | VERIFIED | - |
| 01 OQ3: `_make` fixtures (first earnings 2019-01-25, 23 d after 2019-01-02) are unaffected | tests/test_realtest.py L28, L41 (earliest weekday ≥ 25 in Jan 2019 = Fri 01-25); any sale from 01-02 to 01-24 expires ≥ 2019-02-15 > 01-25, so it is already EARNINGS_BLACKOUT; no `_make` test pins rej counts (L86-126, L273-305) | VERIFIED | Only the code moves (BLACKOUT → UNKNOWN); no sale. I2 confirms by run |
| 01 OQ4: interior gaps > 120 d (CMCSA, MDLZ, MO, T, VZ) still only warn and sell; out of 063's scope | summary.json L158, L290, L312, L400, L444; ccbot/realtest.py L183-185 | VERIFIED | Stated out of scope in the map (note under step 7) |
| 02 Past logs 1: A1 found the hole and proposed this item and the > 120 d fixture; accepted for 061 as labelled in research text only | logs/audit/2026-11-14-061.md L42-45, L72-80 | VERIFIED | - |
| 02 Past logs 2: 247 comes from diag_keep earn (BAC 24→22, USB 11→10, OXY 8→7, CSX 37→38); "it also touches interior gaps (OXY), so it is not a leading-edge measurement" | logs/audit/2026-11-14-061.md L40-41; see F17 row | WRONG | The shifts are verified. OXY's shift is leading-edge (F17 row). The diag rule is the edge rule plus interior-gap blocking, and the interior part changed no calls_sold count |
| 02 Past logs 3: RI-002 root cause, guardrails enumerate the bot's inputs, and the GUARDED condition | logs/recurring-issues.md L25-36 | VERIFIED | - |
| 02 Past logs 4: RI-001 applies; the request's threshold catches 0 of 4 | 01 § Numbers (verified above) | VERIFIED | - |
| 02 Past logs 5: no earlier attempt; "grep of logs/ ... only the 061 audit and RI-002" | Grep `first earnings\|leading edge\|leading-edge` in logs/ → 3 files | WRONG | A third file matches: logs/audit/2026-11-14.md L31 (the daily-audit row that opened 063). "No earlier fix attempt" still holds |
| 02 FOR 1: use the fail-closed rule, add a ~100 d fixture that fails under a threshold-only rule, run the mutation against both | 01 § Numbers, F8, F10-F12 (verified) | VERIFIED | Built into map steps 1 and 4 |
| 02 FOR 2: mirror clause `td.earnings[0] <= d` in `_earnings_known`, same EARNINGS_UNKNOWN code; lead/warning computed in simulate and carried via df.attrs into summarize | ccbot/realtest.py L372-374, L483-484, L515-523, L591-595 | VERIFIED | - |
| 02 FOR 3: "at most 5 sales change among the 17 ... plus each other ticker's first 16-52 days" | see the 01 Fit row | WRONG | 6 sales are blocked directly (OXY too). Path effects can add or remove later ones. For the other 13, the first days change code (BLACKOUT → UNKNOWN) but lose no sale under the bot rule. Grid variants (14-24 DTE) can lose sales; I2 measures them |
| 02 FOR 3 / Holes 4: "I2 should report the measured count and not expect about 247" | see the F17 row | WRONG | 247 is the expected total under option (a): the diag lookback covers the same leading-edge days, and its interior-gap part changed no ticker's calls_sold. I2 measures it per ticker and explains any difference from 247 |
| 02 AGAINST 1: dropping Feb-Mar 2020 sales shifts the sample for a data reason; both arms start at days[0] | ccbot/realtest.py L400-407 | VERIFIED | Label required (map step 6) |
| 02 AGAINST 2: option (a) blocks probably-fine sales; "OXY (52 d) and PBR (44 d) lose sales"; OXY date UNVERIFIED | OXY source above; summary.json L24 (PBR skipped) | UNSUPPORTED | Kept with a correction. OXY loses one sale that held no report (Q4 2019 on 2020-02-27). PBR is skipped by min_years, so it has no reported result to lose. This cost is accepted to keep unknown as unknown (RI-002) |
| 02 AGAINST 3: strict edge vs lax interior gaps; existing tests move; I1 lists fixture edits; I3 checks no assertion loosened | tests/test_realtest.py L213-254, L389-418 | VERIFIED | L380 excluded (see 01 OQ3 row). Map step 5 |
| 02 Holes 2: "data start" must be the first sale day, because price start or `min(td.chain)` "make all 21 warn" | ccbot/realtest.py L396-402; 01 § Numbers | WRONG | Under option (a), the block does not depend on "data start" at all (`d < earnings[0]`). The first sale day (`days[0]`) only sets the lead in the warning. With `days[0]`, all 21 stocks also get a warning (every lead is 16-113 d > 0). The information is in the lead value and in rej_EARNINGS_UNKNOWN, not in whether a warning exists |
| 02 Findings by language: N/A, no non-English source | 01/02 sources are all English (company releases, SEC, DoltHub, repo) | VERIFIED | - |
**Totals:** 49 rows checked → **34 VERIFIED as-is**, **12 fixed**, **3 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)

## Removed claims
1. 01 F6: the date of the one 2019 option snapshot (UNVERIFIED; the map does not need it).
2. 01 F13: VALE's Q4 2019 report date (UNVERIFIED; VALE is skipped by min_years).
3. 01 F14: why the DoltHub earnings history starts in 2020 (UNVERIFIED; the rule does not depend on the cause).

## Decision on the threshold (01 open question 1)
Option (a), fail closed: a stock day before its first listed earnings date is EARNINGS_UNKNOWN. Reasons:
- The request's 120-day bar catches 0 of the 4 known cases (max lead 113 d).
- Option (b) infers "no report" from cadence. That is a filled-in value, the RI-002 root cause, and its "about 90 d" fails for VALE (54 d).
- Option (c) also changes interior gaps, which is out of scope.

Cost: 1 OXY sale that held no report (OXY reported 2020-02-27). Request § What we want allows "blocked (EARNINGS_UNKNOWN) or at least flagged". (a) does both.

## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | Script, ccbot/realtest.py `_earnings_known`: add the leading-edge clause: `bool(td.earnings) and td.earnings[0] <= d and td.earnings[-1] >= d`. Docstring: "a listed date on or before d (no unlisted history) and one on or after d". No threshold constant | `td.earnings` (sorted, load_ticker L182), day `d` | EARNINGS_UNKNOWN (existing code, counted in `rej_EARNINGS_UNKNOWN`) on every stock day before the first listed date | New tests T1 and T2 (step 4) pass. Mutation in 05/06 (scratch copy): delete `td.earnings[0] <= d and` → T1 and T2 fail. Second mutation: replace it with `(td.earnings[0] - d).days <= EARNINGS_GAP_WARN and` (the request's threshold) → T1 fails | Days left to sell (first listed date to period end 2026-11-12): 17 of 17 reported tickers have a non-empty window. Blocked calendar days = lead: 16-107 d for the 17, max CSX 107 of 2,502 days (2020-01-06 to 2026-11-12). Measured by reading row 2 of each data/real/earnings/*.csv plus date arithmetic (Self-check rows 1, 2, 12). Directly blocked bot-rule sales: 6 (BAC 2, USB 1, CSX 2, OXY 1). An empty day has a reason code: EARNINGS_UNKNOWN, counted. Snapshot-day count: I2 measures it as REAL_BAC rej_EARNINGS_UNKNOWN (step 5) |
| 2 | Script, `simulate`: after `days` is set (L400-402), compute `lead = (td.earnings[0] - days[0]).days` for a stock with earnings. Put `earnings_lead_days` in `df.attrs["counts"]`: `max(lead, 0)` as an int; NaN for an ETF or a stock with no dates (never 0, RI-002). When lead > 0, set `df.attrs["warnings"] = ["earnings: first listed date <first> is <lead> days after the first quote day <days[0]>; no call sold before it (EARNINGS_UNKNOWN)"]`. A stock with no dates at all gets `"earnings: no dates (EARNINGS_UNKNOWN for a stock)"` when load_ticker has not already warned "not supplied" (an empty file has no warning today, L182) | `td.earnings`, `td.asset_type`, `days[0]` | `earnings_lead_days` in counts (so it reaches summary.json `counts_bot_rule_bid` via L745 and grid_in_sample.csv via L764); `df.attrs["warnings"]` | T1: `earnings_lead_days == 100` and the warning holds "100 days". T2: 151. Control fixtures: 0 and no edge warning. ETF test (`test_etf_without_earnings_sells`): `math.isnan(earnings_lead_days)`. Tests assert the numeric field, not only the text (RI-012) | – |
| 3 | Script, `summarize` L595: `"warnings": "; ".join(td.warnings + df.attrs.get("warnings", []))`. load_ticker is unchanged, so `test_simulate_no_lookahead_and_accounting` L88 (`not td.warnings`) still holds | `td.warnings`, `df.attrs["warnings"]` | the warning in bot_rule_by_ticker.csv and summary.json `counts_bot_rule_bid[tk]["warnings"]` | T3: in `test_run_end_to_end`, add `assert "first listed date" in s["counts_bot_rule_bid"]["AAA"]["warnings"]` and `s["counts_bot_rule_bid"]["AAA"]["earnings_lead_days"] == 23` (`_make`: 2019-01-02 → 01-25). This shows the warning reaches summary.json (request § What we want) | – |
| 4 | Tests, tests/test_realtest.py. T1 `test_leading_edge_100_days_blocks`: `_tiny(earnings=[date(2024, 4, 11)])` (lead 100 ≤ 120, expiry 02-16 before it) → `tr == []`, `rej_EARNINGS_UNKNOWN == 1`, `rej_OK == 0`, lead 100. T2 `test_leading_edge_151_days_blocks`: `_tiny(earnings=[date(2024, 6, 1)])` → same with lead 151 (the request's > 120 d fixture). REALTEST_MISSING gets the row `"earnings_before_first": "EARNINGS_UNKNOWN before a stock's first listed earnings date; warning with the lead in days"`. DROP_CASES and `test_realtest_missing_lists_every_input` L312 gain that key (the set is extended, not loosened). `test_drop_input` gets its case: AAA earnings rows before 2019-07-01 dropped → no trade with `open_date` before the new first date, `rej_EARNINGS_UNKNOWN > 0`, warning present | `_tiny`, `_copy`, data_root | 3 new test cases + 1 drop case | All pass on the built code. Both step-1 mutations fail them as stated. The drop case fails with the step-1 clause removed | – |
| 5 | Tests, existing fixture edits (no assertion changed): add the prior date `date(2023, 10, 25)` to the control earnings in L216, L237, L251 (`earnings=[date(2023, 10, 25), date(2024, 6, 1)]`), so each control stays a control. L380 is unchanged. Re-measure REAL_BAC (all 3 rules) on data/real and pin the new values, plus `earnings_lead_days=100` | data/real (committed), BAC | updated REAL_BAC dict | I3 diffs tests/test_realtest.py: only the earnings tuples in L216/L237/L251 and the REAL_BAC numbers and new key change; no `assert` line removed or loosened. L418 (`all(v > 0 ...)` for BOT_RULE) still passes. Expected BOT_RULE calls_sold 22 (diag); I2 measures it and explains any other value | BOT_RULE REAL_BAC must keep every non-INFO count > 0 (L417-418): checked by that test |
| 6 | Report (05 only; reports/real/ is not re-published, see Open questions): I2 runs `python3 -m ccbot.realtest --out <scratch dir>` and states in 05 the per-ticker calls_sold before/after for the 17 tickers, the total (expected 247: BAC 22, USB 10, OXY 7, CSX 38, others unchanged), any A-row change per ticker, and the summary.json warning lines for BAC/CSX/USB/OXY. The dropped Feb-Mar 2020 sales are labelled "stock only, no sale (earnings unknown)": a data effect, not a strategy result | data/real | 05 text | Numbers in 05 come from the scratch run's summary.json (paste the lines). Any total other than 247 is explained per ticker | – |
| 7 | Process (needs the person's OK in PR review): .claude/agents/r3-fact-checker.md step 1b and .claude/agents/i3-verifier.md step 3 (RI-002 sentence) add: "For any data-hole check, check the edges of the data window (before the first value and after the last) as well as gaps between values." | the two agent files | 2 one-sentence additions | `Grep "edges of the data window" .claude/agents` → 2 files; `git diff` shows additions only | – |

Out of scope (stated, not built): interior gaps over 120 d (CMCSA, MDLZ, MO, T, VZ) still only warn and still sell. The report would treat the two kinds of hole differently. A1 may open a follow-up item. No rule the person follows (001) changes: realtest is research only. Live-bot code (rules/screen/missing) is not touched.

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| data/real/earnings/<T>.csv (load_ticker L177) | file missing | unchanged: EARNINGS_UNKNOWN every day for a stock; warning "earnings: not supplied (EARNINGS_UNKNOWN for a stock)"; `earnings_lead_days` NaN (not 0) |
| same file, 0 rows | empty | EARNINGS_UNKNOWN every day (`bool(td.earnings)` False); new warning "earnings: no dates (EARNINGS_UNKNOWN for a stock)"; `earnings_lead_days` NaN |
| first listed date (earnings[0]) vs first quote day (simulate days[0]) | history before the first listed date | EARNINGS_UNKNOWN on each stock day before it; warning "earnings: first listed date <date> is <n> days after the first quote day <date>; no call sold before it (EARNINGS_UNKNOWN)"; `earnings_lead_days` = n |
| first listed date after the period end | the whole window is unknown | EARNINGS_UNKNOWN on every day, counted; same warning with its lead; 0 calls sold (shown, not filled). Today 0 of 17 tickers |
| asset_type etf (SPY) | earnings not used | rule not applied (L483); `earnings_lead_days` NaN; no warning |
| interior gap > 120 d | dates missing between listed dates | unchanged: warning "earnings: N gap(s) > 120 days between dates"; sales still allowed (out of scope, stated) |

Step 3a screen check: not applicable. realtest is a backtest, and no ticker is reported as passing `ccbot/screen.TESTS`. No PASS is claimed for any ticker here.

## Open questions (for the person, via the daily report)
1. Should the regenerated `reports/real/` (with the new warning and the about 247-call counts) be committed? The request asks for the warning "in reports/real/" but also says 061's numbers are not re-published here. The map proves the path with test T3 and a scratch run (step 6). Committing the regenerated reports is the person's call.
2. Interior-gap asymmetry: follow-up item or leave as labelled?

## Self-check
Re-derive every numeric threshold in the map from that step's "How we check it" formula, and run every worked example against the trigger of the rule it shows. Show the arithmetic.
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Lead BAC/USB = 100 (steps 1, 5) | first listed − first quote day | 2020-01-06 → 04-15: 25 (Jan 7-31) + 29 (Feb, leap) + 31 (Mar) + 15 = 100 | 100 ✓ (REAL_BAC pin) |
| Lead CSX 107, OXY 52 (step 1) | same | CSX 25 + 29 + 31 + 22 = 107; OXY 25 + 27 = 52 | ✓ |
| Quarterly spacing (decision) | next − previous | BAC 15 + 31 + 30 + 16 = 92, 15 + 31 + 30 + 14 = 90; CSX 8 + 31 + 30 + 22 = 91, 9 + 31 + 30 + 21 = 91; USB 15 + 31 + 30 + 15 = 91, 16 + 31 + 30 + 14 = 91 | ✓ |
| T2 fixture lead 151 > 120 (step 4) | 2024-01-02 → 2024-06-01 | 29 + 29 (Feb 2024 leap) + 31 + 30 + 31 + 1 = 151; 151 > 120 | the request's > 120 d fixture ✓ |
| T1 fixture: lead 100 ≤ 120, so a threshold rule sells and T1 fails it (step 1 second mutation) | 2024-01-02 → 2024-04-11 | 29 + 29 + 31 + 11 = 100 ≤ 120 → threshold clause True → sells → `tr == []` fails ✓. New rule: earnings[0] 04-11 > 01-02 → EARNINGS_UNKNOWN ✓. Old code: earnings[-1] 04-11 ≥ 01-02 → known; [01-02, 02-16] holds no date (04-11 > 02-16) → sells 1 → T1 fails with the clause removed ✓ | ✓ |
| Control fixtures still sell (step 5) | earnings[0] ≤ d and earnings[-1] ≥ d and no date in [d, expiry] | 2023-10-25 ≤ 2024-01-02 ✓; 2024-06-01 ≥ 01-02 ✓; no date in [01-02, 02-16] ✓; pick: expiry 02-16 = 45 DTE in [30, 45]; strike 11 Δ0.28, nearest 0.275 among {0.45, 0.28, 0.21, 0.12}, inside [0.20, 0.35]; bid 0.30 > 0 → sale, strike 11 (L217 assert unchanged); lead = max(2023-10-25 − 2024-01-02, 0) = 0 → no edge warning | ✓ |
| L380 unaffected (fact-check fix) | a sale needs `nxt is not None` (L482) | `end=2024-01-02` → days = [01-02] → i = 0, nxt = None → no attempt; tr = [], years 0 | unchanged ✓ |
| `_make` lead 23 (step 3, T3) | 2019-01-02 → 2019-01-25 | 25 − 2 = 23 (same month) | 23 ✓ |
| `_make` loses no sale (01 OQ3 row) | pre-first-date sale has expiry ≥ first date → BLACKOUT already | from 2019-01-02 the 30-45 (±7) DTE monthly is 2019-02-15 (44 DTE) or later; 02-15 ≥ 01-25 | only the code changes ✓ |
| Expected total 247 (step 6) | 250 + Σ per-ticker shift (diag) | 250 − 2 (BAC) − 1 (USB) − 1 (OXY) + 1 (CSX) = 247 | ✓ expectation; I2 measures |
| 6 directly blocked bot-rule sales (step 1) | d < first date and expiry < first date | BAC 01-06 → 02-21 and 02-21 → 03-20 (< 04-15); USB 01-06 → 02-21 (< 04-15); CSX 01-06 → 02-21, 02-21 → 03-20 (< 04-22); OXY 01-06 → 02-21 (< 02-27) → 2 + 1 + 2 + 1 = 6. Others: first date ≤ 02-06 (BMY, the latest among the remaining 13) ≤ 02-21, the earliest expiry from 01-06 (01-17 is 11 DTE < 30 − 7) → already BLACKOUT | 6 ✓ |
| Period length 2,502 d (step 1 feasibility) | 2020-01-06 → 2026-11-12 | 366 + 365 + 365 + 365 + 366 + 365 = 2,192 to 2026-01-06; + 25 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31 + 12 = 310 → 2,502; CSX blocked 107 / 2,502 = 4.3% | ✓ |

Recurring issues checked:
- RI-001: every count in the Feasibility column is computed with its source. The request's 120 d bar is measured (0 of 4) and replaced.
- RI-002: unknown stays unknown. `earnings_lead_days` is NaN, never 0, when there are no dates. The edge blocks with EARNINGS_UNKNOWN. The guardrail (T1/T2 plus mutations) is in the map. This item meets RI-002's GUARDED condition when merged.
- RI-004: the T1/T2/control fixtures are checked against the rule's trigger, not only the arithmetic.
- RI-005: Self-check above.
- RI-006: counts come from check_handoff.py (PASS, pasted below).
- RI-007: Scope FULL, code changes go through I1-I3, R3 changed no code, and no 07 is needed.
- RI-008: I2 keeps 3.10-compatible syntax.
- RI-010: R3 wrote no log line by hand. The orchestrator writes it with `check_pipeline.py --log`.
- RI-012: tests assert the numeric field, not only the warning text.
- RI-003, RI-009, RI-011: GUARDED and not touched by this item.

`python3 scripts/check_handoff.py 063` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 4
fact-check rows: 49
totals line: 49 rows -> 34 as-is, 12 fixed, 3 removed
PASS
```
