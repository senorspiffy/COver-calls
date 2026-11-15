# 01 Research brief - 066
## Question
Two things, smallest change for each (request.md "Done looks like"):
1. Stop `tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items` from failing one item's test run because of another item's uncommitted step files in the same working tree. Choices: (A) run-item.md says one item at a time per working tree (or one worktree per item), or (B) the test checks committed state only.
2. Move the three constant `_is_code` asserts out of the parametrized `test_work_code_pattern` into one test.

This is EFFICIENCY, with no trading content. Nothing here touches the bot's rules, the $3k account limits or any ticker screen (step 3a does not apply).

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
Repo facts (read in this tree on 2026-11-15; file:line references, not web claims):
- F1. The test runs the real script on the working tree: `_run(REPO, "check_pipeline.py")`, then `assert code == 0, out`, plus `"RESEARCH CODE: none"` and `"061: complete"` (tests/test_pipeline_check.py L139-144). `_run` is `subprocess.run([...], cwd=root)` (L43-46).
- F2. `check_pipeline.main` lists items with `work.iterdir()` (scripts/check_pipeline.py L590). `classify` uses `(item_dir / STEPS[s]).exists()` (L250), and `incomplete` reads every `logs/research|implementation/*.md` on disk (L283-286). Uncommitted files count the same as committed ones.
- F3. The 063 failure was exactly this. 063/05 L98-101: `FAILED ...::test_repo_pipeline_has_no_skipped_items`, and `check_pipeline.py` printed `INCOMPLETE: 064 (no log line for I1)` because 064's uncommitted 04-build-plan.md had no I1 line yet. INCOMPLETE makes the exit code 1 (L654).
- F4. The two halves of the check (step file, then `--log` line) are written one after the other (run-item.md L14: "each step's agent writes its log line with `check_pipeline.py --log` as soon as its file exists"). Any test run that lands between them in a shared tree sees INCOMPLETE for that item. With one item at a time, the only agent running the suite is the one between steps, so this window never overlaps its own run.
- F5. run-item.md has no rule on how many items run in one working tree (whole file read, L1-17). L5 says "one agent at a time" for one item only.
- F6. Right now two items (065 and 066) are running in the same tree (caller's task message). So option A, as a rule, is not what the orchestrator does today. Adopting A means changing how items are launched, not just adding a sentence.
- F7. run-item.md is a rule file. 064/06 L20 says `.claude/commands/run-item.md` edits "need the person's OK in PR review". `check_pipeline.py` lists `.claude/` under RULES BRANCH (docstring L59-61).
- F8. Option B is test-only, in one file. The test could run the script in a detached worktree of HEAD instead of `REPO`. In that worktree, `work/` and `logs/` hold only committed files. Git still works there for UNTRACKED CHANGE, RESEARCH CODE (the `RESEARCH CODE: none` assert) and LOG TIME, because the worktree shares refs and objects. [https://git-scm.com/docs/git-worktree]
- F9. `git worktree add -d <path>` "creates a new worktree with a detached HEAD at the same commit as the current branch", and a linked worktree shares "everything except per-worktree files such as HEAD, index, etc." [https://git-scm.com/docs/git-worktree]
- F10. pytest's `tmp_path` gives "a temporary directory unique to each test function", so a per-test worktree path cannot collide with another run's. [https://docs.pytest.org/en/stable/how-to/tmp_path.html]
- F11. A full worktree checks out all of HEAD, including data/real/options/*.csv.gz (more than 100 files under data/, Glob). Time and disk cost per test run: UNVERIFIED (not measured, since this agent has no shell). A `git archive HEAD work logs` copy would be lighter. But outside a git dir the script prints `RESEARCH CODE: not checked (no git)` (L650), which breaks the L143 assert. So a lighter copy is not a drop-in.
- F12. Under B, the repo test no longer sees the running item's own uncommitted step files either. They are still checked by the `python3 scripts/check_pipeline.py` run that run-item L14 requires at the end, and by I3's run (064/06 L45). B also needs a skip, or a fallback to `REPO`, when there is no git or no HEAD (for example a tarball). Exact form UNVERIFIED (design choice for R2/I1).
- F13. `test_work_code_pattern` (L987-1003) has 8 parametrize cases. Each case runs 2 path-specific asserts (L999-1000) and 3 constant asserts that do not use `path` or `hit` (L1001-1003). pytest runs the function once per argument set, each a separate test. [https://docs.pytest.org/en/stable/how-to/parametrize.html] So one regression in a constant assert is reported 8 times. 064/06 L48: mutation (i) failed "all 8 test_work_code_pattern cases".
- F14. Moving L1001-1003 into one new non-parametrized test changes the collected count by +1 (8 cases stay, 1 test added). Folding them into an existing test, e.g. `test_research_code_rules` (L841, already a `_cp()` unit test of the 062/064 rules), changes it by 0. Neither "merges" a parametrized case away. See Open questions.
- F15. The last full-suite count I can cite is 064/06 L34 on daily-fixes/2026-11-14 at 779a414: `316 passed, 1 skipped`. The count on today's branch (with 063 and 064): UNVERIFIED (not run by R1).

## Numbers used (show the math)
- Option A size: 1 file (.claude/commands/run-item.md), about 1 sentence. It is a rule file (needs the person's OK), and nothing enforces it (F6).
- Option B size: 1 file (tests/test_pipeline_check.py). About 6-10 changed lines (estimate: worktree add, run, assert, remove, skip when there is no git). UNVERIFIED until I1 plans it.
- Constant asserts: 3 asserts × 8 cases = 24 runs today, 3 after the move. Collected tests go 8 → 9 with a new test, or stay at 8 if folded into `test_research_code_rules` (F14).
- 063's count: 297 passed + 1 failed = 298 = 293 + 5 new (063/05 L102). The 1 failure is the cross-item one.

## Fit for a ~$3k account
Not applicable. This is test and process plumbing. No change to screening, strikes, assignment or dividend handling, cost, or trades.

## Open questions
1. A or B? A is smaller in text but needs the person's OK and contradicts how items are launched today (F6, F7). B is test-only and holds however items are launched, but costs a worktree checkout per run (F11, cost UNVERIFIED). For R2/R3 to weigh. R1 leans to B, because it holds without anyone following a new rule.
2. Under B, is a worktree checkout of HEAD acceptable in time and disk, or should it be sparse (work/, logs/, scripts/ only, via `git sparse-checkout`)? UNVERIFIED (not measured).
3. "Same pass count minus the merged cases": moving the 3 asserts into a new test gives +1, not a minus. Confirm with A1 whether a new test (+1) or folding into `test_research_code_rules` (+0) is meant.
4. The suite count on daily-fixes/2026-11-15 before the change: to be measured by I1/I2 (F15).
