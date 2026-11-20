# 01 Research brief - 070
## Question
How should `scripts/check_pipeline.py` check that the item-067 field `## Real-data effect (diff_reports output, pasted)` in 05 and 06 is filled? The check applies only when an item's commits change realtest's decision path. It must flag the gap as INCOMPLETE from item 070 on and leave items 001-069 alone. Which existing parts of check_pipeline can it reuse, and which edge cases must the fixtures cover? (request.md L8, L23)

Branch: daily-fixes/2026-11-17, built on PR #30's daily-fixes/2026-11-16 (RULES BRANCH). Repo sources are cited as file:line on this tree. R1 had no shell, so every git or run result below is a reading of the code, not a measured run.

## Findings (one claim per line, each with [source URL] or UNVERIFIED)
### What exists today
- F1. 067 added the same section to both templates. build-report.md has it at L9-10, and verification.md has it at L7-8, where the comment also asks I3 to compare its TOTAL line with 05's. The trigger is the comment's wording: "Required when the item changes ccbot/realtest.py or a module/file it reads (list in work/067/03-handoff.md)". The fallback is `not required (<git diff --stat file list>)`. [templates/build-report.md:9-10; templates/verification.md:7-8]
- F2. Today nothing checks that field. 04 says so (L123), and so do 06 (L172), the 067 audit (logs/audit/2026-11-16-067.md:55) and RI-010 (logs/recurring-issues.md:119). This is the RI-010 root cause: a duty that only the text asks for, with no script to check it. [work/067/04-build-plan.md:123; work/067/06-verification.md:172; logs/recurring-issues.md:118-120]
- F3. diff_reports.py always ends its stdout with one line of the fixed form `TOTAL: files <n>, only-before <n>, only-after <n>, not compared <n>, json changes <n>, csv rows changed <n> added <n> removed <n>, columns changed <n>`, followed by `no change` when nothing moved. On an error it prints only to stderr and exits 2, so it gives no TOTAL line. [scripts/diff_reports.py:289-295, 304-319; work/067/04-build-plan.md:25]
- F4. So a TOTAL line inside the section shows that diff_reports was actually run and its output pasted. A blank section, the template comment alone, "TBD", "see 05" or `not required (...)` has no such line. With this rule, no separate placeholder list is needed. (Derived from F1 and F3.) [scripts/diff_reports.py:289-292; templates/build-report.md:10]
- F5. The TOTAL test has to be limited to the section. 067/05 has a second TOTAL line, from the self-diff of reports/real, in `## Test output` (L116), before its Real-data section (L144, TOTAL at L377). A file-wide search would accept a 05 whose Real-data section is empty. [work/067/05-build-report.md:116, 144, 377]
- F6. Both trigger items built so far fill the field in this shape. 068 changed ccbot/realtest.py: its 05 section is at L94 with TOTAL at L107, and its 06 section is at L85 with TOTAL at L134. 067's 06 writes `not required for 067's own change (git diff --stat ...)`, and 067 changed no trigger file. [work/068/05-build-report.md:94, 107; work/068/06-verification.md:85, 134; work/067/06-verification.md:125]

### realtest's decision path (the trigger list)
- F7. realtest imports, inside ccbot, only `costs`, `expiries`, `config.load_config` and `pricing`. [ccbot/realtest.py:54-57]
- F8. costs.py and pricing.py import only `math`. config.py imports copy, json and pathlib. expiries.py imports stdlib modules and pandas. None of them imports another ccbot module, so the transitive ccbot set is the same 4 modules. [ccbot/costs.py:2; ccbot/pricing.py:2; ccbot/config.py:2-4; ccbot/expiries.py:2-8]
- F9. realtest reads config/default.json (CONFIG_PATH, used at L278 and L866) and config/tickers.json (L61, L135-137). expiries reads config/holidays.json (L10, L27). load_config reads only the path it is given, merged over the DEFAULTS defined in config.py itself. [ccbot/realtest.py:60-61, 135-137, 278, 866; ccbot/expiries.py:10, 27; ccbot/config.py:104-114]
- F10. config/ holds 10 files. realtest reads 3 of them. The other 7 (paper, practice, weekly, stagger, dip_base, dip_reserve, quality) are not read on its path. [Glob config/*; F9]
- F11. realtest's default `--data` is data/real. 067/03 step 3 put data/real/ in the trigger, but 03's fact-check row and 04's shortened text list only the modules and the 3 config files plus "the --data dir". [ccbot/realtest.py:857; work/067/03-handoff.md:52, 80; work/067/04-build-plan.md:5]
- F12. The request's "config/" is broader than the files realtest reads (F10). Each forced trigger costs a full before/after realtest run, about 11 min per side (A1's runs: 11m19s and 11m22s), and the `not required` fallback would not be accepted. [work/067/03-handoff.md:47, 116; request.md:23]
- F13. If ccbot/realtest.py gains a new ccbot import, a hand-written trigger list goes stale. The same shape happened under RI-002 (a hand list `TICKER_FIELDS`, later read from the file by 046). `ast.parse` plus `ast.ImportFrom` (`module`, `names`, `level`; level 0 = absolute, `from . import x` has module None) can list realtest's relative imports in a test or at run time. [logs/recurring-issues.md:34-36; https://docs.python.org/3/library/ast.html]

### How check_pipeline works now (what can be reused)
- F14. INCOMPLETE comes from `incomplete(item_dir, logs)`. It returns a list of missing duties and has an item-ID cutoff (`CHECKLIST_FROM = 41`, `LOG_CHECK_FROM = 45`, compared with `int(item_dir.name)`). main() joins the list into `INCOMPLETE: <ID> (<a>; <b>)`, and any entry makes the exit code 1. [scripts/check_pipeline.py:134-140, 275-295, 613-615, 643, 654]
- F15. An ID cutoff constant with a comment ("checked from this ID on; earlier items are not re-checked") is the house pattern for "from 070 on". A `WHOLE_DIFF_FROM = 70` next to CHECKLIST_FROM/LOG_CHECK_FROM leaves 001-069 unaffected by construction. [scripts/check_pipeline.py:134-140]
- F16. Commit-to-item attribution exists already. `_walk(cutoff)` lists HEAD's first-parent commits after UNTRACKED_FROM, each with its files from `git diff-tree -r --name-only --no-renames <c>^1 <c>`, and `STEP_FILE` maps a path to its item ID (01-06 only, never 07). [scripts/check_pipeline.py:150, 158-159, 469-488, 508]
- F17. In `_walk`, a merge commit is one unit judged against its first parent (053 docstring). PRs must land as merge commits (run-item.md L16). [scripts/check_pipeline.py:73, 79; .claude/commands/run-item.md:16]
- F18. Consequence (derived): if 070 reuses `_walk` as is, a PR merged into main that carries one item changing realtest.py and another that doesn't puts both items' step files and realtest.py in one unit. The second item would become INCOMPLETE on main (false positive). Walking non-merge commits (`git rev-list --no-merges <cutoff>..HEAD`, each against its own parent) keeps each item's own commits after the merge. This works because run-item requires "I2 commits each code change together with its 05 change". UNVERIFIED until a fixture shows it (see Numbers, check 6). [scripts/check_pipeline.py:481-487; .claude/commands/run-item.md:16]
- F19. Known gap that would carry over: a trigger file committed on a branch with no step file is attributed to no item. 053's gap (b) says the same thing ("commit code together with your 05"). On HEAD's own first-parent chain, 053 already flags such a commit as UNTRACKED CHANGE. [scripts/check_pipeline.py:77-79, 505-510]
- F20. Without git, or when the cutoff can't be used, the existing checks print `not checked (no git)` or `not checked (see UNTRACKED CHANGE)` and never invent a pass or a fail. Most fixtures in tests/test_pipeline_check.py run without git, and their 05/06 bodies are `x\n` (`_item`). So the new check has to say "not checked" without git, not report INCOMPLETE, or those fixtures break. [scripts/check_pipeline.py:494-499, 522-526, 648-650; tests/test_pipeline_check.py:19-41]
- F21. The git fixtures already use IDs ≥ 070 (150-154) and commit `ccbot/x.py`, `scripts/y.py` and `config/x.json`. An exact trigger list (F7-F9) leaves them untouched. A trigger of all of `config/` would bring `config/x.json` into scope for items 150/151. [tests/test_pipeline_check.py:638-645, 670-680, 684-694, 775-785, 807-813]
- F22. `test_repo_pipeline_has_no_skipped_items` runs check_pipeline on a HEAD worktree of the real repo and asserts exit 0. With the ID cutoff, only 070 and later real items are checked, and 070 changes scripts/ and tests/ only (no trigger file). [tests/test_pipeline_check.py:156-163]
- F23. scripts/check_pipeline.py is in RULE_PATHS, so this branch is a RULES BRANCH. The check's docstring lists every report line with its item. 070 adds its entry there, and the PR needs the person's OK. [scripts/check_pipeline.py:20-110, 146]

### Proposed check (for R2/R3 to test, not decided)
- P1. For each item with ID ≥ WHOLE_DIFF_FROM: collect the files of every non-merge commit after UNTRACKED_FROM that contains one of the item's 01-06 step files. If any of them matches TRIGGER, then for each of 05 and 06 that exists, take the text from `## Real-data effect (diff_reports output, pasted)` to the next `## ` heading, drop `<!-- ... -->` comments, and require a line matching the F3 TOTAL format. Otherwise add `05 Real-data effect has no diff_reports TOTAL line (<sha7> changes <files>; item 070)` (06 the same). [design from F3-F5, F14-F18]
- P2. TRIGGER (exact, from F7-F9): `ccbot/realtest.py`, `ccbot/costs.py`, `ccbot/expiries.py`, `ccbot/config.py`, `ccbot/pricing.py`, `config/default.json`, `config/tickers.json`, `config/holidays.json`; data/real/ is an open question (F11). Guardrail test: the set of ccbot modules imported by realtest.py (ast, transitively) and the `"config" / "<name>"` files they name ⊆ TRIGGER. [F7-F9, F13]
- P3. An item that has 05 but no 06 yet is checked on 05 only. An item whose commits touch no trigger gets no line, whatever its field says (request "non-trigger change → no line"). [request.md:23]

## Numbers used (show the math)
- Trigger list: 1 (realtest.py) + 4 imported modules (F7) + 3 config files (F9) = 8 paths, plus data/real/ if R2/R3 take F11.
- config/ breadth: 10 files − 3 read = 7 files that would force a realtest run under a whole-`config/` trigger (F10).
- Cost of one forced trigger: about 2 × 11 min = about 22 min (11m19s + 11m22s = 22m41s, work/067/03-handoff.md:116).
- Items affected today: IDs ≥ 70 among real items = 070 only (069 is in progress elsewhere and is below the cutoff). 070 changes no TRIGGER path, so it gets 0 new lines (F22).
- Fixture cases (request L23 plus the edge cases found here):
  1. Filled (TOTAL line in the section of 05 and 06) → no line.
  2. Section has the template comment only → INCOMPLETE naming 05 and 06.
  3. Non-trigger change (`ccbot/x.py`) with an empty field → no line.
  4. `not required (...)` on a trigger change → INCOMPLETE.
  5. TOTAL only in `## Test output` (the 067/05 L116 shape) → INCOMPLETE.
  6. One PR merge carrying item A (realtest.py) and item B (no trigger), both with empty fields → only A is flagged (F18).
  7. Item 069 with a trigger change and an empty field → no line (cutoff).
  8. No git → "not checked", exit unchanged (F20).
  9. ast guardrail test (P2).

  That is 9 tests. Expected suite size after: base + 9 (base not measured by R1).
- Real-data probe for I2/I3 (not a test): with the cutoff set to 67 in a scratch copy, 068 should give no line (TOTAL at 05 L107 and 06 L134), and 067 should give no line because it changed no trigger file. UNVERIFIED: R1 ran nothing.

## Fit for a ~$3k account
Pipeline tooling only (scripts/check_pipeline.py, tests/, docstring, maybe one sentence in run-item.md). It has no trading effect and changes nothing in ccbot/, config/, reports/real/ or 001. Nothing connects to a brokerage. It indirectly protects the account by making sure any change to the real-quote backtest's decision path reports its whole effect before the person relies on those numbers (RI-013). It costs nothing to run. The only cost is a forced 22-minute realtest run when a trigger file changes, which is why the exact trigger list matters (F12). This is research, not financial advice.

## Open questions
1. Trigger scope: exact 8 paths (P2) or the request's whole `config/`? R1 suggests exact (F10, F12, F21), with the ast guardrail test against staleness. Should data/real/ be included (F11)? A data refetch, for example the RI-002 Q4-2021 earnings follow-up (logs/recurring-issues.md:25), changes realtest output.
2. Attribution: should 070 reuse `_walk`'s first-parent units (simpler, but they give the F18 false positive on main after a multi-item PR) or walk non-merge commits as its own pass? Fixture 6 decides it.
3. How strict is "filled"? The TOTAL line alone (P1), or also a before/after SHA and the data hash that the template asks for? Should 06's TOTAL line also have to equal 05's (the 067/06 L139 comparison)? A mismatch would be INCOMPLETE. A real mismatch should instead make I3's verdict FAIL.
4. Should a `## ` line inside a fenced code block count as the end of the section? Pasted output could contain one. Ignore headings inside fences, or note it as a gap.
5. Uncommitted work: the check sees only commits. I2 commits code with 05 (run-item.md L16), so the in-tree run at I3 time already sees the trigger. Should the working-tree diff (`git diff --name-only HEAD`) count too?
6. Output: INCOMPLETE entries only (request), or also a summary line like `REAL-DATA FIELD: <ids> | none | not checked (no git)` so the not-checked case is visible (F20)?
7. 069 is being built in parallel and falls below the cutoff. If it changes realtest's path, nothing checks its field. Is the cutoff 070 (request) or 069?
