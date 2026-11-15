# 03 Research hand-off - 065
Status: READY

Checked 2026-11-15 on branch daily-fixes/2026-11-15 (working tree carries 063's code from daily-fixes/2026-11-14: `_earnings_known` has the leading-edge clause, realtest L376-379). Repo read only; no repo file changed by R3 except this file and its log line. Mutations and the prototype ran on a scratch copy (`/tmp/claude-0/-home-claude/6c90b420-11c2-5be4-a1cd-f96b977ade9c/scratchpad/r3-065`). No brokerage contacted. Research, not financial advice.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| 01 F1: `load_ticker` counts interior gaps `> EARNINGS_GAP_WARN` and only warns; constant 120; count goes to `td.earnings_gaps` / summary `earnings_gaps_gt120`; nothing reads it in the sale decision | ccbot/realtest.py L62, L185-187, L229, L608, L762; Grep `earnings_gaps` → no use in simulate | VERIFIED | - |
| 01 F2: `_earnings_known` = `bool(td.earnings) and td.earnings[0] <= d and td.earnings[-1] >= d`; a day inside an interior hole returns True | ccbot/realtest.py L376-379 | VERIFIED | - |
| 01 F3: `_earnings_between` only finds listed dates, so inside a hole the sale gets OK | ccbot/realtest.py L372-373, L497-502 | VERIFIED | - |
| 01 F4: trailing edge is covered by `test_stock_without_earnings_sells_nothing` (earnings [2023-10-01]); the mutation is UNVERIFIED | tests/test_realtest.py L223-229; R3 mutation on scratch copy: `td.earnings[-1] >= d` removed → `4 failed, 39 passed` (`test_stock_without_earnings_sells_nothing` + 3 `test_real_counts_bac` params) | UNSUPPORTED | Kept, now verified by run: the trailing-edge mutation fails 4 tests |
| 01 F5: the 3 controls use [2023-10-25, 2024-06-01] (220 d) and sale day 2024-01-02 is inside it | tests/test_realtest.py L219, L274, L288; Grep `earnings=` → no other two-date fixture | VERIFIED | - |
| 01 F6: `_make` dates are about 91 d apart, no gap > 120 (UNVERIFIED) | tests/test_realtest.py L27-42, computed in scratch: 13 dates 2019-01-25 → 2022-01-25, intervals 90-94 d | UNSUPPORTED | Kept, now verified: max interval 94 d ≤ 120, so `_make` tests are unaffected |
| 01 F7: CMCSA/MO 2021-10-28→2022-04-28 (182), T 2021-10-21→2022-04-21 (182), VZ 2021-10-20→2022-04-22 (184), MDLZ 2021-11-02→2022-04-26 (175); no other gap > 120 in these files | data/real/earnings/*.csv, all 22 files computed in scratch (SPY empty; AAL, BAC, BMY, CSX, F, HBAN, KEY, KGC, KMI, OXY, PFE, PYPL, USB: 0 gaps > 120) | VERIFIED | - |
| 01 F8: ITUB 2 gaps (182, 177) | data/real/earnings/ITUB.csv (computed) | VERIFIED | - |
| 01 F9: VALE 4 gaps (177, 133, 181, 180); 2021-10-27→2022-02-24 exactly 120, not counted (`>`) | data/real/earnings/VALE.csv (computed); realtest L185 | VERIFIED | - |
| 01 F10: PBR 7 gaps 172, 192, 208, 246, 126, 186, 178 | data/real/earnings/PBR.csv (computed) | VERIFIED | - |
| 01 F11: ITUB/PBR/VALE skipped "option quotes only 2020-01-06 to 2020-12-02 (< 3.0 years)"; in-window gaps ITUB 0, VALE 2, PBR 2 | reports/real/summary.json L21-25; gap dates above | VERIFIED | - |
| 01 F12: Comcast Q4/FY2021 results dated January 27, 2022 | https://www.sec.gov/Archives/edgar/data/1166691/000116669122000004/ex991-12312021.htm ("PHILADELPHIA - January 27, 2022") | VERIFIED | - |
| 01 F13: Altria Q4 2021 results dated January 27, 2022 | https://www.sec.gov/Archives/edgar/data/764180/000076418022000007/exhibit991erq42021.htm ("RICHMOND, Va. - January 27, 2022") | VERIFIED | - |
| 01 F14: Mondelez Q4/FY2021 results dated January 27, 2022 | https://www.sec.gov/Archives/edgar/data/1103982/000119312522019794/d298614dex991.htm ("CHICAGO, Ill. – January 27, 2022") | VERIFIED | - |
| 01 F15: Verizon Q4 2021 results dated January 25, 2022 | https://www.verizon.com/about/sites/default/files/Verizon-ends-2021-with-strong-wireless-service-revenue-and-eps-growth-1-24-22.pdf | VERIFIED | - |
| 01 F16: AT&T scheduled Q4 2021 results for January 26, 2022; whether it reported that day UNVERIFIED | https://businesswire.com/news/home/20211227005003/en/ATT-to-Release-Fourth-Quarter-2021-Earnings-January-26-2022 (scheduled); https://www.sec.gov/Archives/edgar/data/732717/000073271722000010/t-20220126.htm (8-K Item 2.02: "The registrant announced on January 26, 2022, its results of operations for the fourth quarter of 2021") | UNSUPPORTED | Kept with a new source: AT&T reported Q4 2021 on January 26, 2022. All 5 US holes hide a real report |
| 01 F17: real dates hidden in the ITUB/VALE/PBR gaps; whether PBR's 126-d gap hides a report | none (R1 labelled UNVERIFIED) | UNSUPPORTED | Removed. All three are skipped (F11), and the rule does not depend on it |
| 01 F18: MO 2022-01-19→02-18 $52.5 expired (holds the 01-27 report); 2022-02-23→04-14 $55 expired, no report in life | reports/real/trades_MO.csv rows 6-7; MO earnings: next listed 2022-04-28 > 04-14 | VERIFIED | - |
| 01 F19: MDLZ 4 sales inside its hole: 11-03→12-17 $65 expired; 12-22→01-21 $66 assigned; 01-24→02-18 $70 expired (holds 01-27); 02-23→04-14 $70 expired | reports/real/trades_MDLZ.csv rows 13-16 | VERIFIED | - |
| 01 F20: CMCSA, T, VZ open no sale 2021-10 to 2022-04 | Grep `^(2021-(0[7-9]\|1[0-2])\|2022-0[1-5])` in their trades files: CMCSA last pre-hole sale expires 2021-10-15 < 10-28; T, VZ none | VERIFIED | - |
| 01 F21: 6 current sales inside a hole, 2 held a real report (MO 01-19, MDLZ 01-24); reports/real not regenerated by 063, which changed none of these 5 | F18-F19; `git log -- reports/real` last 6d7d78f 2026-11-14 05:11 (before 063); work/063/05 L146-159 (delta 0 for CMCSA, MDLZ, MO, T, VZ) | VERIFIED | - |
| 01 Numbers: every gap interval (CMCSA … PBR) | computed in scratch from the files (Self-check row 1) | VERIFIED | - |
| 01 Numbers: "PBR's other intervals: 85, 78, 118, 71, 84, 98, 67, 80, 98, 119 (all ≤ 120)" | data/real/earnings/PBR.csv: all 20 intervals 85, 172, 192, 78, 208, 246, 118, 71, 84, 98, 126, 67, 80, 98, 186, 178, 119, 67, 87, 96 | WRONG | PBR has 13 intervals ≤ 120, not 10: the list misses 67, 87, 96 (after 2025-11-06). "All ≤ 120" still holds |
| 01 Numbers: normal spacing for the 5 US names is at most about 100 d | computed: max interval ≤ 120 is CMCSA 100, VZ 100, MO 98, T 98, MDLZ 98 | VERIFIED | - |
| 01 Numbers: control gap 220; replacement [2023-10-25, 2024-02-20] = 118, 02-20 after the 02-16 expiry | arithmetic (Self-check row 3) | VERIFIED | - |
| 01 Numbers: direct effect MO -2, MDLZ -4, others 0; not the new counts (MDLZ's assigned call shifts its path) | R3 prototype of the map's helper on data/real, BOT_RULE from 2020-01-06: MDLZ 34 → 31 (drops 11-03, 12-22, 01-24, 02-23 in the hole plus 2022-05-04 and 2022-11-30 by path; adds 2022-04-27, 07-27, 11-02), MO 23 → 21, CMCSA 12, T 1, VZ 3 unchanged | VERIFIED | - |
| 01 Fit: live bot not affected (snapshot `next_earnings` → EARNINGS_UNKNOWN) | ccbot/missing.py L13 | VERIFIED | - |
| 01 Fit: MO/MDLZ spots about $50-67 in these trades, so 100 shares exceed a $3k account; backtest uses fractional shares | trades rows above (spot 50.09-67.61); 100 × 50.09 = $5,009 > $3,000; realtest L391-399 docstring | VERIFIED | - |
| 01 Fit: CMCSA, T, VZ keep their calls_sold; ITUB/PBR/VALE reports do not change | prototype above; F11 | VERIFIED | - |
| 01 OQ1: options (a) fail closed, (b) label only, (c) cadence estimate; (c) needs the person's decision (RI-002 038/040) | logs/recurring-issues.md L45 (038: last report + 70 d, settled by the person); ccbot/missing.py L15 | VERIFIED | Decision below: (a) |
| 01 OQ2: one bracketing helper covers all three edges; the overlap test reduces to "d strictly inside the gap", because a life [d, exp] with d ≤ a contains a and is already EARNINGS_BLACKOUT; keeps 063's edge at any length | ccbot/realtest.py L372-379, L497-502; logic in Self-check row 6; prototype: BAC 22/60 and CSX 38/58 (calls/UNKNOWN) unchanged | VERIFIED | - |
| 01 OQ3: REAL_BAC pins should not change (UNVERIFIED until run) | BAC has no gap > 120 (F7), so the helper equals the current rule on every BAC day; prototype BOT_RULE BAC 22 calls, 60 UNKNOWN = REAL_BAC L456 | UNSUPPORTED | Kept with a new source (prototype + logic). I2 still runs the 3 REAL_BAC params |
| 01 OQ4: 120 d separates the 5 US holes (175-184) from normal spacing (≤ 100); ADR intervals sit on both sides (VALE 120 not flagged, PBR 118/119 not, 126 flagged) | computed above | VERIFIED | Recorded as a known limit (map note) |
| 02 Past logs 1: audit L65-67 asks for this follow-up; L61-64 found a mislabelled "path effect" in 063 | logs/audit/2026-11-15-063.md L61-67 | VERIFIED | - |
| 02 Past logs 2: 063/02 AGAINST 3 predicted the asymmetry; 063 added `td.earnings[0] <= d`; M1 made 6 tests fail | work/063/02-improvements.md L39-40; work/063/05 L107-115 (I2: 6 failed); logs/audit/2026-11-15-063.md L33-35 (A1: 6 failed) | VERIFIED | - |
| 02 Past logs 3: RI-002 ESCALATED, root cause "into a number (or into 'OK')", 038 cadence estimate allowed only as the person's labelled house rule (040) | logs/recurring-issues.md L25, L26, L45 | VERIFIED | - |
| 02 Past logs 4: RI-001; 063's 120-d leading bar caught 0 of 4; here 120 is counted | work/063/03-handoff.md (01 Numbers row: max lead 113 < 120); Self-check row 2 | VERIFIED | - |
| 02 Past logs 5: R2 logged `languages: N/A` for 063 and 064 | logs/research/2026-11-14.md L5, L7 | VERIFIED | - |
| 02 FOR 1: `td.earnings` is sorted/de-duplicated so `bisect` is safe; a/b bracketing helper; three mutations with the named tests | realtest L184; 063/05 L107-115 (mutation (i) list = M1's 6 tests); R3 trailing-edge run (mutation (ii) → 4 failed) | VERIFIED | Map steps 1, 4 |
| 02 FOR 2: the fixture must have the sale day strictly inside and no listed date in [d, expiry]; pin 120 sells / 121 blocks; controls get the 118-d pair, assertions unchanged | realtest L497-502; Self-check rows 3-5 | VERIFIED | Map step 4-5 |
| 02 FOR 3: separate per-stock count; a new REALTEST_MISSING row is forced by the enumeration test; warning text pattern of L415-416 | realtest L65-77 (the comment at L65-67 names the test), L413-416; tests/test_realtest.py L295-297, L372-376 (the test compares a literal key set with REALTEST_MISSING and DROP_CASES, so a new row fails until both are extended) | VERIFIED | Map steps 2-4 |
| 02 FOR 3 cost: at most 6 sales blocked directly (MO 2, MDLZ 4), CMCSA/T/VZ none; removes the 2 sales that crossed a real report | F18-F21; prototype | VERIFIED | - |
| 02 AGAINST 1: MDLZ path changes beyond the hole; both arms start at `days[0]` "L401-405" | prototype (MDLZ drops 2022-05-04 and 2022-11-30 outside the hole and adds 3); ccbot/realtest.py L419-420 (`c0 = close[days[0]]`, `sh_cc = sh_bh = 1.0 / c0`) | WRONG | Claim holds, but the line cite is wrong: L419-420, not L401-405 |
| 02 AGAINST 2: PBR's 7 gaps add to 1308 d, "all of which would be EARNINGS_UNKNOWN" | 172+192+208+246+126+186+178 = 1308; the listed end dates are known days, so the unknown days are those strictly inside: Σ(gap − 1) = 1308 − 7 = 1301 | WRONG | 1301 calendar days would be EARNINGS_UNKNOWN. PBR is skipped today, so no report changes |
| 02 AGAINST 3: the same quarter missing for all 5 names makes a source/fetch problem "more likely" (UNVERIFIED, fetch code not examined) | none | UNSUPPORTED | Removed as a claim. The follow-up stands on F12-F16 alone (real reports exist on 2022-01-25..27); see Out of scope |
| 02 Findings by language: N/A, no non-English source | all 01/02 sources are English (SEC, company sites, Business Wire, repo) | VERIFIED | - |
**Totals:** 46 rows checked → **37 VERIFIED as-is**, **7 fixed**, **2 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)

## Removed claims
1. 01 F17: the real report dates hidden in the ITUB, VALE and PBR gaps, and whether PBR's 126-d gap hides a report (UNVERIFIED; all three are skipped by min_years, and the rule does not depend on it).
2. 02 AGAINST 3: "a source or fetch problem is more likely than 5 unrelated gaps" (UNVERIFIED reasoning; the follow-up below does not need it).

## Decision: block or label (request § What we want; 01 open question 1)
**Block (option a, fail closed).** A stock day strictly inside an interior gap > EARNINGS_GAP_WARN is EARNINGS_UNKNOWN: no sale. I1 restates this in 04 and I2 in 05, so the person sees it.
- All 5 US holes hide a real, sourced report (Jan 25-27, 2022; F12-F16), and 2 current sales held a call through one (MO 2022-01-19, MDLZ 2022-01-24).
- (b) label-only keeps those 2 calls in P&L. That is RI-002's "missing read as no earnings", only made visible.
- (c) a cadence estimate is a filled-in value. It needs the person's house-rule decision (RI-002 038/040), and it is not taken here.
- Cost (accepted, labelled): 4 blocked sales crossed no report, and MDLZ's path shifts (expected MDLZ 34 → 31, MO 23 → 21). Labelled "stock only, no sale (earnings unknown)", as in 063.

## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | Script, ccbot/realtest.py: one helper `_earnings_state(td, d)` returns `"known"`, `"before_first"`, `"after_last"` or `"interior_gap"`. With `i = bisect_right(td.earnings, d)`: no dates or i == 0 → before_first (no dates: before_first, the existing "no dates" warning stays); `td.earnings[i-1] == d` → known; i == len → after_last; `(td.earnings[i] - td.earnings[i-1]).days > EARNINGS_GAP_WARN` → interior_gap; else known. `_earnings_known(td, d)` becomes `_earnings_state(td, d) == "known"`. The sale path (L497) is unchanged otherwise. Docstring names all three edges and item 065 | `td.earnings` (sorted, unique, L184), d, EARNINGS_GAP_WARN | EARNINGS_UNKNOWN (existing code) on every stock day strictly inside a gap > 120 d, plus the 063 edges as before | Steps 4-5 tests pass. Mutations in 05/06 (scratch copy), each must fail ≥ 1 test: (i) i == 0 treated as known → the 6 M1 tests of 063; (ii) i == len treated as known → `test_stock_without_earnings_sells_nothing` + REAL_BAC (R3 ran the old-code equivalent: 4 failed); (iii) gap check removed → T-gap180 and T-gap121; (iv) `>` changed to `>=` → T-gap120 | Days left to sell: 5 of 5 affected reported tickers keep a non-empty window (the hole is 175-184 of 2,502 days, 2020-01-06 → 2026-11-12). Blocked calendar days strictly inside: CMCSA 181, MO 181, T 181, VZ 183, MDLZ 174. Directly blocked bot-rule sales: 6 of 6 in-hole sales (MO 2, MDLZ 4), from reports/real/trades_*.csv. Prototype (scratch, BOT_RULE): calls CMCSA 12, MDLZ 31, MO 21, T 1, VZ 3; other 12 reported tickers unchanged (no gap > 120). Empty day: EARNINGS_UNKNOWN, counted (step 2) |
| 2 | Script, `simulate`: count attempt days whose EARNINGS_UNKNOWN came from `"interior_gap"` as `earnings_gap_days` in `df.attrs["counts"]` (int for a stock with dates; NaN for an ETF or a stock with no dates, never 0, as `earnings_lead_days`). Add it to the per-ticker column list next to `earnings_gaps_gt120` (L762) so it reaches summary.json and grid_in_sample.csv. When `td.earnings_gaps > 0`, add to `df.attrs["warnings"]`: "earnings: gap(s) > 120 days between listed dates (<a>→<b>, ...); no call sold inside them (EARNINGS_UNKNOWN)" if `rule.skip_earnings`, else "...; earnings not checked by this rule" (pattern of L413-416) | step 1 state, `td.earnings`, `rule.skip_earnings` | `earnings_gap_days` in counts and reports; warning with the gap dates | T-gap180 asserts `earnings_gap_days == 1` and the warning holds "2023-10-25→2024-04-22" and "EARNINGS_UNKNOWN". Control fixtures: `earnings_gap_days == 0`, no gap warning. ETF test: NaN. Tests assert the number, not only the text (RI-012) | – |
| 3 | Script, `load_ticker` L185-187: compute the gap count with the same constant and comparison as step 1 (`> EARNINGS_GAP_WARN`), so "warned" ⇔ "blocked". Keep the existing load warning text unchanged (its count is pinned in summary.json); the rule-dependent "no call sold" text lives in simulate (step 2) | `earnings` | `earnings_gaps` unchanged in meaning | T-gap120: no warning and a sale; T-gap121: warning and EARNINGS_UNKNOWN. Grep: `EARNINGS_GAP_WARN` is used only in L185 and the helper | – |
| 4 | Tests, tests/test_realtest.py (sale day 2024-01-02, expiry 2024-02-16 in `_tiny`): **T-gap180** `_tiny(earnings=[date(2023,10,25), date(2024,4,22)])` → `tr == []`, `rej_EARNINGS_UNKNOWN == 1`, `rej_EARNINGS_BLACKOUT == 0`, `rej_OK == 0`, `earnings_gap_days == 1`. **T-gap120** `[date(2023,10,25), date(2024,2,22)]` → 1 sale, strike 11. **T-gap121** `[date(2023,10,25), date(2024,2,23)]` → no sale, EARNINGS_UNKNOWN 1. **T-gap-noE**: T-gap180 with `skip_earnings=False` → sells, warning says "not checked". REALTEST_MISSING row `"earnings_interior_gap": "EARNINGS_UNKNOWN strictly inside a gap > 120 days between listed earnings dates; warning with the gap dates"`; add it to DROP_CASES and to the literal set in `test_realtest_missing_lists_every_input` (L376, extended, not loosened). `test_drop_input[earnings_interior_gap]`: drop AAA's Apr and Jul 2020 rows from `_make` data → no trade with `open_date` strictly inside the new gap, `earnings_gap_days > 0`, a trade exists after the gap end (no over-blocking), warning present | `_tiny`, `_copy`, `_make` | 4 new tests + 1 drop case | All pass on the built code; mutations (iii)/(iv) fail them as stated in step 1; the drop case fails under (iii) | T-gap fixtures: the sale day lies strictly inside each gap and no listed date is in [01-02, 02-16] (Self-check rows 4-5) |
| 5 | Tests, fixture edits (assertions unchanged): the 3 controls at L219, L274, L288 change `date(2024, 6, 1)` to `date(2024, 2, 20)` (gap 220 → 118 d), so each stays a control. REAL_BAC (L455-481) and `_make` tests: no change expected | tests | edited tuples only | I3 diffs tests: only those 3 tuples change among existing tests; no `assert` removed or loosened. REAL_BAC passes unchanged (BAC has no gap > 120; prototype BOT_RULE 22/60) | – |
| 6 | Report (05 only; reports/real/ is not re-published): I2 runs `python3 -m ccbot.realtest --out <scratch dir>` and states in 05: the decision (blocked, EARNINGS_UNKNOWN); per-ticker calls_sold before/after for CMCSA, MDLZ, MO, T, VZ (expected 12/31/21/1/3) and for ITUB, VALE, PBR ("skipped, < 3.0 years of quotes; no change"); the total (expected 247 − 3 − 2 = 242); `earnings_gap_days` per ticker (prototype EARNINGS_UNKNOWN deltas: CMCSA +72, MDLZ +69, MO +71, T +71, VZ +72); each dropped/added sale split into "blocked inside the gap" vs "path effect" and checked (audit 063 L61-64), with MDLZ's 2022-05-04 and 2022-11-30 drops and its 3 adds explained. Labelled "stock only, no sale (earnings unknown)": a data effect, not a strategy result | data/real | 05 text | Numbers in 05 are pasted from the scratch run's summary.json. Any value other than the expectations is explained per ticker | – |

Notes for I1:
- Known limit (stated in 04/05, not tuned): for the Brazilian ADRs, normal-looking intervals sit near the bar (VALE 120 not flagged; PBR 118/119 not, 126 flagged). They are skipped today, so no report changes. A per-ticker bar would be a cadence guess (RI-002 038/040), so this item does not add one.
- Code changes go through I1-I3 (Scope FULL). No live-bot file (rules, screen, missing) is touched. No rule the person follows changes (realtest is research only).

Out of scope / follow-ups for A1 (not done here):
1. **Refetch or source the missing Q4 2021 earnings rows** for CMCSA, MO, T, VZ and MDLZ (real dates 2022-01-27, 01-27, 01-26, 01-25, 01-27 per F12-F16). R2 suggested it; it changes external data, so A1 may open it as a separate item. Until then the block is a stopgap: with the real dates filled in, 4 of the 6 blocked sales would come back, and the 2 crossing sales would become EARNINGS_BLACKOUT.
2. Committing a regenerated `reports/real/` is the person's call (as in 063).

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| data/real/earnings/<T>.csv (load_ticker L179) | file missing | unchanged: EARNINGS_UNKNOWN every stock day; "earnings: not supplied (EARNINGS_UNKNOWN for a stock)"; `earnings_lead_days` and `earnings_gap_days` NaN |
| same file, 0 rows | empty | unchanged: EARNINGS_UNKNOWN every day; "earnings: no dates ..."; both counts NaN |
| history before the first listed date | leading edge | unchanged (063): EARNINGS_UNKNOWN; lead warning; `earnings_lead_days` = n |
| history after the last listed date | trailing edge | EARNINGS_UNKNOWN (helper state after_last); counted in rej_EARNINGS_UNKNOWN |
| dates missing between two listed dates more than 120 d apart | interior gap > 120 d | NEW: EARNINGS_UNKNOWN on each stock day strictly inside; `earnings_gap_days` = n; warning "earnings: gap(s) > 120 days between listed dates (<a>→<b>, ...); no call sold inside them (EARNINGS_UNKNOWN)" |
| interior gap ≤ 120 d | treated as complete | days are known; a report on a listed date still blocks via EARNINGS_BLACKOUT. Exactly 120 d counts as complete (VALE 2021-10-27→2022-02-24), same in warning and block |
| asset_type etf (SPY) | earnings not used | rule not applied (L497); both counts NaN; no warning |

Step 3a screen check: not applicable. realtest is a backtest, and no ticker is reported as passing `ccbot/screen.TESTS`. No PASS is claimed for any ticker.

## Self-check
Re-derive every numeric threshold in the map from that step's "How we check it" formula, and run every worked example against the trigger of the rule it shows. Show the arithmetic.
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Gap lengths (F7-F10, step 1) | later − earlier | computed in scratch from the CSVs; spot checks: CMCSA 10-28→04-28 = 3 + 30 + 31 + 31 + 28 + 31 + 28 = 182; VZ 11 + 30 + 31 + 31 + 28 + 31 + 22 = 184; MDLZ 28 + 31 + 31 + 28 + 31 + 26 = 175 | all match 01 ✓ |
| 120 separates the US holes (step 3 bar) | max normal < 120 < min hole | 100 (CMCSA/VZ) < 120 < 175 (MDLZ) | ✓ for the 5 reported names; ADR limit noted |
| Control pair 118 d (step 5) | b − a ≤ 120 and b > expiry | 2023-10-25 → 2024-02-20: 6 + 30 + 31 + 31 + 20 = 118 ≤ 120 → known; 02-20 > 02-16 → no date in [01-02, 02-16] → OK; pick unchanged: 45 DTE, strike 11 Δ0.28, bid 0.30 | sells, L219 `strike == 11.0` holds ✓ |
| T-gap180 (step 4) | a < d < b, b − a > 120, no date in [d, exp] | 10-25 → 04-22: 6 + 30 + 31 + 31 + 29 (2024 leap) + 31 + 22 = 180 > 120 → interior_gap → EARNINGS_UNKNOWN. 10-25 < 01-02 < 04-22 ✓; 04-22 > 02-16 ✓, so with the gap check removed the old path gives OK (no BLACKOUT) → the test fails under mutation (iii) | ✓ |
| T-gap120 / T-gap121 (step 4) | known iff b − a ≤ 120 | 6 + 30 + 31 + 31 + 22 = 120 → known → sells (b 02-22 > 02-16, no BLACKOUT); 02-23 → 121 > 120 → UNKNOWN. Mutation (iv) `>=`: 120 → UNKNOWN → T-gap120 fails ✓ | ✓ |
| Overlap reduces to "d strictly inside" (01 OQ2) | life [d, exp] meets gap (a, b) with d ≤ a → a ∈ [d, exp] | if d ≤ a < exp (or a ≤ exp), `_earnings_between(d, exp)` is True → BLACKOUT already; d == a or d == b → a listed date → known, then BLACKOUT; d ≥ b → outside | ✓ only d ∈ (a, b) needs the new state |
| Blocked calendar days (step 1) | gap − 1 | CMCSA/MO/T 182 − 1 = 181; VZ 183; MDLZ 174; PBR Σ 1308 − 7 = 1301 | ✓ |
| Period 2,502 d (step 1) | 2020-01-06 → 2026-11-12 | 2,192 to 2026-01-06 (366 + 365 + 365 + 365 + 366 + 365) + 310 = 2,502 (063/03) | ✓ |
| Expected total 242 (step 6) | 247 + Σ shifts | 247 (063/05 measured) − 3 (MDLZ 34 → 31: −6 + 3) − 2 (MO) = 242 | expectation; I2 measures |
| 2 crossing sales (decision) | report date ∈ [open, exp] | MO 01-19 ≤ 01-27 ≤ 02-18 ✓; MDLZ 01-24 ≤ 01-27 ≤ 02-18 ✓; MDLZ 12-22 → 01-21 < 01-27 ✗; others end 12-17, 04-14 (no Q4 report) ✗ → 2 | ✓ |
| $3k fit | 100 × spot vs 3,000 | 100 × 50.09 = 5,009 > 3,000 | fractional-share backtest only ✓ |

Recurring issues checked (logs/recurring-issues.md, open or ESCALATED: RI-001, RI-002; the others are GUARDED and checked for contact):
- RI-001 (ESCALATED): every count in the Feasibility column is computed with its source (CSV computation, trades files, scratch prototype). The 120 bar is measured against the data, not assumed.
- RI-002 (ESCALATED): unknown stays unknown. Interior-gap days are EARNINGS_UNKNOWN, never "OK". `earnings_gap_days` is NaN, never 0, when there are no dates. The guardrail is one shared helper for all three edges, with one mutation per edge in the map. This is the rest of occurrence 10, not a new count.
- RI-004 / RI-005: fixtures and thresholds checked against the rule's trigger (rows 3-6 above).
- RI-006: counts copied from check_handoff.py output (below).
- RI-007: Scope FULL; code goes through I1-I3. R3 changed no code, and no 07 is needed.
- RI-008: I1/I2 keep the code 3.10-compatible (`bisect` is stdlib).
- RI-010: the log line is written with `check_pipeline.py --log`, never by hand.
- RI-012: tests assert numeric counts, not only warning text.
- RI-003, RI-009, RI-011: GUARDED and not touched by this item.

`python3 scripts/check_handoff.py 065` output (pasted, must say PASS):
```
sources count (unique URLs in 01-research.md): 5
fact-check rows: 46
totals line: 46 rows -> 37 as-is, 7 fixed, 2 removed
PASS
```
