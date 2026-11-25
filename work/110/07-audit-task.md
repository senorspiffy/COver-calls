# 07 Audit task - 110
Audit should look at:
1. The decision: 03's NO-GO on (a) bare summary line under a `#{1,2} round N` wrapper and (b) `N deselected` runs rests on the orchestrator's run of R1's script at 4404a28 (01 L151-270). Re-run it on the current head if desired: 4 in 58 files, 0 at >=092; 34 files gain values, `FILES WHOSE MAX CHANGED: 0`, six `batch_log_items` keys same=True, checked 59.
2. 04's FIT WITH CHANGES: comment wording "deselected runs (-k/-m/--deselect)" instead of 03's "-k runs" (pytest docs, 04 Extra research 1) and the extra positive assert on (ii). Accept or reject.
3. The diff at bc96b01: scripts/check_pipeline.py docstring/comment only (SUMMARY_LINE.pattern and _STATS byte-identical before/after), tests/test_pipeline_check.py +1 test; mutations M0-M5 (+M2b, M4b) in 06 all killed.
4. Watch triggers for A1's daily review (03 map step 4): an `A` line at >=099 classed R, `FILES WHOSE MAX CHANGED` > 0, or any `batch_log_items[...] same=False` would reopen (a) or (b). Copy the RI-010 near-miss closure to recurring-issues.md on main (036).
A1 result: PASS (2026-11-25, logs/audit/2026-11-25-110.md)
