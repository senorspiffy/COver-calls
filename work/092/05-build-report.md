# 05 Build report - 092
Built on branch `daily-fixes/2026-11-24` (on open PR #36), base commit 138e0ce. Scratch dir (mkdtemp, item 091): /tmp/claude-0/-home-claude/17dd566b-e13e-58fe-b556-13d450b5acde/scratchpad/I2-092-r1-ewkz31zm. `git rev-parse --is-shallow-repository`: false. `RULES BRANCH: none`.

## Changes made (file: what changed)
File counts (from commands, item 012):
- new: `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` → 0
- changed: `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` → 3

1. scripts/check_handoff.py
   - `_pipeline()` (new): inserts the scripts dir into sys.path only when it is not already there, then `import check_pipeline` and returns the module. No `from check_pipeline import` remains.
   - `_report(problems)` (new): prints each `FAIL: <p>` line and `PASS` / `<n> problem(s)`; returns 1 if any problem, else 0. Used by all three exits of `main` (why03, no 03 with a problem, readable 03).
   - `UNREADABLE_PROBLEM` (new constant), exactly the plan's regex.
   - `main`: `cp = _pipeline()` after the folder check. 01 via `cp._read(research, missing_ok=True)`: why01 prints `sources count (unique URLs in 01-research.md): not computed (<p>)` and appends `<p>` to problems (`cp._UNREAD[cp._shown(research)]` indexed directly); readable prints the count as before; absent prints nothing. 03 via `cp._read(handoff, missing_ok=True)`: why03 appends the problem and returns `_report(problems)` (exit 1) before `section()`; absent prints `no <handoff>; nothing else to check` and returns `_report(problems)` if any problem, else 0; readable unchanged.
   - `_branch_with_handoff`: `cp = _pipeline(); found = cp.open_branches()`.
   - `check_all`: LEGACY branch is `elif d.name in LEGACY and not any(UNREADABLE_PROBLEM.fullmatch(p) for p in problems):`.
   - Module docstring: the not-computed line, `FAIL: <path> unreadable (<detail>)` with exit 1, the claim "No traceback on an unreadable 01 or 03; work/ listing errors under --all may still raise", never LEGACY, depends on check_pipeline.py importing cleanly.
2. scripts/check_pipeline.py (docstring only, L360): "Known gap: scripts/check_handoff.py still reads its files strictly." replaced by: check_handoff reads 01 and 03 through _read (item 092); known gaps 01 F17 (`--all` never reads the 01 of an item with no 03) and 01 F22 (open_branches' request.md why ignored). No code change.
3. tests/test_pipeline_check.py: after `test_unreadable_log_exits_1_alone`, re-using `BAD`: `_run3h`, `_h03`, a small assert helper `_ok3` (no Traceback, exact lines in `out.splitlines()`, exit code), fixtures (a)-(f) each with its clean twin, `test_unreadable_problem_fullmatch_only`, `test_handoff_read_census`, `test_r1_log_refuses_not_computed`. `_run3` unchanged.

## Connectivity check
- [x] every new function/rule is used: `_pipeline` is called by `main` and `_branch_with_handoff`; `_report` by `main` (3 call sites); `UNREADABLE_PROBLEM` by `check_all` and `test_unreadable_problem_fullmatch_only`; `_run3h`/`_h03`/`_ok3` by the new tests.
- [x] every input has a source, every output has a consumer: 01/03 come from work/<ID>/ via `cp._read`; the detail comes from `cp._UNREAD`, which `_read` writes before returning a why. The `FAIL:` lines are read by `check_all` (problems list) and by the orchestrator after R1/R3 (run-item.md); the not-computed sources line is what the orchestrator copies to `--log R1`, which refuses it (`test_r1_log_refuses_not_computed`).
- [x] every branch ends in a defined result: 01 readable/absent/unreadable; 03 readable/absent/unreadable; absent 03 with and without an 01 problem; `--all` LEGACY with and without an unreadable problem. Each ends in a printed line and an exit code, pinned by (a)-(f) and twins.
- [x] no leftover TODOs or unused files: `git diff | grep -c TODO` adds none; no new files outside work/.

Missing-data policy:
- `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/` → 38 hits, all pre-existing; `git diff -- ccbot | wc -l` → 0, so no new or changed hit in ccbot/.
- Same pattern plus the 014 patterns (`: float|int = <n>`, ` < `/` > `) over the added lines of scripts/ and tests/ (`git diff -U0 -- scripts tests | grep -nE ...`): 4 hits, none a defaulted value:
  - diff L10, L11: docstring words ("number", "or 03"), not code.
  - diff L30: `_report` docstring "1 if any, else 0".
  - diff L34: `return 1 if problems else 0` is the exit code (moved from the old `main` end), not a value standing in for data. An unreadable file always adds a problem, so it can never reach 0.
- No dataclass field and no `>`/`<` comparison is added.
- `elif text01 is not None:` is the absent-01 case (missing_ok gives `(None, None)`): it prints no count and passes nothing.

## Test output (pasted, not summarized)
Full suite, `python3 -m pytest -q` from the repo root, last lines as printed:
```
........................................................................ [ 87%]
........................................................................ [ 96%]
..............................                                           [100%]
821 passed, 1 skipped in 149.79s (0:02:29)
```
Suite: 821 passed, 1 skipped in 149.79s (0:02:29)

Targeted run while building (`python3 -m pytest -q tests/test_pipeline_check.py -k "handoff or unreadable_problem or r1_log_refuses or read_census or read_contract"`): `14 passed, 376 deselected in 2.01s`.

Check 2, `python3.11 -m py_compile scripts/check_handoff.py scripts/check_pipeline.py tests/test_pipeline_check.py; echo "py_compile exit $?"`:
```
py_compile exit 0
```
Check 3: `grep -c "from check_pipeline import" scripts/check_handoff.py` → `0`; `grep -rc "still reads its files strictly" scripts/` → `0` for every file (scripts/check_handoff.py:0, scripts/check_pipeline.py:0, and the rest 0).

Check 4, `python3 scripts/check_handoff.py --all` on the branch tree (exit 0, 99 lines):
```
no new failures
```
- LEGACY count: `grep -c ": LEGACY ("` → `7`; `grep -c "unreadable"` → `0`; no `: FAIL` or `: not checked` line.
- Same-output check (Extra research 1): the base `check_handoff.py` (`git show HEAD:scripts/check_handoff.py`, run from the scratch dir) gives a byte-identical `--all` output (`diff` → IDENTICAL), and the single-item output plus exit code of every work/ folder is identical too: `items 98 differ 0`.

Mutations (scratch copy of scripts/ and tests/ in the scratch dir `repo/`, one at a time, restored after each; script `mut.py`; each run is `pytest -q tests/test_pipeline_check.py -k "handoff or unreadable_problem or r1_log_refuses"`):
```
M-a: 3 failed, 9 passed, 378 deselected in 2.43s | failed: test_handoff_all_bad_01_good_03, test_handoff_bad_01_no_03, test_handoff_read_census
M-b: 5 failed, 7 passed, 378 deselected in 3.80s | failed: test_handoff_03_is_directory, test_handoff_all_one_bad_03, test_handoff_bad_03, test_handoff_legacy_bad_03_is_fail, test_handoff_read_census
M-c: 1 failed, 11 passed, 378 deselected in 1.41s | failed: test_handoff_bad_01_no_03
M-d: 7 failed, 5 passed, 378 deselected in 2.11s | failed: test_check_handoff_all_legacy_and_fail, test_handoff_03_is_directory, test_handoff_all_bad_01_good_03, test_handoff_all_one_bad_03, test_handoff_bad_01_no_03, test_handoff_bad_03, test_handoff_legacy_bad_03_is_fail
M-f: 1 failed, 11 passed, 378 deselected in 1.36s | failed: test_handoff_legacy_bad_03_is_fail
M-g: 4 failed, 8 passed, 378 deselected in 1.72s | failed: test_handoff_03_is_directory, test_handoff_all_one_bad_03, test_handoff_bad_03, test_handoff_legacy_bad_03_is_fail
restored: 12 passed, 378 deselected in 1.27s
```
Each row fails every test the plan names (M-a: census, (a), (f); M-b: census, (b)-(e); M-c: (a); M-d: (b)-(f); M-f: (e); M-g: (b), (d)), plus some extra.
- M-a/M-b were done by putting back `x.read_text(encoding="utf-8") if x.exists()`.
- M-c is the no-03 branch with only `return 0`.
- M-d prints the problem without `FAIL: `.
- M-f drops the UNREADABLE_PROBLEM guard.
- M-g returns 1 on the why03 path without calling `_report`.

Feasibility numbers (Guardrail tests):
- the LEGACY exception covers 7 IDs (002-008);
- fixture (e) gives 1 of 1 FAIL, and its twin 1 of 1 LEGACY;
- the real tree gives 7 LEGACY lines, 0 of 7 unreadable (check 4).

`python3 scripts/check_pipeline.py` (run after the build, before writing 05): exit 1, `SKIPPED: none`, `UNREADABLE: none`, `UNTRACKED CHANGE: none`, `I3 FAIL: none`, `A1 FAIL: none`.
- The only failing lines are other items in flight in this checkout: `INCOMPLETE: 097 (no log line for I1), 098 (no log line for I1)` and `UNCOMMITTED STEP: 097 04-build-plan.md ...; 098 04-build-plan.md ...`. Their 04 files are being written by the orchestrator now. They are not a defect of this build.
- 092 shows `in progress (FULL: next 05)`.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat`: scripts/check_handoff.py, scripts/check_pipeline.py, tests/test_pipeline_check.py; nothing in ccbot/, config/ or data/)

## Deviations from plan
- I added a small test helper `_ok3(code, out, err, want_code, lines)` that makes the plan's three asserts (no Traceback, exact lines, exit code). It is not named in the plan.
- The census positive control asserts `dict(reads) == {"main": 2}`. That is stricter than "exactly 2 in main": it also means no `_read` call outside main.
- Nothing else differs from the plan.

## Known gaps (from 04, repeated)
1. check_handoff now imports check_pipeline for every single-item run, so a broken check_pipeline.py breaks it.
2. After R1, an unreadable 01 gives exit 1 and a `not computed` sources value. `--log R1` refuses it (`test_r1_log_refuses_not_computed`), so the item shows INCOMPLETE until R1 is re-run or the file is fixed. run-item.md L17 does not say this. A `.claude/` edit needs the person's OK, so A1 may open a request.
3. `--all` never reads the 01 of an item with no 03.
4. Under `--all`, an unreadable request.md read by open_branches is silent.
5. A failing `work.iterdir()` or `is_dir()` may still raise.
6. Both scripts are RULE_PATHS, so the person's OK is needed at PR review.

## Recurring issues checked (item 013)
I read logs/recurring-issues.md first and checked against each open or ESCALATED entry:
- RI-001 (ESCALATED): checked. The only selecting rule is the LEGACY exception, and it has counts: 7 IDs, fixture 1 of 1 each way, 0 of 7 unreadable on the real tree (check 4).
- RI-010 (ESCALATED): checked. No log line is typed by hand. The I2 line is written with `check_pipeline.py --log` right after this file, and committed with `commit_step.py`.
- RI-014 (OPEN): checked. This item is in its family. There is no git call in the fix, the census twin pins 0 raw reads, and fixtures (a)-(f) assert no Traceback.
- Also checked (GUARDED): RI-002 (no count computed from an unread file; the R1 log pin), RI-006 (census and file counts from commands/AST), RI-008 (py_compile under 3.11 clean; no reused quote inside f-string braces), RI-009 (mutations only in the scratch copy; no stash), RI-012 (fullmatch plus negative test).

RI-001: ESCALATED, unchanged (no new selecting rule without a count).
RI-010: ESCALATED, unchanged (I2 line via --log).
RI-014: OPEN; 092 closes the check_handoff strict-read near miss (built, PR #36; mutations M-a/M-b fail the census and fixtures).
