# 07 Audit task - 070
A1, please check:
- **Pipeline checks**
  - `python3 scripts/check_handoff.py 070` should give PASS (60 rows -> 40 as-is, 20 fixed, 0 removed).
  - `python3 scripts/check_pipeline.py` should show `070: awaiting A1`, `REAL-DATA FIELD: none`, `INCOMPLETE: none`, `RESEARCH CODE: none`, `UNTRACKED CHANGE: none`. At a237da7 it exits 1 only for `A1 FAIL: 069` (069 is being reworked). That is not a 070 defect.
- **Build, tests and mutations**
  - Round 1 build 875158e: scripts/check_pipeline.py (TRIGGER/TRIGGER_DIRS, `_triggers`, `_field_gap`, `_item_triggers`, `real_data_field`, the REAL-DATA FIELD line and its exit term), both template comments, tests/test_real_data_field.py.
  - Round 2 fix a237da7 (tests only, `git diff 7f5e345 a237da7 -- scripts` is empty): T19/T20 (main's exit 1 for `git log failed` and for no request.md), T21 (TOTAL inside prose, 4 cases), T22 (a TOTAL line inside a comment).
  - Suite (I3, scratch at a237da7): 1 failed (test_repo_pipeline_has_no_skipped_items, only from 069's A1 FAIL), 383 passed, 1 skipped. With 069's last 07 line dropped in a scratch commit: 384 passed, 1 skipped. tests/test_real_data_field.py: 28 passed. The compile test ran on python3.11.
  - Mutations (I3, one change each): the exit term fails t19+t20; `"TOTAL" in line` fails 4, `"TOTAL:" in line` 3 and `TOTAL_LINE.search` 2 (all t21); the comment-strip removal fails t22; no-request `failed` fails t20. Re-run the exit-term and `search` mutations on main after merge.
- **Interaction with 069 (same branch)**
  - 069's round-2 rework edits scripts/check_pipeline.py (uncommitted at the time of this verification). Once 069 is rebuilt, check that 069's INBOX block and 070's REAL-DATA FIELD block both still feed main's return, and that tests/test_real_data_field.py still gives 28 passed.
  - On merge, `test_repo_pipeline_has_no_skipped_items` must be green, which needs 069 to have an A1 PASS line.
- **Live behaviour to watch**
  - The first item from 070 on that changes a TRIGGER path or data/real/ must paste diff_reports' TOTAL line in 05 and 06. Check that the check flags it if the paste is missing, and that I3's TOTAL equals 05's (gap (o): the check cannot see that).
- **Design calls to judge**
  - Gaps (m)-(t) in the docstring: conflict-only merge edits, reverted changes, and a TOTAL that is stale but present. Judge whether a TOTAL-line presence check is enough for RI-013 to move to GUARDED.
- **Recurring issues**
  - No new occurrence. RI-012 is applied (T21, T22). RI-002's absent-input exits are tested (T19, T20). RI-013: this is the guardrail for the "→ 070" gap. GUARDED when merged and the T21 `search` mutation fails on main.
A1 result: FAIL (2026-11-18, logs/audit/2026-11-18-070.md: cutoff edge untested - `WHOLE_DIFF_FROM = 100` and `< -> <=` survive the full suite (383 passed); live probe flags 070 as built but not with 100; add an item-070 edge test next to T7; other 12 mutations killed, suite fails only on 069 A1 FAIL)

## Round 3 audit task (I3, 2026-11-18)
Fix 4789b44 (tests only) for A1's FAIL (cutoff edge untested). Look at:
- `git diff --stat aace9dc..4789b44`: only tests/test_real_data_field.py, work/070/05, logs/implementation/2026-11-18.md.
- Re-run A1's two survivors: `WHOLE_DIFF_FROM = 100` and L645 `<` -> `<=` must now fail T7b/T7c (I3: 2 failed each with T7d deselected); also 71 and 69 (I3: killed by T7b/T7c and T7/T7c).
- Replay the live probe (ccbot/costs.py commit) with 100: the suite must now be red.
- T7d ties the constant to the template comment; judge whether that is too brittle or right.
- Full suite fails only on `test_repo_pipeline_has_no_skipped_items` (`A1 FAIL: 069, 070`); I3 confirmed it passes with both last A1 FAIL lines dropped (scratch).
- Earlier open points still stand: T21 `search` mutation on main for RI-013 GUARDED; REAL-DATA FIELD vs 069's INBOX early return after 069's rebuild.
- The boundary-value root cause (also 069) is for the daily review's recurring-issues check.
