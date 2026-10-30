# 02 Improvements - 005
## What past logs say
- RI-002 ESCALATED (4). The 002 guardrails (standing rule in 002/04, grep `fillna|nan_to_num|or 0`, NaN tests) target NaN in statistics only. They miss `else 0` (data.py L78–79), `pd.notna(x) and …` (screen.py L36/L39) and `max(1,` (backtest.py L121). The standing rule is not in any agent file (013).
- The mutation check worked for the 002 guardrails (7 tests fail when the bugs are put back). Behaviour tests catch bugs, while greps and rules in docs did not.

## 3 ways FOR
1. **Point fixes with explicit unknown checks close the bug (R1).** `data.py` keeps NaN plus a `supplied` flag instead of `else 0`. `screen.py` and `rules.py` L283 test unknown first and return `OI_UNKNOWN` / `EARNINGS_UNKNOWN`. ETFs are KNOWN_NONE for earnings. The order is small but matters: test unknown → test value. Reasoning: A1's evidence (blackout 69 → 0, blank OI passes).
2. **Systemic guardrail = one enumerated "absent-input" behaviour test, driven by a small policy table.** This is the strongest part of R1's proposal. A dict `MISSING_POLICY` lists every optional input (earnings, oi, dividend, ex_div, iv, bh_benchmark …). A parametrised test drops each one in turn and asserts that the run blocks with the named reason or reports n/a. A new optional input with no row fails the test. It is a behaviour test like the 002 ones that the mutation check proved effective, and it does not rely on anyone remembering a rule. The Spanish source in the 003 table ("include delisted…") makes the same point for backtests: absent ≠ none.
3. **Put the standing rule in the i1/i2/i3/R3 agent files (013).** Every RI-002 occurrence arose in a stage that never read it (A1 audit, "Process gap").

## 3 ways AGAINST
1. **A custom `UNKNOWN` singleton is more machinery than needed and does not fit pandas.** Putting an object sentinel in a DataFrame column makes it object dtype and breaks vectorised `<` comparisons. Two values with one meaning (NaN in frames, UNKNOWN in scalars) is a new place for bugs. Simpler: use NaN/None for "unknown" everywhere, and give "known none" an explicit representation (ETF flag; a `dividend` column present = known). Then every check starts with `if pd.isna(x): return "<X>_UNKNOWN"`. Keep a sentinel only if a field genuinely needs three scalar states. Reasoning, not sourced.
2. **The grep test (`test_no_silent_defaults.py`) will be noisy and easy to dodge.** Today it gets 20 hits, of which at most about 7 are real (005/01). Its allow-list needs upkeep, and a new pattern (`.get(k, 0)`, `or 0.0`, `getattr(x, "y", 0)`) slips past it. Keep it only as a cheap backstop to FOR 2, not as the guardrail.
3. **Blocking on unknown can stop all trading on the sandbox broker.** Webull's earnings/OI field names are UNVERIFIED (05 deviation 9). If the names are wrong, every stock gets `OI_UNKNOWN`, so nothing trades. That fails safe, but the person may read it as "the market had no candidates". The report must name the cause (`OI: not supplied by broker, n quotes`). ETFs (no earnings) still run.

## Findings by language
See `work/003/02-improvements.md` § Findings by language (random: Arabic, Hindi, Turkish). Relevant here: English (missing price data makes a backtest an upper bound), Spanish (include delisted instruments), Japanese (the Nikkei index's unstated discretionary fallback, which is the opposite of what the bot should do).

## Holes to watch out for (summary)
- `rules.py` L283 (the backtest/bot blackout) is in R1's list but not in the request. Fix it too, or the screen blocks while the entry rule passes.
- `backtest.py` L50 (last-row next-day dividend = 0.0) is low risk. Give it an allow-list entry with a reason rather than leave it unlisted.
- The CSV warning line must appear in both the backtest and the daily report: "earnings data: not supplied (n days blocked)".
- RI-002 guardrail summary for the person: **(1) the enumerated absent-input test, (2) the account-invariant test from 006, (3) the rule in agent files.** The grep and the sentinel are optional extras.
