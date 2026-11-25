# 06 Verification - 095
Verdict: PASS (round 1)
Sent back to: none

I3 read the branch copies of .claude/agents/i3-verifier.md and .claude/commands/run-item.md, logs/recurring-issues.md, and everything in work/095/. Scratch dir (mkdtemp, item 091): /tmp/claude-0/-home-claude/17dd566b-e13e-58fe-b556-13d450b5acde/scratchpad/I3-095-r1-kkm7m91y. Head commit ed7b80c (095's I2 commit, on base 5bc02ca). Mutations ran in `tree/` there (`git archive ed7b80c`), never in the repo; the file was restored after each and `cmp` with the repo copy was clean.

## I1 audit (plan vs research)
- Every 03 map step (1-5) and every Missing-inputs row has a plan line in 04's Rule trace. The only drops are 03 step 4's "merge 094's sentence" (C2: 094's plan keeps its own sentence and count test; merging would break `test_single_branch_sentence_same_in_three_files`) and 03 #50 / removed #9, #49. All are reasoned.
- C1 (an uncommitted 05/06 must stay INCOMPLETE in a shallow clone, as `_rule_seen` gives `(None, "")` in a full clone too) is an addition. It is sourced: the git-ls-tree docs, the repo's own `uncommitted_steps()` (077) and its tests. It makes the plan stricter, not looser. C3 reuses the 084 fixtures and adds a real `--depth 1 --no-single-branch` clone, which the request asked for. No unsourced addition.

## I2 audit (build vs plan)
- scripts/check_pipeline.py matches Files 1 line by line (diff 5bc02ca..ed7b80c):
  - `_unsure` checks `env != SHALLOW_TEXT` first, by equality, then `committed is None or work/<ID>/<step file> in committed`.
  - `_head_work_files` returns None on a failed ls-tree.
  - Gate branches: TIMED, TESTS (only with the I2_BEFORE `all(...)`), LOG BATCH, Suite, round headings (keyed on the loop's step) and VERDICT. In each, `elif unsure(...)` sits between `seen is False` and the strict branch.
  - Only I2 is removed from `bad`.
  - `held` is added to the unrelated dict, and is None when ls-tree fails.
  - In `main()`: `unchecked` and `committed` (shallow only), the NOT CHECKED line (shallow only), `or unchecked` in the exit, the `folded` sub-line, the per-ref error filter on `isinstance(held, int)`, and the summary when k >= 1.
  - Docstrings are updated as 03 step 3 asks.
- The 3 rule files have the new UNSHALLOW sentence, byte for byte (`test_unshallow_sentence_same_in_three_files` passes; `grep -c "INCOMPLETE NOT CHECKED"` gives 1 in each). 094's sentence is untouched.
- Tests: T-a, T-a2 ... T-a6, T-b and T-b2 exist with the planned assertions. T18, T19, e1 and the non-UTF-8 test are edited as planned. The census goes from 49 to 50.
- 05's single deviation (`unchecked=None` moves nothing, strict) is fail-closed and is pinned in T-a6.
- Connectivity, re-done by grep:
  - `_unsure` is called only via `unsure()`, at 6 call sites, 7 evaluations with the round-heading loop.
  - `_head_work_files` is called once, in `main()`, only when shallow.
  - `held` is read at L2219 and L2220. `folded` feeds the sub-line, the error filter and the summary.
  - check_handoff.py reads neither `held` nor `incomplete`.
  - No TODO.
- Grep reasons in 05: `git diff --stat 5bc02ca ed7b80c -- ccbot/ config/` is empty, so the 38 ccbot/ hits are pre-existing. The 2 added script hits are explained correctly: one is a None collector, which is strict; the other is the existing exit expression.
- RI-012: classification uses `env ==` / `!=` and the `held` key with `isinstance`. It never matches error text, so no in-text negative test is needed. No simulator or picker is involved (item 062 n/a).
- Observation for A1 (not a FAIL): the plan pins the TESTS and VERDICT moves end to end (the 083 shape) and T-a6 covers the unit. The TIMED, LOG BATCH, Suite and round-heading `elif unsure` branches have no test of their own. My probe replaced the TIMED branch with `elif False` and tests/test_pipeline_check.py stayed green (431 passed, 2 skipped). Removing such a branch fails closed: the entry goes back to INCOMPLETE, which is today's behaviour, exit 1 either way. The plan did not ask for these tests, so the build matches the plan. This is a possible follow-up.

## Tests re-run (output)
```
$ python3 -m pytest -q          (repo, head ed7b80c)
........................................................................ [  8%]
...
..................                                                       [100%]
881 passed, 1 skipped in 158.87s (0:02:38)
```
Same count as 05 (881 passed, 1 skipped). `tests/test_safety.py::test_every_py_compiles_on_oldest_python` ran and did not skip: `1 passed in 0.23s` (python3.11 on PATH; python3.10 is not).

`python3 scripts/check_handoff.py 095` (exit 0):
```
sources count (unique URLs in 01-research.md): 8
fact-check rows: 53
totals line: 53 rows -> 41 as-is, 10 fixed, 2 removed
PASS
```

Mutations, in my scratch tree. Each named test was run alone:
```
M1 test_shallow_gated_entries_not_checked -> 1 failed in 1.56s
M1 test_depth1_clone_083_shape_not_incomplete -> 1 failed in 8.62s
M2 test_rule_not_seen_shallow_and_no_git -> 1 failed in 0.94s
M3 test_shallow_uncommitted_step_stays_incomplete -> 1 failed in 0.58s
M4 test_shallow_exact_tests_entry_stays_incomplete -> 1 failed in 0.52s
M5 test_shallow_gated_entries_not_checked -> 1 failed in 0.54s
M6 test_shallow_merged_refs_fold_to_one_line -> 1 failed in 0.98s
M7 test_unrelated_branch_with_work_is_branch_error -> 1 failed in 0.73s
M8 test_shallow_fold_held_unknown_keeps_own_error -> 1 failed in 0.94s
M11 test_shallow_three_readers_not_checked -> 1 failed in 1.04s
RI002 test_unsure_unit_and_head_tree_failure -> 1 failed in 0.43s
restored True
```
What each mutation does:
- M1: `_unsure` returns False.
- M2: `env is None` instead of `!= SHALLOW_TEXT`.
- M3: `return True` without the committed check.
- M4: the TESTS branch without the I2_BEFORE `all(...)`.
- M5: `or unchecked` removed from the exit.
- M6: fold `if False:`.
- M7: fold on `unrelated` alone.
- M8: the per-ref error filter without `isinstance(held, int)`.
- M11: `shallow = False`.
- RI002: `_head_work_files` returns `set()` instead of None when ls-tree fails. This puts back a default for an unknown read.

All 11 fail their named test.

Step 5 checks, re-done:
- Full clone (this repo, ed7b80c): old script (`git show 5bc02ca:scripts/check_pipeline.py`) and new script both exit 0, 119 lines each. `diff` is empty (exit 0).
- Real depth-1 `--no-single-branch` clone. Source: a bare repo in my scratch dir holding this repo's 31 origin refs as heads, with daily-fixes/2026-11-24 set to ed7b80c. `--is-shallow-repository` prints true. Old and new script both exit 1. The whole diff:
  - 29 per-ref sub-lines become 1 line, `  shallow clone: 29 ref(s) with no merge base not checked (...)`.
  - 29 per-ref BRANCH ERRORs (108 to 796 files each) become 1 line, `BRANCH ERROR: shallow clone; 29 of 29 ref(s) hold files on checked paths, not checked (...)`. So 58 lines become 2.
  - `INCOMPLETE: 083 (...)` becomes `INCOMPLETE: none` plus `INCOMPLETE NOT CHECKED: 083 (log line for I2 ...; 06 Verdict is PASS but has no 'Sent back to: none' line (item 071)); rule seen not checked (...)`: 1 item, 2 entries.
  - These match 05. 03 counted 28 on 2026-11-22; there is one more branch today.
- Plain `--depth 1` (single-branch) clone of the same source, exit 1: `OPEN BRANCHES: not checked (single-branch clone; ...)` (094), `INCOMPLETE: none`, and the same `INCOMPLETE NOT CHECKED: 083 (...)` line.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat 5bc02ca ed7b80c`: .claude/agents/a1-auditor.md, .claude/commands/daily-audit.md, .claude/commands/run-item.md, scripts/check_pipeline.py, tests/test_pipeline_check.py, logs/implementation/2026-11-24.md, work/095/05-build-report.md; none is in TRIGGER or TRIGGER_DIRS, so I made no head run)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001 (ESCALATED): both selectors re-run on real data today. The gated-entry selector gives 1 item (083) with 2 of 2 entries. The fold gives 29 of 29 refs, k = 29. Fixtures pin each: T-a and T-a2; T-b with 3 of 3; T18 with 1 of 1; T19 with 0 held, no BRANCH ERROR and exit 0. Each has its empty result: NOT CHECKED `none`, and no sub-line in a full clone. RI-010 (ESCALATED): no log line typed by hand. Mine is written by `--log` after this file and committed by commit_step.py. RI-014 (OPEN): this item. M11 still fails T18 by name, and the full-clone whole-output diff is empty. RI-002 (GUARDED): a failed HEAD tree read, a failed ls-tree and an unknown anchor are never a pass, 0 or none. The RI002 mutation, M3 and M8 each fail a test, and the exit stays 1. RI-012 (GUARDED): env equality and the `held` key, never error text. RI-008 (GUARDED): the compile test passed on 3.11. RI-009 (GUARDED): folded refs keep their names, and 094's single-branch path is unchanged. RI-004, RI-005 and RI-006: the counts come from command output, not by hand.

## Pipeline line (step 2)
check_pipeline line: `095: awaiting A1 (FULL)`

## Sent back / sent to Audit
Sent to Audit. Audit task: work/095/07-audit-task.md.
