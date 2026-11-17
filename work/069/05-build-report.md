# 05 Build report - 069
## Changes made (file: what changed)
Base (branch head when I2 started): 1fb7f6a (Item 069: I1 build plan). 2a51719 (070's I1 plan, work/070 + log only) landed on the branch during the build and touches none of these files.

File counts (from commands, 012):
- new: `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` -> `0`
- changed: `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` -> `5`

Plan said 5 files (0 new, 5 changed). Matches.

1. `.claude/commands/daily-audit.md` (map step 1): the text now opens with "First, A1 runs the Inbox step (a1-auditor job B, item 069) and puts its section at the top of the report." The run list reads "new BUG, EFFICIENCY and IDEA (inbox) work items ... run each through /run-item the same day (IDEA items from the inbox run with the day's BUG and EFFICIENCY items)". 03's two sentences are merged into one so the list isn't repeated.
2. `.claude/agents/a1-auditor.md` job B: new first bullet "Inbox (item 069), before the log review", with sub-steps a) to d) taken word for word from 03 2a-2d, plus:
   - C5: no clone gives `hub: UNREAD: not reachable (no clone at <path>)`, and A1 does not clone.
   - Decision 3: `status:` is never the marker, because threads set read first.
   - Decision 4: own notes are classified by body, listed as "own note" and not moved, because of the hub links at flashloan L21 and quant-trader L59.
   - Decision 5: only projects/covered-calls/inbox.md and shared-facts.md are read, with no keyword search ("6 false hits of 12", R1-15).
   - Decision 7: urgent items are listed first.
   - Missing inputs rows: no previous report, header incomplete (never defaulted), "status not set (<error>)".
   - L20 is amended per C4: "...change only logs/ and work/ markdown; the Inbox step's status lines and moves are on /mnt/project-files, outside the repo, and are listed in the report (item 069)."
3. `templates/daily-audit.md` (map step 3): new first section after the title, `## Inbox (other projects asking us to test or try something; item 069)`. It has a comment line, a `project-inbox:` line and a `hub:` line (each lists its allowed forms, including `UNREAD: not reachable (<error>)`). Four `###` sub-lists follow: New items, FYI, Refused, Status writes. `###` does not end the section, because the bound is `^## ` and the third character must be a space.
4. `scripts/check_pipeline.py` (placement per C1):
   - Docstring: `INBOX (item 069, RI-010)` paragraph after the `--next-id` paragraph (original L112). It covers the rule, the cutoff, that per-item reports are ignored, exit 1, and the known gap ("proves the lines exist, not that A1 read the channels; I3 and A1 spot-check").
   - After LEGACY (original L183): `INBOX_FROM`, `DAILY_REPORT`, `INBOX_HEAD`, `INBOX_PI`, `INBOX_HUB`, exactly as in 04.
   - After `next_id()` (original L562): `inbox_section(audit=Path("logs/audit")) -> tuple[str, bool]`. If the folder is missing or no report fullmatches with stem >= INBOX_FROM, it returns `("not checked (no daily report from 2026-11-18)", False)`. Otherwise it reads the newest such report and cuts the section from `^## Inbox\b` to the next `^## `. It returns `("none", False)` or `("<file> (<missing parts joined by '; '>)", True)`.
   - main: the 5-line block from 04, inserted only between `ORPHAN LOG:` (L652) and `SKIPPED:` (L653). L650 and L654 are unchanged.
5. `tests/test_pipeline_check.py`: 10 test functions (11 test cases; (i)/(i-b) is one parametrized function) at the end of the file, plus the helpers `_daily` and `_inbox` and the constant `INBOX_OK`. (viii) calls `parse_request` through the existing `_cp()`.

## Connectivity check
- [x] every new function/rule is used. `inbox_section` is called once in `main`. Each of the 5 constants is used by `inbox_section`. `_daily`/`_inbox`/`INBOX_OK` are used by the new tests. The a1 bullet is reached through daily-audit.md ("First, A1 runs the Inbox step"). The template section is what A1 fills, and what `inbox_section` reads from 2026-11-18 on.
- [x] every input has a source, every output has a consumer. Input: logs/audit/<YYYY-MM-DD>.md, written by A1 from templates/daily-audit.md. Output: the `INBOX:` line in check_pipeline.py's report, which A1 reads in job B (Every SKIPPED/INCOMPLETE ... is an error), and exit 1. The A1-side outputs (IDEA items, FYI/refused lists, status writes) go to work/<ID>/request.md, the daily report and "For the person".
- [x] every branch ends in a defined result:
  - missing folder → `not checked (...)` (test ix);
  - no daily report >= cutoff → `not checked (...)` (vii);
  - no heading → `<file> (no ## Inbox)`, exit 1 (iii);
  - one or both lines missing → named parts, exit 1 (iv, v, x);
  - all present → `none` (i, i-b, ii);
  - a section running to EOF with no later `## ` → `rest` is used whole (fixtures ii, iv, v have no later heading; i/i-b do).
  - On the A1 side, every channel has UNREAD, a missing SHA gives a full read, a missing header gives "header incomplete", and a failed write gives "status not set". None of these is silent.
- [x] no leftover TODOs or unused files. `git diff | grep -c TODO` → 0. Mutation copies are only in the scratchpad (`/tmp/claude-0/-home-claude/4cc69c4f-899b-56b8-af6f-c0c8dcf01a44/scratchpad/m069/`).

Missing-data grep (`grep -rnE "fillna|nan_to_num|or 0|else 0|pd\.notna\(.*\) and|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)" ccbot/`): 37 hits, all pre-existing. This item changes no file under ccbot/ (`git diff --stat -- ccbot/` is empty), so there is no new or changed hit. The same pattern run over this item's added lines (`git diff -U0 | grep '^+'`) gives 0 hits. The one `or 'none'` in the added lines is `', '.join(skipped) or 'none'`, which is a copy of the existing SKIPPED line: an empty list is shown as "none", and nothing is defaulted. 014 patterns: no dataclass was added. There is no `>`/`<` on a numeric that could be NaN; the only comparison is `p.stem >= INBOX_FROM`, a string comparison on names already filtered by DAILY_REPORT.

Feasibility numbers (real, from 04's guardrail list):
- Real repo today: `INBOX: not checked (no daily report from 2026-11-18)`, exit 0. This is 0 daily reports >= 2026-11-18, as 03 said.
- Hub SHA regex: the 7-char `116c68c` and the 40-char `116c68c533cbd9d13bf3e81c1d833ab408102f84` both give `INBOX: none` (tests i, i-b pass).
- Name filter: `re.compile(r'\d{4}-\d{2}-\d{2}\.md')` on `2026-11-18-070.md` → match False, fullmatch False. On `2026-11-18.md` → True/True. On `2026-11-18.mdx` → match True, fullmatch False (python3 output: `[('2026-11-18-070.md', False, False), ('2026-11-18.md', True, True), ('2026-11-18.mdx', True, False)]`).

## Test output (pasted, not summarized)
Before (base, same tree before edits):
```
$ python3 -m pytest -q
342 passed, 1 skipped in 50.16s
$ python3 -m pytest -q tests/test_pipeline_check.py
90 passed in 11.02s
```
After:
```
$ python3 -m pytest -q
353 passed, 1 skipped in 54.42s
$ python3 -m pytest -q tests/test_pipeline_check.py
101 passed in 12.50s
$ python3 -m pytest -q tests/test_pipeline_check.py -k inbox
11 passed, 90 deselected in 0.57s
```
Base + 11 = 90 + 11 = 101; 342 + 11 = 353. `test_repo_pipeline_has_no_skipped_items` passes.

`python3 scripts/check_pipeline.py` (exit=0), tail:
```
069: in progress (FULL: next 05)
070: in progress (FULL: next 05)
STUCK: none
AWAITING A1: none
IN PR: none
OPEN BRANCHES (not merged into HEAD):
RULES BRANCH: none
ID CLASH: none
A1 FAIL: none
INCOMPLETE: none
LOG TIME: none (not checked: 048: built before 045's --log rule reached main; times typed by hand, not recoverable (item 049))
UNTRACKED CHANGE: none
RESEARCH CODE: none
ORPHAN LOG: none
INBOX: not checked (no daily report from 2026-11-18)
SKIPPED: none
```
RI-008: `python3.11 -m py_compile scripts/check_pipeline.py` → `py311 ok`. python3.10 is not installed. `tuple[str, bool]` as a return annotation is valid from 3.9.

Mutations (scratch copies under `/tmp/claude-0/-home-claude/4cc69c4f-899b-56b8-af6f-c0c8dcf01a44/scratchpad/m069/<m>/`, run with `python3 -m pytest -q -p no:cacheprovider <copy>/tests/test_pipeline_check.py -k inbox`):
```
m1  inbox_section always ("none", False): 6 failed, 5 passed
    FAILED test_inbox_heading_missing_fails, test_inbox_hub_line_without_sha_fails,
    test_inbox_project_inbox_line_missing_fails, test_inbox_report_before_cutoff_not_checked,
    test_inbox_no_audit_folder_not_checked, test_inbox_hub_line_outside_section_fails
m2  INBOX_FROM = "2026-11-17": 2 failed, 9 passed
    FAILED test_inbox_report_before_cutoff_not_checked, test_inbox_no_audit_folder_not_checked
m3  DAILY_REPORT.fullmatch -> .match: 1 failed, 10 passed
    FAILED test_inbox_ignores_per_item_report
m3b name filter removed (p.suffix == ".md"): 1 failed, 10 passed
    FAILED test_inbox_ignores_per_item_report
m4  section bounds removed (section = text): 1 failed, 10 passed
    FAILED test_inbox_hub_line_outside_section_fails
m5b "> " removed from the viii fixture: 1 failed, 10 passed
    FAILED test_inbox_quoted_scope_and_waiver_are_not_read
```
Every 04 mutation fails its named test (iii, iv, v, x under m1; vii under m2; vi under m3; x under m4; viii under m5). m1 and m2 also fail vii/ix, because those pin the exact "not checked" text.

Merge probe with 070: not run. 070 is not built (`070: in progress (FULL: next 05)`), so per 04 A1 runs it. Hand check against 070/04 C1: 070 plans its edits after L110, after L144, after L540, at L588, L613, after L650 and at L654. 069's hunks are after L112, after L183, after L562, and between L652 and L653. Unchanged lines L111-112 and L651-652 separate the closest ones. The plan also leaves L653 untouched, as the line between 069's block and 070's L654 edit. 070 puts its tests in a new file, so the EOF append in test_pipeline_check.py does not collide.

## Real-data effect (diff_reports output, pasted)
not required (`.claude/agents/a1-auditor.md`, `.claude/commands/daily-audit.md`, `scripts/check_pipeline.py`, `templates/daily-audit.md`, `tests/test_pipeline_check.py`; none is ccbot/realtest.py or a file it reads)

## Deviations from plan
1. Test vi fixture (strengthened; I3 to confirm). The plan's fixture (`2026-11-18.md` + `2026-11-18-070.md`) does not pin the name filter. "-" (0x2d) sorts before "." (0x2e), so `2026-11-18.md` is already the newest by name, and m3 (`.match`) and m3b (filter removed) both passed all 11 tests with that fixture. 03 Map step 5 (vi) assumed the opposite order. I kept the plan's file and added two later-dated names: `2026-11-19-070.md` (pins the filter, m3b) and `2026-11-19.md.bak` (pins fullmatch over a prefix match, m3). With them, both mutations fail vi, as 04 expects. The code is unchanged from 04.
2. `_daily` also creates `work/`, because `main()` lists `work/` and raises FileNotFoundError without it (pre-existing behaviour, not in scope). The first run of the new tests failed 9 of 11 on this, before the helper was fixed.
3. daily-audit.md: 03's added sentence is folded into the existing run-list sentence (the same content, not written twice).

## Recurring issues checked
RI-001: ESCALATED, checked. Each filter has a real count and a pinning test: name filter (vi, with deviation 1 making it bite), cutoff (vii and the real repo: 0 reports), SHA length (i, i-b).
RI-002: ESCALATED, checked. Unknown is never "none": a missing folder or a pre-cutoff report gives `not checked`, and UNREAD is a separate accepted form. On the A1 side, missing header fields are never defaulted. No new grep hit, and no ccbot/ change.
RI-004/RI-005: checked. 03's worked examples were re-run against the regexes: `hub: 116c68c, nothing new` matches INBOX_HUB, and 2026-11-17.md's "Hub (116c68c)" has no `^hub:` line. The vi ordering assumption in 03 was found wrong (deviation 1).
RI-006: checked. Counts come from commands.
RI-007: checked. Each message becomes an item, and viii closes the quoted Scope/Waived path (m5b proves it).
RI-008: checked. py_compile ran on 3.11, and no 3.12-only syntax was used.
RI-009: checked. Mutations were run only in scratch copies and the repo tree was never mutated. work/070 was not touched or staged. The 070 merge probe goes to A1 (070 not built).
RI-010: checked. INBOX is the script check for the text duty, and the log line is written with `--log` right after this file.
RI-012: checked. Anchored line regexes are bounded to the section (x; m4).
RI-013: OPEN, n/a (no realtest output change).
RI-003, RI-011: not applicable.
RI-002: ESCALATED, unchanged by 069 (no data path touched).
RI-010: guardrail extended (069); the INBOX check holds once a daily report dated 2026-11-18 or later exists and A1 sees `INBOX: none` on it.
