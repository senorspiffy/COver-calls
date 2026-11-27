# 06 Verification - 107
Verdict: PASS (round 1)
Sent back to: none
Scratch dir: /tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i3-107-r1-d9wawoce

The worktree `wt` is inside the scratch dir above. It was made with `git worktree add --detach` at a522c5d (I2's build). The pyc dir `pyc-tgpposrs` is inside it, made with the same mkdtemp command and prefix `pyc-`. Every test, mutant and check ran in `wt`. In the main checkout I only wrote 06/07, the log line and the commit, because item 106 is being built there. No `git stash` was used. Each mutated file was restored in `wt` with `git checkout HEAD -- <file>`. Afterwards `git status --porcelain` in `wt` was empty.

## I1 audit (plan vs research)
- 04 follows the 03 map step for step, and its Rule trace has a row for every 03 step, the Residual, Missing inputs and the Removed claims.
- The 3 "(I1 change)" edits have sources, and none changes what a rule means:
  - Empty `pytest.ini`, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` and stripping `PYTHONSAFEPATH`. Sourced: Extra research 1, 2 and 4. The PYTHONSAFEPATH point is marked as inference from cmdline.html, which was not re-fetched. That is acceptable: dropping a var that is absent only removes outside influence.
  - "Prefix dir empty" is asserted as "no files under it". This is the meaning 03 intends: no bytecode was written.
  - m4 as a pure helper test, replacing "fixture list or `git add -f`". 03 offered both forms, and 04 records the dropped variant with a reason.
- Unsourced additions: none found. Residual 2 (10 test subprocess sites with no env pin) is new from I1. It states a gap and builds nothing.
- 03's Removed claims (F10, F23) are not used in 04.
- The FLAG for the person's OK on the 4 rule files is kept (request.md L13).

## I2 audit (build vs plan)
Diff a5b8edd..a522c5d, outside work/ and logs/: 7 files, as 04 planned.
- Files 1-4, the rule files. The word-diff of `.claude` shows only insertions: 4 times the same `{+Every mutant or probe run ...+}`. I checked it with a script in `wt`:
  ```
  03==constant True
  .claude/commands/run-item.md 1 1
  .claude/agents/i2-builder.md 1 1
  .claude/agents/i3-verifier.md 1 1
  .claude/agents/a1-auditor.md 1 1
  ```
  The two columns are `count(BYTECODE)` and `count("never in the main checkout (items 091, 097). " + BYTECODE)`. So the sentence appears exactly once in each file, directly after SCRATCH with one space, and its text equals 03 step 1 character for character.
- 5(a): the `BYTECODE` constant and `test_bytecode_sentence_same_in_four_files` come right after the SCRATCH test. The test asserts both variable names and `.count == 1` for each of SCRATCH_FILES, as planned. The one-line comment above the constant is 05 Deviation 3 and is harmless.
- 5(b) and 5(c): `_tracked_bytecode` is defined at module level, `test_no_tracked_pycache` uses it and its docstring note was added, and `test_tracked_bytecode_helper` has the 4-path fixture. All match 04.
- File 6, `tests/test_stale_bytecode.py`. Each of these matches 04 File 6 line by line:
  - `STRIP` covers the 3 vars from 03 plus `PYTHONSAFEPATH`.
  - `_env` sets `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`.
  - `_pytest` runs with `-p no:cacheprovider` and `--rootdir=src`, with timeout 120.
  - `_import_x` uses `.strip()`.
  - `_stale` does: the empty `pytest.ini`, the unguarded setup run, the assert that a pyc exists, `X = 2\n` plus `os.utime(ns=...)`, then the mtime and size preconditions with named messages.
  - Cases (a)-(c) expect exit 0, with (a) printing `1`. Case (d) uses the sibling prefix `pyc-guard`, expects exit 1, prints `2`, and asserts no files.
- File 7: `test_child_env_disables_bytecode_writes` comes after `test_shipped_probes_well_formed`, with no `@NO_GIT`. It uses the 04 monkeypatch calls.
- scripts/, ccbot/ and config/ are unchanged (`git show --stat a522c5d` lists none of them).
- Connectivity: I re-did it. Every helper is used by both stale tests. `_tracked_bytecode` has 2 users, `BYTECODE` has 1, and the sentence is in all 4 files agents read. No TODO.
- 05's grep reasons hold. ccbot/ is untouched, so the 38 hits there are unchanged. The added lines hold no default pattern, and RI-002 does not apply to test-only code.
- 05's deviations are explained and true:
  - (1) m0 was re-run as a true deletion. I did the same.
  - (2) `RULES BRANCH: none` from the branch's own checkout. Same finding as 105/07 point 3.
  - (3) The comment above the constant.
- Text-match rule (item 059, RI-012): no code here sorts an error or reply by matching its text. The new asserts compare exact return codes (0/1), exact stdout (`"1"`/`"2"`) and `.count(...) == 1` of a whole pinned sentence. n/a.
- Simulator/picker rule (item 062): n/a. There is no simulator or replay.
- Rule the person follows (001): unchanged. Agent rule files change (4), and they are FLAGged for the person's OK in PR review (04, 05).
- Data-hole and edge checks: n/a. No data window.

## Tests re-run (output)
Env-check line. The guard was used on every command below, except the unguarded stale-test repeat that is marked as such:
```
$ PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i3-107-r1-d9wawoce/pyc-tgpposrs python3 -c 'import sys; print(sys.dont_write_bytecode, sys.pycache_prefix)'
True /tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i3-107-r1-d9wawoce/pyc-tgpposrs
```
Full suite in `wt` at a522c5d, Python 3.13.18: `python3 -m pytest -q -p no:cacheprovider -rs` (guarded)
```
=========================== short test summary info ============================
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'
1040 passed, 1 skipped in 215.12s (0:03:35)
```
This equals 05's count (1040 passed, 1 skipped). The single skip is exchange_calendars. `test_every_py_compiles_on_oldest_python` ran and passed, not skipped: python3.11 is on PATH at /usr/bin/python3.11, and python3.10 is not. `python3.11 -m py_compile tests/test_stale_bytecode.py` gave `py311 ok`, and the 3.11 pyc it wrote was deleted.

The stale test ran unguarded 3 times in `wt` (not a mutant run), to check that it does not depend on the outer env and is not flaky:
```
2 passed in 1.67s
2 passed in 1.65s
2 passed in 1.61s
```

Mutants: each one ran as `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<pyc dir above> python3 -m pytest -q -p no:cacheprovider <tests>` in `wt`. The runner is /tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i3-107-r1-d9wawoce/mut.sh, and its raw output is in /tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i3-107-r1-d9wawoce/mut-out.txt. Each edit asserts that its anchor occurs exactly once.

| Mutant | Change | Summary line | Failed |
|---|---|---|---|
| m0 | ` ` + BYTECODE deleted from .claude/agents/a1-auditor.md (I2 used i3-verifier.md) | `1 failed, 1 passed in 0.82s` | test_bytecode_sentence_same_in_four_files (`AssertionError: .claude/agents/a1-auditor.md`). SCRATCH test passes |
| m1 | case (d) env without `PYTHONPYCACHEPREFIX` | `1 failed, 1 passed in 8.38s` | test_guard_kills_stale_mutant: "(d) full guard did not kill the mutant (item 107)" |
| m2 | `_stale` writes `X = 22\n` | `2 failed in 0.37s` | both: "precondition size 7 != 6 or != 6 (item 107)" |
| m3 run 1 | `    env["PYTHONDONTWRITEBYTECODE"] = "1"` deleted from scripts/probe_guardrails.py | `1 failed in 0.07s` | test_child_env_disables_bytecode_writes (KeyError) |
| m3 run 2 | same | `1 failed in 0.07s` | same |
| m3 run 3 | same | `1 failed in 0.07s` | same |
| m4 | `_tracked_bytecode` without ` or p.endswith(".pyc")` | `1 failed, 1 passed in 0.82s` | test_tracked_bytecode_helper |

After all mutants: `git status --porcelain` in `wt` was empty, and `pyc files in prefix: 0`.

`python3 scripts/check_handoff.py 107` (in `wt`, exit 0):
```
sources count (unique URLs in 01-research.md): 11
fact-check rows: 68
totals line: 68 rows -> 56 as-is, 8 fixed, 4 removed
PASS
```
`python3 scripts/check_pipeline.py` in `wt` before 06: `107: in progress (FULL: next 06)`, `INCOMPLETE: none`, `SKIPPED: none`, `UNTRACKED CHANGE: none`, `STASH: none`.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat a5b8edd a522c5d`: .claude/agents/a1-auditor.md, .claude/agents/i2-builder.md, .claude/agents/i3-verifier.md, .claude/commands/run-item.md, tests/test_pipeline_check.py, tests/test_probe_guardrails.py, tests/test_stale_bytecode.py, plus work/107/05 and the log; no TRIGGER or TRIGGER_DIRS file)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-014, RI-002, RI-004, RI-005, RI-006, RI-007, RI-009, RI-010, RI-012, RI-013
- RI-001 (ESCALATED): there is no trading window. I re-ran each count the rule text cites:
  - The sentence is in 4 of 4 files (script above).
  - Tracked bytecode is 0: `test_no_tracked_pycache` passes.
  - The stale case reproduces on 3.13.18: case (a) passes 3 of 3 unguarded runs.
- RI-014 (OPEN): no new git-history read. The new tests use `tmp_path` or a pure env dict. `git ls-files` does not depend on clone depth.
- RI-002: a stale case that does not reproduce, a missing pyc and a failed precondition each give a named failure, never a skip. m2 shows the size precondition.
- RI-004/005: worked example re-derived. `X = 1\n` and `X = 2\n` are 6 bytes each, and `X = 22\n` is 7 (m2 message).
- RI-006: the counts above are pasted from command output (1040/1; 68 -> 56/8/4).
- RI-007: Scope FULL, and 01-05 exist before 06.
- RI-009: my own mkdtemp dir and worktree. No stash. Restores were done in `wt` only.
- RI-010: the env-check line is pasted above the mutant table. Residual 1 (no script check) is noted for A1.
- RI-012: no text-matching classifier. The asserts use exact values.
- RI-013: this item's family. All mutants ran under the new guard.

## Pipeline line (step 2)
check_pipeline line: `107: awaiting A1 (FULL)` (main checkout, after 06, 07 and the --log line; INCOMPLETE: none, SKIPPED: none, STASH: none)

## Sent back / sent to Audit
Sent to Audit: work/107/07-audit-task.md. Nothing sent back.
