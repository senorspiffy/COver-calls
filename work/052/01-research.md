# 01 Research brief - 052
## Question
How should `check_pipeline.py` find the files an open branch changes, and the base for ID CLASH, when the branch and HEAD have more than one merge base?

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
- No market facts are needed: the change is in this repo's own script. Sources are repo files, git docs and commands.
- `open_branches()` takes changed files from `git diff --name-only HEAD...<ref>` (items, item-036 note, RULES BRANCH) and the clash base from `git merge-base HEAD <ref>` [repo: scripts/check_pipeline.py `def open_branches`].
- `git diff A...B` is the diff from a merge base of A and B to B; with several merge bases git uses one of them [git docs: https://git-scm.com/docs/git-diff].
- `git merge-base --all` prints every best common ancestor; there can be more than one (criss-cross merge) [git docs: https://git-scm.com/docs/git-merge-base].
- `git merge-tree --write-tree` prints the tree OID of the merge result on its first line, also when there are conflicts (exit 1), and handles several merge bases like a real merge [git docs: https://git-scm.com/docs/git-merge-tree].
- 2026-11-10 on main a30101c: `merge-base --all main origin/daily-fixes/2026-11-09` → bfb0cfe, f74949a; the script lists items 049, 050, 051 and RULES BRANCH with 3 files; `git diff --name-only HEAD <merge-tree tree>` lists 051's files, check_pipeline.py, its test and 2 log files [A1 run, logs/audit/2026-11-10.md].

## Numbers used (show the math)
- Items listed: 3 (049, 050, 051) − 2 already on main = 1 correct.
- RULES BRANCH files: 3 listed − 2 not changed by the branch = 1 correct.

## Fit for a ~$5k account
Process only; no trading rule or number changes.

## Open questions
- Keep a fallback for git without `merge-tree --write-tree` (needs git 2.38)? R2 to weigh.
