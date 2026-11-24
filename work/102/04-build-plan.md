# 04 Build plan - 102
Fit verdict: FIT WITH CHANGES

Scope: Parts 1 and 2 only. Part 3 (the i1-reviewer sentence, RULE_PATHS) is out of scope and waits for the person (03 Residual b). No file under `.claude/`, `scripts/`, `templates/` or `config/` changes.

Fit check: this is test-only pipeline work. It does not touch the bot, the screen or any rule the person follows (001), so the ~$3k account and the strategy rules are not affected. It does not conflict with built code. The tests only read `scripts/commit_step.py` and `scripts/check_pipeline.py`. There is one ordering conflict: 099, 100, 101 and 103 each plan edits to `tests/test_pipeline_check.py`, and 100 also edits `scripts/check_pipeline.py` (their 04s). Under run-item's item-091 rule ("items that change the same file are built (I2-I3) one after another, never in parallel"), 102's I2 starts only after those have been built and committed on this branch. I2 then re-reads every cited line number (03 step 6). New tests go at the end of the file, found by name, so they never land inside another item's block.

Changes to 03 (why this is FIT WITH CHANGES, not FIT):
- C1 (step 2, a bug in the plan text): `{p for p in os.walk(...)}` cannot run. os.walk yields `(dirpath, dirnames, filenames)` tuples that hold lists, which are unhashable. Use the helper below.
- C2 (03 Missing inputs, `.git/objects` row, WRONG): by default os.walk ignores scandir errors. It does not raise them, so an unreadable objects dir gives two empty sets, they compare equal, and the test passes silently (the RI-002 shape). The helper passes `onerror` that re-raises, and the test asserts that the "before" set is not empty.
- C3 (step 1): add `import types` to tests/test_commit_step.py. Wrap the `cs.main` call so that GitCalled becomes `pytest.fail("git called before trailer refusal: <cmd>")`. The 05 output then names the cause instead of a bare traceback. This makes no change to which rows pass or fail.
- C4 (step 3, CHECKLIST rows): the tmp root holds only `_item(..., logged=False)`, so `logs/` is absent. Traced: `_log_text` returns `("", [])` when the folders are absent (check_pipeline L832-845), so the entry is still `no log line for R1 R2 R3 I1 I2 I3`. Even so, the rows create an empty `logs/implementation/` dir. That keeps them independent of how main() treats a missing logs dir, and it changes no expected text.
- C5 (step 5): every mutant is applied in a scratch copy of the repo (the i3 "scratch copy, never in the repo" rule, RI-009 occurrence 2), never by editing the tracked file.

Recurring issues checked (item 013), all open or ESCALATED entries: RI-001 (ESCALATED), RI-010 (ESCALATED), RI-014 (OPEN). GUARDED entries also checked: RI-002, RI-004, RI-005, RI-006, RI-007, RI-009, RI-012. Results:
- RI-001: every cutoff row has its boundary IDs, taken from 03's Feasibility column and Self-check rows 1-5. The Guardrail tests below pin each one.
- RI-002: C2 closes the silent empty-set pass. `calls == []` is an asserted value, not a default.
- RI-010: this item is the 098 near miss. The log line is written by `--log`, never typed by hand (see the end of this file).
- RI-014: no git call is added to scripts/. The fixtures are a fresh `git init` (commit_step) or have no git (check_pipeline, `_rule_seen` → `(None, "")`).
- RI-009: build order and line re-read (above).
- RI-012: the asserts match exact entries or stderr text, never a bare number.
- RI-004/005/006: the arithmetic below is re-derived, and the totals are left to check_handoff.
- RI-007: Scope FULL, and code changes are allowed.

## Extra research (with sources)
1. os.walk ignores errors by default. Its `onerror=None` means errors from the scandir/listdir call are ignored; a callable gets the OSError and may re-raise it. This is the basis for C2. Sources: https://docs.python.org/3/library/os.html#os.walk (the page fetch was truncated before the os.walk entry; the behavior is confirmed by the docs issue that quotes it, "errors from the listdir() call are ignored", https://mail.python.org/pipermail/docs/2018-April/035020.html) and https://mail.python.org/pipermail/python-dev/2003-May/035574.html ("os.walk() silently ignores errors").
2. os.walk yields a 3-tuple `(dirpath, dirnames, filenames)` whose two last members are lists. A set of those tuples raises TypeError (unhashable), which is the basis for C1. Same doc URL.
3. Rebinding `cs.subprocess` (not `subprocess.run`) affects only commit_step's global lookup, so pytest's own subprocess use and the test's `_g` stay real. 03 verified this (Python execution model, FOR 1). I re-checked commit_step.py: `subprocess` appears only at L45 (import) and L64 (`run`), and `run` catches only FileNotFoundError (L65), so GitCalled is never swallowed.
4. Simpler method considered: a mutation tool (mutmut) instead of hand mutants. Rejected. It would add a dependency and it mutates every operator, while this item needs 15 specific mutants (1 + 7 × 2). 03 Residual (a) keeps per-site operator mutants as a follow-up.
5. An edge case R3 left implicit: under M1 the 5 kill rows reach rev-parse at L161 through the module `run`, and the recorder raises there. In T-b (child process, real git) the same mutant writes a blob for R05 "05\n", the filtered log blob and ≥ 1 tree, and leaves HEAD and `.git/index` as they were (temp index L196-210). Only the objects-set compare (step 2) sees it. Traced, not run.

## Files to create/change
1. `tests/test_commit_step.py`
   - `import types` (C3).
   - Module constant `TB_ROWS` holding the 6 `(args, why)` pairs, plus `TB_IDS = ["key-space", "no-colon-space", "empty-value", "lf", "cr", "no-value"]`. `test_trailer_refusals_write_nothing` is parametrized over them with no behavior change.
   - Helper:
     ```python
     def _objects(r):
         """Relative paths of every file under .git/objects; a walk error raises (C2)."""
         top = r / ".git" / "objects"
         def _raise(e):
             raise e
         return {os.path.relpath(os.path.join(d, f), top)
                 for d, _, fs in os.walk(top, onerror=_raise) for f in fs}
     ```
   - T-b (step 2): `objs = _objects(repo)`, `assert objs` (the root commit has ≥ 4 objects: 2 blobs, ≥ 2 trees, 1 commit), and after `_cli`, `assert _objects(repo) == objs`.
   - New `test_trailer_refusals_make_no_git_call(repo, monkeypatch, capsys, args, why)` over TB_ROWS/TB_IDS (step 1). It contains a local `class GitCalled(Exception)` (not an OSError) and `rec` (append, then raise). It runs `monkeypatch.setattr(cs, "subprocess", types.SimpleNamespace(run=rec))`, then `try: code = cs.main(list(args)) except GitCalled as e: pytest.fail(...)`. It asserts `code == 2`, `why in capsys.readouterr().err` and `calls == []`. The docstring names `no-value` as the guard row (refused in `main`, L235-238).
2. `tests/test_pipeline_check.py` (appended at the end of the file, after 099/100/101/103 are committed)
   - `FROM_ROWS` and the `test_from_cutoff_boundary(tmp_path, name, item, expect)` test: 10 rows with literal IDs and ids `<NAME>-FROM` / `<NAME>-FROM-1`, exactly as 03 step 3 describes. CHECKLIST 041/040 (plus an empty `logs/implementation/`, C4), LOG_CHECK 045/044, SUITE 087/086, VERDICT 071/070, TIMED 090/089 (with `_request` first). No value asserts in these rows.
   - `test_from_values()`: CHECKLIST 41, LOG_CHECK 45, TESTS_FORMAT 76, SUITE 87, TIMED 90, WHOLE_DIFF 70, VERDICT 71, read through `_cp()`.

Files planned: 2. There is no change to scripts/, templates/, config/ or .claude/.

## Tests and checks
- `python3 -m pytest -q tests/test_commit_step.py -k "trailer_refusals"` → 12 passed: 6 rows in T-b and 6 in the new test. Paste the line in 05.
- `python3 -m pytest -q tests/test_pipeline_check.py -k "from_cutoff_boundary or from_values"` → 11 passed.
- Full suite: base + 17 (6 + 10 + 1), with no other count changing.
- `python3.11 -m py_compile tests/test_commit_step.py tests/test_pipeline_check.py` exits 0 (RI-008).
- Mutations (05 table, re-run by I3), each in a scratch copy (C5). Run each one with `python3 -m pytest -q tests/test_commit_step.py tests/test_pipeline_check.py tests/test_real_data_field.py -k "not test_from_values and not test_timed_hint_fits_timed_format and not test_t7d"`:
  - M1: move the L159-160 loop to just before L211. Expected: the 5 `_trailer_ok` ids of the new test fail, the same 5 ids of T-b fail, and `no-value` passes in both.
  - S-CHECKLIST ±1, S-LOG_CHECK ±1, S-SUITE ±1, S-VERDICT ±1, S-TIMED ±1: each fails its named `test_from_cutoff_boundary` id.
  - S-TESTS_FORMAT +1/−1: `test_i2_tests_field_cutoff` fails.
  - S-WHOLE_DIFF +1: t7b/t7c fail. S-WHOLE_DIFF −1: t7 fails.
  - For each mutant, paste the pytest summary and the failing IDs. Under S-VERDICT 70, record whether test_real_data_field changes (03's open row 2.4; nothing relies on it). Any survivor sends the item back to I2.
- `python3 scripts/check_pipeline.py` on the branch: 102's own lines only. INCOMPLETE and LOG TIME show nothing new for 102.

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Scope note: Parts 1-2 only, Part 3 out of scope, tests/ only | Scope line; "Files planned: 2", no RULE_PATHS file |
| Step 1: TB_ROWS, recording-subprocess test, GitCalled, `calls == []`, no-value guard row | Files 1, bullets 2 and 5 (+ C3) |
| Step 2: objects-set compare in T-b | Files 1, bullets 3-4 (corrected by C1, C2) |
| Step 3: 10 literal-ID boundary rows, own tmp root, no value asserts | Files 2, bullet 1 (+ C4) |
| Step 4: one separate `test_from_values` (7 constants); existing `== 90` / `== 70` stay | Files 2, bullet 2 |
| Step 5: 15 mutants, `-k` deselect, paste summaries, 070 interaction recorded | Tests and checks, Mutations (+ C5) |
| Step 6: build order, re-read line numbers after rebase | Fit check paragraph (I2 runs after 099/100/101/103) |
| Fact-check correction 01 1.7 / 02 AGAINST 3b (no-value is a guard row) | Files 1, bullet 5 docstring; Mutations M1 expectation |
| Fact-check correction 02 FOR 1 / AGAINST 3c (recorder raises GitCalled, not FileNotFoundError or None) | Files 1, bullet 5 |
| Fact-check correction 01 2.10 TIMED (`_request` first, assert TIMED_HINT) | Files 2, bullet 1 (TIMED rows) |
| Fact-check correction 01 2.10 last line (value asserts moved out) | Files 2, bullet 2; `-k` deselect |
| Fact-check correction 01 2.3 CHECKLIST (041 on branch `next`) | DROPPED: no plan change. The new rows use their own tmp root |
| Fact-check 01 2.4 / 02 Holes (VERDICT 70 vs test_real_data_field) | Tests and checks: recorded in 05, nothing relies on it |
| 02 Holes: ROUND_HEADING/SCRATCH/ROUND_BUILD already pinned both ways | DROPPED: out of scope, already pinned (03 row 02 Holes) |
| TESTS_FORMAT_FROM, WHOLE_DIFF_FROM boundary rows | DROPPED: already pinned both ways by behavior tests (test_i2_tests_field_cutoff / test_old_i2_hint_fits_old_format; t7 / t7b / t7c). Only the value pin is added (Files 2, bullet 2) |
| Residual (a): per-site operator mutants (14 sites) | DROPPED: follow-up item; 05/06 must not call the cutoffs "fully pinned" |
| Residual (b): Part 3 | DROPPED: pending the person (RULE_PATHS) |
| Missing inputs: git binary | Existing `pytestmark = NO_GIT` (skip, never a pass) |
| Missing inputs: recorded calls none | Files 1, bullet 5 (`calls == []` asserted) |
| Missing inputs: `.git/objects` unreadable | Files 1, bullets 3-4: `onerror` re-raise + `assert objs` (C2; 03's row was wrong) |
| Missing inputs: `_rule_seen` anchor without git | Files 2, bullet 1: the rows assert the strict text |
| Missing inputs: REAL-DATA FIELD for 070 without git | Files 2, bullet 1: VERDICT-FROM-1 expects `INCOMPLETE: none` |
| Missing inputs: request.md for the --log rows | Files 2, bullet 1: TIMED-FROM asserts TIMED_HINT in stderr, not only exit 2 |
| Missing inputs: screen tickers n/a | DROPPED: no ticker screen in this item |
| 001 rule text a person follows | DROPPED: none changed (test-only item); no request needed |

## Guardrail tests
- Feasibility: CHECKLIST_FROM 41 → `test_from_cutoff_boundary[CHECKLIST-FROM]` (041 entry) and `[CHECKLIST-FROM-1]` (040 none). 1 of 2 boundary IDs is checked.
- Feasibility: LOG_CHECK_FROM 45 → `[LOG_CHECK-FROM]` (045) and `[LOG_CHECK-FROM-1]` (044).
- Feasibility: SUITE_FROM 87 → `[SUITE-FROM]` (087 exact entry) and `[SUITE-FROM-1]` (`INCOMPLETE: none`).
- Feasibility: VERDICT_FROM 71 → `[VERDICT-FROM]` (071) and `[VERDICT-FROM-1]` (070).
- Feasibility: TIMED_FROM 90 → `[TIMED-FROM]` (exit 2 + TIMED_HINT) and `[TIMED-FROM-1]` (exit 0).
- Feasibility: TESTS_FORMAT_FROM 76 → existing test_i2_tests_field_cutoff (076/075). WHOLE_DIFF_FROM 70 → existing t7 (069), t7b and t7c (070).
- Feasibility: all 7 values → `test_from_values`.
- Feasibility: trailer refusal before git → `test_trailer_refusals_make_no_git_call[key-space|no-colon-space|empty-value|lf|cr]` (5 kill rows) and T-b's objects compare (5 rows). `[no-value]` is the guard row.
- Missing inputs: `.git/objects` unreadable → `_objects` re-raises through `onerror`, and `assert objs` fails on an empty listing.
- Missing inputs: git missing → NO_GIT skip (reported as a skip).
- Missing inputs: request.md missing for --log → TIMED-FROM requires TIMED_HINT in stderr (a 047 refusal has no hint, so it fails the row).

## Expected result
- Real code: 17 new test ids pass, and T-b's 6 still pass with the objects compare. Full suite = base + 17.
- M1 kills 10 ids (5 new + 5 T-b). `no-value` passes in both under M1.
- The 14 shifts each fail ≥ 1 named behavior test with `test_from_values`, `test_timed_hint_fits_timed_format` and `test_t7d` deselected. 1 + 14 = 15 mutants, 0 survivors. The 6 shifts that survive today (CHECKLIST+1, LOG_CHECK+1, SUITE±1, VERDICT±1) are killed by the new rows.
- Arithmetic re-derived: 41≥41 T / 40≥41 F; 45≥45 T / 44≥45 F; 87≥87 T / 86≥87 F; 71≥71 T / 70≥71 F; 90≥90 T / 89≥90 F. For each constant, shift +1 makes the FROM row fail and shift −1 makes the FROM-1 row fail. 5 × 2 = 10 rows. With TESTS_FORMAT 2 and WHOLE_DIFF 2, that is 14 of 14 shifts.
- 05/06 say these cutoffs are pinned against shifts only, not against per-site operator mutants (Residual a).
- Log line: I1 has no shell in this run. The orchestrator must run `python3 scripts/check_pipeline.py --log I1 102 "FIT WITH CHANGES | 2 files planned"` (item 045). It is never typed by hand.

Log fields: FIT WITH CHANGES | 2 files planned
