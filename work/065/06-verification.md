# 06 Verification - 065
Verdict: PASS (round 1; earlier rounds: none)

Verified against committed HEAD e129253 ("Item 065: I2 build") on branch daily-fixes/2026-11-15. Mutations and real-data runs used scratch detached worktrees /tmp/claude-0/i3-065-before (HEAD~1, 063's realtest), /tmp/claude-0/i3-065-after (HEAD) and /tmp/claude-0/i3-065-mut (HEAD). All three were removed afterwards (`git worktree list` shows only the repo). reports/real/ was not regenerated (`git status --short reports` → empty). No brokerage was contacted. Research, not financial advice.

## I1 audit (plan vs research)
- 04 restates 03's decision (block, option a). The Rule trace covers every 03 map step (1-6), the Notes, both Out-of-scope items (DROPPED with reasons), every Missing-inputs row, and the 03 corrections.
- The 6 "WITH CHANGES" points each give a reason drawn from the code. None is an unsourced addition:
  1. REAL_BAC gets the new key and INFO gets an entry. The whole-dict `==` and the `> 0` check would otherwise fail. BAC's value 0 was measured. No existing value changed.
  2. The warning gate uses `_gap_pairs`, not `td.earnings_gaps`, because `_tiny` hard-codes `earnings_gaps=0`. I3 mutation (v) confirms that the gate on `td.earnings_gaps` fails 2 tests.
  3. NaN → null for the new key in summary.json (json/RFC 8259 sources cited).
  4. The decision still goes through `_earnings_known`, so diag_keep's monkeypatch keeps working.
  5. The count is 0 under skip_earnings=False. 03 was silent on this; 04 defines it.
  6. A real-data pin for MO (RI-001), with the values measured by I1.

## I2 audit (build vs plan)
I read `git show HEAD -- ccbot tests` line by line against 04 § Files:
- **ccbot/realtest.py**
  - `import bisect`, the docstring sentence, the EARNINGS_GAP_WARN comment and the REALTEST_MISSING row all match the plan text.
  - `_is_gap`, `_gap_pairs` and `_earnings_state` match: bisect_right, in the order i == 0 → before_first; equal → known; i == len → after_last; gap → interior_gap; else known.
  - `_earnings_known` is now `== "known"`.
  - `load_ticker`: `gaps = len(_gap_pairs(earnings))`, with the warning text unchanged.
  - `simulate`:
    - The counter starts at NaN for an ETF or a stock with no dates, else 0.
    - It is incremented only inside the EARNINGS_UNKNOWN branch, with a NaN guard.
    - The warning comes from `_gap_pairs`, with rule-dependent text.
    - The key is added to the counts.
  - `run`: the NaN → None loop covers both keys.
- **tests/test_realtest.py**
  - The 5 new tests are present with the planned values.
  - The drop case is added, and the literal set is extended, not loosened.
  - Exactly 3 existing fixture tuples change (`2024-06-01` → `2024-02-20`), at the earnings-today control, take50 and sub-3c.
  - No assert was removed or loosened. The added asserts are the ones 04 lists.
  - REAL_BAC gets `earnings_gap_days=0` ×3, and INFO gets the key with its comment.
- Only the 2 planned code files, plus 05 and the log line, are in the commit (`git show --stat HEAD`). No live-bot file (rules, screen, missing) and no 001 rule text changed. No rule the person follows changes, so no 001 edit or request is needed.
- **Connectivity, re-done:**
  - `_is_gap` ← `_gap_pairs`, `_earnings_state`.
  - `_gap_pairs` ← `load_ticker`, `simulate`, the drop test.
  - `_earnings_state` ← `_earnings_known`, simulate's counter.
  - `earnings_gap_days` reaches summary.json `counts_bot_rule_bid`. In the after-run it is present for all 17 tickers, with values {0, 69, 71, 72} and no bare NaN under a strict parse.
  - The gap warning reaches the per-ticker warnings.
  - No TODO/FIXME.
- **Grep checks:**
  - `EARNINGS_GAP_WARN` is compared only at L383 (`_is_gap`). Its other uses are comments, docstrings, the dataclass comment and the two f-strings.
  - Missing-data grep: 36 hits on HEAD~1, 37 on HEAD. The diff of hit lines is exactly the one new line, `earnings_gap_days = float("nan") if td.asset_type == "etf" or not td.earnings else 0`. 05's reason is correct: 0 starts a real count, and the unknown cases are NaN. The RI-002 probe below shows that a test fails if the NaN branch is removed.
  - `: (float|int) = [0-9]` in realtest.py → empty.
- **Item 062 check:** the simulator's pick path (`_pick` → `expiries.pick_expiry` / `pricing.pick_strike` with the config values) is unchanged. Only the pre-pick earnings gate changed.
- **RI-012 check:** no new code classifies anything by matching text. The gate and the count come from date arithmetic. The tests assert numeric counts as well as warning substrings.

## Tests re-run (output)
```
$ python3 -m pytest -q tests/test_realtest.py
49 passed in 20.84s
$ python3 -m pytest -q
324 passed, 1 skipped in 44.88s
  (skip: tests/test_calendar.py:110 could not import 'exchange_calendars', not this item)
$ python3 -m pytest -q -rs tests/test_safety.py
9 passed in 0.77s
  (test_every_py_compiles_on_oldest_python ran with python3.11; python3.10 is not on PATH)
$ python3 scripts/check_handoff.py 065
sources count (unique URLs in 01-research.md): 5
fact-check rows: 46
totals line: 46 rows -> 37 as-is, 7 fixed, 2 removed
PASS
```
Mutations (I3's own run on a scratch worktree of HEAD, one at a time, `pytest -q tests/test_realtest.py`, file restored and worktree clean afterwards):
```
--- i_before_first_known: 9 failed, 40 passed
    test_stock_without_earnings_sells_nothing, test_leading_edge_100_days_blocks, test_leading_edge_151_days_blocks,
    test_empty_earnings_file_warns_and_lead_is_null, test_drop_input[earnings], test_drop_input[earnings_before_first],
    test_real_counts_bac x3
--- ii_after_last_known: 4 failed, 45 passed
    test_stock_without_earnings_sells_nothing, test_real_counts_bac x3
--- iii_gap_check_removed: 4 failed, 45 passed
    test_interior_gap_180_blocks, test_interior_gap_121_blocks, test_drop_input[earnings_interior_gap], test_real_interior_gap_mo
--- iv_gt_to_ge: 1 failed, 48 passed
    test_interior_gap_120_sells
--- v_warn_on_td_gaps: 2 failed, 47 passed
    test_interior_gap_180_blocks, test_interior_gap_not_checked_rule
--- vi_nan_loop_lead_only: 1 failed, 48 passed
    test_empty_earnings_file_warns_and_lead_is_null
--- RI002_else0_restored (earnings_gap_days = 0 always): 4 failed, 45 passed
    test_stock_without_earnings_sells_nothing, test_etf_without_earnings_sells,
    test_empty_earnings_file_warns_and_lead_is_null, test_drop_input[earnings]
restored: clean
```
All of these match 05. Mutation (i) fails 9 tests rather than the 6 that 04 expected, because "no dates" also has i == 0. 05 states and explains this.

Real-data measurement (`python3 -m ccbot.realtest --out <scratch>/out` on HEAD~1 and on HEAD, committed data/real; BOT_RULE bid, from summary.json `counts_bot_rule_bid`; the after file was parsed with a strict `parse_constant`):
```
skipped b/a equal: True {'ITUB': '... (< 3.0 years)', 'KGC': 'no option quotes', 'PBR': '... (< 3.0 years)', 'VALE': '... (< 3.0 years)'}
tk     calls b  calls a  UNK b  UNK a  gap_days
CMCSA  12       12       21     93     72
MDLZ   34       31       18     87     69
MO     23       21       19     90     71
T      1        1        24     95     71
VZ     3        3        22     94     72
(the other 12 reported tickers are unchanged, with gap_days 0)
total 247 242
bxm same: True
in-gap opens before: MDLZ ['2021-11-03','2021-12-22','2022-01-24','2022-02-23'], MO ['2022-01-19','2022-02-23']; CMCSA/T/VZ none
in-gap opens after: none for all 5
```
This confirms the 247 → 242 claim, the per-ticker table in 05 and the 6 blocked in-gap sales.

**BUG checks (RI-002 remainder):**
- The fix is in place: interior-gap days are EARNINGS_UNKNOWN.
- The guardrail is in place: one shared helper for all edges, the fixture tests and the MO real-data pin.
- It would have caught the original error. On 063's code (= mutation iii), a stock day inside the 180-d gap sells, and `test_interior_gap_180_blocks`, `test_interior_gap_121_blocks`, the drop case and `test_real_interior_gap_mo` all fail (4 failed above).
- RI-001 feasibility re-run: MO 21 calls / 71 gap days. This equals the numbers the test and 05 cite, and the real run above gives the same values.

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-002, RI-003, RI-004, RI-005, RI-006, RI-007, RI-008, RI-009, RI-010, RI-011, RI-012
- RI-001 (ESCALATED): I re-ran the feasibility test. The MO pin (21 / 71) matches my real run, and the 120/121 bar is pinned by fixtures. `earnings_gap_days` in INFO is a data-hole count, not a window rule. BAC has no gap, so its 0 is correct.
- RI-002 (ESCALATED): I restored the removed default on a scratch copy (`earnings_gap_days = 0` for every stock and ETF): 4 failed, then restored. The gap check removed: 4 failed. Unknown stays NaN in counts and null in JSON. This is the remainder of occurrence 10, not a new one. It stays ESCALATED until 063 and 065 are merged and A1 re-probes on main.
- RI-004 / RI-005: the fixture day counts follow from the 03 Self-check (180, 120, 121, 118). The tests that pin them pass, and the 120/121 boundary is shown by mutation (iv).
- RI-006: every count in this file is pasted from command output.
- RI-007: Scope FULL. 01-05 exist, and every step has a log line before this one.
- RI-008: `bisect` is stdlib. The oldest-Python compile test ran with 3.11 (3.10 not on PATH).
- RI-009: the work is on daily-fixes/2026-11-15, unmerged (PR state is for A1). The scratch worktrees were removed.
- RI-010: my log line is written with `check_pipeline.py --log`.
- RI-012: no text-matching classification was added (see the I2 audit).
- RI-003, RI-011: GUARDED, and this item does not touch them.

## Pipeline line (step 2)
check_pipeline line: `065: awaiting A1 (FULL)` (exit 0; INCOMPLETE, SKIPPED, LOG TIME, UNTRACKED CHANGE and RESEARCH CODE all none; before 07 was written it read `065: in progress (FULL: next 07)`)

## Sent back / sent to Audit
Nothing was sent back to I1 or I2. Sent to Audit: work/065/07-audit-task.md.
