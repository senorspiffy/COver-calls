# 07 Audit task - 068
A1, please check:
- **Pipeline checks**
  - `python3 scripts/check_handoff.py 068` gives PASS (48 rows -> 35 as-is, 12 fixed, 1 removed).
  - `python3 scripts/check_pipeline.py` should show `068: awaiting A1`, `INCOMPLETE: none`, `UNTRACKED CHANGE: none`, `RESEARCH CODE: none`, `LOG TIME: none`, exit 0.
  - `.claude/commands/run-item.md`, `.claude/agents/i2-builder.md` and `.claude/agents/i3-verifier.md` change: this is a RULES BRANCH and needs the person's OK in PR review.
- **Build, tests and mutations**
  - Build at 8f384c9: `ccbot/realtest.py` (load_ticker count-only warning deleted; simulate line gets `{len(gap_pairs)} `), `tests/test_realtest.py` (+1 test, +1 assert), three agent/command texts (one `item 068` sentence each).
  - Suite (I3, clean worktree at 8f384c9): 342 passed, 1 skipped (exchange_calendars not installed); base 341. Compile test ran with python3.11.
  - Mutations (I3, scratch): M1 restore load_ticker line -> 1 failed; M2 drop count -> 2; M3 `td.earnings_gaps` -> 1; M4 interior-gap block removed -> 4. Same as 05.
- **Real-data effect**
  - Base 065-after (c659560, reused; `git diff --stat c659560 0f11c30 -- ccbot/ config/` empty), head 068-after (orchestrator run, wt-068-head; its working tree has `git diff --stat 8f384c9 -- ccbot/ config/` empty). Same data/real hash fa29a0e8..., python 3.13.18, pandas 3.0.5.
  - `diff_reports.py --max-rows 0 065-after 068-after`: TOTAL `files 22, only-before 0, only-after 0, not compared 0, json changes 5, csv rows changed 15 added 0 removed 0, columns changed 0`; I3's output is byte-identical to 05's 068-diff.txt. `compare_068.py`: RESULT PASS (5 warnings leaves, 15 rows, 20/20 other files byte-identical).
  - `--tickers CMCSA,MDLZ,MO,T,VZ` run (068-tk, 3m57s vs 13m43s full) equals the full run for those names and SPY rows (`compare_068_tk.py` PASS).
  - For the person: the only published change is the warnings text for CMCSA, MDLZ, MO, T, VZ (one line per gap instead of two). No number changes. reports/real/ is not regenerated (still pre-065).
- **Design calls to judge**
  - The new i3-verifier sentence says I3 makes one head full run. In 068 a single orchestrator head run served both I2 and I3 (container restart, 05 Deviations); I3 did not run a second one, after checking it matches 8f384c9. Judge whether the rule should say a head run at the same inputs may be reused by I3 the way the base can, or whether I3 must always make its own.
  - The rule is agent text only; nothing in `check_pipeline.py` checks that 05/06 name a scratch `--out` or that `git status --short reports` is empty (03 Missing inputs, `--out` row). Candidate check (RI-010 pattern).
  - Comparison scripts `compare_068.py` / `compare_068_tk.py` stay in the scratchpad, uncommitted (by plan, to avoid a work/ `.py`, item 064). Not re-runnable after the scratchpad is cleared.
- **Recurring issues**
  - No new occurrence. RI-001 and RI-002 stay ESCALATED; RI-013 stays OPEN (068 does not build 067's guardrail).
A1 result: PASS (2026-11-17, logs/audit/2026-11-17-068.md: suite 342/1 skipped and M1-M3 re-run in clean worktree at bd6ec78; diff_reports + compare_068/_tk re-run on 065-after/068-after/068-tk: only 5 warnings leaves + 15 CSV rows change; I3 single head run is a disclosed deviation flagged for the person)
