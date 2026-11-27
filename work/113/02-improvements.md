# 02 Improvements - 113
## What past logs say
- logs/audit/2026-11-26-105.md L57-58 (07 point 3): "RULES BRANCH from the branch's own checkout reads `none` (`--no-merged HEAD`), as I3 found. 05's "not pushed" reason is wrong". Follow-up 2 (L68-70) is part (a) of this item. Follow-up 3 (L71-72) is part (b): "`who` in parse_request now has no reader in scripts/. It could be removed in a later item, together with the tests L1963 unpack." (That unpack is now at tests L1974.)
- work/105/02-improvements.md L55 (105's R2 hole): "`who` becomes dead in classify. Keep the 3-tuple ... but rename it to `_` at L760. Otherwise a later edit may read it again as if it were the rule." 105 kept the tuple. The docstring at scripts/check_pipeline.py L629-630 now says "who: kept for the tuple shape; no gate reads it since 105" (re-read 2026-11-26).
- logs/recurring-issues.md RI-009 (L108-115) occurrence 2, 2026-11-01 (032/06): "I2's in-repo `git checkout` restore wiped the uncommitted 031 edit". This matters for (a): telling 04/05 to "check from a checkout of origin/main" invites an in-repo checkout switch.
- RI-010 (L118-125): 049 built the `RULES BRANCH:` line. The template has had no field or text for it since then (templates/build-plan.md and templates/build-report.md re-read 2026-11-26: no RULES BRANCH text).
- logs/research/2026-11-25.md: 105's R2 logged `languages: N/A`. 107's and 110's R2s did full searches with German, Russian and Italian.
- I re-read the code on 2026-11-26 and R1's citations hold:
  - check_pipeline.py L226-231: the 110 figures "4404a28 ... 4 in 58 files ... 34 files would gain values ... 59 checked items".
  - L232-234: RULES BRANCH docstring, with no "not merged into HEAD".
  - L628-638: parse_request.
  - L657-660: `_build_waived` says "The anchor implies who == "person"", then has the `_, _, (steps, _, _)` unpack.
  - tests L1974-1976: the `who == ""` assert.
- The shipped build-report.md template is itself run through the checker:
  - tests L3787-3796 (S7) feeds the template to `_suite_item` and asserts the exact INCOMPLETE text built from its `Suite:` and `Scratch dir:` lines.
  - tests L3882-3887 asserts exactly one column-0 `Suite: <` line outside fences and comments.
  - So a new template line must not start with `Suite:` or `Scratch dir:`, and must not be a round heading.

## 3 ways FOR
1. **(a) Explain the mechanism and give a check that works from the branch's own checkout.**
   - Reasoning chain: `open_branches()` lists only `git branch -r --no-merged HEAD` (01 findings 1-2). From the branch's own checkout, neither the branch nor its base is listed (01 finding 5). 105 and 107 made the same wrong guess, in both 04 and 05 (01 findings 6-7). A line that only says "expect `none`" stops the wrong expectation but leaves 04/05 with no way to see the rule change itself.
   - A three-dot diff shows exactly that change without switching checkouts. git-diff: "`git diff A...B` is equivalent to `git diff $(git merge-base A B) B`", i.e. "the changes on the branch containing and up to the second <commit>, starting at a common ancestor of both" [https://git-scm.com/docs/git-diff].
   - Proposed line, placed once in each template (build-plan under `## Tests and checks`, build-report under `## Deviations from plan`): "`RULES BRANCH:` lists only remote branches not merged into HEAD (`git branch -r --no-merged HEAD`), so on this branch it never names this branch's or its base's rule change: expect `none` here. To see this branch's rule files, run `git diff --stat origin/main...HEAD -- .claude templates scripts/check_pipeline.py scripts/check_handoff.py` (item 113)."
   - Also add "not merged into HEAD" to the docstring at L232-234, so that the script and both templates say the same thing. Pin the line with the exact, count-once pattern from `test_scratch_dir_template_line` (tests L5655), parametrized over both templates.
2. **(b) Remove `who`, don't just keep documenting it.**
   - Reasoning chain: nothing reads it (01 finding 15). An equivalent-mutant check on it can't be written (100/01 finding 12). 105's R2 already warned that a dead field invites a later edit to "read it again as if it were the rule" (02-105 L55).
   - The change is small: 3 unpack sites in scripts (L660, L672, L781) and 1 in tests (L1974), for 4 in all (01 Numbers). A missed site fails loudly at unpack time. The Python reference says the iterable must have "the same number of items as there are targets" (01 finding 14). The full suite runs classify, so a miss can't stay hidden.
   - Steps:
     - Return `(steps, line)` and drop the `who` regex at L634.
     - Change the L1976 assert to `waived == [] and line == ""`. `line == ""` still pins that a quoted waiver is not read.
     - Reword L657-658 to "The anchor requires `(person, `".
     - Leave module docstring L15-20 alone: its `<who>` is the request.md field, not the variable (01 finding 17).
   - This closes 105 A1 follow-up 3 instead of carrying it forward.
3. **(c) Say "re-run", quote no new figures, and point to the script without line numbers.**
   - Reasoning chain: RI-001 (counts asserted, not measured) is the reason for this part. Quoting ed9809b's 62 / 38 / 61 would put a second dated set next to the first (R1 open question 3 raised this). Line numbers like "L36-147" go stale with any edit to work/110/01-research.md.
   - Proposed sentence after L231: "These figures are as of 4404a28 and go stale as work/ grows; for current numbers re-run the fenced script in work/110/01-research.md from the repo root (drop its first-line `cd`), don't copy these (item 113)."
   - Pin "re-run the fenced script in work/110/01-research.md" and "(item 113)" by extending `test_check_pipeline_docstring_records_110_no_go` (tests L5991-6002). That test already checks that work/110/03-handoff.md exists, so add the same check for work/110/01-research.md.

## 3 ways AGAINST
1. **All three edits are RULE_PATHS changes, so a small cleanup needs the person's review.**
   - Reasoning chain: RULE_PATHS includes `templates/` and `scripts/check_pipeline.py` (01 finding 3). After this change, main lists this branch as a RULES BRANCH. 105/04 C4 set the rule that rule wording goes to the person in the PR (01 finding 11).
   - The cost is review attention spent on wording, plus more template length. RI-010's history shows that each template line tends to turn into an unchecked duty.
   - Mitigation: the PR description carries a "Rule text for your review (item 113)" section with the two template lines and the docstring sentences verbatim. Keep each template addition to one line.
2. **Removing `who` could break an unmerged branch that still unpacks 3 items.**
   - Reasoning chain: any open remote branch that adds or keeps a `(x, y, z) = ...parse_request(...)[2]`-style unpack will raise a ValueError after it merges with this change (01 finding 14). Its own tests would pass until then.
   - I have no shell and could not list or grep remote branches, so "no open branch calls parse_request with 3 targets" is UNVERIFIED. The base branch daily-fixes/2026-11-25 is inside this branch already, so it is covered.
   - Guardrail: I2 runs `git grep -n parse_request $(git branch -r --no-merged HEAD --format='%(refname:short)')` (or the equivalent per branch) and records the result in 05. If any branch has a 3-target unpack, keep `who` instead: the docstring at L630 already meets the request's "kept with a comment" condition, so add the test's name to it.
3. **The template wording can be wrong in edge cases, and the obvious "check from origin/main" advice is risky.**
   - Reasoning chain, case 1: "never names" is not strictly true. If another clone pushes to the same remote branch, its tip is no longer reachable from HEAD and the branch is listed (01 finding 5, last bullet). So the line should say "normally `none`; if it names this branch, the remote has commits this checkout lacks: fetch and compare".
   - Case 2: "check from a checkout of origin/main" (R1's draft) invites `git checkout origin/main` inside the repo. RI-009 occurrence 2 recorded an in-repo checkout that wiped an uncommitted edit. Prefer the three-dot diff in FOR 1, or a separate worktree or scratch clone.
   - Case 3: the build-report template is fed to the checker by tests S7 (L3787) and the Suite-label pin (L3882). A line that starts with `Suite:` or `Scratch dir:`, or that looks like a round heading, would break them. The proposed line starts with a backtick, so it is safe, but I2 must run both tests.

## Findings by language
Random languages this cycle: none (N/A)
Languages: N/A (no new external claims). 113 is an EFFICIENCY item that changes only wording, template lines, one dead return value and tests inside this repo. It adds or changes no fee, market rule or statistic. The only outside facts are git command behaviour (`--no-merged`, `merge-base --is-ancestor`, three-dot `diff`) and Python unpacking. They are cited from git-scm.com and docs.python.org in 01 findings 1, 8 and 14 and in FOR 1 above.

| Language | For / against / holes found | Source (original URL) | Original quote | English translation |
|---|---|---|---|---|
| All 7 | N/A (no new external claims) | - | - | - |

## Holes to watch out for (summary)
- **Don't say "not pushed".** That was 05's wrong reason in 105. The reason is reachability: the branch's own remote ref and its base are both merged into HEAD.
- **Hedge "never".** If the remote ref is ahead of HEAD (another clone pushed), the branch is listed (AGAINST 3).
- **No in-repo checkout switch.** Use `git diff --stat origin/main...HEAD -- <RULE_PATHS>`, or a separate worktree (RI-009 occurrence 2).
- **Template line safety.** The line must not start with `Suite:` or `Scratch dir:` and must not be a `## Test output (round` heading. Run S7 (tests L3787) and `test_suite_label_in_template_and_i2_text` (L3882) as well as the new pin.
- **Pin each template line exactly once** (`splitlines().count(line) == 1`), parametrized over both templates. Mutation: delete the line from one template, and the test fails for that template only.
- **`who` removal sites.** L634 (regex), L637-638 (return), L660, L672, L781, tests L1974/L1976, and the L657-658 docstring. Re-grep `parse_request` and `who` before and after. The `[0]`-only callers (L760, L768, L1323, L2080) are unaffected. Don't touch the module docstring's `<who>` (it means the request.md field).
- **Open-branch callers.** Grep the `--no-merged` remote branches for 3-target unpacks before removing `who`. If any exist, keep `who` and name the test in the L630 comment (AGAINST 2).
- **(c) without new dated numbers or line numbers.** Point to "the fenced script in work/110/01-research.md" and say to drop the `cd /home/claude/cover-calls` first line (01 finding 20). Keep every existing string that `test_check_pipeline_docstring_records_110_no_go` pins.
- **Same-output check.** Apart from the new RULES BRANCH visibility from main, `check_pipeline.py` output on the branch should be identical before and after: no per-item, INCOMPLETE or LOG BATCH line changes.
- **PR rule text.** List both template lines and the two docstring edits verbatim for the person (AGAINST 1).

Log fields: 3 for / 3 against | languages: N/A
