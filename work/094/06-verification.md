# 06 Verification - 094
Verdict: PASS (round 2; earlier rounds: round 1 FAIL)
Sent back to: none

I3 read the branch copies of .claude/agents/i3-verifier.md and .claude/commands/run-item.md, logs/recurring-issues.md, and everything in work/094/. Scratch dir (mkdtemp, item 091): /tmp/claude-0/-home-claude/17dd566b-e13e-58fe-b556-13d450b5acde/scratchpad/I3-094-r1-t0_brdgs, with my own worktree of head 73fcc6f at `wt/` (094's I2 commit is 8a6cff2; 73fcc6f adds only 096's tests/test_agent_tools.py and work/096 lines on top). Every mutation ran in that worktree, never in the repo checkout; `git status --short` in it was empty after each restore.

## I1 audit (plan vs research)
- The plan follows 03 step by step: steps 1-9 each have a Files line and a Rule trace row. C1 (anchors by name), C2 (census +2 from the AST count), C3 (`file://` clones), C4 (coverage read only after a successful branch read), C5-C7 (docstring notes) are sourced (git-config, git-clone pages quoted in Extra research) or are repo facts. m7 is an added mutation, which is allowed. No unsourced addition.
- **Problem P1 (I1).** 03's Missing inputs table has the row "`remote.origin.fetch` / `remote.origin.url` | git exits other than 0 or 1 | `OPEN BRANCHES: git config failed (exit n) (item 081)`, exit 1". The plan's Rule trace maps it to `test_fetch_coverage_fakes[S12]` and `test_config_failure_end_to_end`, and both fail only the **fetch** read. The url half (fetch exit 1, then `git config --get remote.origin.url` exits other than 0 or 1, 03 step 1(d) "Any other -> `git config failed (exit n)`") has no test and no mutation in the plan. See m9 below: the branch can be turned into "no origin" (today's path, so a possible false `OPEN BRANCHES: none`) and the whole suite stays green. That is the exact failure this item and RI-014/081 exist to prevent ("a failed git read is never none"), and 04/05 both claim it ("a failed config read is an error, never 'none'").

- **Round 2 (I1).** 04's `## Round 2` fixes P1: the Missing-inputs row is split into the fetch read (S12, end-to-end, m10) and the url read (R2-C1 S13, optional S14, R2-C2 open_branches assert, m9 and m9b). Its only extra research is the git-config exit codes (1 absent, 3 invalid file; 128 from `die()`), quoted with its URL, and the reason both keys must be faked. R2-C3 rules out any code or census change. No unsourced addition.

## I2 audit (build vs plan)
- scripts/check_pipeline.py: `SINGLE_TEXT`, `_GLOB`, `fetch_coverage()` (a)-(e), the `open_branches` and `next_id` calls after the branch read, the `--next-id` SINGLE_TEXT text, the new first `if` in the print block, and the exit expression `(isinstance(branches, str) and branches != SINGLE_TEXT)` match Files 1 line by line. `unread` is unchanged. Comparisons are `==`, `!=` and `startswith` on its own constants only (RI-012).
- scripts/check_handoff.py: docstring only, as planned.
- Three rule files: the step 7 sentence, byte for byte, right after UNSHALLOW (UNSHALLOW unchanged in `git show 8a6cff2`).
- tests: census entry and 47 -> 49 with `+ 2 (094)`; the one fake in `test_open_branches_default_computes_shallow` answers the glob; the seven planned tests exist with the planned assertions and use `file://` clones. The 05 deviations (the `_GLOB` name, "no git" on a None url read, helpers, the extra control in the end-to-end test, two runs in the check_handoff test) are inside what the plan left open.
- Connectivity, re-done from the diff: `fetch_coverage` is called from `open_branches` and `next_id`; `SINGLE_TEXT` is read by `fetch_coverage`, `open_branches`, `next_id`, `main` (print, exit, `--next-id`) and the tests; `_GLOB` by `fetch_coverage`. Each branch of `fetch_coverage` ends in one of the five documented strings (probe below shows the url-failure branch returns `git config failed (exit 128)` as built). No TODO added.
- 05's grep reasons check out: `git diff --stat 8a6cff2^ 8a6cff2 -- ccbot/ config/` is empty, so the 38 ccbot/ hits are pre-existing; no dataclass field, no `>`/`<` added.
- **Problem P2 (I2).** Following P1: add the missing test, e.g. a `test_fetch_coverage_fakes` case S13 with `_patched_git` answering `("config", "--get-all", "remote.origin.fetch")` with `("", 1)` and `("config", "--get", "remote.origin.url")` with `("", 128)`, expecting `git config failed (exit 128)`; and show in 05 that m9 (below) fails it.

- **Round 2 (I2).** `git diff c6d0206 537ac82 -- scripts/ ccbot/ config/ .claude/` is empty; only tests/test_pipeline_check.py changed in code, as R2-C3 says. `FETCH_KEY`/`URL_KEY`, the `answers` dict parameter, S8/S11/S12 unchanged in answer and expectation, S13 (`("", 1)` / `("", 128)` -> `"git config failed (exit 128)"`) and S14 (url exit 3) as literals with `==` (RI-012), the docstring clauses, and the R2-C2 assert (open_branches returns the error string, main prints `OPEN BRANCHES: git config failed (exit 128) (item 081)` and returns 1) match R2-C1/R2-C2 line by line. 05 round 2 lists no deviation and none is found. P2 is fixed: m9 now fails 3 tests (below).

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

## Tests re-run (round 2)
Scratch dir (mkdtemp, item 091): /tmp/claude-0/-home-claude/17dd566b-e13e-58fe-b556-13d450b5acde/scratchpad/I3-094-r2-dkdo9c0v, my own worktree of head 537ac82 at `wt/` (`--is-shallow-repository` false; refspec `+refs/heads/*:refs/remotes/origin/*`). Mutations ran only there, by `mut.py` in the scratch dir, which restores the file after each; `git status --short` in wt was `''` afterwards.

Full suite, worktree of 537ac82:
```
$ python3 -m pytest -q -p no:cacheprovider
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 872 passed, 1 skipped in 134.80s (0:02:14)
```
Same counts as 05 round 2 (872 = 870 + S13 + S14). The one failure is the repo pipeline test (`code == 0`), and its non-none lines in my `python3 scripts/check_pipeline.py` run (exit 1) were `094: I3 FAIL (...)` and `I3 FAIL: 094` (this item's round-1 verdict, before this file), `095`/`097`/`098: in progress (FULL: next 05)` (other items), plus the INBOX line below.

INBOX line (asked by the orchestrator): `INBOX: not checked (2026-11-24.md added in 9419d56; its templates/daily-audit.md has no ## Inbox)` does not affect the exit code or the repo test. `inbox_section()` in the worktree returns `('not checked (2026-11-24.md added in 9419d56; ...)', False)`; the second value is `inbox_bad`, and `main` adds to the exit only `if inbox_bad:` (scripts/check_pipeline.py line 2186), so a `not checked` gate result never gives exit 1. `test_repo_pipeline_has_no_skipped_items` asserts `code == 0`, `RESEARCH CODE: none`, `061: complete` and `I3 FAIL: none`, nothing about INBOX. The line comes from main's daily report (9419d56), not from 094, and 094 changes no INBOX code.

Python 3.10/3.11 (RI-008): `tests/test_safety.py -k oldest` -> `1 passed, 8 deselected` (python3.11 on PATH, python3.10 absent); it did not skip.

check_handoff (re-run at head):
```
$ python3 scripts/check_handoff.py 094
sources count (unique URLs in 01-research.md): 9
fact-check rows: 55
totals line: 55 rows -> 50 as-is, 4 fixed, 1 removed
PASS
exit 0
```

Mutations m1-m10 and m9b, each alone on scripts/check_pipeline.py, `pytest tests/test_pipeline_check.py -k "fetch_coverage or single_branch or shallow_clone or config_failure or depth"`:
```
m1: 14 failed, 8 passed, 403 deselected | test_single_branch_clone_not_checked, shapes[S3,S5,S6,S7,S9,S10], fakes[S8,S11,S12,S13,S14], test_config_failure_end_to_end, test_check_handoff_single_branch
m2: 1 failed, 21 passed | test_fetch_coverage_shapes[S5]
m3: 7 failed, 15 passed | shapes[S4b], fakes[S8,S11,S12,S13,S14], test_config_failure_end_to_end
m4: 4 failed, 18 passed | test_uncommitted_step_in_shallow_clone, test_cutoff_missing_in_shallow_clone_not_checked, test_inbox_shallow_clone_not_checked, test_single_branch_clone_not_checked
m5: 1 failed, 21 passed | test_fetch_coverage_shapes[S10]
m6: 2 failed, 20 passed | test_single_branch_clone_not_checked, test_config_failure_end_to_end
m7: 1 failed, 21 passed | test_single_branch_clone_not_checked
m8: 1 failed, 21 passed | test_fetch_coverage_fakes[S8]
m9: 3 failed, 19 passed | test_fetch_coverage_fakes[S13], test_fetch_coverage_fakes[S14], test_config_failure_end_to_end
m9b: 3 failed, 19 passed | test_fetch_coverage_fakes[S13], test_fetch_coverage_fakes[S14], test_config_failure_end_to_end
m10: 1 failed, 21 passed | test_config_failure_end_to_end
```
m9 (the round-1 survivor) and m9b now fail S13, S14 and the end-to-end assert, as 05 round 2 says. m1, m3 and m6 fail more tests than in round 1 because the new cases and the `-k` filter cover them; each still fails its named test. RI-002: m8 and m9 put back a default (exit 0 with no value counts as "full"; a failed url read counts as "no origin") and each fails a test. No mutation survives.

## Real-data effect (diff_reports output, pasted)
not required (.claude/agents/a1-auditor.md, .claude/commands/daily-audit.md, .claude/commands/run-item.md, scripts/check_handoff.py, scripts/check_pipeline.py, tests/test_pipeline_check.py)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001 (ESCALATED: no new filter rule; the 4-of-12 shapes and 3-of-3 depth counts re-run in round 2 by the shapes/fakes/depth tests, all pass; 05's numbers match), RI-002 (m1, m8, m9, m9b put back a default value for a failed or unknown read and each fails >= 1 test; round 1's m9 gap is closed), RI-010 (ESCALATED: no log line typed by hand; mine is written by `--log` after this file and committed by commit_step.py), RI-014 (OPEN, this item's family: both git config reads now pinned as 081 errors, never none: S12, S13, S14, end-to-end; m9, m10 fail), RI-009 (GUARDED: --next-id refuses on SINGLE_TEXT/config failure, m6 fails 2 tests), RI-012 (exact `==` on literals; S7 and S11 negative cases with the glob inside other text), RI-008 (py_compile test passed on 3.11), RI-007 and RI-013 (GUARDED: no step skipped; no real-data numbers in this item)

## Pipeline line (step 2)
check_pipeline line (round 1): `094: I3 FAIL (FULL; sent back to I1 I2, needs a later PASS round in 06 (item 071))`
check_pipeline line: `094: awaiting A1 (FULL)`
(round 2, run after this file, 07 and my `--log` line were written; exit 0, `I3 FAIL: none`, INCOMPLETE, SKIPPED, UNTRACKED CHANGE none; LOG TIME and LOG BATCH do not name 094; INBOX line unchanged, still exit 0)

## Sent back / sent to Audit
FAIL, round 1. Sent back to I1 and I2; no 07 written.
- I1 (P1): add to the Rule trace and Guardrail tests a test for the url half of 03's "git exits other than 0 or 1" Missing-inputs row (fetch exit 1, url exit not in (0, 1) -> `git config failed (exit n)`), and add m9 to the mutation list.
- I2 (P2): build that test (e.g. `test_fetch_coverage_fakes[S13]`), and in 05 show that m9 fails it. Nothing else needs to change.

Round 2: PASS. P1 (I1) and P2 (I2) are fixed; nothing is sent back. Sent to Audit: yes, work/094/07-audit-task.md.
