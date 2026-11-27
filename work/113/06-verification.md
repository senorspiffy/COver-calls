# 06 Verification - 113
Verdict: PASS (round 1)
Sent back to: none
Scratch dir: /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i3-113-r1-cu6ozm3z

The pyc dirs `pyc-gi3emwq1` (suite and mutants) and `pyc-qmf7218k` (the `wt2` check) were made inside it with the same mkdtemp command (prefix `pyc-`).

Verified commit: 8529267 (I2 commit of 113). I made 2 detached worktrees of 8529267 inside my own scratch dir: `wt` for the full suite and the mutants, `wt2` for the -rs check. Both were removed afterwards (`git worktree remove`). I ran no `git stash`. The main checkout was only read, apart from the two base/head `check_pipeline.py` runs (`python3 -B`, no mutated file). While I worked, the orchestrator committed 3794ef2 (112 I1) and 7b11624 (111 I2). They touch none of this item's 4 files (`git diff --stat 8529267 HEAD`: logs, tests/test_agent_tools.py, work/111, work/112). The main checkout also has another item's uncommitted edit to tests/test_pipeline_check.py (an item-112 SITE_ROWS change). It is not mine and I left it alone. My runs used the clean `wt` at 8529267, so that edit was not tested here.

## I1 audit (plan vs research)
- T-RB, D-RB and D-110 are carried word for word into 04 (Files 1-3). The Rule trace covers every 03 map step (0-6), the Missing inputs rows and the 001 row. Nothing from 03 is dropped. The 001 row is DROPPED with a reason that holds: no 001 rule changes.
- C1, C2 and C3 are additions with sources: git-grep doc (Extra research 1), git-branch doc plus docstring L238-239 (Extra research 2), and tests L1284 (Extra research 3). None changes 03's texts.
- **Finding for Audit (plan defect, not a FAIL):** C1 decides "known site vs new caller" by comparing path plus line text with HEAD's own hits. A ref that is simply *behind* HEAD still holds the old text of a site this branch already changed, so it counts as a "new caller". I reproduced this. `git merge-base origin/main HEAD` = 94a20a5, and 94a20a5:scripts/check_pipeline.py:760 already reads `scope, opened, (waived, waived_line, who) = parse_request(req_text)`. `git diff --stat 94a20a5 origin/main` lists only logs/audit/2026-11-26.md and logs/efficiency/2026-11-26.md. So origin/main added no parse_request caller, and a merge-base-aware rule would have given k = 0, which means step 2 (remove `who`). Because of C1, I2 took step 2-alt. That path is safe and allowed: it is 04's conservative path, and request.md's "Done looks like" accepts "kept with a comment". I2 flagged it openly in 05 Deviations 1. So the verdict stays PASS, with a follow-up for Audit (07).

## I2 audit (build vs plan)
Line by line against 04 Files 1-5 (`git diff a1719eb 8529267 -- scripts templates tests`):
- templates/build-plan.md: T-RB is on the line right after `## Tests and checks` (L6). templates/build-report.md: T-RB is on the line right after `## Deviations from plan` (L15). I checked both against 03's fenced T-RB block in a script: `splitlines().count(T-RB)` = 1 in each file.
- scripts/check_pipeline.py: docstring only, no code line changed.
  - D-110 is after "...never to _STATS (the I2 field refuses it)."
  - D-RB is after "Listed, not an error."
  - Whitespace-normalised, both match 03's blocks exactly (script check: `D-RB True D-110 True`).
  - The 2-alt parse_request docstring is 03's 2-alt text, filled in with `<ref>` = origin/main. It keeps the existing L630 sentence and adds the deferral on 2 lines (05 Deviations 2). This is a faithful fill of 03's template text.
- tests/test_pipeline_check.py:
  - `RB_TEMPLATE_LINE` evaluates equal to 03's T-RB (script check: `True`).
  - `test_rules_branch_template_line` (×2), `test_rules_branch_docstring_names_no_merged` and `test_parse_request_docstring_defers_who_removal` are added as 04 specifies.
  - The 110 test gains the 3 asserts. Its existing asserts are unchanged.
  - L1974/L1976 are unchanged (2-alt).
- Step 0, re-run by me on 2026-11-26 in /home/claude/fix, after `git fetch origin` (exit 0):
  - `--is-shallow-repository` = `false`. Fetch refspec = `+refs/heads/*:refs/remotes/origin/*`.
  - `--no-merged HEAD` lists `origin/claude/project-thread-f64g3k` and `origin/main` (edfa114), so n = 2.
  - Per-ref `git grep -n parse_request <ref> -- scripts tests`: project-thread exits 1 with empty stderr. origin/main exits 0, and its 4 three-target hits are 637, 650, 760 and tests 1920, the same hits as 05.
  - 0c `merge-base --is-ancestor origin/daily-fixes/2026-11-25 HEAD` exits 0.
  - Under C1 as written, k = 1 (L760). This matches 05.
- Connectivity: every new test is collected (`--collect-only`: `test_rules_branch_template_line[templates/build-plan.md]`, `[templates/build-report.md]`, `test_rules_branch_docstring_names_no_merged`, `test_parse_request_docstring_defers_who_removal`, `test_check_pipeline_docstring_records_110_no_go`). Each new text has a pin and a killed mutant (below). No new code path, no TODO.
- Grep reasons in 05: the missing-data grep gives 38 pre-existing ccbot/ hits, and ccbot/ is untouched (the diff stat has no ccbot file). That reason holds.
- The item adds no text-matching classifier (RI-012 / item 059 rule: n/a, no code). It adds no simulator or replay (item 062: n/a). It changes no 001 rule the person follows.
- The item is EFFICIENCY, not a BUG, so the fix-plus-guardrail check, the RI-001 feasibility re-runs and the RI-002 default-restore probe do not apply. The template count (1 per file) was re-run, above.
- check_handoff, re-run by me (exit 0):
```
sources count (unique URLs in 01-research.md): 3
fact-check rows: 44
totals line: 44 rows -> 37 as-is, 7 fixed, 0 removed
PASS
```
- Whole-output check, re-run by me in /home/claude/fix. Base = `git show a1719eb:scripts/check_pipeline.py`, head = 8529267's script. Both runs exited 0, and `diff` printed nothing (exit 0). The head output includes `RULES BRANCH: none`, `STASH: none`, `UNTRACKED CHANGE: none` and `SKIPPED: none`, plus the known `MAIN AHEAD` (edfa114, daily report only).
- T-RB's own command works from this checkout. `git diff --stat origin/main...HEAD -- .claude templates scripts/check_pipeline.py scripts/check_handoff.py` lists the 4 .claude files, scripts/check_pipeline.py and both templates (the branch plus its unmerged base). origin/daily-fixes/2026-11-26 is not pushed, so the optional origin/main view of RULES BRANCH cannot show this branch yet. That check is left to A1 after the push.

## Tests re-run (output)
Full suite, scratch worktree `wt` at 8529267:
```
$ PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<scratch>/pyc-gi3emwq1 python3 -m pytest -q -p no:cacheprovider
1073 passed, 1 skipped in 222.98s (0:03:42)
```
This matches 05's count (1073 passed, 1 skipped). Oldest-Python compile: python3.10 is not on PATH, but /usr/bin/python3.11 is. `tests/test_safety.py::test_every_py_compiles_on_oldest_python` ran and passed. It did not skip: `-rs` run in `wt2` gave `6 passed, 543 deselected in 0.89s`, with no skip reported.

Mutants (scratch worktree `wt`, full suite each, restored with `git checkout HEAD -- <file>` in `wt`). The env-check line, run with the same guard used on every mutant command:
```
$ PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i3-113-r1-cu6ozm3z/pyc-gi3emwq1 python3 -c 'import sys; print(sys.dont_write_bytecode, sys.pycache_prefix)'
True /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i3-113-r1-cu6ozm3z/pyc-gi3emwq1
```
```
== M-a1 (templates/build-plan.md) diff lines: 1
FAILED tests/test_pipeline_check.py::test_rules_branch_template_line[templates/build-plan.md]
1 failed, 1072 passed, 1 skipped in 213.90s (0:03:33)
restored templates/build-plan.md
== M-3 (scripts/check_pipeline.py) diff lines: 3
FAILED tests/test_pipeline_check.py::test_rules_branch_docstring_names_no_merged
1 failed, 1072 passed, 1 skipped in 208.88s (0:03:28)
restored scripts/check_pipeline.py
== M-4 (scripts/check_pipeline.py) diff lines: 2
FAILED tests/test_pipeline_check.py::test_check_pipeline_docstring_records_110_no_go
1 failed, 1072 passed, 1 skipped in 240.88s (0:04:00)
restored scripts/check_pipeline.py
== M-2alt (scripts/check_pipeline.py) diff lines: 3
FAILED tests/test_pipeline_check.py::test_parse_request_docstring_defers_who_removal
1 failed, 1072 passed, 1 skipped in 223.77s (0:03:43)
restored scripts/check_pipeline.py
pyc files under wt: 0; in pyc dir: 0
```
All 4 mutants were killed, each by exactly the expected test. M-a1 fails only the build-plan case, as 04 requires. M-b1 and M-b2 are step-2 mutants and do not apply under 2-alt.

## Real-data effect (diff_reports output, pasted)
not required (scripts/check_pipeline.py, templates/build-plan.md, templates/build-report.md, tests/test_pipeline_check.py; no TRIGGER or TRIGGER_DIRS file)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-014, RI-002, RI-009, RI-010, RI-012, RI-015
- RI-001 (ESCALATED): every count here was measured, not assumed: n = 2, k = 1 under C1 (k = 0 under a merge-base rule), template count 1 per file, and 4 of 4 mutants killed. No "every" claim without a count. No new occurrence.
- RI-014 (OPEN): I checked shallow = false and the refspec before any branch read. Nothing is read as "none" from a clone it can't see. No new occurrence. Status unchanged.
- RI-002 (GUARDED): each git read was classified by exit code and stderr. No uncomputable read became a pass.
- RI-009 (GUARDED): no checkout switch, no stash, `STASH: none`. Worktrees were only in my mkdtemp dir. I left the other item's uncommitted edit in the main checkout untouched.
- RI-010 (GUARDED): each new duty text has a pin and a killed mutant.
- RI-012 (GUARDED): the pins are exact-line counts or exact normalised substrings. No text classifier was added.
- RI-015 (GUARDED): the env-check line is pasted above the mutants. Both pyc dirs are fresh, and 0 .pyc files are in `wt` or the pyc dir after the runs.

## Pipeline line (step 2)
check_pipeline line: `113: awaiting A1 (FULL)` (run after 06, 07 and the I3 --log line; exit 0, INCOMPLETE none, SKIPPED none, STASH none, LOG TIME and LOG BATCH do not name 113)

## Sent back / sent to Audit
Sent to Audit (07-audit-task.md). Nothing sent back. The C1 finding (I1 audit above) goes to A1 as a candidate follow-up item, not a send-back.
