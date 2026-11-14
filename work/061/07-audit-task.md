# 07 Audit task - 061
A1, please check:
- check_handoff 061 → PASS; check_pipeline → 061 awaiting A1.
- RESEARCH ONLY: no bot code or config changed. New standalone files: scripts/fetch_real_data.py,
  ccbot/realtest.py, tests/test_realtest.py, data/real/ (free DoltHub/Cboe data), reports/real/.
- pass-criteria.md was committed (bdd67c9) before data/real/ (20b89e7) existed: pre-registration holds.
- 60 variants searched; only the fixed bot rule is used for pass/fail.
- 2026-11-14 re-run after A1 FAIL: _pick now uses the bot's pickers (test added); weekly window dropped (no 5-9 day expiries in the data). Steps 04-06: waiver asked of the person.
