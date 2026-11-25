# 01 Research brief - 085
## Question
How can a `run_daily` test prove that both `BrokerMarket` call sites in `run_daily` pass the ticker's held option, so that reverting either one to `BrokerMarket(broker, t, date, log)` (the A1 mutation in logs/audit/2026-11-20-083.md) fails a test? The fixture is a held VALE 13C 2026-12-18 on a $9.83 close (request "Done looks like").

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
Internal item. Most sources are repo files (path given). The three URLs back the Python and pytest NaN behaviour the test relies on.

Call sites and data flow
- F1. `run_daily` builds `BrokerMarket` in two places: (a) L221, inside the `cfg["universe"]` loop, `BrokerMarket(broker, t, date, log, start.get(t).option)`; (b) L230, for a held ticker that is not in `days` (not in the universe, or skipped there by NoQuote), with the same arguments [ccbot/bot.py L216-230].
- F2. The A1 mutation reverts both sites at once. A single test would catch that, but a revert of only one site would get past a test that reaches only the other. Site (b) runs only when the held ticker is outside `days`, so each site needs its own fixture [ccbot/bot.py L227-230; logs/audit/2026-11-20-083.md "Findings"].
- F3. `BrokerMarket.chain` asks the broker for strikes in [0.7, 1.3] x close. It widens that range to take in `held.strike` only when `held.expiry == expiry`, and it caches the result per `(expiry, kind)` [ccbot/bot.py L35-45].
- F4. Before `_capital`, site (a) also calls `chain(day, pick[0], "C")` for the monthly pick (L223-225). From 2026-11-19 with `monthly_dte` [30, 45] and slack 7, the pick should be 2026-12-18 (29 DTE; 2027-01-15 is 57 DTE). If so, that first call already fills the cache for the held expiry, and with the mutation it fills it without 13. Config values: [ccbot/config.py L22-23]. The pick itself is computed by `pick_expiry`, which is UNVERIFIED by a run: R1 has no shell. The test does not depend on it, because `_capital` reads the same `(expiry, "C")` cache key either way.
- F5. `_capital` marks each open short option at the quote's `mid` when the chain holds a quote at its strike with `ask > 0`. Otherwise it uses `option_mark` (BS on `day.vol`) [ccbot/bot.py L145-160].
- F6. `Day.vol` defaults to NaN [ccbot/rules.py L74]. The Webull sandbox/paper Day is `enrich(Day(self.date, price, q=0.0), ...)` with no vol [ccbot/broker/webull_sandbox.py L193], and `enrich` never sets vol (grep "vol" in ccbot/tickers.py: no match). A stub that returns `Day(DATE, 9.83)` is therefore the same input the main scan had.
- F7. `bs_price` returns intrinsic value only when `T <= 0 or sigma <= 0`. With sigma NaN that test is False, because "Any ordered comparison of a number to a not-a-number value is false" [https://docs.python.org/3/reference/expressions.html]. The BS path then runs `math.log`, `math.erf` and the arithmetic on NaN, and "most functions will return a NaN" given a NaN [https://docs.python.org/3/library/math.html]. So `option_mark` is NaN and equity is NaN when the quote is missing [ccbot/pricing.py L5-21; ccbot/rules.py L136-142].
- F8. A NaN capital rejects every universe ticker with CAPITAL_UNKNOWN (RI-002 guardrail 014) [ccbot/screen.py `_reject`; logs/recurring-issues.md RI-002]. The scan stores `final_eq = _capital(state, ...)` as `scan["equity"]` [ccbot/bot.py L265, L272].

Fixtures that already exist
- F9. `tests/test_held_quote.py::StubBroker` records `(lo, hi)` from `list_option_contracts` and returns no quotes. It is built for `BrokerMarket` alone and lacks `advance`, `get_positions`, `get_underlying_quote`, `submit`, `buy_shares` and `quotes_have_oi`, so `run_daily` cannot use it as is [tests/test_held_quote.py L12-24].
- F10. `tests/test_screen_bot.py::_run` and `tests/test_missing_inputs.py::_scan` run `run_daily` on `SimBroker(cfg, snapshots=SYNTH_SNAPSHOTS.csv)`. That Day's vol is the median snapshot iv, which is finite [ccbot/broker/sim.py L78-80]. In that fixture the mutation's fallback mark is a number, so equity stays finite and the mutation would pass. These fixtures cannot tell the two versions apart.
- F11. `SimBroker(cfg, quotes=<broker>)` takes all market data (`get_underlying_quote`, `list_option_contracts`, `get_option_snapshots`, `quotes_have_oi`) from another broker and keeps its own paper ledger [ccbot/broker/sim.py L21-30, L60-62, L86-88, L99-101]. This is how `--broker webull-paper` is wired (`SimBroker(cfg, ledger_path=..., quotes=self if paper else None)`) [ccbot/broker/webull_sandbox.py L145]. A small quotes stub plus a real SimBroker therefore runs the main-account code path with no network and no Webull SDK.
- F12. A held position can be seeded by setting `broker.state = Portfolio(cash=..., positions={"VALE": State(cash=0.0, ticker="VALE", shares=200, option=Short("C", 13.0, EXP, 2, 0.16, dt.date(2026, 11, 2)))})` after construction. `get_positions` returns a copy of `self.state` [ccbot/broker/sim.py L33, L116-117; ccbot/portfolio.py L15-26]. The `Short` values are the ones 083's tests use [tests/test_held_quote.py L30].
- F13. `advance(2026-11-19)` settles VALE once. The 13C is out of the money at 9.83 (`itm` False) and not expired, and with ex_div_date None no dividend event fires, so settlement changes nothing [ccbot/rules.py L185-221].
- F14. `run_daily` defaults to V0, and V0 has `profit_take` False (the dataclass default; only V1 sets it), so `decide_exit` returns HAS_POSITION before it reads a quote [ccbot/variants.py L12, L22-30; ccbot/rules.py L245-252]. V1 also returns HAS_POSITION: (19 - 2) x 3 = 51 > 46 days of life [ccbot/rules.py L253-255]. `decide_entry` returns HAS_POSITION while an option is open [ccbot/rules.py L263-265]. So no order is sent. `_would_act` runs all six REGISTRY variants on copies and sends nothing [ccbot/bot.py L81-94].
- F15. `pytest.approx` fails on NaN: "NaN is not considered equal to anything by default" [https://docs.pytest.org/en/stable/reference/reference.html]. `math.isfinite` is False for NaN [https://docs.python.org/3/library/math.html]. Either check fails on the mutated run's equity.

Proposed test design (for R2/R3/I1; not built here)
- D1. Quotes stub `HeldQuotes`. Attributes: `quotes_have_oi = True` and `windows = []`. `get_underlying_quote("VALE")` returns `Day(DATE, 9.83)` and any other ticker raises `NoQuote`. `list_option_contracts(u, f, t, lo, hi)` appends `(u, f, lo, hi)` and returns `["VALE261218C00013000"]` only if `lo <= 13 <= hi`, as Webull filters by strike. `get_option_snapshots` returns `Quote("VALE261218C00013000", 13.0, "C", 0.01, 0.03, 0.02, 0.03, 500, None)` for that symbol. The bid/ask/delta/OI values are synthetic fixture values, not market data.
- D2. Test A (site a): `cfg = load_config(None, {"universe": ["VALE"]})` and `SimBroker(cfg, quotes=HeldQuotes(), ledger_path=tmp_path/"state"/"l.json")`, seeded as F12 with cash 1000.0, then `run_daily(dt.date(2026, 11, 19), broker, cfg, state_dir=..., reports_dir=...)`. Assert three things: some recorded window for 2026-12-18 has `lo <= 13.0 <= hi`; `scan["equity"] == pytest.approx(2962.0)`; and `scan["rejects"].get("VALE") != "CAPITAL_UNKNOWN"`.
- D3. Test B (site b): the same setup with `{"universe": ["SYNTH_A"]}`. The stub raises NoQuote for SYNTH_A, so VALE comes in only through L227-230. Same assertions on the window and equity.
- D4. Mutation table for I3. M1 reverts site (a) only: A fails, B passes. M2 reverts site (b) only: B fails, A passes. M3 reverts both (the A1 mutation): A and B fail. M4 removes the widening in `chain` (083's I3 mutation): A, B and the two 083 tests fail. Every row is predicted from F1-F8, not run (R1 has no shell). I2 and I3 must paste the real counts.
- D5. The mutated equity is NaN, not some other wrong number. This is the RI-002 rule: the bot does not invent a mark. The test shows the call site matters, and the NaN path itself stays correct.

## Numbers used (show the math)
- Window without the held option: 0.7 x 9.83 = 6.881; 1.3 x 9.83 = 12.779. 13 > 12.779, so 13 falls outside (13 / 9.83 = 1.3225 > 1.3).
- Window with it: [min(6.881, 13), max(12.779, 13)] = [6.881, 13.0].
- Monthly pick from 2026-11-19: 2026-12-18 - 2026-11-19 = 29 days (not in [30, 45]; inside the slack range [23, 52]). 2027-01-15 - 2026-11-19 = 57 days (outside the slack range).
- V1 exit window: life = 2026-12-18 - 2026-11-02 = 46 days; elapsed 17 days; 17 x 3 = 51 > 46, so HAS_POSITION.
- Fixture equity (fixed code): cash 1000.00 + 200 x 9.83 (= 1966.00) - mid 0.02 x 100 x 2 (= 4.00) = 2962.00. With the mutation: 1000 + 1966 - NaN = NaN.
- Cash 1000.00 and the quote values are synthetic fixture inputs chosen for this test.

## Fit for a ~$3k account
- No trading rule, threshold, order or cost changes. This is a test only.
- The fixture holds 200 VALE shares (2 x 100) at $9.83, which is $1,966 of stock. That fits under $3,000 and under the "stocks under ~$30" limit. The account size does not affect the test's pass or fail. Note: work/083/01 calls the main account "~$5k" while this brief's template says ~$3k. The test works for either.
- What it protects: if a held call moves more than 30% out of the money, the account still gets a quoted mark. Without one, equity goes NaN and every ticker gets CAPITAL_UNKNOWN, which freezes new entries for the day (the 2026-11-19 freeze).

## Open questions
- Q1. F4 depends on `pick_expiry` returning 2026-12-18, which R1 did not run. It does not change the test's result (same cache key either way), but I1 should confirm it.
- Q2. Where should the tests go: tests/test_held_quote.py (083's file, same DATE/EXP constants) or tests/test_screen_bot.py? R1 suggests test_held_quote.py, so 083's whole guardrail sits in one file.
- Q3. Should the report text be asserted too (no "equity n/a" in daily_2026-11-19.md, as in `drop_snapshot_iv`)? This is optional. The `scan["equity"]` assertion already fails under M1-M3.
