# 07 Audit task - 003 to 008 (combined)
For: A1. From: I3, 2026-10-30, after PASS on all six (see `work/003/06-verification.md`).
Items: 003, 004, 005, 006, 007, 008. Branch `claude/bugfixes-003-008`, base `74cf949`, **uncommitted**. Offline, sim and sandbox only, and live trading is still refused (exit 3). This is research, not financial advice.

## 1. recurring-issues updates (yours to make; I2 and I3 did not touch the log)
- **RI-001 (003, 004).** These guardrails are now in place:
  - the Feasibility column in `templates/research-handoff.md`;
  - the R3 step 1 feasibility text, I1 step 1a and I3 step 3;
  - `tests/test_calendar.py::test_monthly_coverage_2016_2025`, pinning 1,440 / 2,483 / 2,609;
  - `tests/test_pricing.py::test_tolerance_finds_strike_on_bs_grid`.

  Decide whether to keep it ESCALATED or move it to GUARDED. The process lines are untested until the next R3 hand-off fills the Feasibility column. Check that hand-off.
- **RI-002 (005, 006).** These guardrails are now in place:
  - `ccbot/missing.py::MISSING_POLICY`;
  - `tests/test_missing_inputs.py` (drop-each-input over 9 keys, plus a check that every optional input is listed);
  - `test_benchmark_cash_never_negative`;
  - the widened review grep in i2.

  Mutations of `else 0`, `pd.notna(oi) and` and `max(1,` each fail ≥ 1 test (06). Three open edges remain:
  - **Model-replay OI (I2 Deviation 1).** `SimBroker` in series mode sets `quotes_have_oi = False`, and the screen then skips OI. This cannot happen from the CLI, from Webull or from snapshots, and mutations prove it. But the daily report does not say "OI: not checked (model quotes)", and `MISSING_POLICY` has no row for it. Suggest a report line and a `model.oi` policy row.
  - **Broker `Day.q` / `dividend` default 0.0** (`rules.Day`), like the listed `broker.div_next` gap. `DIVIDEND_UNKNOWN` can never fire on the sim-snapshot or Webull path. Extend the `broker.div_next` row, or open an item.
  - **NaN `capital` passes the cap tests** (`screen._reject` L28/L30; I2's 05 finding). Today it is reached only while shares are already held. Suggest the `not (… <= …)` form, under RI-002.
- **RI-003 (007).** Set GUARDED, citing `config/holidays.json`, `scan_calendar` (raises outside 2026-01-01..2028-12-31, never falls back to Mon–Fri), and the Thursday tests. The XNYS cross-check passed in a scratch venv. Follow-ups:
  - the paper log on 2026-12-16 to 12-18 should show `…261224…` symbols (the OCC-date item is still UNVERIFIED);
  - add the 2029 NYSE dates before 2028-09-02, when the scan starts to refuse.
- **RI-004 (008).** The R3 worked-example line is in, and `test_worked_example_50pct_exit` passes. Set GUARDED.

## 2. Check the person-facing rule text (001)
- `work/001/03-handoff.md` now has a dated pointer and `## Correction 2026-10-30` (14 added lines, 0 removed). Confirm the person is told that this section replaces steps 1, 3, 4, 5, 6, 8, 9(a), 11, Alt. 1 and the 50% example.
- 001 step 1 now says **0 tickers confirmed on monthly quotes** at $3k. 003/03 step 6 (`config/paper.json` with real tickers) is still in your backlog, for after the paper bot logs monthly scans.

## 3. Process-file edits (need the person's OK in PR review)
- **Files:** `templates/research-handoff.md`, `templates/build-plan.md`, `.claude/agents/{r3-fact-checker,i1-reviewer,i2-builder,i3-verifier}.md`. These are additions only, with no tool or permission changes. 013 (all R/I agents read `recurring-issues.md`) is still open and separate.
- **Style suggestions:**
  - split r3 step 1's new text (858 characters on one line) into a step 1b;
  - add "in a scratch copy" to the i3 mutation step.

## 4. Efficiency and loose ends
- The checked-in `reports/backtest_SYNTH_A_2026-10-30.md` was not regenerated. Its numbers are unchanged, but it lacks `## Missing inputs - none`. Regenerate it, or leave it as a dated artifact.
- The daily report prints "Days to earnings: n/a" for an ETF, where "none (ETF)" would be clearer. This is cosmetic.
- The 005/03 known gap `broker.div_next` (the early-assignment check is off on the broker path) needs the item that 03 asked you to open.
- One combined plan, report and verification covered six items. Judge whether that batching saved time or made the review harder.
