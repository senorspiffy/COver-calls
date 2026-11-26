# 05 Build report - 113
Scratch dir: /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i2-113-r1-oe9jceid

Base: a1719eb (daily-fixes/2026-11-26, I1 commit of 113). During the build the orchestrator committed 56edb15 (112 R3) and dae6c68 (111 R3). They touch only work/111, work/112 and logs/research, none of the 4 code files here. I made the scratch worktree `wt` with `git worktree add --detach` inside the scratch dir above, at a1719eb, and copied this build's 4 files into it. The pyc dir `pyc-pn030g0n` was made inside it with the same mkdtemp command (prefix `pyc-`). Mutants ran only in `wt`, and each mutated file was restored there from the build copy in /home/claude/fix (`cmp` printed `restored` for all 4). Afterwards I removed `wt` with `git worktree remove --force` (it held the copied build files). I ran no `git stash`.

## Pre-build check (item 113)
Every command below ran before any edit, in /home/claude/fix.
- 0a: `git rev-parse --is-shallow-repository` printed `false`. `git config --get-all remote.origin.fetch` printed `+refs/heads/*:refs/remotes/origin/*`. `git fetch origin` exited 0.
- 0a ref list: `git branch -r --no-merged HEAD --format='%(refname:short)'` exited 0 and printed:
  ```
  origin/claude/project-thread-f64g3k
  origin/main
  ```
  It printed no `*/HEAD` line, so n = 2.
- 0b (C1): HEAD's own set came from `git grep -n parse_request HEAD -- scripts tests` (exit 0, 11 hits). Its 3-target sites are scripts/check_pipeline.py `    _, _, (steps, _, _) = parse_request(text)`, `    scope, _, (waived, _, _) = parse_request(req_text)` and `    scope, opened, (waived, waived_line, _) = parse_request(req_text)`, plus tests/test_pipeline_check.py `    scope, _, (waived, line, who) = cp.parse_request(text)`.
- 0b (C2), per ref, with `git grep -n parse_request <ref> -- scripts tests`:
  - `origin/claude/project-thread-f64g3k`: exit 1, 0 stdout lines, empty stderr, so no match.
  - `origin/main` (edfa114): exit 0, empty stderr, 11 hits. The 4 hits that unpack `[2]` into 3 targets:
    - origin/main:scripts/check_pipeline.py:637 `_, _, (steps, _, _) = parse_request(text)`: known site
    - origin/main:scripts/check_pipeline.py:650 `scope, _, (waived, _, _) = parse_request(req_text)`: known site
    - origin/main:scripts/check_pipeline.py:760 `scope, opened, (waived, waived_line, who) = parse_request(req_text)`: new caller (its path plus line text is not in HEAD's set, because HEAD's line reads `waived_line, _)`)
    - origin/main:tests/test_pipeline_check.py:1920 `scope, _, (waived, line, who) = cp.parse_request(text)`: known site
  - The other 7 origin/main hits are a comment (543), the `def` (618), a docstring (645) and `[0]`-only reads (739, 747, 1300, 2057). They do not unpack `[2]`.
  - Result: k = 1.
- 0c: `git merge-base --is-ancestor origin/daily-fixes/2026-11-25 HEAD` exited 0, so the base is in HEAD.
- Decision: k = 1 >= 1, so I took **step 2-alt** and kept `who`. Note for I3/A1: the one "new caller" is main's older text of the same L781 site, from before 105 renamed `who` to `_`. It is not a new reader. C1's rule compares line text, and this line's text differs, so the rule counts it as new. I applied the rule as written and did not override it (see Deviations 1).

## Changes made (file: what changed)
- templates/build-plan.md: T-RB inserted as one physical line, word for word from 03, on the line after `## Tests and checks`. (`grep -c` of that line in work/113/03-handoff.md gives 1.)
- templates/build-report.md: the same T-RB line, inserted on the line after `## Deviations from plan`.
- scripts/check_pipeline.py: docstring only, no code change.
  - D-110 inserted after "... never to _STATS (the I2 field refuses it)." at the 18-space indent.
  - D-RB appended after "Listed, not an error." at the 18-space indent.
  - Step 2-alt: the parse_request docstring line 2 is kept, and 2 lines are added: "tests/test_pipeline_check.py::test_inbox_quoted_scope_and_waiver_are_not_read unpacks it; removal deferred (item 113: origin/main unpacks 3)."
- tests/test_pipeline_check.py:
  - `test_check_pipeline_docstring_records_110_no_go` is extended by 3 asserts: the D-110 phrase "re-run the fenced script in work/110/01-research.md", "don't copy these (item 113)", and `(REPO / "work/110/01-research.md").is_file()`. The existing 7 asserts are unchanged.
  - New `RB_TEMPLATE_LINE` constant holding T-RB.
  - New `test_rules_branch_template_line`, parametrized over both templates.
  - New `test_rules_branch_docstring_names_no_merged`.
  - New `test_parse_request_docstring_defers_who_removal` (step 2-alt).
  - L1974/L1976 are unchanged (2-alt).

File counts:
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
0
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
4
```

## Connectivity check
- [x] every new function/rule is used: the 3 new tests (4 cases) are collected by pytest and ran in the suite. `RB_TEMPLATE_LINE` is read by `test_rules_branch_template_line`. T-RB, D-RB, D-110 and the 2-alt docstring are each read by a test, and each has a mutant that the tests kill (below).
- [x] every input has a source, every output has a consumer:
  - T-RB is read by I1 in build-plan.md and by I2 in build-report.md.
  - D-RB and D-110 are in the docstring the `--help`/module doc readers see.
  - The step 0 result is in this 05 for the PR text (03 step 6).
- [x] every branch ends in a defined result:
  - Step 0: n = 2 was computed, and each ref's grep status matched a C2 case (exit 1 with empty output means no match; exit 0 means hits). k = 1 led to 2-alt.
  - 0c exit 0 means the base is in HEAD.
  - No code path was added.
- [x] no leftover TODOs or unused files: `git diff -U0 | grep -nE "TODO|FIXME"` gave no output. There are 0 new files outside work/.
- Missing-data grep, `grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/ | wc -l`, gave 38. All 38 are existing hits; ccbot/ is untouched (`git diff --stat` lists no ccbot file), so 0 are new or changed. I also ran the same pattern plus `: float = ` and `[<>]` over the added diff lines (`git diff -U0 | grep -E "^\+" | grep -E ...`), and it gave no output. No numeric dataclass default and no `>`/`<` test were added.
- Re-grep (2-alt): parse_request's return is unchanged, so the 3-target unpacks stay by design. `\bwho\b` code lines are unchanged.
- Feasibility test numbers: per template, `splitlines().count(RB_TEMPLATE_LINE)` is 1 (test passes). With M-a1 it is 0, and only the build-plan case fails.

## Test output (pasted, not summarized)
Targeted tests, plus the plan's "staying green" tests, in /home/claude/fix:
```
$ python3 -m pytest -q tests/test_pipeline_check.py -k "rules_branch or 110_no_go or defers_who or unfilled_template_suite or suite_label_in_template or scratch_dir_template_line or round_heading_template or inbox_quoted or build_waived"
.............                                                            [100%]
13 passed, 535 deselected in 2.09s
$ python3 -m pytest -q tests/test_real_data_field.py -k t7d
2 passed, 37 deselected in 0.06s
```
Full suite, run in /home/claude/fix after writing this 05 (dae6c68 plus this build's 4 files and 05):
```
$ python3 -m pytest -q
1073 passed, 1 skipped in 141.58s (0:02:21)
```
Suite: 1073 passed, 1 skipped in 141.58s (0:02:21)

### Mutants (scratch worktree `wt`, full suite each)
Env-check line, run with the guard used on every mutant command:
```
$ PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i2-113-r1-oe9jceid/pyc-pn030g0n python3 -c 'import sys; print(sys.dont_write_bytecode, sys.pycache_prefix)'
True /tmp/claude-0/-home-claude/ae55004c-f800-58fc-9343-38198636732b/scratchpad/i2-113-r1-oe9jceid/pyc-pn030g0n
```
Each mutant ran as `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=<that pyc dir> python3 -m pytest -q -p no:cacheprovider` in `wt`, with the output filtered by `grep -E "^FAILED|passed|failed"`. The small `python3 -` heredocs that wrote each mutant ran before the guarded pytest and import no project module. After all the mutants, `find <pyc dir> -type f | wc -l` gave 0.

| Mutant | Change | Summary line | Failed |
|---|---|---|---|
| M-a1 | T-RB line deleted from templates/build-plan.md only | `1 failed, 1072 passed, 1 skipped in 211.74s (0:03:31)` | test_rules_branch_template_line[templates/build-plan.md] (the build-report case passes) |
| M-3 | D-RB (3 docstring lines) removed | `1 failed, 1072 passed, 1 skipped in 208.29s (0:03:28)` | test_rules_branch_docstring_names_no_merged |
| M-4 | ", don't copy these" dropped from D-110 | `1 failed, 1072 passed, 1 skipped in 221.10s (0:03:41)` | test_check_pipeline_docstring_records_110_no_go |
| M-2alt (extra, not in 04) | "removal deferred (item 113: origin/main unpacks 3)." line removed | `1 failed, 1072 passed, 1 skipped in 223.27s (0:03:43)` | test_parse_request_docstring_defers_who_removal |

M-b1 and M-b2 are step 2 mutants and were not run, because step 0 chose 2-alt and the 3-target unpacks are unchanged.

### Whole-output check (03 step 5)
Base script = `git show HEAD:scripts/check_pipeline.py` saved to the scratch dir. Head script = the build's scripts/check_pipeline.py. Both ran from /home/claude/fix, one right after the other:
```
$ python3 <scratch>/base_check_pipeline.py > <scratch>/out_base.txt   -> base exit 0
$ python3 scripts/check_pipeline.py > <scratch>/out_head.txt          -> head exit 0
$ diff out_base.txt out_head.txt                                      -> no output, diff exit 0
sha256 both c2583eacfc277954a9660abc30c1835ebc1593f000ca9aeb04dcf7ee4f348b2b (136 lines)
```
Relevant head lines:
```
113: in progress (FULL: next 05)
IN PR: none
MAIN AHEAD: origin/main has 1 commits not in HEAD; merge it before building (item 051)
OPEN BRANCHES (not merged into HEAD):
  origin/claude/project-thread-f64g3k: items none; merges cleanly; last commit 2026-11-26 (0 days)
RULES BRANCH: none
UNTRACKED CHANGE: none
STASH: none
```
- RULES BRANCH reads `none` before and after, as T-RB now says it normally will.
- The exit codes are equal (0 and 0).
- MAIN AHEAD (edfa114, the 2026-11-26 daily audit commit) was there before this build. It is the orchestrator's to merge; I2 did not merge main.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat`: scripts/check_pipeline.py, templates/build-plan.md, templates/build-report.md, tests/test_pipeline_check.py; no TRIGGER or TRIGGER_DIRS file)

## Deviations from plan
1. Step 0 came out as k = 1, so I built step 2-alt (keep `who`), not step 2. The only "new caller" is origin/main:scripts/check_pipeline.py:760 `(waived, waived_line, who)`. It is main's pre-105 text of the site that HEAD has at L781 as `(waived, waived_line, _)`. C1 compares path plus line text, and the text differs, so the rule counts it as new. I applied the rule as written; it is the conservative path that 04 defines. Once this branch reaches main, that line is HEAD's text, and a later item can remove `who` under the same rule. This is flagged for I3/A1 and the person: C1 does not tell a stale version of a known site from a real new caller.
2. For 2-alt, the docstring change keeps line 2 ("who: kept for the tuple shape; no gate reads it since 105.") and adds 03's 2-alt sentence on 2 more lines, filled in with `origin/main unpacks 3`.
3. Extra mutant M-2alt was run (04 names none for the 2-alt test). It was killed. No file changed because of it.
4. The 34 `.pyc` files newer than 04 under scripts/ and tests/ in /home/claude/fix come from unmutated suite runs there. No mutant ran in /home/claude/fix.

## Recurring issues checked (item 013)
I read logs/recurring-issues.md first. The OPEN or ESCALATED entries are RI-001 and RI-014. I also checked the GUARDED entries 04 names: RI-002, RI-009, RI-010, RI-012, RI-015, RI-004/005/006.
RI-001: ESCALATED, unchanged. Each count was measured: n = 2, k = 1, 0c exit 0, and template count 1 per file. No "every" claim is made without a count.
RI-014: OPEN, unchanged. The shallow and refspec check ran first (false; `+refs/heads/*:refs/remotes/origin/*`) before any branch read.
RI-002: GUARDED, holds. Each git read was classified by exit code and stderr (C2). None was read as "none" or as a pass.
RI-009: GUARDED, holds. Mutants ran only in the scratch worktree inside my own mkdtemp dir, and restores were made from copies. There was no checkout switch and no stash; `STASH: none`.
RI-010: GUARDED, holds. Each new template line or docstring sentence has a pin and a killed mutant (M-a1, M-3, M-4, M-2alt).
RI-012: GUARDED, holds. The pins are exact-line counts or exact substrings of the normalised docstring.
RI-015: GUARDED, holds. Every mutant pytest ran with PYTHONDONTWRITEBYTECODE=1 and a fresh PYTHONPYCACHEPREFIX. The env-check line is pasted above, and the pyc dir has 0 files.
RI-004/005/006: GUARDED, holds. The file counts, Suite line and mutant lines were copied from command output.
RI-007, RI-008, RI-011, RI-013: not touched.
