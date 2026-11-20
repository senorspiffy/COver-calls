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

# Round 2 (fixes for 06 FAIL round 1)
Base: 875158e (branch head; includes 069 build 8dc2c2d, I3 FAIL 652a320, 070 build 875158e). 070's code (REAL-DATA FIELD in scripts/check_pipeline.py, tests/test_real_data_field.py) is untouched: this round changes no file 070 changed, and scripts/check_pipeline.py is not edited at all.

## Changes made (file: what changed)
File counts (from commands, 012):
- new: `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` -> `0`
- changed: `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` -> `2`

1. `templates/daily-audit.md` (06 problem 2, I3's first option): the allowed forms of each channel line moved into the comment, written so no comment line starts with `project-inbox:` or `hub:`. The two lines in the section are now `project-inbox: <fill in>` and `hub: <fill in>`, which match neither INBOX_PI nor INBOX_HUB. The comment says "an unfilled line fails INBOX". The forms are the same as before ("nothing new (N seen before)", "N new", "UNREAD: not reachable (error)"; "SHA, nothing new", "SHA, N new lines", "UNREAD: not reachable (error)") and match a1-auditor.md 2a/2b. The check code is unchanged, so no `<n>`/`|` rejection was added.
2. `tests/test_pipeline_check.py`: 3 new tests at the end of the file.
   - (xi) `test_inbox_code_words_mid_line_fail` (06 problem 1, m8): the Inbox section holds `project-inbox: nothing new` and `hub: 116c68c` only inside an FYI bullet. Expects `INBOX: 2026-11-18.md (no project-inbox: line; no hub: SHA or UNREAD line)` and exit 1. This is I3's probe fixture.
   - (xii) `test_inbox_heading_mid_line_fails` (06 problem 1, m9): `## Inbox` appears only mid-line ("Notes: see ## Inbox below"), followed by valid channel lines. Expects `INBOX: 2026-11-18.md (no ## Inbox)` and exit 1.
   - (xiii) `test_inbox_unfilled_template_fails` (06 problem 2): reads `templates/daily-audit.md` from the repo, writes it unchanged as `logs/audit/2026-11-18.md`, and expects both channel parts named as missing, with exit 1. It also asserts that the template still has `## Inbox` and `<fill in>`, so the test can't pass vacuously on a template without the section.

## Connectivity check
- [x] Each new test is collected (`-k inbox`: 14 cases, was 11). (xiii) reads the shipped template, so the template and the check are tied by a test: a future edit that makes a placeholder line match fails it.
- [x] Input/output: unchanged from round 1. A1 fills the template's lines, and `inbox_section` reads them. The comment tells A1 which forms are allowed.
- [x] Branches: no code change, so the round-1 branch list holds. The new tests cover two more inputs that end in exit 1 (mid-line code words, mid-line heading).
- [x] No TODOs: `git diff -U0 | grep '^+' | grep -cE "fillna|nan_to_num|or 0|else 0|is not None and|max\(1,|min\(1,|\.get\([^)]*, 0\)|TODO"` -> `0`.
- Missing-data grep over ccbot/: 37 hits, all pre-existing (no ccbot/ change; `git diff --stat -- ccbot/` is empty). 014 patterns: no dataclass, no numeric comparison added.

## Test output (pasted, not summarized)
```
$ python3 -m pytest -q -p no:cacheprovider
377 passed, 1 skipped in 55.19s
$ python3 -m pytest -q -p no:cacheprovider tests/test_pipeline_check.py
104 passed in 13.46s
$ python3 -m pytest -q -p no:cacheprovider tests/test_pipeline_check.py -k inbox
14 passed, 90 deselected in 1.01s
$ python3.11 -m py_compile tests/test_pipeline_check.py && echo py311 ok
py311 ok
```
test_pipeline_check: 101 (06 round 1) + 3 = 104. The full-suite total includes 070's tests from 875158e.

`python3 scripts/check_pipeline.py` (exit=0), tail:
```
069: in progress (FULL: next 07)
070: in progress (FULL: next 06)
STUCK: none
AWAITING A1: none
IN PR: none
OPEN BRANCHES (not merged into HEAD):
  origin/claude/project-thread-f64g3k: items none; merges cleanly; last commit 2026-11-17 (0 days)
RULES BRANCH: none
ID CLASH: none
A1 FAIL: none
INCOMPLETE: none
LOG TIME: none (not checked: 048: built before 045's --log rule reached main; times typed by hand, not recoverable (item 049))
UNTRACKED CHANGE: none
RESEARCH CODE: none
REAL-DATA FIELD: none
ORPHAN LOG: none
INBOX: not checked (no daily report from 2026-11-18)
SKIPPED: none
```
(069 shows `next 07` because 06 exists with a FAIL. I3 re-runs 06.)

Mutations (scratch worktrees of HEAD 875158e with this round's two files copied in, under `/tmp/claude-0/-home-claude/4cc69c4f-899b-56b8-af6f-c0c8dcf01a44/scratchpad/i2r2-069/<m>/`; run with `python3 -m pytest -q -p no:cacheprovider tests/test_pipeline_check.py -k inbox`; worktrees removed afterwards):
```
m8  `^` removed from INBOX_PI and INBOX_HUB:  1 failed, 13 passed
    FAILED tests/test_pipeline_check.py::test_inbox_code_words_mid_line_fail
m9  `^` removed from INBOX_HEAD:              1 failed, 13 passed
    FAILED tests/test_pipeline_check.py::test_inbox_heading_mid_line_fails
mt  round-1 template restored (git show HEAD:templates/daily-audit.md): 1 failed, 13 passed
    FAILED tests/test_pipeline_check.py::test_inbox_unfilled_template_fails
    (with the `<fill in>` assert removed, so the INBOX line itself is compared:)
    - INBOX: 2026-11-18.md (no project-inbox: line; no hub: SHA or UNREAD line)
    + INBOX: 2026-11-18.md (no hub: SHA or UNREAD line)
```
The mt output repeats 06's finding: the round-1 template passed the project-inbox half. With the new template, both halves fail.

## Real-data effect (diff_reports output, pasted)
not required (`templates/daily-audit.md`, `tests/test_pipeline_check.py`; neither is ccbot/realtest.py or a file it reads)

## Deviations from plan
None in round 2. Both fixes are the ones 06 named. For problem 2 I took I3's first option (placeholders that cannot match). It needs no code change, and the template test pins it.

## Recurring issues checked (round 2)
RI-001: ESCALATED, checked. No new filter. The new fixtures are real counts: 0 of 2 mid-line code words match, and 0 of 1 mid-line headings match.
RI-002: ESCALATED, unchanged. An unfilled template line is no longer read as a filled one (06 problem 2), and no value is defaulted.
RI-008: checked (py_compile on 3.11).
RI-009: checked. Mutations ran only in scratch worktrees, which were removed after. work/070 was not touched or staged.
RI-010: guardrail extended (069). The INBOX check now also fails an unfilled template.
RI-012: guardrail applied. The `^` anchors are pinned by tests (xi, xii), and m8 and m9 each fail 1 test.
RI-013: OPEN, n/a (no realtest change).

# Round 3 (after A1 FAIL)
Plan: 04 "Round 2 (after A1 FAIL)". Input: logs/audit/2026-11-18-069.md "Sent back" 1-2. Base: ad30a07 (I1 plan round 2); the branch head is now 8dfc800 (070's I3 commit, which changes only work/070 and logs/implementation, `git show --stat 8dfc800`). 070's code is untouched: `git diff -- scripts/check_pipeline.py | grep -ciE "real_data|TRIGGER|TOTAL_LINE"` -> `0`; main() is not edited.

## Changes made (file: what changed)
File counts (from commands, 012):
- new: `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^??'` -> `0`
- changed: `git status --porcelain -uall -- . ':!work' ':!logs' | grep -c '^ M'` -> `2`

1. `scripts/check_pipeline.py` (R2-1), only 069's lines (`git diff -U0` hunks: L134-147 docstring, L230 constant, L712-738 new helper, L740-750 inbox_section):
   - `INBOX_FROM = "2026-11-18"` deleted; `INBOX_TEMPLATE = "templates/daily-audit.md"` added.
   - new `_inbox_gate(path)` above `inbox_section`, steps 1-5 of R2-1 item 2: no git -> `not checked (no git)`; shallow -> `not checked (shallow clone; run git fetch --unshallow)`; HEAD verifies -> `git log --no-renames --diff-filter=A --format=%H -1 -- <path>`, non-zero -> `<name> (git log failed)`, True; adding commit's `git show <sha>:templates/daily-audit.md` must match INBOX_HEAD; no adding commit -> working-tree template (`not committed`). Returns None when the report is checked.
   - `inbox_section`: date term dropped (`not checked (no daily report)`), gate called after picking the newest report; content checks unchanged.
   - module docstring: template rule, known gaps (u) and (v).
2. `tests/test_pipeline_check.py` (R2-2), 069 block only:
   - `_daily(root, name, body, template=INBOX_TPL, commit=True, git=True)` (git init on first call, writes the template unless None, commits); `_inbox` passes `--untracked-from <HEAD>` when the root has a commit. New constants INBOX_TPL, OLD_TPL, OLD_REPORT (2026-11-17.md's shape: prose `## Inbox`, "Hub (116c68c)").
   - `@NO_GIT` on i-vi and x-xiii (now git fixtures).
   - vii rewritten (renamed `test_inbox_report_under_old_template_not_checked`), ix wording updated.
   - new: xiv, xiv-b, xiv-c (into main / into t), xv, xv-b, xv-c, xvi (116c68 / 2026-11-18 / 41 hex), xvii, xvii-b, xviii, xix, xx, xxi.

## Connectivity check
- [x] `_inbox_gate` is called by `inbox_section`, whose result main() prints and feeds to the exit code (unchanged block). `INBOX_TEMPLATE` is used by the gate (git show path, working-tree path, message). `INBOX_FROM` has no remaining reference (`grep -n INBOX_FROM scripts/check_pipeline.py` -> no output).
- [x] Inputs: logs/audit/ (newest DAILY_REPORT), git history, templates/daily-audit.md at the adding commit or in the working tree. Output: the `INBOX:` line and exit code, read by A1/I3 and test_repo_pipeline_has_no_skipped_items.
- [x] Every branch ends in a defined result: no report / no git / shallow / template absent / template without Inbox -> `not checked (...)`, exit 0 (never `none`, RI-002); git log failure -> exit 1; checked -> content result. Each has a test (table in 04 R2).
- [x] No TODOs: `git diff -U0 | grep '^+' | grep -c TODO` -> `0`. No new files.
- Missing-data grep over ccbot/: 37 hits, all pre-existing (no ccbot/ change). Over the diff, one new hit: tests L100 `if head is not None and head.returncode == 0 else []` in `_inbox`: a test helper that adds `--untracked-from` only when a HEAD exists; with no flag the walk uses the default cutoff and reports it missing (exit 1), so no check passes on absent data. 014 patterns: no dataclass, no `>`/`<` on numbers added.

## Test output (pasted, not summarized)
Before (ad30a07, unchanged tree):
```
$ python3 -m pytest -q -p no:cacheprovider tests/test_pipeline_check.py -k inbox
14 passed, 90 deselected in 1.15s
```
After:
```
$ python3 -m pytest -q -p no:cacheprovider tests/test_pipeline_check.py -k inbox
30 passed, 90 deselected in 4.00s
$ python3 -m pytest -q -p no:cacheprovider tests/test_pipeline_check.py
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 119 passed in 17.39s
$ python3 -m pytest -q -p no:cacheprovider
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 399 passed, 1 skipped in 63.33s (0:01:03)
$ python3.11 -m py_compile scripts/check_pipeline.py && echo py3.11 ok
py3.11 ok
$ python3.11 -m py_compile tests/test_pipeline_check.py && echo py311 ok
py311 ok
```
The one failure is expected: `069: A1 FAIL (FULL; sent back, needs a later A1 PASS line (item 042))` / `A1 FAIL: 069` gives exit 1 until A1 re-audits. Every other report line is `none`, and INBOX is `not checked`.

`python3 scripts/check_pipeline.py` (exit=1), tail:
```
069: A1 FAIL (FULL; sent back, needs a later A1 PASS line (item 042))
070: awaiting A1 (FULL)
STUCK: none
AWAITING A1: 070
IN PR: none
MAIN AHEAD: origin/main has 1 commits not in HEAD; merge it before building (item 051)
OPEN BRANCHES (not merged into HEAD):
  origin/claude/project-thread-f64g3k: items none; merges cleanly; last commit 2026-11-17 (1 days)
RULES BRANCH: none
ID CLASH: none
A1 FAIL: 069
INCOMPLETE: none
LOG TIME: none (not checked: 048: built before 045's --log rule reached main; times typed by hand, not recoverable (item 049))
UNTRACKED CHANGE: none
RESEARCH CODE: none
REAL-DATA FIELD: none
ORPHAN LOG: none
INBOX: not checked (2026-11-17.md added in b268a22; its templates/daily-audit.md has no ## Inbox)
SKIPPED: none
```
MAIN AHEAD is c10b8ae (PR #30 merge); A1 found that merging it changes no file. Not merged here: the plan does not name it and this round is one commit (for the orchestrator).

i, ii and vi in the git fixture (`-v`): all PASSED, each asserting exit 0:
```
tests/test_pipeline_check.py::test_inbox_section_with_sha_passes[116c68c] PASSED [ 25%]
tests/test_pipeline_check.py::test_inbox_section_with_sha_passes[116c68c533cbd9d13bf3e81c1d833ab408102f84] PASSED [ 50%]
tests/test_pipeline_check.py::test_inbox_unread_channels_pass PASSED     [ 75%]
tests/test_pipeline_check.py::test_inbox_ignores_per_item_report PASSED  [100%]
```
Whole main() output for fixture i (7-char SHA), built with the test's own `_daily`/`_inbox`:
```
STUCK: none
AWAITING A1: none
IN PR: none
RULES BRANCH: none
ID CLASH: none
A1 FAIL: none
INCOMPLETE: none
LOG TIME: none
UNTRACKED CHANGE: none (cutoff 71c61b6 from --untracked-from)
RESEARCH CODE: none
REAL-DATA FIELD: none
ORPHAN LOG: none
INBOX: none
SKIPPED: none
exit=0
```

Mutations (each in its own copy under `/tmp/claude-0/-home-claude/4cc69c4f-899b-56b8-af6f-c0c8dcf01a44/scratchpad/069r3/m/<name>/`, `tests/test_pipeline_check.py -k inbox`; I3 re-runs them):
```
m10 {7,40} -> {1,40}          2 failed, 28 passed: xvi[116c68], xvi[2026-11-18]
m10b {7,40} -> {7,}           1 failed, 29 passed: xvi[41 hex]
gate always None              10 failed, 20 passed: vii, xiv, xiv-b, xiv-c[main], xiv-c[t], xv-c, xvii, xviii, xix, xx
gate always not checked       27 failed, 3 passed (all but viii, ix, xvii-b)
HEAD: instead of <sha>:       5 failed, 25 passed: xiv, xiv-b, xiv-c[main], xiv-c[t], xx
--diff-filter=A removed       1 failed, 29 passed: xiv-b
shallow guard off (if False)  1 failed, 29 passed: xviii
git log failure -> False      1 failed, 29 passed: xix
round-1 check_pipeline.py (ad30a07) with the new tests, -k inbox_old_report_after_template_change:
                              1 failed: 'INBOX: 2026-... UNREAD line)' == 'INBOX: not c... no ## Inbox)'
```
Each mutation fails at least the tests 04 names (gate-always-None also fails xix, which is expected since the gate holds the log call). A1's m10 now fails 2 tests (send-back 2).

## Probes
Probe 1 (real repo, read-only git log):
```
$ git log --format='%h %cI %s' -- templates/daily-audit.md
dc162cf 2026-11-17T23:55:40+00:00 Item 069: I2 round 2 - anchor tests and unfillable template placeholders
8dc2c2d 2026-11-17T23:44:30+00:00 Item 069: I2 build - daily Inbox step and INBOX check
bd10ebd 2026-10-31T22:25:24+00:00 Daily fixes 2026-10-31: items 025-030 through the pipeline; complete 023 and 024
ff72e12 2026-10-30T17:09:23+00:00 Add research, implementation, and audit agent teams
$ for each 2026-11-10..17: git log --no-renames --diff-filter=A --format=%H -1 -- logs/audit/<d>.md; git show <sha>:templates/daily-audit.md | grep -c '^## Inbox'
logs/audit/2026-11-10.md added 96b7f94 2026-11-10T22:22:57+00:00 inbox=0
logs/audit/2026-11-11.md added a607ed4 2026-11-11T22:16:45+00:00 inbox=0
logs/audit/2026-11-12.md added 863827c 2026-11-12T23:20:00+00:00 inbox=0
logs/audit/2026-11-13.md added 29a2b28 2026-11-13T23:25:10+00:00 inbox=0
logs/audit/2026-11-14.md added d3827c7 2026-11-14T23:18:35+00:00 inbox=0
logs/audit/2026-11-15.md added 6c7762f 2026-11-15T23:18:16+00:00 inbox=0
logs/audit/2026-11-16.md added c92cd9a 2026-11-16T23:17:51+00:00 inbox=0
logs/audit/2026-11-17.md added b268a22 2026-11-17T23:17:10+00:00 inbox=0
```
Dated count (RI-001): 0 of 8 daily reports from 2026-11-10 to 2026-11-17 were added under an Inbox template. 2026-11-17.md (b268a22, 23:17:10) was added before 8dc2c2d (23:44:30). The real-tree INBOX line is `not checked (2026-11-17.md added in b268a22; ...)`, as above.

Probe 2 (A1's P1 as a real merge; scratch clone `/tmp/claude-0/-home-claude/4cc69c4f-899b-56b8-af6f-c0c8dcf01a44/scratchpad/069r3/p2`, `git clone --no-local` of the repo; this round's two files committed there as `0d94c15 069 r3 WIP (scratch)` on top of 8dfc800; origin/main = c10b8ae fetched as `omain`):
```
--no-ff: on omain, commit logs/audit/2026-11-18.md = copy of 2026-11-17.md (2f892e4), then git merge --no-ff 0d94c15
$ git log --oneline --graph -6
*   9916186 merge branch
|\  
| * 0d94c15 069 r3 WIP (scratch)
| * 8dfc800 Item 070: I3 verification PASS (round 2), audit task
| * ad30a07 Item 069: I1 build plan round 2 (after A1 FAIL): template-tied INBOX start, SHA length test
| * a237da7 Item 070: I2 round 2 - main exit-code tests and TOTAL-in-prose/comment negatives
| * e75703b Item 069: A1 result FAIL (fixed INBOX_FROM date breaks main before merge; SHA length untested)
$ git log --oneline --first-parent -4
9916186 merge branch
2f892e4 daily audit 2026-11-18 (old template, on main)
c10b8ae Merge pull request #30 from senorspiffy/daily-fixes/2026-11-16
b268a22 Daily audit 2026-11-17: report, efficiency list, recurring issues (RI-002, RI-010, RI-013 status), item 070
$ python3 scripts/check_pipeline.py   (exit=1, from A1 FAIL: 069 only)
INBOX: not checked (2026-11-18.md added in 2f892e4; its templates/daily-audit.md has no ## Inbox)
SKIPPED: none
(all other report lines none; A1 FAIL: 069)

same merge with the round-1 code (git merge --no-ff 8dfc800 from 2f892e4's parent line):
INBOX: 2026-11-18.md (no project-inbox: line; no hub: SHA or UNREAD line)

--squash: on omain, commit the same 2026-11-18.md (d4c3670), git merge --squash 0d94c15, commit
$ git log --oneline -3
955f2e1 squash branch
d4c3670 daily audit 2026-11-18 (old template, on main)
c10b8ae Merge pull request #30 from senorspiffy/daily-fixes/2026-11-16
$ python3 scripts/check_pipeline.py   (exit=1, from A1 FAIL: 069 only)
A1 FAIL: 069
UNTRACKED CHANGE: none
INBOX: not checked (2026-11-18.md added in d4c3670; its templates/daily-audit.md has no ## Inbox)
SKIPPED: none

then on the --no-ff merge: commit 2026-11-19.md = templates/daily-audit.md unfilled
$ python3 scripts/check_pipeline.py   (exit=1)
A1 FAIL: 069
INBOX: 2026-11-19.md (no project-inbox: line; no hub: SHA or UNREAD line)
```
Exit is 1 in every scratch run because the scratch clone carries this branch's `A1 FAIL: 069`; the INBOX term is the part probe 2 tests: `not checked` after both merge types, and the check fires on the first report under the new template.

Probe 3 (070's lines): `git diff -U0 -- scripts/check_pipeline.py | grep '^@@'` -> hunks at 134, 139, 224, 705, 707, 710, 712, 713 (old line numbers): docstring, constant and inbox_section region only. No REAL-DATA FIELD / TRIGGER / TOTAL_LINE / main() line changed.

## Real-data effect (diff_reports output, pasted)
not required (scripts/check_pipeline.py, tests/test_pipeline_check.py; neither is ccbot/realtest.py or a file it reads)

## Deviations from plan
- The `_inbox_gate` return annotation is the string `"tuple[str, bool] | None"` (allowed by 04: "or no annotation"; a string is never evaluated, so no 3.10 risk).
- vii's test function was renamed (`..._before_cutoff_...` -> `..._under_old_template_...`) because no cutoff exists any more; it still contains `inbox`.
- xxi creates its report with `_daily(..., commit=False)` (git init, no commit) and calls `cp.inbox_section()` at unit level, as planned.
Nothing else.

## Recurring issues checked (round 3)
RI-001: ESCALATED, checked. The gate has a dated count (0 of 8, probe 1) and pinning tests; the SHA bound has negative tests on both ends (m10 fails 2, m10b fails 1).
RI-002: ESCALATED, checked. No git, shallow, no report, template absent or without Inbox -> `not checked`, never `none`; git log failure -> exit 1 (xix).
RI-008: checked (py_compile on 3.11, both files).
RI-009: checked. Mutations and probes only in scratch copies/clones; work/070 untouched and not staged.
RI-010: guardrail fixed (069 round 3). The check is keyed to the template at the report's adding commit; xiv/xiv-b/xiv-c and probe 2 (--no-ff and --squash) show a main-written old-format report stays `not checked`.
RI-011: checked; no merge-base used; path-limited log through merges pinned by xiv-c.
RI-012: GUARDED, held; INBOX_HEAD (anchored) is reused on the template text.
RI-007: checked; no step skipped (next I3).
RI-013: OPEN, n/a (no realtest change).
