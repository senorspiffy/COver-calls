# 07 Audit task - 093
Item: 093 (BUG, FULL). A person-dated `Waived:` on every pre-05 step must not cause a false LOG BATCH INCOMPLETE. Head 5c1756e on daily-fixes/2026-11-24.

What A1 should look at:
1. `scripts/check_pipeline.py`:
   - `_person_waived_before_i2` and the `if not before:` branch of `batch_log_items`. Confirm that only the first Waived line counts, and that it must be person-dated at the start (anchored `.match`).
   - Confirm that the pre-05 set comes from the Scope, and that every pre-05 step file must be absent.
   - Confirm that the excused reason is not in BATCH_STRICT.
2. Re-run the mutations M1-M9 (06 lists each one with its failing tests). Also re-run M8b from 06:
   - M8b: keep `_read`, and on failure pass the `errors="replace"` decode to the helper.
   - It is killed only by `test_read_census`.
   - Decide whether N-g should use a fixture with a valid person waiver plus a bad byte (REQ_FULL_093 + `\xff`), so that the excusal is pinned directly. If so, that is a follow-up item.
3. Open a follow-up item for R2 FOR1. I probed it on this branch: `_build_waived('Scope: RESEARCH ONLY\nWaived: 04 05 06 (person: x "(person, 2026-11-19: ok)")\n')` gives True. 062's `.search` on the whole line accepts a quoted person-dated form.
4. Known gaps, documented but not fixed. Check that they are acceptable:
   - (3d) `person` is case-sensitive. This fails safe.
   - (3e) Dates are not validated.
   - (j) A second Waived line is ignored.
   - The first I2 round of an excused item is not bounded by LOG BATCH (only LOG TIME applies).
5. RI status to copy on main: RI-010 near miss "waiver gap → 093" is closed, not counted. RI-001: T-real on work/024 is 1 real item, and 0 of the items numbered 090-098 change. RI-014: no git read was added.
6. Real items are unchanged. The base (66e07b9) and head check_pipeline outputs on this repo are identical (06).
A1 result: PASS (2026-11-24, logs/audit/2026-11-24-093.md)
