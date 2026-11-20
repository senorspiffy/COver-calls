# 06 Verification - 069
Verdict: PASS (round 3; earlier rounds: FAIL round 1, PASS round 2 then A1 FAIL)

All checks were run in a scratch worktree of the build commit 8dc2c2d, because /home/claude/df17 is being edited at the same time by item 070 (uncommitted changes to scripts/check_pipeline.py, templates/build-report.md, templates/verification.md and tests/test_real_data_field.py). The scratch paths were `/tmp/claude-0/-home-claude/4cc69c4f-899b-56b8-af6f-c0c8dcf01a44/scratchpad/i3-069`, mutation copies in `.../scratchpad/i3m069/<m>/` and a probe root in `.../scratchpad/i3probe`. The repo tree was never mutated. Nothing connects to a brokerage.

## I1 audit (plan vs research)
04 follows 03's map one row at a time, and its Rule trace covers map steps 1-5, decisions 1-8, the R1/R2 corrections and R3-a to R3-d. The only drops are R2-5/R2-16 (research text, nothing to build) and R1-27 (removed in 03). Both drops are justified.

Additions not in 03, each with a reason or source:
- C1, placement for the 070 merge: git hunk-overlap source.
- C2, missing logs/audit/: pathlib behaviour, plus test ix.
- C3, section bounds: test x.
- C4, L20 wording: 03's "except" is replaced, because the status writes are not commits.
- C5, no clone gives UNREAD.

Tests i-b, ix and x were added. None of these changes a rule the person follows, and 001 is untouched. I1 is OK.

## I2 audit (build vs plan)
`git diff --stat 1fb7f6a..8dc2c2d` shows 5 non-work/log files: a1-auditor.md, daily-audit.md, check_pipeline.py, templates/daily-audit.md, tests/test_pipeline_check.py. The plan said 5. The diff also includes work/070/04 and a 070 log line, which belong to 070's I1 (2a51719) and not to 069.
- File 1, daily-audit.md: matches. "First, A1 runs the Inbox step ...", and IDEA is in the run list (deviation 3, merged sentence, same content).
- File 2, a1-auditor.md: the new first bullet holds 2a-2d word for word from 03, plus C5 and decisions 3, 4, 5 and 7. The `is-ancestor`, `> `, `UNREAD:` and `archive/covered-calls/` text is all present. I checked every Missing-inputs row in 03 against it: folder unreadable, no clone/fetch fails, no SHA / non-zero exit leads to a full read, no covered-calls hub inbox, `from:` missing counts as foreign, priority/status never defaulted, no previous report, and "status not set". L20 matches C4.
- File 3, templates/daily-audit.md: the section comes first, with the heading, both lines and 4 sub-lists. Matches.
- File 4, check_pipeline.py: the constants come after LEGACY, `inbox_section` after `next_id()`, the docstring paragraph after `--next-id`, and the 5-line block between ORPHAN LOG and SKIPPED. The RESEARCH CODE print and the `return 1 if ...` line are unchanged, as C1 requires. The code is exactly as 04 gives it.
- File 5, tests: 10 functions (11 cases), `_daily`, `_inbox` and `INBOX_OK`.
- Deviation 1 (test vi fixture) is confirmed. `sorted(['2026-11-18.md','2026-11-18-070.md'])` gives `['2026-11-18-070.md', '2026-11-18.md']` ('-' is 45, '.' is 46), so with the plan's fixture the daily file is already the newest. I put the plan's fixture back (only `2026-11-18-070.md`) in scratch copies d3/d3b. With the m3 mutation (`.match`) it gave `11 passed`, and with m3b (no name filter) also `11 passed`. With I2's two extra names, both fail vi (below). The deviation is justified, and the code is unchanged from 04.
- Deviation 2 (`_daily` creates work/): `main()` lists work/, so this is a test-only helper change. OK.
- Connectivity re-done: `inbox_section` is called once in main, all 5 constants are used, and the INBOX line feeds the exit code. The a1 bullet is reached from daily-audit.md, and A1 job B already treats check_pipeline errors as errors. Missing-data grep over the added lines: the only hit is `', '.join(skipped) or 'none'`, a copy of the existing SKIPPED line, so nothing is defaulted.
- Merge with 070: moot. 070 is being built on top of 8dc2c2d in the same branch, not in parallel. Its current uncommitted diff of check_pipeline.py removes 2 lines and no INBOX/inbox line (`git diff -U0 | grep -E "^[-+].*(INBOX|inbox)"` gives no output). A1 should re-check once 070 commits.

## Tests re-run (output)
```
$ python3 -m pytest -q -p no:cacheprovider          (scratch @ 8dc2c2d)
353 passed, 1 skipped in 54.89s
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars'
$ python3 -m pytest -q -p no:cacheprovider tests/test_pipeline_check.py
101 passed in 12.78s
$ ... -k inbox
11 passed, 90 deselected in 1.24s
$ python3 -m pytest -q tests/test_safety.py
9 passed            (test_every_py_compiles_on_oldest_python ran on /usr/bin/python3.11; python3.10 not installed)
$ python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py
py311 ok
$ python3 scripts/check_handoff.py 069
sources count (unique URLs in 01-research.md): 2
fact-check rows: 57
totals line: 57 rows -> 50 as-is, 6 fixed, 1 removed
PASS
```
These match 05: 353 passed / 1 skipped, and 101 in test_pipeline_check.

Mutations (scratch copies, `-k inbox`):
```
m1  inbox_section always ("none", False)      6 failed (iii, iv, v, vii, ix, x)
m2  INBOX_FROM = "2026-11-17"                  2 failed (vii, ix)
m3  DAILY_REPORT.fullmatch -> .match           1 failed (vi)
m3b name filter -> p.suffix == ".md"           1 failed (vi)
m4  section = text (bounds removed)            1 failed (x)
m5  "> " removed from the viii fixture         1 failed (viii)
m7  early `return 1` block removed             4 failed (iii, iv, v, x)
m8  `^` removed from INBOX_PI and INBOX_HUB    11 passed   <-- survives
m9  `^` removed from INBOX_HEAD                11 passed   <-- survives
```

Probe of m8 on a report whose Inbox section holds the code words only inside other text (`.../scratchpad/i3probe/logs/audit/2026-11-18.md`):
```
## Inbox (x)
- FYI: quant-trader note (see project-inbox: nothing new there; hub: 116c68c)
## ESCALATED
```
- Build 8dc2c2d: `INBOX: 2026-11-18.md (no project-inbox: line; no hub: SHA or UNREAD line)`, exit=1 (correct).
- m8: `INBOX: none`, exit=0 (wrong, and no test notices).

## Real-data effect (diff_reports output, pasted)
not required (`.claude/agents/a1-auditor.md`, `.claude/commands/daily-audit.md`, `scripts/check_pipeline.py`, `templates/daily-audit.md`, `tests/test_pipeline_check.py`; none is ccbot/realtest.py or a file it reads)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-002, RI-012, RI-013, RI-007, RI-008, RI-009, RI-010 (one line each below)
- RI-001 (ESCALATED): each filter count re-run. The name filter is 8 daily of 15 per 03, and test vi bites with I2's fixture. The cutoff gives `not checked` on today's repo. The SHA lengths 7 and 40 pass (i/i-b).
- RI-002 (ESCALATED): a missing folder or a pre-cutoff report gives `not checked`, never `none`. Defaults: m1 (always none) fails 6 tests. No ccbot/ change.
- RI-012 (GUARDED): **this item fails it.** The INBOX check classifies report lines by code words (`project-inbox:`, `hub:`, `UNREAD:`, `nothing new`), and no test has those words inside other text. m8 and m9 survive.
- RI-013 (OPEN): n/a, no realtest change.
- RI-007: viii pins the quoted Scope/Waived path (m5 fails it).
- RI-008: compile test ran on 3.11.
- RI-009: all runs were in scratch, work/070 untouched.
- RI-010: the INBOX check exists. m7 shows its exit 1 is pinned.

## Pipeline line (step 2)
check_pipeline line: `069: in progress (FULL: next 07)` (real tree, after this file and the I3 log line were written; before them, scratch @ 8dc2c2d and the real tree both gave `next 06`. Exit 0, `INCOMPLETE: none`, `SKIPPED: none`, `INBOX: not checked (no daily report from 2026-11-18)`.)

## Sent back / sent to Audit
Sent back to I2 (not sent to Audit; no 07 is written until a PASS):
1. **RI-012 / item 059 rule: no negative test with the pattern inside other text.** Removing the `^` anchors from INBOX_PI and INBOX_HUB (m8) or from INBOX_HEAD (m9) leaves all 11 inbox tests green. With m8, the probe above passes as `INBOX: none`. Fix: add a test whose `## Inbox` section has `project-inbox: nothing new` and `hub: 116c68c` only mid-line (e.g. inside an FYI bullet), expecting `INBOX: <file> (no project-inbox: line; no hub: SHA or UNREAD line)` and exit 1. Add a test with `## Inbox` only mid-line (e.g. "see ## Inbox below") expecting `(no ## Inbox)`. Show that m8 and m9 each fail ≥ 1 test.
2. **An unfilled template line passes the project-inbox half.** The template line copied as-is, `project-inbox: nothing new (<n> seen before) | <n> new | UNREAD: not reachable (<error>)`, matches INBOX_PI. Probe with `hub: 116c68c, nothing new` gives `INBOX: none`. The hub half fails only because `<origin/main sha>` is not hex. Fix (I2's choice, within map step 3/4): either move the allowed forms into the template comment and leave placeholder lines that cannot match (e.g. `project-inbox: <fill in>`), or have the check reject a line still holding `<n>` / `|`. Add a test that the unfilled template's Inbox section fails.
Nothing in I1's plan needs to change. Both points are test/template gaps in the build, and the shipped code behaves correctly on the probe.

# Round 2 (re-verification of I2 round 2, commit dc162cf)
Verdict: PASS (round 2; earlier rounds: FAIL round 1)

All runs were made in the scratch worktree `/tmp/claude-0/-home-claude/4cc69c4f-899b-56b8-af6f-c0c8dcf01a44/scratchpad/i3-069r2` at dc162cf. Mutation copies (git archive of dc162cf) were in `/tmp/claude-0/-home-claude/4cc69c4f-899b-56b8-af6f-c0c8dcf01a44/scratchpad/i3m069r2/<m>/`. Both were removed afterwards. The real tree was not mutated: `git diff --stat dc162cf -- scripts tests templates .claude ccbot` is empty. Nothing connects to a brokerage.

## I1 audit (plan vs research)
Unchanged from round 1. Round 2 changes no plan step. Both fixes are the ones round 1 sent back to I2, and 04 needed no change.

## I2 audit (build vs plan)
`git diff --stat 875158e dc162cf` lists 4 files: templates/daily-audit.md (+6/-3), tests/test_pipeline_check.py (+31), work/069/05-build-report.md, and logs/implementation/2026-11-17.md (+1). This matches 05 Round 2, which reports 2 non-work/log files changed.
- Problem 1 (RI-012): tests xi `test_inbox_code_words_mid_line_fail` and xii `test_inbox_heading_mid_line_fails` were added. xi is my round-1 probe fixture, with the code words only inside an FYI bullet. xii has `## Inbox` only mid-line. Both expect the exact INBOX line and exit 1.
- Problem 2 (template): the two lines are now `project-inbox: <fill in>` and `hub: <fill in>`, and the allowed forms are in the HTML comment. Inside the comment, the indented `  project-inbox line:` / `  hub line:` lines cannot match `^project-inbox:` / `^hub:`. The forms agree with a1-auditor.md 2a/2b. Test xiii reads the shipped template, so the template and the check are tied together. It also asserts `<fill in>` is present, so it cannot pass vacuously.
- Positive probe (filled template still passes): I put `nothing new (2 seen before)` and `116c68c, nothing new` in place of the two `<fill in>` lines, and `inbox_section` returned `('none', False)`. On the unfilled template it returned `('2026-11-18.md (no project-inbox: line; no hub: SHA or UNREAD line)', True)`.
- 070's REAL-DATA FIELD code is untouched: `git diff --stat 875158e dc162cf -- scripts/check_pipeline.py tests/test_real_data_field.py ccbot` is empty. test_real_data_field.py passes (in the 30 passed below).
- Connectivity: no code change. The new tests are collected (`-k inbox` 14 cases, was 11). The missing-data grep is unchanged, because no ccbot/ or scripts/ change was made.

## Tests re-run (output)
```
$ python3 -m pytest -q -p no:cacheprovider                       (scratch @ dc162cf)
377 passed, 1 skipped in 58.61s
$ python3 -m pytest -q -p no:cacheprovider tests/test_pipeline_check.py
104 passed in 15.04s
$ ... -k inbox
14 passed, 90 deselected in 0.78s
$ python3 -m pytest -q -rs -p no:cacheprovider tests/test_safety.py tests/test_real_data_field.py
30 passed in 4.46s      (test_every_py_compiles_on_oldest_python ran on /usr/bin/python3.11; python3.10 not installed; no skip)
$ python3 scripts/check_handoff.py 069
PASS
```
These match 05 Round 2: 377/1, 104, and 14.

Mutations (each run in its own copy, `tests/test_pipeline_check.py -k inbox`):
```
m8  `^` removed from INBOX_PI and INBOX_HUB      1 failed, 13 passed
    FAILED tests/test_pipeline_check.py::test_inbox_code_words_mid_line_fail
m9  `^` removed from INBOX_HEAD                  1 failed, 13 passed
    FAILED tests/test_pipeline_check.py::test_inbox_heading_mid_line_fails
mt  round-1 template (git show 875158e:templates/daily-audit.md)   1 failed, 13 passed
    FAILED tests/test_pipeline_check.py::test_inbox_unfilled_template_fails
    with the `<fill in>` assert removed, so the INBOX line itself is compared:
    - INBOX: 2026-11-18.md (no project-inbox: line; no hub: SHA or UNREAD line)
    + INBOX: 2026-11-18.md (no hub: SHA or UNREAD line)
```
m8, m9 and the old template each fail a test. This closes round-1 problems 1 and 2.

## Real-data effect (diff_reports output, pasted)
not required (`templates/daily-audit.md`, `tests/test_pipeline_check.py`; neither is ccbot/realtest.py or a file it reads)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-002, RI-007, RI-008, RI-009, RI-010, RI-012, RI-013 (one line each below)
- RI-001 (ESCALATED): no new filter. The fixture counts were re-run: in xi, 0 of 2 mid-line code words match, and in xii, 0 of 1 mid-line headings match. The filled-template probe gives `none`.
- RI-002 (ESCALATED): an unfilled placeholder is no longer read as a filled line (mt). No value is defaulted, and there is no code change.
- RI-007: round 2 has its own I2 log line and 05 section. This 06 follows them.
- RI-008: the compile test ran on 3.11 (3.10 is absent).
- RI-009: all runs were in scratch, and work/070 and 070's files were untouched.
- RI-010: the INBOX check now also fails an unfilled template (xiii, mt).
- RI-012 (GUARDED): the `^` anchors are pinned by negative tests that put the pattern inside other text (xi, xii). m8 and m9 each fail. This item now meets the rule.
- RI-013 (OPEN): n/a, no realtest change.

## Pipeline line (step 2)
check_pipeline line: `069: awaiting A1 (FULL)` (real tree, after this file, 07 and the I3 log line; exit 0, `INCOMPLETE: none`, `SKIPPED: none`, `LOG TIME: none`, `REAL-DATA FIELD: none`, `INBOX: not checked (no daily report from 2026-11-18)`)

## Sent back / sent to Audit
Sent to Audit: `work/069/07-audit-task.md`. Nothing is sent back.

# Round 3 (re-verification of I2 round 3, commit 21d7591, after A1 FAIL)
Verdict: PASS (round 3; earlier rounds: FAIL round 1, PASS round 2 then A1 FAIL)

All runs were made in the scratch worktree `/tmp/claude-0/-home-claude/4cc69c4f-899b-56b8-af6f-c0c8dcf01a44/scratchpad/i3-069r3` at f77247f (branch head; merges main c10b8ae, `git diff --stat 21d7591 f77247f` is empty). Mutation copies (`git archive 21d7591`) were in `.../scratchpad/i3m069r3/<m>/`, the P1 clone in `.../scratchpad/i3p1`. All three were removed afterwards. In the real tree I wrote only this file, 07 and the I3 log line. Nothing connects to a brokerage. During this run the real tree had an uncommitted `tests/test_real_data_field.py` change (+35 lines, tests t7b/t7c). That is 070 round 3 work by another agent, since committed by 070's I2 as 4789b44. It is not part of 069, and I did not run it or touch it.

## I1 audit (plan vs research)
04 "Round 2 (after A1 FAIL)" takes A1's send-back 1 and 2 (logs/audit/2026-11-18-069.md) and A1's option (a): the gate reads the template at the commit that added the report. Nothing is added without a source. The git behaviour it relies on is quoted from git-diff (`--diff-filter=A`) and git-log (History Simplification, TREESAME parent). Each claim is then pinned by a test (xiv-b, xiv-c) rather than taken on trust. The missing-input table gives every new input (git, history depth, adding commit, template at that commit, working template) a `not checked` or exit-1 result. None of them becomes `none` (RI-002). It drops two rows with stated reasons (the EFFICIENCY item and the RI record, both for the daily review, item 036). Scope is limited to 2 files and to 069's lines.

## I2 audit (build vs plan)
`git diff --stat ad30a07 21d7591` lists scripts/check_pipeline.py (+57 incl. docstring), tests/test_pipeline_check.py (+213), work/069/05, logs/implementation/2026-11-18.md, and 070's work/070/06, 07 (from 070's I3 commit 8dfc800, not 069's). `git diff --stat 8dfc800 21d7591` = the 4 files of 069 only.
- R2-1.1: `INBOX_FROM` deleted, `INBOX_TEMPLATE` added (L230). No reference to INBOX_FROM remains.
- R2-1.2: `_inbox_gate` follows steps 1-5 in order: shallow/no-git, HEAD verify, `git log --no-renames --diff-filter=A --format=%H -1 -- <path>`, non-zero → `(<name> (git log failed), True)`, `git show <sha>:templates/daily-audit.md` matched with INBOX_HEAD, else the working-tree template with `not committed`. The return annotation is a string (a deviation 05 declares, allowed by 04).
- R2-1.3: `inbox_section` drops the date term, gives `not checked (no daily report)`, and calls the gate after picking the newest report. The content checks are unchanged.
- R2-1.4: the docstring states the template rule and gaps (u) and (v).
- R2-2: `_daily(..., template, commit, git)`, `_inbox` with `--untracked-from <HEAD>`, `@NO_GIT` on the git fixtures, vii rewritten and renamed (declared), ix wording, new tests xiv, xiv-b, xiv-c[main,t], xv, xv-b, xv-c, xvi[3], xvii, xvii-b, xviii, xix, xx, xxi. That is 14 + 16 = 30 `-k inbox` cases, as planned.
- 070 untouched: `git diff --stat 8dfc800 21d7591 -- tests/test_real_data_field.py ccbot` is empty. `git diff 8dfc800 21d7591 -- scripts/check_pipeline.py | grep -ciE 'real_data|TRIGGER|TOTAL_LINE'` gives `0`. The hunks are only at old L134, 139 (docstring), 224 (constant), 705-713 (gate and inbox_section). main() is not edited.
- Connectivity: `_inbox_gate` ← `inbox_section` ← main() INBOX block (prints, `return 1`). The 30 inbox tests are collected and run.
- Text matching (item 059, RI-012): the gate reuses INBOX_HEAD (`^## Inbox\b`, re.M) on the template text. The mid-line negative xii (m9) still pins that anchor. The gate adds no new text classifier: git results are judged by exit code, and `--is-shallow-repository` is compared as a whole stripped string (`== "true"`).
- No simulator or picker is involved (item 062 n/a).

## Tests re-run (output)
```
$ python3 -m pytest -q -p no:cacheprovider                       (scratch @ f77247f)
FAILED tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 failed, 399 passed, 1 skipped in 63.76s (0:01:03)
$ python3 -m pytest -q -p no:cacheprovider tests/test_pipeline_check.py -k inbox
30 passed, 90 deselected in 6.88s
$ python3 -m pytest -q -rs -p no:cacheprovider tests/test_safety.py
9 passed in 0.86s     (test_every_py_compiles_on_oldest_python ran on /usr/bin/python3.11; python3.10 not on PATH; no skip)
$ python3 scripts/check_handoff.py 069        (real tree)
sources count (unique URLs in 01-research.md): 2
fact-check rows: 57
totals line: 57 rows -> 50 as-is, 6 fixed, 1 removed
PASS
```
These match 05 round 3 (1 failed / 399 passed / 1 skipped, 30 inbox). The skip is exchange_calendars.

The one failure comes from `A1 FAIL: 069` only. Scratch `check_pipeline.py` at f77247f: `069: A1 FAIL (FULL; sent back, needs a later A1 PASS line (item 042))`, `A1 FAIL: 069`, every other line `none`, `INBOX: not checked (2026-11-17.md added in b268a22; its templates/daily-audit.md has no ## Inbox)`, exit 1. I confirmed this with a scratch commit (a2b2fb5) that drops only the last line of work/069/07 (A1's FAIL line):
```
$ python3 -m pytest -q -p no:cacheprovider tests/test_pipeline_check.py::test_repo_pipeline_has_no_skipped_items
1 passed in 2.68s
$ python3 scripts/check_pipeline.py
069: awaiting A1 (FULL)
A1 FAIL: none
INCOMPLETE: none
INBOX: not checked (2026-11-17.md added in b268a22; its templates/daily-audit.md has no ## Inbox)
SKIPPED: none
exit=0
```

Mutations (each in its own `git archive 21d7591` copy, `tests/test_pipeline_check.py -k inbox`):
```
m10  hub {7,40} -> {1,40}           2 failed, 28 passed: xvi[116c68], xvi[2026-11-18]
m10b hub {7,40} -> {7,}             1 failed, 29 passed: xvi[41 hex]
gate always None                   10 failed, 20 passed: vii, xiv, xiv-b, xiv-c[main], xiv-c[t], xv-c, xvii, xviii, xix, xx
gate always not checked            27 failed, 3 passed (all but viii, ix, xvii-b)
HEAD: instead of <sha>:             5 failed, 25 passed: xiv, xiv-b, xiv-c[main], xiv-c[t], xx
--diff-filter=A removed             1 failed, 29 passed: xiv-b
shallow guard off (if False)        1 failed, 29 passed: xviii
git log failure -> (..., False)     1 failed, 29 passed: xix
git log failure -> not checked      1 failed, 29 passed: xix
round-1 check_pipeline.py (ad30a07) with the new tests:
                                   12 failed, 18 passed (incl. xiv, xiv-b, xiv-c, xx; xix gives 'none')
```
Each mutation fails at least the tests 04 names. m10 is A1's surviving mutation, and it now fails 2 tests (send-back 2). With the round-1 code, xiv fails, so the new tests catch A1's P1.

Probe P1, as real merges (scratch clone `i3p1` of the a2b2fb5 scratch commit, so that only INBOX can set the exit; origin/main c10b8ae fetched as `omain`; on `omain`, `logs/audit/2026-11-18.md` = copy of 2026-11-17.md committed first):
```
--no-ff (git merge --no-ff <tip>):
A1 FAIL: none / INCOMPLETE: none / UNTRACKED CHANGE: none
INBOX: not checked (2026-11-18.md added in 330ead4; its templates/daily-audit.md has no ## Inbox)
SKIPPED: none
exit=0
--squash (git merge --squash <tip>; commit):
A1 FAIL: none / INCOMPLETE: none / UNTRACKED CHANGE: none
INBOX: not checked (2026-11-18.md added in 06ec053; its templates/daily-audit.md has no ## Inbox)
SKIPPED: none
exit=0
test_repo_pipeline_has_no_skipped_items on both merge results: 1 passed / 1 passed
then on the --no-ff result, logs/audit/2026-11-19.md = templates/daily-audit.md unfilled, committed:
INBOX: 2026-11-19.md (no project-inbox: line; no hub: SHA or UNREAD line)
exit=1
round-1 check_pipeline.py (ad30a07) on the --no-ff merge:
INBOX: 2026-11-18.md (no project-inbox: line; no hub: SHA or UNREAD line)
exit=1
```
A1's P1 is fixed. After either merge type, main stays green with a report written under the old template, on any date. The first report under the new template is checked, and an unfilled one gives exit 1. The round-1 code still reproduces A1's FAIL on the same history.

Guardrail would have caught the original error: xiv is P1's shape (an old-format report dated after 11-18, then the template change). It fails on the round-1 code (above) and under the `gate always None` and `HEAD:` mutations.

## Real-data effect (diff_reports output, pasted)
not required (`scripts/check_pipeline.py`, `tests/test_pipeline_check.py`; neither is ccbot/realtest.py or a file it reads)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-002, RI-007, RI-008, RI-009, RI-010, RI-011, RI-012, RI-013 (one line each below)
- RI-001 (ESCALATED): I re-ran the gate's dated count: on the real tree, 2026-11-17.md was added in b268a22 under a template with no Inbox, and the real-tree INBOX line agrees. 05 has the 0-of-8 count. The SHA filter is pinned on both ends (m10 fails 2, m10b fails 1).
- RI-002 (ESCALATED): no git, shallow, no report, template absent or without Inbox all give `not checked`, never `none`. A git log failure gives exit 1 (both of its mutations fail xix). Nothing is defaulted.
- RI-007: round 3 has its own I2 log line and 05 section. This 06 follows them. A1 runs next.
- RI-008: the compile test ran on 3.11 (3.10 absent). The string annotation is never evaluated.
- RI-009: all runs were in scratch. 070's code and its uncommitted test file were not touched.
- RI-010 (GUARDED; A1 proposes an occurrence for the daily review): this round is the fix. The check is keyed to the rule's own file at the report's adding commit. P1 stays `not checked` after --no-ff and --squash.
- RI-011: no merge-base is used. xiv-c pins the log through merges in both directions.
- RI-012 (GUARDED): there is no new text classifier. INBOX_HEAD stays anchored (xii) and is reused on the template.
- RI-013 (OPEN): n/a, no realtest change.

## Pipeline line (step 2)
check_pipeline line: `069: A1 FAIL (FULL; sent back, needs a later A1 PASS line (item 042))` (real tree, after this file, 07 and the I3 log line). This line is expected until A1 writes a later PASS line (item 042). It is not SKIPPED or INCOMPLETE: `INCOMPLETE: none`, `SKIPPED: none`, `LOG TIME: none`, `INBOX: not checked (2026-11-17.md added in b268a22; ...)`.

## Sent back / sent to Audit
Sent to Audit: `work/069/07-audit-task.md` (Round 3 section). Nothing is sent back.
