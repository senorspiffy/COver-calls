# 05 Build report - 100
Scratch dir: /tmp/claude-0/-home-claude/8c722f74-340b-5bb8-a4ab-b7e171dc99a9/scratchpad/i2-100-r2-jfe6j8r5

Round 2 (I3 FAIL r1, cbcc301): the round 1 dir's prefix was `i2-100-r1b-`, not the item 097 form `i2-<ID>-r<round>-`, so it is not listed on a `Scratch dir:` line. Every run in round 1 that this 05 relies on was redone in round 2 in the dir above (made with `python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="i2-100-r2-", dir="/tmp/claude-0/-home-claude/8c722f74-340b-5bb8-a4ab-b7e171dc99a9/scratchpad"))'`); see `## Test output (round 2, pasted)`. No code or test change in round 2 (06 item 2: the change matches the plan). The round 1 text below is kept as history.

Built by I2 on branch `daily-fixes/2026-11-24-b`, base c771a21 (plan commit 6a288f5). A first I2 attempt was cut off by a container restart; its uncommitted edits were discarded and this build started fresh from HEAD, in a round 1 scratch dir (not the 097 form, see above) made with `python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="i2-100-r1b-", dir="/tmp/claude-0/-home-claude/8c722f74-340b-5bb8-a4ab-b7e171dc99a9/scratchpad"))'`. Mutations ran in `<scratch dir>/wt` (`git worktree add --detach` at c771a21, with the two changed files copied in); each probe was restored with `cp` from a copy of the fixed files kept in the scratch dir. The worktree was removed before handback (`git worktree list | grep -c i2-100` → 0). No `git stash`. While I built, the branch moved to 2de8e1b (101 A1, work/ and logs/ only; `git diff --stat c771a21 HEAD -- scripts tests` prints nothing).

## Changes made (file: what changed)
- `scripts/check_pipeline.py`
  - `_build_waived(text)`: now `_, _, (steps, _, _) = parse_request(text)`, `m = WAIVED_LINE.search(text)`, `return WAIVE_BUILD <= set(steps) and bool(m and PERSON_DATED.match(m.group(2)))`. The `who == "person"` test and the unanchored `WAIVE_BUILD_BY_PERSON.search` are gone (the anchor implies who = person, 04 Extra research 4). `bool(...)` kept.
  - New docstring (item 062 and item 100): anchored match, quoted person form never counts, format check only, known gaps (case-sensitive `person`, date not validated, first Waived line only).
  - The PERSON_DATED comment block (above `WAIVED_LINE`) now names `_build_waived` (item 100) as a `.match` user beside `_person_waived_before_i2`.
  - Nothing else; `WAIVE_BUILD_BY_PERSON` stays (PERSON_DATED is built from it).
- `tests/test_pipeline_check.py`
  - `test_build_waiver_needs_person_date_and_all_three`: 4 new rows: the F1 line and `(person) x (person, 2026-11-13: ok)` (`# item 100 (RI-012)`), and `""` and `"Waived: 04 05 06"` (`# item 100 (absent)`, from 04 Guardrail tests). 11 cases, 2 True, 9 False.
  - `test_batch_waiver_missing_inputs_strict`: N-g is now `REQ_FULL_093.encode("utf-8") + b"\xff"`; the bytes branch also asserts `cp._UNREAD[path] == "not UTF-8 at byte 59"`; docstring says N-g is a valid person waiver plus one bad byte (item 100, F2). The `no line before I2` assert and the path-in-`_UNREAD` assert are kept.

File counts (item 012), before this 05 was written:
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
0
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
2
$ git diff --stat
 scripts/check_pipeline.py    | 18 ++++++++++++------
 tests/test_pipeline_check.py | 13 ++++++++++---
 2 files changed, 22 insertions(+), 9 deletions(-)
```
2 changed, 0 new, matching the plan's 2 files.

## Connectivity check
- [x] every new function/rule is used: no new function. `_build_waived` keeps its one caller (`_research_code`); `PERSON_DATED` and `WAIVED_LINE` were already defined and are now also used there. The new test rows and the byte-59 assert run in the suite (below).
- [x] every input has a source, every output has a consumer: the input is request.md text from `_read` (unchanged); the output feeds `_research_code`'s RESEARCH ONLY excuse, which ends in the `RESEARCH CODE:` line / SKIPPED reason.
- [x] every branch ends in a defined result: no Waived line → `m` is None → False (`""` row); empty group 2 → `PERSON_DATED.match("")` None → False (`Waived: 04 05 06` row); undated, other who, quoted, `(person) x (...)` → False (rows); missing request.md → unchanged code path (`test_research_code_rules` green); unreadable request.md in batch_log_items → strict `no line before I2` + `_UNREAD` detail (N-g).
- [x] no leftover TODOs or unused files: `git diff -U0 | grep -E "^\+" | grep -nE "fillna|nan_to_num|or 0|else 0|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)|: float = |[<>]"` gives 2 lines: the docstring `<why>` and `WAIVE_BUILD <= set(steps)` (a set-subset test on two sets, never NaN). No TODO. Scratch files only in my scratch dir.
- Missing-data grep: `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/ | wc -l` → `38`, all from before this item (no ccbot/ file changed). No new or changed hit. No dataclass added; no numeric `>`/`<` added.
- Feasibility (plan's named count): RESEARCH ONLY excuse rule, 2 called items (023, 057), 0 True before and after → real-data output diff IDENTICAL (below). `isinstance(err.object, bytes)` confirmed: the M-F2 probe asserts it and did not fire; `python3 -c` on `b"x\xff"` prints `bytes 1`.

## Test output (pasted, not summarized)
Each later round's runs go under their own level-2 heading `## Test output (round N, pasted)`, never under a `###` heading or a `Round N ...` heading (item 091).

Before the fix (base `_build_waived`, new tests), `python3 -m pytest -q tests/test_pipeline_check.py -k "test_build_waiver_needs_person_date_and_all_three or test_batch_waiver_missing_inputs_strict"`:
```
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (person: x "(person, 2026-11-19: ok)")-False]
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (person) x (person, 2026-11-13: ok)-False]
2 failed, 13 passed, 488 deselected in 9.31s
```
The 2 new in-text cases fail (return True); the new N-g and both absent rows pass on base.

After the fix, the plan's must-stay-green set plus the two changed tests (`-k "test_build_waiver_needs_person_date_and_all_three or test_batch_waiver_missing_inputs_strict or test_person_waiver_helper_on_item_024 or test_read_census or test_person_dated_anchor or test_research_code_rules or test_inbox_quoted_scope_and_waiver_are_not_read"`):
```
....................                                                     [100%]
20 passed, 483 deselected in 0.19s
```
`python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py` → exit 0.

Full suite, `python3 -m pytest -q` from the repo root (base was 959 passed, 1 skipped; + 4 rows = 963):
```
........................................................................ [ 97%]
............................                                             [100%]
963 passed, 1 skipped in 131.83s (0:02:11)
```

Round 1 suite line (before 06 existed; superseded by round 2):
```
Suite: 963 passed, 1 skipped in 131.83s (0:02:11)
```

Mutations (scratch worktree, one at a time, restored by `cp` after each; `python3 -m pytest -q tests/test_pipeline_check.py`, FAILED lines and tail line):
```
== M-a  (who == "person" and bool(WAIVE_BUILD_BY_PERSON.search(waived_line)))
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (person: x "(person, 2026-11-19: ok)")-False]
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (person) x (person, 2026-11-13: ok)-False]
2 failed, 501 passed in 64.72s (0:01:04)
== M-a2 (bare WAIVE_BUILD_BY_PERSON.search(waived_line))
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (I2, 2026-11-13: copied "(person, 2026-11-12: ok)")-False]
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (person: x "(person, 2026-11-19: ok)")-False]
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (person) x (person, 2026-11-13: ok)-False]
3 failed, 500 passed in 64.53s (0:01:04)
== M-b  (PERSON_DATED.search(m.group(2)))
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (I2, 2026-11-13: copied "(person, 2026-11-12: ok)")-False]
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (person: x "(person, 2026-11-19: ok)")-False]
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (person) x (person, 2026-11-13: ok)-False]
3 failed, 500 passed in 67.12s (0:01:07)
== M-c  (WAIVE_BUILD_BY_PERSON = re.compile(r"\(\s*person\s*[,:]"))
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (person: ok)-False]
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (person: x "(person, 2026-11-19: ok)")-False]
FAILED tests/test_pipeline_check.py::test_person_dated_anchor
FAILED tests/test_pipeline_check.py::test_batch_waiver_not_excused_stays_strict[N-b]
FAILED tests/test_pipeline_check.py::test_batch_waiver_not_excused_stays_strict[N-d]
FAILED tests/test_pipeline_check.py::test_batch_waiver_missing_inputs_strict[N-j]
6 failed, 497 passed in 68.34s (0:01:08)
== M-d  (subset check dropped: return bool(m and PERSON_DATED.match(m.group(2))))
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 (person, 2026-11-13: x)-False]
1 failed, 502 passed in 68.18s (0:01:08)
```
M-F2 (in `_read`'s except branch after `_UNREAD[shown] = ...`: for a UnicodeDecodeError, `assert isinstance(err.object, bytes)` then `return err.object.decode("utf-8", "replace").replace("\r\n", "\n").replace("\r", "\n"), None`):
```
== M-F2 new fixture, -k test_batch_waiver_missing_inputs_strict
E       AssertionError: assert [('990', 'no ..., item 093)')] == [('990', 'no line before I2')]
FAILED tests/test_pipeline_check.py::test_batch_waiver_missing_inputs_strict[N-g]
1 failed, 3 passed, 499 deselected in 3.12s
== M-F2 new fixture, whole tests/test_pipeline_check.py (FAILED lines)
FAILED tests/test_pipeline_check.py::test_batch_unreadable_06_is_not_computable
FAILED tests/test_pipeline_check.py::test_batch_unreadable_log_file_makes_every_item_not_computable
FAILED tests/test_pipeline_check.py::test_read_contract
FAILED tests/test_pipeline_check.py::test_unreadable_log_exits_1_alone
FAILED tests/test_pipeline_check.py::test_handoff_bad_01_no_03
FAILED tests/test_pipeline_check.py::test_handoff_bad_03
FAILED tests/test_pipeline_check.py::test_handoff_all_one_bad_03
FAILED tests/test_pipeline_check.py::test_handoff_legacy_bad_03_is_fail
FAILED tests/test_pipeline_check.py::test_handoff_all_bad_01_good_03
FAILED tests/test_pipeline_check.py::test_unreadable_06
FAILED tests/test_pipeline_check.py::test_unreadable_request
FAILED tests/test_pipeline_check.py::test_unreadable_log_consumers_say_not_checked
FAILED tests/test_pipeline_check.py::test_orphan_log_with_unreadable_file
FAILED tests/test_pipeline_check.py::test_unreadable_07
FAILED tests/test_pipeline_check.py::test_unreadable_05_at_suite_check
FAILED tests/test_pipeline_check.py::test_real_data_field_unreadable_request_and_05
FAILED tests/test_pipeline_check.py::test_research_code_unreadable_request
FAILED tests/test_pipeline_check.py::test_unreadable_request_still_clashes
FAILED tests/test_pipeline_check.py::test_inbox_unreadable_daily_report
FAILED tests/test_pipeline_check.py::test_inbox_unreadable_working_template
FAILED tests/test_pipeline_check.py::test_batch_waiver_missing_inputs_strict[N-g]
FAILED tests/test_pipeline_check.py::test_round_content_refusal[06-unreadable]
FAILED tests/test_pipeline_check.py::test_round_unreadable_log_refused
FAILED tests/test_pipeline_check.py::test_unreadable_05_round_headings_not_checked
FAILED tests/test_pipeline_check.py::test_round_build_missing_inputs
FAILED tests/test_pipeline_check.py::test_scratch_dir_unreadable_05_not_checked
26 failed, 477 passed in 67.60s (0:01:07)
== M-F2 old fixture b"\xff" with the old test body (byte-59 assert removed), -k test_batch_waiver_missing_inputs_strict
4 passed, 499 deselected in 3.73s
```
F2 evidence: under M-F2 the old `b"\xff"` N-g passes (a replace-decoded `�` is no waiver), the new N-g fails. With the old fixture but the new byte-59 assert kept, N-g fails on `assert 'not UTF-8 at byte 0' == 'not UTF-8 at byte 59'` (also recorded). The `isinstance(err.object, bytes)` assert never fired.

## Test output (round 2, pasted)
Round 2 fixes 06 r1 item 1 only: the `Scratch dir:` line now names the round 2 mkdtemp dir (`i2-100-r2-jfe6j8r5`), the round 1 `Suite:` line is inside a fence, and every run is redone. No code or test file changed in round 2:
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
0
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
0
$ git diff --stat cc91abb HEAD -- scripts/check_pipeline.py tests/test_pipeline_check.py
(empty)
```
Since cc91abb the branch changed only `tests/test_agent_tools.py` (item 104 I2) outside work/ and logs/, so the count is now base 981 + 4 = 985 passed (104 adds 22).

`python3 scripts/check_pipeline.py` in the main checkout with this 05 (uncommitted), lines for 100:
```
100: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))
I3 FAIL: 100
INCOMPLETE: 100 (05 has no 'Suite:' line (item 082))
```
That run was before the round 2 `Suite:` line was added. The Scratch dir entry is gone.

Full suite at a scratch-only probe commit (2e3f1e0, detached in `<scratch dir>/wt` on top of fcf3cff, never on the branch). It holds this 05 plus a column-0 copy of the round 1 `Suite:` line, so the item 082 check still matches the last committed I2 log line. Run with `python3 -m pytest -q -p no:cacheprovider`:
```
E             100: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))
E             I3 FAIL: 100
E             INCOMPLETE: none
=========================== short test summary info ============================
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 985 passed, 1 skipped in 134.42s (0:02:14)
```
The only failure is `test_repo_pipeline_has_no_skipped_items`, and its only non-none entry is `I3 FAIL: 100`, the item sent back (06 r1 committed). This is expected under item 071 and is not a defect of this build. `INCOMPLETE: none`.

Full suite from the repo root, `python3 -m pytest -q` (main checkout, HEAD 5eacd19; the HEAD worktree the repo test reads still has the round 1 05):
```
E             100: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))
E             I3 FAIL: 100, 104
E             INCOMPLETE: 100 (05 Scratch dir '/tmp/claude-0/-home-claude/8c722f74-340b-5bb8-a4ab-b7e171dc99a9/scratchpad/i2-100-r1b-twin92si' is not the mkdtemp form (item 097))
=========================== short test summary info ============================
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 985 passed, 1 skipped in 130.31s (0:02:10)
```
Here the same single test fails on `I3 FAIL: 100, 104` (both sent back, item 071) and on the round 1 05 Scratch dir entry that this commit removes.

Suite: 1 failed, 985 passed, 1 skipped in 130.31s (0:02:10)

Mutations redone in `<scratch dir>/wt` (detached at fcf3cff). One at a time, `python3 -m pytest -q -p no:cacheprovider tests/test_pipeline_check.py`, each restored with `git checkout HEAD -- scripts/check_pipeline.py` in `wt`. Every run also fails `test_repo_pipeline_has_no_skipped_items` (I3 FAIL 100 / round 1 05 at HEAD, present with no mutation):
```
== M-a
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (person: x "(person, 2026-11-19: ok)")-False]
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (person) x (person, 2026-11-13: ok)-False]
3 failed, 500 passed in 70.95s (0:01:10)
== M-a2
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (I2, 2026-11-13: copied "(person, 2026-11-12: ok)")-False]
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (person: x "(person, 2026-11-19: ok)")-False]
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (person) x (person, 2026-11-13: ok)-False]
4 failed, 499 passed in 66.50s (0:01:06)
== M-b
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (I2, 2026-11-13: copied "(person, 2026-11-12: ok)")-False]
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (person: x "(person, 2026-11-19: ok)")-False]
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (person) x (person, 2026-11-13: ok)-False]
4 failed, 499 passed in 68.73s (0:01:08)
== M-c
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (person: ok)-False]
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 05 06 (person: x "(person, 2026-11-19: ok)")-False]
FAILED tests/test_pipeline_check.py::test_person_dated_anchor - AssertionErro...
FAILED tests/test_pipeline_check.py::test_batch_waiver_not_excused_stays_strict[N-b]
FAILED tests/test_pipeline_check.py::test_batch_waiver_not_excused_stays_strict[N-d]
FAILED tests/test_pipeline_check.py::test_batch_waiver_missing_inputs_strict[N-j]
7 failed, 496 passed in 67.38s (0:01:07)
== M-d
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
FAILED tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three[Waived: 04 (person, 2026-11-13: x)-False]
2 failed, 501 passed in 66.78s (0:01:06)
== M-F2 (decode branch returns err.object replace-decoded after asserting bytes), -k test_batch_waiver_missing_inputs_strict
E       AssertionError: assert [('990', 'no ..., item 093)')] == [('990', 'no line before I2')]
FAILED tests/test_pipeline_check.py::test_batch_waiver_missing_inputs_strict[N-g]
1 failed, 3 passed, 499 deselected in 2.31s
```
The same named tests kill each mutation as in round 1 and in 06 r1. `git status --porcelain` in `wt` was empty after the last restore.

Real-data effect: not required (no TRIGGER file). Pipeline output in `wt` at fcf3cff, first with the base script (`git show c771a21:scripts/check_pipeline.py`, restored after) and then with the head script, `diff cp-base.txt cp-head.txt && echo IDENTICAL`:
```
IDENTICAL
```
Both exit 1 (I3 FAIL and the round 1 05 entry). 023 and 057 read `complete (RESEARCH ONLY ...)` in both.

Missing-data grep (round 2): `grep -rnE "fillna|...|\.get\([^)]*, 0\)" ccbot/ | wc -l` → `38`, the same count as round 1, with no ccbot/ change.

Recurring issues re-checked (round 2):
RI-010: ESCALATED, occurrence in round 1 (non-097 scratch name `r1b`), caught by the item 097 check before merge; fixed in round 2 (mkdtemp prefix `i2-100-r2-`, the round 1 path not on a `Scratch dir:` line).
RI-001: ESCALATED, no new occurrence (IDENTICAL pipeline output, 11-case test).
RI-014: OPEN, no new occurrence (no code change in round 2).
RI-009: GUARDED, holds (probes and the probe commit only in my own scratch worktree, no `git stash`).
RI-012, RI-002: GUARDED, hold (mutations killed, absent rows False).

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat`: scripts/check_pipeline.py, tests/test_pipeline_check.py; neither is in TRIGGER / TRIGGER_DIRS). Pipeline output on the real repo, `python3 scripts/check_pipeline.py` at base (before any edit, exit 0) and with the fix (exit 0), `diff <scratch>/out-base.txt <scratch>/out-fix.txt && echo IDENTICAL`:
```
IDENTICAL
```

## Deviations from plan
1. M-b also kills the existing `(I2 ... copied ...)` case (3 failures, plan named the 2 new cases). Extra kill, not a gap.
2. M-c's line is applied to `WAIVE_BUILD_BY_PERSON` (PERSON_DATED is built from it at import), so it also hits `_person_waived_before_i2`: failures are exactly the plan's list (`(person: ok)`, N-b, N-d, N-j, `test_person_dated_anchor`) plus the F1 row.
3. M-F2 across the whole file fails 26 tests (every unreadable-file test), recorded as asked ("Record any other failures").
4. The 04 Guardrail-tests addition (the `""` and `Waived: 04 05 06` rows, 11 cases, base + 4) is built as written in 04, not 03's 9 cases / base + 2.

## Recurring issues checked
Read `logs/recurring-issues.md` first; checked the output against every open or ESCALATED entry:
RI-001: ESCALATED, no new occurrence. The one count-like rule (RESEARCH ONLY excuse: 2 called, 0 True before and after) is measured by the IDENTICAL output diff and the 11-case test.
RI-010: ESCALATED, no new occurrence. The I2 log line is written with `--log` from the `Suite:` line; committed with `scripts/commit_step.py`.
RI-014: OPEN, no new occurrence. No git read and no new file read; `test_read_census` green; M-F2 was a scratch-only mutation, never committed.
RI-012: GUARDED, holds. `_build_waived` now uses anchored `PERSON_DATED.match`; in-text negatives added; mutations back to `.search` (M-a, M-a2, M-b) are killed.
RI-002: GUARDED, holds. Every absent input gives False or the strict reason (rows `""`, `Waived: 04 05 06`, N-g, N-h).
RI-007: GUARDED, holds. Change only narrows `_build_waived` (never False to True); real output IDENTICAL.
RI-008: GUARDED, holds. `re.match`, not `prefixmatch`; py_compile on 3.11 exit 0.
RI-009: GUARDED, holds. Mutations in my own mkdtemp scratch worktree, no `git stash`, worktree removed.
RI-006: GUARDED, holds. File counts and the Suite line copied from command output.
