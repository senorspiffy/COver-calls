# 05 Build report - 094

Built by I2 on branch `daily-fixes/2026-11-24`, base commit c810804 (on top of 092, 093 and 096, as the plan's build order says; 095 comes after and rebases its print-block change onto this item's new first `if`). Scratch dir: /tmp/claude-0/-home-claude/17dd566b-e13e-58fe-b556-13d450b5acde/scratchpad/I2-094-r1-cj6ujtsu (made with mkdtemp, item 091).

RULE_PATHS: scripts/check_pipeline.py, scripts/check_handoff.py, .claude/agents/a1-auditor.md, .claude/commands/run-item.md and .claude/commands/daily-audit.md are rule paths, so the person's OK is needed in PR review.

## Changes made (file: what changed)
- scripts/check_pipeline.py:
  - New constants `SINGLE_TEXT = "single-branch clone; run git remote set-branches origin '*' && git fetch origin"` and `_GLOB = "refs/heads/*:refs/remotes/origin/*"`, next to `SHALLOW_TEXT`.
  - New `fetch_coverage()` placed before `open_branches`. It follows 03 step 1 (a)-(e) and returns one of "full", "no origin", "no git", SINGLE_TEXT or `git config failed (exit <n>)`. It calls `_git` directly (C2). Its docstring covers C5 (exit 1 is "absent" only because the keys are constants), C6 (detached-HEAD single-branch clone), C7 (any `^` line fails closed) and the two known gaps.
  - `open_branches`: after the `branch -r` checks and before `today =`/`shallow =`, a SINGLE_TEXT or config-failure result is returned as the reason string (C4). One docstring sentence added.
  - `next_id`: when `why is None`, the same check gives `(None, cov)` (C4). One docstring sentence added.
  - `main()` `--next-id`: a SINGLE_TEXT reason prints `--next-id refused: {SINGLE_TEXT}; not counting open branches would risk an ID clash (item 037). Re-run after that.` and returns 2. Other reasons keep today's text.
  - `main()` print block: `if branches == SINGLE_TEXT: print(f"OPEN BRANCHES: not checked ({SINGLE_TEXT})")` comes first, and the 081 str branch is now `elif`.
  - `main()` exit expression: `isinstance(branches, str)` is now `(isinstance(branches, str) and branches != SINGLE_TEXT)`.
  - The `unread` line is unchanged.
  - Module docstring: the OPEN BRANCHES paragraph and the `--next-id` paragraph name item 094, the exit choice and the known gaps.
- scripts/check_handoff.py: only the `check_all` docstring changed. It now names the single-branch line `not checked (open branches: <SINGLE_TEXT>)`, exit 1 (item 094).
- tests/test_pipeline_check.py:
  - `GIT_CENSUS` has the new entry `("fetch_coverage", "_git"): (2, ...)`, and the total goes 47 -> 49 with the comment `+ 2 (094)`. 47 was the post-092/093/096 value: the test passed at base.
  - The fake in `test_open_branches_default_computes_shallow` now answers the fetch read with the glob.
  - New literals: `SINGLE_LINE`, `SINGLE_SENTENCE` and `GLOB_LINE`.
  - New helpers: `_sb_source`, `_sb_clone` (always `file://`, C3), `_next_id_run` and `_fetch_lines`.
  - New tests: `test_single_branch_clone_not_checked`, `test_fetch_coverage_shapes` (S1, S2, S3, S4a, S4b, S5, S6, S7, S9, S10), `test_fetch_coverage_fakes` (S8, S11, S12), `test_config_failure_end_to_end`, `test_check_handoff_single_branch`, `test_single_branch_sentence_same_in_three_files` and `test_check_pipeline_docstring_names_094`.
- .claude/agents/a1-auditor.md, .claude/commands/run-item.md, .claude/commands/daily-audit.md: the step 7 sentence was inserted right after the UNSHALLOW sentence, on the same line. UNSHALLOW was not edited.

File counts (item 012), taken before this 05 existed:
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
0
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
6
```
So: 6 files changed, 0 new code files. The only new file is work/094/05-build-report.md.

## Connectivity check
- [x] Every new function or rule is used. `fetch_coverage` is called from `open_branches` and `next_id`. `SINGLE_TEXT` is read by `fetch_coverage`, `main` (print block, exit expression, `--next-id` text) and the tests. `_GLOB` is read by `fetch_coverage`. The rule sentence is pinned by `test_single_branch_sentence_same_in_three_files`.
- [x] Every input has a source and every output has a consumer. Inputs are `remote.origin.fetch` and `remote.origin.url` from local git config. Outputs:
  - the OPEN BRANCHES line, and IN PR, RULES BRANCH and ID CLASH through `unread`;
  - the `--next-id` stderr text and exit 2;
  - check_handoff `--all` through `_branch_with_handoff`'s existing str path.
- [x] Every branch ends in a defined result:
  - `_git` None on the fetch read or the url read -> "no git" (today's path);
  - fetch exit 0 -> "full" or SINGLE_TEXT;
  - fetch exit 1 -> url read: 1 -> "no origin", 0 -> SINGLE_TEXT, other -> `git config failed (exit n)`;
  - any other fetch exit -> `git config failed (exit n)`;
  - in main, SINGLE_TEXT -> not checked with the exit unchanged, a config failure -> the 081 line with exit 1, and `--next-id` exit 2 in both cases.
- [x] No leftover TODOs or unused files. `git diff | grep -c TODO` adds none. No scratch file is in the repo: the mutation copy is in the scratch dir.
- Missing-data grep (`grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/`): 38 hits, all pre-existing. `git diff --stat -- ccbot/ config/` is empty, so there are no new or changed hits. The same pattern on `git diff -U0 scripts/` gives no hit (exit 1). No dataclass field was added. No `>`/`<` comparison was added: the new code uses only `==`, `!=` and `startswith` on its own constants (RI-012), and there is no substring search of SINGLE_TEXT.
- Absent data never passes:
  - exit 0 with no value (S8) is SINGLE_TEXT, never "full";
  - a failed config read is an error, never "none";
  - "no origin" is returned only when the url key is also absent (exit 1).

## Test output (pasted, not summarized)
Full suite, at the working tree with this build (HEAD 14ae430, after the concurrent `Item 096: A1 result FAIL` commit):
```
$ python3 -m pytest -q
...
=========================== short test summary info ============================
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 866 passed, 1 skipped in 131.75s (0:02:11)
```
Suite: 1 failed, 866 passed, 1 skipped in 131.75s (0:02:11)

The one failure is expected (item 071). It is not a defect of this build. `test_repo_pipeline_has_no_skipped_items` asserts `code == 0` of check_pipeline on HEAD, and the only failing lines in its output are:
```
E         096: A1 FAIL (FULL; sent back, needs a later A1 PASS line (item 042))
E         I3 FAIL: none
E         A1 FAIL: 096
E         INCOMPLETE: none
E         SKIPPED: none
```
096 was sent back by A1 in commit 14ae430 while this build ran. An earlier full run of the same build tree, made before that commit landed, printed `867 passed, 1 skipped in 137.17s (0:02:17)`.

Focused run of the new and related tests (before the full suite):
```
$ python3 -m pytest -q tests/test_pipeline_check.py -k "094 or single_branch or fetch_coverage or config_failure or census or default_computes_shallow or shallow or open_branches or next_id or unshallow"
46 passed, 377 deselected in 13.07s
```

py_compile (RI-008):
```
$ python3.11 -m py_compile scripts/check_pipeline.py scripts/check_handoff.py tests/test_pipeline_check.py; echo "py_compile exit $?"
py_compile exit 0
```

Repo checks on this branch (full refspec: `git config --get-all remote.origin.fetch` -> `+refs/heads/*:refs/remotes/origin/*`, not shallow):
```
$ python3 scripts/check_pipeline.py          # base (c810804, before the edit) vs build
OPEN BRANCHES block identical:
OPEN BRANCHES (not merged into HEAD):
  origin/claude/project-thread-f64g3k: items none; merges cleanly; last commit 2026-11-21 (3 days)
RULES BRANCH: none
ID CLASH: none
$ diff base_cp.txt head_cp.txt
96c96
< 096: awaiting A1 (FULL)
---
> 096: A1 FAIL (FULL; sent back, needs a later A1 PASS line (item 042))
100c100
< AWAITING A1: 096
---
> AWAITING A1: none
107c107
< A1 FAIL: none
---
> A1 FAIL: 096
```
The only differences come from the concurrent 096 A1 FAIL commit. The build's exit is 1 for that reason only (item 071); the base run was 0. There is no `UNTRACKED CHANGE:` entry, and SKIPPED, INCOMPLETE, I3 FAIL and UNREADABLE are all none.
```
$ python3 scripts/check_pipeline.py --next-id; echo "next-id exit $?"
099
next-id exit 0
$ python3 scripts/check_handoff.py --all; echo "check_handoff exit $?"
... no new failures
check_handoff exit 0
```
The check_handoff `--all` output is byte-identical to the base run (`diff` empty).

Mutation probes (m1-m7). They were run in a scratch copy at /tmp/claude-0/-home-claude/17dd566b-e13e-58fe-b556-13d450b5acde/scratchpad/I2-094-r1-cj6ujtsu/mut, never in the repo. Each mutation was applied alone, and only its named detector tests were run:
```
m1: 1 failed in 3.76s | FAILED: test_single_branch_clone_not_checked
m2: 1 failed in 1.26s | FAILED: test_fetch_coverage_shapes[S5]
m3: 1 failed in 4.05s | FAILED: test_fetch_coverage_shapes[S4b]
m4: 4 failed in 2.01s | FAILED: test_uncommitted_step_in_shallow_clone, test_cutoff_missing_in_shallow_clone_not_checked, test_inbox_shallow_clone_not_checked, test_single_branch_clone_not_checked
m5: 1 failed in 0.39s | FAILED: test_fetch_coverage_shapes[S10]
m6: 1 failed in 1.00s | FAILED: test_single_branch_clone_not_checked
m7: 1 failed in 1.02s | FAILED: test_single_branch_clone_not_checked
```
What each mutation does:
- m1: `fetch_coverage` returns "full" first.
- m2: the `^` test is removed.
- m3: `--get` replaces `--get-all`.
- m4: `and branches != SINGLE_TEXT` is removed.
- m5: url exit 0 -> "no origin".
- m6: the `next_id` coverage block is removed.
- m7: the `branches == SINGLE_TEXT` print branch is removed.

Feasibility numbers named by the plan:
- "full" holds for 4 of 12 shapes (S1, S2, S4a, S4b). `test_fetch_coverage_shapes` (10 real-git cases) and `test_fetch_coverage_fakes` (3 cases) all pass. S3, S5, S6, S7, S10, S8 and S11 give SINGLE_TEXT, S9 gives "no origin" and S12 gives `git config failed (exit 128)`.
- 3 of 3 plain `--depth 1` tests stay at `code == 0` in the full suite, and m4 fails all 3.
- F2 example: the full clone gives `093`, while sb, d1s and d1s+unshallow refuse with exit 2 and empty stdout. After the recovery (`git remote set-branches origin *` + `git fetch -q origin`), `--get-all` is exactly `+refs/heads/*:refs/remotes/origin/*\n` and `--next-id` gives `093`. After S5's recovery there is also exactly one glob line.

## Real-data effect (diff_reports output, pasted)
not required (.claude/agents/a1-auditor.md, .claude/commands/daily-audit.md, .claude/commands/run-item.md, scripts/check_handoff.py, scripts/check_pipeline.py, tests/test_pipeline_check.py)

## Deviations from plan
- None in behaviour. Small choices the plan left open:
  - The private constant is named `_GLOB`.
  - `fetch_coverage` also returns "no git" if `_git` gives None on the url read (the same rule as the fetch read, so it is never a silent pass).
  - The literal `GLOB_LINE` and the helpers `_sb_source`, `_sb_clone`, `_next_id_run` and `_fetch_lines` were added as the "shared fixture helper" that the plan allows.
  - `test_check_handoff_single_branch` does both runs: one with `open_branches` faked to SINGLE_TEXT and one in a real `--single-branch` clone.
  - `test_config_failure_end_to_end` adds a control: the unpatched clone's `main()` returns 0, so the 1 comes from the config failure alone.

## Recurring issues checked (item 013)
Checked against each open or ESCALATED entry in logs/recurring-issues.md:
- RI-001 (ESCALATED): the filter-like rule ("full" refspec) has a non-zero dated count: 4 of 12 shapes, 2026-11-24. Pinning tests are `test_fetch_coverage_shapes` and `test_fetch_coverage_fakes`. The exit rule keeps 3 of 3 depth tests green.
- RI-010 (ESCALATED): no log line was typed by hand. The I2 line is written by `check_pipeline.py --log`, and the commit is made by `commit_step.py`.
- RI-014 (OPEN): this item. A single-branch clone is now "not checked", never "none", and a failed config read is an 081 error. The fixtures use real `file://` clones of each shape.
- GUARDED entries touched were also checked: RI-002 (absent value never "full"), RI-006 (census total from the AST test, not hand-totalled), RI-008 (py_compile 3.11), RI-009 (`--next-id`, IN PR and ID CLASH never answer from hidden refs) and RI-012 (equality only, literal in tests).

Guardrail status for A1 to copy on main (item 036):
RI-014: guardrail extended (094): single-branch clone gives OPEN BRANCHES/IN PR/RULES BRANCH/ID CLASH not checked and --next-id refuses; m1-m7 each fail a named test; stays OPEN until 079/081/090/094 are merged and M11 and m1 fail on main.
RI-009: unchanged (GUARDED); 094 closes the single-branch near miss of 2026-11-22.
