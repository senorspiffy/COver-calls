# 04 Build plan - 079
Fit verdict: FIT WITH CHANGES

Fit: tooling only (scripts/check_pipeline.py, its tests, two command files). No trade, price, cap or strategy rule changes, so the ~$3k account and 001 rules are untouched. It does not conflict with 076 (LOG_FORMAT / `write_log`), 077 (strip helper, `BRANCH FAIL:`, `UNCOMMITTED STEP:`, which by 077/02 H7 must not call `_walk`) or 078 (probe anchors in `_is_code`, `open_branches`; none are edited here). Build on top of 077's code and find every place by function name or quoted text, never by line number. The changes from 03 are:
- C1 (missed by R3): an existing test pins the behaviour that step 4 removes. `test_failed_diff_tree_is_an_entry_not_none` (tests/test_pipeline_check.py) ends with `assert cp.research_code(cutoff, walked)[0] == "none"` for a `(sha, None)` unit. Step 4 makes that "not checked (see UNTRACKED CHANGE)". The assertion is changed, and this test becomes fixture (f). Its docstring says "062 does not report it twice", which is still true.
- C2: the walk result keeps its first two parts, so existing callers and hand-built tuples keep working: the 2-tuple in that test, and `test_t15_git_log_failure_fails`, which passes `cp._walk(cutoff)` to `real_data_field`. See the shape below.
- C3: S lines are checked. A line that is not 40 or 64 lowercase hex makes S "unreadable", so the result is not checked. (git itself dies with "bad shallow line", shallow.c, 03 row 23.)
- C4: what to expect. The below rule (step 3) is the common case on any shallow clone deep enough to hold the cutoff, not a rare one. In such clones the boundaries are usually older than the cutoff. So a real untracked change found in a shallow clone shows as "not checked (... below the cutoff; n unconfirmed entries ...)", exit 0. That fits the request ("same answer or not checked"), and the step 8 process line (unshallow first) is what keeps real entries loud. I3/A1 should know this.

## Extra research (with sources)
- SHA-256 repositories name objects with "64 hexadecimal digit SHA-256 name" (https://git-scm.com/docs/hash-function-transition). The same page lists shallow clones into SHA-256 repos as a non-goal, so a 64-hex shallow file is unlikely. Accepting 40 or 64 hex costs nothing, so S parsing takes both (C3). Anything else is unreadable, never skipped.
- Missed-commit and extra-commit completeness, re-derived from 03 Self-check row "none is exact". If no b in S is an ancestor of the cutoff (and S ∩ R = ∅), the shallow range equals the full range. An extra X needs a full-clone path C→X that crosses a cut edge b→p, and the first such b is an ancestor of C in the shallow view, so b is "below". So the step 3 test (some b ∈ S below the cutoff) is the exact condition for "entries may be extras". Nothing needs adding to 03's rule. Source: https://git-scm.com/docs/shallow ("pretend as if they are root commits").
- `git rev-parse --git-common-dir` prints `.git` (relative) in a main work tree and an absolute path in a linked worktree (https://git-scm.com/docs/git-rev-parse: relative paths are relative to cwd). `Path.cwd() / out` handles both, because joining an absolute path replaces the base.

## Files to create/change
1. scripts/check_pipeline.py
   - New `SHALLOW_LINE = re.compile(r"[0-9a-f]{40}([0-9a-f]{24})?")` next to `UNTRACKED_FROM`.
   - New `_shallow_boundaries()`, placed just before `_walk`. It returns `"full"`, `"unreadable"` or a list S (order of the file, no duplicates).
     - `r = _git("rev-parse", "--is-shallow-repository")`. If r is None, return "full". If `r[1] == 0` and the output is "false", return "full".
     - Otherwise run `d = _git("rev-parse", "--git-common-dir")`, take `path = Path.cwd() / d[0].strip() / "shallow"` and read it (utf-8).
     - Flag `sure = r[1] == 0 and r[0].strip() == "true"`. If d fails or the file is missing or unreadable (OSError), return "unreadable" when sure, else "full" (Missing inputs row 1).
     - Lines are stripped and empty lines dropped. Any line that fails `SHALLOW_LINE.fullmatch` gives "unreadable". The result is S (it may be empty).
     - Never use a literal `.git/shallow` or `--shallow-file`.
   - New `_note(cutoff)`: the existing `f" (cutoff {cutoff[:7]} from --untracked-from)" if cutoff != UNTRACKED_FROM else ""`. `_walk` and `untracked_changes` use it in place of their inline copies; the text does not change.
   - `_walk(cutoff)`: the docstring gains the third part. Keep the `known` / `--is-ancestor` block and its 053 text exactly as they are (anchor: `not in this shallow clone; run git fetch --unshallow`). After that block, and before the first-parent `rev-list`:
     - `S = _shallow_boundaries()`.
     - "unreadable" returns `(None, ("not checked (shallow clone; run git fetch --unshallow)" + note, False), None)`.
     - If S is a non-empty list: `all_ = _git("rev-list", f"{cutoff}..HEAD")`. A non-zero exit returns the existing `cutoff <c7>: git rev-list failed` + note, True. `inside = [c for c in all_[0].split() if c in set(S)]`. If inside is not empty, return `(None, (f"not checked (shallow boundary {inside[0][:7]}; run git fetch --unshallow)" + note, False), None)`.
     - Otherwise, for b in S: `m = _git("merge-base", "--is-ancestor", b, cutoff)`. Exit 0 sets `below = b` and breaks. Exit 1 continues. Any other exit returns `(None, (f"cutoff {cutoff[:7]}: git merge-base failed" + note, True), None)`.
     - The rest (first-parent rev-list, diff-tree loop) is unchanged. It ends `return units, None, below`, where below is None when the clone is full, S is empty or no boundary is below. Every early return gets a third part, `None`.
   - New `_parts(walked)`: `return walked[0], walked[1], (walked[2] if len(walked) > 2 else None)`. `untracked_changes` and `research_code` change `units, error = walked or _walk(cutoff)` to `units, error, below = _parts(walked or _walk(cutoff))`. `real_data_field` keeps `walked[1]` and takes `below = _parts(walked)[2]`.
   - New `_below_text(below, n, cutoff)`: `f"not checked (shallow boundary {below[:7]} below the cutoff; {n} unconfirmed entries; run git fetch --unshallow)" + _note(cutoff)`.
   - `untracked_changes`: after building `entries`. If `not entries`, keep `"none" + note, False`. If `below`, return `_below_text(below, len(entries), cutoff), False`. Otherwise the existing loud text.
   - `research_code`:
     - Replace `_research_code(files or [], request_text_of)` with `_research_code(files, ...)`.
     - Before the loop: `if any(files is None for _, files in units): return "not checked (see UNTRACKED CHANGE)", {}`.
     - After the loop: if `flagged and below`, return `_below_text(below, len(flagged), cutoff), {}`. The empty flagged dict means no SKIPPED from 062.
   - `real_data_field`: after the existing loop. If `names and below`, return `_below_text(below, len(names), cutoff), {}, False`. The empty entries dict means no INCOMPLETE from 070.
   - Module docstring: under UNTRACKED CHANGE, after the sentence "...when the cutoff is missing from a shallow clone (exit unchanged)", add: "Item 079 (RI-014): in a shallow clone (S = the lines of `<git rev-parse --git-common-dir>/shallow`), a boundary in `cutoff..HEAD` gives `not checked (shallow boundary <b7>; run git fetch --unshallow)`; a boundary that is an ancestor of the cutoff keeps none but turns entries into `not checked (shallow boundary <b7> below the cutoff; <n> unconfirmed entries; ...)`, exit unchanged; an unreadable shallow file gives `not checked (shallow clone; ...)`. A diff-tree failure on a commit not in S stays an entry (exit 1)." Under RESEARCH CODE, add "a failed diff-tree in the walk gives not checked (see UNTRACKED CHANGE), never none (079)". Under REAL-DATA FIELD, add "the 079 below-cutoff text replaces entries".
2. tests/test_pipeline_check.py: new helpers `_shallow(repo, *shas)` and `_graph(...)`, the 7 fixture tests below, the missing-input unit tests, and the C1 edit.
   - `_shallow(repo, *shas)` writes `"".join(s + "\n" for s in shas)` to `Path(repo) / <git rev-parse --git-common-dir run in repo>` / "shallow", then asserts that `--is-shallow-repository` prints "true".
   - `_graph(...)` uses `_history` (C = cutoff), `checkout -b`, `merge --no-ff --no-edit`. Non-code files go under `notes/`.
3. .claude/commands/daily-audit.md: the line that starts "First, A1 runs the Inbox step". After "It runs `python3 scripts/check_pipeline.py` and `python3 scripts/check_handoff.py --all`," insert the step 8 sentence as its own sentence just before "It runs". Additions only.
4. .claude/commands/run-item.md: the paragraph that starts "Fix branches never edit `logs/recurring-issues.md`". After "Before starting, run `python3 scripts/check_pipeline.py` after `git fetch origin`", put the step 8 sentence just before "Before starting" so it comes before the run. Additions only.

Step 8 sentence (both files, verbatim, with an item tag): "If `git rev-parse --is-shallow-repository` prints true, run `git fetch --unshallow`, then test again. If it is still true, report UNTRACKED CHANGE, RESEARCH CODE and REAL-DATA FIELD as 'not checked', never 'none' (item 079)."

## Tests and checks
Every test is `@NO_GIT`. Cutoff C is `_history`'s commit, and every run uses `--untracked-from C`, so note = ` (cutoff <C7> from --untracked-from)`. Each test prints `out` on assertion failure.
- (a) `test_shallow_boundary_inside_walk_not_checked`
  - Graph: C→P (notes/p.md)→B (notes/b.md) on main; side D (parent C, notes/d.md); M = merge(B, D) on main.
  - `_shallow(repo, B)`. Expected:
    - `UNTRACKED CHANGE: not checked (shallow boundary <B7>; run git fetch --unshallow)` + note
    - `RESEARCH CODE: not checked (see UNTRACKED CHANGE)`
    - `REAL-DATA FIELD: not checked (see UNTRACKED CHANGE)`
    - exit 0.
  - Control: delete the shallow file, run again → `UNTRACKED CHANGE: none` + note.
- (b) `test_shallow_boundary_on_second_parent_not_checked`
  - Graph: C→T (notes) on main; side C→Q→B2 (notes); M = merge(T, B2). `_shallow(repo, B2)`.
  - Expected: `UNTRACKED CHANGE: not checked (shallow boundary <B27>; ...)` + note, exit 0. This pins the whole-range check.
- (c1) `test_full_clone_same_graph_unchanged`: graph (a) with no shallow file → `UNTRACKED CHANGE: none` + note, exit 0. Same check as (a)'s control, but a separate test, so m1 cannot pass it.
- (c2) `test_unrelated_root_in_full_clone_stays_loud`
  - Graph: from C's main, `checkout --orphan u`, commit U (notes/u.md), then `merge --allow-unrelated-histories --no-edit main` gives M with first parent U. Check out M on main (`branch -f main` + checkout) so HEAD = M.
  - Expected: the line contains `<U7> (git diff-tree failed)`, exit 1, and `--is-shallow-repository` prints "false".
- (d) `test_shallow_boundary_below_cutoff_entries_unconfirmed`
  - Graph: Z root (notes/z.md) → Y (scripts/y.py) → b' (notes/b.md) → C (`_history`'s files, committed as the cutoff) → T (notes/t.md). M = `merge --no-ff` of T into a branch at Y, so the first parent is Y.
  - Build order: init; Z; Y; b'; then `_item` + config, commit C; T; `checkout -b m Y`; merge T; make that HEAD.
  - `_shallow(repo, b')`. Expected: `UNTRACKED CHANGE: not checked (shallow boundary <b'7> below the cutoff; 2 unconfirmed entries; run git fetch --unshallow)` + note, exit 0. Also `RESEARCH CODE: not checked (see UNTRACKED CHANGE)`, because Z's diff is None (step 4).
  - Control in the same test: remove the shallow file → `UNTRACKED CHANGE: none` + note (the full answer).
- (e) `test_shallow_boundary_in_linked_worktree`
  - Graph (a) plus `_shallow(repo, B)`, then `git worktree add --detach <tmp>/wt M`. Run `check_pipeline.py` with cwd = wt.
  - Expected: the same UNTRACKED CHANGE text as (a), exit 0. Assert first that `<wt>/.git` is a file.
- (f) `test_failed_diff_tree_is_an_entry_not_none` (existing, C1): its last assertion becomes `== "not checked (see UNTRACKED CHANGE)"`. The untracked assertions stay. Add `assert cp.research_code(cutoff, ([("ab"*20, ["ccbot/x.py"])], None))[0] == "none"`, which shows a 2-tuple still works (C2).
- Missing-input unit tests: see Guardrail tests.
- Unchanged and must pass: `test_cutoff_missing_in_shallow_clone_not_checked`, `test_t14_unusable_cutoff_is_not_checked`, `test_t15_git_log_failure_fails`, and the whole of `tests/test_pipeline_check.py` and `tests/test_real_data_field.py`.
- Full suite: `python3 -m pytest -q`. Also `python3.11 -m py_compile scripts/check_pipeline.py` (RI-008). Run `python3 scripts/check_pipeline.py` on the repo; this clone is full (03 row 32), so the expected result is unchanged.
- Mutations for I3, on a scratch copy only:
  - m1: drop the `inside` return → (a), (b), (e) fail (`(git diff-tree failed)`, exit 1).
  - m2: read `Path(".git/shallow")` → (e) fails.
  - m3: drop the `below` returns → (d) fails (2 entries, exit 1).
  - m4: restore `files or []` and remove the None guard → (f) fails.
  - m5 (new): in `_shallow_boundaries`, treat the "unreadable" state as "full" → `test_shallow_file_unreadable_not_checked` fails.
- Process check: `grep -c "fetch --unshallow" .claude/commands/daily-audit.md .claude/commands/run-item.md` gives at least 1 each, and `git diff` shows additions only in both files.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Step 1 `_shallow_boundaries` via `--git-common-dir`, never `.git/shallow` / `--shallow-file` | Files 1, `_shallow_boundaries`; tests (e), m2 |
| Step 2 inside boundary (S ∩ R) → not checked, 053 text unchanged, non-S diff-tree failure stays loud | Files 1, `_walk` `inside`; tests (a), (b), (c1), (c2), m1; 053 test unchanged |
| Step 3 below rule, "none" exact, entries → unconfirmed text, flagged {} | Files 1, `_walk` `below`, `_below_text`, the three users; test (d), m3 |
| Step 3 merge-base exit not 0/1 → loud | Files 1, `_walk`; `test_merge_base_failure_is_loud` |
| Step 4 research_code: None never `[]` | Files 1, `research_code`; test (f) (C1), m4 |
| Step 5 REAL-DATA FIELD through `walked`, below rule on its entries | Files 1, `real_data_field`; (a) asserts its not-checked line. Below with ≥ 1 real-data entry: `test_below_rule_real_data_entries` (unit, monkeypatched `_item_triggers` with one entry, walked = ([], None, B)) → `_below_text(..., 1, ...)`, entries {} |
| Step 6 fixtures (a)-(f) | Tests and checks (a)-(f) |
| Step 7 mutations m1-m4 | Tests and checks, mutations (plus m5) |
| Step 8 process line in daily-audit.md and run-item.md | Files 3, 4 |
| Step 9 RI-014 guardrail status line in 05/06 | I2 and I3 copy it into 05/06: "RI-014: guardrail built (079); GUARDED when 079 is merged and m1 fails fixture (a) on main" |
| Missing inputs table (8 rows) | Guardrail tests, Missing inputs |
| Removed claims / follow-up (log.showRoot=false real root) | DROPPED: out of scope per 03; A1 may open an item |
| Person-followed rules (001) | None changed; no 001 text update needed |

## Guardrail tests
- Feasibility, step 2 inside: (a) S ∩ R = {B} (1 of 1), (b) {B2} (1 of 1) → tests (a), (b) pin the exact text. These are fixture counts made by hand in 03 Self-check, dated 2026-11-19; the tests re-run them.
- Feasibility, step 3 below: (d) S ∩ R = 0 of 1, below = 1 of 1, n = 2 → test (d) pins "2 unconfirmed entries". Full view → none (control in the same test).
- Feasibility, step 1 worktree: (e) S = {B}, 1 of 1 → test (e).
- Missing inputs (unit tests with `monkeypatch.chdir(repo)` and a wrapped `cp._git`, as in `test_t15_git_log_failure_fails`):
  - `--is-shallow-repository` unknown (returns ("", 129)), no file → `test_shallow_flag_unknown_no_file_is_full`: `_shallow_boundaries() == "full"`. With a file holding B → `== [B]`.
  - Shallow file missing or unreadable while the flag is true → `test_shallow_file_unreadable_not_checked`: the flag is patched to "true" with no file → `_walk` error text `not checked (shallow clone; run git fetch --unshallow)` + note, failed False. A malformed line "zz" in the file gives the same text (C3).
  - Shallow file empty → `test_empty_shallow_file_is_today_path`: `_shallow` writes "" with the flag patched to "true" → `_shallow_boundaries() == []` and `untracked_changes` gives today's `none`.
  - rev-list R fails → `test_shallow_rev_list_failure_is_loud`: patch `("rev-list", <c>..HEAD)` without `--first-parent` to exit 128 → `cutoff <c7>: git rev-list failed` + note, True.
  - merge-base fails → `test_merge_base_failure_is_loud`: on graph (d) with the shallow file, patch `merge-base --is-ancestor <b'> <C>` to 128 → `cutoff <C7>: git merge-base failed` + note, True; exit 1 through `untracked_changes`.
  - diff-tree fails on a commit not in S → (c2) (loud) and (f) (RESEARCH CODE not checked).
  - Commits hidden behind an inside boundary → (a): P is hidden, and the line is not checked, never none.
  - Unconfirmed entries below the cutoff → (d).

Recurring issues checked (logs/recurring-issues.md):
- RI-001 (ESCALATED): every rule test pins a computed per-fixture count (above); nothing is asserted as "always".
- RI-014 (OPEN, this item): steps 2-9 are planned, with m1-m5.
- RI-002 (GUARDED): no uncomputable value becomes "none", an error or a pass. The None diff is fixed (C1, step 4), and an unreadable or malformed S is not checked (C3).
- RI-007 (GUARDED): the UNTRACKED CHANGE loud path is kept for full clones (c2), and step 8 keeps real entries loud by unshallowing first (C4).
- RI-008: py_compile on 3.11 is planned.
- RI-010: each new text duty (step 8) is backed by a grep check; the log line goes through `--log`.
- RI-012: boundary membership is a set test on full shas, never a substring; S lines use `fullmatch`.
- RI-006: no counts are typed by hand in this plan beyond the 03 fixture counts, which the tests re-run.
- RI-009/RI-011: 079 builds on 077's branch state (brief); nothing changes in `open_branches`.

## Expected result
- On a shallow clone with a boundary in `cutoff..HEAD`: UNTRACKED CHANGE gives `not checked (shallow boundary <b7>; run git fetch --unshallow)`, and RESEARCH CODE and REAL-DATA FIELD give `not checked (see UNTRACKED CHANGE)`, exit 0.
- With only a boundary below the cutoff: "none" stays "none", and entries become the "unconfirmed entries" text, exit 0.
- Full clones keep today's output exactly, a real root in the range included (exit 1).
- The 2026-11-19 audit case (a15129c inside the range) gives not checked instead of a false entry.
- About 13 new or changed tests in tests/test_pipeline_check.py; all suites pass.
- The two command files gain the unshallow sentence.
- 4 files changed: scripts/check_pipeline.py, tests/test_pipeline_check.py, .claude/commands/daily-audit.md, .claude/commands/run-item.md.

Log fields: FIT WITH CHANGES | 4 files planned
