# 06 Verification - 091
Verdict: PASS (round 2; earlier rounds: FAIL round 1)
Sent back to: none

Verified by I3 on 2026-11-22 in my own worktree of the head commit 4990002 (`git worktree add /tmp/claude-0/scratch/i3-091/wt 4990002`, path given by the orchestrator; removed after the runs). My outputs, the mutation harness and the commit_step probe repo are in my own mkdtemp dir `/tmp/claude-0/-home-claude/6b779538-e393-5b21-a85a-072369e659f6/scratchpad/i3-091-r1-dpe6hf15` (step 7's SCRATCH rule). Base 7e537c2 (087 A1 PASS). I used no `git stash`. Rules: I judged by the I3 rules at base (7e537c2). The new 091 lines in i3-verifier.md (SCRATCH sentence, commit_step pointer) were followed too; whether they hold is under "New rules" below.

## I1 audit (plan vs research)
- 04's Rule trace covers every row of 03's map (steps 0-8), the corrections it names (1.6, 1.9, FOR 1a, 3.9/FOR 2, 5.4, 5.5, 5.8, FOR 3) and the removed 4.4. Each DROPPED row has a reason: 088's unborn/verify forms (not shallow results), option (b) level-aware reading (03 defers it), 4.4 (removed in 03).
- Fit changes 1-7 are sourced. Change 3 (absolute GIT_INDEX_FILE; `read-tree` first on the empty mkstemp file) cites git db137fe/t1009 and the git list thread, and M7 confirms it here: with the order swapped, update-index on the empty file fails, exit 128. Change 2 (no `L<n>`) cites `_md_lines`' comment stripping. Change 4 (narrower run-item sentence) keeps A1's `logs/audit/` and `logs/recurring-issues.md` commits legal, which is right. Changes 5 and 6 follow 089/088's own asks. Change 7 (premise test) turns 03's named residual into a test.
- One 03 sentence is silently replaced, not traced. 03 step 5b says "add the read to [089's] census". 04 says both censuses stay unchanged and gives no Rule-trace row for that sentence. Not a defect: `test_read_census` counts raw `read_text`/`read_bytes`/`open` calls, and 5b reads through `_read`, so there is nothing to add. I re-read the test (L3787-3809). Noted for I1's next plan: say when a 03 instruction is moot.
- Unsourced additions: none. No rule the person follows (001) changes. RULE_PATHS change, so the person's OK is needed at PR review, as 03/04 say.
- I1's plan is fine. Nothing goes back to I1.

## I2 audit (build vs plan)
I compared `git diff 7e537c2 4990002` with 04's file table: 12 files outside work/ and logs/, the same 12 files as 04's table. Commit order (A) 8a8bd33 tests only, (B) 8dec4f6, (C) 4990002, as 04 orders.
- Step 1: `UNRELATED_GROUPS` matches 04's 8-orphan table. The test makes one `_run`, asserts exit 1, the 8 exact lines and `merge-base` returncode 1. `test_rule_path_files_are_inside_research_code_dirs` gives its reason in the docstring.
- Step 2: the 4 tests patch exactly 04's tuples and run their unpatched controls first. I re-read the git args in the head code (`main_ahead(shallow)`, `open_branches(today, shallow)`): unchanged.
- Step 3: 2 tests; probe_guardrails.py is unchanged (`fullmatch`, no `prefixmatch`).
- Step 4: UNSHALLOW plus its 3 copies now read `..., LOG TIME, MAIN AHEAD, OPEN BRANCHES and RULE NOT SEEN as 'not checked', never 'none' (items 079, 084, 090).`, with the new assert. This is 090's list plus RULE NOT SEEN, as 04's "if 090 changed the list" clause asks.
- Step 5a: both template lines are present, one each.
- Step 5b: `ROUND_HEADING_FROM = 92`, `STRAY_RUN_HEADING` as 04 gives it (`.match`), `_section_flags` (`_run_seconds` now uses it), `stray_run_headings` via `_read(missing_ok=True)`, the `incomplete()` hook, the gate exactly like SUITE_FROM's, and docstrings. The module and `_anchor_env` docstrings hold no code change. No `_git(` and no raw read were added: both census tests pass.
- Step 6: commit_step.py has (i)-(vi) as 04 lists them, plus 05 Deviations 6. **One 04 refusal is not met for every input form: see F1.**
- Step 7: the SCRATCH sentence is in the 4 files, once each.
- Connectivity, re-done by grep in the head tree:
  - `_section_flags` is called by `_run_seconds` (L1244) and `stray_run_headings` (L1279);
  - `stray_run_headings` is called by `incomplete()` (L970);
  - `RUN_HEADING` is read by `incomplete()` and `batch_log_items` (L1359-1360);
  - `ROUND_HEADING_FROM` is used at L968/L977;
  - commit_step's functions are reached from `main` and the tests;
  - commit_step is named by run-item.md and the 2 pointers;
  - `grep -c TODO` gives 0 in both new files. Every branch of commit_step ends in exit 0/1/2. Connected.
- The 05 deviations and the run events the orchestrator named, judged one by one:
  1. **Trailers via `git commit --amend --only` (not in 05).** The reflog shows `66f0fcf commit_step: Item 091: 01:53 | I2 | ...`, then `4990002 commit (amend)`. I checked `66f0fcf^{tree}` = `4990002^{tree}` = a6cdc2cb..., and both parents = 8dec4f6. The amend changed only the message, so the commit content is commit_step's own. Accepted as safe. But it is a step outside the helper that no rule names: an `--amend` without `--only` would commit the shared index, which is exactly what 091 exists to prevent. 05 must record it (F3). Trailer support in the helper is a follow-up (below).
  2. **Helper output not pasted in 05 (Deviations 7).** Accepted: 05 is inside commit (C), so it cannot hold that commit's own output. The reflog entry `commit_step: <subject>` (update-ref's `-m`) is independent proof that (C) was made by the helper. Round 2 can paste round 1's output, which is now known (F3).
  3. **Container restart (Deviations 5).** Accepted. (A) and (B) were committed before it. The second run reviewed the uncommitted (C) files against 04. My own runs at head (suite, 39 mutants, probes) are what this verdict rests on, not the resumed run's.
  4. **Exit-term table.** It is not a deviation: 04 step 0 asks for it. 16 rows, none `none found`. I re-ran 2 of the terms (A8 `isinstance(branches, str)`, A9 `isinstance(ahead, str)`): both killed, as the table says. I did not re-run the other 14.
  5. **11 stray headings in 8 items vs 03's 10 in 7 (Deviations 1).** Confirmed by my own walk of work/*/05,06 with `stray_run_headings`: the same 11 lines. The 11th, 087/05 L237, last changed in 7389962 at 2026-11-22T01:00:20Z, after 03's check_handoff run (2026-11-21 23:43 UTC). R3's count was right when it was made, and I2 reported the difference rather than changing the expectation. Accepted. 087 < 92, so no entry.
  6. **Stray stash entries dropped (Deviations 5).** `git stash list` is empty now (count 0). The 3 entries were made from the detached scratch worktree (refs/stash is shared by all worktrees), and only those 3 existed, so nobody else's stash was lost. Accepted. But it shows the RI-009 scratch rule ("scratch copy, never in the repo") does not cover shared refs → follow-up.
  7. **Log-field file count 12.** Confirmed: `git diff --name-only 7e537c2 4990002 -- . ':!work' ':!logs'` gives 12, the same as 04's table.
  8. Deviations 2 (two 089 asserts extended by exactly the new 091 entry; nothing removed), 3 (`RUN_HEADING` dict as the single source; LOG BATCH unchanged) and 8 (the closer mutant kills N1 and the new flags test, not a pre-existing LOG BATCH test): accepted. Each is reported, not hidden.
- **The suite failure in I2's run.** `test_repo_pipeline_has_no_skipped_items` failed only on `INCOMPLETE: 091 (no log line for I2)`. That line was written after the run, because its field is the run's own last line. At head 4990002 the full suite is green: `805 passed, 1 skipped in 111.14s` (below). The skip is tests/test_calendar.py:110, where exchange_calendars is not installed. It is not the 3.10/3.11 compile test.

### Problems (sent back to I2)
- **F1. commit_step commits another item's log lines when the log file is named by an absolute path.** 04 step 6 (i) says the helper refuses "a named path under logs/research/ or logs/implementation/ (the helper finds those itself)". The code checks only the normalized relative text (`n == d or n.startswith(d + "/")`), so `/abs/repo/logs/implementation/<date>.md` passes. `update-index --add` then stages the whole working file. When this item adds no line of its own to that file, the filtered blob equals HEAD's, no `--cacheinfo` overrides it, and the commit carries the other items' lines. Probe B in my scratch repo (HEAD log = title + `01:00 | I1 | 149 | x`; working + `01:05 | I2 | 151 | foreign` + `01:06 | I2 | 150 | mine`, run after probe A committed 150's line):
  ```
  $ python3 /home/claude/cover-calls/scripts/commit_step.py 150 "Item 150: note" work/150/05.md $R/logs/implementation/2026-11-22.md
  90809d6 Item 150: note
  exit 0
  $ git show HEAD:logs/implementation/2026-11-22.md
  # log

  01:00 | I1 | 149 | x
  01:05 | I2 | 151 | foreign
  01:06 | I2 | 150 | mine
  ```
  The `./logs/...` form is refused, as is `../probe_repo/logs/...` (`git update-index failed (exit 128)`). Only the absolute form gets through. That is the form agents are told to prefer: their notes say "always use absolute paths". Fix:
  - resolve each named path against the repo top (`Path(p)` made absolute from the cwd, then `.resolve()` and `relative_to(top)`, refused if it is outside the top);
  - run the log-dir and directory checks on that relative form, and pass the relative form to `update-index`;
  - add T3 rows for an absolute log path (refused, `rev-parse HEAD` and `.git/index` unchanged) and an absolute non-log path (accepted, committed under its relative name);
  - add a mutant row: resolution removed → the absolute-log row fails.
- **F2. No negative test for filter_log's line-owner match (I3 step 3, item 059/RI-012).** filter_log decides which item a line belongs to by matching text (LOG_LINE, group 4 = ID). No test puts the pattern inside other text. The behaviour is right today. My direct call: a line `01:05 | I2 | 151 | see 150 | I3 | 150 | x` is dropped and not counted as 150's, and `note: 01:06 | I2 | 151 | quoted` is kept and not counted. But nothing pins it, and a mutant like `.search` without `^`, or an ID test by `f"| {item} |" in line`, would survive. Add `test_filter_log_pattern_inside_other_text` with those two lines (and the item's real line): the output keeps the note and the item's line, `own` is exactly the item's one line, and the 151 line is dropped.
- **F3. 05 record.** Add to Deviations: (C) was made by commit_step as 66f0fcf and amended to 4990002 with `git commit --amend --only` for the trailers, with the tree (a6cdc2c) and parent unchanged. Paste round 1's helper output (`66f0fcf Item 091: ...`). The round-2 runs go under `## Test output (round 2, pasted)` (the item's own rule). Rewrite the single `Suite:` line.

### New rules (091's own, judged by use in this round)
- SCRATCH: my dir was made with the mkdtemp command. The worktree path was fixed by the orchestrator (`/tmp/claude-0/scratch/i3-091/wt`), not mkdtemp-made. It did not collide (no earlier i3-091 dir existed), but the rule cannot hold while the orchestrator hands out fixed paths. Follow-up below.
- commit_step for this 06: used with relative paths only, so F1 does not apply. Result in "Sent back" below.

## Tests re-run (output)
Each later round's runs go under their own level-2 heading `## Tests re-run (round N)`, never under a `###` heading or a `Round N ...` heading (item 091).

`python3 -m pytest -q` in the worktree at 4990002 (tail as printed):
```
........................................................................ [ 80%]
........................................................................ [ 89%]
........................................................................ [ 98%]
..............                                                           [100%]
805 passed, 1 skipped in 111.14s (0:01:51)
```
`-rs`: `SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars'`. tests/test_safety.py: `9 passed in 1.15s`. python3.11 is on PATH (/usr/bin/python3.11) and python3.10 is not, so `test_every_py_compiles_on_oldest_python` ran with 3.11 (not skipped). Host python3 is 3.13.18.

`python3 scripts/check_handoff.py 091` (main checkout, 2026-11-22), exit 0:
```
sources count (unique URLs in 01-research.md): 11
fact-check rows: 79
totals line: 79 rows -> 61 as-is, 17 fixed, 1 removed
PASS
```
`python3 scripts/check_pipeline.py` before this file: exit 0, `091: in progress (FULL: next 06)`, `INCOMPLETE: none`, `SKIPPED: none`, LOG TIME and LOG BATCH do not name 091, `UNTRACKED CHANGE: none`.

Mutation probes. Each was one text replacement in the worktree, then `git checkout --` and a clean `git status` after each run. Harness: `.../i3-091-r1-dpe6hf15/mut.py`. Whole test file per row: test_pipeline_check.py, test_commit_step.py or test_probe_guardrails.py.
```
== A1: 1 failed, 380 passed in 48.48s            each_checked_group
== A2: 1 failed, 380 passed in 47.24s            each_checked_group
== A3: 1 failed, 380 passed in 47.63s            each_checked_group
== drop-work: 2 failed, 379 passed in 49.32s     with_work, each_checked_group
== drop-templates: 1 failed, 380 passed in 50.83s
== drop-scripts-ls: 1 failed, 380 passed in 52.18s
== equiv-cp: 381 passed in 51.76s                (equivalent, expected to survive)
== premise-scripts: 2 failed, 379 passed in 53.27s  each_checked_group, rule_path_files_are_inside_research_code_dirs
== A8: 1 failed, 380 passed in 54.93s            test_branch_list_failure_exits_1
== A9: 2 failed, 379 passed in 53.97s            main_ref_lookup, main_ahead_count
== A13: 1 failed, 380 passed in 53.52s           next_id_branch_listing_failure_refuses
== M11: 2 failed, 14 passed in 7.89s             trailing_text, trailing_newline
== M11b: 1 failed, 15 passed in 7.63s            trailing_newline
== 4a-runitem-old: 1 failed, 380 passed in 52.30s   unshallow_sentence
== 4b-all-four: 1 failed, 380 passed in 51.93s      unshallow_sentence
== 5a-build: 1 failed, 380 passed in 49.00s      round_heading_template_lines
== 5a-verif: 1 failed, 380 passed in 48.51s      round_heading_template_lines
== 5b-removed: 9 failed, 372 passed in 51.93s    P1-P3, one_entry_per_file, U, G x2, 2 unreadable 089
== 5b-###only: 2 failed, 379 passed in 50.16s    P2, one_entry_per_file
== 5b-noexempt: 1 failed, 380 passed in 52.83s   N1
== 5b-search: 1 failed, 380 passed in 50.96s     N2
== 5b-cutoff0: 2 failed, 379 passed in 49.69s    N3, test_repo_pipeline_has_no_skipped_items
== 5b-gate: 1 failed, 380 passed in 49.61s       G-not-seen
== 5b-closer3: 2 failed, 379 passed in 47.77s    N1, section_flags_match_run_seconds_rule
== 5b-opener: 17 failed, 364 passed in 50.96s    N1, N4 and 15 existing LOG BATCH / RULE NOT SEEN tests
== 5b-unread-silent: 3 failed, 378 passed in 51.72s  U, 2 unreadable 089 (my extra: unreadable branch made silent)
== 7-scr-a1 / 7-scr-i3 / 7-scr-i2 / 7-scr-run: 1 failed, 380 passed each   scratch_sentence_same_in_four_files
== M1-shared: 3 failed, 18 passed in 3.58s       t1 (x.txt), head_moved, write-tree
== M2-whole: 2 failed, 19 passed in 3.84s        t1, t4
== M3-append: 1 failed, 20 passed in 3.78s       t2
== M4-noold: 1 failed, 20 passed in 1.58s        head_moved
== M5-fallback: 2 failed, 19 passed in 1.47s     edited-head-line, filter_log_rule
== M6-subject: 1 failed, 20 passed in 1.66s      wrong-subject
== M7-order: 7 failed, 14 passed in 1.42s        t1, t2, head_moved, read-tree, write-tree, t4, t5
== M8-keepforeign: 10 failed, 11 passed in 1.48s (my extra: foreign lines kept)
== M9-batch: 1 failed, 20 passed in 1.60s        two-own-lines (my extra)
== M10-namedlog: 1 failed, 20 passed in 1.72s    named-log (my extra; relative form only, see F1)
== M11-noreset: 3 failed, 18 passed in 1.46s     t1, t2, t5 (my extra)
== 6t-i3ptr: 1 failed, 20 passed in 1.58s        commit_rule_texts
== 6t-i2ptr: 1 failed, 20 passed in 1.53s        commit_rule_texts
```
The whole printed output, including each FAILED line, is in `mut_fast.txt` and `mut_cp.txt` in my scratch dir. All 04 mutants are killed, except the equivalent one that 04 expects to survive. Its premise is pinned (premise-scripts).

Feasibility numbers (RI-001), re-measured:
- step 1: 8 BRANCH ERROR lines (the test passes, A1-A3 fail it);
- step 2: A8's control exits 0 and the patched run exits 1 (the test passes, the mutant fails);
- step 5b: 11 headings in 8 items at cutoff 0 (03 said 10/7; the extra one postdates 03, see above);
- 0 items >= 92 (work/ ends at 091);
- step 6 T1: 4 of 5 lines kept (the test passes).

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat 7e537c2 4990002 -- ccbot/ config/ data/` is empty: no TRIGGER or TRIGGER_DIRS file changes)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-010, RI-014, RI-002, RI-008, RI-009, RI-012, RI-013. What I checked for each:
- RI-001 (ESCALATED): every count was re-measured, not taken from 03/05: 8/10 entries isolable (equiv-cp survives, premise-scripts kills); 11/8 headings (differs from 03, explained by date); 0 items >= 92; 4 of 5 lines in T1.
- RI-010 (ESCALATED): commit_step is the new guardrail for "a step's commit carries another item's line", and F1 shows a way around it. That is why this round FAILs. The 5b check is INCOMPLETE-enforced and every mutant is killed. 5a and 7 are text only, and 05 says so.
- RI-014 (OPEN): no new depth-dependent reader. 5b uses `_rule_seen` (strict when shallow, 084). UNSHALLOW names RULE NOT SEEN. The worktree reports `--is-shallow-repository` false.
- RI-002 (GUARDED): commit_step's `head is None` means ls-tree exit 0 with empty output (a real "not in HEAD"); a failed ls-tree/cat-file is a refusal (T3 patched rows pass). No default on a failed read in 5b (U, plus my 5b-unread-silent mutant killed). Not a BUG item, so no default-restore probe is required.
- RI-008 (GUARDED): the 3.11 compile test ran (not skipped); no `prefixmatch`; the f-string join is built outside the expression.
- RI-009 (GUARDED): all my runs were in a scratch worktree and a mkdtemp dir; no stash. I2's stash incident was confined (stash list empty), but it shows the gap that refs/stash is shared → follow-up.
- RI-012 (GUARDED): STRAY_RUN_HEADING has its negative test (N2, killed by `.search`). filter_log's owner match has none → F2.
- RI-013 (GUARDED): 05's whole-output diff of check_pipeline before/after (B) is IDENTICAL. My check_pipeline run at head shows the same sections, with only 091's status changing.

## Pipeline line (step 2)
check_pipeline line: `091: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))`

Run after this file and the `--log` line: exit 1, `I3 FAIL: 091`, `INCOMPLETE: none`, `SKIPPED: none`, LOG TIME and LOG BATCH do not name 091 (the expected FAIL-round state).

## Sent back / sent to Audit
Sent back to I2 (round 1): F1 (absolute log path bypass, with 2 T3 rows and a mutant), F2 (negative owner-match test), F3 (05 record of the amend and of the helper output). No 07 is written. I1's plan stands, and the fixes are inside 04 step 6 (i) and I3 step 3.

This 06 and the I3 log line are committed with `python3 scripts/commit_step.py 091 "Item 091: <line>" work/091/06-verification.md` (relative path). The helper takes no trailer argument, so the session trailers are added with `git commit --amend --only` (message only; I check the tree is unchanged), the same as I2 did.

Proposed follow-ups (for A1 to open; not part of 091's fix):
1. commit_step: an option to add trailer lines (e.g. repeated `--trailer "<k>: <v>"` passed to `commit-tree -m`), so no agent has to amend outside the helper.
2. SCRATCH vs the orchestrator: run-item should tell the orchestrator to hand out mkdtemp-made dirs (or let agents with a shell make their own), not fixed paths like `/tmp/claude-0/scratch/i3-091/wt`.
3. RI-009 scratch rule: add "no `git stash` in a scratch worktree (refs/stash is shared by all worktrees); use `git checkout -- <file>` or a copy".
4. 088 A1 finding 1's remainder: the `not checked (unborn HEAD)` label for an unresolvable HEAD (05 Deviations 4).

# Round 2 (I3, 2026-11-22)
Verified at head 1293415 (I2 round 2), base of the round d39d811 (my round-1 FAIL). Worktrees `wt` (suite) and `wt2` (mutants) of 1293415 under `/tmp/claude-0/scratch/i3-091r2-UxQ8`, made with `mktemp -d` as the orchestrator asked; my outputs, harness and probe repo are in my own dir made with step 3's mkdtemp command: `/tmp/claude-0/-home-claude/6b779538-e393-5b21-a85a-072369e659f6/scratchpad/i3-091-r2-mz28r6tf`. Both worktrees were removed after the runs. I used no `git stash` (`git stash list | wc -l` = 0 before and after).

## I1 audit, round 2
No change to 04 in round 2, and none was needed: F1-F3 were inside 04 step 6 (i) and I3 step 3. Nothing goes back to I1.

## I2 audit, round 2 (build vs my round-1 list)
`git diff --stat d39d811 1293415`: scripts/commit_step.py, tests/test_commit_step.py, work/091/05-build-report.md, and one log line (`02:34 | I2 | 091 | ...`, the only line the commit adds to logs/implementation/2026-11-22.md). No other file. `git diff --stat d39d811 1293415 -- ccbot config data` is empty.
- **F1 (fixed).** New `repo_relative(p, top)`: `os.path.abspath`, the parent `.resolve()`d (the name is not, so a named symlink stays a symlink), then `relative_to(top)`. Outside the top gives Refused, exit 2. `commit()` keeps the resolved `topdir` (the same value the cwd check compares) and runs every named path through it before the log-dir, missing and directory checks. `update-index` and the final `reset` get the relative form. The 6 new T3 cases are the rows I asked for (absolute log path refused, in 2 shapes; absolute non-log path committed relative), plus the outside-top and symlinked-dir rows (05 Deviations 11, sourced from F1's fix text). `topdir = ... else None` is no default: None is refused on the next line.
- **F2 (fixed).** `test_filter_log_pattern_inside_other_text` has my two lines plus the item's own line. It asserts the exact output bytes and `own == [L150]`.
- **F3 (fixed).** 05 Deviations 9 records the round-1 amend: 66f0fcf to 4990002, tree a6cdc2c, parent 8dec4f6. Its helper output was rebuilt from the reflog and 05 says so. Round 2 is under `## Test output (round 2, pasted)`, and the single column-0 `Suite:` line is round 2's.
- **Round-2 commit made by the helper.** Reflog: `c01d0d5 commit_step: Item 091: 02:34 | I2 ...`, then `1293415 commit (amend)`. `c01d0d5^{tree}` = `1293415^{tree}` = e6769854bb5e, and both parents are d39d811. The amend changed only the message (05 Deviations 10).
- **F2-search survives (05 Deviations 11).** Accepted as equivalent. check_pipeline's `LOG_LINE` is `^(\d{2}):(\d{2}) \| ... \| (.*)$`, compiled with no flags. So `.search` can only match at position 0, and that is `.match`. The non-equivalent forms (anchor dropped, substring owner) are killed below.
- Connectivity, re-done: `repo_relative` is called once, at L158 (`n = repo_relative(p, topdir)`). It is reached by the 6 new cases and by my CLI probes below. There is no TODO in either file.

## Tests re-run (round 2)
`python3 -m pytest -q -rs` in `wt` at 1293415 (my own run, made after 05 round 2 existed), tail as printed:
```
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'
1 failed, 811 passed, 1 skipped in 113.51s (0:01:53)
```
The only failure is the expected item-071 state. Its assertion output names `091: I3 FAIL (FULL; sent back to I2, needs a later PASS round in 06 (item 071))` and `I3 FAIL: 091`, from my committed round-1 FAIL. INCOMPLETE, SKIPPED and A1 FAIL are all none in the same output. Round 1 had 805 passed; adding the 6 new cases gives 811. tests/test_safety.py: `9 passed in 1.34s`. python3.11 is on PATH and python3.10 is not, so the oldest-Python compile test ran with 3.11 and did not skip.

`python3 scripts/check_handoff.py 091` (main checkout), exit 0:
```
sources count (unique URLs in 01-research.md): 11
fact-check rows: 79
totals line: 79 rows -> 61 as-is, 17 fixed, 1 removed
PASS
```

My F1 probe, re-run with the round-2 helper (`$CS` = wt's scripts/commit_step.py) in a fresh probe repo in my dir. HEAD log = title + `01:00 | I1 | 149 | x`, and x.txt is staged.
```
== probe B (working log + `01:05 | I2 | 151 | foreign` only; absolute log path)
commit_step refused: <R>/logs/implementation/2026-11-22.md: log files are found by the helper; do not name them (item 091)
exit 2   HEAD unchanged   index unchanged (sha1sum of .git/index)
== probe A (+ `01:06 | I2 | 150 | mine`; absolute log path)
commit_step refused: ... log files are found by the helper ...   exit 2
== absolute non-log path ($R/work/150/05.md)
a581fe1 Item 150: 01:06 | I2 | 150 | mine      exit 0
  commit files: logs/implementation/2026-11-22.md, work/150/05.md
  HEAD log: # log / 01:00 | I1 | 149 | x / 01:06 | I2 | 150 | mine      (151's line dropped)
  still staged: x.txt
== /etc/hostname                      -> is outside the repo top ... exit 2
== ./logs/implementation/...          -> log files are found by the helper ... exit 2
== ../probe_repo/logs/implementation/... -> log files are found by the helper ... exit 2   (round 1: update-index exit 128)
== L -> logs symlink in repo: L/implementation/2026-11-22.md and $R/L/implementation/... -> log files are found by the helper ... exit 2
```
The last row is my extra: a symlinked directory inside the repo that leads to logs/ is caught because the parent is resolved.

Direct `filter_log` call (my extra lines). The work text was `01:05 | I2 | 151 | see 150 | I3 | 150 | x`, `note: 01:06 | I2 | 151 | quoted`, `01:07 | I3 | 150 | real` and `150 | I2 | 151 | y`. The output keeps the note, the 150 line and the `150 | I2 ...` line (not a LOG_LINE), and drops the 151 line. `own == ['01:07 | I3 | 150 | real']`.

Mutants: one text replacement each in `wt2`, the whole tests/test_commit_step.py run, and the file restored after each. Harness `.../i3-091-r2-mz28r6tf/mut.py`, output `mut.txt`. `git status --porcelain` after: empty.
```
== F1-noresolve: 4 failed, 24 passed in 2.24s
    FAILED tests/test_commit_step.py::test_t3_absolute_log_path_is_refused[with-own-line]
    FAILED tests/test_commit_step.py::test_t3_absolute_log_path_is_refused[no-own-line]
    FAILED tests/test_commit_step.py::test_t3_path_outside_repo_is_refused[absolute]
    FAILED tests/test_commit_step.py::test_t3_path_outside_repo_is_refused[relative]
== F1-noparentresolve: 1 failed, 27 passed in 4.36s
    FAILED tests/test_commit_step.py::test_t3_absolute_path_through_symlinked_dir
== F2-search-equiv: 28 passed in 1.92s
== F2-search-noanchor: 1 failed, 27 passed in 1.73s
    FAILED tests/test_commit_step.py::test_filter_log_pattern_inside_other_text
== F2-substr: 1 failed, 27 passed in 1.78s
    FAILED tests/test_commit_step.py::test_filter_log_pattern_inside_other_text
```
- F1-noresolve: round 1's `Path(os.path.normpath(p)).as_posix()` put back.
- F1-noparentresolve: `a.relative_to(top)`.
- F2-search-noanchor: `re.search(LOG_LINE.pattern[1:], ...)`.
- F2-substr: `f"| {item} |" not in line` as the drop test.

Every count matches 05's round-2 table. The equivalent mutant survives, as 05 says.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat 7e537c2 1293415 -- ccbot/ config/ data/` is empty: no TRIGGER or TRIGGER_DIRS file changes)

## Recurring issues checked (round 2)
Recurring issues checked: RI-001, RI-010, RI-014, RI-002, RI-008, RI-009, RI-012 (round 2). What I checked for each:
- RI-001 (ESCALATED): I measured every number myself. 811 = 805 + 6 new cases. The mutant failures were 4/1/0/1/1, the same as 05. Probe B is refused with HEAD and the index unchanged.
- RI-010 (ESCALATED): the bypass of the new guardrail (F1) is closed and pinned by F1-noresolve (4 killed). Both round-2 commits were made by the helper; the reflog and the trees show this. The I2 line was written by `--log`.
- RI-014 (OPEN): no new git reader. `repo_relative` is path arithmetic on the top that the code already read.
- RI-002 (GUARDED): `topdir ... else None` is refused at once, never used as a value.
- RI-008 (GUARDED): the 3.11 compile test ran (test_safety 9 passed). `os.path.abspath`, `Path.resolve` and `relative_to` all exist on 3.10.
- RI-009 (GUARDED): mutants ran only in a scratch worktree. No stash was used. Both worktrees were removed.
- RI-012 (GUARDED): filter_log now has its negative test. The substring and unanchored mutants are killed.

## Pipeline line (step 2, round 2)
check_pipeline line: `091: awaiting A1 (FULL)`

Run after this file, 07 and the `--log` line (`02:39 | I3 | 091 | PASS | sent to audit: yes`), before the commit: exit 0. `AWAITING A1: 091`, `I3 FAIL: none`, `A1 FAIL: none`, `INCOMPLETE: none`, `SKIPPED: none`, `UNTRACKED CHANGE: none`; LOG TIME and LOG BATCH do not name 091 (RULE NOT SEEN names only 083, as before).

## Sent back / sent to Audit (round 2)
PASS. Nothing is sent back. Sent to Audit: `work/091/07-audit-task.md`. Round 1's follow-ups 1-4 still stand:
1. a trailer option in commit_step: round 2 needed `--amend --only` again, for I2 and for this commit;
2. orchestrator scratch paths: this round was `mktemp -d`-made and unique, but it is not step 3's mkdtemp form or location, so I made both;
3. no `git stash` in a scratch worktree;
4. 088's unborn-HEAD label.
