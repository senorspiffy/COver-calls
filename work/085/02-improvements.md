# 02 Improvements - 085
## What past logs say
- logs/audit/2026-11-20-083.md: A1 reverted both `run_daily` call sites to `BrokerMarket(broker, t, date, log)`, and the suite still gave 344 passed, 1 skipped. 083's I3 mutation removed only the widening inside `chain`. This item closes that gap.
- work/083/02-improvements.md AGAINST 1: if Webull lists no contract at the held strike, the freeze comes back. This test cannot cover that, because the stub always lists the contract. It proves only the call site.
- RI-002 (GUARDED): never invent a mark. Under the mutation the test must see NaN, or at least a value other than 2962.00. A fallback mark must not make it pass (FOR 2).
- RI-001: R1 computed the window from the numbers (6.881 to 12.779; 13 / 9.83 = 1.3225), so nothing is assumed. R1 did not run the `pick_expiry` result (Q1). Its own reasoning shows the outcome does not depend on it.
- RI-010 / item 045: log lines are written only through `--log`, by the orchestrator.
- Code re-read by R2 (ccbot/bot.py L30-45, L145-160, L195-272; ccbot/broker/sim.py L21-30, L60-117, L169-197; ccbot/portfolio.py L15-45; ccbot/screen.py L15-67; tests/test_held_quote.py). F1, F3, F5, F9, F11 and F12 match the code. `screen._reject` does not read `iv` (grep), so the stub's `iv=None` quote is safe for the screen.

## 3 ways FOR
1. **Two fixtures, one per call site, are the right minimum (answers Q2: put them in tests/test_held_quote.py).** Site (a) (L221) runs only for a universe ticker that has a quote. Site (b) (L230) runs only when `t not in days` (L228). A1's mutation reverts both, but a later edit could revert just one, and one test cannot reach both branches (R1 F2, checked against L216-230). Keeping them next to 083's two `chain` tests puts the whole guardrail in one file with the same DATE/EXP constants and the same `Short("C", 13.0, EXP, 2, 0.16, 2026-11-02)`.
2. **Assert the exact equity, `pytest.approx(2962.0)`, not just `math.isfinite`.** 1000.00 + 200 x 9.83 - 0.02 x 100 x 2 = 1000 + 1966 - 4 = 2962.00. An exact value fails on the NaN from the mutation (pytest: "NaN is not considered equal to anything by default", https://docs.pytest.org/en/stable/reference/reference.html, cited by R1 F15). It also fails if someone later "fixes" the NaN with an invented mark, such as intrinsic 0 (which gives 2966.00) or a BS mark on a made-up vol. A bare `isfinite` check would pass in those cases. So the test guards RI-002 as well as 083.
3. **`SimBroker(cfg, quotes=stub)` runs the real main-account wiring with no network.** That is how `--broker webull-paper` is built (webull_sandbox.py L145, R1 F11). sim.py L60-62, L86-88 and L99-101 pass `get_underlying_quote`, `list_option_contracts` and `get_option_snapshots` to `quotes`, and L30 copies `quotes_have_oi`. The stub only needs those three methods plus that one attribute. The ledger, `advance`, `get_positions` and `submit` stay the real code. The vol is NaN, as on the live path (F6), which the existing SYNTH_SNAPSHOTS fixtures cannot reproduce (F10).

## 3 ways AGAINST
1. **The stub's strike filter models the broker, and its premise is unsourced.** D1 says the stub returns the 13C "only if lo <= 13 <= hi, as Webull filters by strike". That claim about Webull is not sourced in 01 and should be marked UNVERIFIED (R3). The test does not need it, because the window assertion (`lo <= 13.0 <= hi` on a recorded 2026-12-18 window) carries the proof by itself. Keep the filter as a test choice and label it that way in the docstring ("stub filters like a strike-range query"), not as a fact about Webull. The live risk from 083/02 AGAINST 1 (no contract listed even with a wide window) stays untested.
2. **A full `run_daily` run depends on many unrelated parts.** Config defaults (monthly_dte [30, 45], slack 7, max_positions, dip_entry unset), the holiday table for 2026-11-19, VALE's tickers.json entry, V0/V1 exit rules (F14) and report writing all run. A later change to any of them could break the test without 083 being involved, and the person then has to work out the cause. Mitigation: assert only (i) the window, (ii) `scan["equity"]` and (iii) `rejects.get("VALE") != "CAPITAL_UNKNOWN"` (Test A only). Do not assert the pick, the decisions, the passing list or the report text. Q3 answer: leave out the report-text check. It adds coupling to wording and catches nothing new, since M1-M3 already fail on equity.
3. **Cost and seeding fragility.** Each test runs `advance`, the screen, `_would_act` over all six REGISTRY variants and the report writes. That is a little slower than the 083 unit tests (UNVERIFIED size; I2 should report the runtime). Seeding by assigning `broker.state` after construction relies on `SimBroker` not having read the state yet. That holds only if `ledger_path` does not exist when the broker is built (sim.py L34-38). Use a fresh `tmp_path` ledger for each test, never a shared one. Also, `advance` calls `_save()` (L196), so the seeded state is written to disk. That is harmless in tmp_path but must not point at the repo's state/.

## Findings by language
Languages: N/A (no new external claims). This is a test-only EFFICIENCY item. It adds no fee, rule or market fact, and the only outside references are the Python and pytest NaN semantics R1 already cited for the test's own assertions.
Random languages this cycle: N/A
| Language | For / against / holes found | Source (original URL) | Original quote | English translation |
|---|---|---|---|---|
| English | N/A | | | |
| Mandarin Chinese | N/A | | | |
| Spanish | N/A | | | |
| Japanese | N/A | | | |
| N/A | N/A | | | |
| N/A | N/A | | | |
| N/A | N/A | | | |

## Holes to watch out for (summary)
- **Q1 (pick_expiry):** the test's result does not depend on it, because `_capital` reads the `(2026-12-18, "C")` cache key whether site (a)'s pick filled it or not. Do not assert the pick. I1 may print it once for the record.
- **Q2:** tests/test_held_quote.py, as R1 suggested (FOR 1).
- **Q3:** no report-text assertion (AGAINST 2).
- **Mark the Webull filter claim in D1 UNVERIFIED**, or drop the "as Webull filters" wording (AGAINST 1).
- **Window assertion must pick the 2026-12-18 window.** The stub records `(u, f, lo, hi)`. Check `any(f == EXP and lo <= 13.0 <= hi for ...)` for VALE, not `windows[0]`. Site (a) may also fetch other expiries in some configs.
- **Test B's SYNTH_A reject:** with an empty snapshot for SYNTH_A, `feasible_universe` gives it some reject code (not run). Do not assert which one. Only VALE's window and equity matter.
- **Mutation table D4 is predicted, not run.** I3 must paste the real pass/fail counts for M1 (site a only), M2 (site b only), M3 (both) and M4 (widening removed). M1 and M2 are what justify two tests. If either one fails both tests, or neither, the two-fixture design is wrong and goes back to I1.
- The quote values (bid 0.01, ask 0.03, mid 0.02, delta 0.03, OI 500) and cash 1000.00 are synthetic fixture inputs, not market data. Say so in the test docstring.
