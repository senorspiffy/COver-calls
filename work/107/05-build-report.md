# 05 Build report - 107
Scratch dir: /tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i2-107-r1-23bt4ffz

Base: a5b8edd (daily-fixes/2026-11-25, after 108, 110, 105 and 109). Scratch worktrees `base` (baseline suite at a5b8edd) and `mut` (a5b8edd with this build's 7 files copied in, for mutants) were made with `git worktree add --detach` inside the scratch dir above. The pyc dir `pyc-pkftc9fg` was made inside it with the same mkdtemp command (prefix `pyc-`). Mutants ran only in `mut`, and each mutated file was restored there from a copy of the build file. In the main checkout I ran only the unmutated tests. No `git stash` was used.

## Changes made (file: what changed)
- `.claude/commands/run-item.md`, `.claude/agents/i2-builder.md`, `.claude/agents/i3-verifier.md`, `.claude/agents/a1-auditor.md` (FLAG: these 4 need the person's OK in PR review). Each one gets the BYTECODE sentence once, placed directly after the SCRATCH sentence's closing `never in the main checkout (items 091, 097).` with one space before it. It goes on the same line, and nothing else changes. In i2-builder.md and i3-verifier.md it lands before `05 (I2) / 06 (I3) has one column-0 \`Scratch dir:` .... The text was inserted from one string, and a script checked that string against 03 step 1: `03 == constant: True`.
- `tests/test_pipeline_check.py`:
  - 5(a): the constant `BYTECODE` and the test `test_bytecode_sentence_same_in_four_files` go directly after `test_scratch_sentence_same_in_four_files`. The test asserts both variable names are in the constant, and that each file in `SCRATCH_FILES` has `.count(BYTECODE) == 1`.
  - 5(b): the module-level helper `_tracked_bytecode(paths)` is added. `test_no_tracked_pycache` now asserts `_tracked_bytecode(files.splitlines()) == []`, and its docstring adds "Item 107: sourceless .pyc too."
  - 5(c): `test_tracked_bytecode_helper` uses the 4-path fixture from 04 and expects the 2 bytecode paths.
- `tests/test_stale_bytecode.py` (new, 75 lines). It holds `STRIP`, `_env`, `_pytest`, `_import_x` and `_stale`, plus the two tests `test_stale_pyc_survives_without_full_guard` (cases a, b, c) and `test_guard_kills_stale_mutant` (case d), as in 04 File 6. These include the empty `pytest.ini`, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` and the stripped `PYTHONSAFEPATH`. The prefix dir is `tmp_path / "pyc-guard"`, a sibling of `src`.
- `tests/test_probe_guardrails.py`: `test_child_env_disables_bytecode_writes(monkeypatch)` goes after `test_shipped_probes_well_formed`. It has no `@NO_GIT`.
- No change to scripts/, ccbot/, config/ or templates/. `git diff --stat -- ccbot/ config/ scripts/` is empty.

File counts (from commands):
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
1
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
6
```
That is 7 files, matching 04's "7 files planned".

## Connectivity check
- [x] Every new function or rule is used.
  - `_tracked_bytecode` is used by `test_no_tracked_pycache` and `test_tracked_bytecode_helper`.
  - `BYTECODE` is used by `test_bytecode_sentence_same_in_four_files`.
  - In test_stale_bytecode.py, both tests use `_env`, `_pytest`, `_import_x` and `_stale`, and `_env` uses `STRIP`.
  - The BYTECODE sentence is in all 4 rule files that agents read, and this 05 follows it (env-check line below).
- [x] Every input has a source and every output has a consumer. The stale tests write their own inputs in `tmp_path`. `_child_env` is read from scripts/probe_guardrails.py. Each result is a pytest pass or fail, pasted below.
- [x] Every branch ends in a defined result. None of these skips or passes silently; each fails with a named message:
  - a stale case that does not reproduce: "stale case not reproduced on this Python (item 107)"
  - no pyc after setup: "setup wrote no src/__pycache__/m.*.pyc (item 107)"
  - an mtime mismatch: "precondition int(st_mtime) differs"
  - a size mismatch: "precondition size ..."
  - (d) not killed: "(d) full guard did not kill the mutant"
  - `_import_x` on an ImportError: stdout `""`, which fails the `== "1"` or `== "2"` assert
- [x] No leftover TODOs or unused files. `git diff -U0 -- tests/ | grep '^+' | grep -c TODO` gives 0, and `grep -c TODO tests/test_stale_bytecode.py` gives 0.
- Missing-data policy grep (`grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/`): 38 hits, all unchanged, because ccbot/ is untouched. The same pattern on the added test lines and on tests/test_stale_bytecode.py gives no output. `: float = 0` gives 0. A ` [<>] ` comparison in the added lines gives no output. No dataclass was added.
- Feasibility (real numbers, 2026-11-26):
  - BYTECODE sentence: 4 of 4 rule files (`grep -c "PYTHONPYCACHEPREFIX\|DONTWRITEBYTECODE"` gives 1 in each; it was 0 of 4 in 03).
  - Tracked bytecode: `git ls-files | grep -cE "\.pyc$|__pycache__"` gives 0 of 1259 tracked files.
  - The stale case reproduces on Python 3.13.18 with pytest 9.1.1: case (a) exits 0 and prints `1`, and case (d) exits 1 and prints `2`. The pyc-guard dir holds 0 files.
  - Wall time of `test_stale_bytecode.py` (`--durations=0`, main checkout): `test_guard_kills_stale_mutant` 1.00 s, `test_stale_pyc_survives_without_full_guard` 0.70 s.
- python3.11 is present: `python3.11 -m py_compile tests/test_stale_bytecode.py` gives rc=0. python3.11 has no pytest, so the stale test was not run on 3.11. The existing `test_every_py_compiles_on_oldest_python` passed in the full suite. That py_compile wrote `tests/__pycache__/test_stale_bytecode.cpython-311.pyc` (gitignored, not a mutant run), and I deleted it.

## Test output (pasted, not summarized)
Baseline at a5b8edd, scratch worktree `base`: `python3 -m pytest -q -p no:cacheprovider`
```
1035 passed, 1 skipped in 127.42s (0:02:07)
```
Build, repo root, main checkout: `python3 -m pytest -q` (exit 0)
```
........................................................................ [ 96%]
.................................                                        [100%]
1040 passed, 1 skipped in 130.94s (0:02:10)
```
Suite: 1040 passed, 1 skipped in 130.94s (0:02:10)

1035 + 5 new test functions = 1040, as planned (2 in test_stale_bytecode.py, 1 in test_probe_guardrails.py, 2 in test_pipeline_check.py).

Targeted run before the suite (main checkout, not a mutant run):
```
.......                                                                  [100%]
============================== slowest durations ===============================
1.00s call     tests/test_stale_bytecode.py::test_guard_kills_stale_mutant
0.70s call     tests/test_stale_bytecode.py::test_stale_pyc_survives_without_full_guard

(19 durations < 0.005s hidden.  Use -vv to show these durations.)
7 passed in 23.78s
```

`python3 scripts/check_pipeline.py` (before 05): exit 0, with `107: in progress (FULL: next 05)`, `INCOMPLETE: none`, `SKIPPED: none` and `STASH: none`.

## Mutations (04 Tests and checks, m0-m4)
Env-check line, run with the guard used on every mutant command:
```
$ PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i2-107-r1-23bt4ffz/pyc-pkftc9fg python3 -c 'import sys; print(sys.dont_write_bytecode, sys.pycache_prefix)'
True /tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i2-107-r1-23bt4ffz/pyc-pkftc9fg
```
Each mutant ran as `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<that pyc dir> python3 -m pytest -q -p no:cacheprovider <tests>` in worktree `mut`. The runner is /tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i2-107-r1-23bt4ffz/mut.sh and its raw output is /tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i2-107-r1-23bt4ffz/mut-out.txt. After all the mutants, `find <pyc dir> -type f | wc -l` gave 0, and every one of the 8 files in `mut` matched the build copy (no `DIFF` line).

| Mutant | Change | Tests run | Summary line | Failed |
|---|---|---|---|---|
| m0 | BYTECODE sentence (with its leading space) deleted from .claude/agents/i3-verifier.md | test_bytecode_sentence_same_in_four_files, test_scratch_sentence_same_in_four_files | `1 failed, 1 passed in 0.79s` | test_bytecode_sentence_same_in_four_files. SCRATCH still passes. |
| m1 | case (d) env `_env(PYTHONDONTWRITEBYTECODE="1")` (prefix dropped) | tests/test_stale_bytecode.py | `1 failed, 1 passed in 1.26s` | test_guard_kills_stale_mutant: "(d) full guard did not kill the mutant (item 107)", inner `1 passed` |
| m2 | `_stale` writes `X = 22\n` | tests/test_stale_bytecode.py | `2 failed in 0.38s` | both tests: "precondition size 7 != 6 or != 6 (item 107)" |
| m3 run 1 | line `    env["PYTHONDONTWRITEBYTECODE"] = "1"` deleted from scripts/probe_guardrails.py | test_child_env_disables_bytecode_writes | `1 failed in 0.06s` | test_child_env_disables_bytecode_writes |
| m3 run 2 | same | same | `1 failed in 0.07s` | same |
| m3 run 3 | same | same | `1 failed in 0.07s` | same |
| m4 | `_tracked_bytecode` without ` or p.endswith(".pyc")` | test_tracked_bytecode_helper, test_no_tracked_pycache | `1 failed, 1 passed in 0.81s` | test_tracked_bytecode_helper |

Result: m0-m4 each give at least 1 failed under the guard, and m3 fails on 3 of 3 runs.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat`: 4 .claude/ rule files, tests/test_pipeline_check.py, tests/test_probe_guardrails.py, plus new tests/test_stale_bytecode.py; no TRIGGER or TRIGGER_DIRS file)

## Deviations from plan
1. m0 was first run as a text edit: an `X` was inserted inside the sentence in i3-verifier.md, which gave `1 failed, 1 passed in 0.81s`. Because 04 says "delete", I re-ran m0 as a true deletion of ` ` + BYTECODE. The table shows the deletion run.
2. 04's Expected result says `RULES BRANCH` will name the 4 rule files. It shows `RULES BRANCH: none`. Per scripts/check_pipeline.py L232, that line lists other open branches (not merged into HEAD) that change the rules, so it does not list the checked-out branch's own uncommitted or unpushed edits. The FLAG for the person stays in effect through PR review. This is not a code change, only a note that the expectation did not hold.
3. Placement: 04 5(a) puts the `BYTECODE` constant and its test after `test_scratch_sentence_same_in_four_files`. I added a one-line comment above the constant (`# Item 107 step 1 (RI-013): ...`), in the style of the SCRATCH block. This is not a behaviour change.

## Recurring issues checked (item 013)
I read logs/recurring-issues.md first. The OPEN or ESCALATED entries are RI-001 and RI-014. I also checked these GUARDED entries: RI-002, RI-004, RI-005, RI-006, RI-007, RI-009, RI-010, RI-012, RI-013.
RI-001: ESCALATED, unchanged. Every count in this 05 comes from a command: 4 of 4 rule files, 0 of 1259 tracked bytecode files, and +5 tests (1035 to 1040). There are no "every" claims beyond those counts.
RI-014: OPEN, unchanged. No new git-history read. `test_no_tracked_pycache` keeps `git ls-files`, and the new tests use only `tmp_path` or a pure env dict.
RI-002: GUARDED, holds. Every failed precondition or non-reproducing case fails with a named message, and none is skipped or defaulted. An ImportError gives `""`, which fails the exact-value assert.
RI-004/005: GUARDED, holds. The worked example was re-derived by the run: size 6 == 6, and m2 shows 7 != 6.
RI-006: GUARDED, holds. File counts and the Suite line were copied from command output.
RI-007: GUARDED, holds. Scope FULL. This is the I2 step after 04.
RI-009: GUARDED, holds. Mutants ran only in the scratch worktree `mut` inside my own mkdtemp dir. Restores were made from copies, and no stash was used.
RI-010: GUARDED, holds. The env-check line is pasted above the mutant table (Residual 1: no script checks it).
RI-012: GUARDED, holds. Asserts use exact stdout (`"1"`, `"2"`) and exact return codes (0, 1).
RI-013: GUARDED, this item's own family. The guard is applied to every mutant command, and the env-check shows `True <pyc dir>`.
