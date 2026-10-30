# 03 Research hand-off - 006
Status: READY

Checked 2026-10-30 by R3. I reproduced A1's case with the repo code: the first 600 rows of SYNTH_A, closes × 1.5, scratch script only.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| `backtest.py` L121: `shares = max(1, floor(...)) * 100` | code | VERIFIED | – |
| `report.py` L168: weekly report `lots = max(1, ...)` | code | VERIFIED | – |
| A1: s0 = $36, (3,000 − 200)/3,600 = 0.78 → floor 0 → 1 lot → cash −$600 | re-run | VERIFIED: B&H cash after the buy = −$600.00 | – |
| A1: B&H vol 50.44%, MDD −54.77% | re-run (`metrics`) | VERIFIED | – |
| A1: V0 waits (`INSUFFICIENT_CASH` 92); "Excess vs B&H" +5.12% | re-run | VERIFIED: 92; V0 CAGR 18.42% − B&H 13.30% = +5.12% | – |
| R1 F4: 001 step 9c "No margin" (001/03 L128) | doc | VERIFIED | – |
| R1: the strategy refuses the same trade (`INSUFFICIENT_CASH`) | `rules.py` L258–260 | VERIFIED | – |
| R2 holes: "V0's +5.12% is already in a generated report; regenerate" | `reports/backtest_SYNTH_A_2026-10-30.md` | **WRONG** | The +5.12% came from A1's ad-hoc run. The shipped report starts at $24.00 (100 sh = $2,400 ≤ $2,800), so its B&H is feasible and unchanged. The "−5.12%" at L89 is V1's excess, which is unrelated. No regeneration is needed |
| Strategy paths already assert cash ≥ 0 and 100-share lots every day | `backtest._check` L68–77 | VERIFIED (new). The benchmark path has no such check, which is the gap | – |
| R2 AGAINST 2: fractional-share B&H flatters B&H | reasoning | Accepted; not built | – |
| Hindi/Turkish rows cited (max loss; 100-share unit) | fetched | VERIFIED (see 003/03) | – |

## Removed claims
- "Regenerate the V0 +5.12% report" (WRONG, above).

## Decision
- B&H that cannot be formed is shown as **n/a, with the reason**.
- R1's optional "B&H from the strategy's first buy" is **not built here**. It is a different comparison (it shares the strategy's entry timing), and whether to show it is the person's choice (006/01 open question). A1 can open an item if the person wants it.
- n/a uses NaN, so the existing `_fmt` already prints "n/a" (`report.py` L9–10). It follows the 005 policy table (`bh_benchmark: n/a`).

## Implementation map
| Step | Change | Inputs | Outputs | How we check it |
|---|---|---|---|---|
| 1 | `backtest.py`: new `bh_lots(series, cfg)` = `floor((cash − buffer) / (s0·100))` with **no `max(1,`**, and `bh_na_reason(series, cfg)` → `"100 shares cost more than cash − buffer"` if lots == 0, else None. `buy_and_hold` (L118–123) uses `bh_lots`. When it is 0, it returns an all-NaN equity series on the same index. Also add `_bh_cash(series, cfg)`, the cash path that L122 computes today, for the test. | series, cfg | B&H series (NaN when infeasible) | step 3 |
| 2 | Report wiring: `__main__.py` L66 sets `bh_metrics["na_reason"] = bh_na_reason(series, cfg)`. `report.backtest_report` § Buy and hold prints `n/a (100 shares cost more than cash − buffer)` when it is set. Excess columns are NaN → "n/a" (`variants.run_grid` L50/L61; `walk_forward` L60–83). `report.py` L168: `lots = int(...)` without `max(1,`. If lots < 1, `bh_text = "n/a (100 shares cost more than cash − buffer)"`. | step 1 | report lines | step 3 |
| 3 | **Guardrail tests (BUG; RI-002, the account-invariant part of the systemic guardrail):** `tests/test_backtest.py::test_benchmark_cash_never_negative[feasible, infeasible]` on SYNTH_A (s0 $24) and SYNTH_A[:600] × 1.5 (s0 $36). Feasible: `(_bh_cash >= 0).all()` and shares % 100 == 0. Infeasible: `bh_lots == 0`, the equity is all NaN, `metrics` raises no RuntimeWarning, and grid `excess_vs_bh` is NaN. `tests/test_report.py::test_bh_na_line_backtest` and `::test_bh_na_line_weekly` assert the n/a text. Every strategy variant already runs `_check` each day. Add one test `test_all_variants_pass_account_invariants_infeasible_bh`, running each registry variant on the × 1.5 input, so both branches are covered. | sample data | tests | Each fails on today's code. If `max(1,` is put back at L121 or L168, a test fails |
| 4 | Systemic RI-002 items (policy table row `bh_benchmark`, drop-each-input test, agent-file rule, grep with `max\(1,`/`min\(1,`): see 005/03 step 6. | – | – | See 005 |
