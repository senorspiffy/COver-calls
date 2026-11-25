# 06 Verification - 100
Verdict: FAIL (round 1)
Sent back to: I2
Scratch dir: /tmp/claude-0/-home-claude/8c722f74-340b-5bb8-a4ab-b7e171dc99a9/scratchpad/i3-100-r1-_392q1d_

Made with `python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="i3-100-r1-", dir="/tmp/claude-0/-home-claude/8c722f74-340b-5bb8-a4ab-b7e171dc99a9/scratchpad"))'`. Two detached worktrees of cc91abb inside it: `wt` (full suite, untouched) and `mut` (mutations and pipeline runs; each probe restored with `git checkout HEAD -- <file>` in `mut`). No `git stash`. Both worktrees removed at the end.

## I1 audit (plan vs research)
- The 04 Rule trace covers every 03 map step (1-5), the prevention guardrail and every Missing inputs row. The two DROPPED rows cite sources: 02 AGAINST 2 for the shared helper, and 03's WRONG row R1 guardrail 4 for the replace-decode mutation.
- Additions beyond 03: there are two absent-case parametrize rows (`""` and `"Waived: 04 05 06"`), so the expected count is 11 cases / base + 4. They come from 03's own Missing inputs table (no Waived line, empty group 2), so they are sourced, and 04 says so ("Change from 03"). Extra research 1 (UnicodeError.object, with a URL) and 2 (the byte-59 recount) are sourced. Extra research 3 (`classify`'s undated 03/06 waiver) is a note for A1 and makes no change.
- Fit: the change is tooling only. No rule the person follows changes, so no 001 text or request is needed. I1 has no problems.

## I2 audit (build vs plan)
- `scripts/check_pipeline.py` (`git show cc91abb`): `_build_waived` matches 04 Files 1 line by line (`parse_request` steps, `WAIVED_LINE.search`, `bool(m and PERSON_DATED.match(m.group(2)))`, `who` check removed). The docstring and the L538-541 comment match. Nothing else changed.
- `tests/test_pipeline_check.py`: 4 rows added (2 RI-012 in-text negatives and 2 absent rows) and the N-g fixture is now `REQ_FULL_093.encode("utf-8") + b"\xff"` with the byte-59 assert. This matches 04 Files 2 and the Guardrail tests.
- Connectivity re-done: there is no new function. `_build_waived` has one caller, `_research_code` (`grep -n "_build_waived(" scripts/check_pipeline.py` → the def and the one call). It takes `_read` text and feeds the RESEARCH ONLY excuse. Every branch ends in False or a strict reason (rows `""`, `Waived: 04 05 06`, N-g, N-h).
- 05's grep reasons check out: the 2 diff hits are a docstring `<why>` and a set-subset `<=`, and no ccbot/ file changed.
- Data-hole edges: not applicable. There is no data window, and absent and empty inputs are covered above.
- RI-012 negative test with the pattern inside other text: present (the F1 quoted line and `(person) x (person, ...)`), so this is not a FAIL.
- Simulator rule (062): not applicable.
- **Problem (FAIL, I2):** 05's line `Scratch dir: /tmp/.../i2-100-r1b-twin92si` does not fullmatch `SCRATCH_NAME` (`(i2|i3)-(\d{3})-r\d+-[a-z0-9_]{8}`, check_pipeline.py L457), because `r1b` is not `r<round>`. Item 097 says the prefix is `i2-<ID>-r<round>-`. As a result:
  - `check_pipeline.py` at cc91abb gives `INCOMPLETE: 100 (05 Scratch dir '...i2-100-r1b-twin92si' is not the mkdtemp form (item 097))` and exits 1.
  - The full suite at cc91abb is red: `test_repo_pipeline_has_no_skipped_items` fails (`assert 1 == 0`). So 05's `Suite: 963 passed, 1 skipped` does not hold at the commit that contains 05. It held only before 05 was written.

## Tests re-run (output)
Full suite, `python3 -m pytest -q` in worktree `wt` at cc91abb:
```
=========================== short test summary info ============================
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 962 passed, 1 skipped in 130.72s (0:02:10)
```
The failure is the INCOMPLETE line above. It reproduces alone in `mut` with no mutation applied (`-k test_repo_pipeline_has_no_skipped_items` → `1 failed, 502 deselected in 5.30s`). The other 962 tests pass, and the count matches 05 (963 = base 959 + 4).

Oldest Python: `tests/test_safety.py -k oldest` → `1 passed` (python3.11 on PATH, no python3.10). This is not skipped. `python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py` → exit 0.

Mutations, run one at a time in `mut` with `python3 -m pytest -q tests/test_pipeline_check.py`, restored after each. Each run also fails `test_repo_pipeline_has_no_skipped_items`. That failure comes from the 05 INCOMPLETE above and is present with no mutation, so it is not a kill.
```
== M-a  (original code: who == "person" and WAIVE_BUILD_BY_PERSON.search(waived_line))
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (person: x "(person, 2026-11-19: ok)")-False]
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (person) x (person, 2026-11-13: ok)-False]
3 failed, 500 passed in 68.24s (0:01:08)
== M-a2 (bare WAIVE_BUILD_BY_PERSON.search(waived_line))
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (I2, 2026-11-13: copied "(person, 2026-11-12: ok)")-False]
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (person: x "(person, 2026-11-19: ok)")-False]
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (person) x (person, 2026-11-13: ok)-False]
4 failed, 499 passed in 64.41s (0:01:04)
== M-b  (PERSON_DATED.search(m.group(2)))
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (I2, 2026-11-13: copied "(person, 2026-11-12: ok)")-False]
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (person: x "(person, 2026-11-19: ok)")-False]
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (person) x (person, 2026-11-13: ok)-False]
4 failed, 499 passed in 67.05s (0:01:07)
== M-c  (WAIVE_BUILD_BY_PERSON = re.compile(r"\(\s*person\s*[,:]"))
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (person: ok)-False]
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (person: x "(person, 2026-11-19: ok)")-False]
FAILED tests/test_pipeline_check.py::test_person_dated_anchor - AssertionErro...
FAILED tests/test_pipeline_check.py::test_batch_waiver_not_excused_stays_strict[N-b]
FAILED tests/test_pipeline_check.py::test_batch_waiver_not_excused_stays_strict[N-d]
FAILED tests/test_pipeline_check.py::test_batch_waiver_missing_inputs_strict[N-j]
7 failed, 496 passed in 64.66s (0:01:04)
== M-d  (subset check dropped)
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 (person, 2026-11-13: x)-False]
2 failed, 501 passed in 66.28s (0:01:06)
== M-F2 (in _read's decode branch after _UNREAD is set: assert isinstance(err.object, bytes); return err.object replace-decoded, None)
-k test_batch_waiver_missing_inputs_strict:
E       AssertionError: assert [('990', 'no ..., item 093)')] == [('990', 'no line before I2')]
FAILED tests/test_pipeline_check.py::test_batch_waiver_missing_inputs_strict[N-g]
1 failed, 3 passed, 499 deselected in 2.44s
whole file: 27 failed, 476 passed in 69.53s (0:01:09)   (I2's 26 + test_repo_pipeline_has_no_skipped_items; N-g among them)
== M-F2 with the old b"\xff" fixture and old body (byte-59 assert removed), -k test_batch_waiver_missing_inputs_strict
4 passed, 499 deselected in 0.73s
```
Apart from the extra repo-pipeline failure, every mutation is killed by the same named tests as in 05. `isinstance(err.object, bytes)` never fired. F2 evidence reproduced: the old N-g passes under M-F2, and the new N-g fails.

BUG guardrail: M-a is the original pre-fix `_build_waived` expression. Both new in-text rows fail under it, so the guardrail would have caught the original error (A1's F1 line is the first failing row). The fix (anchored `.match`) and the guardrail (the rows plus the M-a/M-a2/M-b kills) are both in place. RI-002 default probe: no default was removed in this item, so there is nothing to put back. The absent rows (`""`, `Waived: 04 05 06`) pin False. RI-001 feasibility: re-run as the pipeline output diff below (IDENTICAL, 0 of 2 called RESEARCH ONLY items change).

`python3 scripts/check_handoff.py 100` (main checkout, exit 0):
```
sources count (unique URLs in 01-research.md): 2
fact-check rows: 43
totals line: 43 rows -> 40 as-is, 3 fixed, 0 removed
PASS
```

## Real-data effect (diff_reports output, pasted)
not required (scripts/check_pipeline.py, tests/test_pipeline_check.py; neither is in TRIGGER / TRIGGER_DIRS). Pipeline output in `mut` at cc91abb, with the base script (`git show cc91abb^:scripts/check_pipeline.py`) and then the head script, `diff cp-base.txt cp-head2.txt && echo IDENTICAL`:
```
IDENTICAL
```
(Both exit 1, only because of the 05 INCOMPLETE for 100. 023 and 057 read `complete (RESEARCH ONLY ...)` in both.)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-010, RI-014 (open/ESCALATED); also RI-002, RI-012
- RI-001 (ESCALATED): no new occurrence. The one count rule (RESEARCH ONLY excuse, 2 called, 0 True before and after) was re-measured by the IDENTICAL output diff and the 11-case test.
- RI-010 (ESCALATED): the guardrail worked. Item 097's Scratch dir check caught 05's non-mkdtemp-form line (`r1b`), and that is this FAIL. It is not counted as a new occurrence: the checker flagged it before merge.
- RI-014 (OPEN): no new occurrence. There is no git read and no new file read, and `test_read_census` is green. M-F2 was a scratch-only change.
- RI-012 (GUARDED): holds. The in-text negatives are present, and M-a/M-a2/M-b are killed.
- RI-002 (GUARDED): holds. The absent inputs give False or the strict reason.

## Pipeline line (step 2)
check_pipeline line: `100: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))`

Also on that run: `INCOMPLETE: 100 (05 Scratch dir '/tmp/claude-0/-home-claude/8c722f74-340b-5bb8-a4ab-b7e171dc99a9/scratchpad/i2-100-r1b-twin92si' is not the mkdtemp form (item 097))`.

## Sent back / sent to Audit
Sent back to I2 (round 2):
1. 05's `Scratch dir:` line names `i2-100-r1b-twin92si`, which is not the item 097 mkdtemp form (`i2-<ID>-r<round>-<8 chars>`). check_pipeline reports `INCOMPLETE: 100` (exit 1), and `test_repo_pipeline_has_no_skipped_items` fails at cc91abb (full suite `1 failed, 962 passed, 1 skipped`). Make the round 2 scratch dir with the run-item.md command (prefix `i2-100-r2-`) and re-run the suite there. Record it under `## Test output (round 2, pasted)` with a `Scratch dir:` line for every dir used. A dir whose name does not match must not be listed as a path: use `none (<reason>)` or redo the work. Then confirm that `python3 scripts/check_pipeline.py` shows no INCOMPLETE for 100 and that the full suite is green at the committed head.
2. The code and test change itself matches the plan and needs no change.
Not sent to Audit (no 07).
