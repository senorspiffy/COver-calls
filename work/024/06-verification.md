# 06 Verification - 024
Verdict: PASS (run afterwards, 2026-10-31, in item 026; two missing tests added)
## I1 audit (plan vs research)
No 01–04 (waived in request.md, item 026). The rule built is the person's 2026-10-31 decision in 001 (Correction, "Step 1 and 9(a)"): up to two single stocks, each ≤ 50% of capital, Σ ≤ cash − $200. Checked the code against that text instead of a plan. RI-001: 024's request asked how often two names pass together. That count can't be computed yet: the only real-ticker screen (023) has one date and 0 passes under the earnings rule, and the sample data has one stock. The bot does not rely on two passing; it opens what passes (test below).
## I2 audit (build vs plan)
05's file table matches `git show 29ade7f --stat`. Code vs 001 rule:
- `portfolio.entry_budget`: stock budget = min(cash, 0.5 × capital + buffer); `decide_entry` keeps the buffer back, so shares ≤ 0.5 × capital. ETF = all cash. Matches.
- `bot.run_daily`: `slots = max_positions − len(held)`; INSUFFICIENT_CASH does not use a slot. Matches.
- `SimBroker.buy_shares`: refuses a new ticker past `max_positions`. Matches.
Connectivity: `Portfolio`, `entry_budget`, `portfolio_equity`, `lend` are each called from bot.py or sim.py (grep). No TODOs.
## Tests re-run (output)
```
$ python3 -m pytest -q
149 passed, 1 skipped
```
Mutations (each restored after):
- `entry_budget` returns all cash for a stock → 4 tests fail (cheap stock, caps, entry budget, two-stock B&H).
- `slots = 99` in bot.py → 1 test fails (`test_max_positions_one_opens_only_one`).
- SimBroker max_positions guard → `False`: **0 tests failed** before 026. Sent back to I2 (026): added `test_sim_broker_refuses_ticker_past_max_positions`; with the mutation it fails (1 failed, 10 passed).
- 024's "done looks like" asks for a one-passing-ticker day test; none existed. Added `test_one_passing_ticker_opens_one` (SYNTH_D fails SPREAD → only SYNTH_B opens).
`python3 scripts/check_pipeline.py` → `024: complete (FULL; Waived: 01 02 03 04 ...)`.
## Sent back / sent to Audit
Two tests sent back to I2 and added in 026. Sent to Audit: yes (07-audit-task.md).
