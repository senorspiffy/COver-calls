# 04 Build plan - 107
Fit verdict: FIT WITH CHANGES

Fit check. No trading, capital or broker path is touched: nothing in ccbot/ or config/ changes, so the ~$3k account and the 001 strategy rules are unaffected. There is no conflict with built code. scripts/probe_guardrails.py already sets `PYTHONDONTWRITEBYTECODE=1` in `_child_env` and uses a fresh `git worktree add --detach`, and this plan leaves its logic unchanged. The SCRATCH sentence (091, 097) stays as it is, and the new sentence goes directly after it. The changes are small hardening edits to the 03 map, listed below and marked "(I1 change)". None changes a rule's meaning:
1. Step 2's inner pytest runs from a source dir that holds its own empty `pytest.ini`, with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`. Its env also drops `PYTHONSAFEPATH`. The stale case then cannot depend on whatever config, plugins or path flags the outer run happens to have (Extra research 1, 2, 4).
2. Step 2's "prefix dir is empty" is asserted as "no files under the prefix dir". An empty subfolder holds no bytecode and is not what the guard protects against.
3. Step 4's mutation m4 becomes a pure fixture test of a small helper (`_tracked_bytecode`). 03 left it as "on a fixture list ... or a scratch `git add -f`", and the pure test kills it the same way on every run.

Rule/agent file edits (FLAG for the person's OK in PR review, request.md L13): `.claude/commands/run-item.md`, `.claude/agents/i2-builder.md`, `.claude/agents/i3-verifier.md`, `.claude/agents/a1-auditor.md`.

Today's items 105/108/109/110 also change `tests/test_pipeline_check.py` (and `scripts/check_pipeline.py`, which this item does not touch). Builds run one at a time. I2 places every edit by the text anchors named below, never by line number, and re-reads the file at build time.

Recurring issues checked (item 013). I read logs/recurring-issues.md first and checked this plan against each entry:
- RI-001 (ESCALATED): this item has no trading filter or window. Each coverage count in 03 has a pin or a stated residual.
  - BYTECODE sentence in the 4 rule files: 0 of 4 today. `test_bytecode_sentence_same_in_four_files` pins 4 of 4 after the build.
  - Tracked `.pyc` outside `__pycache__`: 0 of 56 local files. Pinned by the widened `test_no_tracked_pycache`.
  - Python children that inherit the env: 12 of 12. Only the 2 probe_guardrails sites are pinned, by `test_child_env_disables_bytecode_writes`. The 10 test sites have a dated count but no test (Residual 2 below).
  - I state no "every" or "always" beyond these counts.
- RI-014 (OPEN): no new step reads git history. `test_no_tracked_pycache` keeps its existing `git ls-files` call, which does not depend on clone depth. The new helper test and the stale-bytecode tests use only `tmp_path`.
- GUARDED entries also checked:
  - RI-002: each of these gives a named failure, never a pass:
    - a stale case that does not reproduce
    - a missing in-tree pyc after setup
    - a failed mtime/size precondition
    - `None` or `False` on the env-check line
  - RI-004/005: the worked example is re-derived (6 == 6 bytes; `X = 22\n` = 7 bytes for m2).
  - RI-006: totals are left to check_handoff.
  - RI-007: Scope FULL, so I2/I3/A1 all run.
  - RI-010: the env-check paste is agent text only. Residual 1, A1 watches it.
  - RI-012: tests compare exact stdout (`"1"`, `"2"` after `.strip()`) and pytest return codes (0/1), never a substring.
  - RI-013: this is the item's own family. Guarded mutant runs are a precondition for results.
  - RI-003, RI-008, RI-009, RI-011: not touched. For RI-008, I3 compiles the new test file with python3.10/3.11 via the existing test.

## Extra research (with sources)
1. pytest config discovery. pytest looks for config files "in the ancestor directory and upwards" from the args' common ancestor, and "`pytest.ini`: will always match and take precedence ... even if empty". If none is found, it falls back to `setup.py` and other searches (https://docs.pytest.org/en/stable/reference/customize.html). An empty `pytest.ini` (`[pytest]\n`) written into the inner source dir therefore makes the inner run's rootdir and configfile deterministic, wherever the basetemp lives. This is (I1 change) 1.
2. Plugin autoload. "If you want to disable plugins from loading automatically ... you can use --disable-plugin-autoload or PYTEST_DISABLE_PLUGIN_AUTOLOAD" (https://docs.pytest.org/en/stable/how-to/plugins.html). The inner run needs no third-party plugin. Turning autoload off removes one source of environment-dependent behaviour (an installed plugin's own import hooks or caches).
3. SOURCE_DATE_EPOCH. py_compile's default becomes `CHECKED_HASH` "if the `SOURCE_DATE_EPOCH` environment variable is set" (https://docs.python.org/3/library/py_compile.html). That page names only `py_compile.compile` and says nothing about the import system's own writes. 03 F4 (PEP 552: timestamp "will remain the default") covers imports. No test or script here calls py_compile or compileall (03 row "FOR 1 inference": Grep 0). So the stale case targets `m.py`, which is loaded by a plain import, and not the pytest-rewritten test module. That keeps it independent of pytest's own move to source-hash validation (03 F12b). I2 does not strip SOURCE_DATE_EPOCH. If a future environment ever made import write hash pycs, control (a) would fail with "stale case not reproduced", which is the intended loud failure.
4. `PYTHONSAFEPATH` (3.11+) stops `-c` from putting the cwd on `sys.path`, so `import m` would fail with ImportError and not with a wrong value. This is an edge case R3 missed. The inner env drops it (I1 change 1). On 3.10 the variable does not exist, and dropping it does nothing. This is inference from the variable's documented purpose (https://docs.python.org/3/using/cmdline.html, PYTHONSAFEPATH entry, the same page as 03 F6). I did not re-fetch the page for this item.

## Files to create/change
1. `.claude/commands/run-item.md` (FLAG: person's OK). Insert the BYTECODE sentence (exact text of 03 step 1, quoted in full there) once, directly after the SCRATCH sentence's closing text `never in the main checkout (items 091, 097).`, separated by one space on the same line. Change nothing else.
2. `.claude/agents/i2-builder.md` (FLAG). Same insertion at the same anchor.
3. `.claude/agents/i3-verifier.md` (FLAG). Same insertion at the same anchor. It lands before `05 (I2) / 06 (I3) has one column-0 \`Scratch dir:` ..., and that sentence keeps its count of 1.
4. `.claude/agents/a1-auditor.md` (FLAG). Same insertion at the same anchor.
5. `tests/test_pipeline_check.py`:
   - (a) Directly after `def test_scratch_sentence_same_in_four_files():` and its body, add the constant `BYTECODE = (...)`. It is the exact 03 step 1 sentence, as concatenated string literals in the style of `SCRATCH`, and it ends `(item 107).` Then add `test_bytecode_sentence_same_in_four_files()`: for f in `SCRATCH_FILES`, `(REPO / f).read_text(encoding="utf-8").count(BYTECODE) == 1, f`. It also asserts that `"PYTHONPYCACHEPREFIX" in BYTECODE` and `"PYTHONDONTWRITEBYTECODE=1" in BYTECODE`, so the constant cannot be emptied.
   - (b) In place, at `def test_no_tracked_pycache():`: add a module-level helper `_tracked_bytecode(paths)` that returns `[p for p in paths if "__pycache__" in p or p.endswith(".pyc")]`. The test asserts `_tracked_bytecode(files.splitlines()) == []` and gets a docstring note "item 107: sourceless .pyc too".
   - (c) Directly after it, add `test_tracked_bytecode_helper()`: `_tracked_bytecode(["ccbot/x.pyc", "ccbot/__pycache__/a.cpython-313.pyc", "ccbot/a.py", "docs/pyc.md"]) == ["ccbot/x.pyc", "ccbot/__pycache__/a.cpython-313.pyc"]`.
6. `tests/test_stale_bytecode.py` (new, about 70 lines). Module docstring: item 107, RI-013 family, the 03 worked example.
   - `_env(**extra)`: `os.environ` minus `PYTHONDONTWRITEBYTECODE`, `PYTHONPYCACHEPREFIX`, `PYTEST_ADDOPTS`, `PYTHONSAFEPATH`, plus `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, then `extra`.
   - `_pytest(src, env, *pre)`: runs `subprocess.run([sys.executable, *pre, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"--rootdir={src}", "test_m.py"], cwd=src, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)`.
   - `_import_x(src, env)`: runs `[sys.executable, "-c", "import m; print(m.X)"]` with cwd=src and returns stdout `.strip()`.
   - `_stale(tmp_path)` makes `src = tmp_path / "src"`, then:
     1. Write `src/pytest.ini` = `[pytest]\n`, `src/m.py` = `X = 1\n` and `src/test_m.py` = `from m import X\ndef test_x():\n    assert X == 1\n`.
     2. Take `st = os.stat(m.py)`.
     3. Make an unguarded run (`_env()`) and assert `returncode == 0`.
     4. Assert `list((src/"__pycache__").glob("m.*.pyc"))` is non-empty (message "setup wrote no src/__pycache__/m.*.pyc (item 107)").
     5. Write `X = 2\n`, then call `os.utime(m, ns=(st.st_atime_ns, st.st_mtime_ns))`.
     6. Assert `int(os.stat(m).st_mtime) == int(st.st_mtime)` (message names `int(st_mtime)`), and that `os.stat(m).st_size == st.st_size == 6` (message names `size`).
     7. Return src.
   - `test_stale_pyc_survives_without_full_guard(tmp_path)`:
     - (a) Unguarded `_env()`: exit 0, message "stale case not reproduced on this Python (item 107)", and `_import_x` == `"1"`.
     - (b) `-B` only (`pre=("-B",)`, `_env()`): exit 0.
     - (c) `_env(PYTHONDONTWRITEBYTECODE="1")`: exit 0.
   - `test_guard_kills_stale_mutant(tmp_path)`:
     - (d) `prefix = tmp_path / "pyc-guard"`, created empty, a sibling of `src` and never under it. Run with `_env(PYTHONDONTWRITEBYTECODE="1", PYTHONPYCACHEPREFIX=str(prefix))`: exit 1, `_import_x` == `"2"` under the same env, and `[p for p in prefix.rglob("*") if p.is_file()] == []`.
7. `tests/test_probe_guardrails.py`: add `test_child_env_disables_bytecode_writes(monkeypatch)` after `test_shipped_probes_well_formed`. It calls `monkeypatch.setenv("PYTEST_ADDOPTS", "x")` and `monkeypatch.delenv("PYTHONDONTWRITEBYTECODE", raising=False)`, then sets `env = pg._child_env()`. It asserts `env["PYTHONDONTWRITEBYTECODE"] == "1"` and `"PYTEST_ADDOPTS" not in env`. It has no git, so no `@NO_GIT`.

No change to scripts/probe_guardrails.py, scripts/check_pipeline.py, ccbot/ or config/. No helper script.

## Tests and checks
I2 runs every mutant under the guard of the BYTECODE sentence. The mkdtemp `pyc-` dir sits inside I2's own scratch dir. The env-check line, which must read `True <pyc dir>`, is pasted above the mutant table in 05. I3 does the same in 06 with its own new dir. Mutations run in a scratch `git worktree add --detach`, never in the main checkout:
- m0: delete the BYTECODE sentence from one of the 4 rule files. Expect `test_bytecode_sentence_same_in_four_files` 1 failed.
- m1: in `test_guard_kills_stale_mutant`, drop `PYTHONPYCACHEPREFIX` from case (d)'s env. (d) then exits 0, and the test fails.
- m2: in `_stale`, write `X = 22\n` in place of `X = 2\n`. The size precondition fails, with a message naming `size`. Both stale tests fail.
- m3: in scripts/probe_guardrails.py, delete the line `env["PYTHONDONTWRITEBYTECODE"] = "1"`. Expect `test_child_env_disables_bytecode_writes` 1 failed. Repeat 3 times; it must fail on each run.
- m4: in `_tracked_bytecode`, drop `or p.endswith(".pyc")`. Expect `test_tracked_bytecode_helper` 1 failed.
- Full suite at HEAD: green. I2 pastes the pytest summary line as printed, with the before and after counts. There are 5 new test functions: 2 in test_stale_bytecode.py, 1 in test_probe_guardrails.py, and 2 in test_pipeline_check.py (the sentence test and the helper test). The total should rise by 5 on top of whatever 105/108/109/110 add.
- `test_stale_bytecode.py` wall time: I2 reports it. It is unmeasured, so no number is promised here.
- `python3 scripts/check_pipeline.py`: the line for 107 is not SKIPPED or INCOMPLETE. `RULES BRANCH` is expected to name the 4 rule files, and that is the FLAG above.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Decision: Option B, env vars on the command, `-B`/clear not enough, `-p no:cacheprovider` = `.pytest_cache` hygiene | Files 1-4 (BYTECODE sentence, exact 03 text); test 5(a) |
| Step 1: BYTECODE sentence once in 4 files, after SCRATCH, SCRATCH unchanged | Files 1-4; 5(a) `test_bytecode_sentence_same_in_four_files`; existing `test_scratch_sentence_same_in_four_files` still passes; m0 |
| Step 1: variables on each command, not `export` | It is inside the BYTECODE text (Files 1-4) |
| Step 1: edits need the person's OK | FLAG line at the top; PR review |
| Step 2: stale-pyc test in tmp_path, unguarded setup, `os.utime` mutation, precondition asserts | File 6 `_stale`; m2 |
| Step 2: cases (a) unguarded, (b) `-B`, (c) env var only → exit 0 | File 6 `test_stale_pyc_survives_without_full_guard` |
| Step 2: case (d) full guard → exit 1, prefix dir empty | File 6 `test_guard_kills_stale_mutant`. "Empty" is asserted as no files (I1 change 2) |
| Step 2: plain-import variant prints exactly `1` / `2` | File 6, `_import_x` in both tests |
| Step 2: env strips PYTHONDONTWRITEBYTECODE, PYTHONPYCACHEPREFIX, PYTEST_ADDOPTS | File 6 `_env`. It also strips PYTHONSAFEPATH and sets PYTEST_DISABLE_PLUGIN_AUTOLOAD=1, with an empty pytest.ini (I1 change 1) |
| Step 2: m1 drop prefix → fail | Tests and checks m1 |
| Step 3: `_child_env` test, PYTHONDONTWRITEBYTECODE == "1", PYTEST_ADDOPTS absent; probe_guardrails.py unchanged | File 7; m3 ×3 |
| Step 4: widen `test_no_tracked_pycache` to any `.pyc` | File 5(b) |
| Step 4: m4 fixture list or scratch `git add -f` | File 5(c) pure helper test; m4 (I1 change 3). The `git add -f` variant is DROPPED: the pure test kills the same mutant deterministically, with no git state |
| Step 5: 05 and 06 paste `True <pyc dir>` and run m1-m4 under the guard | Tests and checks, first paragraph (plus m0) |
| Residual: no script checks the env-check paste; A1 watches the next 3 items with mutants | Kept as Residual 1. No build |
| Missing inputs table (7 rows) | Guardrail tests below |
| Removed claims F10, F23, container prefix, extra seconds | Not used anywhere in this plan |

No code here changes a rule the person follows (001: slack, tolerance, cap). n/a.

## Guardrail tests
- Feasibility: sentence in 4 of 4 rule files (03: 0 of 4 on 2026-11-25) → `test_bytecode_sentence_same_in_four_files`; m0.
- Feasibility: tracked `.pyc` outside `__pycache__` = 0 (03: 0 of 56 local on 2026-11-25) → widened `test_no_tracked_pycache` + `test_tracked_bytecode_helper`; m4.
- Feasibility: probe_guardrails children inherit the guard (2 of the 12 sites, L174/L185) → `test_child_env_disables_bytecode_writes`; m3.
- Feasibility: stale case reproduces on this Python (same-size, same-second) → control (a) in `test_stale_pyc_survives_without_full_guard`. It fails loudly if a later Python stops reading the pyc.
- Missing inputs: `PYTHONPYCACHEPREFIX` absent on a mutant command → m1 shows the mutant survives without it (case (d) minus prefix = exit 0). The env-check line reads `None` → I3/A1 re-run. Not script-checked (Residual 1).
- Missing inputs: `PYTHONDONTWRITEBYTECODE` absent → cases (a) and (b) show what happens. The env-check reads `False` → "make a new `<pyc dir>`" (sentence text, pinned by 5(a)).
- Missing inputs: stale case does not reproduce → (a) fails with "stale case not reproduced on this Python (item 107)". It is not skipped.
- Missing inputs: mtime/size precondition fails → `_stale` asserts, with messages naming `int(st_mtime)` / `size`; m2.
- Missing inputs: no `src/__pycache__/m.*.pyc` after setup → `_stale` assert. This also catches an outer `PYTHONPYCACHEPREFIX` leaking in, which `_env` strips.
- Missing inputs: env-check line absent in a later 05/06 → no test (Residual 1, A1 review).
- Missing inputs: python3.10/3.11 absent → `test_every_py_compiles_on_oldest_python` skips as today; 06 says so.
- Residual 2 (new, I1): the 10 `[sys.executable, ...]` test sites inherit the env today (03: 9 with no `env`, 1 with `{**os.environ, **IDENT}`). No test stops a future site from passing a replacing `env=` that drops the guard. A text-match test would be fragile (RI-012), and an AST walker is out of scope for this item. A1 notes it with Residual 1. If either recurs, a request is opened.

## Expected result
- The 4 rule files each hold the BYTECODE sentence exactly once, right after SCRATCH. These need the person's OK in PR review.
- 3 test files change: `tests/test_stale_bytecode.py` is new, and `tests/test_probe_guardrails.py` and `tests/test_pipeline_check.py` are edited. There are 5 new test functions. The full suite is green.
- `test_guard_kills_stale_mutant` shows the request's "Done looks like": with a same-size, same-second stale `.pyc` present, the guarded run kills the mutant (exit 1, prints `2`) and writes nothing. The unguarded, `-B`-only and env-var-only runs falsely survive (exit 0, prints `1`).
- m0-m4 each give ≥ 1 failed under the guard (m3 on 3 of 3 runs), with `True <pyc dir>` pasted above the table in 05 and 06.
- No change to ccbot/, config/, scripts/. `check_pipeline.py` line for 107 is not SKIPPED or INCOMPLETE.

Log fields: FIT WITH CHANGES | 7 files planned
