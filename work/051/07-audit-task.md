# 07 Audit task - 051
A1, please check:
- `python3 scripts/check_handoff.py 051` → PASS; `python3 scripts/check_pipeline.py` → 051 complete after this line.
- On PR #15's head with this script: MAIN AHEAD shown, origin/main and the thread mirror not listed.
- `--next-id` on a branch behind main still counts main's IDs (test).

A1 result: PASS (2026-11-09, on daily-fixes/2026-11-09: check_handoff 051 PASS; PR #15 head with new script → `MAIN AHEAD: origin/main has 2 commits`, no false 036 lines; suite 206 passed, 1 skipped; mutation `behind = False` fails the new test)
