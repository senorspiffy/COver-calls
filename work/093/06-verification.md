# 06 Verification - 093
Verdict: PASS (round 1)
Sent back to: none

Head commit verified: 5c1756e (branch daily-fixes/2026-11-24; base 66e07b9). Scratch dir: /tmp/claude-0/-home-claude/17dd566b-e13e-58fe-b556-13d450b5acde/scratchpad/I3-093-r1-uw7kan4h (made with `tempfile.mkdtemp(prefix="I3-093-r1-", ...)`). Mutations ran on a `git archive HEAD` copy there, never in the repo.

## I1 audit (plan vs research)
- Each of 03's map steps 1-7 has a plan line (04 Rule trace). I checked them against 03 and they match. Removed claim 1 (the I3-only bound) is DROPPED in the plan with 03's reason and recorded as "first I2 round not bounded".
- Additions not in 03, each sourced or reasoned in 04 "Extra research":
  - `PERSON_DATED` is built from `WAIVE_BUILD_BY_PERSON.pattern`, so the pattern has one source. I compared them: it equals 03's literal regex with a leading `\s*`.
  - N-h, N-i and N-j come from 03's Missing inputs table, which listed them with no fixture.
  - M9 pins gap j.
  - Case-sensitivity (3d) and unvalidated dates (3e) are documented, not changed.
  - T-real on work/024 is the RI-001 real count.
  - No unsourced addition.
- request.md asks to "decide whether the per-round bound applies". The plan decides it does not, following 03's removed claim 1, and puts that in the reason text and the docstring.

## I2 audit (build vs plan)
I read `git diff 66e07b9 5c1756e -- scripts/ tests/` line by line against 04 Files 1-2:
- Constants `WAIVED_LINE` and `PERSON_DATED`, with the comment, are placed after `WAIVE_BUILD_BY_PERSON`, as planned.
- `parse_request` uses `WAIVED_LINE.search`. Its behaviour is unchanged: the existing parse_request, classify and `_build_waived` tests pass in the suite below.
- `_person_waived_before_i2` has exactly the planned conditions: the first Waived line, the anchored `.match`, non-empty `pre`, the subset check and the files-absent check. Its docstring covers gap j, 3d and 3e.
- `batch_log_items` reads request.md with `_read(missing_ok=True)`. The reason text is as planned and contains no `;`.
- `incomplete()` and `_build_waived` are unchanged.
- Both docstrings (the module docstring and `batch_log_items`) are updated.
- Tests:
  - [990] is flipped and [089] is unchanged.
  - F is parametrized over `cp.REQUIRED` entries that contain "05" (FULL, FAST).
  - `test_person_dated_anchor`, `test_excused_reason_not_strict` and T-real are added.
  - N-a to N-f run as integration tests, with the SKIPPED flag asserted where the plan says. N-g to N-j are unit tests via `_bl`.
- The two deviations in 05 are harmless:
  - the `_UNREAD` key is the rendered absolute path;
  - `or 024` is added to the mutation `-k`.

Connectivity check, redone:
- `WAIVED_LINE` is used in parse_request and in the helper. `PERSON_DATED` is used in the helper. The helper is called only from `batch_log_items`.
- Its reason reaches `out["not_computable"]`, which main() prints on the LOG BATCH line.
- `incomplete()` compares reasons by equality with BATCH_STRICT, and the new text is not in it (`test_excused_reason_not_strict`).
- `_read` returns `(None, why)` on any decode or OS error (L545-553), so an unreadable request.md cannot reach the helper.
- No dead code, no TODOs.

Grep reasons in 05:
- 0 hits on added lines, which I re-checked by reading the diff.
- The one near-form, `if why is None and text is not None else None`, falls back to strict.
- ccbot/ is not touched.

Data-window edges for the data-hole check:
- Before the first value: request.md missing (N-h) or unreadable (N-g).
- After the last value: a second Waived line (N-j).
- Gaps: a partial set (N-e), a file present (N-f), no Scope (N-i).
- Each one stays strict.

Observation, not a defect (for A1):
- N-g's fixture `b"\xff"` has no Waived text, so N-g alone cannot tell "unreadable and excused" from "unreadable and strict". I2's M8 is killed only by N-g's `_UNREAD` assert.
- I ran a stronger mutation, M8b: keep `_read`, but on failure decode the bytes with `errors="replace"` and pass them to the helper.
  - On a probe item (REQ_FULL_093 + `\xff`), M8b excuses the item. On restored code the same probe gives the strict reason.
  - M8b is still killed: `tests/test_pipeline_check.py::test_read_census` fails (1 failed, 402 passed, 2 skipped), because any file read outside `_read` fails that census.
- So the "unreadable is never excused" rule holds through 089's census. A stronger N-g fixture (a valid person waiver plus a bad byte) would pin it directly.

## Tests re-run (output)
Full suite at 5c1756e, repo root, Python 3.13.18 (`python3 -m pytest -q -rs`):
```
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'
836 passed, 1 skipped in 134.46s (0:02:14)
```
`tests/test_safety.py::test_every_py_compiles_on_oldest_python` ran (python3.11 is on PATH, python3.10 is not): `1 passed, 8 deselected in 0.18s`. It did not skip.

`python3 -m pytest -q tests/test_pipeline_check.py -k "waiv or no_line_before or person_dated or excused or 024"`:
```
30 passed, 375 deselected in 2.57s
```
`python3 scripts/check_handoff.py 093` (exit 0):
```
sources count (unique URLs in 01-research.md): 1
fact-check rows: 29
totals line: 29 rows -> 24 as-is, 4 fixed, 1 removed
PASS
```
Mutations M1-M9, my own script (`I3-093-r1-uw7kan4h/mut.py`, on the archive copy, same `-k` as 05):
```
M1 | 5 failed, 25 passed, 375 deselected in 8.12s | test_batch_no_line_before_i2_strict_from_090[990-INCOMPLETE:, test_batch_person_waiver_before_i2_excused[FAST], test_batch_person_waiver_before_i2_excused[FULL], test_excused_reason_not_strict, test_person_waiver_helper_on_item_024
M2 | 1 failed, 29 passed, 375 deselected in 7.58s | test_batch_waiver_not_excused_stays_strict[N-d]
M3 | 2 failed, 28 passed, 375 deselected in 2.55s | test_batch_waiver_not_excused_stays_strict[N-c], test_batch_waiver_not_excused_stays_strict[N-d]
M4 | 4 failed, 26 passed, 375 deselected in 2.98s | test_batch_waiver_missing_inputs_strict[N-j], test_batch_waiver_not_excused_stays_strict[N-b], test_batch_waiver_not_excused_stays_strict[N-d], test_person_dated_anchor
M5 | 2 failed, 28 passed, 375 deselected in 2.66s | test_batch_waiver_missing_inputs_strict[N-i], test_batch_waiver_not_excused_stays_strict[N-e]
M6 | 1 failed, 29 passed, 375 deselected in 2.65s | test_batch_person_waiver_before_i2_excused[FAST]
M7 | 1 failed, 29 passed, 375 deselected in 2.74s | test_batch_waiver_not_excused_stays_strict[N-f]
M8 | 30 passed, 375 deselected in 2.56s |
M9 | 1 failed, 29 passed, 375 deselected in 2.61s | test_batch_waiver_missing_inputs_strict[N-j]
restored | 30 passed, 375 deselected in 2.56s
```
- My M8 was written differently from I2's. It reads the bytes as latin-1 inside the helper call and keeps `_read`, so `_UNREAD` is still recorded, and the `b"\xff"` fixture has no Waived line, so nothing is excused.
- I2's M8 (bypassing `_read`) is killed by N-g's `_UNREAD` assert, as 05 shows. M8b (above) is killed by `test_read_census`.
- M1-M7 and M9 match 05's failing sets exactly.

Bug guardrail (step 3):
- The fix and the guardrail are both in place.
  - The fix: the person-dated excuse.
  - The guardrail: the flipped [990] test, F parametrized over REQUIRED, and 10 strict negatives, each pinned by a mutation.
- The guardrail would have caught the original error. M1 ("helper always None") is the original behaviour: every waived item is strict, the false INCOMPLETE. Under M1, F[FULL], F[FAST], the flipped [990] and T-real all fail.
- RI-001 feasibility, re-run:
  - `cp._person_waived_before_i2` on work/024 gives `['01', '02', '03', '04']`. That is 1 real item, the number 04/05 cite.
  - `grep -l "^Waived:" work/*/request.md` finds only work/023 and work/024, so 0 of the items numbered 090-098 have a Waived line, as cited.
- RI-002: no default was removed in this item. The closest probes are M8 and M8b, which I re-ran and which are killed (above).
- RI-012: the code matches text with an anchored `.match`. N-c and N-d put the quoted person form inside other text, and M2 and M3 are killed by them.
- No rule text the person follows (001) is changed.
- No simulator or replay is involved.
- R2 FOR1 probe (062 follow-up), on this branch:
  - `_build_waived('Scope: RESEARCH ONLY\nWaived: 04 05 06 (person: x "(person, 2026-11-19: ok)")\n')` gives `True`. The hole is confirmed.
  - Not built here, per plan. It is a follow-up item for A1 to open.

Real items are unchanged. I ran the base script (`git show 66e07b9:scripts/check_pipeline.py`) and the head script on this repo. Both exit 0, and `diff` printed nothing.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat 66e07b9 5c1756e`: logs/implementation/2026-11-24.md, scripts/check_pipeline.py, tests/test_pipeline_check.py, work/093/05-build-report.md; no TRIGGER or TRIGGER_DIRS file)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-010, RI-014, RI-002, RI-012, RI-007, RI-008, RI-009, RI-006, RI-004, RI-005 (RI-003, RI-011, RI-013 not applicable)
- RI-001 (ESCALATED): checked. I re-ran the real count: 1 item (024) excused, 0 of 9 items numbered 090-098 affected.
- RI-010 (ESCALATED): checked. Only the exact person-dated, all-pre-05, files-absent shape is excused. The 10 strict negatives pass, and my mutation re-runs kill M1-M7 and M9. M8 is covered by N-g's `_UNREAD` assert or by test_read_census, depending on how the mutation is written. My log line is written with `--log` right after this file.
- RI-014 (OPEN): checked. The helper reads no git, and `_rule_seen(TIMED_FROM)` is unchanged.
- RI-002: absent or unreadable inputs stay strict (N-g, N-h, N-i, N-j, and the M8b probe above).
- RI-012: anchored match, with in-text negatives N-c and N-d.
- RI-007: excused only with `(person, YYYY-MM-DD:`.
- RI-008: test_every_py_compiles_on_oldest_python passed with python3.11.
- RI-009: scratch dir only, with no stash.
- RI-006: every count here is pasted command output.
- RI-004/005: no worked numbers.

RI-001: ESCALATED (unchanged). RI-010: ESCALATED (unchanged; near miss closed by 093, not counted). RI-014: OPEN (unchanged).

## Pipeline line (step 2)
check_pipeline line: `093: awaiting A1 (FULL)` (run after this file and the I3 --log line were written, exit 0)

## Sent back / sent to Audit
Sent to Audit (work/093/07-audit-task.md).
