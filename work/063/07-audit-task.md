# 07 Audit task - 063
A1, please check:
- `python3 scripts/check_handoff.py 063` → PASS (49 rows: 34 as-is, 12 fixed, 3 removed). `python3 scripts/check_pipeline.py` should show `063: awaiting A1` with INCOMPLETE none once the orchestrator has written the I3 line with `--log`.
- RI-002 GUARDED condition: on a scratch copy, delete `td.earnings[0] <= d and` in `ccbot/realtest._earnings_known`. I3 got 6 failed, 37 passed: T1, T2, `test_drop_input[earnings_before_first]` and the 3 `test_real_counts_bac` rules. Do this again on main after merge to move RI-002 to GUARDED.
- Unknown is never 0: on a scratch copy, set `earnings_lead_days = 0` when lead is None. I3 got 4 failed. summary.json writes an unknown lead as `null`, and the strict `parse_constant` load in `test_empty_earnings_file_warns_and_lead_is_null` catches a bare NaN (M4: 1 failed).
- Edges of the data window:
  - Before the first date: the new clause.
  - After the last date: the existing `earnings[-1] >= d` clause. `test_stock_without_earnings_sells_nothing` `[2023-10-01]` → UNKNOWN.
  - Interior gaps > 120 d (CMCSA, MDLZ, MO, T, VZ) still only warn and still sell. This is out of scope. 04 names the follow-up: "realtest interior earnings gaps > 120 d (CMCSA, MDLZ, MO, T, VZ) still sell; decide block vs label". Open it if you agree.
- Real-data effect, measured in a scratch run and not committed (reports/real/ unchanged):
  - Bot-rule calls 250 → 247 (BAC 24→22, USB 11→10, OXY 8→7, CSX 37→38 by path).
  - Leads: BAC 100, USB 100, CSX 107, OXY 52; the other 13 are 16-31 d.
  - No A-row verdict changes (05 table).
  - I3's own run matched 05 ticker for ticker, trade open dates included.
  - Check the "stock only, no sale (earnings unknown)" label and the accepted cost: 1 OXY sale that held no report.
- REAL_BAC re-pin in tests/test_realtest.py:
  - BOT_RULE BLACKOUT stays 104. 04 said "lower". 05 explains why: there was no blackout day before 2020-04-15, and the counts from 2020-04-15 on are identical field for field.
  - Grid 0.15/14-24 NO_STRIKE goes 4 → 0, a path effect. Judge whether 05's explanation covers it.
- Person items for the PR description:
  - (a) The one-sentence additions to .claude/agents/r3-fact-checker.md step 1b and .claude/agents/i3-verifier.md step 3 ("edges of the data window") need the person's OK (03 step 7).
  - (b) 03 Open question 1: whether to commit a regenerated reports/real/. The default is no.
  - (c) The interior-gap follow-up.
- 05 Deviation 1 is a misreading with no effect: 04's "step 1b and 4." is list item 4 (the i3 file), not r3 step 4.
- RI-012: no new text classification. The "no dates" warning is keyed on `er is not None and not earnings and asset != "etf"`.
A1 result: PASS (2026-11-15, logs/audit/2026-11-15-063.md: A1 re-ran on eee257e (addf948 code): tests/test_realtest.py 43 passed, full suite 316 passed 1 skipped; check_handoff 063 PASS 49 rows; check_pipeline 063 awaiting A1, INCOMPLETE/SKIPPED/UNTRACKED/LOG TIME/ORPHAN/ID CLASH none; M1 in scratch worktree 6 failed 37 passed; data/real spot check BAC 24->22, CSX 37->38, USB 11->10, OXY 8->7, BMY 13->13, leads 100/107/100/52/31)
