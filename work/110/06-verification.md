# 06 Verification - 110
Verdict: PASS (round 1)
Sent back to: none
Scratch dir: /tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i3-110-r1-20wfjrhp

Verified at bc96b01 (I2's build commit) in my own worktrees `wt` (tests, check_handoff, constants) and `mut` (mutations), both `git worktree add --detach` inside the scratch dir above. Every pytest run used `PYTHONDONTWRITEBYTECODE=1`, a fresh `PYTHONPYCACHEPREFIX` dir in the scratch dir and `-p no:cacheprovider`. No `git stash`; mutants were restored with `git checkout HEAD -- <file>` inside `mut`, which was then removed (`git worktree remove`). Nothing was run in the main checkout except `check_pipeline.py` (read-only) and the `--log`/commit helpers.

## I1 audit (plan vs research)
- 04 follows 03's Decision ((a) NO-GO, (b) NO-GO, text-only step 3) and every map row: rule-trace rows cover map steps 1-3; step 4 (A1 watch) and the 02 typo correction are DROPPED with reasons that match 03 (map step 4 is "watch only"; the typo is recorded in 03 L12).
- The three FIT WITH CHANGES changes are sourced or are test tightening only: change 1 ("-k" -> "deselected runs (-k/-m/--deselect)") is backed by Extra research 1 (pytest docs on `--deselect` and `-m`), and makes the comment more exact without changing a measured fact (R1's script matched any `N deselected` part, 03 L9); change 2 adds a positive assert so (ii) is pinned on both sides; change 3 fixes placement. No unsourced addition.
- Paragraph (i)'s numbers equal 03's Measured count (03 L5-10, Self-check L118): 4 in 58 files, 0 at >=092, 34 files, 0 maxes, 0 LOG BATCH changes, 59 checked, 4404a28.
- Extra research 3 (copy filter `kept06` can raise Σ when an unread 05 run is not filtered) agrees with 03's fix of 01 F10.

## I2 audit (build vs plan)
`git diff bc96b01^ bc96b01 --stat`: logs/implementation/2026-11-25.md, scripts/check_pipeline.py (15 +++++--), tests/test_pipeline_check.py (14 +), work/110/05-build-report.md. No templates/, ccbot/ or config/ file.
- Files 1 (i): checked by script against the 04 text, whitespace-joined: `(i) verbatim: True`; placed after `See work/103/03-handoff.md before proposing it.` and before `RULES BRANCH an open branch`: True.
- Files 1 (ii): `(w) runs pasted outside the two sections are not read (can lower Σ, or raise it when 06 copies such a run, which the copy filter then keeps; item 110);` present whitespace-joined: True. The rewrap of the two previous lines changed no word.
- Files 1 (iii): the diff hunk `@@ -465 +471,2 @@` replaces exactly the second comment line with the two 04 lines; `# Item 076: ...` unchanged.
- Files 2: the new test is the 04 text exactly, directly after `test_check_pipeline_docstring_records_103_no_go`.
- Text-only guard (04 T&C 4): first `import` is at L421; hunks are `@@ -194,3 +194,3 @@`, `@@ -222,0 +223,6 @@` (inside the docstring) and `@@ -465 +471,2 @@` (every +/- line starts with `#`). `SUMMARY_LINE.pattern` and `_STATS` printed from the file at bc96b01^ and at bc96b01 (`python3 -I` import of each): `cmp` -> `consts-identical`.
- `only lowers` / old comment text: Grep over tracked `.py` outside work/ finds them only inside the new test's negatives and docstring.
- Deviation noted by I2 (line width 111 vs "about 105"): lines 223-228 measure 107, 107, 106, 111, 103, 93 columns; the file already has longer lines and no test checks width. Accepted.
- Connectivity: no function, constant or regex added; the new test is collected (`-k records_110_no_go`: 1 passed) and reads the docstring, the source file (utf-8) and work/110/03-handoff.md. Grep reasons in 05 checked: the 38 ccbot/ missing-data hits are pre-existing (ccbot/ untouched), 0 in the added lines.
- No data-hole check, no text-matching classifier (the test uses literal `in`/`not in` with two negatives, each shown to kill alone below), no simulator/replay, no person-followed rule (001) changed: those step-3 checks are n/a.

## Tests re-run (output)
check_handoff (`python3 scripts/check_handoff.py 110` in `wt`):
```
sources count (unique URLs in 01-research.md): 1
fact-check rows: 50
totals line: 50 rows -> 40 as-is, 10 fixed, 0 removed
PASS
exit 0
```
Full suite in `wt` at bc96b01 (`PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<scratch>/pyc python3 -m pytest -q -p no:cacheprovider`), last lines:
```
........................................................................ [ 99%]
.......                                                                  [100%]
1014 passed, 1 skipped in 215.89s (0:03:35)
```
Same as 05 (`1014 passed, 1 skipped`), base 1013 + 1.

Oldest Python (RI-008): python3.10 is not on PATH; python3.11 (/usr/bin/python3.11) is. `tests/test_safety.py -k oldest` -> `1 passed, 8 deselected in 0.19s` (ran with python3.11, did not skip). `python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py` -> `python3.11 ok`.

04 T&C 5/6 (`-k "records_110_no_go or records_103_no_go or test_i2_summary_line_refused or test_i2_summary_line_accepted"`):
```
36 passed, 485 deselected in 7.49s
```
Mutations in `mut` (`python3 -m pytest -q -p no:cacheprovider tests/test_pipeline_check.py -k records_110_no_go`, each restored with `git checkout HEAD -- scripts/check_pipeline.py work/110/03-handoff.md`):
```
== unmutated
1 passed, 520 deselected in 0.73s
== M0 pre-edit file (bc96b01^ check_pipeline.py)
E       assert 'Item 110 (gap w, RI-010)' in "Check that every work item's step files ..."
1 failed, 520 deselected in 0.83s
== M1 paragraph (i) removed   (grep -c 'Item 110 (gap w' -> 0)
E       assert 'Item 110 (gap w, RI-010)' in "..."
1 failed, 520 deselected in 1.03s
== M2 old (only lowers Σ) restored
E       assert 'or raise it when 06 copies such a run' in "..."
1 failed, 520 deselected in 0.83s
== M2b new (ii) kept, " (only lowers Σ)" appended after it
1 failed, 520 deselected in 1.18s
== M3 (ii) parenthetical deleted
E       assert 'or raise it when 06 copies such a run' in "..."
1 failed, 520 deselected in 0.84s
== M4 old comment restored
E       assert 'measured to change nothing (item 110)' in '#!/usr/bin/env python3 ...'
1 failed, 520 deselected in 0.89s
== M4b old comment line added back next to new
E       assert '"deselected...un has none.' not in '#!/usr/bin/...argv[1:]))\n'
1 failed, 520 deselected in 0.86s
== M5 03 deleted
E       assert ('work/110/03-handoff.md' in "..." and False)
1 failed, 520 deselected in 0.92s
== restored
1 passed, 520 deselected in 0.71s
```
All 7 mutants (plus the pre-edit file) killed; `git status --porcelain` in `mut` empty after restore.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat bc96b01^ bc96b01`: logs/implementation/2026-11-25.md, scripts/check_pipeline.py, tests/test_pipeline_check.py, work/110/05-build-report.md; no ccbot/realtest.py or TRIGGER/TRIGGER_DIRS file)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001 (ESCALATED: no filter or window is built; every number in paragraph (i) equals 03's dated measurement at 4404a28 and is stated as measured; the test pins `0 per-file maxes` and the 03 pointer), RI-010 (GUARDED, this item is its near miss "`## Round N (...)` wrapper / `deselected` -> 110": closed as two documented no-gos pinned by a test that M0-M5 kill; my log line is written with `--log` right after this file), RI-014 (OPEN: the new test makes no git call; my only git use is diff/show on bc96b01, depth-independent). Also GUARDED: RI-002 (nothing defaulted; missing 03 fails the test, M5), RI-004/RI-005 (each asserted string is in the built text and fails on the pre-edit file, M0), RI-006 (counts pasted as printed), RI-007 (no other item's files edited), RI-008 (oldest-python test ran with 3.11; py_compile ok), RI-009 (probes only in my scratch worktrees, no stash, `mut` removed), RI-012 (literal checks; both negatives kill alone, M2b and M4b). RI-003, RI-011, RI-013 n/a.

## Pipeline line (step 2)
check_pipeline line: `110: awaiting A1 (FULL)`

## Sent back / sent to Audit
Sent to Audit (07-audit-task.md).
