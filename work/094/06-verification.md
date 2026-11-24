# 06 Verification - 094
Verdict: FAIL (round 1; earlier rounds: none)
Sent back to: I1 I2

I3 read the branch copies of .claude/agents/i3-verifier.md and .claude/commands/run-item.md, logs/recurring-issues.md, and everything in work/094/. Scratch dir (mkdtemp, item 091): /tmp/claude-0/-home-claude/17dd566b-e13e-58fe-b556-13d450b5acde/scratchpad/I3-094-r1-t0_brdgs, with my own worktree of head 73fcc6f at `wt/` (094's I2 commit is 8a6cff2; 73fcc6f adds only 096's tests/test_agent_tools.py and work/096 lines on top). Every mutation ran in that worktree, never in the repo checkout; `git status --short` in it was empty after each restore.

## I1 audit (plan vs research)
- The plan follows 03 step by step: steps 1-9 each have a Files line and a Rule trace row. C1 (anchors by name), C2 (census +2 from the AST count), C3 (`file://` clones), C4 (coverage read only after a successful branch read), C5-C7 (docstring notes) are sourced (git-config, git-clone pages quoted in Extra research) or are repo facts. m7 is an added mutation, which is allowed. No unsourced addition.
- **Problem P1 (I1).** 03's Missing inputs table has the row "`remote.origin.fetch` / `remote.origin.url` | git exits other than 0 or 1 | `OPEN BRANCHES: git config failed (exit n) (item 081)`, exit 1". The plan's Rule trace maps it to `test_fetch_coverage_fakes[S12]` and `test_config_failure_end_to_end`, and both fail only the **fetch** read. The url half (fetch exit 1, then `git config --get remote.origin.url` exits other than 0 or 1, 03 step 1(d) "Any other -> `git config failed (exit n)`") has no test and no mutation in the plan. See m9 below: the branch can be turned into "no origin" (today's path, so a possible false `OPEN BRANCHES: none`) and the whole suite stays green. That is the exact failure this item and RI-014/081 exist to prevent ("a failed git read is never none"), and 04/05 both claim it ("a failed config read is an error, never 'none'").

## I2 audit (build vs plan)
- scripts/check_pipeline.py: `SINGLE_TEXT`, `_GLOB`, `fetch_coverage()` (a)-(e), the `open_branches` and `next_id` calls after the branch read, the `--next-id` SINGLE_TEXT text, the new first `if` in the print block, and the exit expression `(isinstance(branches, str) and branches != SINGLE_TEXT)` match Files 1 line by line. `unread` is unchanged. Comparisons are `==`, `!=` and `startswith` on its own constants only (RI-012).
- scripts/check_handoff.py: docstring only, as planned.
- Three rule files: the step 7 sentence, byte for byte, right after UNSHALLOW (UNSHALLOW unchanged in `git show 8a6cff2`).
- tests: census entry and 47 -> 49 with `+ 2 (094)`; the one fake in `test_open_branches_default_computes_shallow` answers the glob; the seven planned tests exist with the planned assertions and use `file://` clones. The 05 deviations (the `_GLOB` name, "no git" on a None url read, helpers, the extra control in the end-to-end test, two runs in the check_handoff test) are inside what the plan left open.
- Connectivity, re-done from the diff: `fetch_coverage` is called from `open_branches` and `next_id`; `SINGLE_TEXT` is read by `fetch_coverage`, `open_branches`, `next_id`, `main` (print, exit, `--next-id`) and the tests; `_GLOB` by `fetch_coverage`. Each branch of `fetch_coverage` ends in one of the five documented strings (probe below shows the url-failure branch returns `git config failed (exit 128)` as built). No TODO added.
- 05's grep reasons check out: `git diff --stat 8a6cff2^ 8a6cff2 -- ccbot/ config/` is empty, so the 38 ccbot/ hits are pre-existing; no dataclass field, no `>`/`<` added.
- **Problem P2 (I2).** Following P1: add the missing test, e.g. a `test_fetch_coverage_fakes` case S13 with `_patched_git` answering `("config", "--get-all", "remote.origin.fetch")` with `("", 1)` and `("config", "--get", "remote.origin.url")` with `("", 128)`, expecting `git config failed (exit 128)`; and show in 05 that m9 (below) fails it.

## Tests re-run (output)
Full suite, my worktree of head 73fcc6f:
```
$ python3 -m pytest -q
...
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 870 passed, 1 skipped in 138.45s (0:02:18)
```
The one failure is the repo pipeline test; its non-none lines are `094: in progress (FULL: next 06)` (this step), `096: A1 FAIL (...)` and `A1 FAIL: 096` (096 is being re-verified concurrently, not 094's). INCOMPLETE, SKIPPED and I3 FAIL are none.

Python 3.10/3.11 (RI-008): `tests/test_safety.py -k oldest` -> `1 passed` (python3.11 on PATH, python3.10 absent); it did not skip.

check_handoff (re-run at head):
```
$ python3 scripts/check_handoff.py 094
sources count (unique URLs in 01-research.md): 9
fact-check rows: 55
totals line: 55 rows -> 50 as-is, 4 fixed, 1 removed
PASS
exit 0
```

Repo refspec here: `git config --get-all remote.origin.fetch` -> `+refs/heads/*:refs/remotes/origin/*`, `--is-shallow-repository` false, so the repo's own OPEN BRANCHES output takes the full path (the same as 05's).

Mutations (each applied alone to scripts/check_pipeline.py in the worktree, then restored from a saved copy):
```
m1 fetch_coverage returns "full" first        -> 1 failed: test_single_branch_clone_not_checked
m2 `^` test removed                           -> 1 failed, 9 passed: test_fetch_coverage_shapes[S5]
m3 --get instead of --get-all                 -> 1 failed, 9 passed: test_fetch_coverage_shapes[S4b]
m4 `and branches != SINGLE_TEXT` removed      -> 4 failed: test_uncommitted_step_in_shallow_clone, test_cutoff_missing_in_shallow_clone_not_checked, test_inbox_shallow_clone_not_checked, test_single_branch_clone_not_checked
m5 url exit 0 -> "no origin"                  -> 1 failed, 9 passed: test_fetch_coverage_shapes[S10]
m6 next_id coverage block disabled            -> 1 failed: test_single_branch_clone_not_checked
m7 SINGLE_TEXT print branch removed           -> 1 failed: test_single_branch_clone_not_checked
m8 (I3, RI-002 default) exit 0 with no value counts as full (`not values or any(...)`) -> 1 failed, 2 passed: test_fetch_coverage_fakes[S8]
m10 (I3) open_branches config-failure return removed -> 1 failed: test_config_failure_end_to_end
m9 (I3) url read exit other than 0/1 -> "no origin" -> SURVIVES: whole suite with the repo test deselected: 870 passed, 1 skipped, 1 deselected in 132.61s (0:02:12)
```
m9 probe (fetch read `("", 1)`, url read `("", 128)`, other git calls real):
```
as built: fetch_coverage: 'git config failed (exit 128)' | open_branches: 'git config failed (exit 128)'
m9:       fetch_coverage: 'no origin' | open_branches: [{'ref': 'origin/claude/project-thread-f64g3k', ...}]
```
So the built code is right, but nothing pins it: under m9 a failed url read silently takes today's path, and in a clone with no fetch key (no origin refs) that prints `OPEN BRANCHES: none`.

## Real-data effect (diff_reports output, pasted)
not required (.claude/agents/a1-auditor.md, .claude/commands/daily-audit.md, .claude/commands/run-item.md, scripts/check_handoff.py, scripts/check_pipeline.py, tests/test_pipeline_check.py)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001 (ESCALATED: the 4-of-12 shapes count re-run by test_fetch_coverage_shapes/fakes, all pass, and the 3-of-3 depth tests stay `code == 0`, m4 fails all 3; matches 03/04/05), RI-002 (m1 and m8 put back "full" for an unknown refspec and each fails a test; but the url-failure branch is unpinned, m9, P1/P2), RI-010 (ESCALATED: no log line typed by hand; mine is written by `--log` after this file), RI-014 (OPEN, this item's family: the fetch-read failure is an 081 error and pinned; the url-read failure is not pinned, m9 -> FAIL), RI-009 (--next-id, IN PR, ID CLASH refuse or say not checked in sb, d1s, d1s+unshallow; recovery gives 093), RI-012 (equality on one constant; S7 and S11 are negative cases with the glob inside other text, both SINGLE_TEXT), RI-008 (py_compile test passed on 3.11).

## Pipeline line (step 2)
check_pipeline line: `094: I3 FAIL (FULL; sent back to I1 I2, needs a later PASS round in 06 (item 071))`

## Sent back / sent to Audit
FAIL, round 1. Sent back to I1 and I2; no 07 written.
- I1 (P1): add to the Rule trace and Guardrail tests a test for the url half of 03's "git exits other than 0 or 1" Missing-inputs row (fetch exit 1, url exit not in (0, 1) -> `git config failed (exit n)`), and add m9 to the mutation list.
- I2 (P2): build that test (e.g. `test_fetch_coverage_fakes[S13]`), and in 05 show that m9 fails it. Nothing else needs to change.
