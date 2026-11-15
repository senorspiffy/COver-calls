# 06 Verification - 066
Verdict: PASS (round 1; earlier rounds: none)

Verified against committed HEAD d957132 ("Item 066: I2 build") in a scratch detached worktree /tmp/claude-0/i3wt066 (removed afterwards). Item 065's uncommitted files in the main tree (` M ccbot/realtest.py`, later also ` M tests/test_realtest.py`) are 065's and were not used or touched.

## I1 audit (plan vs research)
- 04 follows 03's map step by step (Rule trace covers steps 1-4, every correction, both removed claims, the Missing inputs rows). Option B only; one file; no run-item.md, rule, scripts/, ccbot/ or config/ change, as the map header says.
- One addition, sourced and labelled: "FIT WITH CHANGES" adds the `_run_head` helper and the fixture pin `test_head_run_ignores_uncommitted_item` (T2), because 03 pinned the committed-only filter only with R3's one-off probe. Reason given: I1 step 1a (every filter rule gets a planned suite test). It reuses `_history`/`_item`. The suite target moves from 317 to 318 with the arithmetic shown (316 + 2). Not an unsourced addition.
- Extra research point 2 (keep `REPO/scripts`, so an uncommitted check_pipeline.py edit is still tested) matches 03 step 2 ("keeping `REPO / "scripts"` inside `_run` (unchanged)").
- Line numbers in 04 were a few lines off (05 notes `NO_GIT` at L599); every anchor text was unique, so no effect.

## I2 audit (build vs plan)
`git diff HEAD~1 HEAD -- tests/` read line by line against 04 Files 1-5:
1. `NO_GIT` moved to just before `def _run`, removed from the 053 block. Matches.
2. `_run_head(root, tmp, script, *args)` after `_run`: `wt = tmp / "head"`; `git worktree add --detach -q <wt> HEAD`, `cwd=root`; `assert add.returncode == 0, add.stderr`; `try: return _run(wt, ...)`; `finally: git worktree remove --force`, result not checked. Docstring as planned. Matches.
3. `test_repo_pipeline_has_no_skipped_items`: `@NO_GIT`, `tmp_path`, `_run_head(REPO, tmp_path, ...)`, the 3 asserts unchanged, docstring as planned. Matches.
4. `test_head_run_ignores_uncommitted_item` after `_history`: control (`code == 1 and "INCOMPLETE: 151"`), HEAD run (`INCOMPLETE: none`, `code == 0`), worktree-list assert. Matches. `wt` = `tmp_path/head` is a sibling of the fixture repo `tmp_path/repo`, not inside it.
5. The 3 `_is_code` asserts moved unchanged into `test_is_code_examples`; `test_work_code_pattern` keeps 8 cases and 2 asserts. Matches.
- Only tests/test_pipeline_check.py and work/066/05 in the commit (`git show --stat HEAD`). No deviations, as 05 says.
- Connectivity re-done: `_run_head` has 2 callers (the repo test, T2); `NO_GIT` is used by both plus the 053+ tests (90 collected, no NameError); inputs = HEAD of REPO or fixture repo, outputs = stdout/rc consumed by asserts; every branch ends in a defined result (no git -> skip; add fails -> AssertionError with stderr, re-run below; remove fails -> unasserted, visible in `git worktree list`). No TODOs.
- 05 grep reasons: the missing-data grep is on ccbot/, which this item doesn't touch (`git diff --stat HEAD~1 HEAD -- ccbot/` empty), so 0 new hits holds. No new dataclass field, no new `>`/`<` test.
- Not a BUG item (Type: EFFICIENCY), so no fix/prevention pair is needed. No removed default to put back (RI-002 probe below uses the equivalent mutation). No rule text the person follows changed (001 untouched). No text-matching classifier added (T2's `in out` checks are test asserts, not code that classifies). No simulator/replay (062 n/a).

## Tests re-run (output)
All in /tmp/claude-0/i3wt066 at d957132.
Full suite `python3 -m pytest -q -p no:cacheprovider`:
```
318 passed, 1 skipped in 46.44s
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'
```
Matches 05 and the plan target (316 + 2). The skip is the pre-existing calendar one.
`python3 -m pytest --collect-only -q tests/test_pipeline_check.py`: `90 tests collected` (88 -> 90).
Oldest-Python compile: `PASSED tests/test_safety.py::test_every_py_compiles_on_oldest_python` (python3.11 on PATH; python3.10 is not, so it compiled with 3.11). Not skipped.
Durations: `0.72s call test_repo_pipeline_has_no_skipped_items`, `0.21s call test_head_run_ignores_uncommitted_item` (both < 2 s).

Mutation A (`return _run(root, script, *args)` as the first line of `_run_head`), then restored:
```
E         INCOMPLETE: 151 (no log line for R1)
FAILED tests/test_pipeline_check.py::test_head_run_ignores_uncommitted_item
1 failed, 89 passed in 12.32s
```
Mutation (i) (check_pipeline.py L211 -> `return f.startswith(paths)`), then restored:
```
FAILED tests/test_pipeline_check.py::test_research_code_rules
FAILED tests/test_pipeline_check.py::test_work_code_pattern[work/061/diag_keep.py-True]
FAILED tests/test_pipeline_check.py::test_work_code_pattern[work/160/sub/x.py-True]
FAILED tests/test_pipeline_check.py::test_is_code_examples
FAILED tests/test_pipeline_check.py::test_research_only_work_py_is_research_code
FAILED tests/test_pipeline_check.py::test_py_added_to_completed_item_is_untracked
FAILED tests/test_pipeline_check.py::test_research_only_branch_work_py_is_branch_skipped
FAILED tests/test_pipeline_check.py::test_research_only_branch_nested_py_is_seen
8 failed, 82 passed in 12.15s
```
Same 8 as 05 (was 13 with all 8 pattern cases failing, 064/06). The constant asserts now fail once.
Probe C5 (uncommitted `work/999/request.md` Scope FULL + `01-research.md`, no R1 line, in the scratch worktree; REPO = that tree):
```
== new body
1 passed, 89 deselected in 1.18s
== old body (HEAD~1's test file)
E         INCOMPLETE: 999 (no log line for R1)
1 failed, 87 deselected in 0.64s
```
Probe files and old test file removed afterwards (`git status --short` in the worktree: empty).
Absent case (`_run_head` on an empty non-git dir): `AssertionError: fatal: not a git repository (or any of the parent directories): .git`. Fails loudly, no fallback.
Cleanup: `git worktree list` after all runs shows no pytest tmp entry (only the main tree, 065's own `/tmp/claude-0/065-base` and `065-mut`, and my i3wt066, which I then removed). REPO status: before ` M ccbot/realtest.py`; after, also ` M tests/test_realtest.py`, which is 065's concurrent build (I wrote nothing in REPO except this file, 07 and the log line).

`python3 scripts/check_handoff.py 066`:
```
sources count (unique URLs in 01-research.md): 3
fact-check rows: 34
totals line: 34 rows -> 26 as-is, 6 fixed, 2 removed
PASS
```

## Recurring issues checked (step 0)
Recurring issues checked: RI-001 (ESCALATED: the committed-only filter has a suite pin with a control assert proving the fixture triggers, count 1 not 0; mutation A fails it, re-run above), RI-002 (ESCALATED: no missing input becomes a pass; no git -> skip with reason; non-repo -> AssertionError with git stderr, re-run above; no fallback to REPO), RI-007 (GUARDED: 066 has all step files 01-05 with log lines before this one; check_pipeline shows no SKIPPED/UNTRACKED CHANGE/RESEARCH CODE), RI-009 (GUARDED: all my probes and mutations ran in a scratch worktree, never in REPO; no stash/checkout/reset in REPO; worktree removed), RI-010 (GUARDED: this file was written before its `--log` line, which goes through check_pipeline.py), RI-006 (all counts pasted from commands), RI-008 (oldest-Python compile test passed with python3.11), RI-012 (no text-matching classifier added). RI-003, RI-004, RI-005, RI-011 not applicable (no calendar, worked price example, hand-off numbers beyond those re-measured, or branch diff).

## Pipeline line (step 2)
check_pipeline line: `066: awaiting A1 (FULL)` (after 06, 07 and the I3 `--log` line; exit 0, INCOMPLETE: none, SKIPPED: none, LOG TIME: none, UNTRACKED CHANGE: none, RESEARCH CODE: none. Run between 06 and the log line it read `066: in progress (FULL: next 07)` with `INCOMPLETE: 066 (no log line for I3)`, as expected.)

## Sent back / sent to Audit
Nothing sent back. Sent to Audit: work/066/07-audit-task.md.
