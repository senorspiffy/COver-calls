# 05 Build report - 097
Scratch dir: /tmp/claude-0/-home-claude/17dd566b-e13e-58fe-b556-13d450b5acde/scratchpad/i2-097-r1-yoi5b4bm

Built by I2 on branch `daily-fixes/2026-11-24`. I made the scratch dir myself with `python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="i2-097-r1-", dir="/tmp/claude-0/-home-claude/17dd566b-e13e-58fe-b556-13d450b5acde/scratchpad"))'`. The mutation worktree was `<scratch dir>/wt`, made with `git worktree add --detach` and removed afterwards (`git worktree list` then shows only the main checkout). No `git stash` was run anywhere. Probe files were restored from in-memory copies, never in the main checkout.

RULE_PATHS are touched (.claude/, templates/, scripts/check_pipeline.py), so RULES BRANCH shows and **the person's OK is needed at PR review**. The review also covers option (i), the reading of "the orchestrator never names a scratch path", which the plan's Fit check flags.

## Base (plan Tests and checks 1)
- Head at start: 45699f54bc56323ea39d5ea2461ab7e67bf860fa. 095's A1 then committed 762c8ec7b58a8b45294d8166329a5a7834bf50cb, which touches only logs/audit and work/095/07. That commit is this build's base.
- `git stash list; echo "exit $?"` in the orchestrator checkout, at base:
```
exit 0
```
  (empty list, so no stop.) Re-run before this 05 was finished: the same (`exit 0`, no lines).
- Census total in the base (`test_git_call_census`): `assert sum(seen.values()) == 50`. After the build it is 51, which is the base plus 1 (`("main", "_git_ok")`, a new key with count 1).
- GIT_LINES in the base: `("LOG TIME:", "OPEN BRANCHES", "IN PR:", "RULES BRANCH:", "ID CLASH:", "MAIN AHEAD:", "UNTRACKED CHANGE:", "RESEARCH CODE:", "REAL-DATA FIELD:", "UNCOMMITTED STEP:", "INBOX:", "RULE NOT SEEN:")`. After the build, `"STASH:"` is appended.

## Changes made (file: what changed)
Commits, in the plan's order: A `5550445` (rule text and pins), B `13fb139` (STASH line), and C, which is the commit holding this final 05 and the I2 log line.

**A (5550445)**
- `.claude/commands/run-item.md`, `.claude/agents/i2-builder.md`, `i3-verifier.md`, `a1-auditor.md`: 091's SCRATCH sentence is replaced in each file by 03 step 1's sentence, byte for byte.
- `i2-builder.md`: "(`git worktree add` or a copied folder)" becomes "(a `git worktree add --detach` worktree or a copied folder)".
- `run-item.md`: after "and `LOG BATCH:` must not name it (item 086)", added " and `STASH:` must be `none`; only the person drops or clears a stash entry, and an agent never drops one it did not make (item 097)".
- `i2-builder.md`, `i3-verifier.md`: right after the SCRATCH sentence, added "05 (I2) / 06 (I3) has one column-0 `Scratch dir: <path mkdtemp printed>` line per dir used, or `Scratch dir: none (<reason>)` (item 097)."
- `tests/test_pipeline_check.py`:
  - `OLD_SCRATCH` holds 091's text; `SCRATCH` holds the new text; `SCRATCH_FILES` lists the 4 files.
  - `test_scratch_sentence_same_in_four_files` checks `count(SCRATCH) == 1` and `count(OLD_SCRATCH) == 0` in each file, plus `"git stash" in SCRATCH and "--detach" in SCRATCH`.
  - New tests: `test_run_item_stash_clause`, `test_i2_detach_phrase` and `test_scratch_dir_line_in_agent_texts` (i2 and i3). Each checks `count == 1`.

**B (13fb139)**
- `scripts/check_pipeline.py` `main()`: right after the `UNCOMMITTED STEP:` print, `stash_out, stash_why = _git_ok("stash", "list")` gives one of four results:
  - `"no git"`: `STASH: not checked (no git)`, exit unchanged.
  - any other reason: `STASH: not checked (<why>) (item 097)` and `stash_bad = True`. stdout is not read.
  - exit 0 with `stash_out.strip() == ""`: `STASH: none`.
  - otherwise: `STASH: <n> (first: <first non-empty line>); local to this checkout; only the person drops an entry (item 097)` and `stash_bad = True`.
  - `or stash_bad` is added to the return expression. The module docstring gets a `STASH` entry under UNCOMMITTED STEP (item 097, RI-009, exit 1, decided by exit code only, the cosmetic `n`, and the known gap).
- `tests/test_pipeline_check.py`:
  - `GIT_LINES` gains `"STASH:"`. `GIT_CENSUS` gains `("main", "_git_ok"): (1, "097: stash list; ...")`, and the total goes 50 to 51.
  - `test_repo_pipeline_has_no_skipped_items` reads `git stash list` in REPO first. Non-empty means exit 1 and `STASH: <n> (first: ...`; empty means exit 0 and `STASH: none` in the lines.
  - `test_malformed_shallow_real_git_nothing_none` (b) exempts only `STASH:` from the no-none rule and asserts `["STASH: none"]`. The reason is no refs/stash, so no history read (stash.c list_stash). Measured: without the exemption the test failed on `STASH: none`.
  - New fixtures:
    - (a)+(b) `test_stash_entry_is_listed_then_none_after_drop`
    - (c) `test_stash_failed_read_is_not_checked`: the monkeypatched `("stash","list")` gives `("stash@{0}: WIP on main: abc x\n", 128)`, so stdout holds text and mutant B3 is killed.
    - `test_stash_no_git_is_not_checked_exit_unchanged`
    - (d) `test_stash_in_detached_worktree_is_seen_by_main_checkout`
    - (e) `test_stash_entry_with_bad_shallow_is_never_none`
  - Helpers: `_stash_repo`, `_short`, `STASH_TAIL`.

**C (this commit)**
- `scripts/check_pipeline.py`:
  - `SCRATCH_FROM = 97` sits after `ROUND_HEADING_FROM`, with a comment ("the 9th `*_FROM` cutoff"). Also new: `SCRATCH_NAME = re.compile(r"(i2|i3)-(\d{3})-r\d+-[a-z0-9_]{8}")` (used with `.fullmatch`), `SCRATCH_AGENT = {"05": "i2", "06": "i3"}`, and `from pathlib import Path, PurePosixPath`.
  - New `scratch_dir_problems(text, step, item)` reads column-0 `Scratch dir:` lines on `_md_lines` "out" rows, the same way `_suite_lines` does.
    - No line gives `<step> has no Scratch dir: line (item 097)`.
    - Each value is the whole text after `Scratch dir:`, stripped. It is OK if it fullmatches `none \((.*)\)` with a non-blank reason. It is also OK if it is absolute (`PurePosixPath(v).is_absolute()`) and the basename (one trailing `/` stripped) fullmatches SCRATCH_NAME, with group 1 equal to the step's agent and group 2 equal to the item ID.
    - Anything else gives `<step> Scratch dir '<value>' is not the mkdtemp form (item 097)`.
  - `incomplete()`, right after the ROUND_HEADING_FROM block: `if int(item_dir.name) >= SCRATCH_FROM:` loops over 05 and 06.
    - An absent file is skipped.
    - A `_read` failure gives `<step> scratch dir not checked (<why>; item 097)`.
    - Problems go through `_rule_seen(item_dir, step, "SCRATCH_FROM", env)`. False gives the not_seen row `(ID, step, sha7, "SCRATCH_FROM", "097", "no Scratch dir check")`. `unsure(step)` sends the problems to `unchecked` (see Deviations 3). Otherwise they go to `missing`, plus the sha7 note.
    - Docstring sentences were added to `incomplete` (item 097, plus the 095 list of gates). The module RULE NOT SEEN paragraph says "7 from SCRATCH_FROM on" in the cost sentence and lists "Scratch dir" among 095's gates.
- `templates/build-report.md`: the line `Scratch dir: <absolute path printed by mkdtemp; one line per dir used, or none (<reason>)>` goes right after the `# 05` title. `templates/verification.md` gets the same line after the `Sent back to:` comment block.
- `tests/test_pipeline_check.py`:
  - `import tempfile`. New `_scratch_line(step, item)`: the fixture's good line (`/tmp/x/scratchpad/i2|i3-<ID>-r1-ab_cd123`) for IDs >= 97, else "".
  - `_item`, `_batch_item`, `_suite_item` and `_rounds_item` add it to the 05/06 they write. Two tests that rewrite 05/06 by hand do the same (`test_incomplete_06_and_missing_log_line`, `test_commits_before_cutoff_ignored`). See Deviations 2.
  - Expected strings updated in `test_unreadable_06` and `test_unreadable_05_at_suite_check`, which now also have `0x scratch dir not checked (...; item 097)`. `test_unfilled_template_suite_line_is_incomplete` now also expects the template's unfilled `Scratch dir:` placeholder entry (N9 on the real template).
  - New tests:
    - `test_scratch_dir_template_line` (both templates)
    - `test_scratch_dir_good_lines` (P1, P2, P3, N6)
    - `test_scratch_dir_bad_lines` (N1-N5, N7-N12, plus one bad line next to a good one)
    - `test_scratch_dir_06_is_tied_to_i3`
    - `test_scratch_dir_cutoff_boundary` (097 entry, 096 none)
    - `test_scratch_dir_real_mkdtemp_name`
    - `test_scratch_dir_absent_step_file_no_entry`
    - `test_scratch_dir_unreadable_05_not_checked`
    - `test_scratch_dir_no_anchor_env_is_strict`
    - `test_scratch_dir_gate_follows_rule_file_of_05_commit` (G-not-seen, G-seen)
- `tests/test_real_data_field.py`: `_rd_item` adds `_scratch_line` to its 05/06 (imported from test_pipeline_check).

File counts (item 012) for commit C's uncommitted part, taken before this 05 was finished:
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
0
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
5
```
The whole item compared with base 762c8ec (A+B+C), `git diff --stat 762c8ec -- . ':!work' ':!logs'`:
```
 .claude/agents/a1-auditor.md  |   2 +-
 .claude/agents/i2-builder.md  |   2 +-
 .claude/agents/i3-verifier.md |   2 +-
 .claude/commands/run-item.md  |   4 +-
 scripts/check_pipeline.py     |  85 ++++++++++-
 templates/build-report.md     |   1 +
 templates/verification.md     |   1 +
 tests/test_pipeline_check.py  | 346 ++++++++++++++++++++++++++++++++++++++----
 tests/test_real_data_field.py |   7 +-
 9 files changed, 408 insertions(+), 42 deletions(-)
```
So 9 files changed over the item and 0 new code files. The plan named 8; the 9th is tests/test_real_data_field.py (Deviations 2). The log field says 9.

## Connectivity check
- [x] Every new function or rule is used:
  - `scratch_dir_problems` is called by `incomplete`.
  - `SCRATCH_FROM` is read by `incomplete`, and its name by `_rule_seen`. `SCRATCH_NAME` and `SCRATCH_AGENT` are read by `scratch_dir_problems`.
  - `stash_bad` is read by the return expression.
  - Each rule sentence has a `count == 1` pin, and the template lines are pinned.
- [x] Every input has a source and every output has a consumer:
  - `git stash list` feeds the STASH line and the exit code.
  - The 05/06 text (via `_read`) feeds INCOMPLETE, INCOMPLETE NOT CHECKED (shallow), RULE NOT SEEN, UNREADABLE and the exit code.
- [x] Every branch ends in a defined result:
  - STASH has four outcomes: no git → not checked, exit unchanged; failed → not checked, exit 1; empty → none; entries → listed, exit 1.
  - Scratch dir: below 097, no check. A missing 05/06 gives no entry, because classify reports it. Unreadable → `scratch dir not checked`. No line → entry. A bad value → entry. not_seen → RULE NOT SEEN row. Shallow and committed → INCOMPLETE NOT CHECKED. Otherwise strict.
- [x] No leftover TODOs or unused files. `git diff 762c8ec | grep -c TODO` gives 0 added. Scratch files live only in my scratch dir. The worktree was removed.
- Missing-data grep (`grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/`): 38 hits, all from before this item. `git diff --stat -- ccbot/ config/` is empty. The same pattern on the lines this item added to scripts/check_pipeline.py gives 5 lines:
  - 4 are comment or docstring text where "for 05 / or 06" matches `or 0`. They are not code.
  - `or unchecked or stash_bad else 0`: the existing exit expression. A bad stash read adds exit 1 (fail closed).
- No dataclass was added. The new `>=` (`int(item_dir.name) >= SCRATCH_FROM`) compares ints from an `isdigit()` name, never NaN. `stash_bad = False` is a flag that only a defined bad outcome sets to True; it is not a defaulted value. STASH is decided by the exit code and empty stdout only. No line text is classified (RI-012). Matching is an anchored `.fullmatch`, with negative fixtures N1-N12.

## Feasibility numbers (plan Guardrail tests)
- STASH in this checkout: 0 entries at base and at build time (`git stash list` printed nothing, exit 0). Fixtures: (a) 1 entry → exit 1; (b) 0 → `STASH: none`, exit 0, and the raw `git stash list` gives `(0, "")` on git 2.43.0; (c) failed read → not checked, exit 1; (d) 1 entry made in a `--detach` worktree is seen in the main checkout.
- (e), measured in my scratch dir on git 2.43.0: a stash entry, then `.git/shallow` = `<head>\nzz\n`. `git stash list` printed `fatal: bad shallow line: zz` and exited **1** (it printed `stash@{0}: WIP on main: 49f0cb0 c`, exit 0, before the corruption). The fixture pins `STASH: not checked (git stash failed (exit <that exit>)) (item 097)`. It asserts the exit is non-zero, and it is 1 here.
- (b) with no stash and a bad shallow file, measured: `STASH: none` (the test failed on it before the exemption). The same holds for `test_non_utf8_shallow_line_no_traceback` (Deviations 4).
- Scratch-dir shape over the 8 known 091 dirs, using the basename rule: 3 pass, 5 fail (plan Extra research 1). Fixtures pin the passing cases (P1, P2, P3, N6 and a real mkdtemp) and 12 failing cases.
- SCRATCH_FROM covers 0 items before 097. `check_pipeline.py` below shows no INCOMPLETE entry for any item other than 097, and 097's own entry is only the I2 log line before it is written.
- Census: base 50, after 51.

## Mutants (plan Tests and checks 3)
Run in `<scratch dir>/wt`, a `git worktree add --detach` worktree of 13fb139 with commit C's files copied in. Each file was restored from an in-memory copy. Command: `python3 -m pytest -q -p no:cacheprovider tests/test_pipeline_check.py` per mutant. Output pasted as printed by my driver script (`<scratch dir>/mutants.out`). `test_repo_pipeline_has_no_skipped_items` fails in every run for the reason given in Test output, so the driver also counts the failures other than that one:
```
A1: 2 failed, 467 passed in 67.85s (0:01:07) | other than repo test: 1 e.g. ['test_scratch_sentence_same_in_four_files']
A2: 2 failed, 467 passed in 61.19s (0:01:01) | other than repo test: 1 e.g. ['test_scratch_sentence_same_in_four_files']
A3: 2 failed, 467 passed in 65.19s (0:01:05) | other than repo test: 1 e.g. ['test_i2_detach_phrase']
A4: 2 failed, 467 passed in 66.33s (0:01:06) | other than repo test: 1 e.g. ['test_run_item_stash_clause']
B1: 4 failed, 465 passed in 66.48s (0:01:06) | other than repo test: 3 e.g. ['test_stash_entry_is_listed_then_none_after_drop', 'test_stash_failed_read_is_not_checked', 'test_stash_in_detached_worktree_is_seen_by_main_checkout']
B2: 4 failed, 465 passed in 69.72s (0:01:09) | other than repo test: 3 e.g. ['test_all_git_fails_no_line_says_none', 'test_stash_failed_read_is_not_checked', 'test_stash_entry_with_bad_shallow_is_never_none']
B3: 4 failed, 465 passed in 70.76s (0:01:10) | other than repo test: 3 e.g. ['test_all_git_fails_no_line_says_none', 'test_stash_failed_read_is_not_checked', 'test_stash_entry_with_bad_shallow_is_never_none']
C1: 22 failed, 447 passed in 73.41s (0:01:13) | other than repo test: 21 e.g. ['test_unfilled_template_suite_line_is_incomplete', 'test_unreadable_06', 'test_unreadable_05_at_suite_check']
C2: 3 failed, 466 passed in 66.72s (0:01:06) | other than repo test: 2 e.g. ['test_scratch_dir_bad_lines[N7-9-chars]', 'test_scratch_dir_bad_lines[N12-trailing-text]']
C3: 3 failed, 466 passed in 64.98s (0:01:04) | other than repo test: 2 e.g. ['test_scratch_dir_bad_lines[N3-agent-not-i2]', 'test_scratch_dir_06_is_tied_to_i3']
C4: 2 failed, 467 passed in 62.27s (0:01:02) | other than repo test: 1 e.g. ['test_scratch_dir_bad_lines[N10-wrong-id]']
C5: 2 failed, 467 passed in 62.65s (0:01:02) | other than repo test: 1 e.g. ['test_scratch_dir_cutoff_boundary[FROM]']
C6: 3 failed, 466 passed in 65.34s (0:01:05) | other than repo test: 2 e.g. ['test_scratch_dir_good_lines[P2-no-scratchpad-trailing-slash]', 'test_scratch_dir_real_mkdtemp_name']
```
Mutant edits:
- A1: a1-auditor.md goes back to OLD_SCRATCH.
- A2: the new sentence is deleted from i3-verifier.md.
- A3: the i2 phrase is reverted.
- A4: the run-item clause is removed.
- B1: `or stash_bad` is dropped.
- B2: the failed-read branch prints `STASH: none` and does not set the flag.
- B3: stdout is tested first (`stash_out.strip() == ""` → none, before the exit check).
- C1: `if False:` replaces the SCRATCH_FROM test.
- C2: `.match` replaces `.fullmatch`.
- C3: `m[1] in ('i2', 'i3')`.
- C4: the ID test becomes `True`.
- C5: `SCRATCH_FROM = 98`.
- C6: the `/scratchpad/` segment replaces the basename.

All 13 mutants fail at least one test other than the repo test.

## Test output (pasted, not summarized)
`python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py tests/test_real_data_field.py` (RI-008), Python 3.11.18: exit 0, no output. The suite runs on Python 3.13.18.

After commit A, before this 05 existed: `885 passed, 1 skipped in 157.46s (0:02:37)`. After B's edits, at HEAD 5550445 (commit A, with the partial 05): `1 failed, 889 passed, 1 skipped in 122.86s (0:02:02)`. The 1 failure was `test_repo_pipeline_has_no_skipped_items`, which saw `INCOMPLETE: 097 (no log line for I2)` (see the note below).

Full suite, working tree = commit C's files plus this 05, HEAD 13fb139, run from the repo root:
```
$ python3 -m pytest -q
(progress dots omitted; the failure's INCOMPLETE line and the tail as printed)
E             INCOMPLETE: 097 (no log line for I2)
E           assert 1 == 0
...
tests/test_pipeline_check.py:199: AssertionError
=========================== short test summary info ============================
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 916 passed, 1 skipped in 128.98s (0:02:08)
```
Suite: 1 failed, 916 passed, 1 skipped in 128.98s (0:02:08)

Note on the 1 failure, expected and not a defect of this build. `test_repo_pipeline_has_no_skipped_items` runs check_pipeline on a detached worktree of HEAD. HEAD (13fb139) holds the partial 05 from commits A and B without its I2 log line, so it prints `INCOMPLETE: 097 (no log line for I2)` and exits 1. The log line is written by `--log` after this run and committed in C. The in-tree `check_pipeline.py` run below, made after `--log`, shows 097 with no INCOMPLETE entry. See Deviations 1.

`python3 scripts/check_pipeline.py` in the orchestrator checkout, after the `--log` line was written:
```
(exit 0; the lines naming 097 and the summary lines, as printed)
097: in progress (FULL: next 06)
RULES BRANCH: none
I3 FAIL: none
A1 FAIL: none
INCOMPLETE: none
RULE NOT SEEN: 083 (05 added in cfc0634 without TESTS_FORMAT_FROM (076): judged by I2_BEFORE; 06 added in cfc0634 without VERDICT_FROM (071): judged by no Sent-back check; item 084)
LOG TIME: none (not checked: 048: built before 045's --log rule reached main; times typed by hand, not recoverable (item 049))
LOG BATCH: none (not checked: 083: six lines written in one batch at 10:15 after the build (commit cfc0634 10:15:48); real times not recoverable (item 086)); not computable: 048: no pytest time in 05/06/I2 line; 054: no pytest time in 05/06/I2 line; 055: no pytest time in 05/06/I2 line; 056: no pytest time in 05/06/I2 line; 058: no pytest time in 05/06/I2 line; 059: no pytest time in 05/06/I2 line; 060: no pytest time in 05/06/I2 line
UNTRACKED CHANGE: none
UNCOMMITTED STEP: none
STASH: none
UNREADABLE: none
SKIPPED: none
```

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat 762c8ec -- ccbot/ config/ data/` is empty; files changed: .claude/agents/a1-auditor.md, .claude/agents/i2-builder.md, .claude/agents/i3-verifier.md, .claude/commands/run-item.md, scripts/check_pipeline.py, templates/build-report.md, templates/verification.md, tests/test_pipeline_check.py, tests/test_real_data_field.py)

## Deviations from plan
1. **Commits A and B each carry a partial 05.** UNTRACKED CHANGE (053) flags a commit that changes code, tests or rules without a step file of an open item. So code commits A and B had to include a step file, and I committed a partial 05 in each. That 05 has no I2 log line until C, so at A and B, `check_pipeline.py` and `test_repo_pipeline_has_no_skipped_items` report `INCOMPLETE: 097 (no log line for I2)`. The plan's "each commit leaves the suite green" cannot hold for intermediate code commits under 053 plus 043; at A and B every other test was green. **For I1:** a plan that asks for several code commits should say which step file each one carries.
2. **Fixture helpers carry a good `Scratch dir:` line, which the plan did not name.** Many existing fixtures use IDs >= 97 (150, 151, 160, 172, 179, 990, 999 ...), so the new check made 110 tests fail (85 in test_pipeline_check.py, 25 in test_real_data_field.py) with `has no Scratch dir: line`. I followed the item-082 precedent, where `_item` writes the Suite line. `_scratch_line(step, item)` adds a good line for IDs >= 97 to the 05/06 that `_item`, `_batch_item`, `_suite_item`, `_rounds_item`, `_rd_item` and two hand-written fixtures produce. No assertion was weakened. Three expected strings gained the new entry (`test_unreadable_06`, `test_unreadable_05_at_suite_check`, and the S7 template test, which now pins N9 on the real template). This adds a 9th file, tests/test_real_data_field.py. I3 should check that the helper change hides no existing check: the line is added only for IDs >= 97, and only to files those helpers already wrote.
3. **The `unsure` branch (095) is in the Scratch block.** The plan says "as the ROUND_HEADING_FROM block does". Since 095, that block has an `elif unsure(step): unchecked...` branch, so the Scratch block has one too: in a shallow clone, a committed 05/06's Scratch entries go to INCOMPLETE NOT CHECKED, like every other gated entry. The 095 docstring list names it.
4. **`test_non_utf8_shallow_line_no_traceback` gets the same `STASH: none` exemption as (b).** It also iterates GIT_LINES with a corrupted shallow file and no stash. Measured: it failed on `STASH: none` until the exemption was added, for the same reason (no refs/stash, so no history read). The plan named only (b).
5. Fixture (e) pins the exit it measures (`raw.returncode`, asserted non-zero) and does not hard-code 1, so that a git version giving 128 still gets an exact line. The measured exit, 1 on git 2.43.0, is recorded above.
6. A fixture for STASH without git (`test_stash_no_git_is_not_checked_exit_unchanged`) was added for the plan's Missing-inputs row. Also added: a two-line case with one bad value, and an absent-file fixture and an `env="no git"` fixture (`test_scratch_dir_absent_step_file_no_entry`, `test_scratch_dir_no_anchor_env_is_strict`), both named in the plan's Guardrail tests.

## Next item (plan change 4)
098 comes after 097, and its ID is >= SCRATCH_FROM. So 098's own 05 and 06 must each carry a column-0 `Scratch dir: <path mkdtemp printed>` line (i2-098-... in 05, i3-098-... in 06), or `Scratch dir: none (<reason>)`. Without it, `check_pipeline.py` shows `INCOMPLETE: 098 (05 has no Scratch dir: line (item 097))`. 098's I1/I2: test fixtures with IDs >= 97 get the line through `_scratch_line` (Deviations 2).

## Residuals (no check can see these)
- STASH sees only entries left behind, so 091's run (3 entries made, 3 dropped) would still pass.
- The no-stash rule at the moment of use is text only.
- The orchestrator's hand-outs to R1-R3/I1 are text only, because their files have no Scratch dir field. I1's dir for this item was `/tmp/claude-0/-home-claude/17dd566b-e13e-58fe-b556-13d450b5acde/scratchpad/i1-097-r1-rti7e4v7` (from 04).
- A1's own dir is text only.
- `n` in the STASH line may count lines added by user log config. That is cosmetic: `n` never decides the result, and the exit and empty stdout cannot turn entries into `none`.
- The Scratch dir field shows that a path of the mkdtemp shape was written, not that mkdtemp made it.
- The `--detach` part of the sentence is preventive only: no `wt` branch was found from 091 (03 C8).

## Recurring issues checked (item 013)
- RI-001 (ESCALATED): every filter has a dated count (Feasibility numbers): STASH 0 entries on 2026-11-24, fixtures 1/0/fail/1; the shape check is 3 of 8 pass; 0 earlier items affected; census 50 → 51.
- RI-010 (ESCALATED): the new duties are in the agent text (i2/i3 Scratch dir sentence, run-item STASH clause), and the checks that can exist enforce them (STASH exit 1, INCOMPLETE Scratch dir). The text-only parts are listed under Residuals.
- RI-014 (OPEN): the one new git read goes through `_git_ok`. A failed read prints `not checked`, never none (mutant B2 is killed). The shallow cases are measured: no stash gives a true none, and a stash entry gives not checked, exit 1.
- Also checked:
  - RI-002: nothing defaulted (grep reasons above).
  - RI-004/005: the counts were re-derived. `ab_cd123` has 8 chars, `ab_cd1234` has 9, and `Scratch dir: /tmp/` is 18 bytes, so the non-UTF-8 byte sits at byte 18. My first guess of 17 was wrong; the test caught it and I fixed it.
  - RI-006: the census total was read from the base, not typed.
  - RI-007: FULL scope, code only in I2.
  - RI-008: py_compile on 3.11.
  - RI-009: this item. No stash was used, the scratch dir came from mkdtemp, and the worktree was `--detach` inside it, then removed.
  - RI-012: decided by exit code and empty stdout; anchored fullmatch; negative fixtures.
  - RI-013: no realtest path.
RI-009: guardrail built (097). The STASH line plus the Scratch dir INCOMPLETE check, both with fixtures; all 13 mutants are killed. Stays GUARDED.
RI-010: guardrail extended (097). The Scratch dir duty is enforced by INCOMPLETE from SCRATCH_FROM; it stays ESCALATED until 086 is merged (its own condition).
