# 03 Research hand-off - 085
Status: READY (test-only EFFICIENCY item; no trading rule, threshold or production code changes. READY on condition that the orchestrator's `check_handoff.py 085` run says PASS. R3 has no shell in this run, see Self-check.)
## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| F1 two BrokerMarket constructions in run_daily: L221 (universe loop) and L230 (held ticker not in days), both with `start.get(t).option` | ccbot/bot.py L216-230 (read) | VERIFIED | |
| F2 site (b) runs only when the held ticker is outside `days`, so one fixture cannot reach both sites; A1 mutation reverted both | ccbot/bot.py L226-230; logs/audit/2026-11-20-083.md Findings | VERIFIED | |
| F3 chain window [0.7, 1.3] x close, widened to held.strike only when held.expiry == expiry; cached per (expiry, kind) | ccbot/bot.py L35-45 | VERIFIED | |
| F4 monthly pick from 2026-11-19 is 2026-12-18 (R1: UNVERIFIED by a run) | ccbot/expiries.py L72-88 traced by R3; config.py L22-23 | VERIFIED with new source (counted fixed) | R3 traced `pick_expiry`: after bisect the list starts 2026-11-20 (1 DTE), then 2026-12-18 (29 DTE, not in [30, 45]), then 2027-01-15 (57 > 45 + 7 = 52, loop breaks). `near` keeps only DTE >= 23: 12-18, gap 30 - 29 = 1. Returns (2026-12-18, False). Still not asserted in the test (02 AGAINST 2). |
| F5 `_capital` marks a short at quote mid when a quote at its strike has ask > 0, else `option_mark` | ccbot/bot.py L145-160 | VERIFIED | |
| F6 a stub returning `Day(DATE, 9.83)` is "the same input the main scan had" | ccbot/rules.py L69-84; webull_sandbox.py L193; grep "vol" in ccbot/tickers.py: no match | WRONG in part (counted fixed) | Same vol input (NaN), not the same Day: the Webull Day has q=0.0 and enrich fields (earnings, ex-div); the stub Day has q NaN and no enrich. The difference does not change the test: equity reads only close and vol/q through `option_mark`, and NaN in either gives NaN. Docstring must say "same vol (NaN) as the live path", not "same input". |
| F7 `bs_price` with sigma NaN skips the intrinsic branch (NaN comparison False) and returns NaN; Python docs quotes | ccbot/pricing.py L5-21; rules.py L136-142; https://docs.python.org/3/reference/expressions.html ("Any ordered comparison of a number to a not-a-number value is false."); https://docs.python.org/3/library/math.html ("most functions will return a NaN"; exceptions listed are pow and hypot, not used here) | VERIFIED | |
| F8 a NaN capital rejects "every universe ticker" with CAPITAL_UNKNOWN; scan stores final `_capital` as `scan["equity"]` | ccbot/screen.py L15-22; bot.py L265, L272 | WRONG in part (counted fixed) | `_reject` returns NO_QUOTES first when a ticker has no snapshot rows (screen.py L17-18). Correct: every universe ticker that has snapshot rows gets CAPITAL_UNKNOWN. In Test B, SYNTH_A is NO_QUOTES under both versions. The L265/L272 part is correct. |
| F9 tests/test_held_quote.py::StubBroker records (lo, hi), returns no quotes, lacks the methods run_daily needs | tests/test_held_quote.py L12-24 | VERIFIED | |
| F10 SYNTH_SNAPSHOTS fixtures have finite vol (median iv), so the mutation passes there | ccbot/broker/sim.py L78-80; tests/test_screen_bot.py L46-50; tests/test_missing_inputs.py L46-49; A1 344 passed under the mutation | VERIFIED | |
| F11 `SimBroker(cfg, quotes=...)` takes quote, contracts, snapshots and quotes_have_oi from the other broker; webull-paper is wired this way | ccbot/broker/sim.py L21-30, L60-62, L86-88, L99-101; webull_sandbox.py L145 | VERIFIED | |
| F12 seed by assigning `broker.state = Portfolio(...)`; `get_positions` returns a copy | ccbot/broker/sim.py L33, L116-117; portfolio.py L15-26 | VERIFIED | |
| F13 `advance(2026-11-19)` settlement changes nothing (13C OTM, not expired, ex_div None, dividend NaN) | ccbot/rules.py L185-221 | VERIFIED | R3 also checked the dividend branches: NaN > 0 is False; the DIVIDEND_UNKNOWN branch needs ex_div_date == date, and ex_div_date is None. |
| F14 V0 `decide_exit` returns HAS_POSITION (profit_take False); V1 HAS_POSITION by 51 > 46; `decide_entry` HAS_POSITION; `_would_act` sends nothing | ccbot/variants.py L12, L22-30; rules.py L245-255, L263-265; bot.py L81-94 | VERIFIED | |
| F15 `pytest.approx` fails on NaN by default; `math.isfinite(NaN)` is False | https://docs.pytest.org/en/stable/reference/reference.html ("NaN is not considered equal to anything by default", nan_ok=False default); https://docs.python.org/3/library/math.html (isfinite: False for NaN) | VERIFIED | |
| D1 stub returns the 13C "only if lo <= 13 <= hi, as Webull filters by strike" | webull_sandbox.py L195-204 (the bot sends strike_price_gte/lte); no source for how Webull applies them | UNSUPPORTED in part (counted fixed) | Keep the filter as a test choice, reworded: "stub filters like a strike-range query (test choice; not a claim about Webull)". The Webull clause is dropped. The window assertion carries the proof on its own (02 AGAINST 1). |
| D2 Test A: universe ["VALE"], cash 1000.0, seeded 13C; asserts window, equity approx 2962.0, VALE reject not CAPITAL_UNKNOWN | ccbot/bot.py L216-231, L265; screen.py L15-50 traced | VERIFIED | R3 traced the fixed run: VALE reject is NO_STRIKE_IN_TOLERANCE (quote delta 0.03 is outside tolerance [0.20, 0.35]); under the mutation it is CAPITAL_UNKNOWN. So the third assertion also tells the versions apart. |
| D3 Test B: universe ["SYNTH_A"], stub raises NoQuote for SYNTH_A, VALE reaches only L227-230 | ccbot/bot.py L216-230; screen.py L17-18 | VERIFIED | SYNTH_A's reject is NO_QUOTES (no rows), computed by R3. Still do not assert it (02). |
| D4 mutation predictions M1 (A fails, B passes), M2 (B fails, A passes), M3 (both fail), M4 (A, B and both 083 tests fail) | code trace bot.py L216-231, L35-45; tests/test_held_quote.py L27-43 | VERIFIED as predictions | M4: test_window_widens fails (hi 12.779 < 13), test_window_unchanged fails at `windows[-1][1] == 15.0` (hi 13.0). I3 must paste real counts. |
| D5 mutated equity is NaN (no invented mark) | pricing.py L14-21; bot.py L155-159 | VERIFIED | |
| N1 0.7 x 9.83 = 6.881; 1.3 x 9.83 = 12.779; 13 / 9.83 = 1.3225 > 1.3 | arithmetic (R3) | VERIFIED | |
| N2 widened window [6.881, 13.0] | arithmetic; bot.py L38-39 | VERIFIED | |
| N3 2026-12-18 is 29 DTE, 2027-01-15 is 57 DTE; slack range [23, 52] | arithmetic (R3): 11 + 18 = 29; 11 + 31 + 15 = 57; 30 - 7, 45 + 7 | VERIFIED | |
| N4 V1 life 46 days, elapsed 17, 51 > 46 | arithmetic (R3): Nov 2 to Dec 18 = 28 + 18 = 46; Nov 19 - Nov 2 = 17 | VERIFIED | |
| N5 fixture equity 1000 + 1966 - 4 = 2962.00; mutated NaN | arithmetic (R3); bot.py L148-159 | VERIFIED | |
| Fit: 200 VALE x 9.83 = $1,966, under $3,000 | arithmetic (R3) | VERIFIED | |
| Fit: protects against the 2026-11-19 freeze (no quote, equity NaN) | ccbot/bot.py L26-28 docstring; logs/audit/2026-11-20-083.md | VERIFIED | |
| 02 FOR 2: an intrinsic-0 fallback would give 2966.00, so approx(2962.0) also guards RI-002 | arithmetic (R3): max(9.83 - 13, 0) = 0; 1000 + 1966 - 0 = 2966 | VERIFIED | |
| 02 FOR 3: stub needs only the three quote methods plus quotes_have_oi; ledger, advance, get_positions, submit stay real | ccbot/broker/sim.py L27-30, L60-62, L86-88, L99-101, L116-197 | VERIFIED | Stub also needs no `calendar`: SimBroker.calendar uses Broker.calendar (base.py L114-116) when series is None. |
| 02 AGAINST 2: test depends on "VALE's tickers.json entry" among other parts | ccbot/broker/sim.py L60-62 (quotes stub returns the Day directly); `enrich` is called only in webull_sandbox.py L193 | WRONG (counted fixed) | tickers.json is not read on this path: SimBroker forwards `get_underlying_quote` to the stub, which never calls `enrich`. The other dependencies listed (config defaults, holiday table, V0/V1 exits, report writing) do run. |
| 02 AGAINST 3: seeding works only if the ledger file does not exist at construction; `advance` saves to disk | ccbot/broker/sim.py L33-38, L196 | VERIFIED | |
| 02 (R2): `screen._reject` does not read `iv` | ccbot/screen.py L15-50 (read in full) | VERIFIED | |
**Totals:** 32 rows checked → **27 VERIFIED as-is**, **5 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None. (D1's clause "as Webull filters by strike" is reworded in place, see the fact-check row, so it counts as fixed.)
## Implementation map
Test-only. Every change is in tests/test_held_quote.py. No ccbot/ file changes.
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | Add a quotes stub `HeldQuotes` to tests/test_held_quote.py: `quotes_have_oi = True`; `windows = []`; `get_underlying_quote("VALE")` returns `Day(DATE, 9.83)`, other tickers raise `NoQuote`; `list_option_contracts(u, f, t, lo, hi)` appends `(u, f, lo, hi)` and returns `["VALE261218C00013000"]` only if `u == "VALE" and f == EXP and lo <= 13.0 <= hi`; `get_option_snapshots` returns `Quote("VALE261218C00013000", 13.0, "C", 0.01, 0.03, 0.02, 0.03, 500, None)` for that symbol, else nothing. Docstring: "synthetic fixture values, not market data; strike filter is a test choice like a strike-range query; same vol (NaN) as the live path" | DATE, EXP constants (file L8-9) | stub class | Used by steps 3-4. The symbol must equal `occ_symbol("VALE", EXP, "C", 13.0)` (base.py L87-89): "VALE" + "261218" + "C" + "00013000" | Strike filter (window rule): 13C returned for 1 of 1 widened window [6.881, 13.0], 0 of 1 unwidened [6.881, 12.779] (13 > 12.779), fixture day 2026-11-19, computed by R3 from bot.py L37-39 |
| 2 | Helper `_held_run(tmp_path, universe)`: `cfg = load_config(None, {"universe": universe})`; `b = SimBroker(cfg, quotes=HeldQuotes(), ledger_path=tmp_path / "state" / "l.json")` (fresh file per test, never the repo's state/); `b.state = Portfolio(cash=1000.0, positions={"VALE": State(cash=0.0, ticker="VALE", shares=200, option=Short("C", 13.0, EXP, 2, 0.16, dt.date(2026, 11, 2)))})`; `scan = run_daily(DATE, b, cfg, state_dir=tmp_path / "state", reports_dir=tmp_path / "reports")`; return `scan, b.quotes` | cfg defaults, tmp_path | scan dict, stub with recorded windows | Ledger path must not exist before construction (sim.py L34-38); with tmp_path it never does | – |
| 3 | `test_run_daily_passes_held_option_at_universe_site` (site a, bot.py L221): `_held_run(tmp_path, ["VALE"])`. Assert (i) `any(u == "VALE" and f == EXP and lo <= 13.0 <= hi for u, f, lo, hi in stub.windows)`; (ii) `scan["equity"] == pytest.approx(2962.0)`; (iii) `scan["rejects"].get("VALE") != "CAPITAL_UNKNOWN"`. Do not assert the pick, decisions, passing list or report text | step 2 | pass/fail | Passes on current code. Fails under M1 (site a reverted) and M3 (both) and M4 (widening removed). Fixed run: VALE reject NO_STRIKE_IN_TOLERANCE (delta 0.03 outside [0.20, 0.35]); mutated run: CAPITAL_UNKNOWN | Window rule: 1 of 1 fixture day (2026-11-19); held strike 13 inside [6.881, 13.0] on fixed code, outside [6.881, 12.779] under M1, computed by R3 |
| 4 | `test_run_daily_passes_held_option_at_held_only_site` (site b, bot.py L230): `_held_run(tmp_path, ["SYNTH_A"])`. Assert (i) and (ii) as in step 3. Do not assert SYNTH_A's reject (R3 computed NO_QUOTES, not pinned) | step 2 | pass/fail | Passes on current code. Fails under M2 (site b reverted), M3, M4. Only window recorded on fixed code is from `_capital` (L231): V0 exit returns before reading a quote, V1 returns at 51 > 46 | Window rule: 1 of 1 fixture day (2026-11-19), same window numbers as step 3 |
| 5 | I2: run the full suite and paste the pytest line as printed; report the two new tests' runtime (`pytest -q --durations=0 tests/test_held_quote.py`) | repo | pytest line | Expected: prior 344 passed, 1 skipped on main 6b652ff plus 2 new tests; I2 pastes the real line for this branch (PR #33 base may differ) | – |
| 6 | I3: on a scratch copy, run M1 (L221 back to `BrokerMarket(broker, t, date, log)`), M2 (L230 likewise), M3 (both: A1's mutation), M4 (remove bot.py L38-39). Paste real pass/fail counts for tests/test_held_quote.py | scratch copy | mutation table | Predicted: M1 A fails, B passes; M2 B fails, A passes; M3 A and B fail; M4 A, B and both 083 tests fail. If M1 or M2 fails both tests or neither, the two-fixture design is wrong: back to I1 | – |
## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| Quote at the held strike (`_capital`, bot.py L155-159) | broker lists no contract in the window (the mutation, or 083/02 AGAINST 1 live risk) | `option_mark` on NaN vol gives NaN equity; every universe ticker with snapshot rows gets CAPITAL_UNKNOWN (missing.py `derived.capital` = block). Never a filled mark. Report shows equity n/a |
| `Day.vol` (stub and Webull Day) | not set by the stub, the Webull Day or `enrich` | NaN; used only by the fallback mark, which stays NaN (RI-002). No default vol |
| `Day.q` (stub Day) | not set by the stub | NaN (rules.py L75). Would give DIVIDEND_UNKNOWN in `_option_entry`, which is not reached (HAS_POSITION first). Not filled |
| `Day.next_earnings` (stub Day) | not set | EARNINGS_UNKNOWN in the screen if reached; in Test A NO_STRIKE_IN_TOLERANCE fires first (screen.py L35-36 before L46-47). VALE is reported with a reject code, not PASS (item 025) |
| SYNTH_A quote (Test B) | stub raises NoQuote | skipped at bot.py L219-220; screen reject NO_QUOTES (no rows). Not a pass |
| Held ticker quote at site (b) (bot.py L229) | NoQuote | raises (no silent skip). Not exercised: the stub always quotes VALE |
## Self-check
Re-derived from each step's own check, with the arithmetic shown.
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Unwidened window low (steps 1, 3) | 0.7 x close | 0.7 x 9.83 = 6.881 | 6.881 ✓ |
| Unwidened window high | 1.3 x close vs 13 | 1.3 x 9.83 = 12.779 < 13; 13 / 9.83 = 1.32248 > 1.3 | 13 excluded under M1-M4 ✓ |
| Widened window (bot.py L39) | [min(6.881, 13), max(12.779, 13)] | [6.881, 13.0]; 6.881 <= 13.0 <= 13.0 | 13 included on fixed code ✓ (edge: hi equals 13 exactly; stub test `lo <= 13.0 <= hi` is inclusive, and `max` returns the float 13.0 itself, so no rounding gap) |
| Monthly pick (F4) | first DTE in [30, 45], else nearest within slack 7 with DTE >= 23 | 11-20: 1 DTE (< 23, dropped); 12-18: 29 DTE, gap 1; 01-15: 57 > 52, loop stops | 2026-12-18, in_window False ✓ |
| V1 exit gate (F14) | (date - sold_on) x 3 > (expiry - sold_on) | 17 x 3 = 51 > 46 | HAS_POSITION, no chain read ✓ |
| Fixture equity (steps 3-4 assertion ii) | cash + shares x close - mid x 100 x qty | 1000.00 + 200 x 9.83 - 0.02 x 100 x 2 = 1000 + 1966 - 4 = 2962.00 | approx(2962.0) ✓ |
| Mutated equity | cash + shares x close - option_mark(NaN vol) | 1000 + 1966 - NaN = NaN; NaN != approx(2962.0) (pytest nan_ok=False) | fails as required ✓ |
| Invented intrinsic mark (02 FOR 2) | 1000 + 1966 - max(9.83 - 13, 0) x 200 | 1000 + 1966 - 0 = 2966 != 2962 | approx(2962.0) fails it ✓ (default rel 1e-6 x 2962 = 0.003, far below 4.00) |
| PRICE_CAP in Test A fixed run (screen.py L24) | price x 100 <= capital - 200 | 983 <= 2962 - 200 = 2762 | passes ✓ |
| SINGLE_NAME_CAP (screen.py L26) | price x 100 <= 0.5 x capital | 983 <= 1481 | passes ✓ |
| Delta tolerance (screen.py L34-36) | nearest delta to 0.275 inside [0.20, 0.35] | only quote delta 0.03; 0.03 < 0.20 | NO_STRIKE_IN_TOLERANCE, not CAPITAL_UNKNOWN (assertion iii holds on fixed code) ✓ |
| Spread on fixture quote | ask - bid <= 0.05 | 0.03 - 0.01 = 0.02 | not reached (tolerance fails first) ✓ |
| Mid consistent with bid/ask | (bid + ask) / 2 | (0.01 + 0.03) / 2 = 0.02 | ✓ |
| OCC symbol (step 1) | underlying + yymmdd + kind + strike x 1000 as 8 digits | "VALE" + "261218" + "C" + "00013000" | VALE261218C00013000 ✓ |
| Account fit | 200 x 9.83 vs 3000 | 1966 < 3000 | ✓ |
| Totals | 27 + 5 + 0 | 32 | equals rows (copy from script output, below) |

Recurring issues checked (logs/recurring-issues.md, read first): RI-001 (ESCALATED): every window rule in the map has a computed count in the Feasibility column (1 of 1 fixture day, window numbers shown); no "always" without a count. RI-002 (linked, GUARDED): no value is filled; the mutated path stays NaN, and approx(2962.0) also fails an invented mark (2966). RI-004 / RI-005: the worked example (2962) and every threshold were re-run against the rule, including the inclusive window edge at 13.0. RI-006: Totals copied from the script output, not hand counts; the orchestrator pastes it. RI-010 (ESCALATED): R3 wrote no log line; the orchestrator writes it with `--log`. RI-014 (OPEN): not applicable (no git or checker change). RI-007: Scope FULL, so no 07-audit-task.md is needed; the item adds test code only, which FULL allows.

`check_handoff output (run by the orchestrator 2026-11-20 23:31 UTC, exit 0; must say PASS):`
```
sources count (unique URLs in 01-research.md): 3
fact-check rows: 32
totals line: 32 rows -> 27 as-is, 5 fixed, 0 removed
PASS
```
