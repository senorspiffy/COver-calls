# 01 Research brief - 084
## Question
PR #33 + main (b2f11b9) prints `INCOMPLETE: 083`. 083 was built and merged on main (PR #34, build commit cfc0634) while the format rules of items 071 and 076 were only on open PRs #32/#33. What item-number cutoff rules does `scripts/check_pipeline.py` have, which items on main does each one reach, and what anchor ("the rule applies to this item") would leave 083 unflagged while still checking every item built under the rule (fixture + mutation, request.md)?

Method: read on this branch (daily-fixes/2026-11-20, built on PR #33): `scripts/check_pipeline.py` (L1-197 docstring, L214-302 constants, L464-616 incomplete/log checks, L720-803 `_open_at`/`_walk`, L990-1014 `_inbox_gate`), `tests/test_pipeline_check.py`, `logs/recurring-issues.md` (RI-010), `logs/audit/2026-11-20.md`, `logs/audit/2026-11-20-083.md`, `logs/audit/2026-11-18.md`, the 083 log lines and `work/083/06-verification.md`. This agent has no shell in this run: no git command and no `check_pipeline.py` / `check_handoff.py` run was done by R1. Which PR carries which rule is taken from request.md and the audit reports, not from `git log`.

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
### A. Why 083 is flagged (repo files, read 2026-11-20)
1. The INCOMPLETE text has two parts: (a) the I2 line `10:15 | I2 | 083 | 2 files changed | tests 344/344` (logs/implementation/2026-11-20.md L19) fails `LOG_FORMAT["I2"]` because 083 >= `TESTS_FORMAT_FROM = 76` (check_pipeline.py L225, L467-470, L529-534); (b) 06 L2 is `Verdict: PASS (round 1)` with no `Sent back to:` line, and 083 >= `VERDICT_FROM = 71` (L245, L537-543). [repo: scripts/check_pipeline.py; logs/implementation/2026-11-20.md; work/083/06-verification.md]
2. Under main's rules, the same line passes: `I2_BEFORE` (L235) accepts `344/344` with pass <= total. Note for A1, not part of 084: main's suite at 083 was "344 passed, 1 skipped" (logs/audit/2026-11-20-083.md L10), so by 076's own definition of total (passed + skipped + ...; docstring L76-78) the field would be 344/345. Main's rule never defined total (RI-006 near miss 2026-11-19), so this is not an error under the rules 083 was built under. [repo: logs/audit/2026-11-20-083.md; logs/recurring-issues.md RI-006]
3. 083's I3 log line (`PASS | sent to audit: yes`) matches its 06 verdict PASS, so the 071 verdict-vs-log cross-check does not fire for 083. [repo: logs/implementation/2026-11-20.md L20]
4. 083 changes `ccbot/bot.py` (logs/audit/2026-11-20-083.md L8), which is not in `TRIGGER` (L250-251), so the 070 REAL-DATA FIELD rule does not fire for 083 today. [repo]

### B. Every item-number (or list) cutoff in check_pipeline.py and the main items it reaches
Main's items, per the audit reports: 001-068 built, plus 083 (PR #34); 069-070 are on PR #31, 071-074 on PR #32, 075-079 on PR #33 (logs/audit/2026-11-20.md L17); 080-086 are today's branch. `work/073/request.md` alone reached main in 4d690a3 before 073 was built (logs/audit/2026-11-18.md L2, L57). Not re-checked with git by R1 (UNVERIFIED by command).

| # | Rule (item) | Cutoff in code | Where the rule is (per request/audit) | Main items it reaches | Flags on PR #33 + main today |
|---|---|---|---|---|---|
| 1 | 06 `Recurring issues checked:` line + one log line per step (043) | `CHECKLIST_FROM = 41` (L220, L518) | main (PR #11, 2026-11-05) | 041-068, 083 | none (built after or with 043) |
| 2 | Log line format per agent (045) | `LOG_CHECK_FROM = 45` (L224, L529) | main (PR #12, 2026-11-07) | 045-068, 083 | none |
| 3 | LOG TIME, line timed after its commit (045) | `LOG_CHECK_FROM`, minus `LOG_TIME_EXCEPT = {048}` (L239, L609) | main (PR #12; exception 049, PR #15) | 045-068, 083 (048 named) | none |
| 4 | REAL-DATA FIELD in 05/06 (070) | `WHOLE_DIFF_FROM = 70` (L241, L920) | PR #31 only | 083 | none today (083 touches no TRIGGER path); would flag any main item >= 070 that changes realtest's path |
| 5 | Readable `Verdict:` + matching `Sent back to:` (071) | `VERDICT_FROM = 71` (L245, L537) | PR #32 only | 083 | **083** ("PASS but has no 'Sent back to: none' line") |
| 6 | 06 verdict = first word of last I3 log line (071) | `CHECKLIST_FROM = 41` (L544-554; docstring L46-48) | PR #32 only, but reaches back to 041 | 041-068, 083 | none today; a 071 rule applied to 28 main items built before it, so it is in the same family as rows 5 and 7 |
| 7 | I2 tests field = pytest summary as printed (076) | `TESTS_FORMAT_FROM = 76` (L225, L467, L476; also `--log` refusal L561-562) | PR #33 only | 083 | **083** (`tests 344/344`) |
| 8 | I3 FAIL status from 06 verdict (071, 077) | no cutoff, every item (L443-452) | PR #32/#33 | all | none (no main 06 opens with FAIL, `test_repo_pipeline_has_no_skipped_items` asserts `I3 FAIL: none`, tests L177) |
| 9 | UNCOMMITTED STEP (077) | no cutoff; working tree vs HEAD only (L493-513) | PR #33 | committed items never | none |
| 10 | UNTRACKED CHANGE / RESEARCH CODE (053, 062, 064) | SHA `UNTRACKED_FROM` (L264) + `_open_at(parent, item)` at each commit (L720-730) | main | commit-based, not item-number | none |
| 11 | INBOX (069 round 2) | template at the commit that added the report (`git log --diff-filter=A`, L1002-1014) | PR #31 | commit-based | none |
| 12 | Closed lists `PRE_A1_LINE`, `LEGACY`, `LOG_TIME_EXCEPT` | fixed IDs, "never add" (L213-216, L236-239, L299-301) | main | 001-022, 048 | n/a |

So the rules that reach a main item they were not on main for are rows 4, 5, 6 and 7 (the four on unmerged PRs). Today only rows 5 and 7 produce an entry, both for 083. Rows 1-3 are on main and every main item they reach was built after them, except 048, which the closed `LOG_TIME_EXCEPT` covers for row 3 only (049).

### C. Commit-based precedents already in the script
5. Item 053 judges each first-parent commit after a fixed SHA against its first parent and asks whether the item was open at that parent (`_open_at`, L720-730; `_walk`, L796-803). [repo: scripts/check_pipeline.py]
6. Item 069 round 2 applies the Inbox rule only if the template at the commit that added the report has `## Inbox` ("never a date", L183-196, L302). This is the closest precedent: the rule follows when the checked file was written, not a number. [repo: scripts/check_pipeline.py]
7. `git log --first-parent` follows "only the first parent commit upon seeing a merge commit". [https://git-scm.com/docs/git-log]
8. `git merge-base --is-ancestor A B` exits 0 if A is an ancestor of B, 1 if not; "Errors are signaled by a non-zero status that is not 1". [https://git-scm.com/docs/git-merge-base]
9. Whether `--is-ancestor X X` returns 0 is not stated on that page. UNVERIFIED (I1 should run it once in a scratch repo and pin it in a test if the design relies on it).
10. `--diff-filter=A` selects files that are Added; `-S<string>` finds commits that "change the number of occurrences of the specified <string>". [https://git-scm.com/docs/git-diff]
11. `git blame` annotates each line "with information from the revision which last modified the line"; `--line-porcelain` gives commit information for each line. [https://git-scm.com/docs/git-blame]

### D. Anchor choice: the request's wording has a hole
12. request.md L13 anchors on "items whose request.md first reached main after the rule's own commit reached main". Two problems, from the repo: (i) request.md often reaches main before the item is built: `work/073/request.md` was committed alone on main (4d690a3) on 2026-11-18, before 071's rule (PR #32) reached main; 075-078 were opened in an audit addendum before 076 was built (logs/audit/2026-11-19.md L29). With this anchor 073, and very likely 076-079 themselves, would be exempt from the very rules they were built under. That is a silent loosening, the RI-010 failure mode. (ii) On an open rules branch, "reached main" is false for the rule itself, so on PR #33 before merge every item would be "not checked" by 071/076, and the branch check would lose its purpose. [repo: logs/audit/2026-11-18.md L2, L57; logs/audit/2026-11-19.md L29]
13. An anchor without those holes: the rule applies to an item's artifact when the commit that **added the rule** is an ancestor of (or equal to) the commit that **added the checked artifact**. The artifact is the log line for rows 2/3/7 (blame commit, as LOG TIME already uses, L600-615), and 06 for rows 1/5/6 (`git log --diff-filter=A -- work/<ID>/06-verification.md`, as INBOX does). For 083, cfc0634 (on main) does not descend from the 071/076 rule commits, so it is "not checked", on the branch and after the merge alike. Items built on the rules branch descend from them, so they stay checked. Basis: findings 8, 10, 11; the design itself is R1's proposal for R2/R3, not a sourced fact.
14. How to find "the commit that added the rule" needs a decision. (a) A hard-coded SHA can't name the commit it sits in; 053's precedent uses the parent (L263), but the parent of a rule commit cut from main can be a main commit, and then parallel main items descend from it. So the parent is wrong here. (b) The commit that added `work/<rule-item>/05-build-report.md` (`--diff-filter=A`): I2 commits code with 05 (053 gap b, L113-114). (c) `git log -S"VERDICT_FROM ="`: finds the constant's first commit, but it is fragile to renames. R1 leans to (b). Not verified on real history (no shell).
15. The 048 case is already this situation (branch cut before 045 reached main, RI-010 2026-11-07). Under finding 13, 048's format/time checks would turn into "not checked" by the anchor instead of by the closed list. Its lines were rewritten by 049 (L236-238), so blame now gives 049's commit and they may stay checked. Keep `LOG_TIME_EXCEPT` unchanged either way ("never add", L238). UNVERIFIED which way 048 falls (needs `git blame`).

### E. Effects on the tests and the no-git case
16. Most fixtures in tests/test_pipeline_check.py build items in a plain tmp_path with no `git init` (`_item` L27, `_run` L59). `_git` returns None when cwd is not a work-tree top (L619-630), and fixtures like `test_old_06_without_round_headers_unchanged` (L2133-2146: 060/065 unchecked, 173 flagged) and `test_i2_tests_field_cutoff` (L689) depend on the numeric cutoffs alone. With no git, the anchor can't be computed. The safe reading (RI-002: never default unknown to a pass) is that the numeric cutoff applies unchanged without git and the line says so. The anchor only narrows items >= the numeric cutoff when git can answer, and never reaches below it. [repo]
17. A failed ancestry call (exit not 0/1, finding 8) must be an error or "not checked", never "applies: no" (081's lesson, RI-014 near miss 2026-11-20). [https://git-scm.com/docs/git-merge-base; logs/recurring-issues.md RI-014]
18. `test_repo_pipeline_has_no_skipped_items` runs `check_pipeline.py` on a detached worktree of HEAD (tests L169-178, `_run_head`), so git history is there and the anchor can be computed in that test. In a shallow clone the rule/artifact commits may be missing. That must print "not checked (... run git fetch --unshallow)", as 079 does. [repo]

## Numbers used (show the math)
- Main items that rows 4-7 reach but were not built under: row 5 and row 7: IDs >= 71 and >= 76 on main = {083} -> 1 item each. Row 4: IDs >= 70 on main = {083} -> 1, 0 flagged (no TRIGGER path). Row 6: IDs 041-068 plus 083 = 28 + 1 = 29 items reached, 0 flagged today (orchestrator's INCOMPLETE shows only 083, and 083's own reason has no verdict-vs-log part).
- 083 I2 field under 076's definition: total = 344 passed + 1 skipped = 345, not 344 (finding 2).
- Count of sources: taken by the orchestrator from `python3 scripts/check_handoff.py 084` (R1 could not run it in this session). URLs cited: git-log, git-merge-base, git-diff, git-blame docs.

## Fit for a ~$3k account
Process-only item. No trade, price, option or broker input, so no effect on the $3k limits, assignment, dividends, taxes, commissions or liquidity. It keeps PR #33 mergeable, so the earlier guardrails in it can reach main. Research, not financial advice. Nothing connected to a brokerage.

## Open questions
1. Anchor (finding 12 vs 13): should R2/R3 keep request.md's "request.md reached main" wording or switch to "rule commit is an ancestor of the artifact's commit"? R1's reading: the request.md anchor exempts 073 and probably 076-079 from their own rules. R2 should confirm this with `git log --diff-filter=A -- work/07[1-9]/request.md` against the rule commits.
2. How the rule commit is found (finding 14 a/b/c). R1 leans to (b), the commit adding the rule item's 05.
3. Should row 6 (071 cross-check reaching back to 041) be gated too? It flags nothing today, but it is the same pattern. Also, should rows 1-3 (on main, cutoffs older than every main item they reach) be gated at all, or left numeric to avoid churn?
4. No-git behaviour (finding 16): numeric cutoff as today, plus a printed note? Needs R3's call. It decides how many fixtures change.
5. Whether `--is-ancestor X X` exits 0 (finding 9), if the rule commit and the artifact commit can be the same commit (an I2 line committed with the rule code).
6. The 083 I2 field `344/344` with 1 skipped (finding 2) is for A1/RI-006, not 084.
