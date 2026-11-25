# 05 Build report - 099
Base commit: 425094f (branch daily-fixes/2026-11-24-b; 01-04 at 253d556, builds of 101, 100, 104 already on the branch). During the build 05460b7 (100 A1) and aaf145c (104 I3) landed: work/ and logs/ only. `git diff 425094f aaf145c --stat -- tests/test_pipeline_check.py` is empty, and `git status --short` showed only ` M tests/test_pipeline_check.py` (this build), so no other item's uncommitted edit is in the shared file (03 step 0).
Scratch dir: /tmp/claude-0/-home-claude/8c722f74-340b-5bb8-a4ab-b7e171dc99a9/scratchpad/i2-099-r1-ua8vrwe2

## Changes made (file: what changed)
- tests/test_pipeline_check.py, 092 block only (as planned):
  - Block comment header: one item-099 paragraph (whole-output pins and the A1-3/A1-2 kill map).
  - `_ok3` deleted. Added `_unread(path, detail)` (C1), the shared constants `U8`, `SRC1`, `NO03`, `TABLE_OK`, `NO_CLAIM`, `_exact3(code, out, err, want_code, lines)` (no Traceback, `out.splitlines() == lines`, exit code, `err == b""`; the stderr pin is used because step 1 measured b"" on all 15 runs), and `_no_claim(out)` (the absent-claim fullmatch assert, with an `A1-3:` message).
  - All 13 existing runs in (a)-(f) now use `_exact3` with the measured whole list. The old extra asserts are kept (C4).
  - New single runs: `_run3h(bad, "151")` in test_handoff_all_one_bad_03 and `_run3h(bad, "003")` in test_handoff_legacy_bad_03_is_fail, both pinned to the FAIL line plus `1 problem(s)`, exit 1.
  - `_no_claim` on (b) bad, (d) bad, single 151 and single 003 ((a) left out, research 3).
  - New `test_check_all_unreadable_problem_call_site`, parametrized with `ids=["n1", "n2", "p"]` (C3). It uses a fake `main` set by monkeypatch that records its argument (`calls == ["003"]`, `len(calls) == 1`), writes `work/003/03-handoff.md` so the git lookup is skipped, adds `sys.path` only if it is missing, and pins the whole capsys stdout and the return code. The docstring names `main(d.name)`, `l[6:]` and `UNREADABLE_PROBLEM.fullmatch` by text.
- Deviation note (wording only): 04 C3 says `test_unreadable_problem_fullmatch_only` inserts into sys.path only if the path is missing. It actually inserts every time. The new test uses the conditional form that 04 asks for, and the old test is not changed.

File counts (commands, item 012):
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` -> 0 new
- `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` -> 1 changed
- `git diff --stat`: ` tests/test_pipeline_check.py | 108 +++++++++++++++++++++++++++++++++++--------` / ` 1 file changed, 88 insertions(+), 20 deletions(-)`
- `grep -n "_ok3" tests/test_pipeline_check.py` -> no output (exit 1).

## Connectivity check
- [x] every new function/rule is used: `_unread` is used in the lists of (a)-(f). `_exact3` is used for all 15 subprocess runs. `_no_claim` is used for 4 runs. `U8`/`SRC1`/`NO03`/`TABLE_OK` are used in the lists, `NO_CLAIM` in `_no_claim`, and `_LEGACY003` in the n1/n2 cases. The new test is collected (3 ids, see the run below).
- [x] every input has a source, every output has a consumer: the inputs are fixture trees in tmp_path and the fake main. The outputs are the pytest asserts. The mutation results go to this report and to I3/A1.
- [x] every branch ends in a defined result: a fake that is never reached fails `calls == ["003"]`, and the p case fails as well. A stderr that is not empty fails `_exact3`. A missing base would be reported as `not checked (no base)`, but the base is 425094f, so it does not apply.
- [x] no leftover TODOs or unused files: none added. measure.py, edit.py, mut.py and the worktree are only in the scratch dir.

Missing-data policy: `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/ | wc -l` -> 38, all already there. ccbot/ is not touched, so there is no new or changed hit. The same pattern plus `: float = ` and `[<>]` over the added diff lines finds only `->` in comments/docstrings and the literal `totals line: ... 1 rows -> 1 as-is` string. There is no comparison and no dataclass. stderr is not assumed empty: it is pinned only because it was measured empty on 15 of 15 runs.

Feasibility numbers (04 Guardrail tests, measured):
- Run count: 15 of 15 runs measured (table below). Every run equals 04/03's expected list character for character, so there is no EXPECTED OUTPUT MISMATCH.
- Absent-claim selector: under A1-3 the `no ...; nothing else to check` line appears in 4 of 4 single-item unreadable-03 runs (failure messages below: work/150 twice, work/151, work/003). The 3 `--all` bad runs still pass under A1-3 (shown by (c)/(e) failing only at the single runs, see A1-3 detail).
- `.search` vs `.fullmatch`: 2 of 3 fake cases separate them (n1, n2 fail under A1-2, p passes).
- `stderr pin: applied (b'' measured on 15 of 15 runs)`.

## Test output (pasted, not summarized)
Step 1 gate: the 15 runs at HEAD 425094f, before any edit. The trees are built exactly as in tests L3987-4074 (same `_h03`, BAD), with `python3 <scratch>/measure.py <scratch>/m`:
```
--- run 1: a bad 150 | exit 1 | stderr b''
sources count (unique URLs in 01-research.md): not computed (work/150/01-research.md unreadable (not UTF-8 at byte 0))
no work/150/03-handoff.md; nothing else to check
FAIL: work/150/01-research.md unreadable (not UTF-8 at byte 0)
1 problem(s)
--- run 2: a clean 150 | exit 0 | stderr b''
sources count (unique URLs in 01-research.md): 1
no work/150/03-handoff.md; nothing else to check
--- run 3: b bad 150 | exit 1 | stderr b''
sources count (unique URLs in 01-research.md): 1
FAIL: work/150/03-handoff.md unreadable (not UTF-8 at byte 0)
1 problem(s)
--- run 4: b clean 150 | exit 0 | stderr b''
sources count (unique URLs in 01-research.md): 1
fact-check rows: 1
totals line: 1 rows -> 1 as-is, 0 fixed, 0 removed
PASS
--- run 5: c bad --all | exit 1 | stderr b''
150: PASS
151: FAIL: work/151/03-handoff.md unreadable (not UTF-8 at byte 0)
152: PASS
FAIL on 151
--- run 6: c clean --all | exit 0 | stderr b''
150: PASS
151: PASS
152: PASS
no new failures
--- run 7: c clean 150 | exit 0 | stderr b''
fact-check rows: 1
totals line: 1 rows -> 1 as-is, 0 fixed, 0 removed
PASS
--- run 8: c bad 151 (new) | exit 1 | stderr b''
FAIL: work/151/03-handoff.md unreadable (not UTF-8 at byte 0)
1 problem(s)
--- run 9: d bad 150 | exit 1 | stderr b''
FAIL: work/150/03-handoff.md unreadable (IsADirectoryError)
1 problem(s)
--- run 10: d clean 150 | exit 0 | stderr b''
fact-check rows: 1
totals line: 1 rows -> 1 as-is, 0 fixed, 0 removed
PASS
--- run 11: e bad --all | exit 1 | stderr b''
003: FAIL: work/003/03-handoff.md unreadable (not UTF-8 at byte 0)
FAIL on 003
--- run 12: e bad 003 (new) | exit 1 | stderr b''
FAIL: work/003/03-handoff.md unreadable (not UTF-8 at byte 0)
1 problem(s)
--- run 13: e clean --all | exit 0 | stderr b''
003: LEGACY (written 2026-10-30, before the Totals/Self-check template (commit 77273f0); 2 known problem(s))
no new failures
--- run 14: f bad --all | exit 1 | stderr b''
151: FAIL: work/151/01-research.md unreadable (not UTF-8 at byte 0)
FAIL on 151
--- run 15: f clean --all | exit 0 | stderr b''
151: PASS
no new failures
```

Targeted run on the build tree: `python3 -m pytest -q tests/test_pipeline_check.py -k "handoff or unreadable_problem or check_all"`:
```
...............                                                          [100%]
15 passed, 491 deselected in 1.60s
```
`python3.11 -m py_compile tests/test_pipeline_check.py` -> exit 0 (RI-008).

Step 6 mutations. Scratch worktree `<scratch>/wt` (`git worktree add --detach` at 425094f, build test file copied in). One mutation at a time on scripts/check_handoff.py, restored with `git checkout HEAD -- scripts/check_handoff.py` in the worktree, `python3 <scratch>/mut.py <scratch>/wt`, `-k "handoff or unreadable_problem or check_all"`:
```
M-a strict 01 | 3 failed, 12 passed, 491 deselected in 2.01s | failed: test_handoff_all_bad_01_good_03, test_handoff_bad_01_no_03, test_handoff_read_census
M-b strict 03 | 5 failed, 10 passed, 491 deselected in 1.49s | failed: test_handoff_03_is_directory, test_handoff_all_one_bad_03, test_handoff_bad_03, test_handoff_legacy_bad_03_is_fail, test_handoff_read_census
M-f no LEGACY guard | 2 failed, 13 passed, 491 deselected in 1.22s | failed: test_check_all_unreadable_problem_call_site[p], test_handoff_legacy_bad_03_is_fail
A1-1 01 problem not appended | 2 failed, 13 passed, 491 deselected in 1.30s | failed: test_handoff_all_bad_01_good_03, test_handoff_bad_01_no_03
A1-2 check_all .search | 2 failed, 13 passed, 491 deselected in 1.30s | failed: test_check_all_unreadable_problem_call_site[n1], test_check_all_unreadable_problem_call_site[n2]
A1-3 why03 no early return | 4 failed, 11 passed, 491 deselected in 1.43s | failed: test_handoff_03_is_directory, test_handoff_all_one_bad_03, test_handoff_bad_03, test_handoff_legacy_bad_03_is_fail
restored | 15 passed, 491 deselected in 1.09s | failed: none
diff after restore: clean
```
Mutation forms: M-a / M-b replace `cp._read(x, missing_ok=True)` with `(x.read_text(encoding="utf-8") if x.exists() else None), None` (as in 092/05). M-f changes the LEGACY test to `elif d.name in LEGACY:`. A1-1 drops `problems.append(p)` after the not-computed sources line. A1-2 changes `UNREADABLE_PROBLEM.fullmatch(p)` to `.search(p)`. A1-3 deletes the `return _report(problems)` under `if why03:`.
Each mutant fails every test the plan names. M-a, M-b and A1-1 fail the same tests as audit L40-43. M-f also fails `[p]`: without the guard, LEGACY 003 shows as LEGACY. That is an extra kill, and nothing was weakened.
A1-3 detail (`--tb=line`, same worktree): every failure is at the `_exact3` lines assert (L4004). The extra line printed in each case is the false claim. In (c) and (e) it comes from the new single runs, because the `--all` runs come before them and pass:
```
.../wt/tests/test_pipeline_check.py:4004: AssertionError: sources count (unique URLs in 01-research.md): 1
.../wt/tests/test_pipeline_check.py:4004: AssertionError: no work/151/03-handoff.md; nothing else to check
.../wt/tests/test_pipeline_check.py:4004: AssertionError: no work/150/03-handoff.md; nothing else to check
.../wt/tests/test_pipeline_check.py:4004: AssertionError: no work/003/03-handoff.md; nothing else to check
```
(The first line is (b): the assert message shows the start of `out`, whose second line is the false claim.)

Kill map (03 step 8 wording): A1-3 → (b), (d), single 151 in (c), single 003 in (e). A1-2 → the call-site test n1/n2 only. The `--all` pins of (c), (e) kill neither mutant.

Step 7, shipped output unchanged:
- `git diff 425094f -- scripts/ .claude/ | wc -c` -> 0 (empty).
- `--all` cmp (C2), with one cwd (repo root) and two script copies: `python3 <scratch>/wt/scripts/check_handoff.py --all` (base 425094f) -> exit 0, and `python3 scripts/check_handoff.py --all` (head) -> exit 0. `cmp base.out head.out` -> `cmp: identical`, 105 lines, last line `no new failures`.

Full suite, first run (repo root, `python3 -m pytest -q`), at HEAD aaf145c plus this edit. It ran while 104 was still in I3 FAIL r1 (item 071 rule):
```
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 992 passed, 1 skipped in 113.08s (0:01:53)
```
That failure is expected and is not a defect of this build. Once 104's I3 PASS (aaf145c) was committed, `python3 scripts/check_pipeline.py` exited 0, and `pytest -q tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items` gave `1 passed in 2.87s`. Second full run, same tree:
```
993 passed, 1 skipped in 114.06s (0:01:54)
```
Suite: 993 passed, 1 skipped in 114.06s (0:01:54)

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat`: tests/test_pipeline_check.py only)

## Deviations from plan
- None in code. Two wording notes: (1) the 04 C3 remark about the sys.path insert in `test_unreadable_problem_fullmatch_only` (see Changes). (2) The audit's "13 passed" used a different `-k`, which also selected `r1_log_refuses`. With 04's `-k`, base 425094f collects `12/503 tests collected (491 deselected)` (`--collect-only` in the scratch worktree, using the base test file). Adding the 3 call-site cases gives the 15 above. This is information only.

Recurring issues checked (item 013):
- RI-001 (ESCALATED): no selecting rule without a count. Run count 15 of 15, absent-claim selector 4 of 4, fake separation 2 of 3, all measured above.
- RI-010 (ESCALATED): the I2 log line is written with `check_pipeline.py --log` right after this file and committed with commit_step.py. Step 1 and step 6 are pasted script output.
- RI-014 (OPEN): no git read added. Every fixture folder and the call-site tmp tree have a 03, so `_branch_with_handoff` is never called.
- GUARDED, also checked: RI-002 (stderr pinned only after it was measured; no default), RI-006 (counts from commands and pytest), RI-008 (py_compile 3.11), RI-009 (mutations only in the scratch worktree, no stash, restored by `git checkout HEAD --` there), RI-012 (target), RI-013 (whole-output pins).
RI-012: GUARDED, unchanged; 099 closes the "check_handoff tests check presence only" near miss: call-site test n1/n2 fail under A1-2 (`.search`), whole pins fail under A1-3.
RI-014: OPEN, unchanged; 099 adds no git read.
