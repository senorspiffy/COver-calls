# Work item 014
Type: BUG
Opened by: A1
Date: 2026-10-30
Against: 003–008 build (`ccbot/rules.py::Day` L75–77, `ccbot/broker/sim.py` L67–71, `ccbot/broker/webull_sandbox.py` L144, `ccbot/screen.py::_reject` L28/L30). Found by A1 in the follow-up audit of 003–008. I2 (05, "Finding") and I3 (07 §1) flagged parts of it. 005/03 (table row `broker.div_next`) asked A1 to open this item.

## What we want
On the broker path (sim snapshots, Webull sandbox), a dividend value or a capital figure that is unknown must block, or show n/a with a reason. It must not reach the rules as 0.0, and it must not pass a cap test. A known ex-dividend date must reach the early-assignment check.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `rules.Day` defaults `q = 0.0`, `dividend = 0.0`, `div_next = 0.0` (L75–77). Neither broker sets them: `SimBroker.get_underlying_quote` (snapshot mode, L67–71) and `WebullSandboxBroker.get_underlying_quote` (`Day(self.date, price)`, L144). So the 005 check `if math.isnan(day.q): DIVIDEND_UNKNOWN` (rules.py L287) can never fire on the broker path. A1 probe (`python -I`, repo code, SYNTH_SNAPSHOTS, 2026-10-30):
  ```
  snapshot ex_div_date: {'SYNTH_A': 2026-12-18, 'SYNTH_B': None, 'SYNTH_C': None}
  SYNTH_A q 0.0 dividend 0.0 div_next 0.0 ex_div_date 2026-12-18 isnan(q) False
  SYNTH_B q 0.0 dividend 0.0 div_next 0.0 ex_div_date None     isnan(q) False
  ```
  Today's paper scan (A1 re-run, scratch) sells `SYNTH_A261218C00026000`, which expires on SYNTH_A's ex-dividend date. The daily report prints "days to ex-dividend: 49". The rules saw `div_next = 0.0`, so the early-assignment check (rules.py L204, `day.div_next > 0`) is off for this exact contract. `MISSING_POLICY["broker.div_next"]` lists this as a `known_gap`, but `q` and `dividend` are not listed at all.
- NaN capital passes both cap tests. `_reject` L28/L30 use `price * 100 > capital − buffer`, which is False for NaN. A1 probe, same snapshots:
  ```
  capital 3000.0 {'SYNTH_A': None, 'SYNTH_B': 'SPREAD', 'SYNTH_C': 'PRICE_CAP'}
  capital nan    {'SYNTH_A': None, 'SYNTH_B': 'SPREAD', 'SYNTH_C': None}        <- PRICE_CAP lost
  ```
  `bot.run_daily` L128 makes `capital = equity(...)`. That is NaN while an option is held and the snapshot `iv` is blank (policy row `snapshot.iv`). The impact today is low, because the shares are already held, but the check passes on unknown.
- Related, and fail-safe (not an error): the Webull `Day` also defaults `asset_type = "stock"`. So on the sandbox every ticker, ETFs included, is `EARNINGS_UNKNOWN` and the bot cannot trade there. The fix for this item should supply the known fields rather than relax that block.
- Model-replay OI (I3's note, 07 §1): `SimBroker` series mode sets `quotes_have_oi = False`, and the screen skips OI. This can't be reached from the CLI (only `tests/test_broker.py` builds a series `SimBroker`; I3's mutations confirm). It is not a separate bug, but it is a third broker-side input with no `MISSING_POLICY` row.

## Root cause and prevention guardrail (BUG only)
Root cause: the 005 guardrail enumerates only **loader** inputs. `test_policy_lists_every_optional_input` is built from `OPTIONAL_CSV_COLUMNS` and `OPTIONAL_SNAPSHOT_FIELDS`. Values that enter as **dataclass defaults** (`Day.q/dividend/div_next = 0.0`), as **broker capability flags** (`quotes_have_oi`) or as **derived values** (`capital`) are outside it. The review grep matches none of them (`: float = 0.0`, a `>` comparison against NaN). This is the RI-002 pattern again: unknown became 0.0, or a pass.
Guardrail:
1. **Fail-safe defaults.** `Day.q`, `dividend` and `div_next` default to NaN, like `earnings_known = False`. Each broker sets what it knows. For example, sim snapshots give `div_next` from `ex_div_date` plus an amount if one is supplied, or leave it unknown. R1 decides how an unknown dividend affects entry (block with `DIVIDEND_UNKNOWN`, or allow with an early-assignment warning), and states it in the policy.
2. **The enumeration test covers every way in.** Extend `test_policy_lists_every_optional_input` so that every `dataclasses.fields(Day)` entry with a default, and every `Broker` capability attribute (`quotes_have_oi`), is either set by every broker's `get_underlying_quote` (asserted on `SimBroker` snapshot mode and on a stubbed `WebullSandboxBroker`) or has a `MISSING_POLICY` row. Add rows for `broker.q`, `broker.dividend` and `model.oi`. A new `Day` field with a silent default then fails the test.
3. **Cap tests fail closed.** `_reject` writes `not (price * 100 <= capital − buffer)` (and the same for the single-name cap), or returns `CAPITAL_UNKNOWN` when capital is NaN. Test: `capital = NaN` → no ticker passes.
4. Add the patterns `: float = 0\.0` (in dataclasses) and the "comparison against a possibly-NaN value" check to the i2 review grep notes.

## Recurring issue link (RI-#, if any)
RI-002 (missing or uncomputable data silently turned into a value), occurrences 5 and 6. ESCALATED.

## Done looks like
On SYNTH_SNAPSHOTS for 2026-10-30, SYNTH_A's broker `Day` carries a non-zero `div_next` (or is marked unknown and handled per the policy), and the scan shows that outcome. `_reject` with NaN capital passes no ticker. The extended enumeration test fails if a `Day` default goes back to 0.0 (mutation shown in 05). `MISSING_POLICY` has rows for `broker.q`, `broker.dividend` and `model.oi`, and `broker.div_next` is no longer a `known_gap`.
