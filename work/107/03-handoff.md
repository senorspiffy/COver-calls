# 03 Research hand-off - 107
Status: READY (valid only once the orchestrator's check_handoff run below prints PASS)
Decision: Option B. Every mutant or probe run sets `PYTHONDONTWRITEBYTECODE=1` and `PYTHONPYCACHEPREFIX=<new empty dir>` on the command itself. `-B` and clearing `__pycache__` are described as not enough on their own. `-p no:cacheprovider` is labelled `.pytest_cache` hygiene, not a bytecode guard. Built as: one pinned sentence in the 4 rule files, a deterministic stale-.pyc test, a deterministic test of probe_guardrails' env, and a wider no-tracked-pyc test. No helper script. probe_guardrails.py logic is unchanged. Nothing in ccbot/ or config/ changes.

Recurring issues checked (item 013), open and ESCALATED entries:
- RI-001 (ESCALATED): there is no trading filter or window here. Each coverage claim in the map has a count I made with Grep/Glob on 2026-11-25. Python child sites that inherit the env: 12 of 12. Rule files with the sentence today: 0 of 4. `.pyc` files outside `__pycache__` in the main checkout: 0 of 56. I write no "every" or "always" without one of these counts.
- RI-014 (OPEN): no step reads git history or depends on clone depth. The new stale-.pyc test uses `tmp_path` only, not git. The tracked-pyc test keeps the existing `git ls-files` call (`test_no_tracked_pycache`, L213-216), and that call is not depth-dependent.
GUARDED entries also checked: RI-002 (Missing inputs: a stale case that does not reproduce, an unset prefix or a missing env-check line each give a named failure, never a pass); RI-004/005 (Self-check, including the same-size and same-second preconditions of the worked example); RI-006 (totals are left to check_handoff); RI-007 (Scope FULL, code goes through I1-I3, no 07 needed); RI-010 (this duty is agent text, so it gets a pinned-sentence test, a pasted env-check line and two deterministic tests; residual below); RI-012 (the new tests compare exact stdout `1`/`2` and pytest exit codes, never a substring of free text); RI-013 (this item's family: a result from a wrong run).

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| 01 F1: by default a .pyc stores the source mtime and size, checked on import | https://docs.python.org/3/reference/import.html §5.4.6 "storing the source's last-modified timestamp and size" | VERIFIED | |
| 01 F2: `source_mtime = int(st['mtime'])`; `_validate_timestamp_pyc` raises "bytecode is stale" only on a mtime or size mismatch (& 0xFFFFFFFF) | https://raw.githubusercontent.com/python/cpython/main/Lib/importlib/_bootstrap_external.py (fetched) | VERIFIED | |
| 01 F2a: a same-second, same-size mutant is not detected; this matches 101/05 L125 and 103/06 L24 | F2 + work/101/05-build-report.md L125, work/103/06-verification.md L24 (Read) | VERIFIED | |
| 01 F2b: same-size mutants are common (`<`→`>`, `==`→`!=`, one digit for another; 103 m4 "30 of 152"→"31 of 152") | 103/06 L24; byte counts 1=1, 2=2, 2=2 | VERIFIED | |
| 01 F3: a timestamp pyc header holds magic, timestamp and size | https://peps.python.org/pep-0552/ ("magic number, the source timestamp, and the source file size") | VERIFIED | |
| 01 F4: hash pycs exist (3.7+), checked ones are hashed, imports write timestamp pycs by default | import.html §5.4.6; PEP 552 "the current timestamp invalidation method will remain the default" | VERIFIED | |
| 01 F5: the module run from the command line is always recompiled and never cached | https://docs.python.org/3/tutorial/modules.html §6.1.3 | VERIFIED | |
| 01 F6: `-B` = no .pyc writing; PYTHONDONTWRITEBYTECODE is equivalent | https://docs.python.org/3/using/cmdline.html | VERIFIED | |
| 01 F7: `-B` stops writing only; get_code reads and validates the cached pyc, and `dont_write_bytecode` gates only `_cache_bytecode` | _bootstrap_external.py (fetched: "if (not sys.dont_write_bytecode and bytecode_path is not None and" before `_cache_bytecode`) | VERIFIED | |
| 01 F8: `sys.dont_write_bytecode` is set from -B / PYTHONDONTWRITEBYTECODE | https://docs.python.org/3/library/sys.html | VERIFIED | |
| 01 F9: a subprocess child inherits the parent env unless `env` is given | https://docs.python.org/3/library/subprocess.html ("the default behavior of inheriting the current process' environment") | VERIFIED | |
| 01 F10: `-B` does not reach a `[sys.executable, script]` child | cmdline.html says nothing about children (fetched); R1 marked it as inference | UNSUPPORTED | Removed. The map does not rely on it: the rule is the env var, which children inherit (F9) |
| 01 F10a: subprocess sites at test_pipeline_check L73, 643, 699, 2604, 2635, 3874, 3975, 5688; test_commit_step L65; test_diff_reports L12 | Grep `subprocess\.run\(\[sys\.executable` -A2 in tests/ (R3): exactly these 10, none passes a replacing env | VERIFIED | |
| 01 F10b / Numbers: "only the check_handoff one (L63) is known to import a project module" | Grep imports in scripts/ (R3): check_handoff.py L63 `import check_pipeline`, **and** commit_step.py L51 `from check_pipeline import LOG_LINE` | WRONG | Fixed: 2 of the 10 child scripts import scripts/check_pipeline.py: check_handoff (test_pipeline_check L3975, and L73 when `script` is check_handoff) and commit_step (test_commit_step L65). A stale `scripts/__pycache__/check_pipeline.*.pyc` exists in the main checkout (Glob). |
| 01 F11: pytest caches rewritten test modules; `sys.dont_write_bytecode = True` disables that | https://docs.pytest.org/en/stable/how-to/assert.html | VERIFIED | |
| 01 F12: installed pytest 9.1.1 rewrite.py L164 `write = not sys.dont_write_bytecode`, L176 `_read_pyc` unconditional, L368-391 int(st_mtime)/st_size check | /usr/local/lib/python3.13/dist-packages/_pytest/assertion/rewrite.py (Read); pytest-9.1.1.dist-info | VERIFIED | |
| 01 F12b: pytest main validates by source hash | https://raw.githubusercontent.com/pytest-dev/pytest/main/src/_pytest/assertion/rewrite.py (fetched: `importlib.util.source_hash`, flags `\x03`) | VERIFIED | |
| 01 F13: pytest's cache dir follows `sys.pycache_prefix`, else `__pycache__` | installed rewrite.py L1182-1193 (Read) | VERIFIED | |
| 01 F14: cacheprovider stores `.pytest_cache` (`cache/lastfailed`, `cache/nodeids`) | https://docs.pytest.org/en/stable/how-to/cache.html (`--cache-show` example) | VERIFIED | |
| 01 F15: `-p no:NAME` stops a plugin from loading | https://docs.pytest.org/en/stable/how-to/plugins.html | VERIFIED | |
| 01 F16: `-p no:cacheprovider` does not affect stale bytecode | R1: "neither page links" (docs silence only) | VERIFIED | Fixed (new source): the installed rewrite.py L1182-1193 puts rewritten pycs in `sys.pycache_prefix` or `__pycache__`, never `.pytest_cache`, and L164-185 write and read them with no reference to the cache plugin |
| 01 F17: with `sys.pycache_prefix` set, pycs are read from and written to the prefix tree and in-tree `__pycache__` is ignored; 3.8+ | sys.html ("write ... to (and read them from)", "Any `__pycache__` directories in the source code tree will be ignored", "Added in version 3.8"); cmdline.html | VERIFIED | |
| 01 F17b: project minimum Python 3.10 | pyproject.toml L9 `requires-python = ">=3.10"` | VERIFIED | |
| 01 F18: if the prefix is already set, deleting in-tree `__pycache__` does nothing | sys.html (F17) | VERIFIED | The map sets the prefix itself and prints `sys.pycache_prefix`, so an agent's preset value does not matter |
| 01 F19: 101/05 L125 first mutant pass without the env var gave wrong ids (same bytes, same second) | work/101/05-build-report.md L125 (Read) | VERIFIED | |
| 01 F20: 103/06 L24 m4 first `1 passed`, re-run `1 failed, 506 deselected in 0.19s` | work/103/06-verification.md L24 | VERIFIED | |
| 01 F21: 085/06 L40 M2 reused M1's .pyc | work/085/06-verification.md L40 | VERIFIED | |
| 01 F22: nothing in the pipeline flags a stale-.pyc survivor or kill | Grep .claude/ `DONTWRITEBYTECODE\|pycache\|PYCACHEPREFIX\|-B\b`: 0; Grep tests/test_probe_guardrails.py `DONTWRITE\|_child_env`: 0 | VERIFIED | |
| 01 F23: `git checkout HEAD -- <file>` rewrites the file with the current time | no git doc fetched (R1 UNVERIFIED); search gave mailing-list threads only | UNSUPPORTED | Removed. The map's test does not depend on restore timing: it sets the mtime itself with `os.utime` and asserts the precondition |
| 01 context: probe_guardrails `_child_env` sets PYTHONDONTWRITEBYTECODE=1 (L162-165), `-p no:cacheprovider` (L170), fresh `git worktree add --detach` (L345) | scripts/probe_guardrails.py (Read) | VERIFIED | |
| 01 context: A1 074 audit, env var removed → 2 / 1 / 2 failed over 3 runs | logs/audit/2026-11-18-074.md L59, L70 | VERIFIED | |
| 01 context: 080/07, 085/07, 101/07 ask for -B / env var / clearing; rule files i2 L19, i3 L14, a1 L38, run-item L21 name none | work/080/07 L6, 085/07 L5, 101/07 L5 (Grep); `git checkout HEAD -- ` sentence at i2 L19, i3 L14, a1 L38, run-item L21 | VERIFIED | |
| 01 Numbers: 3 hand-caught occurrences (085, 101, 103) between 2026-11-20 and 2026-11-25 | logs/audit/2026-11-20-085.md, 2026-11-24-101.md, 2026-11-25-103.md; 20..25 inclusive = 6 days | VERIFIED | |
| 01 Numbers: 10 `sys.executable` sites (8 + 1 + 1) | Grep (R3) | VERIFIED | |
| 01 Fit: no effect on capital or broker paths; no ccbot/ or config/ change | map below touches tests/, .claude/ only | VERIFIED | |
| 01 OQ3: the stale case can be made deterministic with `os.utime`; os.utime semantics UNVERIFIED | os.html was fetched twice and cut off before `os.utime` (95,378 chars) | UNSUPPORTED | Fixed: the test does not rely on the docs. After `os.utime(path, ns=(atime_ns, mtime_ns))` it asserts `int(st_mtime)` and `st_size` equal the originals, and that the unguarded control prints `1`. If either fails, the test fails with a named message and never passes |
| 01 OQ4: probe_guardrails is safe (fresh worktree, env var); `test_no_tracked_pycache` | probe_guardrails L162-165, L345; tests/test_pipeline_check.py L213-216; Glob `**/*.pyc` in main checkout: 56, all inside `__pycache__` | VERIFIED | Fixed (gap added): the test only rejects paths containing `__pycache__`, and .gitignore L11 ignores only `__pycache__/`, so a tracked sourceless `x.pyc` beside a source file would pass. Step 4 widens it to any `.pyc` |
| 01 OQ5: the .claude/ edits need the person's OK in PR review | request.md L13 | VERIFIED | |
| 02: no RI entry for stale bytecode; the 3 cases are not logged as RI-013 occurrences | logs/recurring-issues.md RI-013 (1 occurrence, 067) | VERIFIED | |
| 02: 074 audit L17 says rewrite.py L164 obeys `dont_write_bytecode`; L59/L70 quotes | logs/audit/2026-11-18-074.md | VERIFIED | |
| 02: audit guard mixes 080 L36, 085 L13, 101 L21/L28, 102 L29, 103 L37/L40 vary; no single recipe | Grep logs/audit (R3): each line matches as cited | VERIFIED | |
| 02: 2026-11-24.md L83 raised 107 | logs/audit/2026-11-24.md L83 | VERIFIED | |
| 02: no .pyc tracked (030): 2026-10-31 L37, 2026-11-01 L45 | logs/audit/2026-10-31.md L37, 2026-11-01.md L45 | VERIFIED | |
| 02: orchestrator fact, no PYTHONPYCACHEPREFIX in this container | orchestrator statement; R3 has no shell to check | UNSUPPORTED | Removed. The map does not depend on it: every command sets the prefix and prints `sys.pycache_prefix` |
| 02: every Python child gets no env or `{**os.environ, ...}` (test_commit_step L31, L66); probe_guardrails builds from os.environ | Grep `env=` (R3): test_commit_step L31 is a **git** child; L66 is the Python child; probe_guardrails L163 | WRONG | Fixed: Python children: 10 test sites (9 with no env, L65-66 with `{**os.environ, **IDENT}`) + probe_guardrails L174, L185 (`_child_env()` from os.environ) = 12 of 12 inherit the env. L31 is git and not relevant |
| 02: last cycle's languages French/Korean/Portuguese (104, L39); this cycle Russian/German/Italian | logs/research/2026-11-24.md L39, L17 | VERIFIED | |
| 02 FOR 1 zh-cn sys quote and translation | https://docs.python.org/zh-cn/3/library/sys.html (original matches; translation correct; same entry also says "并从中读取" = "and read from it") | VERIFIED | |
| 02 FOR 1: one setting covers the parent, the check_pipeline import children and pytest's rewriter | F9, F13, F17; 12 of 12 sites | VERIFIED | |
| 02 FOR 1 inference: with `dont_write_bytecode` on, the prefix dir stays empty, so one dir per session suffices | get_code gate (F7); pytest L164/L180; Grep tests/ scripts/ ccbot/ for `py_compile\|compileall`: 0 (test_safety L127 uses builtin `compile()`, which writes nothing) | VERIFIED | Step 2's test asserts the prefix dir is empty after the guarded run |
| 02 FOR 2: bpo-31772 quote, closed wont fix then reopened, fix not merged, "hash-based checking will not become the default" | https://bugs.python.org/issue31772 (fetched; open, patch "needs some more work on the test") | VERIFIED | |
| 02 FOR 2: 2024 discuss thread quotes | https://discuss.python.org/t/change-pyc-file-format-to-record-more-accurate-timestamp-and-other-information/57815 (2024-07-10; Zheaoli, MegaIng) | VERIFIED | |
| 02 FOR 2: hazard current on 3.10-3.13; 3.14+ UNVERIFIED | bpo open (above); no 3.14 source | UNSUPPORTED | Fixed: step 2's control case pins it. If a later Python stops reading the stale pyc, the control assertion fails with "stale case not reproduced" and the item is revisited. It is never a silent pass |
| 02 FOR 3: probe_guardrails owns the child env (L162-165), `module_file` pattern (L181-185) | scripts/probe_guardrails.py (Read) | VERIFIED | Not adopted as an `--env-check` flag. Step 3 pins `_child_env` with a deterministic test instead (less surface, AGAINST 1) |
| 02 FOR 3 ja `-B` quote and translation | https://docs.python.org/ja/3/using/cmdline.html | VERIFIED | |
| 02 AGAINST 1: guards asked only in per-item 07s, 101 and 103 still hit; .claude/ needs the person's OK | 080/085/101 07 lines (Grep); 101/05 L125; 103/06 L24; request L13 | VERIFIED | |
| 02 AGAINST 2: sourceless .pyc in the source dir imports when the .py is absent (it, ru quotes) | https://docs.python.org/it/3/tutorial/modules.html ("il modulo compilato deve essere nella directory sorgente e non deve esserci un modulo sorgente"); https://qna.habr.com/q/531673 | VERIFIED | |
| 02 AGAINST 2: PYTHONPYCACHEPREFIX does not change the sourceless lookup | R2 reasoning only; the fetched loader code shows SourcelessFileLoader but not the finder's search path | UNSUPPORTED | Fixed: the map makes no claim about it. Step 4 instead pins that no `.pyc` is tracked anywhere, and a fresh worktree has no untracked files |
| 02 AGAINST 2: pytest-remove-stale-bytecode quote | https://pypi.org/project/pytest-remove-stale-bytecode/5.0/ | VERIFIED | |
| 02 AGAINST 2: import checks `sys.modules` first (quote UNVERIFIED) | import.html §5.3.1 (fetched): "The first place checked during import search is `sys.modules`" | VERIFIED | Fixed: upgraded from UNVERIFIED with the quote |
| 02 AGAINST 2: UNCHECKED_HASH pycs are never validated (zh-cn quote); the delete or the prefix removes the risk, `-B` does not | https://docs.python.org/zh-cn/3/library/py_compile.html (original and translation correct); sys.html (F17); F7 | VERIFIED | |
| 02 AGAINST 3: probe_guardrails is already safe; a run_mutant.py would duplicate `_child_env` | L162-165, L345 | VERIFIED | No helper script is built |
| 02 AGAINST 3: extra seconds per guarded mutant run UNVERIFIED | none | UNSUPPORTED | Removed. No number is used anywhere |
| 02 AGAINST 3 / Holes: `-p no:cacheprovider` is `.pytest_cache` hygiene only | F16 | VERIFIED | |
| 02 table es: PYTHONDONTWRITEBYTECODE and PYTHONPYCACHEPREFIX quotes | https://docs.python.org/es/3.12/using/cmdline.html (originals match; translations correct) | VERIFIED | |
| 02 table ja Qiita: prefix is a mirrored tree; a reused dir can go stale if writing is on | https://qiita.com/ksato9700/items/da8df4e01b8b77293dbf (quote matches) + sys.html "read them from" | VERIFIED | |
| 02 table de: kanaries quote; no mention of 1-second resolution | https://docs.kanaries.net/de/topics/Python/pycache (quote matches; no same-second text) | VERIFIED | |
| 02 table it: "controlla la data di modifica ... completamente automatico" | https://docs.python.org/it/3/tutorial/modules.html (matches) | VERIFIED | |
| 02 table ru: "скрипт переданный интерпретатору непосредственно будет всегда компилироваться заново" | https://qna.habr.com/q/531673 (matches; consistent with F5) | VERIFIED | |

**Totals:** 68 rows checked → **56 VERIFIED as-is**, **8 fixed**, **4 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)

## Removed claims
- 01 F10: "`-B` does not reach a `[sys.executable, script]` child". No source says this; it is inference only. The rule uses the env var, which F9 supports.
- 01 F23: "`git checkout HEAD --` sets the current time". No source. The test sets the mtime itself.
- 02: "no PYTHONPYCACHEPREFIX in this container". This is the orchestrator's statement and R3 could not check it. Every command now sets the prefix and prints it.
- 02 AGAINST 3: "extra seconds per guarded run". Unmeasured, and no number is used.

## Implementation map
| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 1 | Rule text. In each of `.claude/commands/run-item.md` (after L21's scratch sentence), `.claude/agents/i2-builder.md` (L19), `.claude/agents/i3-verifier.md` (L14) and `.claude/agents/a1-auditor.md` (L38), add the sentence BYTECODE once, directly after the existing SCRATCH sentence. Leave SCRATCH unchanged. BYTECODE = "Every mutant or probe run (each `python3` or `python3 -m pytest` command on a mutated file) sets both `PYTHONDONTWRITEBYTECODE=1` and `PYTHONPYCACHEPREFIX=<pyc dir>` on the command itself, where `<pyc dir>` is a new dir made by the same mkdtemp command with prefix `pyc-` inside your scratch dir; child processes inherit both, so no `.pyc` in the source tree is read or written. `python3 -B` or a deleted `__pycache__` alone is not enough (`-B` stops writing, not reading, an existing `.pyc`), and `-p no:cacheprovider` only keeps `.pytest_cache` out; it is not a bytecode guard. If any command ran without `PYTHONDONTWRITEBYTECODE=1`, make a new `<pyc dir>`. Paste the output of `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<pyc dir> python3 -c 'import sys; print(sys.dont_write_bytecode, sys.pycache_prefix)'` (must be `True <pyc dir>`) above the mutant results in 05, 06 or the audit file (item 107)." The variables go on each command, not `export`, because shell state does not persist between agent bash calls. These edits need the person's OK in PR review. | 4 rule files; SCRATCH constant (tests/test_pipeline_check.py L5496-5504) | 4 edited rule files | New `test_bytecode_sentence_same_in_four_files` next to `test_scratch_sentence_same_in_four_files` (L5509): `text.count(BYTECODE) == 1` for each of SCRATCH_FILES, and the existing SCRATCH test still passes. Mutation: delete the sentence from one file → 1 failed | Rule files with the sentence today: 0 of 4 (Grep .claude/ `PYCACHEPREFIX\|DONTWRITEBYTECODE`, 2026-11-25). Python children that inherit both vars: 12 of 12 (10 test sites + probe_guardrails L174, L185; Grep 2026-11-25) |
| 2 | New `tests/test_stale_bytecode.py`. This is the "Done looks like" probe, deterministic and in `tmp_path`. Setup: write `m.py` = `X = 1\n` and `test_m.py` = `from m import X\ndef test_x():\n    assert X == 1\n`. Record `st = os.stat(m.py)`. Run the inner pytest once unguarded (`[sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"--rootdir={tmp}", "test_m.py"]`, cwd=tmp) with env = os.environ minus `PYTHONDONTWRITEBYTECODE`, `PYTHONPYCACHEPREFIX`, `PYTEST_ADDOPTS`; expect exit 0 and `tmp/__pycache__/m.*.pyc` to exist. Mutate: write `X = 2\n`, then `os.utime(m.py, ns=(st.st_atime_ns, st.st_mtime_ns))`. Precondition asserts: `int(os.stat(m.py).st_mtime) == int(st.st_mtime)` and size 6 == 6. Cases (each a fresh subprocess): (a) unguarded → exit 0 (stale read, false survivor; assertion message "stale case not reproduced on this Python (item 107)"); (b) `-B` only → exit 0; (c) `PYTHONDONTWRITEBYTECODE=1` only → exit 0; (d) guard = `PYTHONDONTWRITEBYTECODE=1` + `PYTHONPYCACHEPREFIX=<new mkdtemp under tmp_path>` → exit 1 (mutant killed), and the prefix dir is empty afterwards. Plus a plain-import variant of (a) and (d): `[sys.executable, "-c", "import m; print(m.X)"]` prints exactly `1` and exactly `2`. | Python 3.10+ (F17b); installed pytest | 1 new test file (5 asserted cases) | Suite passes. Mutation m1: drop `PYTHONPYCACHEPREFIX` from case (d)'s env → (d) exits 0 → test fails. Mutation m2: in setup, write `X = 22\n` (size 7) instead → the precondition assert fails (shows the size guard is pinned) | – |
| 3 | `tests/test_probe_guardrails.py`: add `test_child_env_disables_bytecode_writes`, which asserts `probe_guardrails._child_env()["PYTHONDONTWRITEBYTECODE"] == "1"` and `"PYTEST_ADDOPTS" not in` it (with `monkeypatch.setenv("PYTEST_ADDOPTS", "x")`). No change to probe_guardrails.py. | scripts/probe_guardrails.py L162-165 | 1 new test | Mutation m3: delete L164 → exactly this test fails, every run. A1 measured the current suite at 2 / 1 / 2 failed over 3 runs (074 audit L59), so the kill is now deterministic | – |
| 4 | `tests/test_pipeline_check.py::test_no_tracked_pycache` (L213-216): also assert that no tracked path ends in `.pyc` (sourceless legacy pycs, 02 AGAINST 2). | `git ls-files` | widened assert | Suite passes. Mutation m4: make the new filter always empty (`[]`) on a fixture list holding `ccbot/x.pyc` → it must fail. Or show in 05 that a scratch-worktree `git add -f ccbot/x.pyc` makes the test fail | .pyc files outside `__pycache__` in the main checkout: 0 of 56 (Glob `**/*.pyc`, 2026-11-25) |
| 5 | Process check for this item's own build. I2's 05 and I3's 06 paste step 1's env-check line, run m1-m4 under that guard, and paste results. | steps 1-4 | 05/06 lines | 05 and 06 each show `True <pyc dir>` before the mutant table, and m1-m4 each give ≥ 1 failed | – |
| Residual | Not built: no script checks that the env-check line is pasted in later 05/06 files (the RI-010 pattern). A1 watches the next 3 items with mutants. If one has no `True <pyc dir>` line, A1 opens an item for a check_pipeline rule. | – | – | A1 daily review | – |

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| `PYTHONPYCACHEPREFIX` on a mutant command (step 1) | The run counts as not guarded. Its mutant results are not evidence. The env-check line shows `None` instead of a path | env-check line must read `True <pyc dir>`; `None` → I3/A1 re-run the mutants |
| `PYTHONDONTWRITEBYTECODE` on a mutant command | The env-check shows `False`. The prefix dir may now hold pycs, so it must be replaced | "make a new `<pyc dir>`" (step 1 sentence) |
| Stale case does not reproduce (step 2 control (a), for example on a later Python) | Test fails, not skipped, not passed | `stale case not reproduced on this Python (item 107)` |
| mtime/size precondition after `os.utime` (step 2) | Test fails before any case runs | precondition assert names `int(st_mtime)` or size |
| `tmp/__pycache__/m.*.pyc` after the first unguarded run (step 2) | Test fails; the stale setup is not built | assert names the missing pyc path |
| Env-check line in a later 05/06 | Not checked by any script (Residual). A1 review only | n/a: no script check (Residual row) |
| python3.10/3.11 for `test_every_py_compiles_on_oldest_python` | Skips as today, and 05/06 say so (i3 step 2) | existing skip text |

## Self-check
Re-derive every numeric threshold in the map from that step's "How we check it" formula, and run every worked example against the trigger of the rule it shows. Show the arithmetic.
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Step 1 coverage: children inherit the env | sites with no `env` or `{**os.environ, ...}` / all Python child sites | tests: 9 no env + 1 `{**os.environ, **IDENT}` = 10; probe_guardrails `_child_env()` (built from os.environ) at L174, L185 = 2; 10 + 2 = 12 of 12 | Matches Feasibility |
| Step 1 sentence count | `text.count(BYTECODE) == 1` per file | 4 files × 1 = 4; today 0 of 4 | Consistent |
| Step 2 worked example, same-size trigger | stale iff stored size == `st_size` and stored mtime == `int(st_mtime)` (F2, F12 L368/L385/L389) | `X = 1\n` = 6 bytes, `X = 2\n` = 6 bytes, so 6 == 6. utime with `ns=` restores st_mtime_ns, so int(mtime) is equal. Both hold → stale under (a), (b), (c) | (a)/(b)/(c) exit 0, plain import prints `1` |
| Step 2 guard case | prefix set → in-tree `__pycache__` ignored (F17); prefix dir empty → compile from source; `dont_write_bytecode` → nothing written (F7, pytest L164/L180) | source X = 2; test asserts `X == 1` → 2 ≠ 1 → 1 failed → pytest exit 1; prefix file count 0 after the run | (d) exit 1, prints `2`, dir empty |
| Step 2 m2 | size 7 ≠ 6 | `X = 22\n` = 7 bytes | precondition fails, as intended |
| Step 2 why (b) and (c) are stale | `-B` / env var gate only `_cache_bytecode`; the read is unconditional (F7, pytest L176) | the existing `__pycache__/m.*.pyc` is still read | exit 0 in both, which pins "not enough on its own" |
| Step 3 determinism | `_child_env()["PYTHONDONTWRITEBYTECODE"] == "1"` is pure, with no subprocess | m3 removes L164 → KeyError/assert fails every run (1 of 1), against 2/1/2 over 3 timed runs today | Deterministic kill |
| Step 4 | tracked paths ending `.pyc` == [] | 0 of 56 local `.pyc` outside `__pycache__` (Glob); tracked `__pycache__` = 0 (030) | Passes on HEAD |
| Occurrence window (01 Numbers) | days from 2026-11-20 to 2026-11-25 inclusive | 25 − 20 + 1 = 6 | "within 6 days" holds |
| Premium / yield / breakeven | n/a: no trading figure in this item | – | – |

`check_handoff output (run by the orchestrator 2026-11-25 23:42 UTC, exit 0; must say PASS):`
```
sources count (unique URLs in 01-research.md): 11
fact-check rows: 68
totals line: 68 rows -> 56 as-is, 8 fixed, 4 removed
PASS
```

R3 log line: not written. R3 has no shell. After check_handoff prints PASS, the orchestrator runs `python3 scripts/check_pipeline.py --log R3 107 "<as-is> verified, <fixed> fixed, <removed> removed | READY"`, taking the counts from check_handoff's `totals line:`.
