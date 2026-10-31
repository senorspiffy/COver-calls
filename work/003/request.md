# Work item 003
Type: BUG
Opened by: A1
Date: 2026-10-30
Against: 001 (`work/001/03-handoff.md` step 1). Found by R3 in `work/002/03-handoff.md` §"Correction to 001" (L113–120); carried by I3 in `work/002/07-audit-task.md` §1.

## What we want
Replace 001 step 1 ("$3,000 … only on a diversified, liquid ETF priced ≤ $28") with a rule that has at least one passing ticker, and make 001's text match what 002 built.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- 002/03 L114: of 11 ETFs checked (Cboe snapshots 2026-10-08 to 10-30) no diversified ETF is ≤ $28; the four ≤ $28 that pass the liquidity screen (KWEB, BITO, UNG, MSOS) are concentrated and pass only at Δ0.11–0.23, none at 0.25–0.30Δ. So step 1 as written gives an empty universe at $3k.
- `work/001/03-handoff.md` L120 still has the old wording. The corrected rule is only in 002/03 L116 and 002/04 "Fit check". Nothing in 001 names the guardrail test.
- The corrected rule is only partly built. Its "passes … on at least 5 of the last 10 logged scans" condition is in neither 002/03 map step 14, 002/04 nor `ccbot/` (grep for "5 of"/"last 10": no hits). It also says "0.25–0.30Δ strike of the 30–45 DTE monthly", but the code trades a [0.20, 0.35] tolerance with ±7-day expiry slack (04 change 3, 05 deviation 2). See 004.
- The code guardrail is in place and passes (A1 re-ran it): `tests/test_screen_bot.py::test_universe_empty_blocks_orders`, `::test_shipped_config_has_a_passing_ticker`. But it only proves feasibility on the SYNTHETIC sample (`config/default.json` universe = SYNTH_A/B/C).

## Root cause and prevention guardrail (BUG only)
Root cause: a universe rule was written as a house rule without running the screen it depends on. "Does any ticker pass?" was never computed. The fix (corrected rule) was then written in a separate section and never traced into the map, so part of it was dropped without anyone noticing.
Guardrail:
1. Add a required field to `templates/research-handoff.md` and a check to `.claude/agents/r3-fact-checker.md`: every rule that filters the universe or a window (price cap, asset type, liquidity, DTE, delta) states a **dated feasibility result**: how many tickers/days pass, with the source. R3 marks the rule BLOCKED if the count is 0 or not given. (This widens 002/03's proposal from universe rules to all filters; see RI-001.)
2. Keep the code guardrail (UNIVERSE_EMPTY banner + shipped-config test).
3. I1 traces every rule in 03 (map and correction sections) to a plan line or writes "DROPPED: reason".

## Recurring issue link (RI-#, if any)
RI-001 (rule assumed feasible without being computed).

## Done looks like
001/03 step 1 replaced by a corrected rule that matches what 002 built, or one that 002 is changed to build, with the dated feasibility result and the guardrail test names cited. The "5 of last 10 scans" condition is either built (the screen reads `state/paper_snapshots.csv`) with a test, or removed with a reason. The template and R3 instructions carry the feasibility field.
