# 03 Research hand-off - 004
Status: READY

Checked 2026-10-30 by R3. I re-ran the coverage numbers with the repo's `expiries.business_days`/`third_fridays`/`pick_expiry` and with `exchange_calendars` 4.13.2 (XNYS), in a scratch venv. Sessions run 2016-01-01 to 2025-12-31, with expiries listed to 2026-03-31.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| A1: strict 30–45 DTE has a monthly on 55.2% of days; with ±7 slack, 95.2% (Mon–Fri) | re-run | VERIFIED: 1,440/2,609 = 55.2%; 2,483/2,609 = 95.2% | On XNYS sessions: 1,410/2,514 = 56.1%; slack 2,399/2,514 = 95.4% |
| R1 table: 30–45 56.1%, 28–49 74.0%, 25–50 82.7%, 21–49 93.6% (XNYS, 2,514 days) | re-run | VERIFIED (all four rows exact) | Mon–Fri: 55.2 / 73.6 / 82.8 / 93.6% |
| R1: nearest-35 within 21–56 = 2,514/2,514 = 100%, DTE 21–56 | re-run | VERIFIED (Mon–Fri: 2,609/2,609, DTE 21–53) | – |
| R1: "the nearest-to-35 rule gives the same pick where both find one" | re-run | **WRONG** | The picks differ on **156** of the days where both rules find one. Example: at 22 vs 50 DTE, the slack rule takes 50 (5 days off the edge) and nearest-35 takes 22 |
| R1 F4: monthly gaps 28/35, 34/36 with holiday moves | re-run | VERIFIED, but incomplete | XNYS gaps are {27, 28, 29, 34, 35, 36} |
| R1: today's monthlies 11-20 (21), 12-18 (49), 01-15 (77); tie → the later one, 12-18; the bot traded `SYNTH_A261218C00026000` | re-run; `tests/test_calendar.py::test_live_scan_rule_2026_10_30` | VERIFIED | – |
| R2 AGAINST 1: share of nearest-35 picks with DTE < 25 or > 50 "not computed" | re-run | Computed: 510/2,514 = **20.3%** (389 below 25, 121 above 50) | – |
| R2 AGAINST 3: the slack rule has no candidate on about 1 day in 20 | re-run | VERIFIED: 4.8% of days. The longest run of no-candidate days is **3 business days** | – |
| Slack-rule DTE distribution | re-run | New: picks are 23–52 DTE. ≤ 30 DTE on 642/2,609 = **24.6%** of days; > 45 on 20.0% | Affects 001 step 11 (QCC note), see step 3 below |
| R1 F1 tastylive: "At tastylive, we like to target 25-50 DTE … with 45 days being our sweet spot." | tastylive.com (fetched) | VERIFIED | – |
| R1 F2 BXM: "a succession of one-month, at-the-money call options" held "to maturity, generally the third Friday of each month" | govinfo FR 2008-06-18 (fetched) | VERIFIED | – |
| R1 F3: theta speeds up near expiry; ORATS best 30 DTE | 001/03 | VERIFIED (carried from 001) | – |
| R2 FOR 2 / 003 table: M-X "30-45 days", theta quote | m-x.ca PDF (fetched) | VERIFIED | – |
| R2 FOR 1 / 003 table: Nikkei CC index sells 「直近限月」 | Nikkei PDF (fetched) | VERIFIED | – |
| R1 strike table (BS, 35 DTE, r 4%, $0.50 grid): S 24 / σ 25% none in 0.25–0.30, adjacent 0.07–0.09Δ apart | re-run (`pricing.bs_delta`, q = 0) | VERIFIED (25.0C 0.330, 25.5C 0.244, 26.0C 0.172) | – |
| S 17 / σ 35% none; S 12 / σ 25% none, gap 0.16Δ; S 24 / σ 50% two | re-run | VERIFIED (12.5C 0.330 → 13.0C 0.172; 26.5C 0.295 and 27.0C 0.255) | – |
| R1: "the tolerance [0.20, 0.35] covered every case except S = $12, σ 25%" | re-run (`pick_strike`) | **WRONG** | It covers **all four** cases (S 12 picks 12.5C Δ0.33). A 0.16Δ gap is wider than the 0.15 tolerance, so at other prices it *can* miss |
| Request: `tests/test_calendar.py` asserts strict < 70% and slack > 94% | code | VERIFIED, but on SYNTH_A's dates, not on 2016–2025 business days | Step 4 adds a test pinned to the 2016–2025 numbers |
| Request: "Weekly 5–9 DTE on every Monday": 0 of 522 | `test_weekly_5_to_9_dte` | VERIFIED (it asserts Mon/Tue → None) | – |

## Removed claims
- "Nearest-35 gives the same pick where both find one" (WRONG, above).
- "Except S = $12" as worded (corrected above).

## Decision (R1 vs R2): keep the code's slack rule
**Rule: 30–45 DTE, else the monthly nearest that window within 7 days of its edges (23–52 DTE, ties go to the later one), else no trade that day.**
- It needs **no code change**. The bot already does this (`monthly_dte: [30, 45]`, `monthly_slack_days: 7`) and already logs `in_window`.
- It stays closer to the 30–45 evidence (M-X, 001). Nearest-35 goes below 25 DTE on 15.5% of days (389/2,514), down to 21. That is the faster-gamma zone 001 C1 warns about.
- Its cost is small. It skips 4.8% of days, at most 3 business days in a row, and it only matters on entry days. The bot retries at the next scan (R2 AGAINST 3).
- "Never skip" (R2 FOR 1) is not worth a new selector, new config keys, and a second rule for V2's weekly path to keep separate.

The strike rule is unchanged: nearest 0.275Δ, accepted only in [0.20, 0.35] (R2 FOR 3).

## Implementation map
| Step | Change | Inputs | Outputs | How we check it |
|---|---|---|---|---|
| 1 | **Docs: replace 001/03 step 4** (`work/001/03-handoff.md` L123), keeping the 0DTE and weekly sentences: "Sell the **monthly** (third-Friday) expiry with **30–45 DTE**. If none is in 30–45, take the monthly nearest that window within 7 days of its edges (**23–52 DTE**; ties → the later one), logged `in_window = False`. If none is within 23–52, make no trade that day (`NO_EXPIRY`) and retry at the next scan. Feasibility (2016–2025, Mon–Fri, repo `pick_expiry`): 30–45 alone 55.2% of days; with the 7-day slack 95.2%; at most 3 business days in a row without a candidate. Example: 2026-10-30 → 2026-12-18, 49 DTE, `in_window = False`." Check column: "Log DTE and `in_window`; DTE must be 23–52. Tests: `test_monthly_coverage_2016_2025`, `test_live_scan_rule_2026_10_30`." | 001/03 | edited 001 | The diff matches; the cited tests exist and pass |
| 2 | **Docs: replace 001/03 step 5** (L124), first sentence and check column: "Sell the listed call whose delta is **nearest 0.275**. Accept it only if its delta is in **[0.20, 0.35]**; otherwise make no trade that day (`NO_STRIKE_IN_TOLERANCE`). The strike must be ≥ cost basis. If the nearest is below basis, take the lowest strike ≥ basis if its delta is ≥ 0.20; otherwise no trade (`BASIS_ABOVE_BAND`). Why not 0.25–0.30 only: on a $0.50 strike grid at 35 DTE, adjacent strikes are 0.07–0.16Δ apart, so the 0.05-wide band was empty in 3 of 4 Black–Scholes cases (004/03). The 0.25–0.30 band is logged as `in_band`." Keep the limit-at-mid sentence. Check column: "Log delta (must be in [0.20, 0.35]), `in_band`, strike ≥ basis, fill vs mid." | 001/03; `rules.py` L285–295 | edited 001 | The text matches `_option_entry` L285–295 and `config` `tolerance`/`band` |
| 3 | **Docs: 001/03 steps 8, 11 and Alternative 1.** Step 8 (L127): "30–45 DTE, ~0.25–0.30 delta" → "the step-4 expiry and the step-5 strike rule (put delta nearest −0.275, \|Δ\| in [0.20, 0.35])". Step 11 (L130): replace "— another reason for 30–45 DTE" with "— under the step-4 rule about 25% of entry days (2016–2025) pick 23–30 DTE, and those calls are not QCCs". Alternative 1 (L145): "30–45 DTE, 0.25–0.30Δ" → "step-4 expiry, step-5 strike". | 001/03 | edited 001 | grep `work/001/03-handoff.md` for "30–45" and "0.25–0.30": each remaining hit is either the in-window/in-band log definition or the evidence text |
| 4 | **Guardrail test (BUG, RI-001):** `tests/test_calendar.py::test_monthly_coverage_2016_2025`. Use `business_days(2016-01-01, 2026-03-31)` and `third_fridays`, and loop over the days ≤ 2025-12-31. Assert strict == 1,440/2,609 and slack == 2,483/2,609. Assert the longest no-candidate run is ≤ 3. This pins the numbers 001 cites. Keep the existing `test_monthly_coverage_on_synth_a`. | repo code only (offline) | new test | Passes now. If `monthly_slack_days` is set to 0 it fails |
| 5 | **Guardrail test:** `tests/test_pricing.py::test_tolerance_finds_strike_on_bs_grid`. On the four BS cases (S 24/σ .25, 17/.35, 12/.25, 24/.50; 35 DTE, r .04, q 0, $0.50 grid), `pick_strike(…, 0.275, (0.20, 0.35))` is not None, and `band (0.25, 0.30)` is empty in 3 of 4 cases. | `pricing.bs_delta` | new test | Passes now |
| 6 | **Systemic RI-001 guardrail:** as in 003/03 step 5 (Feasibility column + R3/I1/I3 lines). Nothing extra here. | – | – | See 003 |
