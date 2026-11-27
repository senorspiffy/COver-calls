# 01 Research brief - 113
## Question
Three small EFFICIENCY cleanups from the 105/107/110 audits (all PR #39), on branch daily-fixes/2026-11-26 (built on daily-fixes/2026-11-25):
(a) What should templates/build-plan.md and templates/build-report.md say about `RULES BRANCH:`, so that 04/05 stop expecting a branch to show its own rule change?
(b) `who` from `parse_request` has no reader in scripts/ since 105. Should it be removed or kept, and what does each choice touch?
(c) The item-110 figures in the check_pipeline.py docstring are dated 4404a28. What text tells a reader to re-run the script instead of copying them?

Recurring issues read first: RI-009 (branch visibility), RI-010 (checklist step with no check), RI-001 (counts asserted, not measured). This item fixes wording only. No RI occurrence is counted.

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
### (a) RULES BRANCH visibility
1. `git branch --no-merged [<commit>]`: "Only list branches whose tips are not reachable from <commit> (HEAD if not specified)." `-r` lists the remote-tracking branches. [https://git-scm.com/docs/git-branch]
2. `open_branches()` takes its branch list from `git branch -r --no-merged HEAD --format=%(refname:short)`. Every RULES BRANCH entry comes from that list (`ruling = [... for b in blist if b["rules"]]`). [repo: scripts/check_pipeline.py L1700, L1712, L2333-2334]
3. RULE_PATHS = `.claude/`, `templates/`, `scripts/check_pipeline.py`, `scripts/check_handoff.py`. [repo: scripts/check_pipeline.py L538-539]
4. The docstring says RULES BRANCH lists "an open branch that changes the rules ... build new items on top of it". It does not say the branch must be not merged into HEAD, or that the checked-out branch's own ref is left out. [repo: scripts/check_pipeline.py L232-234]
5. Effect from a branch's own checkout, derived from 1 and 2:
   - Once the branch is pushed, the tip of its own remote-tracking ref is HEAD or an ancestor of HEAD, so it is reachable and not listed.
   - Uncommitted or unpushed edits are on no remote ref at all.
   - The open branch it was built on (here daily-fixes/2026-11-25, PR #39) is also merged into HEAD, so it is not listed either.
   - So from the branch's own checkout, RULES BRANCH never names that branch's own rule change. It can name it only if the remote ref has commits that HEAD lacks (for example, another clone pushed to it).
   [derived from https://git-scm.com/docs/git-branch and scripts/check_pipeline.py L1700]
6. Seen in practice:
   - 105/04 Tests 5 expected the RULES BRANCH line to "now name scripts/check_pipeline.py on this branch" (work/105/04-build-plan.md L110, L165).
   - 105/06 shows `RULES BRANCH: none` from the branch checkout (work/105/06-verification.md L107).
   - From origin/main 1d0de33, the line reads `origin/daily-fixes/2026-11-25 changes scripts/check_pipeline.py` (work/105/07-audit-task.md L5).
   - 05 gave the wrong reason, "not pushed" (logs/audit/2026-11-26-105.md L57-58, follow-up 2 L68-70).
   [repo files named]
7. Same misread in 107: 04 expected RULES BRANCH to name the 4 rule files, and 05 got `none` (work/107/04-build-plan.md L80; work/107/05-build-report.md L101; work/107/07-audit-task.md L15). [repo files named]
8. `git merge-base --is-ancestor A B` "exit[s] with status 0 if true, or with status 1 if not". It is a one-command way to confirm a ref is merged into HEAD. [https://git-scm.com/docs/git-merge-base]
9. The templates today have no RULES BRANCH text:
   - build-plan.md has `## Tests and checks` (L5) and `## Expected result` (L12).
   - build-report.md has `## Deviations from plan` (L14).
   [repo: templates/build-plan.md, templates/build-report.md]
10. Existing pattern for pinning a template line: `test_scratch_dir_template_line` asserts the exact line appears once (`splitlines().count(...) == 1`) in each parametrized template. `test_round_heading_template_lines` does the same with `.count(line) == 1`. [repo: tests/test_pipeline_check.py L5651-5658, L5221-5238]
11. Editing templates/ (and check_pipeline.py for (c)) is a RULE_PATHS change. This branch will then show as a RULES BRANCH from main, and the wording needs the person's OK in PR review (precedent 105/04 C4, L10). [repo: work/105/04-build-plan.md L10; scripts/check_pipeline.py L539]

### (b) `who` in parse_request
12. `parse_request` returns `(scope, date, (steps, first Waived line, who))`. `who` = `re.match(r"\s*\(\s*([^,:)]+)", group 2)`, stripped and lower-cased. The docstring already says "who: kept for the tuple shape; no gate reads it since 105." [repo: scripts/check_pipeline.py L628-638]
13. All callers of parse_request, from a whole-repo grep outside logs/:
    - In scripts/check_pipeline.py: L660 `_, _, (steps, _, _)` (`_build_waived`), L672 `scope, _, (waived, _, _)` (`_person_waived_before_i2`), L781 `scope, opened, (waived, waived_line, _)` (`classify`). These three unpack the 3-tuple and discard `who`.
    - L760, L768, L1323 and L2080 index `[0]` only.
    - In tests: tests/test_pipeline_check.py L1974 `scope, _, (waived, line, who) = cp.parse_request(text)`, with L1976 `assert waived == [] and line == "" and who == ""`.
    - No other script calls it.
    [repo: grep `parse_request`]
14. Python unpacking: for a target list without a starred target, "The object must be an iterable with the same number of items as there are targets in the target list". A site left on 3 targets after a 2-tuple change raises at runtime (ValueError in CPython: UNVERIFIED on that page, which names no exception type). It does not silently mis-assign. [https://docs.python.org/3/reference/simple_stmts.html]
15. No gate depends on `who`:
    - `_person_dated` (`WAIVED_LINE.search` + `PERSON_DATED.match(group 2)`) is the single check behind classify, `_build_waived` and `_person_waived_before_i2` (105).
    - The anchor implies who == "person", so a who check would be an equivalent mutant (100/03 R1/R2 row; 100/01 finding 12).
    [repo: scripts/check_pipeline.py L641-650, L653-661; work/100/01-research.md L23]
16. In 105 the planners chose to keep `who` for the tuple shape (105/04 L40; 105/05 L35). A1 marked removing it "Information only ... could be removed in a later item, together with the tests L1963 unpack" (the test is now at L1974). [repo: work/105/04-build-plan.md L40; logs/audit/2026-11-26-105.md L71-72]
17. Text that names `who` and would need a word change if it is removed:
    - the `_build_waived` docstring: "The anchor implies who == "person"" (L657-658);
    - the module docstring L15-20 (`<who>` in the documented waiver form). This means the request.md field, not the variable, so it stays.
    [repo: scripts/check_pipeline.py L15-20, L657-658]

### (c) dated 110 figures
18. The docstring says "Item 110 (gap w, RI-010): 103's two residuals were measured at 4404a28 ... 4 in 58 files ... 34 files would gain values, 0 per-file maxes and 0 LOG BATCH results change over 59 checked items." [repo: scripts/check_pipeline.py L226-231]
19. A1 re-ran the script at ed9809b and got 62 files read, 38 files gaining values and 61 checked, with the same conclusions (0 maxes changed, all same=True). A1's follow-up: "If a later item quotes these figures it should re-run the script rather than copy them." [repo: logs/audit/2026-11-25-110.md L32-36, L67-69]
20. The script is the fenced block at work/110/01-research.md L36-147, run as `python3 -I -`. Its first line hard-codes `cd /home/claude/cover-calls` (L37), so a re-run from another checkout must change or drop that `cd`. [repo: work/110/01-research.md L36-37, L149]
21. `test_check_pipeline_docstring_records_110_no_go` pins these strings: "Item 110 (gap w, RI-010)", "0 per-file maxes", "work/110/03-handoff.md" (and that the file exists), "or raise it when 06 copies such a run", the absence of "only lowers Σ", and the source comment "measured to change nothing (item 110)". If a sentence is added and the figures are left in place, all of these stay green. [repo: tests/test_pipeline_check.py L5991-6002]
22. The `_STATS_PARTS` comment at L473-475 ("measured to change nothing (item 110)") gives a conclusion, not a figure, so it is not dated in the same way. [repo: scripts/check_pipeline.py L473-475]

## Numbers used (show the math)
- (b) call sites: 3 tuple-unpacking sites in scripts (L660, L672, L781) + 1 in tests (L1974) = 4 sites to change if `who` is removed. 4 more sites index `[0]` only and are unaffected. Count from the grep in finding 13 (Grep tool, not a shell run; I2 should re-grep).
- (c) dated vs current: 58 -> 62 files read, 34 -> 38 files gaining values, 59 -> 61 checked (4404a28 vs ed9809b, finding 19). Those are differences of 4, 4 and 2, and the conclusions are unchanged.
- (a) misreads: 105 (04 Tests 5 and 05) + 107 (04 and 05) = 2 items with the same wrong expectation (findings 6, 7).

## Fit for a ~$3k account
This is a process and tooling item only. It changes no trading rule, price, screen or order path, and it has no effect on capital, assignment, dividends, taxes, commissions or liquidity. No brokerage connection.

## Open questions
1. (a) Proposed wording for R3/I1 to refine, one line placed once in each template. In build-plan.md, under `## Tests and checks` or `## Expected result`. In build-report.md, under `## Deviations from plan` or as a lead line near `## Test output`. For example: "`RULES BRANCH:` lists only remote branches not merged into HEAD (`git branch -r --no-merged HEAD`), so from this branch's own checkout it does not name this branch's (or its base branch's) rule change: expect `none` there, and check it from a checkout of origin/main (item 113)." Pin it with an exact-line, count-once test like `test_scratch_dir_template_line`. Should the check_pipeline.py docstring L232-234 also say "not merged into HEAD"? That is a small RULE_PATHS edit, and it would make the template and the script say the same thing.
2. (b) Remove or keep?
   - Remove: 4 unpack sites plus the L1976 `who == ""` assert change. `line == ""` still pins that a quoted waiver is not read. The `_build_waived` docstring at L657-658 needs a word change. A missed site fails loudly (finding 14), and the full suite exercises classify.
   - Keep: it is already documented in the docstring (L630). The request's "kept with a comment" condition may already be met, apart from naming the test that unpacks it.
   R2/R3 to decide. Removal is small, and it closes 105's A1 follow-up 3.
3. (c) Proposed sentence after L231: "These figures are as of 4404a28 (ed9809b gave 62 / 38 / 61, same conclusions); re-run the script in work/110/01-research.md (L36-147, `python3 -I -` from the repo root, without its `cd`) for current numbers, don't copy them (item 113)." Should the newer ed9809b figures be quoted at all? Quoting them dates the text again. Pin the new sentence by extending test_check_pipeline_docstring_records_110_no_go or adding a new test.
4. All three edits are RULE_PATHS changes (templates/, scripts/check_pipeline.py). The PR description should carry the rule text for the person's review, as 105/04 C4 did.
