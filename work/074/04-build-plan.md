# 04 Build plan - 074
Fit verdict: FIT WITH CHANGES

Fit check. This is tooling only. Nothing changes in ccbot/, config/, data/ or reports/, nothing connects to a brokerage, and there is no trading, sizing or capital rule, so the ~$3k account and the strategy rules are not affected. It does not conflict with existing code. It reads committed code through a detached worktree, as tests/test_pipeline_check.py `_run_head` (L52-62) already does. The script lives in scripts/, which the suite does not collect (pyproject `testpaths = ["tests"]`, L20), so the real ~2-minute probes never run in `pytest -q`. The a1-auditor.md edit puts this on the RULES BRANCH list (.claude/), so the person must OK it in PR review.

The changes to 03, each one explained under Extra research or in the Rule trace:
- C1. Every pytest command gets `--rootdir=<wt>`. Without it, the fixture repo (which has no config file) gets node ids rooted at `<wt>/tests`, so `tests/test_mod.py::test_f` is never found.
- C2. The target is looked up in junit by `(classname, name)`, using pytest's own mangling rule. Counts come from the `<testcase>` children.
- C3. The compile check uses the builtin `compile(text, path, "exec")`, not `py_compile`, so no .pyc is written. The restore check is `git status --porcelain --untracked-files=no`. The child env sets `PYTHONDONTWRITEBYTECODE=1`. Without these, pytest's `__pycache__/` in a fixture repo with no .gitignore would show as `??` and trip "worktree not restored".
- C4. The child env drops `PYTEST_ADDOPTS`, which would otherwise add options such as `-k` or `-x` and change the counts. The script prints the dropped value.
- C5. `--repo` defaults to `Path(__file__).resolve().parents[1]` (the repo root), not "the script's parent dir".
- C6. A baseline timeout reads `ERROR (baseline: timeout <s> s)`. Fixture (h) asserts `timeout 1 s` and `ERROR`.
- C7. I3's "exit-code check removed" mutant does not make (d) fail: (d) is caught earlier, by the compile check. A new fixture (d2), a module-level import error that gives pytest exit 2 at collection, asserts the exact text `ERROR (pytest exit 2)`. That pins it.
- C8. (b2) gets a concrete pair (`G = 1` → `G = 2`, test_g checks G).
- C9. Absent-case tests are added for every Missing-inputs row that 03 left untested (see Guardrail tests).
- C10. A per-test-file baseline line is printed with its runtime, because step 5 needs measured baseline time.
- C11. `git worktree prune` also runs at the start, to clear a registration left by an interrupted run.
- C12. A cheap suite test checks the shipped `PROBES` against the working tree: anchor count 1 and the target `def` exists. A refactor that removes an anchor then turns the suite red in the same PR, not only at the next audit.
- C13. A README scripts-list line (shared file with 072, see Files).

## Extra research (with sources)
1. **rootdir and node ids.** If no config file or setup.py is found, pytest uses "the already determined common ancestor" of the args as rootdir, "each test is assigned a unique nodeid which is rooted at the rootdir", and "`--rootdir=path` ... can be used to force a specific directory" (https://docs.pytest.org/en/stable/reference/customize.html, fetched 2026-11-18). The fixture repo in step 3 has no pyproject or ini, and the arg is `tests/test_mod.py`, so the rootdir would be `<wt>/tests`. The node id would then be `test_mod.py::test_f` and the target `tests/test_mod.py::test_f` would give a false `ERROR (baseline: target not found)`. The real repo is not affected (pyproject.toml sits at `<wt>`), but passing `--rootdir=<wt>` makes both the same. Fixture (a) pins it: with the flag removed, (a) gives ERROR, not HOLDS. → C1.
2. **junit classname/name.** pytest's `mangle_test_address` replaces `/` with `.` in the path, strips `.py$`, and keeps params on the last name. `record_testreport` sets `classname = ".".join(names[:-1])` and `name = names[-1]`. A collection failure becomes a testcase with an `<error message="collection failure">` child. The testsuite `errors`/`failures` come from the same stats (https://raw.githubusercontent.com/pytest-dev/pytest/main/src/_pytest/junitxml.py, fetched 2026-11-18). So `tests/test_realtest.py::test_leading_edge_100_days_blocks` → `("tests.test_realtest", "test_leading_edge_100_days_blocks")`. None of the three test files has a test class (Grep `class ` in tests/test_realtest.py and tests/test_diff_reports.py: 0 hits), so the simple mapping is enough. Classes would join with `.` in classname and still work. → C2. Per testcase: `<failure>` = failed, `<error>` = error, `<skipped>` = skipped, no child = passed. FAILED lines print `<classname>::<name>`.
3. **PYTEST_ADDOPTS.** "you can set a `PYTEST_ADDOPTS` environment variable to add command line options", combined as `<pytest.ini:addopts> $PYTEST_ADDOPTS <extra command-line arguments>` (https://docs.pytest.org/en/8.3.x/example/simple.html, fetched 2026-11-18; search result list: https://pytest.org/latest/example/simple.html). An inherited `-k`/`-x`/`--lf` would change the counts, or skip the target, without any trace in the script's command. → C4. A fixture pins it.
4. **No .pyc in the worktree.** 03 row D22 already notes that `py_compile` writes a .pyc to `__pycache__`, and pytest's assertion rewrite does too. That is harmless in the real repo (.gitignore L11), but the fixture repo has no .gitignore, and 03's restore check (`git status --porcelain` empty) would flag `?? pkg/__pycache__/`. The builtin `compile()` catches the same SyntaxError and writes nothing. `--untracked-files=no` keeps the check about tracked files, which are the only ones a mutation touches. → C3.
5. **Exit 2 on collection errors.** pytest's exit code 2 is "Test execution was interrupted by the user"... In practice pytest also uses 2 for collection errors ("Interrupted: 1 error during collection"). 03 row D19 quotes the exit-code page. Fixture (d2) measures this rather than relying on the doc. If the installed pytest gives another non-0/1 code, the fixture's expected text is the measured one, and I2 writes it down. The rule (exit not in {0,1} → ERROR) is unchanged.

## Files to create/change
Four files. Each edit is given as a text anchor, not a line number, because 072 is being built on the same branch.

1. **NEW `scripts/probe_guardrails.py`** (stdlib only).
   - `PROBES`: a list of 3 dicts with keys `id, ri, file, anchor, replacement, test_file, target, module` (optional) and `recorded` (optional, printed only). Strings are copied byte for byte from 03 step 1 (= scratchpad probe.py L12-18). `recorded` values: `"2026-11-18: 9 failed, 41 passed"`, `"2026-11-18: 4 failed, 46 passed"`, `"2026-11-18: 1 failed, 16 passed"`.
   - Functions (names fixed so the tests can call them):
     - `junit_key(nodeid) -> (classname, name)`, from Research 2.
     - `read_junit(path) -> dict[(classname, name)] = "passed"|"failed"|"error"|"skipped"`. Raises `JunitError` if the file is missing or unparseable.
     - `classify(returncode, junit_path, target, timed_out) -> (verdict, results)`. The order is fixed, from 03 step 2.6: timeout, then exit not in {0,1}, then junit missing or bad, then errors > 0, then target not in results, then target failed = HOLDS, else NOT HELD.
     - `run_pytest(wt, test_file, junit, timeout)` builds `[sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rfE", f"--rootdir={wt}", f"--junit-xml={junit}", test_file]` with cwd=wt. The env is `os.environ` minus `PYTEST_ADDOPTS`, plus `PYTHONDONTWRITEBYTECODE=1`.
     - `module_file(wt, module, timeout)` runs a child `-c` import with cwd=wt and returns the resolved `__file__`, or the import error text.
     - `worktree_clean(wt) -> bool` runs `git -C <wt> status --porcelain --untracked-files=no`. It is its own function so the test can monkeypatch it.
     - `main(argv=None, probes=PROBES) -> int`.
   - Flow, per 03 step 2:
     - 2.1 checks `shutil.which("git")` (→ exit 2 `SETUP: git not found`), runs `git worktree prune`, `rev-parse --verify <ref>^{commit}`, then `TemporaryDirectory()` with no `dir=` and no `delete=`. Scratch inside the repo → exit 2. Then `worktree add --detach -q`. First line: `ref <ref> = <sha>`.
     - 2.2-2.7 per probe.
     - The baseline runs once per test_file, before that file's first probe. It prints `baseline <test_file>: <f> failed, <p> passed, <e> errors; <s> s`.
     - The module check runs once per (module, file) pair, before any mutation.
     - 2.8 lines and the TOTAL line. Exit 0 only if all probes are HOLDS, 1 otherwise, 2 for setup errors.
     - 2.9 `finally`: `worktree remove --force`, then `prune`.
   - Constraints: file I/O by `read_bytes`/`write_bytes` with explicit utf-8 decode/encode (test_safety L51-64), no same-quote f-strings (RI-008), and no `assert` for control flow (03 FOR 2b).
   - P3's line says `code check: n/a (no module; tests run scripts/diff_reports.py by path via tests/conftest.py REPO, conftest L7)`.
2. **NEW `tests/test_probe_guardrails.py`**: the tests below. It loads the script with `importlib.util.spec_from_file_location` from `REPO/"scripts"/"probe_guardrails.py"`. The `NO_GIT` skipif is copied from test_pipeline_check L43, so the test does not import that test module.
3. **`.claude/agents/a1-auditor.md`**. Anchor: the line `In the daily review, also check that every guardrail from past BUG items is still in place.` Append, in the same paragraph, the 03 step 4 text verbatim, plus "(item 074)". No other item on this branch plans to edit this file (Grep of 071-073 03/04: 0 hits). It is a RULES BRANCH file, so the person must OK it.
4. **`README.md`**. **Shared with 072**, which replaces text inside the line starting "- `scripts/check_handoff.py`". Anchor: insert a new line right **after** the line starting "- `scripts/check_pipeline.py`", and do not touch the check_handoff line. The new line: "- `scripts/probe_guardrails.py` - runs each recurring-issue mutation probe listed in its `PROBES` on a scratch worktree of `--ref`; exit 0 only if every probe's target test fails (HOLDS); run by A1 daily (item 074)". If 072 is still unmerged when 074 is built, build on top of 072's branch state (run-item rule) and say so in 05. The edits are on different lines with an unchanged line between them, so a 3-way merge does not conflict.

Not changed: logs/recurring-issues.md (item 036; A1's daily commit renames the probes by entry id, per 03 step 7(iv)). Also unchanged: templates/, scripts/check_pipeline.py and tests/test_pipeline_check.py (071's files).

## Tests and checks
One committed fixture repo per test (helper `_fixture(tmp_path)`). It holds:
- `git init` with user.name/email set by `-c` flags
- `pkg/__init__.py` (empty)
- `pkg/mod.py` = `def f():\n    return 1\n# marker\nG = 1\n`
- `pkg/twice.py` = `# marker\n# marker\n`
- `tests/test_mod.py` (`test_f`: `mod.f() == 1`; `test_g`: `mod.G == 1`)
- `tests/test_red.py` (`test_ok`: passes; `test_bad`: `assert False`)
- `tests/test_slow.py` (`test_sleep`: `time.sleep(5)`)
- no pyproject and no .gitignore, on purpose (Research 1, 4)

Tests:
1. `test_holds_exits_0` (a): one probe, `return 1`→`return 2`, target `tests/test_mod.py::test_f`, module `pkg.mod`, recorded `"99 failed"`, with `PYTEST_ADDOPTS="-k test_g"` set by monkeypatch. Expect `HOLDS`, `1 failed, 1 passed, 0 errors`, `FAILED tests.test_mod::test_f`, `recorded 99 failed` (never compared), `PYTEST_ADDOPTS ignored`, and exit 0.
2. `test_mixed_run_reports_every_probe`: one `main()` call. Probes in order:
   - (c1) anchor `nosuch` → `ANCHOR MISSING (count 0)` and `pytest not run`
   - (a) → HOLDS
   - (b) `# marker`→`# changed` → NOT HELD
   - (b2) `G = 1`→`G = 2`, target test_f → NOT HELD, with `FAILED tests.test_mod::test_g` printed
   - (c2) file pkg/twice.py, anchor `# marker` → `ANCHOR MISSING (count 2)`
   - (d) `return 1`→`return (` → `ERROR (mutation does not compile`
   - (d2) `# marker`→`import nosuchmod_074` → `ERROR (pytest exit 2)`, exact text
   - (e) target `tests/test_mod.py::test_typo` → `ERROR (baseline: target not found)`
   - (f) test_file tests/test_red.py, target test_ok → `ERROR (baseline:` with `1 failed`
   - (k) file `pkg/absent.py` → `ANCHOR MISSING (file not in <sha>)`
   - (l) test_file `tests/test_nofile.py` → `ERROR (baseline: pytest exit 4)`
   - (i1) module `pkg.nosuch` → `ERROR (code under test is` with `ModuleNotFoundError`
   - (i2) module `pkg` with file pkg/mod.py → `ERROR (code under test is <...>/pkg/__init__.py)`
   - (o) (b) with no `recorded` → `recorded: none`

   Also asserted:
   - exit 1
   - `TOTAL: 13 probes, 1 hold, 2 not held, 3 anchor missing, 7 error`
   - `baseline tests/test_mod.py:` printed exactly once
   - (g): SHA-256 of every fixture working file is the same before and after, `git status --porcelain` is empty in the fixture repo, and `git worktree list --porcelain` has exactly 1 `worktree ` line

   (o) is folded into (b), so 13 probes: c1, a, b, b2, c2, d, d2, e, f, k, l, i1, i2.
3. `test_timeout` (h): test_file tests/test_slow.py, `--timeout 1`. The line has `ERROR (baseline: timeout 1 s)` and the exit is 1. The worktree is still removed.
4. `test_setup_errors_exit_2` (parametrized ×3):
   - `shutil.which` monkeypatched to None → `SETUP: git not found`
   - `--ref nosuch` → `SETUP: ref nosuch not found`
   - `tempfile.tempdir` monkeypatched to `<fixture>/scratch` → `SCRATCH INSIDE REPO`

   Each exits 2 with no probe line.
5. `test_classify_missing_or_bad_junit` (unit): a missing path and a file holding `not xml` each → `ERROR (no junit result)`. A valid junit without the target → `ERROR (target not run)`. A junit with 1 error testcase and exit 1 → `ERROR (1 errors)`. Exit 3 → `ERROR (pytest exit 3)`.
6. `test_unrestored_worktree_stops`: `worktree_clean` monkeypatched to False after the first probe → `ERROR (worktree not restored)`. The second probe has no line, and the worktree is still removed.
7. `test_shipped_probes_well_formed` (C12, no subprocess, no git): 3 entries, unique ids, every required key present. Each `anchor` occurs exactly once in `REPO/<file>` (utf-8). Each target's function name appears as `def <name>(` in `REPO/<test_file>`. The targets are exactly the three node ids in 03 step 1.

Checks:
- `python3 -m pytest -q tests/test_probe_guardrails.py tests/test_safety.py`: all pass. test_safety's utf-8, f-string and 3.10-compile tests cover the new files once they are tracked.
- Greps (I3):
  - `probe_guardrails.py --ref origin/main` in .claude/agents/a1-auditor.md: 1 hit
  - `scripts/probe_guardrails.py` in README.md: 1 hit
  - `run by R3, I3, A1` in README.md: unchanged by 074
  - `read_text\|write_text` in the script: every hit names utf-8
  - `delete=` in the script: 0 hits
- I3 mutations of the script, each on a scratch copy (03 step 3 plus C7):
  - count check removed → test 2 (c1/c2) fails
  - baseline check removed → (f) fails
  - "any failure = HOLDS" → (b2) fails
  - exit-code check removed → (d2) fails (the text becomes `ERROR (1 errors)`)
  - `--rootdir` removed → test 1 fails
  - `PYTEST_ADDOPTS` kept → test 1 fails
  - `--untracked-files=no` removed → test 2 fails (worktree not restored)
- Real run, I2 and I3 (03 step 5): `python3 scripts/probe_guardrails.py`, with the whole output pasted plus the measured total and per-baseline runtime.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Step 1 PROBES: 3 entries, byte-for-byte strings, keys, recorded printed only | Files 1 (PROBES); test 7 (well-formed, anchors count 1); test 1 (recorded "99 failed" still HOLDS) |
| Step 1 utf-8 bytes I/O, no `delete=`, no same-quote f-strings | Files 1 constraints; Checks (test_safety, greps) |
| Step 1 CLI `--ref`/`--repo`/`--timeout`, `main(argv, probes)` | Files 1; `--repo` default corrected (C5); tests 1-6 call `main` |
| 2.1 rev-parse ref, TemporaryDirectory outside repo, worktree add --detach, first line SHA | Files 1 flow 2.1, plus a prune at the start (C11); test 4 (bad ref, scratch inside repo); test 2 (`<sha>` in the (k) line) |
| 2.2 file absent / count != 1 → ANCHOR MISSING, no pytest, carry on; mutated != original | Files 1; test 2 (k, c1 first then a still HOLDS, c2) |
| 2.3 compile check | Changed to builtin `compile()` (C3); test 2 (d) |
| 2.3 module `__file__` equality, once per module on the unmutated tree | Files 1 `module_file`; tests 1, 2 (i1, i2) |
| 2.4 baseline once per test_file: exit 0, 0 failed, 0 errors, target passed | Files 1, plus a printed baseline line (C10); test 2 (e, f, l, "baseline printed once") |
| 2.5 mutated run, own junit | Files 1 `run_pytest` (+ `--rootdir`, C1; env, C3/C4) |
| 2.6 classify order from exit code and junit only (RI-012) | Files 1 `classify`; test 5; test 2 (d2); test 3 |
| 2.7 restore bytes, status clean or stop | Files 1 `worktree_clean` with `--untracked-files=no` (C3); test 6 |
| 2.8 per-probe line, FAILED lines, TOTAL, exit 0/1/2 | Files 1; tests 1, 2 (TOTAL counts), 4 (exit 2) |
| 2.9 finally remove --force + prune; repo never written | Files 1; test 2 (g); tests 3, 6 (worktree removed) |
| Step 3 fixtures (a)-(h) | Tests 1-3. (b2) pair fixed (C8). (c1) "no junit file written" became "`pytest not run` in its line", because the scratch dir is internal; the count-check mutant still fails it. (d) exit-code mutant moved to (d2) (C7) |
| Step 3 skipif no git | Files 2 `NO_GIT` |
| Step 4 a1-auditor.md paragraph | Files 3; grep check |
| Step 5 real run, whole output, measured runtime, never tune the mutation, not-HOLDS blocks merge | Checks (real run); Expected result |
| Step 6 full suite does not run real probes | Fit check (scripts/ not collected); test 7 makes no subprocess call; Expected result |
| Step 7 follow-ups (13 probes, CLI entry type, `--copy`, RI text renaming) | DROPPED: not built here, per 03; A1 opens them with `--next-id` |
| Missing inputs table (13 rows) | Guardrail tests, Missing inputs (one test per row) |
| Removed claim 01 D24 (str.count/replace) | No dependency; test 2 (c2) and the mutated != original check measure it |
| I1 additions C1-C13 | Listed above; each maps to a test in Tests and checks |
| Rule the person follows (001 slack, tolerance, cap) | n/a: no strategy rule changes. The a1-auditor.md text is a process rule and goes to the person in PR review (RULES BRANCH) |

## Guardrail tests
- Feasibility: anchor count == 1 (3 of 3, 03 step 1) → test 7 `test_shipped_probes_well_formed` pins the count per anchor on every suite run. The real run (step 5) re-measures it at `--ref`.
- Feasibility: baseline all-pass, 50 of 50 and 17 of 17 (03 step 2) → the real run's printed `baseline` lines must read `0 failed, 50 passed, 0 errors` and `0 failed, 17 passed, 0 errors`. Fixture (f) pins the red-baseline rule.
- Feasibility: targets exist, 3 of 3 → test 7 (`def <name>(` in each test file) and the real run (target in the baseline junit).
- Missing inputs: git on PATH → test 4 (which → None, exit 2)
- Missing inputs: `--ref` does not resolve → test 4 (`--ref nosuch`, exit 2)
- Missing inputs: scratch inside the repo → test 4 (tempfile.tempdir inside the fixture, exit 2)
- Missing inputs: probe file not in the commit → test 2 (k)
- Missing inputs: anchor count 0 / ≥ 2 → test 2 (c1, c2)
- Missing inputs: `module` not set → test 2 (b) has no module and still classifies. Its line has `code check: n/a`.
- Missing inputs: module import fails, or `__file__` is elsewhere → test 2 (i1, i2)
- Missing inputs: test_file absent → test 2 (l), `ERROR (baseline: pytest exit 4)`
- Missing inputs: baseline red or target not found → test 2 (f, e)
- Missing inputs: junit missing or unparseable → test 5
- Missing inputs: target not in mutated results → test 5
- Missing inputs: timeout → test 3
- Missing inputs: `recorded` not set → test 2 (o, folded into b), `recorded: none`
- Missing inputs (I1 addition): `PYTEST_ADDOPTS` set → test 1 (dropped and printed, and the counts are unchanged)

## Expected result
- `python3 -m pytest -q tests/test_probe_guardrails.py`: 9 passed (tests 1, 2, 3, 4×3, 5, 6, 7). Estimated ≈ 10 s: about 15 short child pytest runs at ~0.4 s each, plus git calls and the 1 s timeout. This is an estimate; I2 records the measured time.
- Full suite `python3 -m pytest -q`: the branch base count + 9 passed, with no new failure or skip. The base count includes 072's new tests/test_agent_tools.py if 072 is in the base, so 05 states the base it measured.
- Real run `python3 scripts/probe_guardrails.py` (ref HEAD of the branch):
  - `ref HEAD = <sha>`
  - `baseline tests/test_realtest.py: 0 failed, 50 passed, 0 errors`
  - `RI-002-063-leading-edge (RI-002): 9 failed, 41 passed, 0 errors; target ... failed: yes; HOLDS`
  - `RI-002-065-interior-gap (RI-002): 4 failed, 46 passed, 0 errors; ... HOLDS`
  - `baseline tests/test_diff_reports.py: 0 failed, 17 passed, 0 errors`
  - `RI-013-067-1b (RI-013): 1 failed, 16 passed, 0 errors; ... HOLDS`
  - `TOTAL: 3 probes, 3 hold, 0 not held, 0 anchor missing, 0 error`, exit 0
  - total ≈ 128 s (03 Self-check estimate; measured value in 05)

  If a measured count differs from `recorded`, 05 writes the measured count. Any line that is not HOLDS blocks the merge.
- Git state: no worktree is left (`git worktree list` shows 1), and the repo working tree is unchanged.

Recurring issues checked (item 013), against this plan:
- RI-001 (ESCALATED): there is no trading filter. The two selection rules (anchor count 1, baseline pass) have 03 counts (3 of 3; 50 of 50, 17 of 17) and tests that pin them (test 7, test 2 (f), real-run baseline lines).
- RI-002: every Missing-inputs row has an absent-case test, and none becomes HOLDS.
- RI-003: n/a.
- RI-004/005: the expected counts and the TOTAL line in test 2 are derived from the probe list (1 + 2 + 3 + 7 = 13).
- RI-006: no hand totals beyond that one, which is re-derived here.
- RI-007: Scope FULL, and I1 wrote no code.
- RI-008: test_safety covers the new files, and `delete=` is forbidden.
- RI-009: committed code only, via the worktree; README.md is flagged as shared with 072.
- RI-010: this item.
- RI-011: n/a.
- RI-012: junit and exit code only, C2.
- RI-013: whole result per probe, plus baseline lines.

Log fields: FIT WITH CHANGES | 4 files planned
