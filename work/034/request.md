# Work item 034
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-02

## What we want
The daily audit and `scripts/check_pipeline.py` look only at the checked-out tree (main). Work that is done but waiting in an open pull request is invisible, so the person is told it hasn't started, and new branches are built without the rules those PRs add. Make unmerged branch work visible to the check and to A1.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- `logs/audit/2026-11-01.md` told the person: "014 has not started (now 2 days)" and "009–016 ... 2 days with `request.md` only ... Please say which to run."
- But PR #7 "Run stuck items 009-016" (branch `daily-fixes/2026-10-31-stuck`, commit a95a51a, opened 2026-10-31 22:39 UTC) already carries 01–07 for all eight items. On that branch `check_pipeline.py` → `STUCK: none`, `SKIPPED: none`; `python3 -m pytest -q` → 159 passed, 1 skipped (A1, 2026-11-02).
- PR #8 (`daily-fixes/2026-11-01`) was built on main without PR #7's i3 rule "RI-002: in a scratch copy, never in the repo, put back one removed default" (i3-verifier.md on PR #7). In PR #8, I2's mutation restore used `git checkout` in the repo and wiped the uncommitted 031 edit (work/032/06-verification.md, "Note from I2").
- PR #7 now conflicts with main (`logs/recurring-issues.md`) and with main + PR #8 (`logs/recurring-issues.md`, `.claude/agents/i3-verifier.md`): A1 trial merges in scratch, 2026-11-02. Nobody reported it.
- `scripts/check_pipeline.py` reads only `Path("work")`; it never asks git about other branches.

## Root cause and prevention guardrail (BUG only)
Root cause: the pipeline check and A1's daily review have one source of truth, the working tree. A fix branch that waits for the person's merge is outside it, so STUCK means "not on main", not "not started", and later branches don't know what earlier PRs change.
Guardrail:
1. `check_pipeline.py` asks git (when run in a repo) for every remote branch not merged into HEAD. An item that is STUCK / not started / in progress on HEAD but has more step files on such a branch is reported `IN PR (<branch>: <steps>)`, listed on an `IN PR:` line, not as STUCK.
2. It prints `OPEN BRANCHES:` with each unmerged branch, the work items it carries, and `merges cleanly` / `CONFLICTS: <files>` against HEAD (`git merge-tree --write-tree`).
3. a1-auditor daily mode: put IN PR items and any CONFLICTS at the top of the report; build the next fix branch on top of (or after merging) any open fix branch it depends on.
4. Tests in a temp git repo: an item with request.md only on main and 01–07 on a branch → `IN PR`; a conflicting branch → `CONFLICTS`.

## Recurring issue link (RI-#, if any)
New RI-009 (2 occurrences).

## Done looks like
Run on main today, the check shows 009–016 as `IN PR (daily-fixes/2026-10-31-stuck ...)`, `STUCK: none`, and `daily-fixes/2026-10-31-stuck: ... CONFLICTS: logs/recurring-issues.md`. Two new tests pass.
