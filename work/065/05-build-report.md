# 05 Build report - 065

Built 2026-11-15 (UTC) on branch daily-fixes/2026-11-15 from work/065/04-build-plan.md (FIT WITH CHANGES). Research backtest only (ccbot/realtest.py). No brokerage was contacted and no order was placed. Data used: committed data/real (historical sample) and synthetic test fixtures. reports/real/ was not regenerated in the repo (`git status --short reports` → empty); both real-data runs wrote to scratch folders under /tmp/claude-0/. Research, not financial advice.

**Decision restated (for the person): block.** A stock day strictly inside an interior gap of more than EARNINGS_GAP_WARN (120) days between two listed earnings dates is EARNINGS_UNKNOWN, so no call is sold that day. There is no label-only option and no cadence estimate.

File counts (commands run before writing this file; work/ and logs/ excluded):
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` → **0** new
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` → **2** changed (ccbot/realtest.py, tests/test_realtest.py)
- Plus this file and the log line in logs/implementation/2026-11-15.md.
- Item 066's files (tests/test_pipeline_check.py, work/066/05) were uncommitted when I started. 066 was committed during this build (HEAD 5883ba4 "Item 066: A1 result PASS"). I did not touch them.

## Changes made (file: what changed)
- **ccbot/realtest.py**
  - `import bisect` (stdlib).
  - Module docstring: EARNINGS_UNKNOWN also applies "strictly inside a gap > EARNINGS_GAP_WARN days between listed dates (item 065)".
  - `EARNINGS_GAP_WARN` comment rewritten as the plan says.
  - `REALTEST_MISSING`: new row `earnings_interior_gap`.
  - New helpers:
    - `_is_gap(a, b)`: `(b - a).days > EARNINGS_GAP_WARN`. This is the only place the constant is compared.
    - `_gap_pairs(earnings)`: the consecutive pairs for which `_is_gap` is true.
    - `_earnings_state(td, d)`: returns before_first / known / after_last / interior_gap. It uses `bisect_right` in the order from 03 step 1. No dates gives before_first.
  - `_earnings_known(td, d)` now returns `_earnings_state(td, d) == "known"`. It keeps the same name and caller, so diag_keep.py's monkeypatch still works.
  - `load_ticker`: `gaps = len(_gap_pairs(earnings))`. The warning text is unchanged.
  - `simulate`:
    - `earnings_gap_days` is 0 for a stock with dates and NaN for an ETF or a stock with no dates.
    - When a day is blocked as EARNINGS_UNKNOWN and the counter is not NaN, it adds `_earnings_state(td, d) == "interior_gap"`.
    - A gap warning is built from `_gap_pairs(td.earnings)`, not from `td.earnings_gaps`. It reads `earnings: gap(s) > 120 days between listed dates (<a>→<b>, ...)`, followed by "; no call sold inside them (EARNINGS_UNKNOWN)" or "; earnings not checked by this rule".
    - `earnings_gap_days` is added to `df.attrs["counts"]`.
  - `run`: the NaN → None loop now covers `earnings_lead_days` and `earnings_gap_days`.
- **tests/test_realtest.py**
  - New tests: `test_interior_gap_180_blocks`, `test_interior_gap_120_sells`, `test_interior_gap_121_blocks`, `test_interior_gap_not_checked_rule`, `test_real_interior_gap_mo`.
  - New `DROP_CASES` entry `earnings_interior_gap`, with a branch in `test_drop_input` (AAA's Apr and Jul 2020 rows dropped).
  - The literal set in `test_realtest_missing_lists_every_input` is extended with the new entry.
  - Control fixtures: `date(2024, 6, 1)` → `date(2024, 2, 20)` (×3, 118 d). Their assertions are unchanged.
  - `REAL_BAC`: `earnings_gap_days=0` added to all 3 dicts. `INFO` gets `"earnings_gap_days"`, with a comment that it is a data-hole count and not a window rule. No existing value changed.
  - Added asserts:
    - run end-to-end: AAA gap 0.
    - no-dates and ETF: NaN.
    - empty file: NaN in the counts, `None` in summary.json.
    - drop `earnings`: NaN.
    - drop `earnings_before_first`: 0.

## Connectivity check
- [x] Every new function or rule is used:
  - `_is_gap` is used by `_gap_pairs` and `_earnings_state`.
  - `_gap_pairs` is used by `load_ticker`, `simulate` and the drop test.
  - `_earnings_state` is used by `_earnings_known` and by simulate's counter.
  - The new REALTEST_MISSING row is checked by `test_realtest_missing_lists_every_input` and `test_drop_input[earnings_interior_gap]`.
- [x] Every input has a source and every output has a consumer:
  - Input: `td.earnings` (sorted in load_ticker and in `_tiny`).
  - `earnings_gap_days` goes to `df.attrs["counts"]`, then to summary.json `counts_bot_rule_bid` (null when NaN) and grid_in_sample.csv (through `*df.attrs["counts"]`).
  - The gap warning goes to `df.attrs["warnings"]`, then to summarize's `warnings`, which reaches summary.json and bot_rule_by_ticker.csv.
  - Seen in the scratch run: MDLZ's warnings end "...(2021-11-02→2022-04-26); no call sold inside them (EARNINGS_UNKNOWN)".
- [x] Every branch ends in a defined result:
  - The 4 states are each defined.
  - An ETF never reaches the check and its count is NaN.
  - A rule with skip_earnings=False gets count 0 and the "not checked" warning.
  - A stock with no dates gets before_first (UNKNOWN) and NaN.
- [x] No leftover TODOs or unused files: `grep -n "TODO\|FIXME"` on both files is empty. The scratch worktrees /tmp/claude-0/065-base and /tmp/claude-0/065-mut were removed (`git worktree list` shows only the repo).
- `EARNINGS_GAP_WARN` grep: it is compared only in `_is_gap` (L383). Its other uses are the docstrings/comments (L19, L64, L129, L382, L396, L411, L450) and the f-string texts (L191, L455).
- Missing-data grep (`grep -rnE "fillna|nan_to_num|or 0|else 0|..." ccbot/`): 37 hits now vs 36 on HEAD. The single new hit:
  - `ccbot/realtest.py:452: earnings_gap_days = float("nan") if td.asset_type == "etf" or not td.earnings else 0`. Reason: the 0 is the start of a real count for a stock that has dates (each blocked inside-gap day adds 1). Unknown cases (ETF, no dates) are NaN, never 0.
  - No other hit is new or changed.
- 014 patterns:
  - No dataclass field with a numeric default was added (`grep -nE ": (float|int) = [0-9]"` → empty).
  - The new comparisons (`>` in `_is_gap`, `==` on dates) are on `date` values, which cannot be NaN.
  - The NaN counter is guarded explicitly with `isinstance(..., float) and math.isnan(...)` before it is incremented.

## Test output (pasted, not summarized)
Baseline on HEAD before the change (scratch worktree): `python3 -m pytest -q tests/test_realtest.py` → `43 passed in 21.28s`.

After:
```
$ python3 -m pytest -q tests/test_realtest.py
49 passed in 20.93s
$ python3 -m pytest -q
324 passed, 1 skipped in 42.67s
$ python3.11 -m py_compile ccbot/realtest.py tests/test_realtest.py && echo py311 ok
py311 ok
```
The full suite is green, so nothing in it fails from item 066's files. (python3.10 is not installed. 3.11 is the lowest interpreter available, as in RI-008's check.)

Mutations (scratch worktree /tmp/claude-0/065-mut, one at a time, `pytest -q tests/test_realtest.py`):
```
--- mutation (i) i == 0 -> "known": 9 failed, 40 passed
    test_stock_without_earnings_sells_nothing, test_leading_edge_100_days_blocks, test_leading_edge_151_days_blocks,
    test_empty_earnings_file_warns_and_lead_is_null, test_drop_input[earnings], test_drop_input[earnings_before_first],
    test_real_counts_bac x3
--- mutation (ii) i == len -> "known": 4 failed, 45 passed
    test_stock_without_earnings_sells_nothing, test_real_counts_bac x3
--- mutation (iii) gap check removed from _earnings_state: 4 failed, 45 passed
    test_interior_gap_180_blocks, test_interior_gap_121_blocks, test_drop_input[earnings_interior_gap], test_real_interior_gap_mo
--- mutation (iv) > -> >= in _is_gap: 1 failed, 48 passed
    test_interior_gap_120_sells - assert (0 == 1)
--- mutation (v) warning gated on td.earnings_gaps > 0: 2 failed, 47 passed
    test_interior_gap_180_blocks, test_interior_gap_not_checked_rule
--- mutation (vi) NaN -> None loop back to the lead only: 1 failed, 48 passed
    test_empty_earnings_file_warns_and_lead_is_null
```
Mutation (i) fails 9 tests, not the 6 the plan expected. "No dates" also maps to i == 0, so the no-dates and empty-file tests fail as well.

Real data (`python3 -m ccbot.realtest --out /tmp/claude-0/065-before/out` on HEAD code and `--out /tmp/claude-0/065-after/out` on the new code; BOT_RULE, bid fills, start 2020-01-01). The table is pasted from the two summary.json files. The after file was parsed with a strict `parse_constant`, so it contains no bare NaN.
```
skipped before/after (identical): ITUB, PBR, VALE 'option quotes only 2020-01-06 to 2020-12-02 (< 3.0 years)'; KGC 'no option quotes'
tk     calls b calls a  UNK b  UNK a  dUNK gap_days
AAL          4       4     21     21     0        0
BAC         22      22     60     60     0        0
BMY         13      13     22     22     0        0
CMCSA       12      12     21     93    72       72
CSX         38      38     58     58     0        0
F           11      11     22     22     0        0
HBAN        15      15     21     21     0        0
KEY         13      13     23     23     0        0
KMI         16      16     21     21     0        0
MDLZ        34      31     18     87    69       69
MO          23      21     19     90    71       71
OXY          7       7     23     23     0        0
PFE         12      12     15     15     0        0
PYPL        13      13     20     20     0        0
T            1       1     24     95    71       71
USB         10      10     59     59     0        0
VZ           3       3     22     94    72       72
total calls_sold before 247 after 242
bxm_vs_spy unchanged
```
Gaps (`_gap_pairs` on data/real): CMCSA 2021-10-28→2022-04-28 (182 d), MDLZ 2021-11-02→2022-04-26 (175), MO 2021-10-28→2022-04-28 (182), T 2021-10-21→2022-04-21 (182), VZ 2021-10-20→2022-04-22 (184), BAC none. ITUB/VALE/PBR: skipped (< 3.0 years of quotes), no change.

Every measured value matches the expectations in 03/04: CMCSA 12, MDLZ 31, MO 21, T 1, VZ 3; total 242; UNKNOWN deltas +72/+69/+71/+71/+72.

Each changed sale, split into blocked and path effect:
```
MO   dropped 2022-01-19 blocked inside the gap
MO   dropped 2022-02-23 blocked inside the gap
MDLZ dropped 2021-11-03 blocked inside the gap
MDLZ dropped 2021-12-22 blocked inside the gap
MDLZ dropped 2022-01-24 blocked inside the gap
MDLZ dropped 2022-02-23 blocked inside the gap
MDLZ dropped 2022-05-04 path effect
MDLZ dropped 2022-11-30 path effect
MDLZ added   2022-04-27 path effect
MDLZ added   2022-07-27 path effect
MDLZ added   2022-11-02 path effect
```
How MDLZ's path effects arise (checked by tracing the `basis` passed to `_pick` in old and new code):
- Before the change, the in-gap 2021-12-22 call was assigned on 2022-01-21. That re-bought shares and reset the cost basis to 68.37.
- In the old run, the cost-basis floor rejected 2022-04-27 and 2022-05-02 (BASIS_ABOVE_BAND, basis 68.37) and sold on 2022-05-04 at strike 70. In Oct-Nov 2022 it rejected every day until 2022-11-30 (BASIS_ABOVE_BAND or NO_EXPIRY).
- In the new run that sale is blocked, so the basis stays 64.27. 2022-04-27 sells at strike 67.5 (the first day after the 04-26 report), and it is still open on 05-04.
- 2022-07-27 and 2022-11-02 also sell. The 11-02 call is open on 11-30, which removes that sale.
- These are effects of the data hole on the cost-basis path, not sales inside the gap. MDLZ rej_BASIS_ABOVE_BAND 286 → 259.

Feasibility pin (`test_real_interior_gap_mo`): MO calls_sold 21, earnings_gap_days 71, no open_date in (2021-10-28, 2022-04-28). Re-measured here, as above.

Label for the report: a stock day inside a gap reads "stock only, no sale (earnings unknown)". This is a data effect, not a strategy result. Known limit, unchanged: the ADR near-bar intervals (VALE 120 not flagged; PBR 118/119 not flagged, 126 flagged) are not tuned. All three tickers are skipped today.

## Deviations from plan
- None in code or tests.
- Mutation (i) fails 9 tests instead of the expected 6 (reason above). It still fails, so the probe holds.
- The T-gap-noE rule is built with `dataclasses.replace(rt.BOT_RULE, skip_earnings=False)`. It has the same delta and dte as BOT_RULE, which is how the existing 063 test builds it.

RI-001: checked. The interior-gap filter has a dated, measured, non-zero count on real data (2026-11-15: MO 71 / MDLZ 69 / CMCSA 72 / T 71 / VZ 72 blocked attempt days; MO 2 and MDLZ 4 in-gap sales removed), pinned by `test_real_interior_gap_mo`. `earnings_gap_days` in INFO is a data-hole count, not a window rule.
RI-002: guardrail built (065). Interior-gap days are EARNINGS_UNKNOWN, and `earnings_gap_days` is NaN (JSON null) with no dates or for an ETF, never 0. Mutation (iii) (gap check removed) fails 4 tests. GUARDED when 063 and 065 are merged and that probe fails on main. This is the remainder of occurrence 10, not a new occurrence.

Recurring issues checked (logs/recurring-issues.md): RI-001 (ESCALATED) and RI-002 (ESCALATED), as above. RI-004/RI-005: fixture day counts re-run with python `date` (118, 120, 121, 180). RI-006: every count above is pasted from command output. RI-007: Scope FULL, I2 step on 04. RI-008: stdlib `bisect` only; py_compile with 3.11 OK. RI-009: mutations ran only in scratch worktrees, which were removed. RI-010: log line written with `check_pipeline.py --log`. RI-012: the warning gate is computed from `_gap_pairs`, not from text. RI-003 and RI-011: GUARDED, not touched.
