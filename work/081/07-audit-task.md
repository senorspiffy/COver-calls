# 07 Audit task - 081
Item: 081 (BUG, FULL). Failed git reads never read as "none" in scripts/check_pipeline.py, and non-UTF-8 git output never crashes it (RI-014).
I3: PASS round 2 (round 1 FAIL, sent back to I1). Build commits: d44b687 (round 1), e5297e7 (round 2), on daily-fixes/2026-11-20.

## What to look at
1. **RULES change from round 1 (needs the person's OK).** `.claude/agents/a1-auditor.md` has 2 added runs and 0 removed words (`--word-diff=porcelain`): L23 says `BRANCH ERROR:` lines go to the top of the report, and L29 covers the `--next-id` refusal. Round 2 adds no rule text. Get the person's approval in PR review.
2. **Round-2 decision: no common history is a real answer.**
   - `git merge-base --all` exit 1 → the line `<ref>: no common history with HEAD; not scanned (item 081)`.
   - That branch is quiet only when a successful `ls-tree` shows 0 files under work/, logs/recurring-issues.md, RULE_PATHS and RESEARCH_CODE_PATHS. Otherwise it is a BRANCH ERROR.
   - Any other merge-base exit is `git merge-base failed (exit <n>)`.
   - Check that this classification uses the exit code only (RI-012), and that the quiet case cannot hide anything the per-ref scan would read. Is any path the per-ref scan reads missing from the ls-tree pathspec?
3. **Shallow-clone wording (I3 probe, not a defect).** In a `--depth 1` clone, a branch that does share history makes `merge-base --all` exit 1, so it reads as "no common history". It stays loud: BRANCH ERROR when it holds checked paths, plus the shallow `not checked` lines, exit 1. A branch with no checked paths would be quiet, but it holds nothing the scan reads. Decide whether the wording needs a later EFFICIENCY item. A cross-check with 079's shallow detection would be enough.
4. **Known gap, documented in the docstring.** check_handoff's `_branch_with_handoff` does not read per-ref `errors`, so a 03 that exists only on an unreadable or unrelated branch shows `no hand-off`. Decide whether this needs its own item.
5. **Mutation probe on main after merge** (RI-014 GUARDED condition): "GUARDED when 079 and 081 are merged and m2 fails fixture (b) on main." m2: in `open_branches`, change `if why:\n        return why` to `return []` → `test_malformed_shallow_real_git_nothing_none` must fail. Also try m1 (blame failure → bare `continue`) → `test_blame_failure_of_committed_log_is_an_entry` must fail.
6. **Census.** `GIT_CENSUS` total is 47 (41 + 5 for 084 + 1 for 081 r2). If 086 lands git calls first, re-check the total and the per-function reasons after merge.
7. **Suite state at e5297e7.** 4 failed, 642 passed, 1 skipped. None of the 4 is 081's: 3 come from 086's not-computable text, and `test_repo_pipeline_has_no_skipped_items` fails while 081/084/086 are open. Confirm they are gone once 086 is fixed and the items close.

## Files
- scripts/check_pipeline.py, scripts/check_handoff.py, tests/test_pipeline_check.py, .claude/agents/a1-auditor.md
- work/081/04-build-plan.md (Round 2), work/081/05-build-report.md (Round 2), work/081/06-verification.md (# Round 2)
