# 07 Audit task - 060
A1, please check:
- check_handoff 060 → PASS; check_pipeline → 060 awaiting A1.
- `_dip` window is 20 NYSE trading days ending today; a gap in the snapshots does not pull in an older high.
A1 result: PASS (2026-11-12, logs/audit/2026-11-12.md: window re-computed 251/251; gap test fails without the date filter; check_handoff PASS)
