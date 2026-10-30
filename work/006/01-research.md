# 01 Research brief - 006
## Question
What should the buy-and-hold benchmark do when 100 shares cost more than cash − buffer, and what guardrail stops "defaulted into a number" (RI-002)? (Code review only; no web research needed.)

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- F1. `ccbot/backtest.py` L121: `shares = max(1, floor((cash − buffer) / (s0·100))) · 100` forces at least 100 shares, even when they cost more than the cash. (read 2026-10-30)
- F2. `ccbot/report.py` L168: the weekly report uses the same `max(1, …)`. (read)
- F3. The strategy itself refuses the same trade (`INSUFFICIENT_CASH`), so the comparison sets a levered benchmark against an unlevered strategy (A1 evidence: cash −$600, V0 "excess" +5.12%).
- F4. 001 step 9c: "No margin". A benchmark that borrows breaks the account's own rules. (work/001/03-handoff.md L128)

## Numbers used (show the math)
- A1 case: s0 = $36, (3,000 − 200) / 3,600 = 0.78, floor → 0, `max(1, 0)` = 1 lot. Cash 3,000 − 3,600 = **−$600**.
- Correct: 0 lots → B&H = n/a. Or start B&H at the strategy's first share buy (same day, price and shares), which is always feasible because the strategy only buys when it has the cash.

## Fit for a ~$3k account
- At $3k, any stock above $28 hits this case, and so do ETF-only universes as prices drift. The benchmark must say n/a rather than show an invented excess.
- **Correct behaviour:** lots = floor((cash − buffer) / (100·s0)). If lots == 0, `buy_and_hold` returns `UNKNOWN`/None with the reason `"100 shares cost more than cash − buffer"`. `metrics` and the report print `Excess vs B&H: n/a (100 shares cost more than cash − buffer)`. Optional second benchmark: "B&H from the strategy's first buy". Label it as such, because it shares the strategy's entry timing.
- Same fix in `report.py` L168.
- Tests: on SYNTH_A × 1.5 (start $36), B&H is n/a and no negative cash appears on any path. A property test: for any input where B&H exists, `min(cash) ≥ 0`. A report test: the n/a line is printed.
- **Systemic guardrail (RI-002 ESCALATED):** same as 005. The shared `UNKNOWN` sentinel and policy table (`bh_benchmark: n/a`), plus the `test_no_silent_defaults.py` grep test, which flags `max(1,`/`min(1,` (both hits today: backtest.py L121, report.py L168). Generalise the invariant with an "every simulated account path obeys the account rules" test: cash ≥ 0 and shares ∈ 100·ℕ, for the strategy **and** each benchmark. That catches the next defaulted benchmark even if it does not use `max(1,`.

## Open questions
- Should the report show the "from first buy" benchmark by default, or only n/a? (Person's choice.)
