# 01 Research brief - 107
## Question
Mutation probes run by I2, I3 and A1 have twice reported a wrong result because Python, or pytest's assertion rewriter, loaded a stale compiled file (work/101/05 L125, work/103/06 L24; also work/085/06 L40). What exact settings make sure a probe never reads stale bytecode? Do `python3 -B`, `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider` and clearing `__pycache__` each do what the request assumes? What test shows "a probe with a stale .pyc shows the mutant killed"?

Recurring issues read first: RI-013 family (results from a wrong run), named in the request. RI-010 and RI-012 are not affected. No earlier item covers this. Related lessons already in the repo:
- 074 (scripts/probe_guardrails.py L162-171) sets `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider` for every child, and runs in a fresh `git worktree add --detach`.
- A1's 074 audit (logs/audit/2026-11-18-074.md L59, L70) measured that removing the env var makes the kill timing-dependent (2 / 1 / 2 failed over 3 runs).
- 080/07, 085/07 and 101/07 already ask for `-B` / `PYTHONDONTWRITEBYTECODE=1` / a cleared `__pycache__`, but only in per-item audit tasks. None of the agent files (i2-builder.md L19, i3-verifier.md L14, a1-auditor.md L36-38, run-item.md L21) names any of them (Grep of .claude/ for `DONTWRITEBYTECODE|pycache|-B`: 0 hits).

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
How Python decides that a .pyc is current:
1. By default a .pyc stores the source's last-modified timestamp and size. On import, Python checks that stored metadata against the source file's metadata [https://docs.python.org/3/reference/import.html].
2. CPython takes the source mtime as `int(st['mtime'])`, so only whole seconds count. `_validate_timestamp_pyc` raises "bytecode is stale" only if the stored mtime differs from `source_mtime & 0xFFFFFFFF`, or the stored size differs from `source_size & 0xFFFFFFFF` [https://raw.githubusercontent.com/python/cpython/main/Lib/importlib/_bootstrap_external.py].
   - So a mutant written in the same wall-clock second as the run that wrote the .pyc, and with the same byte count, is not detected as changed. That matches the cause given in 101/05 L125 and 103/06 L24.
   - Same-size edits are the common mutant shape: `<` to `>`, `==` to `!=`, one digit for another ("30 of 152" to "31 of 152" in 103 m4).
3. A timestamp-based pyc header holds the magic number, the source timestamp and the source size [https://peps.python.org/pep-0552/].
4. Hash-based .pyc files (Python 3.7+) store a hash of the source instead. "Checked" ones are validated by hashing the source [https://docs.python.org/3/reference/import.html]. But imports write timestamp pycs by default, so this does not help unless the pycs are built deliberately (finding 1).
5. Python always recompiles, and never caches, the module loaded directly from the command line [https://docs.python.org/3/tutorial/modules.html]. So `python3 scripts/x.py` never runs a stale x.py. Modules that x.py imports can still be stale.

What `-B` and `PYTHONDONTWRITEBYTECODE` do and don't do:
6. `-B`: "Python won't try to write .pyc files on the import of source modules." `PYTHONDONTWRITEBYTECODE` set to a non-empty string is equivalent [https://docs.python.org/3/using/cmdline.html].
7. Both stop only the writing. `SourceLoader.get_code` reads and validates the cached .pyc first, and checks `sys.dont_write_bytecode` only before `_cache_bytecode` [https://raw.githubusercontent.com/python/cpython/main/Lib/importlib/_bootstrap_external.py]. So **`-B` alone does not protect against a .pyc that already exists.** It protects only when no .pyc for the mutated file exists before the run (for example a fresh worktree, or one whose `__pycache__` was just removed).
8. `sys.dont_write_bytecode` is set from `-B` / `PYTHONDONTWRITEBYTECODE` [https://docs.python.org/3/library/sys.html].
9. A `subprocess.run` child inherits the parent's environment unless `env` is given [https://docs.python.org/3/library/subprocess.html]. So `PYTHONDONTWRITEBYTECODE=1` reaches children that tests spawn.
10. `-B` is a command-line option of one interpreter, so it does not reach a child started as `[sys.executable, script]` [https://docs.python.org/3/using/cmdline.html]. This is an inference: the page documents per-invocation options and does not discuss children.
   - It matters here. tests/test_pipeline_check.py L73, L643, L699, L2604, L2635, L3874, L3975 and L5688, tests/test_commit_step.py L65 and tests/test_diff_reports.py L12 run scripts with `[sys.executable, ...]`.
   - scripts/check_handoff.py L63 does `import check_pipeline`. A check_pipeline mutant exercised through the check_handoff subprocess (test_pipeline_check.py L3975) can therefore read `scripts/__pycache__/check_pipeline.*.pyc` under `python3 -B -m pytest` unless the env var is set as well.

pytest's own cache of test files:
11. pytest writes rewritten test modules back to disk for caching. `sys.dont_write_bytecode = True` disables that caching [https://docs.pytest.org/en/stable/how-to/assert.html].
12. In the installed pytest 9.1.1 (/usr/local/lib/python3.13/dist-packages/_pytest/assertion/rewrite.py):
   - L164: `write = not sys.dont_write_bytecode`.
   - L176: `_read_pyc` is still called unconditionally.
   - L368-391: the cached file is out of date only if `int(st_mtime)` or `st_size` differ.
   So mutating a test file (for example a probe that edits a test) has the same whole-second / same-size hazard, and `-B` again stops only the writing. Local file, read by R1. No URL for this version. pytest's main branch now checks a source hash instead [https://raw.githubusercontent.com/pytest-dev/pytest/main/src/_pytest/assertion/rewrite.py], but that is not the installed version.
13. pytest puts these files under `sys.pycache_prefix` when it is set, otherwise in `__pycache__` next to the file (installed rewrite.py L1182-1193, local).

`-p no:cacheprovider` (named in the request):
14. `cacheprovider` is pytest's cache plugin. It stores `.pytest_cache` data such as `cache/lastfailed` and `cache/nodeids` [https://docs.pytest.org/en/stable/how-to/cache.html].
15. `-p no:NAME` stops a plugin from loading [https://docs.pytest.org/en/stable/how-to/plugins.html].
16. Neither page links the cache plugin to .pyc files. **`-p no:cacheprovider` therefore does not affect stale bytecode.** It only keeps `.pytest_cache` out of the scratch tree and prevents `--lf`/`--ff` ordering. It is worth keeping, but agent text should not describe it as the bytecode guard.

A stronger option than deleting `__pycache__`:
17. When `sys.pycache_prefix` is set (`PYTHONPYCACHEPREFIX` or `-X pycache_prefix=PATH`, Python 3.8+), Python reads and writes .pyc files in that parallel tree, and "Any `__pycache__` directories in the source code tree will be ignored" [https://docs.python.org/3/library/sys.html], [https://docs.python.org/3/using/cmdline.html].
   - So `PYTHONPYCACHEPREFIX=<new empty dir per run>` makes every in-tree stale .pyc irrelevant, for the parent and for every child that inherits the env (finding 9).
   - pytest's rewriter follows it too (finding 13).
   - The project's minimum is Python 3.10 (RI-008, pyproject.toml), so 3.8+ is satisfied.
18. Interaction to note: if `PYTHONPYCACHEPREFIX` is already set in an agent's environment, the caches live there and deleting in-tree `__pycache__` does nothing [https://docs.python.org/3/library/sys.html]. A guard that only deletes `__pycache__` should check `sys.pycache_prefix` is None, or set the prefix itself. UNVERIFIED whether any agent environment sets it: R1 has no shell.

Repo evidence (local files, no URL):
19. work/101/05 L125: the first mutant pass without `PYTHONDONTWRITEBYTECODE` gave wrong ids for M-rh and K-suite, because each mutant changed the same number of bytes as its predecessor within the same second.
20. work/103/06 L24: m4 first gave `1 passed`, because the sed ran in the same second as the previous restore with an unchanged size. After a re-run it gave `1 failed`.
21. work/085/06 L40: M1 and M2 were same-size edits within one second, so M2 reused M1's .pyc.
22. All three were caught by hand. Nothing in the pipeline would have flagged a mutant that "survives" because of a stale .pyc. A false survivor reads as a test gap, and a false kill (stale bytecode from an earlier mutant) reads as a guardrail that holds. The second is the dangerous direction for RI-013.
23. `git checkout HEAD -- <file>` (the restore rule in i2/i3/a1, items 091/097) rewrites the file with the current time. The next sed in the same second then matches that mtime. This is consistent with 103/06 L24. UNVERIFIED as a general git guarantee: git docs not fetched.

## Numbers used (show the math)
- Stale window: the stored mtime is whole seconds (finding 2). A mutant is read stale only if it was written in the same second as the source the cached .pyc was compiled from, and has the same byte size. A sed edit and restore take well under 1 s (103/06 m4: `1 failed, 506 deselected in 0.19s` for the whole run), so back-to-back same-size mutants land in that window often. Measured flake rate: A1 got 2 / 1 / 2 failed over 3 runs with the env var removed (logs/audit/2026-11-18-074.md L59). That is 3 runs, not a rate. No larger sample exists.
- Occurrences caught by hand: 3 (085, 101, 103), each in a different item within 6 days (2026-11-20 to 2026-11-25).
- Subprocess sites in tests that `-B` alone would not cover: 8 in test_pipeline_check.py + 1 in test_commit_step.py + 1 in test_diff_reports.py = 10 (Grep `sys\.executable` count: 8 + 1 + 1 = 10). Of these, only the check_handoff one is known to import a project module (check_handoff.py L63). The others run a script as `__main__`, which is never cached (finding 5), unless that script imports a sibling. R1 did not check every script's imports.

## Fit for a ~$3k account
- No effect on capital, positions, caps, assignment, dividends, taxes, commissions or liquidity. This is a process and test-harness change only: nothing in ccbot/ or config/ and no broker path.
- It protects the account indirectly. The guardrail probes (RI-002 earnings/dividend unknowns, cap checks) are what stop the bot from selling into an unknown earnings date or past the $3k cap. A probe that reports HOLDS because of a stale .pyc would hide a removed guardrail.

## Open questions
1. Which guard should the agent text name?
   - Option A, the request's: `PYTHONDONTWRITEBYTECODE=1` + `python3 -B` + remove every `__pycache__` in the scratch worktree before each mutant run.
   - Option B: `PYTHONDONTWRITEBYTECODE=1` + `PYTHONPYCACHEPREFIX=<new empty dir per run>`, which ignores in-tree `__pycache__` (finding 17) and needs no recursive delete.
   - A alone with `-B` but no env var misses children (finding 10). `-B` alone without clearing misses pre-existing pycs (finding 7). `-p no:cacheprovider` is not a bytecode guard (finding 16).
   - R2 and R3 to weigh. R1 recommends the agent text name the env var and the clear/prefix step, with `-B` as optional, so the rule doesn't rest on the weaker flag.
2. Helper or text only? A small helper, for example `scripts/run_mutant.py <worktree> -- <pytest args>`, could set the env, use a fresh prefix dir, refuse if `sys.pycache_prefix` is already set to something else, and print the settings into 05/06. That would make the setting checkable (RI-010 lesson: duties only in agent text get skipped). It is not required by "Done looks like".
3. Shape of the "Done looks like" probe, proposed and not built. R1 has no shell, so nothing here was run, and the exact outcomes are UNVERIFIED until I2 runs it.
   - In a tmp dir, write `m.py` with `X = 1` and import it once with writing enabled, which creates a .pyc.
   - Overwrite it with `X = 2`, same size, and reset its mtime to the original with `os.utime`. This makes the stale case deterministic, not timing-dependent. `os.utime` semantics are UNVERIFIED: the os docs page was truncated before that entry.
   - Expect the unguarded child import to print 1 (the stale read) and the guarded one to print 2 (mutant visible, so the "test" kills it).
   - A second case should show `-B` alone, with the old .pyc present, still prints 1. That pins finding 7, so nobody later "simplifies" the guard to `-B`.
4. Does probe_guardrails.py need a change? It uses a fresh worktree (no `__pycache__`, since it is gitignored and untracked, test_no_tracked_pycache) and the env var for every child, so by findings 7 and 9 it is already safe. Not re-run by R1. I2/I3 to confirm whether the fresh-worktree assumption should be asserted in code.
5. Rule-file change: i2-builder.md, i3-verifier.md, a1-auditor.md and run-item.md are under `.claude/`, so this needs the person's OK in PR review (request, RI link line).
