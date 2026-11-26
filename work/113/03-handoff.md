# 03 Research hand-off - 113
Status: READY
## Recurring issues checked
Read logs/recurring-issues.md first (item 013). I checked this file against each open or ESCALATED entry and against the GUARDED entries this item touches:
- RI-001 (ESCALATED): no "always", "never" or "every" claim reaches the map without a count or a defined empty result. R2's "never names" is hedged to "normally `none`" (row R2 FOR1 proposed line). The open-branch check (step 0) has a defined result for 0 branches and for a check it cannot run. Its count is measured by I2, not asserted here.
- RI-014 (OPEN): step 0 and step 5 run git reads that a shallow or single-branch clone can hide (094/095). Step 0 records `--is-shallow-repository` and the fetch refspec first. Either one failing makes the open-branch check "not computed", which takes the keep-`who` path. It is never read as 0 branches (Missing inputs).
- RI-009 (GUARDED, this item's link): nothing in the map switches the repo checkout. The origin/main view uses a three-dot diff or a scratch worktree, never `git checkout origin/main` in the repo (occurrence 2).
- RI-010 (GUARDED, this item's link): each new template line and docstring sentence has its own pin test (steps 1, 3, 4). No duty is added that has no check.
- RI-002 (GUARDED): Missing inputs table filled. An uncomputable branch list or diff blocks with a named reason and never becomes "none" or a pass.
- RI-004/RI-005 (GUARDED): the Self-check re-derives every count. It also checks the template line against the rules that read the template (S7, the Suite pin, the round-heading pin).
- RI-006 (GUARDED): the orchestrator's check_handoff run checks the totals. The table has one row per claim.
- RI-012 (GUARDED): the new pins are exact-line (`splitlines().count(...) == 1`) or exact substrings of the normalised docstring. None is a loose substring guess.
- RI-015 (GUARDED): step 2's mutant M-b1 and the pin mutants run with PYTHONDONTWRITEBYTECODE=1 and a fresh PYTHONPYCACHEPREFIX (107).
- RI-007, RI-008, RI-011, RI-013: not touched. There is no RESEARCH ONLY code, no syntax newer than 3.10, no branch-diff logic change and no realtest change.

## Fact check
| Claim | Source | Result (VERIFIED/WRONG/UNSUPPORTED) | Fix |
|---|---|---|---|
| R1-1: `--no-merged [<commit>]` "Only list branches whose tips are not reachable from <commit> (HEAD if not specified)"; `-r` lists remote-tracking branches | https://git-scm.com/docs/git-branch (fetched 2026-11-26) | VERIFIED | - |
| R1-2: open_branches reads `git branch -r --no-merged HEAD --format=%(refname:short)`; RULES BRANCH built from `ruling = [... if b["rules"]]` | scripts/check_pipeline.py L1700, L1712, L2333-2334 | VERIFIED | - |
| R1-3: RULE_PATHS = .claude/, templates/, scripts/check_pipeline.py, scripts/check_handoff.py | check_pipeline.py L538-539 | VERIFIED | - |
| R1-4: docstring L232-234 does not say "not merged into HEAD" or that the own branch is left out | check_pipeline.py L232-234 | VERIFIED | - |
| R1-5: from the branch's own checkout neither the branch's remote ref nor its base is listed; listed only if the remote ref has commits HEAD lacks | derived from R1-1 + L1700; 105/06 L107, 105/07 L5 | fixed | The mechanism holds. "The base daily-fixes/2026-11-25 is merged into HEAD" cannot be confirmed without a shell, so it becomes I2 step 0c (`git merge-base --is-ancestor origin/daily-fixes/2026-11-25 HEAD`, expect exit 0) |
| R1-6: 105/04 Tests 5 expected RULES BRANCH to name check_pipeline.py; 105/06 shows `RULES BRANCH: none`; from origin/main 1d0de33 it names origin/daily-fixes/2026-11-25; 05's "not pushed" reason wrong | work/105/04 L110, L165; 105/06 L107; 105/07 L5; logs/audit/2026-11-26-105.md L57-58, L68-70 | VERIFIED | - |
| R1-7: 107 same misread (04 L80, 05 L101, 07 L15) | work/107/04-build-plan.md L80; 05-build-report.md L101; 07-audit-task.md L15 | VERIFIED | - |
| R1-8: `merge-base --is-ancestor` "exit with status 0 if true, or with status 1 if not" | https://git-scm.com/docs/git-merge-base (fetched 2026-11-26) | VERIFIED | - (the page adds that errors are a non-zero status other than 1; used in Missing inputs) |
| R1-9: templates have no RULES BRANCH text; build-plan `## Tests and checks` L5, `## Expected result` L12; build-report `## Deviations from plan` L14 | templates/build-plan.md, templates/build-report.md | VERIFIED | - |
| R1-10: pin pattern `test_scratch_dir_template_line` (`splitlines().count(...) == 1`, parametrized) and `test_round_heading_template_lines` (`.count(line) == 1`) | tests/test_pipeline_check.py L5650-5658, L5220-5238 | VERIFIED | - |
| R1-11: editing templates/ and check_pipeline.py is a RULE_PATHS change and needs the person's OK in PR review (105/04 C4) | work/105/04-build-plan.md L10; check_pipeline.py L539 | VERIFIED | - |
| R1-12: parse_request returns `(scope, date, (steps, first Waived line, who))`; who regex; docstring "who: kept for the tuple shape; no gate reads it since 105" | check_pipeline.py L628-638 | VERIFIED | - |
| R1-13: callers: 3-tuple unpacks at L660, L672, L781; `[0]` only at L760, L768, L1323, L2080; tests L1974/L1976; no other script | Grep `parse_request` over the repo (logs/ excluded), 2026-11-26 | VERIFIED | - |
| R1-14: a site left on 3 targets "raises at runtime (ValueError ... UNVERIFIED)" and does not silently mis-assign | https://docs.python.org/3/reference/simple_stmts.html (fetched 2026-11-26) | fixed | The page says only "must be an iterable with the same number of items as there are targets". It names no exception and does not say it raises. The claim is replaced by a measured check: step 2 mutant M-b1 (L672 left at 3 targets) must make the suite fail, and I2 records the count |
| R1-15: no gate reads who; `_person_dated` is the single check; the anchor implies who == "person" (equivalent mutant) | check_pipeline.py L641-650, L653-661; work/100/01-research.md L23 | VERIFIED | - |
| R1-16: 105 kept who (105/04 L40, 105/05 L35); A1 follow-up 3 "could be removed ... together with the tests L1963 unpack" | work/105/04 L40; 105/05 L35; logs/audit/2026-11-26-105.md L71-72 | VERIFIED | - |
| R1-17: text naming who: `_build_waived` docstring L657-658; module docstring L15-20 `<who>` is the request.md field | check_pipeline.py L15-20, L657-658 | VERIFIED | - |
| R1-18: docstring 110 figures "measured at 4404a28 ... 4 in 58 files ... 34 files ... 0 per-file maxes ... 59 checked items" | check_pipeline.py L226-231 | VERIFIED | - |
| R1-19: A1 re-ran at ed9809b: 62 files read, 38 gaining values, 61 checked, same conclusions; follow-up "should re-run the script rather than copy them" | logs/audit/2026-11-25-110.md L32-36, L67-69 | VERIFIED | - |
| R1-20: script is the fenced block in work/110/01-research.md, first line `cd /home/claude/cover-calls && python3 -I - <<'EOF'` | work/110/01-research.md L36-37, L146-149 | VERIFIED | - |
| R1-21: `test_check_pipeline_docstring_records_110_no_go` pins exactly the listed strings; adding a sentence leaves it green | tests/test_pipeline_check.py L5991-6002 | VERIFIED | - |
| R1-22: `_STATS_PARTS` comment states a conclusion, not a figure | check_pipeline.py L473-475 | VERIFIED | - |
| R1 Numbers (b): 3 script unpack sites + 1 test = 4; 4 `[0]`-only callers unaffected | Grep (row R1-13) | VERIFIED | - |
| R1 Numbers (c): 58 to 62, 34 to 38, 59 to 61 (differences 4, 4, 2) | logs/audit/2026-11-25-110.md L24-36 | VERIFIED | - (62-58=4, 38-34=4, 61-59=2) |
| R1 Numbers (a): 2 items (105, 107) misread RULES BRANCH | rows R1-6, R1-7 | VERIFIED | - |
| R1 OQ1 draft wording: "check it from a checkout of origin/main" | RI-009 occurrence 2 (recurring-issues.md L115) | fixed | Replaced by the three-dot diff (or a scratch worktree), never an in-repo checkout switch (text T-RB) |
| R1 OQ3 draft sentence quoting ed9809b 62/38/61 and "L36-147" | R2 FOR3 reasoning; work/110/01-research.md | fixed | No new dated figures and no line numbers. Uses R2's wording, with the `cd` part named exactly (text D-110) |
| R2 past logs: audit 105 L57-58 quote and follow-ups 2, 3 (L68-72) | logs/audit/2026-11-26-105.md L57-58, L68-72 | VERIFIED | - |
| R2 past logs: 105's R2 hole "Keep the 3-tuple ... rename it to `_` at L760 ... read it again as if it were the rule" | work/105/02-improvements.md L55 | VERIFIED | - |
| R2 past logs: RI-009 occurrence 2 "I2's in-repo `git checkout` restore wiped the uncommitted 031 edit" | logs/recurring-issues.md L115 | VERIFIED | - |
| R2 past logs: RI-010 / 049 built RULES BRANCH; templates have no field for it | logs/recurring-issues.md L123; templates (row R1-9) | VERIFIED | - |
| R2 past logs: 105 R2 `languages: N/A`; 107 and 110 full searches incl. German, Russian, Italian | logs/research/2026-11-25.md L7, L10, L14 | VERIFIED | - |
| R2 past logs: shipped build-report.md is fed to the checker (S7 L3787-3796) and has exactly one column-0 `Suite: <` line (L3882-3887) | tests/test_pipeline_check.py L3787-3796, L3882-3889 | VERIFIED | - |
| R2 FOR1: git diff A...B "is equivalent to git diff $(git merge-base A B) B", "changes on the branch containing and up to the second <commit>, starting at a common ancestor" | https://git-scm.com/docs/git-diff (fetched 2026-11-26) | VERIFIED | - |
| R2 FOR1 proposed line: "on this branch it never names this branch's or its base's rule change" | rows R1-1, R1-5; R2 AGAINST3 case 1 | fixed | "never" is not true when the remote is ahead of HEAD. The wording becomes "normally reads `none`" and says what a non-none result means (text T-RB) |
| R2 FOR1 command `git diff --stat origin/main...HEAD -- <RULE_PATHS>` "to see this branch's rule files" | git-diff doc (row above) | fixed | It shows every change since merge-base(origin/main, HEAD), so it also shows the unmerged base branch's rule files. The text now says "this branch and its unmerged base" |
| R2 FOR2: removal steps (return 2-tuple, drop L634 regex, L1976 assert to `waived == [] and line == ""`, reword L657-658, leave L15-20) | check_pipeline.py L628-661; tests L1974-1976 | VERIFIED | - |
| R2 FOR3: sentence after L231, no new figures; pin by extending the 110 test and checking work/110/01-research.md exists | check_pipeline.py L226-231; tests L5991-6002 | VERIFIED | - (pin strings set in map step 4) |
| R2 AGAINST1: all edits are RULE_PATHS; PR carries "Rule text for your review (item 113)" | rows R1-3, R1-11 | VERIFIED | - |
| R2 AGAINST2: "no open branch calls parse_request with 3 targets" UNVERIFIED; guardrail `git grep -n parse_request $(git branch -r --no-merged HEAD ...)` | R2's own UNVERIFIED mark; git grep with no tree argument searches the working tree | fixed | Becomes I2 pre-build step 0 with a recorded count. If the branch list is empty, the grep is NOT run, because a bare `git grep` would search the working tree and look like a branch result. If the list can't be computed, `who` is kept (step 2-alt) |
| R2 AGAINST3 case 1: listed if another clone pushed to the same remote branch | row R1-5, last bullet; R1-1 | VERIFIED | - |
| R2 AGAINST3 case 2: R1's "checkout of origin/main" invites an in-repo switch (RI-009 occ. 2) | recurring-issues.md L115 | VERIFIED | - |
| R2 AGAINST3 case 3: new build-report line must not start with `Suite:` / `Scratch dir:` or be a round heading | tests L3787-3796, L3882-3889, L5230-5238 | VERIFIED | - |
| R2 Holes "same-output check": check_pipeline output on the branch identical before/after except item 113's own lines | no logic change in the map (docstring, templates, one dead return value) | VERIFIED | - (measured in step 5) |
**Totals:** 44 rows checked → **37 VERIFIED as-is**, **7 fixed**, **0 removed**
(fixed = claim kept with a correction or new source; removed = claim dropped with nothing in its place)
## Removed claims
None. Three claims that were UNVERIFIED in R1/R2 are now checks, not facts:
- R1-14's "ValueError" is gone. Mutant M-b1 in step 2 replaces it.
- R2 AGAINST2's open-branch claim is now I2 step 0, measured before any edit.
- R1-5's "base is in HEAD" is now I2 step 0c.

## Implementation map
All edits are RULE_PATHS (templates/, scripts/check_pipeline.py). The PR description must carry a section "Rule text for your review (item 113)". It holds T-RB, D-RB, D-110 and the step 2 or 2-alt docstring text word for word, plus the step 0 result (step 6).

Exact texts. I1 copies them and I2 pastes them unchanged. Each fenced block is one physical line.

T-RB: the template line for step 1. It is the same line in both templates and starts with a backtick:
```
`RULES BRANCH:` lists only remote branches not merged into HEAD (`git branch -r --no-merged HEAD`), so on this branch's own checkout it normally reads `none` and does not name this branch's or its base branch's rule change; if it does name this branch, the remote has commits this checkout lacks (fetch and compare). To see the rule files this branch and its unmerged base change, run `git diff --stat origin/main...HEAD -- .claude templates scripts/check_pipeline.py scripts/check_handoff.py`; never switch this checkout to origin/main (item 113).
```
D-RB: the docstring sentence for step 3. Append it after "Listed, not an error." at L234, wrapped to the docstring's 18-space indent:
```
Only remote branches not merged into HEAD are read (`git branch -r --no-merged HEAD`), so from a branch's own checkout that branch and its merged base are not listed and the line normally reads none (item 113).
```
D-110: the docstring sentence for step 4. Insert it after L231 ("... never to _STATS (the I2 field refuses it).") at the same indent:
```
These figures are as of 4404a28 and go stale as work/ grows; for current numbers re-run the fenced script in work/110/01-research.md from the repo root (drop the `cd /home/claude/cover-calls &&` on its first line), don't copy these (item 113).
```

| Step | Change | Inputs | Outputs | How we check it | Feasibility |
|---|---|---|---|---|---|
| 0 (I2, before any edit; R2 AGAINST2) | Pre-build check, no file change. 0a: confirm a full clone: `git rev-parse --is-shallow-repository` prints false and `git config --get-all remote.origin.fetch` includes `refs/heads/*`. Then run `git fetch origin` and `git branch -r --no-merged HEAD --format='%(refname:short)'`, dropping `*/HEAD`. 0b: only if that list has n >= 1 refs, run `git grep -n parse_request <each ref> -- scripts tests` and read each hit. Count k = hits that unpack element [2] into 3 targets (or index [2][2]). If n = 0, do not run git grep: a bare `git grep` searches the working tree. 0c: run `git merge-base --is-ancestor origin/daily-fixes/2026-11-25 HEAD` and record the exit code | full clone of origin | 05 section "Pre-build check (item 113)": the 0a outputs, the ref list and n, k with each hit's ref:path:line, and the 0c exit code | Decision rule: k = 0 with 0a/0b computed means step 2 (remove). k >= 1, or 0a/0b not computable, means step 2-alt (keep). 0c exit 0 means the base is in HEAD. Exit 1 means 05 says the base is not in HEAD; T-RB is unchanged because its "base" clause still holds. Any other exit means "not computed" with the error text | I2 measures n and k on the build day (R3 has no shell). Defined empty result: n = 0 gives "0 open branches; grep not run", k = 0 |
| 1 (a) templates | Add T-RB once: in templates/build-plan.md on the line after `## Tests and checks`; in templates/build-report.md on the line after `## Deviations from plan` | T-RB | 2 template lines | New `test_rules_branch_template_line`, parametrized over both files: `splitlines().count(RB_TEMPLATE_LINE) == 1`, plus `cp.STRAY_RUN_HEADING.match(line) is None` and `not line.startswith(("Suite:", "Scratch dir:"))`. These stay green: S7 `test_unfilled_template_suite_line_is_incomplete`, `test_suite_label_in_template_and_i2_text`, `test_scratch_dir_template_line`, `test_round_heading_template_lines`. Mutant M-a1: delete the line from build-plan.md only; exactly the build-plan case fails | – |
| 2 (b) remove `who`, only if step 0 says remove | parse_request: drop L634 and return `(steps, waived.group(0).strip())` or `([], "")`. Docstring L629-630 becomes "(scope, date, (waived steps, first Waived: line)) from request.md text. `who` removed: no gate read it since 105 (item 113)." Unpacks: L660 `_, _, (steps, _)`, L672 `scope, _, (waived, _)`, L781 `scope, opened, (waived, waived_line)`. `_build_waived` docstring L657-658: "The anchor implies who == "person"." becomes "The anchor requires `(person, `.". Tests: L1974 `scope, _, (waived, line) = ...`, L1976 `assert waived == [] and line == ""`. Module docstring L15-20 unchanged | check_pipeline.py, tests | 2-tuple inner value | New `test_parse_request_inner_is_steps_and_line`: `cp.parse_request("Scope: FULL\nWaived: 03 06 (person, 2026-11-26: x)\n")[2] == (["03", "06"], "Waived: 03 06 (person, 2026-11-26: x)")`, and `[2]` of a text with no Waived line `== ([], "")`. Re-grep after the edit: `parse_request` shows no 3-target inner unpack, and `\bwho\b` in check_pipeline.py matches no code line (only docstring prose: L15, L16, L20, L645, the L657 "proof of who wrote it", and the new L629-630 wording). Mutant M-b1: leave L672 at `(waived, _, _)`; the suite must fail, and I2 records the count. Full suite green | – |
| 2-alt (b) keep `who`, only if step 0 says keep | Docstring L630 becomes "who: kept for the tuple shape; no gate reads it since 105. tests/test_pipeline_check.py::test_inbox_quoted_scope_and_waiver_are_not_read unpacks it; removal deferred (item 113: <ref> unpacks 3, or open-branch check not computed)." | step 0 result | docstring line | Test: normalised `cp.parse_request.__doc__` contains "removal deferred (item 113" and "test_inbox_quoted_scope_and_waiver_are_not_read". Full suite green | – |
| 3 (a) docstring | Append D-RB after "Listed, not an error." (L234) | D-RB | docstring sentence | New `test_rules_branch_docstring_names_no_merged`: the whitespace-normalised module docstring contains "so from a branch's own checkout that branch and its merged base are not listed and the line normally reads none (item 113)" and "(`git branch -r --no-merged HEAD`)". Mutant M-3: remove the sentence; the test fails | – |
| 4 (c) docstring | Insert D-110 after L231 | D-110 | docstring sentence | Extend `test_check_pipeline_docstring_records_110_no_go` with asserts that "re-run the fenced script in work/110/01-research.md" and "don't copy these (item 113)" are in doc, and that `(REPO / "work/110/01-research.md").is_file()`. All existing asserts stay unchanged ("0 per-file maxes" etc. remain because the figures remain). Mutant M-4: drop "don't copy these"; the test fails | – |
| 5 whole-output check | none | `python3 scripts/check_pipeline.py` with the base script and with the head script, in a full clone | whole-output diff in 05 | The diff is identical except for lines naming item 113. `RULES BRANCH:` on the branch checkout is the same before and after (expected `none`, unless step 0 listed refs that change rule paths). Exit codes are equal. Full-suite last line pasted as `Suite:`. Optional for A1: from a scratch worktree of origin/main (never an in-repo checkout), RULES BRANCH names this branch with templates/build-plan.md, templates/build-report.md, scripts/check_pipeline.py | – |
| 6 PR text | PR description section "Rule text for your review (item 113)": T-RB, D-RB, D-110, the step 2 or 2-alt docstring text, and the step 0 result (n, k) | 05 | PR body | A1 reads the PR body. It holds the texts word for word and the step 0 numbers | – |

## Missing inputs
| Input (where it enters) | When absent | Reason code / report text |
|---|---|---|
| Remote branch list (step 0a, `git branch -r --no-merged HEAD`) | command fails, or the clone is shallow or single-branch (094/095) | 05: "open-branch check not computed (<git error / shallow / single-branch>)". Take step 2-alt (keep `who`). Never "0 branches" |
| Remote branch list is empty (step 0a) | n = 0 | 05: "0 open branches; grep not run". k = 0, so step 2 proceeds. No bare `git grep` |
| `git grep` on a ref (step 0b) | exit code other than 0 or 1 (1 = no match) | 05: "<ref>: grep not computed (<error>)". Take step 2-alt |
| origin/daily-fixes/2026-11-25 ref (step 0c) | ref missing, or exit other than 0/1 | 05: "base ancestry not computed (<error>)". T-RB is unchanged, because its "base" clause holds either way. No pass is claimed |
| origin/main ref for T-RB's three-dot diff (whoever runs it later) | missing, or no merge base (`git diff` errors) | The command error is the result: "rule-file diff not computed (<error>)", never "no rule change" |
| Waived line in request.md (parse_request, step 2) | no Waived line | inner value `([], "")`, pinned by step 2's new test. Same as today apart from dropping the third "" |

## Self-check
Re-derive every numeric threshold in the map from that step's "How we check it" formula, and run every worked example against the trigger of the rule it shows. Show the arithmetic.
| Rule | Check formula | Arithmetic | Result |
|---|---|---|---|
| Step 2 unpack sites | count of 3-target inner unpacks from Grep `parse_request` | scripts L660, L672, L781 = 3; tests L1974 = 1; 3 + 1 = 4. `[0]`-only callers L760, L768, L1323, L2080 = 4, unaffected | 4 sites to edit, matches R1/R2 |
| Step 2 `who` hits | Grep `\bwho\b` in check_pipeline.py, today: L15, L16, L20, L629, L630, L634, L638, L645, L657, L658 = 10 | Code lines L634 and L638 are removed or rewritten (2). L658 `who == "person"` is reworded (1). L629-630 are rewritten (they keep "`who` removed"). L15, L16, L20, L645, L657 are prose that stays (5) | after the edit: 0 code hits; prose hits = 5 kept + the new L629-630 wording. The check is "no code line", not a fixed total |
| Step 1 pin | `splitlines().count(RB_TEMPLATE_LINE) == 1` per template | T-RB added once to each of 2 files gives 1 and 1. M-a1 removes it from build-plan: 0 ≠ 1, so only that case fails; build-report stays 1 | holds |
| Step 1 vs S7 / Suite pin / round-heading pin (worked example: the template line against the rules that read the template) | S7 takes the first line with `startswith("Suite:")` and the first with `startswith("Scratch dir:")`; L3887 counts column-0 `Suite: <` lines outside fences = 1; round-heading pin needs `STRAY_RUN_HEADING.match(line) is None` | T-RB starts with a backtick, not "Suite:", "Scratch dir:", "#" or "Round", so S7's picked lines and the count of 1 are unchanged | holds |
| Step 1 text vs the rule it states | RULES BRANCH = refs from `--no-merged HEAD` with rule paths | 105, branch checkout: 105/06 L107 `RULES BRANCH: none` (matches "normally none"). origin/main 1d0de33: names origin/daily-fixes/2026-11-25 (105/07 L5), because from main the branch is not merged, so it is listed | the text agrees with both observed runs |
| Step 4 figures kept | existing test asserts | D-110 is inserted and nothing is deleted, so all 6 existing asserts are unchanged; 2 new substrings and 1 is_file are added | holds |
| R1 Numbers (c) | ed9809b minus 4404a28 | 62 − 58 = 4; 38 − 34 = 4; 61 − 59 = 2 | matches R1. Not quoted in D-110, on purpose |
| Step 0 decision | remove iff k = 0 and n, k computed | n = 0: k = 0, remove. n >= 1 and k = 0: remove. k >= 1: keep. Not computed: keep | every case has a named result |
| Totals | 37 + 7 + 0 | = 44 = table rows | holds (the orchestrator runs check_handoff) |
`check_handoff output (run by the orchestrator 2026-11-26 23:25 UTC, exit 0; must say PASS):`
```
sources count (unique URLs in 01-research.md): 3
fact-check rows: 44
totals line: 44 rows -> 37 as-is, 7 fixed, 0 removed
PASS
```
