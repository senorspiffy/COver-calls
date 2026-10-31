# Work item 005
Type: BUG
Opened by: A1
Date: 2026-10-30
Against: 002 code (`ccbot/data.py`, `ccbot/screen.py`, `ccbot/broker/webull_sandbox.py`).

## What we want
When earnings, open interest or dividend data is **unknown**, the code must say so and not treat it as "none" or as a pass.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `data.py` L78–79: a CSV without an `earnings` column gets `earnings = 0` and one without `dividend` gets `0.0`. The report does not mention it. A1 ran SYNTH_B (a stock, 4 earnings flags) with the column and with it dropped: V0's reasons go from `EARNINGS_BLACKOUT 69` to no blackout at all, and the report has no line saying earnings data was missing.
- `screen.py` L36: `if pd.notna(q["oi"]) and q["oi"] < min_oi` means missing OI → pass. L39: missing `next_earnings` → pass. A1, on SYNTH_SNAPSHOTS: SYNTH_A with OI 100 → rejected `OI`; with OI blank → **passes**. Earnings 2026-11-15 → `EARNINGS`; earnings blank → **passes**.
- `webull_sandbox.py` L144: `return Day(self.date, price)`, with no `next_earnings` or `ex_div_date`. So on the sandbox broker the 001 step 3(d) earnings rule is never enforced. The OI field names are UNVERIFIED (05 deviation 9). If Webull's name differs from `open_interest`/`oi`, every quote has OI None and the OI test is silently skipped for every ticker.

## Root cause and prevention guardrail (BUG only)
Root cause: "unknown" and "none" share one value (0/None), and the checks treat that value as "OK". This is the same root cause as the look-ahead and PBO bugs: missing data silently turned into a value. The Revision 2 guardrail grep (`fillna|nan_to_num|or 0`) does not match `else 0` or `pd.notna(x) and …`.
Guardrail:
1. Three states for these fields: known-none, known value, unknown. Unknown blocks the trade for `asset_type != "etf"` with new closed-list reasons (e.g. `EARNINGS_UNKNOWN`, `OI_UNKNOWN`) and is printed in the daily/backtest report ("earnings data: not supplied").
2. Tests: a stock CSV without `earnings` gives the warning line, and the run either blocks or labels it; a snapshot with blank OI is rejected `OI_UNKNOWN`; a sandbox `Day` without earnings is not a pass.
3. Widen the review check in `.claude/agents/i2-builder.md` and `i3-verifier.md`: for every optional input, write down what happens when it is absent, and test that case.

## Recurring issue link (RI-#, if any)
RI-002 (missing data silently turned into a value), occurrence 3.

## Done looks like
No screen or rule check passes on missing data. Reports name every missing optional input. The tests above are in the suite and fail if the old behaviour returns.
