# 06 Verification - 079
Verdict: PASS (round 2; earlier rounds: FAIL round 1)
Sent back to: none

Head verified: bff5839 ("Item 079: I2 build round 2"), branch daily-fixes/2026-11-19, parent 627a2a0 (my round 1 FAIL). Round 2 changes only `scripts/check_pipeline.py` (+2 lines) and `tests/test_pipeline_check.py` (+18 / -4), plus 05 and I2's log line (`git diff 627a2a0 bff5839 --stat`). The item total against 7b09a8a is still the same 4 code/command files. Scratch work: a new full clone `/tmp/claude-0/-home-claude/13c4a4b3-cf85-50b9-b50f-3e762631e621/scratchpad/079-I3/clone2` at bff5839 (`--is-shallow-repository` = false, git 2.43.0), mutation script `/tmp/claude-0/-home-claude/13c4a4b3-cf85-50b9-b50f-3e762631e621/scratchpad/079-I3/mut_r2.py`, outputs `full_r2.txt`, `full_r2b.txt`, `p1_r2.txt`, `repro_r2.txt` in the same folder. Nothing in the repo changed except this file, 07 and my log line.

## I1 audit (plan vs research)
Unchanged since round 1 (no 04 change in round 2): the plan follows 03 steps 1-9 and every Missing inputs row, with no unsourced additions. Round 2's code is exactly what the plan's C3 / Missing inputs row 2 required ("missing or unreadable while shallow is true" -> `not checked (shallow clone; run git fetch --unshallow)`), so I1 is not sent anything.

## I2 audit (build vs plan)
- P1 fix, `_walk` 053 block (L773-774): `if shallow[1] != 0 and _shallow_boundaries() == "unreadable": return None, ("not checked (shallow clone; run git fetch --unshallow)" + note, False), None`. That is the 2-line fix my round 1 named. It is placed after the shallow-true branch and before the squash/rebase return. When the flag fails, `sure` is False in `_shallow_boundaries`, so a missing or non-UTF-8 file gives "full" and the loud text stays. Only a malformed S line (a `SHALLOW_LINE` fullmatch miss) gives "unreadable". The comparison is `==` on the return value, not a substring match (RI-012).
- Test fix: `test_shallow_file_unreadable_not_checked` no longer asserts a `_walk` result in the patched-flag state that real git cannot produce. It now asserts only `_shallow_boundaries() == "unreadable"`. New `test_malformed_shallow_line_real_git_not_checked` runs with no patching: it asserts that git exits non-zero with "bad shallow line", then runs check_pipeline end to end and asserts the exact UNTRACKED CHANGE, RESEARCH CODE and REAL-DATA FIELD lines, not the exit code. That is what round 1 asked for.
- 05 round 1 deviation 1 is corrected and withdrawn, and the text describes real git (exit 128 on the flag). This matches my round 1 output.
- 05's round 2 numbers match my re-runs below: 568 passed + 1 expected failure, mutations m0-m6, and anchors at 1.
- Connectivity: the new branch is reachable only from `_walk`. It calls the existing `_shallow_boundaries`, and its output reaches `main()` through the same three printed lines. No new function, file or TODO.

## Tests re-run (output)
Full suite, scratch clone at bff5839:
```
$ python3 -m pytest -q -rs
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'
1 failed, 568 passed, 1 skipped in 90.21s (0:01:30)
```
The one failure is the expected one (item 071): before this file, check_pipeline at bff5839 gave `079: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))` and `I3 FAIL: 079`. UNTRACKED CHANGE, RESEARCH CODE, REAL-DATA FIELD, UNCOMMITTED STEP and SKIPPED were all `none` (`full_r2.txt`).
RI-008: `pytest -q tests/test_safety.py -k oldest` gives `1 passed, 8 deselected`. python3.11 is on PATH and python3.10 is not, so it compiled on 3.11 only (the 3.10 leg was skipped).

`python3 scripts/check_handoff.py 079` (exit 0):
```
sources count (unique URLs in 01-research.md): 9
fact-check rows: 37
totals line: 37 rows -> 32 as-is, 4 fixed, 1 removed
PASS
```

**P1 re-check with real git, no patching** (clone2, `.git/shallow` = a15129c571ebbd7765cbcebd55943117e7092dbb + `zz`; 694bf4d is an ancestor of HEAD):
```
$ git rev-parse --is-shallow-repository   -> fatal: bad shallow line: zz   flag=128
$ python3 scripts/check_pipeline.py       -> exit=1
UNTRACKED CHANGE: not checked (shallow clone; run git fetch --unshallow)
RESEARCH CODE: not checked (see UNTRACKED CHANGE)
REAL-DATA FIELD: not checked (see UNTRACKED CHANGE)
UNCOMMITTED STEP: git ls-tree HEAD failed (item 077)
INBOX: 2026-11-19.md (git log failed)
```
Round 1 printed `cutoff 694bf4d not in HEAD's history (squash/rebase or wrong SHA)` here, so P1 is fixed. The exit 1 comes from the 077 and INBOX lines, which hit git's die. Round 1 already called that honest and out of scope. More edge files, also real git:
- `zz` alone gives the same not checked text.
- A 39-hex line (git: `bad shallow line`) gives the same not checked text.

**Original a15129c repro** (clone2, `git rev-parse a15129c > .git/shallow`, flag `true`):
```
exit=1
079: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))
UNTRACKED CHANGE: not checked (shallow boundary a15129c; run git fetch --unshallow)
RESEARCH CODE: not checked (see UNTRACKED CHANGE)
REAL-DATA FIELD: not checked (see UNTRACKED CHANGE)
UNCOMMITTED STEP: none
INBOX: not checked (shallow clone; run git fetch --unshallow)
```
Here exit 1 is only the pre-PASS 079 line. The base 7b09a8a and e69d5bd scripts gave `a15129c (git diff-tree failed)`, exit 1 (round 1, unchanged code path). The guardrail would have caught the original error: m1 below turns this fixture back into the `(git diff-tree failed)` entry, and 3 tests fail.

**Full clone unchanged.** After `rm .git/shallow` (flag `false`), the output is byte-identical to the run before any shallow file was written (`diff full_r2.txt full_r2b.txt` -> IDENTICAL). A wrong cutoff with a failed or missing flag stays loud: `--untracked-from 000…001` gives `UNTRACKED CHANGE: cutoff 0000000 not in HEAD's history (squash/rebase or wrong SHA)`. `test_t14_unusable_cutoff_is_not_checked` and `test_unrelated_root_in_full_clone_stays_loud` pass.

**Mutations** (my own script, clone2, each anchor asserted count 1, restored: `restored True`, `git status` clean). Selection: `tests/test_pipeline_check.py tests/test_real_data_field.py -k "shallow or below or unrelated or full_clone or failed_diff_tree or merge_base or malformed or t14"`, 21 selected:
```
m0 new branch dropped        | 1 failed, 20 passed | test_malformed_shallow_line_real_git_not_checked
m1 inside                    | 3 failed, 18 passed | (a) inside_walk, (b) second_parent, (e) linked_worktree
m2 literal .git/shallow      | 1 failed, 20 passed | test_shallow_boundary_in_linked_worktree
m3 untracked below           | 1 failed, 20 passed | test_shallow_boundary_below_cutoff_entries_unconfirmed
m3b real_data below          | 1 failed, 20 passed | test_below_rule_real_data_entries
m4a RI-002 None guard removed| 3 failed, 18 passed | failed_diff_tree_is_an_entry_not_none, unrelated_root_in_full_clone_stays_loud, below_cutoff_entries_unconfirmed
m5 unreadable->full          | 2 failed, 19 passed | shallow_file_unreadable_not_checked, malformed_shallow_line_real_git_not_checked
m6 merge-base other exit     | 1 failed, 20 passed | test_merge_base_failure_is_loud
```
RI-002 (the removed default put back, `_research_code(files or [], ...)` + None guard off, 20 selected): 2 failed, 18 passed (`test_failed_diff_tree_is_an_entry_not_none`, `test_shallow_boundary_below_cutoff_entries_unconfirmed`), then restored. The m0 result shows the new branch is pinned. The m5 result shows the malformed line's "unreadable" is pinned on both the patched path and the real path.

**Probe anchors (078) at bff5839**, count in their file: RI-002-063-leading-edge 1, RI-002-065-interior-gap 1, RI-013-067-1b 1, RI-002-046-tickers-key 1, RI-007-064-work-py 1, RI-009-037-clash-line 1, RI-010-049-rules-line 1, RI-011-052-merge-tree 1, RI-012-059-bare-429 1. `git diff 7b09a8a bff5839 -U0 -- scripts/check_pipeline.py` touches none of the 4 check_pipeline anchor lines (grep 0), so the full 270 s probe run was not repeated.

Window edges and RI-012: a boundary inside the walk is covered by (a), (b) and (e). A boundary below the cutoff is covered by (d). A boundary above HEAD cannot exist. Malformed-file edges: a bad line after a good one, a bad line alone, and a 39-hex line all give not checked. The flag uses `==` and S lines use `fullmatch`, so nothing classifies by substring. No 001 rule the person follows is changed, and there is no simulator or replay.

Observation, not a FAIL, for Audit: a non-UTF-8 byte in `.git/shallow` makes git print it in stderr, and `_git` crashes with `UnicodeDecodeError` (in `open_branches`, before the 079 code runs). The base 7b09a8a script crashes the same way, so this is not caused by 079. It is loud (a traceback, never a pass or a false entry), and it is outside 079's scope.

## Real-data effect (diff_reports output, pasted)
not required (.claude/commands/daily-audit.md, .claude/commands/run-item.md, scripts/check_pipeline.py, tests/test_pipeline_check.py)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-002, RI-006, RI-007, RI-008, RI-009, RI-010, RI-012, RI-014
- RI-001 (ESCALATED): every count here comes from a fixture or a real run that I re-ran. No "always" claim.
- RI-002: the default put back fails 2 tests, and m4a fails 3. The malformed file is now not checked, never a pass or a false-cause error.
- RI-006: every number above was pasted from a command.
- RI-007: a full-clone real root and a wrong cutoff stay loud (c2, t14, my `--untracked-from` probe).
- RI-008: compiled on 3.11 only, because python3.10 is absent.
- RI-009: all mutations and shallow files were in clone2, never in the repo.
- RI-010: my log line goes through `--log`.
- RI-012: no substring classification was added.
- RI-014 (OPEN, this item): it now holds for a boundary inside or below the walk, the original a15129c case, and a malformed shallow file with real git.

RI-014: guardrail built (079); GUARDED when 079 is merged and m1 fails fixture (a) on main.

## Pipeline line (step 2)
check_pipeline line: `079: awaiting A1 (FULL)` (run after this file, 07 and the log line; exit 0)

## Sent back / sent to Audit
PASS. Sent to Audit: work/079/07-audit-task.md.

## Round 1 (FAIL, kept for the record)

Head verified: e820bd7 ("Item 079: I2 build"), branch daily-fixes/2026-11-19, parent 7b09a8a. The repo clone is not shallow (`git rev-parse --is-shallow-repository` prints `false`). All scratch work is under /tmp/claude-0/-home-claude/13c4a4b3-cf85-50b9-b50f-3e762631e621/scratchpad/079-I3/: a full clone `clone` checked out at e820bd7, the base scripts `base_cp.py` (7b09a8a) and `e69_cp.py` (e69d5bd), and the outputs `full.txt`, `shallow.txt`, `base_shallow.txt`, `e69_shallow.txt`, `bad.txt` and `bad2.txt`. Nothing was changed in the repo except this file and the log line.

### I1 audit (plan vs research)
- The plan follows 03 steps 1-9 and all 8 Missing inputs rows. The Rule trace lists every row, and the one DROPPED row (the log.showRoot follow-up) is out of scope in 03 too.
- C1 (the existing `test_failed_diff_tree_is_an_entry_not_none` pins `files or []`) is correct. 03 step 4 does remove that behaviour.
- C2 (callers that pass a 2-tuple) is correct. The tuple is in that test, and `test_t15_git_log_failure_fails` passes `_walk` to `real_data_field`.
- C3 (a malformed S line gives "unreadable", so not checked) is sourced: 03 row 23 cites shallow.c `die("bad shallow line")`.
- C4 is a fair note for I3 and A1.
- The extra research is sourced: the hash-function-transition page for 64 hex, the shallow doc for the "none is exact" proof, and the rev-parse doc for relative `--git-common-dir`.
- No unsourced additions. The plan is fine and is not sent back.

### I2 audit (build vs plan)
These match the plan line by line (read in `git diff 7b09a8a e820bd7`):
- `SHALLOW_LINE`, `_note`, `_shallow_boundaries`, the `_walk` order (053 block first and unchanged, then unreadable, then inside, then merge-base below), `_parts`, `_below_text`.
- The three users (untracked_changes, research_code, real_data_field), the docstring inserts, and the two command-file sentences (additions only, verbatim step 8 text with the item tag).
- The function diff (ast) shows `_walk`, `real_data_field`, `research_code` and `untracked_changes` changed, and `_below_text`, `_note`, `_parts` and `_shallow_boundaries` added. `uncommitted_steps` and `_md_lines` are byte-identical to 7b09a8a.
- probe_guardrails anchors at HEAD all have count 1. RI-002-063-leading-edge, RI-002-065-interior-gap, RI-013-067-1b, RI-002-046-tickers-key, RI-007-064-work-py, RI-009-037-clash-line, RI-010-049-rules-line, RI-011-052-merge-tree and RI-012-059-bare-429 each give 1. I did not re-run the full 270 s probe, because no anchor text moved.
- Deviations 2 to 4 are accepted. The `UnicodeDecodeError` catch is the same Missing-inputs rule, the renames are form only, and the placement before "It runs" / "Before starting" matches the plan's intent.

**Deviation 1 is not accepted (problem P1 below).** 05 says that with a malformed line, "real git dies on the bad line, so the 053 `known` / `--is-ancestor` block answers first with `not checked (cutoff <c7> not in this shallow clone; ...)`, still failed False and exit 0". With real git that is false. It holds only because the test patches `rev-parse --is-shallow-repository` to `("true\n", 0)`. Real git dies on that command too, so the 053 block takes its full-clone branch. I ran it in the scratch clone at e820bd7, with `.git/shallow` = `a15129c…` plus a `zz` line and no patching:
```
git rev-parse --is-shallow-repository        -> fatal: bad shallow line: zz   exit=128
git rev-parse --verify -q 694bf4d…^{commit}  -> fatal: bad shallow line: zz   exit=128
git merge-base --is-ancestor 694bf4d HEAD    -> fatal: bad shallow line: zz   exit=128
git rev-parse --git-common-dir               -> .git                          exit=0
$ python3 scripts/check_pipeline.py          -> exit=1
UNTRACKED CHANGE: cutoff 694bf4d not in HEAD's history (squash/rebase or wrong SHA)
RESEARCH CODE: not checked (see UNTRACKED CHANGE)
REAL-DATA FIELD: not checked (see UNTRACKED CHANGE)
```
So a malformed shallow file gives a loud error entry that names the wrong cause (squash/rebase). The plan (C3, and the Missing inputs row "missing or unreadable while shallow is true") and 03 step 1 call for `not checked (shallow clone; run git fetch --unshallow)`. The test asserts a state that real git cannot produce, so it does not pin the real path.

### Tests re-run (output)
Full suite, in the scratch clone at e820bd7:
```
$ python3 -m pytest -q
568 passed, 1 skipped in 89.70s (0:01:29)
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars'
```
RI-008: `tests/test_safety.py -k oldest` gives 1 passed. python3.11 is on PATH and python3.10 is not, so the compile ran on 3.11.

`python3 scripts/check_handoff.py 079` (exit 0):
```
sources count (unique URLs in 01-research.md): 9
fact-check rows: 37
totals line: 37 rows -> 32 as-is, 4 fixed, 1 removed
PASS
```

**Original bug repro (the brief's check).** This was a full clone at e820bd7 with `git rev-parse a15129c > .git/shallow` (`--is-shallow-repository` is then true). a15129c is in `694bf4d..HEAD`, and 694bf4d is an ancestor of HEAD.
```
build e820bd7:          exit 0
UNTRACKED CHANGE: not checked (shallow boundary a15129c; run git fetch --unshallow)
RESEARCH CODE: not checked (see UNTRACKED CHANGE)
REAL-DATA FIELD: not checked (see UNTRACKED CHANGE)
base 7b09a8a script:    exit 1
UNTRACKED CHANGE: a15129c (git diff-tree failed) (item 053: ...)
RESEARCH CODE: none
e69d5bd script:         exit 1
UNTRACKED CHANGE: a15129c (git diff-tree failed) (item 053: ...)
```
The same clone without the shallow file gives `UNTRACKED CHANGE: none`, exit 0. The diff against the shallow run is only those three lines plus INBOX (`not checked (shallow clone; ...)`). The fix holds for the reported case. It also stops the base's `RESEARCH CODE: none` (step 4).

**Guardrail mutations**, in the scratch clone, each restored with `git checkout`. Selection: `-k "shallow or below or unrelated or full_clone or failed_diff_tree or merge_base"`, 16 tests.
- m1 `if inside:` → `if False:`: 3 failed, 13 passed. Failed: (a), (b) and (e), each with `<sha7> (git diff-tree failed)`.
- m2 `Path(".git/shallow")`: 1 failed, 15 passed. Failed: (e).
- m3 untracked `if below:` → `if False:`: 1 failed, 15 passed. Failed: (d), with `524ba40 (git diff-tree failed); ac15520 scripts/y.py`.
- m3b real_data `if names and below:` → False: 1 failed, 15 passed. Failed: `test_below_rule_real_data_entries`.
- m4 (RI-002: the removed default `files or []` put back, and the None guard removed): 2 failed, 14 passed. Failed: (f) and (d).
- m4a (only the None guard removed): 3 failed. Failed: (f), (c2) and (d).
- m5 unreadable → "full": 1 failed, 15 passed. Failed: `test_shallow_file_unreadable_not_checked`.
- m6 merge-base exit not 0/1 treated as 1: 1 failed, 15 passed. Failed: `test_merge_base_failure_is_loud`.

All mutations match 05. m1 is the GUARDED probe for RI-014.

The feasibility counts in 03/04 are re-run by the tests and match: (a) {B}, (b) {B2}, (d) inside 0 / below 1 / n = 2, and (e) {B}.

RI-012 (text matching): the flag is compared with `==` to "true"/"false", S lines use `fullmatch`, and boundary membership is a set test on full SHAs. Nothing matches a substring. Window edges: (d) is a boundary below the window, and (a), (b) and (e) are boundaries inside it. A boundary above HEAD cannot exist. No 001 rule the person follows is changed, and there is no simulator or replay.

### Real-data effect (diff_reports output, pasted)
not required (.claude/commands/daily-audit.md, .claude/commands/run-item.md, scripts/check_pipeline.py, tests/test_pipeline_check.py)

### Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-002, RI-006, RI-007, RI-008, RI-010, RI-012, RI-014
- RI-001 (ESCALATED): each rule count is a fixture count that the tests re-run. None is asserted as "always".
- RI-002: m4 (the default put back) fails 2 tests. The malformed-S path does not turn into a pass, but it does become a false-cause error (P1).
- RI-006: every count above comes from a command.
- RI-007: (c2) keeps a full-clone real root loud (exit 1). The 053 shallow test is unchanged and passes.
- RI-008: compiled on 3.11; python3.10 is absent.
- RI-010: the step 8 sentence is in both command files (grep 1 each). The log line goes through `--log`.
- RI-012: no substring classification, as above.
- RI-014 (OPEN, this item): the fix holds for a boundary inside or below the walk and for the original a15129c case. It does not yet hold for a malformed shallow file with real git (P1).

RI-014: guardrail built (079); GUARDED when 079 is merged and m1 fails fixture (a) on main. Not reached: this round FAILs.

### Pipeline line (step 2)
check_pipeline line: `079: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))` (run after the log line; exit 1, expected in a FAIL round)

### Sent back / sent to Audit
Sent back to I2. No 07 this round.

P1. Malformed shallow line (deviation 1).
- **Problem.** With real git, `--is-shallow-repository` exits 128, so the 053 block in `_walk` returns `cutoff <c7> not in HEAD's history (squash/rebase or wrong SHA)`, failed True. The plan (C3, Missing inputs row 2) requires `not checked (shallow clone; run git fetch --unshallow)`, failed False.
- **Fix the code.** In the 053 block, when the flag command itself fails (`shallow[1] != 0`) and `_shallow_boundaries()` returns "unreadable" (with sure False it still reads the file and finds the bad line), return the 079 unreadable tuple instead of the squash/rebase text. A missing file still gives "full", so a real wrong cutoff stays loud. I tried this 2-line change in scratch. The UNTRACKED CHANGE line became `not checked (shallow clone; run git fetch --unshallow)`, and tests/test_pipeline_check.py gave 225 passed.
- **Fix the test.** In `test_shallow_file_unreadable_not_checked`, test the malformed case with no patching of `_git`. Write `<C>\nzz\n` to the shallow file, run `check_pipeline.py` end to end and assert the exact UNTRACKED CHANGE text. Also check that a mutation which drops the new branch fails this test.
- **Expected exit code.** The whole run still exits 1 in that state, because other checks hit git's die (`UNCOMMITTED STEP: git ls-tree HEAD failed (item 077)`, `INBOX: ... (git log failed)`). That is honest and out of scope. Assert only the UNTRACKED CHANGE, RESEARCH CODE and REAL-DATA FIELD lines, not exit 0.
- **Fix 05.** Correct deviation 1 so it states the real git behaviour.

Everything else passes. After the fix, re-run the suite and mutations m1 to m6.
