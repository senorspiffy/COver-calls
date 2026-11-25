# 07 Audit task - 100
Item: 100 (BUG, FULL, RI-012). `scripts/check_pipeline.py::_build_waived` now accepts a person build waiver only when the text after the step numbers passes the anchored `PERSON_DATED.match` (the `who` check removed as implied, 04 Extra research 4). `tests/test_pipeline_check.py`: 4 new `test_build_waiver_needs_person_date_and_all_three` rows (F1 quoted line, `(person) x (person, <date>: ...)`, `""`, `Waived: 04 05 06`) and N-g fixture = `REQ_FULL_093` + `b"\xff"` with the `not UTF-8 at byte 59` assert (F2). Code commit cc91abb, round 2 head 6764567 (05 Scratch dir fix only) on daily-fixes/2026-11-24-b, base c771a21. I3 FAIL r1 (05 Scratch dir `r1b`), PASS r2.

What A1 should look at:
1. Re-run M-a (original `who == "person" and WAIVE_BUILD_BY_PERSON.search`) and M-b (`.match` -> `.search`) on a scratch worktree: the F1 and `(person) x (person, ...)` rows must fail by name.
2. Re-run M-F2 (decode branch returns the replace-decoded `err.object`): new N-g must fail, the old `b"\xff"` fixture passes (F2 evidence).
3. 04 Extra research 3: `classify` accepts `Waived: 03 06 (person: x)` with no date (looser than templates/request.md L5). Not changed here; decide whether it needs its own item.
4. Real output: check_pipeline output with base vs head script was IDENTICAL in 05 and 06 (023, 057 still `complete (RESEARCH ONLY ...)`); confirm on the merged branch.
5. Suite at 6764567: 1 failed, 985 passed, 1 skipped; the failure is `I3 FAIL: 100, 104` only (item 071). After this 06, 100 should no longer be in I3 FAIL; confirm the repo test goes green once 104 also passes.
6. RI status to copy on main: RI-012 GUARDED, holds (this item closes the 2026-11-24 near miss `_build_waived` quoted-person `.search`). RI-010 ESCALATED: near miss in r1 (non-mkdtemp `r1b` scratch name), caught by the 097 check before merge, not counted. RI-001 ESCALATED and RI-014 OPEN, unchanged.
