# Work item 037
Type: BUG
Scope: FULL
Opened by: A1
Date: 2026-11-03

## What we want
Two different work items carry the ID 025, one on main and one on an open branch. Because the check matches items by ID, the open PR's item is hidden: `check_pipeline.py` says `IN PR: none` while PR #5 waits with its own 025. Stop two items from getting the same ID, and make the check report a clash when one exists.

## Evidence (for BUG/EFFICIENCY: log lines, files, test output)
- main `work/025/request.md`: "Type: BUG ... Opened by: A1 ... Date: 2026-10-31", the F/VALE `EARNINGS_UNKNOWN` correction (merged in PR #6).
- `origin/claude/project-thread-xrug2s:work/025/request.md` (PR #5, open since 2026-10-31 15:49 UTC): "Type: IDEA ... Opened by: person (023 thread ...) ... Paper trade real tickers (F, VALE, AAL)".
- Neither file exists at the merge base (`git merge-base main origin/claude/project-thread-xrug2s`): both sides created `work/025/` on their own.
- `python3 scripts/check_pipeline.py` on main, 2026-11-03: `025: complete (FULL)`, `IN PR: none`, and only `origin/claude/project-thread-xrug2s: items 025; CONFLICTS: ... work/025/05-build-report.md, work/025/request.md`. The person's open paper-trading PR is never named as an item in a PR.
- `logs/audit/2026-11-02.md` "Items reviewed" lists "open PRs #5" but says nothing about it; the OPEN BRANCHES line looked like an old copy of the merged 025.

## Root cause and prevention guardrail (BUG only)
Root cause: a new item's ID is taken as the next free number in the tree you are standing in. Work started in another thread on another branch is invisible to that choice (same blind spot as RI-009), and `check_pipeline.py` then joins the two items by ID, so the clash also hides the branch's item.
Guardrail:
1. `check_pipeline.py` reports `ID CLASH: <ID> (<branch>)` when an open branch and HEAD each added `work/<ID>/request.md` since their merge base with different text. A1 lists it at the top of the daily report.
2. `check_pipeline.py --next-id` prints the next free ID over HEAD and every unmerged remote branch. a1-auditor and the README say to use it when opening an item.
3. Tests in a temp git repo: both sides add 050 → `ID CLASH: 050`; `--next-id` counts the branch's items.

## Recurring issue link (RI-#, if any)
RI-009 (work on unmerged branches invisible to the audit): occurrence 3 → ESCALATED.

## Done looks like
On main today the check prints `ID CLASH: 025 (origin/claude/project-thread-xrug2s)` and `--next-id` prints the next number above every branch. Tests pass. Renaming PR #5's item is the person's call (we don't push to their branch).
