# Recurring issues

Kept by A1. Read by R1 and R2 before every item. One entry per root cause.
Any entry with 3+ occurrences is ESCALATED: the guardrail didn't hold and the person is told.

<!-- Entry format:
## RI-001: <short name>
Status: OPEN | GUARDED | ESCALATED
Root cause:
Guardrail(s) added: <what, where, work item ID>
Occurrences: <count>
- <YYYY-MM-DD> | <work item ID> | <where found> | <evidence>
-->

## RI-001: Rule or window assumed to have candidates, never computed
Status: ESCALATED (4 occurrences, all found 2026-10-30)
Root cause: a filter (universe price/asset cap, DTE window, delta band, weekday window) is written as a rule or test expectation without anyone computing how many tickers/days/strikes pass it. "Always found" or "exists" is asserted, not measured.
Guardrail(s) added:
- Code: `screen.feasible_universe` + "UNIVERSE EMPTY" banner, `tests/test_screen_bot.py::test_universe_empty_blocks_orders`, `::test_shipped_config_has_a_passing_ticker` (002). Only covers the ticker universe, and only on synthetic data.
- Code: `tests/test_calendar.py` asserts strict 30–45 DTE coverage < 70% and with slack > 94%; Mon/Tue weekly → None (002).
- Proposed (003, 004): a dated feasibility field (pass count / coverage %) for every filter rule in `templates/research-handoff.md`, checked by R3 and I1. Not yet in place.
Why ESCALATED: no guardrail existed before today. The only one proposed (002/03 §Correction: a "dated screen run" for universe rules) was limited to universe rules and was written only in an item doc, not in any agent instruction or template. In the same 03, R3 asserted "30–45 DTE is always found (gap ≤ 35 days)" without computing it, and I1 copied it into 04 along with "5–9 DTE on every Monday".
Occurrences: 4
- 2026-10-30 | 003 | work/001/03-handoff.md step 1 | "diversified ETF ≤ $28" – no diversified ETF passes; the 4 that pass do so only at Δ0.11–0.23 (002/03 L114)
- 2026-10-30 | 004 | 001 step 4, 002/03 step 6, 002/04 test_calendar | "30–45 DTE always found" – A1 measured 55.2% of 2016–2025 days; none on 2026-10-30
- 2026-10-30 | 004 | 001 step 5 | 0.25–0.30Δ band often has no listed strike (~0.10Δ per $0.50 strike, 002/04 research 1); code uses [0.20, 0.35]
- 2026-10-30 | 002 (fixed by I2, 05 deviation 3) | 002/04 test_calendar | "Weekly picks 5–9 DTE on every Monday" – 0 of 522 Mondays

## RI-002: Missing or uncomputable data silently turned into a value
Status: ESCALATED (4 occurrences, all found 2026-10-30)
Root cause: when a value cannot be computed from the data available, the code fills, defaults, or tie-breaks it into a number (or into "OK") instead of keeping it NaN/n/a/unknown and saying why.
Guardrail(s) added:
- Standing rule (002/04 Revision 2): "if a value or statistic cannot be computed from the data available at that point, it stays NaN/n/a and the code says why. It is never filled, defaulted or tie-broken into a number."
- Tests (002): `test_realized_vol_uses_only_past_closes`, `test_no_option_sold_during_vol_warmup`, `test_pbo_undefined_on_too_few_months[0,1,7]` (+24×1), `test_short_csv_reports_pbo_na_without_warnings`. A1 checked them on 2026-10-30: putting both old bugs back makes 7 tests fail.
- Review grep `fillna|nan_to_num|or 0` (002/05 Rev 2, 06 Re-verification 2).
- Proposed (005, 006): three-state unknown/none/value for optional inputs; tests for every absent optional input; add `else 0`, `pd.notna(x) and`, `max(1,` to the review grep; put the standing rule in i1/i2/i3 instructions (013).
Why ESCALATED: the 002 guardrail targeted NaN in statistics only. Its grep does not match `else 0` defaults for missing columns (`data.py` L78–79), checks that pass on unknown (`screen.py` L36, L39), or `max(1, …)` (`backtest.py` L121). The standing rule lives only in 002/04, not in any agent instruction.
Occurrences: 4
- 2026-10-30 | 002 (fixed) | ccbot/data.py::realized_vol | warm-up vol back-filled from later closes (look-ahead); I3 06 first pass
- 2026-10-30 | 002 (fixed) | ccbot/walkforward.py::pbo_cscv | empty CSCV blocks → NaN → PBO 0.000; held-out config tie-broken on 0 train years; I3 06 Re-verification
- 2026-10-30 | 005 | ccbot/data.py L78–79, screen.py L36/L39, webull_sandbox.py L144 | missing earnings/OI/dividend treated as none/pass; earnings blackout never runs on the sandbox broker
- 2026-10-30 | 006 | ccbot/backtest.py L121, report.py L168 | B&H forces 1 lot when 100 sh > cash − buffer → cash −$600 benchmark

## RI-003: Scan calendar ignores exchange holidays
Status: OPEN
Root cause: `expiries.business_days` is Mon–Fri with no holiday list, so holiday-moved expiries get the wrong date or symbol.
Guardrail(s) added: proposed in 007 (holiday list + tests on 2026-12-24, 2026-06-18).
Occurrences: 1
- 2026-10-30 | 007 | ccbot/expiries.py, webull_sandbox.py L165 | June 2026 monthly computed as 06-19 (holiday); Thursday OCC fallback → []

## RI-004: Worked example not checked against the rule it shows
Status: OPEN
Root cause: R3 checks an example's arithmetic but not whether each step meets the rule's thresholds/tick.
Guardrail(s) added: proposed in 008 (R3 instruction line).
Occurrences: 1
- 2026-10-30 | 008 | work/001/03-handoff.md worked example | 50% buy-back "fills at $0.24" = 51.1% of $0.47; V1 code (`ask ≤ 0.5 × premium`) would not fire

## RI-005: Numbers in the hand-off not re-checked against the rule they belong to
Status: OPEN
Root cause: R3 changes a rule (adds a buffer, sets a % trigger) but does not re-derive the thresholds and worked-example numbers from that rule's own formula, so the text and the check disagree.
Guardrail(s) added: Self-check section in `templates/research-handoff.md` + R3 duty 5 + A1 spot-check (017, 018) - in PR daily-fixes/2026-10-30, GUARDED once merged
Occurrences: 2
- 2026-10-30 | 017 | work/001/03-handoff.md step 1, step 9(a) | "2 at ≥ $5.6k" / "one ≤ $55" fail step 1's own check `(price × 100 × positions) ≤ cash − $200` (need $5,800 / $5,700)
- 2026-10-30 | 018 | work/001/03-handoff.md worked example | 50% exit filled at $0.24 on a $0.47 sale = 51.1% (> 50% trigger)

## RI-006: Hand-counted totals in hand-off and logs
Status: OPEN
Root cause: R3 counts fact-check rows by hand and "fixed" vs "removed" is undefined, so totals, the removed list and the log line drift apart.
Guardrail(s) added: `scripts/check_handoff.py` run by R3, I3, A1 + fixed/removed definitions in template (019) - in PR daily-fixes/2026-10-30, GUARDED once merged
Occurrences: 1
- 2026-10-30 | 019 | work/001/03-handoff.md Totals + logs/research/2026-10-30.md 17:33 | 77 rows in table vs "76 rows → 60/12/4"; removed list has 7 entries vs "4 removed"
