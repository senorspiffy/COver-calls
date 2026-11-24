# 04 Build plan - 094
Fit verdict: FIT WITH CHANGES

I1 read the branch copy of .claude/agents/i1-reviewer.md, logs/recurring-issues.md, work/094/request.md and 03-handoff.md, work/095/03-handoff.md (overlap rows), work/092/04-build-plan.md and work/093/04-build-plan.md (build order), .git/config, scripts/check_pipeline.py (`_git`, `_git_ok`, `open_branches`, `next_id`, `main`, `SHALLOW_TEXT`), scripts/check_handoff.py (`_branch_with_handoff`, `check_all`), and these parts of tests/test_pipeline_check.py: `GIT_CENSUS`, `test_git_call_census`, `_patched_git`, every `setattr(cp, "_git", ...)` fake, `UNSHALLOW`, `_clone`, `test_open_branches_none_line`, `test_check_handoff_open_branches_states`, `test_open_branches_default_computes_shallow`, and the three plain `--depth 1` tests. I1 has no shell (item 072), so nothing was run.

Fit: the work is checker tooling only. It places no order and changes no strategy rule (001), so the ~$3k account is not affected. It fits the 081/090 pattern already built: a state that cannot be checked gets a "not checked" line, and a git failure is an error, never "none". It conflicts with nothing that is built. The 03 map is sound. The changes below fix anchors that have moved since R3 wrote it, and pin details that would otherwise make the build or a test go wrong.

Changes to 03 (binding for I2):
- C1. Anchors have shifted, so use names, not 03's line numbers. The three plain `--depth 1` tests (03's "L966, L1067, L2086") are `test_uncommitted_step_in_shallow_clone`, `test_cutoff_missing_in_shallow_clone_not_checked` and `test_inbox_shallow_clone_not_checked`. 03's "L4415 `_clone`" is `_clone` and "L4468" is `test_open_branches_default_computes_shallow`. "h1" is `test_open_branches_none_line`, "h2" is `test_check_handoff_open_branches_states` and "d3" is `test_main_ahead_exact_ref_only`. The exit test is the final `return 1 if skipped or ...` expression in `main()`, which holds `isinstance(branches, str)`. The print block is the `if isinstance(branches, str):` / `elif branches == []:` block after the MAIN AHEAD lines.
- C2. Census total: do not hard-code 49. In `test_git_call_census`, add `("fetch_coverage", "_git"): (2, "fetch read: exit 0 values, exit 1 -> url read, other -> 'git config failed' (081); url read: exit 1 = no origin, 0 = SINGLE_TEXT, other -> failed (094)")`. Then raise the `sum(seen.values())` literal by exactly 2 from whatever it is after 092, 093 and 096 are built (47 today, so 49 if nothing earlier changed it), and extend its comment with `+ 2 (094)`. fetch_coverage must call `_git` directly, not `_git_ok`, because exit 1 is an answer here (key absent) and not an error.
- C3. Every new clone in the fixtures uses a `file://` URL, as `_clone` and the three `--depth 1` tests already do. Per git-clone, a plain path "implies `--local`", which copies the refs directory, so the d1s and sb shapes would not be what they claim. The sb clone is `clone -q --single-branch file://...`. The d1s clone is `clone -q --depth 1 file://...`, with no `--no-single-branch`. Do not use `_clone`, because it forces `--no-single-branch`. The full clone may use `_clone` with no extra args, or a plain `clone -q file://...`.
- C4. fetch_coverage is called only after the branch read succeeds (`why is None`), in both `open_branches` and `next_id`. On "no git" (`_git` gives None for `branch -r`), both return as they do today and fetch_coverage is not called. This keeps the order shown in `test_all_git_fails_no_line_says_none` (`git branch failed (exit 128)` first).
- C5. Exit 1 from `git config` also means "section or key is invalid" (git-config, ret=1). Both keys are fixed constants, so for us exit 1 means only "absent". Say this in the fetch_coverage docstring, so a later edit that builds the key from input knows the exit-1 meaning changes.
- C6. A source repo whose HEAD is detached gives a single-branch clone with no remote-tracking branch (git-clone). That clone has either no fetch line (with a URL, which is S10) or a non-glob line (S3). Both are SINGLE_TEXT, so no new code is needed. Name it in the docstring as a covered shape.
- C7. A `^` line of any kind gives SINGLE_TEXT, even one that would hide no `claude/*` branch. That over-reports "not checked", which fails closed. This is deliberate, and the docstring says so.

## Extra research (with sources)
1. git-config exit codes: "The section or key is invalid (ret=1) ... the config file is invalid (ret=3) ... On success, the command returns the exit code 0." `get` "emits the last value" and with `--all` "emits all values" (https://git-scm.com/docs/git-config). So exit 1 is ambiguous in general but not for our constant keys (C5). A corrupt config (ret=3) falls into the `git config failed (exit 3)` path, and in practice `git branch` dies first. Multiple `remote.origin.url` values give exit 0 with `--get` (last value), which is still SINGLE_TEXT when no fetch key is set, as intended.
2. git-config `--includes`: on "when searching all config files". So `--get-all` sees fetch lines that come in through `[include]`, as `git fetch` does. No special case is needed.
3. git-clone `--single-branch`: "If the HEAD at the remote did not point at any branch when --single-branch clone was made, no remote-tracking branch is created" (https://git-scm.com/docs/git-clone). This is covered by S3/S10 (C6).
4. git-clone GIT URLS: a plain path and `file://` "are mostly equivalent, except the former implies --local option". `--local` copies "everything under objects and refs directories" (same page). This is why C3 requires `file://`, matching the existing tests.
5. Repo check: this checkout's .git/config has `fetch = +refs/heads/*:refs/remotes/origin/*` (S1). So the real-repo tests (`test_round_bound_on_repo_data` and the check_handoff `--all` run in 05/06) keep the full path, and `--next-id` keeps working here.
6. Fake audit (beyond 03's R1-25): every `setattr(cp, "_git", ...)` fake was checked. Only `test_open_branches_default_computes_shallow` reaches the new config read through a catch-all `("", 0)`. The all-128 fakes fail at `branch -r` first. The `("x", 0)` fakes in the 089 tests call `real_data_field` / `research_code`, not `open_branches`. `_patched_git` falls through to real git. The real-git tests clone with the default refspec, or have no origin at all (h1, d3, which go to "no origin").

## Files to create/change
1. scripts/check_pipeline.py
   - A new constant next to `SHALLOW_TEXT`: `SINGLE_TEXT = "single-branch clone; run git remote set-branches origin '*' && git fetch origin"`.
   - `GLOB_REFSPEC = "refs/heads/*:refs/remotes/origin/*"` (private constant, `_GLOB` is fine).
   - `fetch_coverage()`, placed before `open_branches`, implements 03 step 1 (a)-(e) exactly:
     - It returns one of "full", "no origin", "no git", SINGLE_TEXT, or `f"git config failed (exit {n})"`.
     - Full means: at least one non-empty value, after removing one leading `+` (`v[1:] if v.startswith("+") else v`), `== GLOB_REFSPEC`, and no value `startswith("^")`.
     - The docstring cites item 094 and C5, C6 and C7, and names the known gaps: full refspec never fetched, and other remotes.
   - `open_branches`: after the `why` checks on `branch -r` and before `today =`/`shallow =`, add `cov = fetch_coverage()`; `if cov == SINGLE_TEXT or cov.startswith("git config failed"): return cov`. Add one docstring sentence.
   - `next_id`: when `why is None`, add `cov = fetch_coverage()`, and if it is SINGLE_TEXT or a config failure, `return None, cov`. Add one docstring sentence.
   - `main()`, `--next-id` branch: `if why == SINGLE_TEXT:` prints `--next-id refused: {SINGLE_TEXT}; not counting open branches would risk an ID clash (item 037). Re-run after that.` to stderr. Other reasons keep today's text. Return 2 in both cases.
   - `main()`, print block: before `if isinstance(branches, str):`, add `if branches == SINGLE_TEXT: print(f"OPEN BRANCHES: not checked ({SINGLE_TEXT})")`, so the existing str branch becomes `elif`.
   - `main()`, exit expression: `isinstance(branches, str)` becomes `(isinstance(branches, str) and branches != SINGLE_TEXT)`.
   - The `unread` line stays as it is (any str gives `not checked (see OPEN BRANCHES)`).
   - All comparisons are `==` / `!=` / `startswith` on the constant's own prefix. No substring search of SINGLE_TEXT (RI-012).
   - Module docstring: add a sentence to the OPEN BRANCHES paragraph and the `--next-id` paragraph naming item 094, the exit choice (main unchanged, `--next-id` 2, check_handoff `--all` 1) and the known gaps.
2. scripts/check_handoff.py: docstring of `check_all` only. The single-branch state prints `not checked (open branches: <SINGLE_TEXT>)`, exit 1 (item 094). No code change. 092 has already put `cp.open_branches()` through `_pipeline()`, and the str path (`isinstance(found, str)`) already returns `(None, found)`.
3. tests/test_pipeline_check.py
   - `SINGLE_LINE = "OPEN BRANCHES: not checked (single-branch clone; run git remote set-branches origin '*' && git fetch origin)"` (a literal, not built from cp.SINGLE_TEXT, so an edit to the constant fails a test).
   - `SINGLE_SENTENCE` is the step 7 sentence, literal.
   - New tests are listed under Tests and checks.
   - `GIT_CENSUS` gets an entry and the total is bumped (C2).
   - `test_open_branches_default_computes_shallow`: the fake answers `("config", "--get-all", "remote.origin.fetch")` with `("+refs/heads/*:refs/remotes/origin/*\n", 0)`. Its other answers are unchanged, and it still asserts `== []`.
4. .claude/agents/a1-auditor.md: add the step 7 sentence right after the UNSHALLOW sentence, on the same line or as the next sentence. UNSHALLOW is not edited.
5. .claude/commands/run-item.md: same.
6. .claude/commands/daily-audit.md: same.

Build order: 092, 093 and 096 are already built on this branch before 094, and 095 comes after. 094 must not edit the UNSHALLOW sentence or the shallow logic of `open_branches`. 095 rebases its print-block change onto 094's new first `if`. Files 1, 2, 4, 5 and 6 are RULE_PATHS, so the person's OK is needed in PR review, and 05 says so.

## Tests and checks
New tests (each docstring names item 094):
- `test_single_branch_clone_not_checked` (@NO_GIT, real git; 03 step 8a with C3).
  - Source: a repo whose main holds work/091/request.md. A pushed branch `claude/probe-092` holds work/092/request.md.
  - Full clone: `git config --get-all remote.origin.fetch` stdout == `+refs/heads/*:refs/remotes/origin/*\n`. `--next-id` gives `(0, "093\n")`. The OPEN BRANCHES block lists `origin/claude/probe-092`.
  - sb, d1s and d1s after `git fetch --unshallow`:
    - `_pick(out, "OPEN BRANCHES:") == SINGLE_LINE`.
    - `IN PR:`, `RULES BRANCH:` and `ID CLASH:` each `not checked (see OPEN BRANCHES)`.
    - No `BRANCH ERROR` line, and exit 0.
    - `--next-id`: exit 2, stdout "", and stderr starts `--next-id refused: single-branch clone;`.
  - Recovery in sb: `git remote set-branches origin *` (list args, no shell) and `git fetch -q origin`. `--get-all` is then exactly one glob line, and `--next-id` gives `093`.
- `test_fetch_coverage_shapes` (@NO_GIT, parametrized over S1, S2, S3, S4a, S4b, S5, S6, S7, S9, S10; ids are the S names).
  - Each case starts from a full `file://` clone and builds its shape with `git config --unset-all remote.origin.fetch`, `git config --add ...` and, for S9, `--unset remote.origin.url`.
  - It asserts `cp.fetch_coverage()` (with `monkeypatch.chdir`) per the 03 Self-check table.
  - S5 also runs the recovery and asserts one glob line.
- `test_fetch_coverage_fakes`: `_patched_git` gives `("", 0)` for S8, `("++refs/heads/*:refs/remotes/origin/*\n", 0)` for S11 and `("", 128)` for S12. The results are SINGLE_TEXT, SINGLE_TEXT and `git config failed (exit 128)`.
- `test_config_failure_end_to_end`: in a real full clone, `_patched_git` gives `("", 128)` for the fetch read.
  - `cp.main([...])` returns 1 and prints `OPEN BRANCHES: git config failed (exit 128) (item 081)`.
  - `cp.main(["--next-id"])` returns 2 with stderr `--next-id refused: git config failed (exit 128); ... Fix the clone (git fetch origin) and re-run.` (today's tail).
- `test_check_handoff_single_branch` (03 step 8e): in the sb clone from a shared fixture helper (or monkeypatch `open_branches` to return `cp.SINGLE_TEXT`, plus one real-clone run), `check_handoff.check_all` on a work/ with an item that has no 03 gives exit 1 and prints `150: not checked (open branches: single-branch clone; run git remote set-branches origin '*' && git fetch origin)`.
- `test_single_branch_sentence_same_in_three_files`: `count(SINGLE_SENTENCE) == 1` in each of the three rule files, and the sentence follows UNSHALLOW (`text.index(UNSHALLOW) < text.index(SINGLE_SENTENCE)`).
- `test_check_pipeline_docstring_names_094`: `"(item 094)"` is in `cp.__doc__`, `cp.fetch_coverage.__doc__`, `cp.open_branches.__doc__` and `cp.next_id.__doc__`.

Existing tests that must pass unchanged (they act as detectors): the three plain `--depth 1` tests (C1, `code == 0`), h1, h2, d3, `test_all_git_fails_no_line_says_none`, `test_unshallow_sentence_same_in_three_files`, `test_shallow_three_readers_not_checked`, `test_shallow_docs_only_orphan_exit_0`, and the `--next-id` tests (041/042/058/100/151). The only edits allowed are the census (C2) and `test_open_branches_default_computes_shallow` (fake answer).

Checks for I2 and I3:
- The full suite is green.
- `python3.11 -m py_compile scripts/check_pipeline.py scripts/check_handoff.py tests/test_pipeline_check.py` (RI-008).
- `python3 scripts/check_pipeline.py` on this branch: the OPEN BRANCHES output is the same as before the change (full refspec here).
- `python3 scripts/check_pipeline.py --next-id`: an ID, exit 0.
- `python3 scripts/check_handoff.py --all`: no new FAIL.
- The mutations m1-m6 from 03 step 9. Each must fail the named test, and 06 gives the failed/passed counts. m4's detectors are the three `--depth 1` tests by name plus `test_single_branch_clone_not_checked`.
- Add m7: remove the `branches == SINGLE_TEXT` print branch (the str falls to the 081 line). This must fail `test_single_branch_clone_not_checked` (wrong line text).

## Rule trace
| 03 rule (map step or correction section) | Plan line, or DROPPED: <reason> |
|---|---|
| Exit-code decision: main exit unchanged by the single-branch state | Files 1, exit expression; three `--depth 1` tests stay `code == 0`; m4 |
| Exit-code decision: `--next-id` exit 2 | Files 1 `--next-id` branch; test_single_branch_clone_not_checked; m6 |
| Exit-code decision: check_handoff `--all` exit 1 | Files 2 (docstring only); test_check_handoff_single_branch; h2 unchanged |
| Exit-code decision: failed `git config` is the 081 path (main 1, `--next-id` 2) | test_config_failure_end_to_end; test_fetch_coverage_fakes[S12] |
| Step 1 SINGLE_TEXT constant and fetch_coverage (a)-(e) | Files 1 fetch_coverage; test_fetch_coverage_shapes; test_fetch_coverage_fakes; C2, C5, C6, C7 |
| Step 2 open_branches: coverage after the branch read, before the shallow logic | Files 1 open_branches; C4; test_all_git_fails_no_line_says_none unchanged |
| Step 3 next_id: coverage after a successful branch read | Files 1 next_id; C4; m6 |
| Step 4a print `OPEN BRANCHES: not checked (SINGLE_TEXT)` | Files 1 print block; SINGLE_LINE literal; m7 |
| Step 4b exit test `and branches != SINGLE_TEXT` | Files 1 exit expression; m4 |
| Step 4c IN PR / RULES BRANCH / ID CLASH via `unread`, no new code | Files 1 (unchanged `unread`); asserted in test_single_branch_clone_not_checked |
| Step 4d `--next-id` stderr text for SINGLE_TEXT; other reasons unchanged; `==` only | Files 1 `--next-id` branch; test_single_branch_clone_not_checked; test_config_failure_end_to_end |
| Step 5 check_handoff: no code change, docstring | Files 2 |
| Step 6 docstrings name item 094, exit choice, known gaps | Files 1 docstrings; test_check_pipeline_docstring_names_094 |
| Step 7 rule sentence after UNSHALLOW in three files; UNSHALLOW unedited | Files 4-6; test_single_branch_sentence_same_in_three_files; test_unshallow_sentence_same_in_three_files |
| Step 8a real-clone fixture (full, sb, d1s, d1s+unshallow, recovery) | test_single_branch_clone_not_checked with C3 (`file://`) |
| Step 8b real `git config` shapes S1-S7, S9, S10 | test_fetch_coverage_shapes |
| Step 8c S8, S11, S12 fakes | test_fetch_coverage_fakes |
| Step 8d S12 end to end | test_config_failure_end_to_end |
| Step 8e check_handoff in sb | test_check_handoff_single_branch |
| Step 8f census 47 → 49 | C2: +2 over the post-092/093/096 total (49 if unchanged) |
| Step 8g fake in L4468 test answers the glob | Files 3, test_open_branches_default_computes_shallow |
| Step 8h docstring/sentence pins | test_check_pipeline_docstring_names_094; test_single_branch_sentence_same_in_three_files |
| Step 9 mutations m1-m6 | Tests and checks (I3); plus m7 |
| Missing input: no fetch key, no URL → "no origin", today's path | test_fetch_coverage_shapes[S9]; h1, d3 unchanged |
| Missing input: no fetch key, URL present → SINGLE_TEXT | test_fetch_coverage_shapes[S10]; m5 |
| Missing input: exit 0, no value → SINGLE_TEXT | test_fetch_coverage_fakes[S8] |
| Missing input: git config exit other than 0/1 → 081 error | test_fetch_coverage_fakes[S12]; test_config_failure_end_to_end |
| Missing input: `_git` None → "no git", unchanged | C4; existing no-git tests (h1's "without git there is no line") |
| Missing input: full refspec never fetched | DROPPED: known gap, not computable offline (would need ls-remote, R2 AGAINST 2); written in the docstrings; the rule files already require `git fetch origin` first |
| Missing input: other remotes (`upstream/*`) | DROPPED: known gap, origin-only as MAIN is today; written in the docstrings |
| Implementation map, build order: on top of 092/093/096; 095 after; RULE_PATHS need the person's OK | Files, Build order paragraph; 05 says it |
| Removed claim R2-24 (ls-remote `--branches` on 2.43) | DROPPED: removed in 03; ls-remote not used |

No 001 rule (slack, tolerance, cap) is changed, so no strategy-text update is needed. The rule-file sentence (step 7) is the "rule the person follows" for this item, and it is updated in the same plan.

## Guardrail tests
- Feasibility: fetch_coverage "full" holds for 4 of 12 shapes (S1, S2, S4a, S4b; 03 Self-check, dated 2026-11-24). test_fetch_coverage_shapes and test_fetch_coverage_fakes pin all 12, with S1 the shape `git clone` writes (and this repo's .git/config).
- Feasibility: the exit rule keeps 3 of 3 plain `--depth 1` tests at `code == 0` (`test_uncommitted_step_in_shallow_clone`, `test_cutoff_missing_in_shallow_clone_not_checked`, `test_inbox_shallow_clone_not_checked`). m4 must fail all three.
- Feasibility: the F2 example (full 093, single-branch 092 = clash) is pinned by test_single_branch_clone_not_checked (full `093`, sb refuses, recovery `093`).
- Missing inputs: `remote.origin.fetch` absent and URL absent → test_fetch_coverage_shapes[S9].
- Missing inputs: `remote.origin.fetch` absent and URL present → test_fetch_coverage_shapes[S10].
- Missing inputs: exit 0 with no value → test_fetch_coverage_fakes[S8].
- Missing inputs: config exit 128 → test_fetch_coverage_fakes[S12] and test_config_failure_end_to_end.
- Missing inputs: git absent → the existing no-git paths (h1 no-git half, `next_id` HEAD-only), unchanged by C4.

## Expected result
- In a single-branch clone (`--single-branch`, plain `--depth 1`, or either one after `--unshallow`), `check_pipeline.py` prints `OPEN BRANCHES: not checked (single-branch clone; run git remote set-branches origin '*' && git fetch origin)`. IN PR, RULES BRANCH and ID CLASH each print `not checked (see OPEN BRANCHES)`, and the exit code is unchanged.
- In that clone, `--next-id` refuses with exit 2 and prints nothing on stdout, and `check_handoff.py --all` shows the item as not checked, exit 1.
- After the recovery command, all three report as in a full clone (`093` in the fixture).
- A full clone (including this repo) gives the same output as before.
- A failed `git config` is a loud 081 error.
- Six files change. The suite is green, and m1-m7 each fail a named test.

Recurring issues checked (item 013), against this file:
- RI-001 (ESCALATED): every filter-like rule has a non-zero dated count and a pinning test (4 of 12 shapes; 3 of 3 depth tests).
- RI-010 (ESCALATED): no log line is typed here. The only one is the `Log fields:` line below, for the orchestrator's `--log`.
- RI-014 (OPEN, this family): a failed config read is an error, never "full" or "none". The fixtures use real clones of each depth/branch shape (C3).
- Also checked, GUARDED and related:
  - RI-002: an absent value is never turned into "full"; S8 and S10 give "not checked".
  - RI-009: --next-id, IN PR and ID CLASH never answer from hidden refs.
  - RI-012: equality checks on one constant, and a literal in the tests.
  - RI-008: the py_compile check.
  - RI-006: the census total is bumped from the AST count, not hand-totalled (C2).

Log fields: FIT WITH CHANGES | 6 files planned
