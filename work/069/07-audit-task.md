# 07 Audit task - 069
A1, please check:
- **Pipeline checks**
  - `python3 scripts/check_handoff.py 069` should give PASS (57 rows -> 50 as-is, 6 fixed, 1 removed).
  - `python3 scripts/check_pipeline.py` should show `069: awaiting A1`, `INCOMPLETE: none`, `UNTRACKED CHANGE: none`, `RESEARCH CODE: none`, `LOG TIME: none`, `INBOX: not checked (no daily report from 2026-11-18)`, exit 0.
  - `.claude/agents/a1-auditor.md` and `.claude/commands/daily-audit.md` change. This is a RULES BRANCH and needs the person's OK in PR review.
- **Build, tests and mutations**
  - Round 1 build 8dc2c2d: a1-auditor.md (Inbox step 2a-2d), daily-audit.md, templates/daily-audit.md, scripts/check_pipeline.py (`inbox_section`, INBOX line, exit 1), tests (11 inbox cases).
  - Round 2 fix dc162cf: the template placeholders are now `<fill in>`, so an unfilled template fails INBOX. Tests xi, xii and xiii were added.
  - Suite (I3, scratch at dc162cf): 377 passed, 1 skipped (exchange_calendars), test_pipeline_check 104, `-k inbox` 14. The compile test ran on python3.11.
  - Mutations (I3): round 1 m1-m7 fail (06 round 1). In round 2, m8 (no `^` on INBOX_PI/HUB) fails 1 (xi), m9 (no `^` on INBOX_HEAD) fails 1 (xii), and the round-1 template fails 1 (xiii).
  - Re-run on main after merge: m8 and m9 should fail. This is RI-012's pattern-inside-other-text rule applied to INBOX.
- **Interaction with 070 (same branch)**
  - 070's REAL-DATA FIELD code (scripts/check_pipeline.py, tests/test_real_data_field.py) is unchanged by 069 round 2: `git diff --stat 875158e dc162cf -- scripts tests/test_real_data_field.py ccbot` is empty. Check that the INBOX and REAL-DATA FIELD blocks both still feed the exit code once 070 is done.
- **Live behaviour to watch**
  - The first daily report under the new template is due 2026-11-18. After it, the INBOX line should say `none` (or a file name with a reason), not `not checked`. Check that A1 filled both `<fill in>` lines with one of the listed forms and wrote no "nothing new" for an unreadable channel.
  - The status writes to /mnt/project-files/project-inbox (step 2d) happen outside the repo. Check that the 11-18 report lists each write and each failed write.
- **Design calls to judge**
  - The check fails only on unfilled placeholders and missing lines. It does not check that the hub SHA is the actual origin/main, or that the "N seen before" count is right. Judge whether that is enough.
- **Recurring issues**
  - No new occurrence. RI-012 is applied (xi, xii). RI-010 is extended (INBOX check, unfilled template). RI-001 and RI-002 stay ESCALATED, and RI-013 stays OPEN (n/a).
A1 result: FAIL (2026-11-18, logs/audit/2026-11-18-069.md: suite 377/1 skipped, check_pipeline exit 0, check_handoff PASS and I3 mutations m8/m9/mt reproduced at ecc1538; FAIL: INBOX_FROM "2026-11-18" makes main exit 1 at merge on a daily report written under the old template (probe P1, exit=1) -> back to I1/I2; SHA 7-char minimum unpinned (m10 survives))

## Round 3 (I3 PASS 2026-11-18, build 21d7591, branch head f77247f)
A1, please re-check:
- **Pipeline checks**
  - `python3 scripts/check_handoff.py 069` gives PASS (57 rows -> 50 as-is, 6 fixed, 1 removed).
  - `python3 scripts/check_pipeline.py` gives `069: A1 FAIL (...)` and exit 1 until your new A1 result line is written. Everything else should be `none`, with `INBOX: not checked (2026-11-17.md added in b268a22; its templates/daily-audit.md has no ## Inbox)`.
  - With only the FAIL line dropped (I3 scratch commit), `test_repo_pipeline_has_no_skipped_items` passes and the exit is 0.
- **Send-back 1 (P1)**
  - `INBOX_FROM` is gone. `_inbox_gate` checks a daily report only if `templates/daily-audit.md` at the report's adding commit (`git log --no-renames --diff-filter=A -1`) has `## Inbox`. An uncommitted report is judged by the working-tree template.
  - Re-run P1 as real merges onto origin/main, with an old-format 2026-11-18.md committed on main first. I3 got `not checked`, exit 0, after both `--no-ff` and `--squash`. An unfilled new-format 2026-11-19.md then gave exit 1. The round-1 code on the same history still gave exit 1 on 2026-11-18.md.
  - Tests xiv, xiv-b and xiv-c[main/t] pin this. With the round-1 code, 12 of 30 inbox tests fail.
- **Send-back 2 (P2)**
  - xvi[116c68 / 2026-11-18 / 41 hex]: m10 `{1,40}` fails 2 and `{7,}` fails 1.
- **Other mutations (I3, 06 Round 3)**
  - gate always None: 10 failed.
  - gate always not checked: 27 failed.
  - `HEAD:` instead of `<sha>:`: 5 failed.
  - no `--diff-filter=A`: 1 failed.
  - shallow guard off: 1 failed.
  - git log failure hidden (two forms): 1 failed each.
- **Suite**
  - 1 failed (repo test, from A1 FAIL only), 399 passed, 1 skipped. `-k inbox` 30 passed. The compile test ran on python3.11.
- **Design calls to judge**
  - Known gap (u): an uncommitted report pulled under a new template is judged by the new one. Is "commit the daily report before pulling" enough?
  - Shallow clones are always `not checked`. Does CI or the VPS ever run on a shallow clone, where INBOX would then never be checked?
  - The gate keys on any `## Inbox` heading in the template at the adding commit.
- **Interaction with 070**
  - 069 round 3 changes no 070 line (`git diff 8dfc800 21d7591` has 0 REAL_DATA/TRIGGER/TOTAL_LINE hits; tests/test_real_data_field.py and ccbot are unchanged).
  - During I3 the real tree had an uncommitted 070 edit to tests/test_real_data_field.py (t7b, t7c), committed since under 070 by its own I2. Check that no 069 commit carries it.
- **Live behaviour**
  - The first daily report added after this branch merges is checked by content. Every report added on main before the merge stays `not checked`.
- **Recurring issues**
  - RI-010 fix (record A1's proposed occurrence in the daily review). RI-001 and RI-002 stay ESCALATED and were checked. RI-011 and RI-012 held. RI-013 n/a.
A1 result: PASS (2026-11-18, logs/audit/2026-11-18-069.md 'Re-audit (round 3)': P1 replay --no-ff/--squash not checked; m10 2 failed; gate mutations g1-g6 caught)
