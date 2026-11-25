# 04 Build plan - 095
Fit verdict: FIT WITH CHANGES

Base: branch daily-fixes/2026-11-24 (on open PR #36), built right after 094 (build order 092, 093, 096, 094, 095, 097, 098). This plan is on top of 094's planned changes (work/094/03-handoff.md map steps 1-8): `SINGLE_TEXT`, `fetch_coverage()`, the `if branches == SINGLE_TEXT` print in `main()`, the exit test `(isinstance(branches, str) and branches != SINGLE_TEXT)`, 094's single-branch sentence after the UNSHALLOW sentence in the three rule files, and GIT_CENSUS with `("fetch_coverage", "_git"): 2`. Everything below is anchored by function or constant name, because line numbers move after 094 (the 03 line numbers already differ by about 2 on today's tree: `incomplete()` starts at L874, `main()`'s OPEN BRANCHES block at L2013).

Fit check:
- Account and strategy: tooling only (scripts/check_pipeline.py, its tests, rule text). No effect on the ~$3k account, the screen or any trading rule. The 001 rules (slack, tolerance, cap) are not touched.
- Existing code: fits. Step 1 is a new list beside `not_seen` in `incomplete()`. Step 2 adds one dict key and changes printing only in `main()`. `check_handoff.py` reads only `b["ref"]` and `b["items"]` (03 #29), so the new key is safe.
- Conflicts: 094 touches the same `main()` print block and the same rule-file line. These are not text conflicts if 095 is built after 094: 094's SINGLE_TEXT branch sits before the `isinstance(branches, str)` branch, and 095 changes only the list branch and `branch_errors`. In a plain `--depth 1` clone (single-branch), 094 returns SINGLE_TEXT, so 095's fold applies only to `--no-single-branch` shallow clones, which is the A1 28-ref shape. 095's step 1 runs in both.
- RULE_PATHS are touched (.claude/, scripts/check_pipeline.py), so the person's OK is needed in PR review. tests/ is CODE_PATHS (03 #35).

Changes to 03 (why the verdict is "with changes"):
- C1 (an edge case R3 missed). In a full clone, an uncommitted 05/06 gets `(None, "")` from `_rule_seen` and the entry stays INCOMPLETE (03 #43). The 03 map's switch `env == SHALLOW_TEXT` alone would move that entry to NOT CHECKED in a shallow clone, even though the full clone keeps it. That is a false "not checked" for in-progress items, which is exactly when I3 runs the check. So `_unsure` also needs the step file to be in HEAD's tree. That set is read once in `main()`, and only when shallow, so the full-clone run makes no extra git call.
- C2. 03 step 4 says "merge 094's single-branch sentence into the same edit". 094's plan keeps its sentence separate, right after UNSHALLOW, with its own count test, and never edits UNSHALLOW. 095 edits only the UNSHALLOW sentence and the constant, and leaves 094's sentence and test alone.
- C3. Fixture (a) reuses the existing 084 fixture helpers (`_rules_repo`, `_merge_main_into_rules`, `_shallow`, `_unshallow`, `_defective`), plus one real `git clone --depth 1 --no-single-branch` variant so the request's "Depth-1 fixture" is a real clone. The existing test `test_rule_not_seen_shallow_and_no_git` (e1) asserts `"150 (" in INCOMPLETE` in the shallow case. That assertion is the old behaviour and has to change (named below).

## Extra research (with sources)
1. `git ls-tree` "Lists the contents of a given tree object" (https://git-scm.com/docs/git-ls-tree). So `ls-tree -r --name-only HEAD -- work/` lists only files committed at HEAD and never the index or the working tree. The repo already relies on this in two places: `uncommitted_steps()` (item 077), and `test_staged_step_is_still_uncommitted` ("HEAD's tree decides, never the index"). `test_uncommitted_step_in_shallow_clone` pins that ls-tree HEAD sees the whole tip tree in a depth-1 clone. The docs say nothing about an absent path. The repo pins it in `test_rule_anchor_without_rule_file` (exit 0, empty output). That is enough for C1's membership test.
2. Shallow semantics (https://git-scm.com/docs/shallow, verified in 03 #1): the boundary commits act as root commits. In a shallow clone, a step file can be (i) committed under the boundary (the anchor can't be known), (ii) committed after the boundary (knowable; the finer `_shallow_boundaries` test stays a follow-up, 03 #50), or (iii) uncommitted. The full clone gives (iii) a known answer, `(None, "")`, which means strict and keep the entry. Only (i) and (ii) are truly unsure. C1 separates (iii) at the cost of one ls-tree.
3. `git clone --depth` "Implies --single-branch unless --no-single-branch is given" (https://git-scm.com/docs/git-clone, 03 #2). With 094 built, the BRANCH ERROR fold (step 2) can only be reached from a `--no-single-branch` shallow clone. Fixture (b) must use the existing `_clone` helper, which passes `--no-single-branch`.

## Files to create/change
1. scripts/check_pipeline.py
   - New helper `_unsure(item_dir, step, env, committed)` placed before `incomplete()`. It returns True only when `env == SHALLOW_TEXT` (equality, never `env is not None`, never `seen is None`; 03 #43/#44) and the step file is committed: `committed is None` (the HEAD read failed, so it can't be known, which stays not checked and exit 1) or `f"work/{item_dir.name}/{STEPS[step]}" in committed`. This is the one switch for every gate.
   - New helper `_head_work_files()`: `out, why = _git_ok("ls-tree", "-r", "--name-only", "HEAD", "--", "work/")`. It returns `None` if `why` is set, else `set(out.splitlines())`. Docstring: item 095, C1.
   - `incomplete(item_dir, logs=..., env=None, not_seen=None, batch_nc=None, unchecked=None, committed=None)`. `unchecked` is a list of `(ID, entry)`, like `not_seen`. At each gate where the full clone's `seen is False` branch would drop the entry, and `_unsure(...)` is True, the entry text goes to `unchecked` instead of `missing`:
     - TIMED gate (05): remove "I2" from `bad` and append `log line for I2 does not match its format (item 045): I2 wants "<log_hint('I2', ID, new_rule)>"`.
     - TESTS gate (05): only when every own I2 line passes `log_fields_ok(..., new_rule=False)` (the existing `all(...)`). It moves I2 the same way. When any I2 line fails I2_BEFORE, the entry is exact and stays in `missing` (03 step 1).
     - Only I2 moves. Other agents in `bad` keep their `log line for <agents> ...` entry in `missing`.
     - LOG BATCH (05): the `LOG BATCH not computable: <nc> (item 090)` entry.
     - SUITE (05): `fired`.
     - ROUND_HEADING (05 and 06, both turns of the loop): `fired`, keyed on that loop's step.
     - VERDICT (06): `fired`.
     - With env set, `_rule_seen` gives `(None, "")`, so no sha7 note is added either way. The no-git, unborn and failed-verify envs are unchanged (strict, `missing`).
     - Docstring: an item 095 paragraph.
   - `open_branches()`: in the `mb[1] == 1` (unrelated) branch, add the key `"held": len(held) if why is None else None`. Nothing else in the dict or its errors changes. Docstring: `held`, item 095.
   - `main()`:
     - After `(env, env_failed), not_seen = _anchor_env(), []` and `shallow = ...`, add `unchecked = []` and `committed = _head_work_files() if shallow else None`. Pass `unchecked=unchecked, committed=committed` to `incomplete(...)`.
     - Right after the `INCOMPLETE:` print, and only `if shallow:`, group by ID in first-seen order and print `INCOMPLETE NOT CHECKED: <ID> (<e1>; <e2>), <ID> (...); rule seen not checked (SHALLOW_TEXT; item 095)`. With no entries, print `INCOMPLETE NOT CHECKED: none`.
     - Exit: add `or unchecked` to the return expression (fail closed; 03 exit default).
     - OPEN BRANCHES list branch: replace the per-ref `if b.get("unrelated") and b.get("shallow")` print with a skip that collects those refs into `folded`. After the loop, if `folded` is not empty, print once `  shallow clone: <n> ref(s) with no merge base not checked (<ref>, <ref>, ...); run git fetch --unshallow (item 095)`. Refs keep the order in which `open_branches` lists them, and the per-ref age is dropped.
     - `branch_errors`: per-ref errors are built for every `b` except folded refs whose `held` is an int. Then, if `k = sum(1 for b in folded if isinstance(b.get("held"), int) and b["held"] > 0)` is ≥ 1, append one `shallow clone; <k> of <n> ref(s) hold files on checked paths, not checked (<refs with held > 0>); run git fetch --unshallow (item 095)`. A folded ref with `held` None keeps its own `<ref> (<why>)` error. Classification uses the `held` key only, never error text (RI-012).
     - Not touched: the full-clone 081 unrelated line, scanned refs, the str path, and 094's SINGLE_TEXT line.
   - Module docstring: the RULE NOT SEEN paragraph (the "No git or a shallow clone ... prints `RULE NOT SEEN: not checked`" text) now says that shallow gated entries go to INCOMPLETE NOT CHECKED. The open_branches/090 known-gaps paragraph (the "unrelated ref prints `<ref>: not checked (shallow clone ...)`" text) now describes the fold. Known gaps kept: no-git and unborn entries are not labelled, merged and open refs are still not told apart in a shallow view, and the finer boundary test is not built. One more known gap: in a shallow clone, an exact TESTS entry keeps the new-rule hint while the full clone shows the I2_BEFORE hint. That is today's behaviour, and both views are INCOMPLETE.
2. tests/test_pipeline_check.py (tests listed below)
   - `UNSHALLOW` constant: the new text (file 3).
   - `GIT_CENSUS`: add `("_head_work_files", "_git_ok"): (1, "095: failure -> None -> entries stay not checked, exit 1")`. Total after 094 goes from 49 to 50.
   - `_shallow_source(..., merged=0)`: a new keyword that pushes `merged` branches `claude-old1..N`, each pointing at c1 (which holds work/150), before `dev` is made. Default 0, so T18 and T19 build the same repo as today.
3. .claude/agents/a1-auditor.md (L22), 4. .claude/commands/run-item.md (L12), 5. .claude/commands/daily-audit.md (L4): replace the UNSHALLOW sentence, byte for byte the same in all three, with:
   `If \`git rev-parse --is-shallow-repository\` prints true, run \`git fetch --unshallow\`, then test again. If it is still true, report UNTRACKED CHANGE, RESEARCH CODE, REAL-DATA FIELD, LOG TIME, MAIN AHEAD, OPEN BRANCHES and RULE NOT SEEN as 'not checked', never 'none'; the \`INCOMPLETE NOT CHECKED:\` entries and the one \`shallow clone:\` OPEN BRANCHES line with its BRANCH ERROR are 'not checked', not errors, though the run exits 1 for them (items 079, 084, 090, 095).`
   (The backslashes here only mark the backticks; the files use plain backticks, as today.) 094's single-branch sentence after it is left as it is.

## Tests and checks
New and edited tests (all `@NO_GIT` where they use real git):
- T-a `test_shallow_gated_entries_not_checked` (fixture (a), C3): `_rules_repo` → `_merge_main_into_rules` → `_shallow(repo, rules)`.
  - Shallow: `INCOMPLETE:` does not contain `150 (`. `INCOMPLETE NOT CHECKED:` == `INCOMPLETE NOT CHECKED: 150 (log line for I2 does not match its format (item 045): {NEW_I2_WANT}; {NO_SENT_BACK}), 151 (...); rule seen not checked (shallow clone; run git fetch --unshallow; item 095)`. 151, built on `rules`, is unsure in the shallow view too. I2 pins the exact text from the run. `RULE NOT SEEN: not checked (shallow clone; ...)` is unchanged, and exit is 1.
  - After `_unshallow`: `RULE NOT SEEN:` == SEEN_150, 150 is not in INCOMPLETE, 151 is in INCOMPLETE, no line starts with `INCOMPLETE NOT CHECKED`, and `item 095` is not in the output.
- T-a2 `test_depth1_clone_083_shape_not_incomplete`: the same source repo cloned with `git clone -q --depth 1 --no-single-branch file://...` (rules checked out). Asserts `INCOMPLETE:` has no `150 (`, 150 is on `INCOMPLETE NOT CHECKED:` with 2 entries, and exit is 1.
- T-a3 exactness twin: `_rules_repo(i2="1 files changed | tests 10/9")` + merge + `_shallow`. 150's I2 format entry stays in `INCOMPLETE:`, and only `NO_SENT_BACK` for 150 is on NOT CHECKED.
- T-a4 other-agent twin: append a bad R1 line for 150 (`12:00 | R1 | 150 | x`) in the shallow fixture. `INCOMPLETE:` holds `150 (log line for R1 does not match its format`, and NOT CHECKED holds 150's I2 entry.
- T-a5 uncommitted twin (C1): in the shallow fixture, `_defective(repo, "153")` is left uncommitted. 153's I2 and VERDICT entries stay in `INCOMPLETE:`, and 153 is not on NOT CHECKED. Full-clone control (after `_unshallow`): 153 is in INCOMPLETE as well.
- T-a6 unit, `incomplete(item, env=SHALLOW_TEXT, unchecked=u, committed=None)` on 150: the entries go to `u`. With `committed=set()`, they stay in the return value. `_head_work_files` with `_patched_git` failing ls-tree → None.
- T-b `test_shallow_merged_refs_fold_to_one_line` (fixture (b)): `_shallow_source(merged=2)`.
  - Full clone: only `  origin/claude-x: items none; merges cleanly`, no `claude-old`, no `BRANCH ERROR`.
  - Depth 1 (`_clone(..., "--depth", "1")`): exactly 1 line contains `ref(s) with no merge base not checked`, and it is `  shallow clone: 3 ref(s) with no merge base not checked (origin/claude-old1, origin/claude-old2, origin/claude-x); run git fetch --unshallow (item 095)`. Exactly 1 `BRANCH ERROR:` line == `BRANCH ERROR: shallow clone; 3 of 3 ref(s) hold files on checked paths, not checked (origin/claude-old1, origin/claude-old2, origin/claude-x); run git fetch --unshallow (item 095)`. No line starts with `  origin/claude-old`, and exit is 1.
- T-b2 unit: `open_branches(shallow=True)` with `_patched_git` giving merge-base exit 1 and ls-tree 128 for one ref → `held` None and `errors == ["git ls-tree failed (exit 128)"]`. `main()` prints `BRANCH ERROR: <ref> (git ls-tree failed (exit 128))` and no shallow summary.
- T18 edit (`test_shallow_three_readers_not_checked`): the sub-line assertion becomes the folded form (1 ref, origin/claude-x). The BRANCH ERROR assertion becomes `BRANCH ERROR: shallow clone; 1 of 1 ref(s) hold files on checked paths, not checked (origin/claude-x); run git fetch --unshallow (item 095)`. The LOG TIME, MAIN AHEAD, origin/main and full-clone assertions are kept, so M11 still fails it by name.
- T19 edit (`test_shallow_docs_only_orphan_exit_0`): the sub-line becomes `  shallow clone: 1 ref(s) with no merge base not checked (origin/docs); ...`. `BRANCH ERROR` stays absent, and exit 0 is kept.
- e1 edit (`test_rule_not_seen_shallow_and_no_git`): the shallow `"150 (" in INCOMPLETE` becomes `"150 (" in _pick(out, "INCOMPLETE NOT CHECKED:")` and `"150 (" not in _pick(out, "INCOMPLETE:")`. e2 (no git) is kept exactly as it is: that is the `env is not None` detector.
- `test_non_utf8_shallow_line_no_traceback`: add an assertion that one `INCOMPLETE NOT CHECKED:` line is present. That pins that an unreadable shallow file takes the shallow path.
- `test_unshallow_sentence_same_in_three_files`: unchanged code. It now passes only with the new constant in all three files. Add `assert "INCOMPLETE NOT CHECKED" in UNSHALLOW and "095" in UNSHALLOW`.
- `test_git_call_census`: passes with the new census row.
- I2 greps the tests for `startswith("INCOMPLETE")` or `_pick(out, "INCOMPLETE")` without the colon (two lines would match in shallow runs) and fixes any it finds.

Mutations (I3; each must fail a named test):
- M1: `_unsure` always False → T-a, T-a2.
- M2: `_unsure` keyed on `env is not None` → e2 (`test_rule_not_seen_shallow_and_no_git`, exact no-git INCOMPLETE).
- M3: the committed check dropped from `_unsure` → T-a5.
- M4: the TESTS gate moves I2 without the I2_BEFORE `all(...)` → T-a3.
- M5: `or unchecked` removed from the exit → T-a (exit 1). I2 makes sure T-a's shallow run has no other exit-1 source; if it has one, I2 uses a fixture where INCOMPLETE is none and the only exit-1 cause is NOT CHECKED, and records which in 05.
- M6: fold removed → T-b.
- M7: fold on `unrelated` without `shallow` → `test_unrelated_branch_with_work_is_branch_error` (full-clone 081).
- M8: `held` None treated as 0 (folded, no own error) → T-b2.
- M11 (090): `shallow = False` in `main()` → T18 still fails.

Checks in 05 (step 5): the `RI-014:` line; the M11 re-run result; the real counts on a `--depth 1 --no-single-branch` clone of this repo (items moved to NOT CHECKED, refs folded, k); and a whole-output diff of the old and new script on a full clone, which must be empty.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Step 1: `unchecked` list in `incomplete()`, keyed on `env == SHALLOW_TEXT` | File 1 `_unsure`, `incomplete(... unchecked, committed)`; T-a, T-a2; M1, M2 |
| Step 1: gates that move (TIMED, LOG BATCH, SUITE, ROUND_HEADING 05+06, VERDICT always; TESTS only when all I2 pass I2_BEFORE) | File 1 gate list; T-a3 (TESTS exact), T-a6; M4 |
| Step 1: only I2 moves out of the format entry | File 1; T-a4 |
| Step 1: `INCOMPLETE NOT CHECKED:` line only when shallow; `none` when empty | File 1 `main()`; T-a (absent after unshallow), `test_non_utf8_shallow_line_no_traceback` |
| Step 1: exit 1 for a non-empty list | File 1 `or unchecked`; M5 |
| Step 1: no-git / unborn unchanged (03 #44 correction) | `_unsure` equality; e2 kept; M2 |
| Step 1 / 03 #43 (uncommitted file also gives `(None, "")`) | C1: `committed` set via `_head_work_files()`; T-a5; M3 |
| Step 2: `held` key on the unrelated dict | File 1 `open_branches()`; T-b2 |
| Step 2: one folded sub-line, names kept, age dropped | File 1 `main()` fold; T-b, T18, T19; M6 |
| Step 2: one summary BRANCH ERROR when k ≥ 1; `held` None keeps its own | File 1 `branch_errors`; T-b, T-b2; M8 |
| Step 2: fold only when shallow; full clone, scanned refs, str path untouched | File 1; T-b full-clone half; M7; step 5 diff |
| Step 2: M11 still fails T18 | T18 edit keeps LOG TIME/MAIN AHEAD asserts; M11 |
| Step 3: docstrings | File 1 docstring bullets |
| Step 4: one sentence byte-identical in 3 files + `UNSHALLOW` constant | Files 3-5, file 2 constant; `test_unshallow_sentence_same_in_three_files` |
| Step 4: "If 094 lands first, merge its single-branch sentence into the same edit" | DROPPED: 094's plan keeps its sentence separate with its own count test and never edits UNSHALLOW (C2); merging would break 094's `test_single_branch_sentence_same_in_three_files` |
| Step 5: RI-014 line, M11 re-run, real depth-1 counts, full-clone diff | Tests and checks, "Checks in 05" |
| Missing inputs: shallow file unreadable → shallow path | `test_non_utf8_shallow_line_no_traceback` new assertion |
| Missing inputs: rule-seen anchor not computable | T-a (kept with label, exit 1, never dropped) |
| Missing inputs: own I2 lines unreadable | unchanged 089 path; existing 089 tests (gate not reached) |
| Missing inputs: ls-tree of shallow ref fails → `held` None | T-b2 |
| Missing inputs: merge-base exit not 0/1 | unchanged; existing 081 tests |
| Missing inputs: folded ref's age dropped | by design; T-b asserts names only |
| Removed #9 / #49 (boundary-commit derivation) | DROPPED: removed by R3, no plan line depends on it |
| 03 #50 finer boundary test via `_shallow_boundaries` | DROPPED: follow-up, kept as known gap in docstring |

## Guardrail tests
- Feasibility: gated-entry selector (step 1). 03 gives 1 item (083), 2 of 2 entries, from four A1 full-clone runs dated 2026-11-20..22. T-a pins 150 with 2 entries, and T-a2 does the same on a real depth-1 clone. I2 records the real-tree count in 05.
- Feasibility: shallow unrelated-ref fold (step 2). 03 gives 28 of 28 refs fold and 28 held (A1 d1 probe, 2026-11-22): 56 lines become 2. T-b pins 3 of 3 folded and 3 of 3 held. T18 pins 1 of 1 and 1 held. T19 pins 1 of 1 and 0 held, which gives 0 BRANCH ERROR and exit 0.
- Missing inputs: shallow file unreadable → `test_non_utf8_shallow_line_no_traceback` (NOT CHECKED line present).
- Missing inputs: rule anchor not computable in shallow → T-a (label, exit 1).
- Missing inputs: HEAD tree read fails (`committed` None) → T-a6 (`_head_work_files` → None, entries stay not checked).
- Missing inputs: ls-tree of a shallow unrelated ref fails → T-b2 (own BRANCH ERROR, never folded as 0).
- Missing inputs: own I2 lines unreadable → existing 089 log-unreadable tests (unchanged text).

## Expected result
- Shallow clone of this repo (both `--depth 1` single-branch, which 094 gives as OPEN BRANCHES single-branch not checked, and `--no-single-branch`): `INCOMPLETE:` no longer lists 083. `INCOMPLETE NOT CHECKED: 083 (<2 entries>); rule seen not checked (shallow clone; run git fetch --unshallow; item 095)`. Exit stays 1.
- `--no-single-branch` depth 1: one `  shallow clone: 28 ref(s) with no merge base not checked (...)` line and one `BRANCH ERROR: shallow clone; 28 of 28 ...` line, instead of 56 lines. Exit stays 1. These are 03's counts; I2 re-derives them on today's tree.
- Full clone: whole output byte-identical to before (no new line, no extra git call).
- Suite green with the new and edited tests, and every mutation M1-M8 and M11 fails its named test.
- Rule text in the 3 files names INCOMPLETE NOT CHECKED and the folded line as "not checked", items 079, 084, 090, 095.

Recurring issues checked (item 013):
- RI-001 (ESCALATED): both selectors have dated, non-zero counts (1 item / 2 entries; 28 of 28 refs), and fixture tests pin them (T-a, T-a2, T-b, T18, T19). Each has a stated empty result.
- RI-010 (ESCALATED): no log line is typed here; the last line is for the orchestrator. No step duty is changed. The rule sentence is pinned by a test.
- RI-014 (OPEN): this item. M11 still fails T18, and the full-clone diff must be empty.
- Also checked (GUARDED):
  - RI-002: an unknown anchor, a failed HEAD tree read or a failed ls-tree is never a pass, 0 or none, and the exit stays 1.
  - RI-012: equality on env, and the `held` key, never error text.
  - RI-004/RI-005: the 56 → 2 and 3-of-3 counts were re-derived from the fold rule.
  - RI-006: no hand totals here.
  - RI-009: folded refs keep their names, and 094's single-branch path is unchanged.

Log fields: FIT WITH CHANGES | 5 files planned
