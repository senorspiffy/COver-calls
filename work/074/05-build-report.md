# 05 Build report - 074
Base commit: cf13af8 (daily-fixes/2026-11-18, after 071's I2 build ba78fb0, 072's and 073's A1 PASS). 072's README.md edit is in the base; 074 is built on top of it (04 Files 4). Built from work/074/04-build-plan.md.

## Changes made (file: what changed)
- `scripts/probe_guardrails.py` (NEW, stdlib only): `PROBES` (3 entries, strings byte for byte from the scratchpad probe.py L12-18, `recorded` printed only), `REQUIRED`, `JunitError`, `junit_key`, `read_junit`, `classify`, `run_pytest`, `module_file`, `worktree_clean`, `main(argv=None, probes=PROBES)` and the helpers `_probe_all`, `_run_probe`, `_baseline`, `_counts`, `_bad_lines`, `_child_env`, `_git`. Flow as 04 Files 1: `shutil.which("git")`, `worktree prune`, `rev-parse --verify -q <ref>^{commit}`, `TemporaryDirectory()` (no `dir=`, no `delete=`) checked against the resolved repo, `worktree add --detach -q <tmp>/wt <sha>`, first line `ref <ref> = <sha>`; per probe: file, anchor count, mutated != original, builtin `compile()` on the mutated text, module `__file__` check (once per (module, file)), baseline once per test_file (printed with its runtime), mutated run with `--rootdir=<wt>`, env without `PYTEST_ADDOPTS` plus `PYTHONDONTWRITEBYTECODE=1`, classify from exit code + junit only, restore bytes in `finally`, `git status --porcelain --untracked-files=no` clean or stop; `finally` `worktree remove --force`, then `prune`.
- `tests/test_probe_guardrails.py` (NEW): the 7 tests of 04 (9 ids: 1, 2, 3, 4x3, 5, 6, 7) on a committed fixture repo (no pyproject, no .gitignore). Loads the script by `importlib.util.spec_from_file_location`; `NO_GIT` copied from test_pipeline_check.
- `.claude/agents/a1-auditor.md`: the 03 step 4 text appended in the same paragraph as "In the daily review, also check that every guardrail from past BUG items is still in place.", ending "(item 074)". RULES BRANCH file: the person must OK it in PR review.
- `README.md`: one line inserted right after the `scripts/check_pipeline.py` line (04 Files 4 text). The check_handoff line (072) is untouched.

File counts. Restricted to this item's paths, because I3 for 071 and A1 for 073 work in the same tree in parallel; the unrestricted command gives the same numbers at this moment:
```
$ P="scripts/probe_guardrails.py tests/test_probe_guardrails.py .claude/agents/a1-auditor.md README.md"
$ git status --porcelain -uall -- $P | grep -c '^??'
2
$ git status --porcelain -uall -- $P | grep -c '^ M'
2
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
2
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
2
```
New: 2. Changed: 2. Matches 04 "4 files planned".

## Connectivity check
- [x] every new function/rule is used: `main` is the `__main__` entry and is called by tests 1-4 and 6; `classify`, `junit_key` are called by `_run_probe`/`_probe_all` and by test 5; `read_junit` by `classify` and `_baseline`; `run_pytest` by `_baseline` and `_run_probe`; `module_file` and `worktree_clean` by `_run_probe`/`_probe_all` (test 6 monkeypatches `worktree_clean`); `PROBES`/`REQUIRED` by `main`'s default and test 7. The a1-auditor paragraph names the command; the README line names the script.
- [x] every input has a source, every output has a consumer: inputs `--ref` (default HEAD; A1 passes origin/main), `--repo` (default `Path(__file__).resolve().parents[1]`), `--timeout` (default 600), `PROBES`. Outputs: stdout lines, pasted by A1 under "Guardrails still in place?" (a1-auditor.md) and by I2/I3 into 05/06; exit code 0/1/2.
- [x] every branch ends in a defined result: no git, bad ref, scratch inside repo, worktree add failed -> `SETUP: ...` / `SCRATCH INSIDE REPO: ...`, exit 2; file absent / anchor count != 1 -> `ANCHOR MISSING (...)`; mutated == original -> `ERROR (mutation does not change the file)`; SyntaxError -> `ERROR (mutation does not compile: ...)`; import fails or `__file__` elsewhere -> `ERROR (code under test is ...)`; baseline timeout / exit not 0-1 / no junit / any failure or error / target not found / target not passed -> `ERROR (baseline: ...)`; mutated timeout / exit / junit / errors / target not run -> ERROR, target failed -> HOLDS, else NOT HELD; restore not clean -> `ERROR (worktree not restored)` plus `STOPPED: <k> probes not run`; a probe entry lacking a required key -> `ERROR (probe entry lacks ...)`; an empty probe list -> `TOTAL: 0 probes ...`, exit 1. Every probe outcome other than HOLDS exits 1.
- [x] no leftover TODOs or unused files: `grep -n TODO` on both new files: 0 hits. No scratch file left in the repo; the mutation worktree was removed (`git worktree list` shows only the repo and three pre-existing worktrees of other sessions).
- Missing-data grep (`grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/`): 37 hits, all pre-existing; `git diff --stat HEAD -- ccbot/ config/` is empty, so no new or changed hit. The same grep on the two new files: 0 hits. No dataclass field. No `>`/`<` on floats: the only `>` is `_RANK[status] > _RANK[out[key]]` on ints from a fixed dict. A missing count is never filled: `counts n/a` / `pytest not run`, and `recorded: none` when `recorded` is absent.
- Python 3.10 floor (RI-008): no same-quote f-strings, no `delete=`; `python3.11` compile of both new files: `ok 3.11` (test_safety's own compile test only sees tracked files, so it covers them after the commit). `grep -n "read_text\|write_text\|delete=" scripts/probe_guardrails.py`: 0 hits (bytes I/O only).
- Feasibility numbers named in 04, measured: anchor count 1 for 3 of 3 (test 7 passes on the working tree; the real runs re-measured it at both refs: no ANCHOR MISSING); baselines `0 failed, 50 passed, 0 errors, 0 skipped` (test_realtest.py) and `0 failed, 17 passed, 0 errors, 0 skipped` (test_diff_reports.py) at both refs; targets 3 of 3 found and passed in the baseline.
- Greps of 04 Checks: `probe_guardrails.py --ref origin/main` in .claude/agents/a1-auditor.md: 1 hit. `scripts/probe_guardrails.py` in README.md: 1 hit. `delete=` in the script: 0 hits.

## Test output (pasted, not summarized)
Base suite at cf13af8 (scratch worktree, before any 074 file):
```
$ python3 -m pytest -q -p no:cacheprovider
444 passed, 1 skipped in 58.36s
```
New tests:
```
$ time python3 -m pytest -q tests/test_probe_guardrails.py
.........                                                                [100%]
9 passed in 4.29s
real	0m4.563s
```
(04 estimated about 10 s; measured 4.3 s.)
```
$ python3 -m pytest -q tests/test_probe_guardrails.py tests/test_safety.py
..................                                                       [100%]
18 passed in 5.87s
```
Full suite with 074:
```
$ time python3 -m pytest -q
........................................................................ [ 79%]
........................................................................ [ 95%]
......................                                                   [100%]
453 passed, 1 skipped in 68.26s (0:01:08)
```
453 = 444 + 9, no new failure or skip. The 1 skip is pre-existing (`tests/test_calendar.py:110: could not import 'exchange_calendars'`). Tests 453/454 collected (1 skipped).

Real run 1, `--ref origin/main` (origin/main = f103aa3, not fetched in this step):
```
$ python3 scripts/probe_guardrails.py --ref origin/main
ref origin/main = f103aa37b0992109c907759375f97a8462e9b07d
baseline tests/test_realtest.py: 0 failed, 50 passed, 0 errors, 0 skipped; 25.7 s
RI-002-063-leading-edge (RI-002): 9 failed, 41 passed, 0 errors, 0 skipped; target tests/test_realtest.py::test_leading_edge_100_days_blocks failed: yes; HOLDS; recorded 2026-11-18: 9 failed, 41 passed; code check: ccbot.realtest is ccbot/realtest.py in the worktree; 77.1 s
    FAILED tests.test_realtest::test_drop_input[earnings]
    FAILED tests.test_realtest::test_drop_input[earnings_before_first]
    FAILED tests.test_realtest::test_empty_earnings_file_warns_and_lead_is_null
    FAILED tests.test_realtest::test_leading_edge_100_days_blocks
    FAILED tests.test_realtest::test_leading_edge_151_days_blocks
    FAILED tests.test_realtest::test_real_counts_bac[d0.150_dte14-24_noE_hold_bid]
    FAILED tests.test_realtest::test_real_counts_bac[d0.275_dte30-45_noE_hold_bid]
    FAILED tests.test_realtest::test_real_counts_bac[d0.450_dte30-45_noE_hold_bid]
    FAILED tests.test_realtest::test_stock_without_earnings_sells_nothing
RI-002-065-interior-gap (RI-002): 4 failed, 46 passed, 0 errors, 0 skipped; target tests/test_realtest.py::test_interior_gap_180_blocks failed: yes; HOLDS; recorded 2026-11-18: 4 failed, 46 passed; code check: ccbot.realtest is ccbot/realtest.py in the worktree; 26.8 s
    FAILED tests.test_realtest::test_drop_input[earnings_interior_gap]
    FAILED tests.test_realtest::test_interior_gap_121_blocks
    FAILED tests.test_realtest::test_interior_gap_180_blocks
    FAILED tests.test_realtest::test_real_interior_gap_mo
baseline tests/test_diff_reports.py: 0 failed, 17 passed, 0 errors, 0 skipped; 1.6 s
RI-013-067-1b (RI-013): 1 failed, 16 passed, 0 errors, 0 skipped; target tests/test_diff_reports.py::test_a_nested_key_and_list_in_dict failed: yes; HOLDS; recorded 2026-11-18: 1 failed, 16 passed; code check: n/a (no module; tests run scripts/diff_reports.py by path via tests/conftest.py REPO, conftest L7); 2.6 s
    FAILED tests.test_diff_reports::test_a_nested_key_and_list_in_dict
TOTAL: 3 probes, 3 hold, 0 not held, 0 anchor missing, 0 error; 106.6 s
exit 0
wall 106.77 s
```
Real run 2, `--ref HEAD` (cf13af8; the 074 files are uncommitted, so HEAD holds the code under probe, not the script, which runs from the working tree):
```
$ python3 scripts/probe_guardrails.py --ref HEAD
ref HEAD = cf13af8946294b91889992e9dbefc6808c0a7190
baseline tests/test_realtest.py: 0 failed, 50 passed, 0 errors, 0 skipped; 26.1 s
RI-002-063-leading-edge (RI-002): 9 failed, 41 passed, 0 errors, 0 skipped; target tests/test_realtest.py::test_leading_edge_100_days_blocks failed: yes; HOLDS; recorded 2026-11-18: 9 failed, 41 passed; code check: ccbot.realtest is ccbot/realtest.py in the worktree; 76.8 s
    FAILED tests.test_realtest::test_drop_input[earnings]
    FAILED tests.test_realtest::test_drop_input[earnings_before_first]
    FAILED tests.test_realtest::test_empty_earnings_file_warns_and_lead_is_null
    FAILED tests.test_realtest::test_leading_edge_100_days_blocks
    FAILED tests.test_realtest::test_leading_edge_151_days_blocks
    FAILED tests.test_realtest::test_real_counts_bac[d0.150_dte14-24_noE_hold_bid]
    FAILED tests.test_realtest::test_real_counts_bac[d0.275_dte30-45_noE_hold_bid]
    FAILED tests.test_realtest::test_real_counts_bac[d0.450_dte30-45_noE_hold_bid]
    FAILED tests.test_realtest::test_stock_without_earnings_sells_nothing
RI-002-065-interior-gap (RI-002): 4 failed, 46 passed, 0 errors, 0 skipped; target tests/test_realtest.py::test_interior_gap_180_blocks failed: yes; HOLDS; recorded 2026-11-18: 4 failed, 46 passed; code check: ccbot.realtest is ccbot/realtest.py in the worktree; 26.6 s
    FAILED tests.test_realtest::test_drop_input[earnings_interior_gap]
    FAILED tests.test_realtest::test_interior_gap_121_blocks
    FAILED tests.test_realtest::test_interior_gap_180_blocks
    FAILED tests.test_realtest::test_real_interior_gap_mo
baseline tests/test_diff_reports.py: 0 failed, 17 passed, 0 errors, 0 skipped; 1.6 s
RI-013-067-1b (RI-013): 1 failed, 16 passed, 0 errors, 0 skipped; target tests/test_diff_reports.py::test_a_nested_key_and_list_in_dict failed: yes; HOLDS; recorded 2026-11-18: 1 failed, 16 passed; code check: n/a (no module; tests run scripts/diff_reports.py by path via tests/conftest.py REPO, conftest L7); 2.6 s
    FAILED tests.test_diff_reports::test_a_nested_key_and_list_in_dict
TOTAL: 3 probes, 3 hold, 0 not held, 0 anchor missing, 0 error; 106.2 s
exit 0
wall 106.41 s
```
Measured runtime: about 106 s per run (04/03 estimated about 128 s). Baselines 25.7 / 26.1 s (test_realtest.py) and 1.6 s (test_diff_reports.py). A probe's own seconds include the baseline and module check it triggered (P1 77 s = module check + 26 s baseline + about 50 s mutated run). Every measured count equals `recorded`. Mutations were not tuned. Afterwards `git worktree list` showed no worktree from the script (only the repo plus three pre-existing worktrees of other sessions under the scratchpad), and `git status` showed only the 4 planned paths.

Mutation probes of the script (04 Checks, I3 list), run in a scratch worktree of cf13af8 under the session scratchpad with the two new files copied in, never in the repo (RI-009). Driver: scratchpad mut074.py; the worktree was removed afterwards.
```
count check removed -> 1 failed, 8 passed in 5.39s
    FAILED tests/test_probe_guardrails.py::test_mixed_run_reports_every_probe - A...
baseline check removed -> 1 failed, 8 passed in 5.50s
    FAILED tests/test_probe_guardrails.py::test_mixed_run_reports_every_probe - A...
any failure = HOLDS -> 1 failed, 8 passed in 5.01s
    FAILED tests/test_probe_guardrails.py::test_mixed_run_reports_every_probe - A...
exit-code check removed -> 2 failed, 7 passed in 4.10s
    FAILED tests/test_probe_guardrails.py::test_mixed_run_reports_every_probe - A...
    FAILED tests/test_probe_guardrails.py::test_classify_missing_or_bad_junit - A...
--rootdir removed -> 9 passed in 4.14s
PYTEST_ADDOPTS kept -> 1 failed, 8 passed in 3.96s
    FAILED tests/test_probe_guardrails.py::test_holds_exits_0 - AssertionError: r...
--untracked-files=no removed -> 9 passed in 4.15s
```
5 of 7 mutants are killed. 2 survive; see Deviations (the plan's prediction is wrong for both, and the code was not changed to hide that).

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat HEAD -- ccbot/ config/ data/` is empty; the item changes scripts/probe_guardrails.py, tests/test_probe_guardrails.py, .claude/agents/a1-auditor.md, README.md only; realtest.py is not changed, so no realtest run is needed).

## Deviations from plan
1. **`--rootdir` mutant survives (04 C1 / Research 1 is wrong for the installed pytest).** I measured it in a scratch dir with no config file: `cd <dir>; python3 -m pytest tests/test_mod.py` prints `rootdir: <dir>` (the cwd), not `<dir>/tests`, and junit has `classname="tests.test_mod"`. pytest 9.1.1 includes the invocation dir when it computes the common ancestor, so the fixture cannot tell the flag apart from no flag. The flag is kept as planned (harmless, and it pins the behaviour on other pytest versions), but test 1 does not pin it. For I1/I3: either accept it as defence in depth, or drop the claim "with the flag removed, (a) gives ERROR".
2. **`--untracked-files=no` mutant survives (04 Checks prediction is wrong).** With `PYTHONDONTWRITEBYTECODE=1` in every child env (04 C3) and `-p no:cacheprovider`, no untracked file is created in the worktree (the scratch run above shows pytest writes `tests/__pycache__/` only when that env var is absent). The two C3 measures cover the same hazard, so removing either one alone is not visible. I also gave the module-check child the same env (04 does not say which env `module_file` uses): if it wrote a .pyc of the unmutated module, a same-size mutation such as `return 1` -> `return 2` made within the same second could be served from that stale .pyc and give a false NOT HELD.
3. **Line format details not fixed by 04:** counts are printed as `<f> failed, <p> passed, <e> errors, <s> skipped` (the skipped count is added so the whole result is shown, RI-013; the 04 substrings still match). Probes that never ran pytest say `pytest not run`; a run with no junit says `counts n/a`; ERROR testcases get an indented `ERROR <classname>::<name>` line next to the `FAILED` lines. When the restore check fails, that probe's line shows `ERROR (worktree not restored)`, then `STOPPED: <k> probes not run (worktree not restored)`, and TOTAL counts only the probes reported (test 6 pins this). A probe entry that lacks a required key gets `ERROR (probe entry lacks ...)`, and an empty probe list exits 1. These are defined results for branches 04 left open; no rule changed.
4. **Compile check order:** the builtin `compile()` runs on the mutated text before it is written, so a mutation that does not compile never touches the worktree. The result and the text (`ERROR (mutation does not compile: <msg>, line <n>)`) are the same as 04 asked for.
5. **Test 4 also asserts that no worktree is left** (`git worktree list` = 1), and test 5 also covers `classify(..., timed_out=7)` and `junit_key` with params. These are extra asserts; nothing was removed.
6. The a1-auditor.md text ends "Takes about 2 minutes (item 074)." The measured time is about 106 s, so "about 2 minutes" stays true.

Recurring issues checked (item 013), against this build:
- RI-001 (ESCALATED): no trading filter. The selection rules (anchor count 1, baseline all-pass) have measured counts: 3 of 3 anchors, 50 of 50 and 17 of 17 at both refs.
- RI-002: every absent input gives a named ERROR or ANCHOR MISSING line and exit 1 or 2, never HOLDS; no count is defaulted (`counts n/a`, `recorded: none`).
- RI-003: n/a (no calendar).
- RI-004 / RI-005: test 2's TOTAL (1 + 2 + 3 + 7 = 13) is asserted against the script's own output, not hand-copied.
- RI-006: file counts and test counts come from the commands pasted above.
- RI-007: Scope FULL; this is I2 after I1's 04.
- RI-008: no `delete=`, no same-quote f-strings, compiles on python3.11, bytes I/O only.
- RI-009: committed code only, through a TemporaryDirectory worktree outside the repo; mutation probes in a scratch worktree; staged by exact path; logs/recurring-issues.md not edited.
- RI-010: this item; the log line is written by `check_pipeline.py --log`.
- RI-011: n/a.
- RI-012: classification by exit code and junit only.
- RI-013: whole result per probe (counts, every FAILED node id, runtime, baselines).

Guardrail status lines (A1 copies them on main, item 036):
- RI-010: guardrail built (074). The probe entries for RI-002 (063, 065) and RI-013 (067 1b) are now committed in scripts/probe_guardrails.py `PROBES`; `--ref origin/main` -> 3 hold, exit 0. In force when 074 is merged and A1's daily run pastes the output.
- RI-002: unchanged (GUARDED). 074 runs its 063/065 probes by entry id: both HOLDS on origin/main f103aa3 (9 failed / 4 failed, as recorded).
- RI-013: unchanged (GUARDED). Probe RI-013-067-1b HOLDS on origin/main f103aa3 (1 failed, 16 passed, as recorded).
