# 01 Research brief - 062
## Question
How should `scripts/check_pipeline.py` find the files a `Scope: RESEARCH ONLY` item's commits change (on HEAD and on an open branch), how does item 053's `untracked_changes` already map commits to items, why did 061 pass both checks, and what should the person's waiver line look like? Internal tooling bug: every source is a repo file (path:line on branch daily-fixes/2026-11-13 unless stated). No web sources; no brokerage contact.

Limit of this brief: R1 had no shell in this run (Read/Grep/Glob only), so no `git show`/`git diff` on `origin/claude/project-thread-ltyppm` was run. Branch-side facts below are from `work/062/request.md` and the RI-007 entry and are marked UNVERIFIED; R3 must re-run them.

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
1. RESEARCH ONLY requires 01 02 03 07 only (`REQUIRED`), and nothing in `classify` looks at non-work files; scope is checked only against step files. [scripts/check_pipeline.py:96-98, 162-194]
2. `run-item.md` says RESEARCH ONLY stops after R3 and "Missing 04-06 files are expected"; it says nothing about code. [.claude/commands/run-item.md:8]
3. `r3-fact-checker.md` says only to write 07 for RESEARCH ONLY "because no I3 step will"; no rule against code. [.claude/agents/r3-fact-checker.md:22]
4. `i3-verifier.md` has no rule that a simulator/replay must use the bot's own pickers. [.claude/agents/i3-verifier.md:10-16]
5. Open-branch scope check (038): `open_branches` copies the branch's `work/<ID>/` files into a temp dir and calls `classify`; the temp dir has no git and no non-work files, so code the branch adds is invisible to it. [scripts/check_pipeline.py:340-357]
6. `open_branches` already has the branch's net change list: `changed(*paths)` = `git diff --name-only HEAD <merge-tree tree>` (fallback `HEAD...ref`), used for `work/`, `RECURRING`, `RULE_PATHS`. Calling `changed("ccbot/", "scripts/", "tests/", "config/")` gives the branch's code files with no new git plumbing. [scripts/check_pipeline.py:310-336]
7. BRANCH SKIPPED does not change the exit code by design ("exit code unchanged, since the branch is not part of HEAD"), and a test pins `code == 0`. [scripts/check_pipeline.py:47-49; tests/test_pipeline_check.py:263-271]
8. 053 maps commits to items by paths, not messages: walk `git rev-list --first-parent --reverse <cutoff>..HEAD`; per commit `git diff-tree -r --name-only --no-renames <c>^1 <c>`; items = IDs of files matching `STEP_FILE` (01-06 only; request.md and 07 excluded); code is covered if any of those items is open at `<c>^1` (`_open_at`: 07 absent, no `A1 result:`, or last FAIL). [scripts/check_pipeline.py:119-124, 366-410]
9. Because 053 judges a merge against its first parent as one unit, a PR merged into main is one unit containing every file of the PR. [scripts/check_pipeline.py:68-74, 391-396; tests/test_pipeline_check.py:661-674]
10. Why 053 would pass 061 once merged: the merge unit contains 061's 01/02/03 (step files of an item open at the first parent) plus the code, so it is "covered"; 053 never reads Scope. [scripts/check_pipeline.py:404-406, inferred from code; not run]
11. 053 only walks HEAD's first-parent chain; it never runs on open branches. [scripts/check_pipeline.py:391; docstring gap (b) line 78]
12. 053's CODE_PATHS includes `.claude/` and `templates/`; 062's request names only `ccbot/ scripts/ tests/ config/`. [scripts/check_pipeline.py:120; work/062/request.md:8,18]
13. Waiver parsing: `read_request` takes only the first `^Waived:` line (`re.search`), steps = two-digit groups from `[0-9 ,]+`, who = text after `(` up to `,` `:` or `)`, lowercased. The date is not checked for waivers (only FAST is checked with `FAST_BY_PERSON`). [scripts/check_pipeline.py:150-159, 144]
14. For RESEARCH ONLY, `need` = REQUIRED minus waived, so a `Waived: 04 05 06` line today changes nothing: 04-06 are not required anyway. [scripts/check_pipeline.py:171]
15. Bot rule (for the i3 text): `pick_expiry` returns the first expiry with DTE in range, else the nearest within `slack` days; `rules.py` calls it with `monthly_slack_days` and `pick_strike(..., cfg["tolerance"])`; config `monthly_dte` [30, 45], `target_delta` 0.275, `tolerance` [0.20, 0.35], `monthly_slack_days` 7. [ccbot/expiries.py:72-88; ccbot/rules.py:285-304; config/default.json:9-13]
16. `screen.py` uses the same pickers with the same config keys, so they are the bot's single source. [ccbot/screen.py:30,34]
17. 061 is on `origin/claude/project-thread-ltyppm`, tip c6638556e79a388d5388a756b7499607d85173a8. [.git/FETCH_HEAD:5]
18. work/061 does not exist on this branch's working tree (only on the PR branch). [Glob work/06*/* on daily-fixes/2026-11-13]
19. 061 is `Scope: RESEARCH ONLY` with 01, 02, 03, 07 and adds ccbot/realtest.py (570 lines), scripts/fetch_real_data.py (177), tests/test_realtest.py (111). UNVERIFIED (from work/062/request.md:11; R3: `git show origin/claude/project-thread-ltyppm:work/061/request.md`, `git diff --stat main...origin/claude/project-thread-ltyppm`)
20. `realtest._pick` picks the expiry nearest 37.5 DTE and accepts delta within ±0.12 of 0.275. UNVERIFIED (work/062/request.md:12; R3: `git show origin/claude/project-thread-ltyppm:ccbot/realtest.py`)
21. Whether 061's code and step files are in one commit or several, and what their messages say ("Item 061: ..."), is UNVERIFIED (R3: `git log --format='%h %s' --name-only main..origin/claude/project-thread-ltyppm`).
22. Commit messages are free text: the 2026-11-13 daily audit commit names "item 062" and "061" while changing logs/ and work/ for many items. [.git/logs/HEAD:7] Matching "Item 061:" in a message is the substring-classification pattern of RI-012. [logs/recurring-issues.md:137-140]

## Numbers used (show the math)
- Delta band 061 (UNVERIFIED): 0.275 ± 0.12 = [0.155, 0.395]; bot: [0.20, 0.35] (config/default.json:11). The 061 band is wider on both sides by 0.045.
- Window midpoint: (30 + 45) / 2 = 37.5 DTE, matching the request's 061 description; the bot takes the first expiry in [30, 45], else nearest within 7 days ([23, 52]).
- Sources count: 0 URLs (all sources are repo paths); R3 should confirm with `python3 scripts/check_handoff.py 062`.

## Fit for a ~$3k account
No trading change. The check keeps research-only simulators from reporting numbers that are not the bot's rule (request: median excess -1.8 vs -1.7 pts/yr, A2 6 vs 4 of 17; verdict unchanged; UNVERIFIED here, A1's probe). No brokerage contact.

## Proposed design (for R2/R3 to test, not verified by running)
A. One "unit" = what lands together, same as 053:
   - HEAD: each first-parent commit after `UNTRACKED_FROM` (`diff-tree <c>^1 <c>`; a merged PR is one unit). Reuse the 053 loop: for each unit, `items` from STEP_FILE; read each item's Scope at `<c>` (`git show <c>:work/<ID>/request.md`), not from the working tree.
   - Open branch: the whole branch = one unit (it will land as one merge commit; run-item.md:16): `changed("ccbot/", "scripts/", "tests/", "config/")` plus `touched` items, Scope from `git show <ref>:work/<ID>/request.md` (already fetched as `theirs`, line 342).
B. Flag rule: a unit with code under ccbot/ scripts/ tests/ config/ and a step file of a RESEARCH ONLY item, unless (i) that item's request has the person's waiver, or (ii) the same unit has an 04 or 05 of an open FULL/FAST item (the code is that item's). Open choice for R2: strict (flag any RESEARCH ONLY item in a code unit, ignore (ii)) is simpler and safer; (ii) avoids a false flag when a daily-fixes branch carries a FULL fix and a research item together.
C. Output: on HEAD, `<ID>: SKIPPED (RESEARCH ONLY: commits change <files> with no 04-06; needs FULL or Waived: 04 05 06 (person, <date>: ...), item 062)` and exit 1. On a branch, the same detail as `BRANCH SKIPPED: <ID> (<ref>: ...)`.
D. Waiver: `Waived: 04 05 06 (person, YYYY-MM-DD: <why>)`. Count it only when who == `person`, the steps include 04, 05 and 06, and a date is present (a regex like `FAST_BY_PERSON`, e.g. `^Waived:\s*[0-9 ,]*\b04\b[0-9 ,]*\(\s*person\s*,\s*\d{4}-\d{2}-\d{2}\s*:`). Any other who → still SKIPPED. Reuse `read_request`'s (steps, line, who) and add a date check, since today's waiver parse checks no date (finding 13).
E. Do not use commit messages to find items (finding 22); paths are what 053 already trusts and tests pin.
F. Fixtures (in the style of `_repo_with_open_branch`/`_branch_adds` and `_history`/`_commit`): (1) branch adds work/160 RESEARCH ONLY 01 02 03 07 + ccbot/x.py → `BRANCH SKIPPED: 160 (origin/...: RESEARCH ONLY ... ccbot/x.py ...)`; (2) same with `Waived: 04 05 06 (person, 2026-11-13: ...)` → no line; with `(I2, ...)` → still flagged; (3) HEAD commit after cutoff with 160's 01 + ccbot/x.py → `160: SKIPPED`, exit 1; (4) RESEARCH ONLY item with only work/ changes → not flagged; (5) mutation: drop the scope test → (1)/(3) fail.

## Open questions
1. Exit code for branches: request "Done looks like" says SKIPPED / BRANCH SKIPPED "and exit 1", but BRANCH SKIPPED is exit 0 by design and pinned by `test_open_branch_item_that_skips_steps_is_reported` (finding 7). Read as: exit 1 for the HEAD fixture only? The person/A1 should say.
2. Path set: request names ccbot/ scripts/ tests/ config/; 053 also counts .claude/ and templates/. Should a RESEARCH ONLY item that edits rules files also be flagged? (A rules edit by a research item would also skip I1-I3.)
3. Strict vs. "covered by a FULL item in the same unit" (design B).
4. HEAD commits before `UNTRACKED_FROM` (e.g. 023, 001) are not re-judged; acceptable since they are closed/LEGACY?
5. Only the first `Waived:` line is read (finding 13): an item with an earlier `Waived: 02 (...)` line would hide a later `Waived: 04 05 06` line. Require one combined line, or switch to `findall`?
6. Findings 19-21 (061's files, picker, commit layout) need R3 to run the git commands named there.
