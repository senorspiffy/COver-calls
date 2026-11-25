# 06 Verification - 074
Verdict: PASS (round 1; earlier rounds: none)
Sent back to: none
<!-- On every round, FAIL too, update these two lines first. Verdict: its first word is PASS or FAIL (bold allowed), then the latest round. Sent back to: I1, I2 or I1 I2 on FAIL, none on PASS. check_pipeline.py reads the first Verdict and Sent back line outside code fences (item 071). -->
Build commit: b54c1b2 (base cf13af8). Branch HEAD at check time: b73d5e3 (071's A1 result only: logs/audit/2026-11-18-071.md, work/071/07-audit-task.md; `git diff --stat b54c1b2 HEAD` = those 2 files). Checked 2026-11-19 UTC.

**Restart note.** A first I3 run wrote an earlier version of this file (uncommitted, Verdict PASS round 1) and was then cut off by a container restart before 07, the log line and the commit. Its pipeline line ("`074: awaiting A1 (FULL)`") was written before 07 and the log line existed, so it could not have been measured. I did not reuse any claim from that run that I could not confirm. I re-ran in my own fresh detached worktree of b54c1b2 at /tmp/claude-0/-home-claude/17414523-55e9-552d-bf38-90b98a4fb4ca/scratchpad/i3r2-074-wt: the full suite, the new tests + test_safety, the 3.11 compile, the greps, the PROBES compare, check_handoff, the 11-mutant driver and the real `--ref origin/main` probe run. Afterwards I removed the worktree with `git worktree remove` (no `--force`; `git status --porcelain --untracked-files=all` there gave 0 lines). The first run's `--ref HEAD` probe output (saved file /tmp/claude-0/-home-claude/17414523-55e9-552d-bf38-90b98a4fb4ca/scratchpad/i3-074-probe-head.txt, kept below) was not re-run: it is the same script at the same commit, and the `--ref origin/main` run I did re-run matches its counts line for line. This is still round 1, because the cut-off run never got to a verdict that counted (no log line, no commit).

## I1 audit (plan vs research)
- 04 Files 1-3 carry out 03 Implementation-map steps 1-6. The 04 Rule trace has a row for every 03 step (1, 2.1-2.9, 3-7), for the Missing-inputs table and for the removed claim D24. Step 7 (follow-ups) is DROPPED with the reason 03 gives ("not built here").
- Exact texts: the three PROBES strings in 04 are the 03 step 1 strings. The a1-auditor.md paragraph is the 03 step 4 text word for word, with "(item 074)" added.
- Additions to 03 (C1-C13). Each one has a stated reason or source:
  - C1 `--rootdir`: pytest customize docs (Research 1). The prediction attached to it is wrong on the installed pytest; see the mutation decision below.
  - C2: junitxml.py source (Research 2).
  - C3: Research 4. It builds on 03's own row D22 (`py_compile` writes a .pyc).
  - C4: pytest docs on PYTEST_ADDOPTS (Research 3).
  - C5: corrects 03's "script's parent dir", which would be scripts/, not the repo root.
  - C6-C11: test or reporting refinements of 03 rules. C7 is the reason (d) cannot catch the exit-code mutant (confirmed: that mutant fails (d2) and test 5).
  - C12: shift-left test. It puts 03's anchor-count feasibility into the suite.
- C13 (README line) is the one addition with no reason beyond "a scripts-list line". It fits the README convention: every other workflow script that agents run has a line there (check_handoff, check_pipeline). It changes no rule. I accept it and flag it for Audit; it is not a FAIL.
- One stale check in 04: the grep "`run by R3, I3, A1` in README.md: unchanged by 074" gives 0 hits at the base cf13af8 too, because 072 reworded that line. What it was meant to show still holds: `git diff cf13af8 b54c1b2 --stat -- README.md` = 1 insertion, and the check_handoff line is untouched.

## I2 audit (build vs plan)
- Files: the 4 planned paths, plus 05 and I2's log line (`git show --stat b54c1b2`: 6 files, 714 insertions, 1 deletion). `git diff --stat cf13af8 b54c1b2` also lists work/071/06, work/071/07 and 3 more log lines: those come from 166e8b4 (071's I3 commit, between base and build), not from 074. `git diff --stat cf13af8 b54c1b2 -- ccbot config data templates scripts/check_pipeline.py tests/test_pipeline_check.py logs/recurring-issues.md` is empty (0 lines), which matches 04 "Not changed".
- PROBES: I read `PROBES` from b54c1b2 by `ast.literal_eval` (3 entries) and compared anchor, replacement and test file with A1's /tmp/claude-0/-home-claude/17414523-55e9-552d-bf38-90b98a4fb4ca/scratchpad/probe.py L12-18: the same strings for all 3. Targets are the three node ids of 03 step 1.
- Functions: `junit_key`, `read_junit`, `classify`, `run_pytest`, `module_file` and `worktree_clean` match 04 Files 1, including the classify order, the run_pytest command line and the child env. `main(argv=None, probes=PROBES)` follows the 2.1 flow:
  - `which git`, then prune, then `rev-parse --verify -q <ref>^{commit}`
  - `TemporaryDirectory()` with no `dir=` or `delete=`, and the scratch-inside-repo check
  - `worktree add --detach -q`
  - `finally`: `remove --force`, then prune
- I2's Deviations 3-6 are small and stated:
  - extra `skipped` count
  - `pytest not run` / `counts n/a` texts
  - `STOPPED:` line
  - a missing-key check
  - an empty list exits 1
  - compile runs before the write
  None of them weakens a 03/04 rule: every new branch ends in ERROR or exit 1, never HOLDS.
- Connectivity (redone): every function is reached from `main` or from a test. `__main__` → `main`. The a1-auditor.md paragraph names `--ref origin/main` (grep in the worktree: 1 hit; the diff is the one-line append of the 03 step 4 text plus "(item 074)"). The README names the script (grep: 1 hit). No TODO in either new file (grep: 0 and 0).
- RI-012 (text classification): verdicts come from the pytest exit code and from junit XML element tags (`failure`/`error`/`skipped`). Nothing parses free text from pytest output. `verdict.startswith("ANCHOR MISSING")` reads the script's own verdict strings for the tally. So the item-059 negative-test rule does not apply. Test 5 still covers error-tag, bad-XML and missing-target junit.
- 062 (simulator must call the bot pickers): n/a, no simulator or replay.
- Utf-8 / 3.10 floor: grep `read_text|write_text|delete=` in both new files gives 0 and 0. python3.11 `compile()` of both prints ok311. `tests/test_safety.py::test_every_py_compiles_on_oldest_python` ran with python3.11 (`which python3.10`: not found; `which python3.11`: /usr/bin/python3.11). It was not skipped: `-rs` on the full suite shows only the calendar skip.

### Decision on I2's two surviving mutants (`--rootdir` removed; `--untracked-files=no` removed)
Decision: **accept both flags as shipped, with no new pinning test; withdraw the two 04 predictions.** Both mutants survive again in my run (9 passed each, below). Reasons:
1. **Both are fail-safe: neither can give a false HOLDS.** HOLDS needs the target key to be found in the baseline junit and then to fail in the mutated junit (`classify`).
   - `--rootdir` removed: if a pytest roots node ids somewhere else, the classname changes and the baseline lookup gives `ERROR (baseline: target not found)`, exit 1. I measured this on pytest 9.1.1 in a scratch dir with no config file: run from the dir, `rootdir: <dir>`, `classname="tests.test_mod"`; run from `<dir>/tests`, `rootdir: <dir>/tests`, `classname="test_mod"`. So the node id follows the cwd, and the script always runs with `cwd=wt` (L117, L128). In the real repo, pyproject.toml at `<wt>` fixes rootdir anyway.
   - `--untracked-files=no` removed: the restore check only gets stricter. Any untracked file gives `ERROR (worktree not restored)`, `STOPPED:` and exit 1.
   - A1's rule (a1-auditor.md, this item) makes any non-HOLDS line a finding, so neither flag can be removed silently without A1 seeing a red line.
2. **`--rootdir` cannot be pinned on this pytest** with the script's fixed `cwd=wt`: the measurement above shows the flag changes nothing there. A test that cannot fail here adds nothing.
3. **`--untracked-files=no` could be pinned** (a test that leaves an untracked file in the worktree). But a mutation only edits one tracked file, so the flag only stops false ERRORs from junk the probe did not make. There is no unsafe direction to guard.
4. **What is wrong is 04's text, not the code.** 04 Research 1/C1 says "with the flag removed, (a) gives ERROR, not HOLDS". 04 Checks says "`--untracked-files=no` removed → test 2 fails (worktree not restored)". Both are false on pytest 9.1.1. I2 said so in 05 Deviations 1-2 with measurements and did not change the code to hide it. I withdraw both 04 claims here. An I1 round only to delete two sentences would change no behaviour, so this is not a FAIL. 07 item 3 asks A1 to confirm.

Related finding (supports 04 C3). 05 Deviation 2 says the two bytecode measures "cover the same hazard, so removing either one alone is not visible". That is not right. With `PYTHONDONTWRITEBYTECODE` removed alone, my driver run now gives 2 failed (test 1 and test 2). The first I3 run's saved notes say 1 failed, then 2 of 3 re-runs passed. So the result depends on timing: the module-check child writes `pkg/__pycache__/mod.*.pyc`, and the same-size `return 1`→`return 2` edit lands in the same second, so the stale bytecode is used and the result is a false NOT HELD. The env var guards against a real, timing-dependent fault and is set for every child (L107). As shipped (env var set), test 1 passed in every run I made: the full suite, the new file plus test_safety, and every other mutant run. It is not flaky as shipped.

## Tests re-run (output)
All of this ran in my fresh worktree of b54c1b2 (/tmp/claude-0/-home-claude/17414523-55e9-552d-bf38-90b98a4fb4ca/scratchpad/i3r2-074-wt). `env | grep -c PYTEST_ADDOPTS` = 0. pytest 9.1.1.

Full suite:
```
$ time python3 -m pytest -q -p no:cacheprovider -rs
......................                                                   [100%]
=========================== short test summary info ============================
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'
453 passed, 1 skipped in 61.83s (0:01:01)
real	1m2.929s
```
This matches 05's 453 = 444 + 9. The 1 skip is pre-existing.

New tests plus test_safety:
```
$ python3 -m pytest -q -p no:cacheprovider tests/test_probe_guardrails.py tests/test_safety.py
18 passed in 5.15s
```

Mutation probes of the script. Driver: /tmp/claude-0/-home-claude/17414523-55e9-552d-bf38-90b98a4fb4ca/scratchpad/i3-074-mut.py (written by the first I3 run; I read it and re-used it as is). It asserts each anchor occurs once, writes the mutant, runs the new test file and restores the bytes in `finally`. Saved output: /tmp/claude-0/-home-claude/17414523-55e9-552d-bf38-90b98a4fb4ca/scratchpad/i3r2-mut.txt.
```
$ python3 i3-074-mut.py <wt>
count check removed -> 1 failed, 8 passed in 4.11s
    FAILED tests/test_probe_guardrails.py::test_mixed_run_reports_every_probe - A...
baseline check removed -> 1 failed, 8 passed in 4.24s
    FAILED tests/test_probe_guardrails.py::test_mixed_run_reports_every_probe - A...
any failure = HOLDS -> 1 failed, 8 passed in 3.95s
    FAILED tests/test_probe_guardrails.py::test_mixed_run_reports_every_probe - A...
exit-code check removed -> 2 failed, 7 passed in 3.95s
    FAILED tests/test_probe_guardrails.py::test_mixed_run_reports_every_probe - A...
    FAILED tests/test_probe_guardrails.py::test_classify_missing_or_bad_junit - A...
--rootdir removed -> 9 passed in 3.85s
PYTEST_ADDOPTS kept -> 1 failed, 8 passed in 3.79s
    FAILED tests/test_probe_guardrails.py::test_holds_exits_0 - AssertionError: r...
--untracked-files=no removed -> 9 passed in 3.97s
PYTHONDONTWRITEBYTECODE removed -> 2 failed, 7 passed in 4.11s
    FAILED tests/test_probe_guardrails.py::test_holds_exits_0 - AssertionError: r...
    FAILED tests/test_probe_guardrails.py::test_mixed_run_reports_every_probe - A...
both bytecode guards removed -> 2 failed, 7 passed in 2.73s
    FAILED tests/test_probe_guardrails.py::test_holds_exits_0 - AssertionError: r...
    FAILED tests/test_probe_guardrails.py::test_mixed_run_reports_every_probe - A...
restore removed -> 2 failed, 7 passed in 2.76s
    FAILED tests/test_probe_guardrails.py::test_holds_exits_0 - AssertionError: r...
    FAILED tests/test_probe_guardrails.py::test_mixed_run_reports_every_probe - A...
scratch-inside check removed -> 1 failed, 8 passed in 4.50s
    FAILED tests/test_probe_guardrails.py::test_setup_errors_exit_2[scratch_inside]
restored: True
```
Afterwards `git status --porcelain --untracked-files=all` in the worktree gave 0 lines.
- The first 7 lines are 04's list. They match 05 line for line: 5 are killed, and `--rootdir` / `--untracked-files=no` survive (decision above).
- The last 4 are extra mutants: env var alone, both bytecode guards, restore removed, and the scratch-inside check. All 4 are killed.

Real probes. `--ref origin/main`: my own run, in my worktree (origin/main = f103aa3, unchanged since 05). Saved: /tmp/claude-0/-home-claude/17414523-55e9-552d-bf38-90b98a4fb4ca/scratchpad/i3r2-probe-main.txt.
```
$ python3 scripts/probe_guardrails.py --ref origin/main
ref origin/main = f103aa37b0992109c907759375f97a8462e9b07d
baseline tests/test_realtest.py: 0 failed, 50 passed, 0 errors, 0 skipped; 24.3 s
RI-002-063-leading-edge (RI-002): 9 failed, 41 passed, 0 errors, 0 skipped; target tests/test_realtest.py::test_leading_edge_100_days_blocks failed: yes; HOLDS; recorded 2026-11-18: 9 failed, 41 passed; code check: ccbot.realtest is ccbot/realtest.py in the worktree; 73.2 s
    FAILED tests.test_realtest::test_drop_input[earnings]
    FAILED tests.test_realtest::test_drop_input[earnings_before_first]
    FAILED tests.test_realtest::test_empty_earnings_file_warns_and_lead_is_null
    FAILED tests.test_realtest::test_leading_edge_100_days_blocks
    FAILED tests.test_realtest::test_leading_edge_151_days_blocks
    FAILED tests.test_realtest::test_real_counts_bac[d0.150_dte14-24_noE_hold_bid]
    FAILED tests.test_realtest::test_real_counts_bac[d0.275_dte30-45_noE_hold_bid]
    FAILED tests.test_realtest::test_real_counts_bac[d0.450_dte30-45_noE_hold_bid]
    FAILED tests.test_realtest::test_stock_without_earnings_sells_nothing
RI-002-065-interior-gap (RI-002): 4 failed, 46 passed, 0 errors, 0 skipped; target tests/test_realtest.py::test_interior_gap_180_blocks failed: yes; HOLDS; recorded 2026-11-18: 4 failed, 46 passed; code check: ccbot.realtest is ccbot/realtest.py in the worktree; 26.0 s
    FAILED tests.test_realtest::test_drop_input[earnings_interior_gap]
    FAILED tests.test_realtest::test_interior_gap_121_blocks
    FAILED tests.test_realtest::test_interior_gap_180_blocks
    FAILED tests.test_realtest::test_real_interior_gap_mo
baseline tests/test_diff_reports.py: 0 failed, 17 passed, 0 errors, 0 skipped; 0.9 s
RI-013-067-1b (RI-013): 1 failed, 16 passed, 0 errors, 0 skipped; target tests/test_diff_reports.py::test_a_nested_key_and_list_in_dict failed: yes; HOLDS; recorded 2026-11-18: 1 failed, 16 passed; code check: n/a (no module; tests run scripts/diff_reports.py by path via tests/conftest.py REPO, conftest L7); 2.0 s
    FAILED tests.test_diff_reports::test_a_nested_key_and_list_in_dict
TOTAL: 3 probes, 3 hold, 0 not held, 0 anchor missing, 0 error; 101.4 s
exit 0
wall 101.512003177 s
```
`--ref HEAD` (b54c1b2): from the first I3 run, saved in /tmp/claude-0/-home-claude/17414523-55e9-552d-bf38-90b98a4fb4ca/scratchpad/i3-074-probe-head.txt, not re-run (see the restart note). Its counts and FAILED ids are the same as above:
```
$ python3 scripts/probe_guardrails.py --ref HEAD
ref HEAD = b54c1b2cbf6ed0116b151631cce8108871036470
baseline tests/test_realtest.py: 0 failed, 50 passed, 0 errors, 0 skipped; 24.2 s
RI-002-063-leading-edge (RI-002): 9 failed, 41 passed, 0 errors, 0 skipped; target tests/test_realtest.py::test_leading_edge_100_days_blocks failed: yes; HOLDS; recorded 2026-11-18: 9 failed, 41 passed; code check: ccbot.realtest is ccbot/realtest.py in the worktree; 71.4 s
    FAILED tests.test_realtest::test_drop_input[earnings]
    FAILED tests.test_realtest::test_drop_input[earnings_before_first]
    FAILED tests.test_realtest::test_empty_earnings_file_warns_and_lead_is_null
    FAILED tests.test_realtest::test_leading_edge_100_days_blocks
    FAILED tests.test_realtest::test_leading_edge_151_days_blocks
    FAILED tests.test_realtest::test_real_counts_bac[d0.150_dte14-24_noE_hold_bid]
    FAILED tests.test_realtest::test_real_counts_bac[d0.275_dte30-45_noE_hold_bid]
    FAILED tests.test_realtest::test_real_counts_bac[d0.450_dte30-45_noE_hold_bid]
    FAILED tests.test_realtest::test_stock_without_earnings_sells_nothing
RI-002-065-interior-gap (RI-002): 4 failed, 46 passed, 0 errors, 0 skipped; target tests/test_realtest.py::test_interior_gap_180_blocks failed: yes; HOLDS; recorded 2026-11-18: 4 failed, 46 passed; code check: ccbot.realtest is ccbot/realtest.py in the worktree; 24.1 s
    FAILED tests.test_realtest::test_drop_input[earnings_interior_gap]
    FAILED tests.test_realtest::test_interior_gap_121_blocks
    FAILED tests.test_realtest::test_interior_gap_180_blocks
    FAILED tests.test_realtest::test_real_interior_gap_mo
baseline tests/test_diff_reports.py: 0 failed, 17 passed, 0 errors, 0 skipped; 1.0 s
RI-013-067-1b (RI-013): 1 failed, 16 passed, 0 errors, 0 skipped; target tests/test_diff_reports.py::test_a_nested_key_and_list_in_dict failed: yes; HOLDS; recorded 2026-11-18: 1 failed, 16 passed; code check: n/a (no module; tests run scripts/diff_reports.py by path via tests/conftest.py REPO, conftest L7); 1.9 s
    FAILED tests.test_diff_reports::test_a_nested_key_and_list_in_dict
TOTAL: 3 probes, 3 hold, 0 not held, 0 anchor missing, 0 error; 97.7 s
exit 0
wall 97.814990117 s
```
- Both runs match 04 Expected result and 05:
  - the same counts and the same FAILED node ids
  - every count equals `recorded`
  - baselines 50/50 and 17/17
- Runtime about 98-101 s (05: about 106 s). 05's `--ref HEAD` was cf13af8 with the script uncommitted; the HEAD run above is b54c1b2, so the committed script probed its own commit.
- After my run, `git worktree list` showed no worktree from the script: only the repo, my i3r2-074-wt and the other sessions' wt-main and wt-rb.

Repo tree never written. Before any run I took SHA-256 of every file in /home/claude/cover-calls outside .git: 977 files (/tmp/claude-0/-home-claude/17414523-55e9-552d-bf38-90b98a4fb4ca/scratchpad/i3r2-repo-before.sha). `git status --porcelain` showed only this uncommitted file (`?? work/074/06-verification.md`). After all runs and after removing my worktree:
```
$ diff i3r2-repo-before.sha i3r2-repo-after.sha && echo IDENTICAL
IDENTICAL
```
977 files, and `git status --porcelain` showed the same single line. Nothing from the script, the tests or the mutations reached the repo tree. (The first run's hash diff showed only the parallel b73d5e3 files; that is now in HEAD.)

check_handoff (03 exists):
```
$ python3 scripts/check_handoff.py 074
sources count (unique URLs in 01-research.md): 11
fact-check rows: 80
totals line: 80 rows -> 63 as-is, 16 fixed, 1 removed
PASS
exit 0
```

## Real-data effect (diff_reports output, pasted)
not required (`git show --stat b54c1b2`: .claude/agents/a1-auditor.md, README.md, logs/implementation/2026-11-19.md, scripts/probe_guardrails.py, tests/test_probe_guardrails.py, work/074/05-build-report.md; none is in TRIGGER/TRIGGER_DIRS, and `git diff --stat cf13af8 b54c1b2 -- ccbot config data` is empty)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-002, RI-003, RI-004, RI-005, RI-006, RI-007, RI-008, RI-009, RI-010, RI-011, RI-012, RI-013
- RI-001 (ESCALATED, the only open/ESCALATED entry): this item has no trading filter. Its selection rules are measured in my own runs: anchor count 1 for 3 of 3 (test 7, plus no ANCHOR MISSING at either ref), and baselines 50 of 50 and 17 of 17 at both refs.
- RI-002: every absent input gives ERROR, ANCHOR MISSING or SETUP, never HOLDS. The test 2 cases (k, l, e, f, i1, i2), test 3, test 4 and test 5 pass, and the missing-key and empty-list branches exit 1 (code read). It is EFFICIENCY, so the step-3 default probe does not apply. No count is defaulted (`counts n/a`, `recorded: none`).
- RI-003: n/a (no calendar).
- RI-004 / RI-005 / RI-006: test 2's TOTAL 13 = 1 + 2 + 3 + 7 is asserted from the script's own output. Every count in this file is pasted command output.
- RI-007: Scope FULL. 01-05 exist, and this is the I3 step.
- RI-008: python3.11 compiles both files. test_safety ran its compile test (python3.10 not on PATH). No `delete=`.
- RI-009: everything ran in a detached worktree outside the repo, removed afterwards. Repo-tree hashes identical before and after (977 files). Commit by exact path, no `-A`.
- RI-010: this item is the guardrail. I re-ran the probes by command, not by hand. The cut-off first run is a near miss of this kind: its 06 had a pipeline line that it could not yet have measured. I replaced it with the line I measured after 07 and the log line were written.
- RI-011: n/a.
- RI-012: no free-text classification (see the I2 audit).
- RI-013: every probe line carries the full counts and every FAILED node id, and the whole output is pasted.

## Pipeline line (step 2)
check_pipeline line: `074: awaiting A1 (FULL)`
Measured after 07 and my `--log` line (`00:28 | I3 | 074 | PASS | sent to audit: yes`) were written: exit 0; `AWAITING A1: 074`; I3 FAIL, INCOMPLETE, LOG TIME, SKIPPED, UNTRACKED CHANGE: none.

## Sent back / sent to Audit
Sent to Audit: work/074/07-audit-task.md. Nothing sent back. The two withdrawn 04 claims (--rootdir and --untracked-files=no "pin" predictions) are recorded above and in 07 item 3.
