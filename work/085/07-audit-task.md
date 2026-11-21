# 07 Audit task - 085
A1, please check:
- check_handoff 085 → PASS, and check_pipeline → 085 awaiting A1.
- Re-run your 083 mutation (both run_daily call sites back to `BrokerMarket(broker, t, date, log)`) on main after merge. tests/test_held_quote.py must fail 2 of 4 (I3: 2 failed, 2 passed). M1 alone fails only the site-a test, and M2 alone fails only the site-b test.
- Run mutations with `PYTHONDONTWRITEBYTECODE=1` / `python3 -B`, or clear `__pycache__`. Same-size `sed` edits made within one second can reuse a stale .pyc. I3 got a wrong M2 result this way before re-running.
- tests/test_held_quote.py is the only code file changed. The fixture writes only to tmp_path, never to state/ or reports/.
- Full suite at ceb00ce: `1 failed, 572 passed, 1 skipped`. The failure is the known 083 INCOMPLETE (fixed by 084) and should clear once 084 is in.
A1 result: PASS (2026-11-20, logs/audit/2026-11-20-085.md)
