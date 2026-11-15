# 06 Verification - 063
Verdict: PASS (round 1)

Verified 2026-11-15 on branch daily-fixes/2026-11-14 against commit addf948 (I2 build). `git diff addf948 HEAD -- ccbot tests/test_realtest.py` is empty, so HEAD's 063 code is the commit that was checked. Repo read only: no code changed, nothing staged or committed, no log line written by I3 (the orchestrator writes it with `check_pipeline.py --log`). Item 064's files (scripts/check_pipeline.py, tests/test_pipeline_check.py, work/064/, the a1/run-item agent edits) were not touched. Tests, mutations and the real-data run were done in scratch worktrees made with `git worktree add --detach` (wt063, wt063m under the session scratchpad); both were removed afterwards. No brokerage contacted. Data: data/real (historical, committed) and synthetic fixtures. Research, not financial advice.

## I1 audit (plan vs research)
04 follows 03's map step by step. Its Rule trace has a row for each map step (1-7), the Decision, the Missing inputs rows, the Open questions, each correction row and the removed claims. Each row is built or DROPPED with a reason. I checked the 4 "WITH CHANGES" items:
1. "no dates" warning moved from simulate into load_ticker, keyed on data (`er is not None and not earnings and asset != "etf"`). This removes a text match on `td.warnings` that would have been the RI-012 pattern. The sourced reason is valid (RI-012 entry). No unsourced addition.
2. Warning ends "earnings not checked by this rule" for `skip_earnings=False` rules. Sourced to L483: those rules skip the earnings check, so the 03 text would be false for them. New test T4.
3. NaN lead is written as JSON `null` in summary.json. Sourced (Python json docs, RFC 7159, in 04 Extra research 1). Keeps unknown as unknown (RI-002), never 0.
4. The drop case also asserts that at least one sale happens on or after the edge, so the edge cannot over-block. This only adds a check.

Dropped items each have a reason: the request's 120 d threshold (catches 0 of 4, kept as Mutation 2), interior gaps (out of scope, with a named follow-up), option (b), and the removed claims. Numbers re-derived by me: 2019-01-02 to 2019-07-25 = 29+28+31+30+31+30+25 = 204; 2024-01-02 + 100 d = 2024-04-11, + 151 d = 2024-06-01; `_make` lead 2019-01-02 to 01-25 = 23. All match.

One misreading, no effect: 05 Deviation 1 takes 04 Files "step 1b and 4." to mean r3 step 4. In 04 the "4." is the number of the next list item (i3-verifier.md). I2 did what 04 actually asked: one sentence in r3 step 1b and one in i3 step 3. Nothing is missing.

## I2 audit (build vs plan)
I compared `git diff addf948~1 addf948` line by line with 04 Files 1-4.
- ccbot/realtest.py:
  - docstring: as planned.
  - REALTEST_MISSING row `earnings_before_first`: as planned.
  - load_ticker "no dates" warning: as planned (change 1).
  - `_earnings_known` body is `bool(td.earnings) and td.earnings[0] <= d and td.earnings[-1] >= d`, with the planned docstring.
  - simulate: lead from `days[0]` after `days` is set; `max(lead, 0)` int or `float("nan")`; edge warning only when `lead > 0`, ending per `rule.skip_earnings`; the `earnings_lead_days` count; `df.attrs["warnings"]`. All as planned.
  - summarize joins `td.warnings + df.attrs.get("warnings", [])`: as planned.
  - run writes a NaN lead as None: as planned. Nothing else changed.
- tests/test_realtest.py: T1, T2, T4, the empty-file test, T3 asserts, the DROP_CASES key and its branch (all 6 planned asserts), the L312 set extended (the `files ==` line is byte-identical), the NaN asserts in `[earnings]`, ETF and no-dates tests, the `== 0` assert for `[2023-10-01]`, and the fixture edits in only the 3 named control tests. Their assert lines are unchanged and `test_premium_yield_na_zero_years` is untouched. REAL_BAC was re-pinned with `earnings_lead_days=100`. No assert line was removed or loosened: the diff's `-` lines are only the 3 earnings tuples, the DROP_CASES line, the L312 set line (extended) and the REAL_BAC values.
- Agent files: one sentence appended in each. Word diff has no removals. `grep -rl "edges of the data window" .claude/agents` lists 2 files. **This needs the person's OK in PR review (flagged in 05 and in 07).**
- Not changed, as planned: reports/real/ (`git status --short reports` is empty), rules/screen/missing, config, 001 rule text.

Connectivity (re-done):
- `_earnings_known` has one caller, simulate's entry check.
- `_edge` is used by T1, T2 and T4; `_no_nan` by the empty-file test.
- `earnings_lead_days` reaches summary.json `counts_bot_rule_bid` (T3, and the scratch run below, where all 17 tickers carry it).
- The edge warning reaches summary.json `warnings` (T3 and the scratch run).
- The `earnings_before_first` row is enumerated by `test_realtest_missing_lists_every_input`.
- No TODO in the diff.

Grep reasons in 05: the missing-data grep on ccbot/realtest.py gives exactly two new hits, L226 (`er is not None and ...`) and L413 (`lead is not None and lead > 0`). Each one only adds a warning and gives nothing a pass or a value, so 05's reasons hold. The other hits (L446, 466, 481, 496, 522) predate 063.

Data-hole edges (i3 step 3, the new sentence):
- Before the first value: the new `earnings[0] <= d` clause, tested by T1, T2 and the drop case.
- After the last value: the existing `earnings[-1] >= d` clause, tested by `test_stock_without_earnings_sells_nothing` `[2023-10-01]` → UNKNOWN. A call whose life passes the last listed date is already BLACKOUT, because that date lies inside the life.
- Between values: interior gaps over 120 d still only warn. This is out of scope as stated in 03/04, with a named follow-up.

Rule the person follows (001): unchanged. realtest is research only, and its earnings check now means the same as the bot's fail-closed EARNINGS_UNKNOWN. No 001 text change and no request needed.

RI-012 / item 059: no new code classifies anything by matching text. The "no dates" warning is keyed on data, and the tests pin the numeric `earnings_lead_days`. Item 062: realtest still calls `expiries.pick_expiry` (L349, L353) and `pricing.pick_strike` (L358) with the config values. 063 does not touch the pickers.

## Tests re-run (output)
Scratch worktree at addf948, `python3 -m pytest -q -p no:cacheprovider tests/test_realtest.py`:
```
...........................................                              [100%]
43 passed in 25.03s
```
Full suite in the repo (HEAD, which also holds 064's I1/I2 work in progress), `python3 -m pytest -q -p no:cacheprovider`:
```
298 passed, 1 skipped in 49.19s
```
(05's single failure, `INCOMPLETE: 064`, has cleared now that 064's I1 line is written.)

RI-008: `python3 -m pytest -q -p no:cacheprovider -rs tests/test_safety.py -k compiles` → `1 passed, 8 deselected in 0.09s`. It ran and was not skipped: python3.11 is on PATH (/usr/bin/python3.11); python3.10 is not.

`python3 scripts/check_handoff.py 063`:
```
sources count (unique URLs in 01-research.md): 4
fact-check rows: 49
totals line: 49 rows -> 34 as-is, 12 fixed, 3 removed
PASS
```

BUG fix + guardrail (step 3). The original error was `_earnings_known` = `bool(td.earnings) and td.earnings[-1] >= d`. Mutation M1 puts exactly that body back, which shows the guardrail would have caught it. Each mutation below was made in the scratch worktree wt063m, then `pytest tests/test_realtest.py` was run, then `git checkout` restored the file (`git diff --quiet` → restored each time):
- M1, delete `td.earnings[0] <= d and` (the RI-002 removed-default probe and the RI-002 GUARDED condition):
  ```
  FAILED tests/test_realtest.py::test_leading_edge_100_days_blocks
  FAILED tests/test_realtest.py::test_leading_edge_151_days_blocks
  FAILED tests/test_realtest.py::test_drop_input[earnings_before_first]
  FAILED tests/test_realtest.py::test_real_counts_bac[d0.275_dte30-45_noE_hold_bid]
  FAILED tests/test_realtest.py::test_real_counts_bac[d0.150_dte14-24_noE_hold_bid]
  FAILED tests/test_realtest.py::test_real_counts_bac[d0.450_dte30-45_noE_hold_bid]
  6 failed, 37 passed in 51.95s
  ```
- M2, the request's threshold `(td.earnings[0] - d).days <= EARNINGS_GAP_WARN and`. T1 fails and T2 passes, as planned. This shows why the 100 d fixture is needed:
  ```
  FAILED ...test_leading_edge_100_days_blocks
  FAILED ...test_drop_input[earnings_before_first]
  FAILED ...test_real_counts_bac[d0.275_dte30-45_noE_hold_bid]
  FAILED ...test_real_counts_bac[d0.150_dte14-24_noE_hold_bid]
  FAILED ...test_real_counts_bac[d0.450_dte30-45_noE_hold_bid]
  5 failed, 38 passed in 49.45s
  ```
- M5 (mine, RI-002 "put back a default"), lead `float("nan")` → `0` when unknown:
  ```
  FAILED ...test_stock_without_earnings_sells_nothing
  FAILED ...test_etf_without_earnings_sells
  FAILED ...test_empty_earnings_file_warns_and_lead_is_null
  FAILED ...test_drop_input[earnings]
  4 failed, 39 passed in 23.88s
  ```
- M3, the "no call sold" text for every rule → `FAILED ...test_leading_edge_rule_without_earnings_check_still_sells`, 1 failed, 42 passed.
- M4, the NaN → None line in `run` removed → `FAILED ...test_empty_earnings_file_warns_and_lead_is_null`, 1 failed, 42 passed.
- M6 (mine), `df.attrs["warnings"] = []` (warning never reaches reports) → 5 failed: `test_run_end_to_end`, T1, T2, T4, `test_drop_input[earnings_before_first]`.

RI-001 feasibility re-run:
- `test_real_counts_bac` (3 rules) passes on data/real with BOT_RULE calls_sold 22, rej_EARNINGS_UNKNOWN 60 and earnings_lead_days 100.
- L417-418 (every non-INFO count > 0) passes.
- 05's numbers match the pinned dict, and 05's 247 matches my run below.

Real-data scratch run (my own, `python3 -m ccbot.realtest --out <scratch>/after063 --mc-paths 200` in wt063, 14m25s). summary.json parses with a strict `parse_constant` (no NaN token). `skipped` is ITUB, KGC, PBR, VALE. calls_sold total is **247** (committed reports/real before: 250). Per ticker (calls / lead / rej_EARNINGS_UNKNOWN):
- AAL 4/17/21, BAC 22/100/60, BMY 13/31/22, CMCSA 12/17/21, CSX 38/107/58, F 11/29/22
- HBAN 15/17/21, KEY 13/17/23, KMI 16/16/21, MDLZ 34/23/18, MO 23/24/19, OXY 7/52/23
- PFE 12/22/15, PYPL 13/23/20, T 1/23/24, USB 10/100/59, VZ 3/24/22

This is identical to 05's table, and all 17 tickers still sell at least one call. Trade open-date diffs against the committed reports/real/trades_*.csv:
- BAC dropped 2020-01-06 and 2020-02-21.
- USB dropped 2020-01-06.
- OXY dropped 2020-01-06.
- CSX dropped 2020-01-06, 02-21, 05-27 and 08-26, and added 04-29, 06-19, 07-24, 08-21 and 09-18.

These are the same as 05: 6 direct blocks, plus a path shift for CSX. The 4 warning lines for BAC, CSX, USB and OXY are byte-identical to 05's pasted lines. The scratch output was deleted with the worktrees, and reports/real/ is unchanged.

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-002 (ESCALATED); RI-003, RI-004, RI-005, RI-006, RI-007, RI-008, RI-009, RI-010, RI-011, RI-012 (GUARDED, scanned)
- RI-001: the edge rule's feasibility was re-measured. BAC's pin passes, 17/17 reported tickers still sell, and the 247 total in 05 matches my run.
- RI-002: unknown stays unknown. The lead is NaN in simulate and null in JSON, never 0 (M5 → 4 failures). M1 (the old body) → 6 failures, which meets this entry's "Move to GUARDED when" test once merged. Edges were checked before the first and after the last value.
- RI-003: not touched (no calendar change).
- RI-004: fixtures checked against the trigger (T1 2024-04-11 > 01-02 → UNKNOWN; controls 2023-10-25 ≤ 01-02 ≤ 2024-06-01 still sell).
- RI-005: 100, 151, 23 and 204 were re-derived by hand.
- RI-006: no hand totals. Every count comes from command output.
- RI-007: Scope FULL, and 01-05 exist before this 06. check_pipeline shows `RESEARCH CODE: none` and `UNTRACKED CHANGE: none`.
- RI-008: the compile test ran on python3.11 and passed.
- RI-009: ID CLASH none. One open branch, which has no items.
- RI-010: I3 wrote no log line by hand. The orchestrator uses `--log`.
- RI-011: not touched.
- RI-012: no text classification in the new code. The tests pin the numeric field.

## Pipeline line (step 2)
check_pipeline line: `063: awaiting A1 (FULL)`
- That line is from a run after 06 and 07 were written. The same run gives `INCOMPLETE: 063 (no log line for I3)` and exit 1. This is expected: the orchestrator writes the I3 line with `check_pipeline.py --log I3 063 "PASS | sent to audit: yes"` after this step, and I3 does not write log lines here (task instruction).
- Rest of that run: SKIPPED none, STUCK none. Right after 06 was written (before 07), the item line was `063: in progress (FULL: next 07)`. Before 06 it was `063: in progress (FULL: next 06)` with exit 0.

## Sent back / sent to Audit
Nothing sent back to I1 or I2. Sent to Audit: yes, with work/063/07-audit-task.md.
