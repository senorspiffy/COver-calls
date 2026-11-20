# 04 Build plan - 085
Fit verdict: FIT WITH CHANGES

The item adds tests only, in one file (tests/test_held_quote.py). It changes no trading rule, threshold, order path or ccbot/ file, so the $3k account, the 001 rules and the existing code are untouched. The fixture holds 200 VALE x $9.83 = $1,966, which is under $3,000. No other item built today touches this file or ccbot/bot.py, ccbot/broker/sim.py. I grepped work/080-086 03/04: 084/03 only mentions bot.py in a fact row about 083. I2 builds 085 last, so the file is in its 083 state when 085 starts.

Changes to 03 (small; none changes the design):
- C1. 03 § Missing inputs, row "Held ticker quote at site (b)": the claim "raises (no silent skip)" at bot.py L229 is right, but SimBroker cannot reach that line with a held ticker that has no quote. `SimBroker.advance` quotes every held ticker first, and on NoQuote it raises `DataError("cannot settle the paper ledger: ...")` (ccbot/broker/sim.py L182-186). That happens at bot.py L213, before L229. No test is planned for it (Rule trace: DROPPED, with reason).
- C2. The stub's `get_underlying_quote` must raise `ccbot.broker.base.NoQuote`, the class bot.py L219 catches, not another LookupError. Otherwise Test B crashes at L218 instead of skipping SYNTH_A.
- C3. Test-name and docstring wording, per 03 F6/D1: "same vol (NaN) as the live path", and "strike filter is a test choice, like a strike-range query (not a claim about Webull)". The quote and cash values are labelled synthetic.

## Extra research (with sources)
- E1. `pytest.approx` defaults: "within a relative tolerance of `1e-6`" and "an absolute tolerance of `1e-12`" [https://docs.pytest.org/en/stable/reference/reference.html]. The allowed error at 2962 is 1e-6 x 2962 = 0.002962. Float noise in 200 x 9.83 (order 1e-13) passes. An invented intrinsic-0 mark (2966, off by 4.00) fails, as 03's Self-check says. So `approx(2962.0)` with default tolerance is correct; do not pass `abs=` or `rel=`.
- E2. `tmp_path` gives "a temporary directory unique to each test function" [https://docs.pytest.org/en/stable/how-to/tmp_path.html]. The two tests therefore never share a ledger, so each `SimBroker` starts with no ledger file and the seeded `broker.state` is not overwritten (sim.py L34-38, 02 AGAINST 3).
- E3. Under the mutation, `run_daily` does not crash on the NaN equity. `json.dumps` writes NaN when `allow_nan` is `True`, which is "the default" [https://docs.python.org/3/library/json.html] (bot.py L277), and `report._fmt` prints NaN as "n/a" (ccbot/report.py L8-10). So the mutated run gets as far as the assertions, and I3's mutation failures will be assertion failures (equity NaN != approx(2962.0)), not errors. I3 should report them that way. An ERROR row means something else broke.
- E4. Edge case R3 did not cover: there is a simpler wiring that is closer to live. tests/test_paper.py L94-135 already runs `run_daily` on `WebullSandboxBroker(paper=True)` with a `FakeSDK`. I considered it and rejected it. It would need the SDK fake's chain, rate limiter, token dir and the tickers.json enrich path, which brings in the coupling 02 AGAINST 2 warns about. It would also test the same `SimBroker(quotes=...)` forwarding (webull_sandbox.py L145) that the plain stub uses. The R1/R3 `SimBroker(cfg, quotes=HeldQuotes())` design stays.
- E5. Checked against the code (read, not run, since I1 has no shell): `Day(DATE, 9.83)` defaults are vol/q/dividend/div_next NaN, asset_type "stock", earnings_known False (ccbot/rules.py L69-84). `settle_day` makes no event: `NaN > 0` is False, ex_div_date is None, and the 13C is OTM before expiry (rules.py L185-221). `Portfolio.get("SYNTH_A")` returns an empty State, but site (a) never reaches it because NoQuote comes first (portfolio.py L19-21; bot.py L217-221). 2026-11-19 is a Thursday, so no weekly report is written and `paper_trades.csv` is not read back (bot.py L289). `entry_budget` = min(1000, 0.5 x 2962 + 200 = 1681) = 1000 (portfolio.py L65-71). `pick_strike` returns None for the only delta, 0.03, which is outside [0.20, 0.35] (pricing.py L53-65). VALE's reject is therefore NO_STRIKE_IN_TOLERANCE on the fixed code.

## Files to create/change
1. `tests/test_held_quote.py` (change; the only file).
   - Imports added: `import pytest`; `from ccbot.bot import BrokerMarket, run_daily`; `from ccbot.broker.base import NoQuote`; `from ccbot.broker.sim import SimBroker`; `from ccbot.config import load_config`; `from ccbot.portfolio import Portfolio`; `from ccbot.rules import Day, Quote, Short, State`.
   - Constants: `HELD_SYM = "VALE261218C00013000"` (= `occ_symbol("VALE", EXP, "C", 13.0)`, base.py L87-89) and `HELD = Short("C", 13.0, EXP, 2, 0.16, dt.date(2026, 11, 2))`. The two 083 tests stay exactly as they are.
   - `class HeldQuotes` (03 step 1, with C2/C3). Docstring: market data for `SimBroker(quotes=...)`; synthetic fixture values, not market data; the strike filter is a test choice, like a strike-range query, not a claim about Webull; same vol (NaN) as the live Webull Day.
     - `quotes_have_oi = True`; `__init__`: `self.windows = []`.
     - `get_underlying_quote(t)`: returns `Day(DATE, 9.83)` for "VALE", else `raise NoQuote(t)`.
     - `list_option_contracts(u, f, t, lo, hi)`: appends `(u, f, lo, hi)`; returns `[HELD_SYM]` if `u == "VALE" and f == EXP and lo <= 13.0 <= hi`, else `[]`.
     - `get_option_snapshots(symbols)`: returns `[Quote(HELD_SYM, 13.0, "C", 0.01, 0.03, 0.02, 0.03, 500, None)]` if `HELD_SYM in symbols`, else `[]`.
   - `_held_run(tmp_path, universe)` (03 step 2): `cfg = load_config(None, {"universe": universe})`; `b = SimBroker(cfg, quotes=HeldQuotes(), ledger_path=tmp_path / "state" / "ledger.json")`; `b.state = Portfolio(cash=1000.0, positions={"VALE": State(cash=0.0, ticker="VALE", shares=200, option=HELD)})`; `scan = run_daily(DATE, b, cfg, state_dir=tmp_path / "state", reports_dir=tmp_path / "reports")`; return `scan, b.quotes`. Never the repo's state/ or reports/.
   - `_widened(stub)`: `any(u == "VALE" and f == EXP and lo <= 13.0 <= hi for u, f, lo, hi in stub.windows)`. It does not look at `windows[0]` (02 holes).
   - `test_run_daily_passes_held_option_at_universe_site(tmp_path)` (03 step 3; site a, bot.py L221). Docstring: "item 085: a reverted L221 leaves 13 outside 6.881-12.779; equity NaN". Asserts: (i) `_widened(stub)`; (ii) `scan["equity"] == pytest.approx(2962.0)`; (iii) `scan["rejects"].get("VALE") != "CAPITAL_UNKNOWN"`.
   - `test_run_daily_passes_held_option_at_held_only_site(tmp_path)` (03 step 4; site b, bot.py L230; universe ["SYNTH_A"]). Asserts (i) and (ii). It does not assert SYNTH_A's reject.
   - No assertion on the pick, the decisions, the passing list or the report text (02 AGAINST 2, Q3).

Files planned: 1.

## Tests and checks
- I2: `python3 -m pytest -q tests/test_held_quote.py --durations=0`. Expected: 4 passed (2 from 083 and 2 new). Paste the two new tests' runtimes (02 AGAINST 3).
- I2: full suite `python3 -m pytest -q`. Paste the pytest line as printed (RI-006, 076). Expected: this branch's count before 085 plus 2 passed, with the skip count unchanged. The branch count is set by 081/084/086/082/080, which are built first today, so I give no fixed number here.
- I2: `python3 -m py_compile tests/test_held_quote.py` with python3.11 if it is installed (RI-008). The new code uses no 3.12-only syntax.
- I2: `git status` must show only tests/test_held_quote.py and work/085/ changed. Nothing is written to state/ or reports/ (tmp_path only).
- I3 mutations, on a scratch copy and never in the repo (03 step 6). Run `tests/test_held_quote.py` for each and paste the real counts:

| Mutation | Change | Predicted |
|---|---|---|
| M1 | bot.py L221 → `BrokerMarket(broker, t, date, log)` | site-a test FAILS, site-b test passes, 083 tests pass (3 passed, 1 failed) |
| M2 | bot.py L230 → `BrokerMarket(broker, t, date, log)` | site-b test FAILS, site-a passes (3 passed, 1 failed) |
| M3 | both (A1's mutation, logs/audit/2026-11-20-083.md) | both new tests FAIL (2 passed, 2 failed) |
| M4 | delete bot.py L38-39 (widening) | all 4 FAIL (0 passed, 4 failed) |

  The failures should be assertion failures (E3). If M1 or M2 fails both new tests, or neither, the two-fixture design is wrong and the item goes back to I1 (03 step 6).

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Step 1: quotes stub `HeldQuotes` | Files 1, `class HeldQuotes` (with C2: NoQuote class; C3: docstring wording) |
| Step 2: helper `_held_run`, fresh tmp_path ledger, seeded Portfolio | Files 1, `_held_run` (E2: tmp_path is unique per test) |
| Step 3: site-a test, assertions (i)-(iii) | Files 1, `test_run_daily_passes_held_option_at_universe_site`; I3 M1/M3/M4 |
| Step 4: site-b test, assertions (i)-(ii) | Files 1, `test_run_daily_passes_held_option_at_held_only_site`; I3 M2/M3/M4 |
| Step 5: I2 full suite + runtime | Tests and checks, I2 lines 1-2 |
| Step 6: I3 mutations M1-M4 with real counts | Tests and checks, mutation table |
| Fact row F4 (pick 2026-12-18, not asserted) | Not asserted (02 AGAINST 2). It does not affect the result: `_capital` reads the same `(EXP, "C")` cache key |
| Fact row F6 (same vol, not same Day) | C3 docstring "same vol (NaN) as the live path" |
| Fact row F8 (CAPITAL_UNKNOWN only for tickers with rows) | Test B does not assert SYNTH_A's reject (NO_QUOTES either way) |
| Fact row D1 (Webull clause dropped) | C3 docstring "test choice, not a claim about Webull" |
| Fact row 02 AGAINST 2 (tickers.json not read on this path) | No tickers_file in cfg; nothing planned depends on tickers.json |
| Missing inputs: quote at held strike absent → NaN equity, CAPITAL_UNKNOWN, never a filled mark | Pinned by I3 M1-M4 (the absent case is the mutation) and by assertion (ii) `approx(2962.0)`, which also fails an invented mark (2966). The absent quote on its own is already pinned by tests/test_paper.py::test_capital_marks_option_at_quote_else_nan (NaN) |
| Missing inputs: `Day.vol` NaN | Covered: the stub Day has no vol, so both new tests run the NaN-vol path |
| Missing inputs: `Day.q` NaN | DROPPED: not reached. `decide_entry` returns HAS_POSITION before `_option_entry` (rules.py L264-265); already pinned by tests/test_missing_inputs.py drop tests |
| Missing inputs: `Day.next_earnings` absent | DROPPED: not reached in Test A (NO_STRIKE_IN_TOLERANCE fires first, screen.py L35-36 before L46-47). EARNINGS_UNKNOWN is already pinned by `test_drop_each_input[snapshot.next_earnings]` |
| Missing inputs: SYNTH_A quote absent (Test B) | Covered: the stub raises NoQuote, so the bot.py L219-220 skip is what Test B runs |
| Missing inputs: held ticker quote absent at site (b) | DROPPED: unreachable through SimBroker. `advance` raises DataError at bot.py L213 first (sim.py L182-186; C1). Not a silent skip either way |
| 001 rules the person follows | None changed (test-only), so no 001 text edit and no request opened |

## Guardrail tests
- Feasibility: strike-window rule (bot.py L37-39), fixture day 2026-11-19, VALE $9.83 close. The 13C is inside 1 of 1 widened window [6.881, 13.0] and inside 0 of 1 unwidened window [6.881, 12.779] (13 / 9.83 = 1.3225 > 1.3). Pinned by assertion (i) in both new tests, and by `test_window_widens_to_the_held_strike` (083) for the unit case.
- Feasibility: monthly pick on 2026-11-19 is 1 candidate, 2026-12-18 (29 DTE, inside slack [23, 52]; 2027-01-15 is 57 DTE, outside), traced by R3. Not pinned on purpose (02 AGAINST 2). The test does not depend on it (F4).
- Feasibility: delta tolerance [0.20, 0.35]: 0 of 1 fixture quote passes (delta 0.03). That is why VALE's fixed-code reject is NO_STRIKE_IN_TOLERANCE. Pinned indirectly by assertion (iii) (not CAPITAL_UNKNOWN).
- Missing inputs: quote at the held strike → I3 M1-M4 (absent-case run) + assertion (ii); `tests/test_paper.py::test_capital_marks_option_at_quote_else_nan`.
- Missing inputs: Day.vol → both new tests (vol absent by construction).
- Missing inputs: SYNTH_A quote → `test_run_daily_passes_held_option_at_held_only_site` (NoQuote skip).

## Expected result
- tests/test_held_quote.py has 4 tests, and all pass on the branch: equity 2962.00 in both runs, a recorded VALE 2026-12-18 window that includes 13.0, and VALE's reject NO_STRIKE_IN_TOLERANCE in Test A.
- Reverting either `run_daily` call site fails exactly one new test (M1, M2). Reverting both fails both (M3, the A1 mutation that left 344 passed). Removing the widening fails all four (M4).
- Full suite: the branch count before 085 plus 2 passed, skips unchanged. No ccbot/, config/, state/ or reports/ change.

Recurring issues checked (logs/recurring-issues.md, read first): RI-001 (ESCALATED): every window/filter rule in the plan has a dated, computed count (1 of 1 window on 2026-11-19; 0 of 1 quote in tolerance; 1 pick candidate) and a named test, or is marked not pinned with a reason. Nothing is called "always found". RI-002 (GUARDED, linked): no value is filled. The absent-quote path stays NaN, and `approx(2962.0)` at default tolerance (E1) fails an invented mark. RI-010 (ESCALATED): I1 does not type a log line. The line must be written with `check_pipeline.py --log` (see the hand-off note: I1 has no shell in this run). RI-014 (OPEN): not applicable, since there is no git or checker change. Also checked: RI-006 (I2 pastes the pytest line as printed, with no fixed total in this plan), RI-007 (Scope FULL, all steps run), RI-008 (py_compile on 3.11).
