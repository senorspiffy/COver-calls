# 05 Build report - 095

Built by I2 on branch `daily-fixes/2026-11-24`, base commit 16b46ba (after 092, 093, 096 and 094, as the plan's build order says; 094's A1 PASS commit 5bc02ca landed during this build and touches only logs/audit and work/094/07). Scratch dir: /tmp/claude-0/-home-claude/17dd566b-e13e-58fe-b556-13d450b5acde/scratchpad/I2-095-r1-fma16f8l (made with mkdtemp, item 091). Mutations ran in a copied folder there (`tree/`), never in the repo.

RULE_PATHS: scripts/check_pipeline.py, .claude/agents/a1-auditor.md, .claude/commands/run-item.md and .claude/commands/daily-audit.md are rule paths, so the person's OK is needed in PR review.

## Changes made (file: what changed)
- scripts/check_pipeline.py:
  - New `_unsure(item_dir, step, env, committed)` before `incomplete()`: False unless `env == SHALLOW_TEXT` (equality); then True when `committed is None` or `work/<ID>/<step file>` is in `committed`.
  - New `_head_work_files()`: `_git_ok("ls-tree", "-r", "--name-only", "HEAD", "--", "work/")`; None on failure, else the set of lines.
  - `incomplete(..., unchecked=None, committed=None)`. A local `unsure(step)` returns `unchecked is not None and _unsure(...)`. At each gate an `elif unsure(<step>):` branch sits between the `seen is False` branch and the strict branch:
    - TIMED gate (05): I2 removed from `bad`; `log line for I2 does not match its format (item 045): I2 wants "<log_hint('I2', ID, new_rule)>"` appended to `unchecked`.
    - TESTS gate (05): same, only when every own I2 line passes `log_fields_ok(..., new_rule=False)`; else I2 stays in `bad` (exact).
    - Other agents in `bad` keep their entry in the return value.
    - LOG BATCH not computable (05), Suite (05), round headings (05 and 06, keyed on the loop's step), VERDICT (06, one tuple per fired text).
    - Docstring: an item 095 paragraph.
  - `open_branches()`: the unrelated dict has `"held": len(held) if why is None else None` (variable `count`). Docstring sentence added.
  - `main()`: `unchecked = []` and `committed = _head_work_files() if shallow else None` after `shallow = ...`; both passed to `incomplete`. After the `INCOMPLETE:` print, only `if shallow:`, the line `INCOMPLETE NOT CHECKED: <ID> (<e1>; <e2>), ...; rule seen not checked (shallow clone; run git fetch --unshallow; item 095)` or `INCOMPLETE NOT CHECKED: none`. Exit: `or unchecked` added.
  - `main()` OPEN BRANCHES list branch: `unrelated and shallow` refs go to `folded` (initialised before the print block, so it exists on every path); after the loop one `  shallow clone: <n> ref(s) with no merge base not checked (<refs>); run git fetch --unshallow (item 095)` line.
  - `branch_errors`: per-ref errors skipped for folded refs whose `held` is an int; one summary `shallow clone; <k> of <n> ref(s) hold files on checked paths, not checked (<refs with held > 0>); run git fetch --unshallow (item 095)` when k >= 1. A folded ref with `held` None keeps its own `<ref> (<why>)`.
  - Module docstring: the OPEN BRANCHES 090 paragraph now describes the fold (and the known gap "merged and open unrelated refs are not told apart"); the RULE NOT SEEN paragraph has an item 095 paragraph (INCOMPLETE NOT CHECKED, C1, the known gaps the plan names).
- tests/test_pipeline_check.py:
  - `UNSHALLOW` constant: the new sentence. `test_unshallow_sentence_same_in_three_files` asserts `"INCOMPLETE NOT CHECKED" in UNSHALLOW and "095" in UNSHALLOW`.
  - `GIT_CENSUS`: `("_head_work_files", "_git_ok"): (1, ...)`; total 49 -> 50.
  - `_shallow_source(..., merged=0)`: pushes `claude-old1..N` at c1 before `dev`.
  - Edited: T18 (`test_shallow_three_readers_not_checked`, folded sub-line and summary BRANCH ERROR), T19 (`test_shallow_docs_only_orphan_exit_0`, folded sub-line), e1 (`test_rule_not_seen_shallow_and_no_git`, 150 on NOT CHECKED, not on INCOMPLETE; e2 unchanged), `test_non_utf8_shallow_line_no_traceback` (one NOT CHECKED line).
  - New: `test_shallow_gated_entries_not_checked` (T-a), `test_depth1_clone_083_shape_not_incomplete` (T-a2), `test_shallow_exact_tests_entry_stays_incomplete` (T-a3), `test_shallow_other_agent_format_entry_stays` (T-a4), `test_shallow_uncommitted_step_stays_incomplete` (T-a5), `test_unsure_unit_and_head_tree_failure` (T-a6), `test_shallow_merged_refs_fold_to_one_line` (T-b), `test_shallow_fold_held_unknown_keeps_own_error` (T-b2). Helper `_shallow_rules`, constants `NC_TAIL`, `I2_ENTRY`, `FOLD_D1`, `FOLD_ERR`.
  - Grep for `startswith("INCOMPLETE")` / `_pick(out, "INCOMPLETE")` without the colon in tests/: no hit, nothing to fix.
- .claude/agents/a1-auditor.md, .claude/commands/run-item.md, .claude/commands/daily-audit.md: the UNSHALLOW sentence replaced, byte for byte the same in all three, with the plan's text. 094's single-branch sentence after it is untouched.

File counts (item 012), taken before this 05 existed:
```
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'
0
$ git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'
5
```
So: 5 files changed, 0 new code files. The only new file is work/095/05-build-report.md.

## Connectivity check
- [x] Every new function or rule is used. `_unsure` is called by `incomplete`'s `unsure`, which is used at all 7 gate branches. `_head_work_files` is called in `main()` (shallow only). `unchecked` is printed on `INCOMPLETE NOT CHECKED:` and read by the exit. `held` is read by `branch_errors` and the summary. `folded` feeds the sub-line and the summary. The rule sentence is pinned by `test_unshallow_sentence_same_in_three_files`.
- [x] Every input has a source and every output has a consumer. Inputs: `env` (`_anchor_env`), HEAD's tree (`ls-tree -r HEAD -- work/`), the per-ref `ls-tree` count. Outputs: the `INCOMPLETE NOT CHECKED:` line, the `shallow clone:` sub-line, the summary BRANCH ERROR, exit 1.
- [x] Every branch ends in a defined result:
  - not shallow (full, no git, unborn, failed verify) -> unchanged strict path, no new line, no extra git call;
  - shallow, step file committed -> NOT CHECKED, exit 1; shallow, step file not in HEAD's tree -> INCOMPLETE (as full clone);
  - shallow, HEAD tree read fails -> `committed` None -> NOT CHECKED, exit 1;
  - shallow, nothing gated -> `INCOMPLETE NOT CHECKED: none`;
  - TESTS gate with an I2 line failing I2_BEFORE -> stays INCOMPLETE (exact);
  - `incomplete` called without `unchecked` -> nothing moves (strict; see Deviations);
  - folded ref with `held` > 0 -> in the summary; `held` 0 -> sub-line only; `held` None -> own BRANCH ERROR, exit 1.
- [x] No leftover TODOs or unused files. `git diff | grep -c TODO` adds none. Scratch files are only in the scratch dir.
- Missing-data grep (`grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/`): 38 hits, all pre-existing; `git diff --stat -- ccbot/ config/` is empty, so no new or changed hit there. The same pattern on `git diff -U0 scripts/check_pipeline.py` gives 2 added lines:
  - `return unchecked is not None and _unsure(...)`: not a default; a None collector means nothing moves (strict), never a pass.
  - `or unchecked else 0`: the existing exit expression; a non-empty list adds exit 1 (fail closed).
- No dataclass field added. The one new `>` is `b["held"] > 0`, guarded by `isinstance(b.get("held"), int)`, so None never compares (and is never 0). Env and held tests use `==`/`!=`/isinstance only, never error text (RI-012).

## Test output (pasted, not summarized)
Full suite, working tree with this build plus this 05 (HEAD 5bc02ca):
```
$ python3 -m pytest -q
........................................................................ [  8%]
........................................................................ [ 16%]
...........s............................................................ [ 24%]
........................................................................ [ 32%]
........................................................................ [ 40%]
........................................................................ [ 48%]
........................................................................ [ 57%]
........................................................................ [ 65%]
........................................................................ [ 73%]
........................................................................ [ 81%]
........................................................................ [ 89%]
........................................................................ [ 97%]
..................                                                       [100%]
881 passed, 1 skipped in 152.97s (0:02:32)
```
Suite: 881 passed, 1 skipped in 152.97s (0:02:32)

Targeted run while building:
```
$ python3 -m pytest -q -x tests/test_pipeline_check.py -k "shallow or unsure or depth1 or census or unshallow or rule_not_seen or unrelated"
.....................................                                    [100%]
37 passed, 396 deselected in 23.78s
```

Mutations (copied tree in the scratch dir, `scripts/check_pipeline.py` edited there, each named test run alone; script `mut.py` in the scratch dir):
```
M1 test_shallow_gated_entries_not_checked -> 1 failed in 0.71s | E       AssertionError: 150: complete (FULL)
M1 test_depth1_clone_083_shape_not_incomplete -> 1 failed in 0.89s | E       AssertionError: 150: complete (FULL)
M2 test_rule_not_seen_shallow_and_no_git -> 1 failed in 1.27s | E       AssertionError: 150: complete (FULL)
M3 test_shallow_uncommitted_step_stays_incomplete -> 1 failed in 0.67s | E       AssertionError: 150: complete (FULL)
M4 test_shallow_exact_tests_entry_stays_incomplete -> 1 failed in 0.75s | E       AssertionError: 150: complete (FULL)
M5 test_shallow_gated_entries_not_checked -> 1 failed in 0.75s | E       AssertionError: 150: complete (FULL)
M6 test_shallow_merged_refs_fold_to_one_line -> 1 failed in 1.24s | E       AssertionError: 150: STUCK (FULL, opened 2026-11-20, 1 day(s) with request.md only)
M7 test_unrelated_branch_with_work_is_branch_error -> 1 failed in 0.89s | E       AssertionError: 040: IN PR (origin/fix has 01 02 03 04 05 06 07; was STUCK here)
M8 test_shallow_fold_held_unknown_keeps_own_error -> 1 failed in 1.02s | E       AssertionError: 150: STUCK (FULL, opened 2026-11-20, 1 day(s) with request.md only)
M11 test_shallow_three_readers_not_checked -> 1 failed in 1.33s | E       AssertionError: 150: STUCK (FULL, opened 2026-11-20, 1 day(s) with request.md only)
```
(The `E` text is the start of each assert's `out` message, the script output.) M1 `_unsure` returns False; M2 `if env is None: return False`; M3 `return True` after the env test; M4 TESTS branch without the I2_BEFORE `all(...)`; M5 `or unchecked` removed; M6 fold condition `if False:`; M7 fold on `unrelated` alone; M8 per-ref error filter `True` (held None folded, no own error); M11 `shallow = False` in `main()`. All 9 fail their named test. M5: T-a's shallow run has `INCOMPLETE: none` (asserted), so NOT CHECKED is its only exit-1 source.

Step 5 checks:
- Full-clone whole-output diff (this repo, not shallow; old = `git show 5bc02ca:scripts/check_pipeline.py`, new = working tree; run at HEAD 5bc02ca): old exit 0, new exit 0, 119 lines each, `diff` exit 0 (empty).
- Real counts, depth-1 `--no-single-branch` clone: a bare repo in the scratch dir holding this repo's 31 `refs/remotes/origin/*` as heads, with `daily-fixes/2026-11-24` set to HEAD 5bc02ca; 29 fold, origin/main is skipped (090) and daily-fixes/2026-11-24 is HEAD (no network); `git clone -q --depth 1 --no-single-branch --branch daily-fixes/2026-11-24 file://.../src.git d1`, `--is-shallow-repository` true. Old vs new script there (both exit 1), whole diff:
  - old: 29 per-ref `  <ref>: not checked (shallow clone; ...)` lines and 29 per-ref `BRANCH ERROR:` lines (held 108 to 796 files each); new: 1 `  shallow clone: 29 ref(s) with no merge base not checked (...)` line and 1 `BRANCH ERROR: shallow clone; 29 of 29 ref(s) hold files on checked paths, not checked (...)`. 58 lines -> 2. (03 said 28 of 28 on 2026-11-22; one more daily-fixes branch exists today.)
  - old: `INCOMPLETE: 083 (log line for I2 ...; 06 Verdict is PASS but has no 'Sent back to: none' line (item 071))`; new: `INCOMPLETE: none` and `INCOMPLETE NOT CHECKED: 083 (log line for I2 does not match its format (item 045): I2 wants "<n> files changed | tests <last line of python3 -m pytest -q, as printed>"; 06 Verdict is PASS but has no 'Sent back to: none' line (item 071)); rule seen not checked (shallow clone; run git fetch --unshallow; item 095)`. 1 item, 2 entries, as 03.
  - No other line differs.
- Plain `--depth 1` (single-branch) clone of the same source, new script, exit 1: `OPEN BRANCHES: not checked (single-branch clone; ...)` (094), `INCOMPLETE: none`, and the same `INCOMPLETE NOT CHECKED: 083 (...)` line.
- `python3 scripts/check_pipeline.py` on this repo at HEAD 5bc02ca with this build, before 05: exit 0, `INCOMPLETE: none`, `095: in progress (FULL: next 05)`.
- `python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py`: no error (RI-008).

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat`: .claude/agents/a1-auditor.md, .claude/commands/daily-audit.md, .claude/commands/run-item.md, scripts/check_pipeline.py, tests/test_pipeline_check.py; none is in TRIGGER or TRIGGER_DIRS)

## Deviations from plan
- `incomplete()` called with `unchecked=None` (the default) moves nothing: the plan names only the collecting call. Without this, a caller that does not pass a list would lose the entries silently; strict is the missing-data default. `main()` is the only caller and always passes the list. Pinned in T-a6 (`incomplete(item, env=SHALLOW_TEXT)` returns both entries).
- Fixture (b) real counts are 29 refs, not 03's 28: one more branch on origin since 2026-11-22.
- None else.

## Recurring issues checked (item 013)
Read logs/recurring-issues.md first; checked against every open or ESCALATED entry, plus the GUARDED ones the plan names.
- RI-001 (ESCALATED): both selectors computed on real data with dated non-zero counts (083: 1 item, 2 entries; 29 of 29 refs, k = 29), and fixtures pin each, with an empty result (T19: 0 held, no BRANCH ERROR, exit 0; full clone: no NOT CHECKED line).
- RI-010 (ESCALATED): log line written only by `check_pipeline.py --log`, after this file; commit via `commit_step.py`. No step duty changed; the rule sentence is pinned by a test.
- RI-014 (OPEN): this item. M11 still fails T18; full-clone whole-output diff empty.
- RI-002 (GUARDED): an unknown anchor, a failed HEAD tree read or a failed ls-tree is never a pass, 0 or none; exit stays 1.
- RI-012 (GUARDED): equality on env, the `held` key, never error text.
- RI-004/RI-005/RI-006: counts taken from command output (the d1 diff), not by hand.
- RI-009 (GUARDED): folded refs keep their names; 094's single-branch path unchanged; mutations in a copied folder.
- RI-008 (GUARDED): python3.11 compile clean.

RI-014: OPEN; 095 built (shallow gated entries -> INCOMPLETE NOT CHECKED, shallow unrelated refs fold to one line + one BRANCH ERROR); M11 still fails T18; GUARDED condition unchanged (merged and M11 fails on main).
RI-001: ESCALATED, unchanged; 095's selectors have dated real counts (1 item / 2 entries; 29 of 29 refs).
RI-010: ESCALATED, unchanged; no step duty changed.
