# 06 Verification - 085
Verdict: PASS (round 1)
Sent back to: none

## I1 audit (plan vs research)
04 follows 03's map step by step (Rule trace covers steps 1-6, fact rows F4/F6/F8/D1/02 AGAINST 2, and every Missing-inputs row). It adds nothing that has no source:
- C1 (site-b NoQuote is unreachable through SimBroker because `advance` raises DataError first) is sourced to ccbot/broker/sim.py L182-186. Dropping that test is recorded as DROPPED with a reason.
- C2 (raise `ccbot.broker.base.NoQuote`) matches bot.py L219, which catches that class.
- C3 is 03's own F6/D1 wording.
- E1-E3 cite pytest/Python docs. E1's approx tolerance is checked below: NaN and 2966 both fail `approx(2962.0)`. E4 is a rejected alternative, so it adds no code. E5 is a code read, and my probe run confirms it: VALE is rejected NO_STRIKE_IN_TOLERANCE on the fixed code.
- Two cosmetic differences from 03, neither of which changes the design. The ledger file is named `ledger.json` instead of 03's `l.json`; it is in tmp_path either way. 04's sentence "I2 builds 085 last" did not happen: 085 was built first, and 05 says so. 04 also says no other item touches this file, and that still holds at ceb00ce.
- No 001 rule changed (test-only), so no 001 text edit or request is needed.

## I2 audit (build vs plan)
I diffed `git show ceb00ce -- tests/test_held_quote.py` against 04's "Files to create/change" line by line. The commit changes code in tests/test_held_quote.py only, plus work/085/05 and the I2 log line. `git diff --stat 289d321 ceb00ce -- ccbot tests config` shows that file only (60+, 2-).
- Imports: all 7 planned lines are present. The two 083 tests are unchanged: only the import lines above them changed.
- `HELD_SYM`/`HELD`: as planned. The OCC string is VALE+261218+C+00013000.
- `HeldQuotes`: `quotes_have_oi = True`; `windows` set in `__init__`; VALE returns `Day(DATE, 9.83)` and anything else raises `NoQuote(t)` (C2). The strike filter is `u == "VALE" and f == EXP and lo <= 13.0 <= hi`. The snapshot returns the planned `Quote(...)` only when HELD_SYM is asked for. The docstring carries the C3 wording.
- `_held_run`, `_widened` and both tests match the plan: assertions (i)-(iii) for site a, (i)-(ii) for site b, nothing on the pick, decisions, passing list or report text. Two docstrings are additions with no behaviour change: `_held_run`'s, and site b's "VALE held but not in the universe (bot.py L230)...".

Connectivity check, re-done:
- Every new import is used: pytest (approx), run_daily, NoQuote, SimBroker, load_config, Portfolio, Quote, State.
- `HeldQuotes` is used by `_held_run`; `_held_run` and `_widened` are used by both tests; `HELD_SYM` and `HELD` are used by the stub and the fixture.
- `grep -n TODO tests/test_held_quote.py` finds nothing.
- After the full suite, `git status --short` in /tmp/claude-0/wt085 is empty, so nothing was written to state/ or reports/.

Missing-data grep (05's pattern) on ccbot/ at ceb00ce gives 38 hits, as 05 says. `git diff --stat 289d321 ceb00ce -- ccbot` is empty, so none of them is new.

Feasibility re-measured by a probe (scratch script `/tmp/claude-0/-home-claude/8f94cbd2-523d-52d1-8971-85df3e672dc0/scratchpad/probe085.py`, run in the worktree, calling the test's own `_held_run`):
```
== fixed
['VALE'] equity 2962.0 rejects {'VALE': 'NO_STRIKE_IN_TOLERANCE'} windows [('VALE', '2026-12-18', 6.881, 13.0)]
['SYNTH_A'] equity 2962.0 rejects {'SYNTH_A': 'NO_QUOTES'} windows [('VALE', '2026-12-18', 6.881, 13.0)]
== M3
['VALE'] equity nan rejects {'VALE': 'CAPITAL_UNKNOWN'} windows [('VALE', '2026-12-18', 6.881, 12.779)]
['SYNTH_A'] equity nan rejects {'SYNTH_A': 'NO_QUOTES'} windows [('VALE', '2026-12-18', 6.881, 12.779)]
```
This matches 05's numbers. The 13C is inside 1 of 1 widened window and 0 of 1 unwidened window. Under M3, assertions (ii) (NaN) and (iii) (CAPITAL_UNKNOWN) would also fail on their own, not only (i).

Mutations M1-M4 (04 table), run in /tmp/claude-0/wt085 with `sed` on ccbot/bot.py and restored after each one with `git checkout ccbot/bot.py`. Note: my first pass gave a wrong M2 result. It showed the site-a test failing, because M1 and M2 are same-size edits made within one second, so Python reused M1's stale `.pyc`. I discarded that pass and re-ran all four with `PYTHONDONTWRITEBYTECODE=1`, `python3 -B` and `__pycache__` removed. Real counts, `pytest -q tests/test_held_quote.py`:

| Mutation | Diff | Result | Predicted (04) |
|---|---|---|---|
| none | - | 4 passed | 4 passed |
| M1 | L221 `BrokerMarket(broker, t, date, log)` | 1 failed, 3 passed: `test_run_daily_passes_held_option_at_universe_site` (`assert False`, at (i)) | same |
| M2 | L230 likewise | 1 failed, 3 passed: `test_run_daily_passes_held_option_at_held_only_site` (`assert False`, at (i)) | same |
| M3 | both | 2 failed, 2 passed: both new tests | same |
| M4 | L38-39 deleted | 4 failed: both 083 tests (`assert (13.0 <= 12.779)`, `assert 13.0 == 15.0`) and both new tests | same |
| restored | - | 4 passed; `git status --short` empty | - |

Each of M1 and M2 fails exactly one new test, so the two-fixture design holds (03 step 6). Every failure is an assertion failure, with no ERROR rows (E3).

## Tests re-run (output)
In /tmp/claude-0/wt085 (clean worktree of ceb00ce), Python 3.13.18:
`python3 -m pytest -q tests/test_held_quote.py --durations=0`:
```
0.01s call     tests/test_held_quote.py::test_run_daily_passes_held_option_at_universe_site
0.01s call     tests/test_held_quote.py::test_run_daily_passes_held_option_at_held_only_site
4 passed in 2.05s
```
Full suite `python3 -m pytest -q` (wall 1m19.4s):
```
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 572 passed, 1 skipped in 79.07s (0:01:19)
```
This is the same line as 05's after-change line. The one failure was there before this item: `INCOMPLETE: 083 (log line for I2 does not match its format (item 045) ...; 06 Verdict is PASS but has no 'Sent back to: none' line (item 071))`, which is PR #33's format rules on 083, fixed by 084. The skip is `tests/test_calendar.py:110: could not import 'exchange_calendars'`, which is unrelated. Collection count: 572 tests at ceb00ce^ (scratch worktree, since removed) and 574 at ceb00ce, so the item adds 2 tests.

RI-008 / items 027, 032: `tests/test_safety.py -k oldest` → `1 passed`. It ran rather than skipped: python3.11 is at /usr/bin/python3.11, and python3.10 is not on PATH. `python3.11 -m py_compile tests/test_held_quote.py` gives exit 0.

`python3 scripts/check_handoff.py 085` (in the worktree and in /home/claude/cover-calls, both exit 0):
```
sources count (unique URLs in 01-research.md): 3
fact-check rows: 32
totals line: 32 rows -> 27 as-is, 5 fixed, 0 removed
PASS
```
Item-specific checks:
- Type is EFFICIENCY, not BUG, so the bug-fix part of step 3 does not apply. The guardrail purpose is shown anyway: A1's 083 mutation (M3, which left 344 passed on main) now fails 2 tests.
- RI-002 probe: on top of M3, `rules.option_mark`'s BS mid was replaced by an intrinsic mark `max(day.close - o.strike, 0.0)`. Equity became 2966.0 in both runs and the file gave 2 failed, 2 passed. Directly: `2966.0 == pytest.approx(2962.0)` → False and `nan == pytest.approx(2962.0)` → False. The probe was restored with `git checkout ccbot/`.
- Item 059 / RI-012: the new code classifies no error or reply by matching text. `NoQuote` is caught by class.
- Item 062: this is not a simulator or replay. The tests drive the bot's own `run_daily`, which calls `BrokerMarket.pick` (expiries) with `for_ticker(cfg, t)["monthly_dte"]`/`cfg["monthly_slack_days"]`, and the screen's own strike pick with the config tolerance. The probe confirms the pick is 2026-12-18 and the reject is NO_STRIKE_IN_TOLERANCE.
- Data-window edges: no data-hole check in this item.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat ceb00ce^ ceb00ce`: logs/implementation/2026-11-20.md, tests/test_held_quote.py, work/085/05-build-report.md; ccbot/realtest.py and its TRIGGER files are unchanged, so no head run or diff_reports was needed)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001 (ESCALATED: every window in the item has a measured count, which I re-measured: 13C in 1 of 1 widened window [6.881, 13.0], 0 of 1 unwidened [6.881, 12.779], 0 of 1 quote in delta tolerance, pick 2026-12-18), RI-002 (GUARDED: no default added in ccbot/; an invented intrinsic mark (2966) and NaN equity both fail approx(2962.0), shown by the probe above), RI-010 (ESCALATED: the I2 line exists and was written by --log; my line is written with `check_pipeline.py --log` right after this file), RI-014 (OPEN: not applicable, no git or checker change), RI-006 (pytest lines pasted as printed), RI-008 (compiled with python3.11; the oldest-python test passed), RI-009 (all mutations in the scratch worktree, never in the repo), RI-012 (no text-matched error classification)

## Pipeline line (step 2)
check_pipeline line: `085: awaiting A1 (FULL)`

## Sent back / sent to Audit
Nothing sent back. Sent to Audit: yes (07-audit-task.md).
