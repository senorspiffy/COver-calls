# 06 Verification - 092
Verdict: PASS (round 1)
Sent back to: none

I3 read the branch copies of .claude/agents/i3-verifier.md and .claude/commands/run-item.md, logs/recurring-issues.md (first), work/092/request.md and 01-05, and `git diff 138e0ce c098a17` (scripts/check_handoff.py, scripts/check_pipeline.py, tests/test_pipeline_check.py). Head c098a17 on daily-fixes/2026-11-24 (open PR #36). `git rev-parse --is-shallow-repository`: false. `RULES BRANCH: none`. Scratch dir (mkdtemp, item 091): /tmp/claude-0/-home-claude/17dd566b-e13e-58fe-b556-13d450b5acde/scratchpad/I3-092-r1-__r3i3lc, with two detached worktrees of c098a17 (`wt` for the suite, `mut` for mutations). No git stash was used; the repo checkout was not edited except for this file, 07 and the log line.

## I1 audit (plan vs research)
- Every 03 map step 1-8 has a plan line (04 Rule trace), and the 8 fact-check fixes are carried: `cp._UNREAD[cp._shown(path)]` indexed with no `.get`, `_read`'s return unchanged (FOR 1); pin on `log_fields_ok`, not LOG_FORMAT (FOR 2); fullmatch constant `UNREADABLE_PROBLEM` plus a negative test, never a substring (FOR 2, RI-012); new `_run3h`, `_run3` unchanged (FOR 3); M-d killed by (b)-(e) too (01 F27); M-e dropped with a reason (check_pipeline's, covered by 089's test_read_contract); Q5/AGAINST 2 as known gap 2.
- I1's three additions are sourced and do not change R3's design: (1) guarded `sys.path` insert (Extra research 4, from check_handoff.py L94); (2) fixture (f), bad 01 next to a good 03 under `--all` (Extra research 3, from L114-125); (3) absent-01 assert in (c) (03 Missing inputs table had no pin). M-g is a mutation for the new `_report` helper. The newline and sys.modules claims cite docs.python.org (functions.html#open, reference/import.html 5.3.1).
- No unsourced addition found.

## I2 audit (build vs plan)
Line by line against 04 "Files to create/change":
- check_handoff.py `_pipeline()`: inserts the scripts dir only if absent, `import check_pipeline`, returns it. `grep -c "from check_pipeline import" scripts/check_handoff.py` → 0. Matches.
- `UNREADABLE_PROBLEM`: exactly `\S+ unreadable \((?:not UTF-8 at byte \d+|[A-Z]\w*Error)\)`. Matches.
- `main`: `cp = _pipeline()` after the folder check; 01 via `cp._read(research, missing_ok=True)`, why01 → not-computed line + problem, `unique_urls` only on non-None text; 03 via `cp._read(handoff, missing_ok=True)`, why03 → problem + `return _report(problems)` before `section()`; absent 03 → `no <path>; nothing else to check`, `_report` if problems else 0; readable → unchanged, `_report` at the end. Matches (`_report` is the plan's named helper).
- `_branch_with_handoff`: `cp = _pipeline(); found = cp.open_branches()`. Matches.
- `check_all`: `elif d.name in LEGACY and not any(UNREADABLE_PROBLEM.fullmatch(p) for p in problems):`. Matches.
- Docstring names the not-computed line, `FAIL: <path> unreadable (<detail>)`, exit 1, the claim worded as planned ("No traceback on an unreadable 01 or 03; work/ listing errors under --all may still raise"), never LEGACY, the check_pipeline import dependency. Matches.
- check_pipeline.py: docstring L360 only, gap text replaced as planned (01 F17, 01 F22). `grep -rl "still reads its files strictly" scripts/` → no file. No code change.
- tests: `_run3h`, `_h03`, fixtures (a)-(f) each with a clean twin, `test_unreadable_problem_fullmatch_only`, `test_handoff_read_census` (walker plus positive control `{"main": 2}`), `test_r1_log_refuses_not_computed`. The two deviations in 05 (`_ok3` helper; positive control stricter than planned) are test-only and tighten, not loosen, the plan.
- Connectivity re-done: `_pipeline` is called from `main` and `_branch_with_handoff`; `_report` from 3 exits of `main`; `UNREADABLE_PROBLEM` from `check_all` and its test; `_run3h`/`_h03`/`_ok3` from the new tests. Inputs: 01/03 from work/<ID>/ through `cp._read`; detail from `cp._UNREAD`, which `_read` writes before returning a why. Outputs: `FAIL:` lines feed `check_all`'s problems list (L162) and the orchestrator; the not-computed sources value is refused by `--log R1` (`log_fields_ok` False, pinned). No dead code, no TODO.
- Grep reasons in 05 checked: the same pattern over `git diff -U0 138e0ce c098a17 -- scripts tests` gives the same 4 added-line hits (two docstring lines, the `_report` docstring, `return 1 if problems else 0`), plus the removed old return; none is a defaulted value. `git diff 138e0ce c098a17 -- ccbot | wc -l` → 0.
- Readable files unchanged: I3 ran base (138e0ce check_handoff.py + check_pipeline.py in a scratch scripts dir) and head over the real tree. `--all` outputs byte-identical (`cmp` → IDENTICAL, 99 lines, both exit 0); single-item output plus exit code for every work/ folder: `items 98 differ 0`.

BUG checks (step 3):
- Fix in place: a b"\xff\xfe" 01 with no 03 in a scratch work/150. Base (138e0ce): `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte`, exit 1 (traceback). Head: `sources count (unique URLs in 01-research.md): not computed (work/150/01-research.md unreadable (not UTF-8 at byte 0))`, `no work/150/03-handoff.md; nothing else to check`, `FAIL: work/150/01-research.md unreadable (not UTF-8 at byte 0)`, `1 problem(s)`, exit 1, no traceback.
- Guardrail would have caught the original error: the new tests run against the base check_handoff.py (BASE row below) give 8 failed, including the census (2 raw reads) and every bad-byte fixture. M-a and M-b (each strict read restored on its own) fail the census plus the matching fixtures.
- RI-002 mutation: no default was removed in this item; the RI-002 shape here is "a number from an unread file". Restoring the strict 01 read (M-a) fails 3 tests; M-c (no-03 branch back to `return 0`, which would hide the unreadable 01) fails (a).
- RI-001: the only selecting rule is the LEGACY exception. Re-run: `python3 scripts/check_handoff.py --all` on the head tree → 7 `: LEGACY (` lines (= 7 IDs 002-008 the rule text cites), 0 `unreadable`, 0 `: FAIL`, `no new failures`, exit 0. Fixture (e): 1 of 1 FAIL, twin 1 of 1 LEGACY (pass).
- RI-012 negative test: `test_unreadable_problem_fullmatch_only` asserts None for `x unreadable (not UTF-8 at byte 0); y` (pattern inside other text) and for a `no Totals line (...)` problem. Present and passing.
- Data-hole edges: no data window in this item (n/a). Rule the person follows (001): none changed. Simulator/replay (item 062): none.

## Tests re-run (output)
Full suite in worktree `wt` (c098a17), `python3 -m pytest -q`, last lines as printed:
```
........................................................................ [ 96%]
..............................                                           [100%]
821 passed, 1 skipped in 148.51s (0:02:28)
```
Same count as 05 (821 passed, 1 skipped).

Oldest-Python compile: `tests/test_safety.py::test_every_py_compiles_on_oldest_python` → `1 passed in 0.18s` (ran with /usr/bin/python3.11; python3.10 is not on PATH). `python3.11 -m py_compile scripts/check_handoff.py scripts/check_pipeline.py tests/test_pipeline_check.py` → exit 0.

Mutations (scratch worktree `mut`, one at a time, file restored after each; `pytest -q tests/test_pipeline_check.py -k "handoff or unreadable_problem or r1_log_refuses or read_census"`; my -k also selects test_read_census, so passed counts are 1 higher than 05's):
```
M-a: 3 failed, 10 passed, 377 deselected in 2.10s | failed: test_handoff_all_bad_01_good_03, test_handoff_bad_01_no_03, test_handoff_read_census
M-b: 5 failed, 8 passed, 377 deselected in 7.98s | failed: test_handoff_03_is_directory, test_handoff_all_one_bad_03, test_handoff_bad_03, test_handoff_legacy_bad_03_is_fail, test_handoff_read_census
M-c: 1 failed, 12 passed, 377 deselected in 1.53s | failed: test_handoff_bad_01_no_03
M-d: 7 failed, 6 passed, 377 deselected in 2.02s | failed: test_check_handoff_all_legacy_and_fail, test_handoff_03_is_directory, test_handoff_all_bad_01_good_03, test_handoff_all_one_bad_03, test_handoff_bad_01_no_03, test_handoff_bad_03, test_handoff_legacy_bad_03_is_fail
M-f: 1 failed, 12 passed, 377 deselected in 1.69s | failed: test_handoff_legacy_bad_03_is_fail
M-g: 4 failed, 9 passed, 377 deselected in 1.87s | failed: test_handoff_03_is_directory, test_handoff_all_one_bad_03, test_handoff_bad_03, test_handoff_legacy_bad_03_is_fail
BASE: 8 failed, 5 passed, 377 deselected in 2.15s | failed: test_handoff_03_is_directory, test_handoff_all_bad_01_good_03, test_handoff_all_one_bad_03, test_handoff_bad_01_no_03, test_handoff_bad_03, test_handoff_legacy_bad_03_is_fail, test_handoff_read_census, test_unreadable_problem_fullmatch_only
restored: 13 passed, 377 deselected in 1.31s
```
Each mutation fails every test the 04 table names for it, and the same sets as 05.

check_handoff for this item (`python3 scripts/check_handoff.py 092`, exit 0):
```
sources count (unique URLs in 01-research.md): 7
fact-check rows: 63
totals line: 63 rows -> 55 as-is, 8 fixed, 0 removed
PASS
```

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat 138e0ce c098a17`: scripts/check_handoff.py, scripts/check_pipeline.py, tests/test_pipeline_check.py; nothing in ccbot/, config/ or data/, no TRIGGER or TRIGGER_DIRS path)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001 (ESCALATED: only selecting rule is LEGACY, re-counted 7 of 7, 0 unreadable; fixture 1 of 1 each way), RI-010 (ESCALATED: my log line written with `--log` right after this file, committed with commit_step.py; LOG TIME and LOG BATCH do not name 092), RI-014 (OPEN: this item's family; fix makes no git call, census pins 0 raw reads, no-Traceback fixtures (a)-(f), mutations M-a/M-b fail). Also checked (GUARDED): RI-002 (no count from an unread file; R1 log pin), RI-006 (census from AST; test counts pasted from pytest), RI-008 (3.11 compile clean, 3.10 absent), RI-009 (mutations only in a scratch worktree, no stash), RI-012 (fullmatch plus in-text negative test).

RI-014: OPEN, unchanged; 092 closes the check_handoff strict-read near miss (built on PR #36, I3 PASS r1).

## Pipeline line (step 2)
check_pipeline line: `092: awaiting A1 (FULL)` (run after 06, 07 and the I3 --log line were written; exit 0)

## Sent back / sent to Audit
Sent to Audit (A1, per-item mode): work/092/07-audit-task.md. Not sent back.
