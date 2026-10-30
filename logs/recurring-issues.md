# Recurring issues

Kept by A1. Read by R1 and R2 before every item. One entry per root cause.
Any entry with 3+ occurrences is ESCALATED: the guardrail didn't hold and the person is told.

<!-- Entry format:
## RI-001: Rule or window assumed to have candidates, never computed
Status: ESCALATED (4 occurrences, all found 2026-10-30). The systemic guardrail is now in place (003/004, uncommitted), but it has not been tested at the stage where the errors arose. Reviewed in the follow-up audit, 2026-10-30.
Root cause: a filter (universe price/asset cap, DTE window, delta band, weekday window) is written as a rule or test expectation without anyone computing how many tickers/days/strikes pass it. "Always found" or "exists" is asserted, not measured.
Guardrail(s) added:
- Code (002): `screen.feasible_universe` + "UNIVERSE EMPTY" banner, `tests/test_screen_bot.py::test_universe_empty_blocks_orders`, `::test_shipped_config_has_a_passing_ticker`. Synthetic data only.
- Code (002): `tests/test_calendar.py` coverage asserts; Mon/Tue weekly → None.
- Fix 003: 001 step 1 now states a dated screen result ("0 tickers confirmed on monthly quotes", `work/001/03-handoff.md` § Correction 2026-10-30). The "5 of last 10" count is built as information only (`screen.pass_history`, `test_pass_history_counts_last_10`, `test_daily_report_shows_pass_history`).
- Fix 004: 001 steps 4/5/8/11/Alt. 1 state the bot's rule (30–45, else ±7 d slack; nearest 0.275Δ in [0.20, 0.35]).
- Guardrail tests (004): `test_calendar.py::test_monthly_coverage_2016_2025` pins 1,440 / 2,483 / 2,609 and fails with `monthly_slack_days: 0` (17 failed, 05). `test_pricing.py::test_tolerance_finds_strike_on_bs_grid`. A1 re-ran them: pass.
- Process (003/004): Feasibility column in `templates/research-handoff.md` (0 or blank → BLOCKED); Rule trace and Guardrail tests in `templates/build-plan.md`; r3 step 1 feasibility text; i1 step 1a; i3 step 3. A1 confirmed each is present in `git diff` (additions only). These need the person's OK in PR review.
Why still ESCALATED: every occurrence was a process error at R3 → I1, and the process guardrail has never run. The 003–008 hand-offs were written before the column existed, so none has a Feasibility column (grep, 2026-10-30). The code tests pin only the two windows already found. They would not catch the next unmeasured rule. **Move to GUARDED when:** the process edits are approved and committed, and the first R3 hand-off after that fills the Feasibility column with a computed, re-runnable count for every filter rule (A1 checks it).
Occurrences: 4
- 2026-10-30 | 003 (fixed) | work/001/03-handoff.md step 1 | "diversified ETF ≤ $28" – no diversified ETF passes; the 4 that pass do so only at Δ0.11–0.23 (002/03 L114)
- 2026-10-30 | 004 (fixed) | 001 step 4, 002/03 step 6, 002/04 test_calendar | "30–45 DTE always found" – A1 measured 55.2% of 2016–2025 days; none on 2026-10-30
- 2026-10-30 | 004 (fixed) | 001 step 5 | 0.25–0.30Δ band often has no listed strike (~0.10Δ per $0.50 strike, 002/04 research 1); code uses [0.20, 0.35]
- 2026-10-30 | 002 (fixed by I2, 05 deviation 3) | 002/04 test_calendar | "Weekly picks 5–9 DTE on every Monday" – 0 of 522 Mondays

## RI-002: Missing or uncomputable data silently turned into a value
Status: ESCALATED (6 occurrences). The guardrail added in 005/006 works for loader inputs. Two new occurrences on the broker path got past it (014). Reviewed in the follow-up audit, 2026-10-30.
Root cause: when a value cannot be computed from the data available, the code fills, defaults, or tie-breaks it into a number (or into "OK") instead of keeping it NaN/n/a/unknown and saying why.
Guardrail(s) added:
- Standing rule (002/04 Revision 2). Tests (002): `test_realized_vol_uses_only_past_closes`, `test_no_option_sold_during_vol_warmup`, `test_pbo_undefined_on_too_few_months[0,1,7]`, `test_short_csv_reports_pbo_na_without_warnings`. They still pass.
- Fix 005: `EARNINGS_UNKNOWN`, `OI_UNKNOWN`, `DIVIDEND_UNKNOWN`. `Day.earnings_known` (default False, so a bare Day fails safe). `PriceSeries.missing`. `## Missing inputs` report section.
- Fix 006: `bh_lots` (no `max(1,`), `bh_na_reason`, B&H n/a with reason, weekly report n/a.
- Guardrail (005/006): `ccbot/missing.py::MISSING_POLICY` (9 rows); `tests/test_missing_inputs.py::test_drop_each_input[9]` + `test_policy_lists_every_optional_input`; `test_benchmark_cash_never_negative`; the widened grep in i2; the r3 step 3a and i1 step 1a policy lines; the i3 mutation step. A1 re-ran the mutations in scratch: `max(1,` in `bh_lots` → 3 failed; `else 0` in data.py → 2 failed; removing the screen's `EARNINGS_UNKNOWN` → 2 failed.
- Proposed (014): `Day.q/dividend/div_next` default to NaN; extend the enumeration test to every `Day` default and broker capability flag; make the cap tests fail closed (`not (… <= …)`).
Why still ESCALATED: `test_policy_lists_every_optional_input` enumerates only `OPTIONAL_CSV_COLUMNS` and `OPTIONAL_SNAPSHOT_FIELDS`. Values that enter as dataclass defaults (`Day.q/dividend/div_next = 0.0`) or derived values (`capital`) are outside it, and the review grep cannot see them. I2 and I3 each flagged one (05 "Finding", 07 §1). A1 reproduced both. **Move to GUARDED when** 014's extended enumeration test is in and fails on the 0.0 defaults.
Occurrences: 6
- 2026-10-30 | 002 (fixed) | ccbot/data.py::realized_vol | warm-up vol back-filled from later closes (look-ahead); I3 06 first pass
- 2026-10-30 | 002 (fixed) | ccbot/walkforward.py::pbo_cscv | empty CSCV blocks → NaN → PBO 0.000; held-out config tie-broken on 0 train years; I3 06 Re-verification
- 2026-10-30 | 005 (fixed) | ccbot/data.py L78–79, screen.py L36/L39, webull_sandbox.py L144 | missing earnings/OI/dividend treated as none/pass; earnings blackout never runs on the sandbox broker
- 2026-10-30 | 006 (fixed) | ccbot/backtest.py L121, report.py L168 | B&H forces 1 lot when 100 sh > cash − buffer → cash −$600 benchmark
- 2026-10-30 | 014 | ccbot/rules.py L75–77, broker/sim.py L67–71, broker/webull_sandbox.py L144 | broker `Day.q/dividend/div_next` = 0.0 → `DIVIDEND_UNKNOWN` can never fire on the broker path. SYNTH_A's snapshot ex-div is 2026-12-18 and today's call `SYNTH_A261218C00026000` expires that day, but the rules saw `div_next = 0.0` (A1 probe)
- 2026-10-30 | 014 | ccbot/screen.py::_reject L28/L30 | NaN capital passes PRICE_CAP and SINGLE_NAME_CAP (`x > NaN` is False). The probe with capital NaN lets SYNTH_C through, while at $3,000 it gets PRICE_CAP

## RI-003: Scan calendar ignores exchange holidays
Status: GUARDED (since 2026-10-30, 007; uncommitted)
Root cause: `expiries.business_days` is Mon–Fri with no holiday list, so holiday-moved expiries get the wrong date or symbol.
Guardrail(s) added (007):
- Fix: `config/holidays.json` (NYSE 2026–2028: 29 holidays, 5 early closes; A1 checked each date against the NYSE rules). `scan_calendar` raises outside `covers` and never falls back to Mon–Fri. `Broker.calendar`. The Thursday OCC fallback in webull_sandbox and sim. Early-close banner.
- Tests: `test_holiday_table_matches_nyse`, `test_scan_calendar_raises_outside_table[2]`, `test_monthly_moves_to_thursday`, `test_weekly_moves_to_thursday`, `test_occ_fallback_builds_thursday_symbols`, `test_early_close_banner_2026_12_24`, `test_scan_outside_holiday_table_changes_nothing`; `test_table_matches_exchange_calendars` (skips offline; I3 ran it in a scratch venv: pass). Mon–Fri mutation → 3 failed (05, 06). A1: the suite passes; `scan --date 2028-10-01` → exit 2, no state dir; the 2026-12-16 calendar includes Thursday 2026-12-24.
- Follow-ups (not guardrail gaps): (1) the paper log for 2026-12-16 to 12-18 should show `…261224…` symbols (OCC date still UNVERIFIED); A1 checks it then. (2) The scan refuses from **2028-09-03** (A1: 09-02 ok, 09-03 raises). Add the 2029 NYSE dates before then. The refusal is loud, so this can't fail silently.
Occurrences: 1
- 2026-10-30 | 007 (fixed) | ccbot/expiries.py, webull_sandbox.py L165 | June 2026 monthly computed as 06-19 (holiday); Thursday OCC fallback → []

## RI-004: Worked example not checked against the rule it shows
Status: GUARDED (since 2026-10-30, 008; uncommitted)
Root cause: R3 checks an example's arithmetic but not whether each step meets the rule's thresholds/tick.
Guardrail(s) added (008):
- Fix: 001 § Correction, worked example: limit $0.23 (48.9% of $0.47), profit $23.80, day ≤ 11 of 35. A1 re-computed: 0.5 × 0.47 = 0.235 → $0.23 at the $0.01 tick; (0.47 − 0.23) × 100 − 0.20 = 23.80; 11 × 3 = 33 ≤ 35, 12 × 3 = 36 > 35.
- Test: `test_backtest.py::test_worked_example_50pct_exit` (ask 0.23 → exit, 0.24 → hold; day 11 exit, day 12 hold). It passes. I3 showed the two original claims fail as assertions on the old code.
- Process: the r3 step 1 worked-example sentence (in `git diff`; needs the person's OK). It has not yet run on a new example. 015 moves it to its own step 1b so it isn't buried.
Occurrences: 1
- 2026-10-30 | 008 (fixed) | work/001/03-handoff.md worked example | 50% buy-back "fills at $0.24" = 51.1% of $0.47; V1 code (`ask ≤ 0.5 × premium`) would not fire
