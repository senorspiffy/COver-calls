# 06 Verification - 099
Verdict: PASS (round 1)
Sent back to: none
Scratch dir: /tmp/claude-0/-home-claude/8c722f74-340b-5bb8-a4ab-b7e171dc99a9/scratchpad/i3-099-r1-0lj1w4gu

Made with `python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="i3-099-r1-", dir="/tmp/claude-0/-home-claude/8c722f74-340b-5bb8-a4ab-b7e171dc99a9/scratchpad"))'`. Three detached worktrees inside it: `wt` at d8f8f58 (full suite, untouched), `mut` at d8f8f58 (mutations, check_handoff runs; each probe restored with `git checkout HEAD -- <file>` in `mut`), `base` at 425094f (base script for the `--all` cmp). No `git stash`. All worktrees removed at the end. The main checkout (103's I2 edits in scripts/check_pipeline.py and tests/test_pipeline_check.py) was not touched apart from this file, 07 and the log line.

## I1 audit (plan vs research)
- 04's Rule trace covers 03 map steps 0-8, every Missing inputs row, the removed Windows claim and Self-check S1-S11. Nothing from 03 is dropped without a reason (only the Windows claim, removed in 03 itself).
- The four changes C1-C4 are sourced: C1 simplifies 03's ambiguous `_unread(item, n, detail)` name rule; C2 cites the 092 audit method (logs/audit/2026-11-24-092.md L35-36) and check_handoff's cwd-relative `Path("work")`; C3 cites the pytest monkeypatch doc and the existing in-process import; C4 only keeps existing asserts. Extra research 1-4 cite contextlib docs or traces of check_handoff.py. Extra research 3 (the (a) bad list has 4 lines incl. `1 problem(s)`) is a correction found by trace, and I2's step 1 measurement confirms it (run 1).
- Fit: tests only; no rule the person follows changes (001: none), no RULE_PATHS file changes. No unsourced additions. I1 has no problems.

## I2 audit (build vs plan)
- `git diff 425094f d8f8f58 --stat`: of non-step files only tests/test_pipeline_check.py changed (88+, 20-); the other paths are work/ and logs/ of 099, 100 and 104. `git diff 425094f d8f8f58 -- scripts/ .claude/ | wc -c` -> 0.
- Line by line against 04 Files 1: `_ok3` deleted (`grep -n "_ok3"` no hits in d8f8f58); `_unread(path, detail)` (C1); `_exact3` with Traceback check, `out.splitlines() == lines`, exit code and `err == b""` (applied because 05 step 1 measured b'' on 15 of 15 runs); all 13 existing runs swapped to whole lists that equal 04's lists and 05's measured table; the new single runs `151` and `003` with exit 1 and the 2-line pin; `_no_claim` (fullmatch `no \S+; nothing else to check`, message `A1-3:`) on (b) bad, (d) bad, single 151 and single 003, not on (a); `test_check_all_unreadable_problem_call_site` with `ids=["n1", "n2", "p"]`, `calls == ["003"]`, conditional `sys.path` insert, work/003/03-handoff.md written, docstring naming `main(d.name)`, `l[6:]`, `UNREADABLE_PROBLEM.fullmatch`; the block comment header has the item-099 kill-map paragraph. C4: the old extra asserts in (a), (b), (c), (e) are all still in the diff context; the diff removes no assert other than the `_ok3` -> `_exact3` swap.
- Connectivity re-done: `_unread`, `U8`, `SRC1`, `NO03`, `TABLE_OK` are used in the pinned lists; `NO_CLAIM` in `_no_claim`; `_no_claim` 4 calls; `_LEGACY003` in n1/n2; the new test is collected (15 selected below = 12 base + 3). Every branch ends in a defined result: fake never reached fails `calls == ["003"]`; non-empty stderr fails `_exact3`.
- 05's grep reasons check out: ccbot/ is not touched (no new missing-data hit); the added lines' `->` hits are comments and the literal `totals line: ... 1 rows -> 1 as-is` string.
- Data-hole edges: not applicable (no data window). Absent inputs (no 01, no 03, 03 as a directory) are covered by (a), (d) and the measured runs.
- RI-012 negative text-match test with the pattern inside other text: present, and it is this item's point (n1 `x unreadable (...); y`, n2 `see work/003/03-handoff.md unreadable (...)`), tested at the check_all call site, not only on the constant. Not a FAIL.
- Simulator rule (062): not applicable.
- 05's deviation notes (the sys.path remark about the old test; the audit's `-k` counted 13 vs 12 collected) are wording only; I agree.

## Tests re-run (output)
Full suite, `python3 -m pytest -q` in worktree `wt` at d8f8f58:
```
993 passed, 1 skipped in 115.13s (0:01:55)
```
Same count as 05 (`993 passed, 1 skipped in 114.06s`). `tests/test_safety.py` (incl. `test_every_py_compiles_on_oldest_python`) ran, not skipped: `9 passed in 1.03s`; python3.11 is on PATH (python3.10 is not). `python3.11 -m py_compile tests/test_pipeline_check.py` -> exit 0.

Targeted, `mut` at d8f8f58: `python3 -m pytest -q tests/test_pipeline_check.py -k "handoff or unreadable_problem or check_all"`:
```
15 passed, 491 deselected in 6.98s
```

Mutations (my own script `<scratch>/tools/mut.py`, one at a time on scripts/check_handoff.py in `mut`, exact-string replace asserted to hit once, restored with `git checkout HEAD -- scripts/check_handoff.py`, `-k "handoff or unreadable_problem or check_all"`):
```
A1-3 no early return | 4 failed, 11 passed, 491 deselected in 1.33s | test_handoff_bad_03, test_handoff_all_one_bad_03, test_handoff_03_is_directory, test_handoff_legacy_bad_03_is_fail
A1-2 .search | 2 failed, 13 passed, 491 deselected in 1.39s | test_check_all_unreadable_problem_call_site[n1], test_check_all_unreadable_problem_call_site[n2]
M-f no LEGACY guard | 2 failed, 13 passed, 491 deselected in 1.17s | test_handoff_legacy_bad_03_is_fail, test_check_all_unreadable_problem_call_site[p]
A1-1 01 problem not appended | 2 failed, 13 passed, 491 deselected in 1.23s | test_handoff_bad_01_no_03, test_handoff_all_bad_01_good_03
restored | 15 passed, 491 deselected in 1.14s
git status: ''
```
These match 05's step 6 table test for test. M-a/M-b were not re-run by me (05 shows them, and the 092 tests they kill are unchanged apart from stronger pins).

Guardrail would have caught the original error (BUG): the same two mutations with the base test file (`git checkout 425094f -- tests/test_pipeline_check.py` in `mut`, then restored to HEAD):
```
A1-3 no early return | 12 passed, 491 deselected in 1.61s |
A1-2 .search | 12 passed, 491 deselected in 0.97s |
```
So both survive at base (as in audit 092 L44-45) and both are killed at head: fix (whole pins) and guardrail (call-site negative test + absent-claim assert) are both in place. Note: my base-file probe pipe was cut after 2 lines, leaving the M-f edit in `mut`; I restored it with `git checkout HEAD -- scripts/check_handoff.py` and `git status --short` was empty before any later run.

Step 7, shipped output unchanged (C2): cwd = `mut` root (d8f8f58), `python3 <scratch>/base/scripts/check_handoff.py --all` -> exit 0; `python3 scripts/check_handoff.py --all` -> exit 0; `cmp` -> identical, 105 lines, last line `no new failures`.

`python3 scripts/check_handoff.py 099` (in `mut`, d8f8f58):
```
sources count (unique URLs in 01-research.md): 6
fact-check rows: 50
totals line: 50 rows -> 45 as-is, 4 fixed, 1 removed
PASS
```
Same as the output pasted in 03.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat 425094f d8f8f58`, non-step files: tests/test_pipeline_check.py only)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-010, RI-014, RI-012, RI-002, RI-008, RI-009
- RI-001 (ESCALATED): every selector has a measured count: 15 of 15 runs (05 table), absent-claim selector 4 of 4 single runs (my A1-3 kills the 4 named tests), fake separation 2 of 3 (my A1-2 run: n1, n2 fail, p passes). The rule text has no number that differs from these.
- RI-010 (ESCALATED): 05 step 1 and step 6 are pasted script output and I re-ran step 6; my log line is written with `--log` after this file, and committed with commit_step.py.
- RI-014 (OPEN): no git read added; every fixture and the call-site tmp tree have a 03, so `_branch_with_handoff` is not called. Unchanged.
- RI-012 (GUARDED, target): call-site in-text negatives n1/n2 present and they kill A1-2. Holds; closes the 2026-11-24 "check_handoff tests check presence only" near miss.
- RI-002: no default added; the stderr pin is applied only because it was measured empty on 15 of 15 runs. RI-002 removed-default probe: not applicable (no default was removed in this item).
- RI-008: python3.11 compile of the changed file exit 0; the oldest-python test ran.
- RI-009: mutations only in my scratch worktrees; no stash.

## Pipeline line (step 2)
check_pipeline line: `099: awaiting A1 (FULL)` (run in the main checkout after this file and the `--log` line; exit 0, `I3 FAIL: none`, `INCOMPLETE: none`, `SKIPPED: none`, `STASH: none`)

## Sent back / sent to Audit
PASS, round 1. Sent to Audit: work/099/07-audit-task.md.
