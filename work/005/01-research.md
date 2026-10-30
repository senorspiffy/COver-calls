# 01 Research brief - 005
## Question
How should earnings, open interest and dividend data behave when they are unknown, what is the root cause, and what systemic guardrail stops RI-002 recurring? (Code review only; no web research needed.)

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- F1. `ccbot/data.py` L78–79: a missing `dividend` or `earnings` column becomes `0.0`/`0`, the same value as "known none". (read 2026-10-30)
- F2. `ccbot/screen.py` L36: `pd.notna(q["oi"]) and q["oi"] < min_oi` lets a missing OI pass. L39 does the same for a missing `next_earnings`. (read)
- F3. **Also affected (not in the request):** `ccbot/rules.py` L283 `if day.next_earnings is not None and day.next_earnings <= expiry` is the entry rule's blackout for the backtest and the bot. With the sandbox `Day` (`webull_sandbox.py` L144, no `next_earnings`), the blackout never runs. (read)
- F4. `webull_sandbox.py` get_option_snapshots: `oi = _num(i, "open_interest", "oi")` → None if the field name differs. Webull's real field name: UNVERIFIED (002/05 deviation 9).
- F5. `backtest.py` L50: the next-day dividend on the last row is `0.0`. That is the end of the data and is not used for a decision after it. Low risk, but it is the same pattern (review item).
- F6. 001 step 3(c)–(d) requires OI ≥ 500 and no earnings before expiry. 001's check column asks for a log "of spread, OI and next earnings date at each entry", so an entry with an unknown earnings date cannot meet it. (work/001/03-handoff.md L122)

## Numbers used (show the math)
- A1's evidence (request): SYNTH_B blackout days go from 69 to 0 when the column is dropped. OI blank → pass (it should be rejected); earnings blank → pass.
- No new numbers.

## Fit for a ~$3k account
- One position means one earnings gap or one illiquid strike is a large share of the account. Unknown must block, not pass.
- **Correct behaviour:** three states per optional input: `KNOWN_NONE` (e.g. an ETF has no earnings; `dividend` column present and 0), `VALUE`, `UNKNOWN`. Unknown → the screen/entry returns `EARNINGS_UNKNOWN` / `OI_UNKNOWN` / `DIVIDEND_UNKNOWN`. For `asset_type == "etf"`, earnings are KNOWN_NONE by definition. The report prints `<input>: not supplied (n days blocked)`.
- **Point fixes:** `data.py` keeps a per-column `supplied` flag in `meta` (or NaN plus flag), with no `else 0`. `screen.py` L36/L39 and `rules.py` L283 test `UNKNOWN` first. The sandbox `Day` carries `next_earnings=UNKNOWN` until a source is wired.
- **Systemic guardrail (RI-002 ESCALATED), proposed:**
  1. One shared sentinel: `ccbot/missing.py` with `UNKNOWN` (a singleton, not None/0/NaN) and `require_known(x, reason)`. A check that receives `UNKNOWN` must return a block reason. Using `None` for "absent" in decision inputs is banned.
  2. A policy table in one place (`MISSING_POLICY = {"earnings": block_unless_etf, "oi": block, "dividend": block_for_assignment_check, "bh_benchmark": n/a}`). A test iterates over every optional input the loader and brokers accept, drops it, and asserts that the run either blocks with the named reason or reports n/a. The pattern is "every optional input has an absent-case test", enforced by enumeration, not by memory.
  3. A static check test (`tests/test_no_silent_defaults.py`) greps `ccbot/` for `else 0`, `else 0.0`, `pd.notna(.*) and`, `is not None and`, `max(1,`, `min(1,`, `fillna`, `nan_to_num`, `or 0`. Each hit must sit on a short allow-list with a one-line reason (e.g. `costs.py` L31 SEC fee on buys = 0 is a rule, not a missing value). Grep today: 20 hits in `ccbot/`; at least 5 are defaults on missing data (data.py L78, L79; screen.py L36, L39; rules.py L283), plus backtest.py L121 and report.py L168 (006).
  4. Move the 002/04 standing rule into `.claude/agents/i1/i2/i3` and R3 (013), so that it is read at every stage.

## Open questions
- Webull field names for OI, earnings and ex-dividend (sandbox unreachable; UNVERIFIED).
- A real earnings-date source for the paper bot (none chosen yet).
