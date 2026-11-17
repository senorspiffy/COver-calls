# 06 Verification - 069
Verdict: FAIL (round 1; earlier rounds: none)

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
