# 06 Verification - 072
Verdict: PASS (round 1)
Sent back to: none
<!-- On every re-verification, update the Verdict line first: it must show the latest round. -->

Verified: I1 plan work/072/04-build-plan.md against R3 hand-off work/072/03-handoff.md, and I2 build commit bb5a32e against 04. All tests and mutations ran in my own detached worktree of bb5a32e under the session scratchpad (`git worktree add --detach .../i3wt072 bb5a32e`, removed afterwards). Nothing ran in the repo tree except the read-only `check_handoff.py`, `check_pipeline.py`, `git blame` and `git show`.

## I1 audit (plan vs research)
- Every 03 map step (1-9) and decision (D1-D6) appears in 04's Rule trace with a plan line. Nothing is dropped. D5 (drift test) is kept.
- I1's four changes (C1-C4) each have a source:
  - C1, the test goes in its own file `tests/test_agent_tools.py`. Source: 071 adds I3 FAIL fixture tests to tests/test_pipeline_check.py. I checked work/071/01-research.md items 29-31; the 042 test lines it cites have shifted since, but the content is there. Moving the test changes where it lives, not what it checks.
  - C2, the parser reads YAML lists, `disallowedTools` and `Bash(...)` specifiers. I fetched https://code.claude.com/docs/en/sub-agents (2026-11-18) and found "or a YAML list", "Same format as" (for disallowedTools) and "still removes the whole tool".
  - C3, "from the repo root". Source: `scripts/check_handoff.py:47` `Path("work") / item`; `scripts/check_pipeline.py:359,364` `Path("work")`, `Path("logs")`. Confirmed.
  - C3, "the exit code does not gate R1". This follows from check_handoff's main(): it returns 0 with no 03, and an old 03 can FAIL. Reasoning from the code, consistent with it.
  - C4, plain `Log fields:` line. Source: `check_pipeline.py:354` `re.fullmatch(LOG_FORMAT[agent], fields.strip())`, so a backtick would be refused. Confirmed.
- Unsourced additions: none. The time token added to the template label (Files 6) is sourced to 072/03's own paste format.
- 04's own last line, `Log fields: FIT WITH CHANGES | 8 files planned`, matches the I1 regex. The log line I1 072 at 23:34 has the same fields.

## I2 audit (build vs plan)
Line by line against 04 "Files to create/change" (`git show bb5a32e`):
1. run-item.md
   - Anchor A: the sentence is reworded exactly as planned, and the rest of the sentence is unchanged.
   - Anchor B: the new paragraph sits between the "Before each step" and "A follow-up" paragraphs. It has all three planned edits: "from the repo root (both scripts use paths relative to it)", "After R1, take only the `sources count` line; its exit code does not gate R1 ...", and "from the text after `Log fields: ` on the last line of 02/04, unchanged".
   - The pinned strings are word-for-word.
   - The 073 realtest paragraph is untouched by bb5a32e. 073's later build (5f3f6bb) edits run-item.md, and the pinned strings are still there at 5f3f6bb (`git show 5f3f6bb:.claude/commands/run-item.md | grep -c ...` gives 1 line holding them).
2. r1-researcher.md: the line is replaced with map step 2's text, as one line. MATCH.
3. r2-improver.md: map step 3's text plus "a last line, plain text, no backticks:". MATCH.
4. r3-fact-checker.md: the step-7 line and the log line are replaced with map step 4's texts. The RESEARCH ONLY paragraph is unchanged. MATCH.
5. i1-reviewer.md: map step 5's text plus the plain-text addition. MATCH.
6. templates/research-handoff.md: the last line is now the planned label, with the time. MATCH.
7. README.md: "(run by R3, I3, A1)" becomes "(run by the orchestrator after R1 and R3, and by I3 and A1; item 072)". MATCH.
8. tests/test_agent_tools.py (new):
   - `_field` and `agent_tools` cover both forms, `disallowedTools`, the name before `(`, and the three error strings.
   - Six parser cases a-f, exactly as planned.
   - The tree test makes the planned checks: errors, the line rule, the set assert, and the two run-item strings.
   - MATCH.
- Nothing outside the plan changed: no change in scripts/, ccbot/, config/ or i2/i3/a1. The commit also holds 05 and the I2 log line (053).

Connectivity check, re-done:
- `agent_tools` is called by both tests, and `_field` by `agent_tools`.
- The template label quoted in run-item (2) is byte-identical to the template's last line. `grep -o` of the full label hits both `.claude/commands/run-item.md` and `templates/research-handoff.md`.
- r3 step 7 points to "the template's check_handoff output line", which exists.
- r2 and i1 write the `Log fields:` line, and run-item (4) reads it.
- No TODOs. No dead code.

I2's 3 deviations (05):
1. **Template label carries `<HH:MM> UTC` in run-item (2). Accepted.** Plan Files 6 adds the time to the template label. Quoting 03's older label in run-item would point at text the template no longer has. Both strings are now identical (grep above).
2. **m5 fails on the line check, not the set assert. Accepted, and the reason is confirmed.** The tree test checks lines before the set. I also checked that m5 really depends on `disallowedTools` being read: with the `tools -= ...` line disabled in the test and m5 applied, the parser case `e_disallowed_bash` fails and the tree test passes (i2 is then skipped as Bash-capable). So the parser case pins it and m5 shows it on real files.
3. **Base is before 071 (404 passed, 1 skipped). Confirmed.** I re-ran the suite at bb5a32e~1 and got `404 passed, 1 skipped in 62.97s`. 071's build is still not on the branch: HEAD is 5f3f6bb, and 071 is at 05-next.

Missing-data grep (05): `git diff --stat bb5a32e~1 bb5a32e -- ccbot/` is empty, so the 37 ccbot/ hits are all existing code. The new test file has no default-to-value pattern. This is consistent with 05.

## Tests re-run (output)
Worktree at bb5a32e, Python 3.13.18:
```
$ python3 -m pytest -q tests/test_agent_tools.py
.......                                                                  [100%]
7 passed in 0.02s
$ python3 -m pytest -q
411 passed, 1 skipped in 57.81s
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'
```
This is base 404 + 7 new tests, with no new failures. The skip is the existing exchange_calendars import skip.

Oldest-Python compile: python3.11 is on PATH and python3.10 is not. `tests/test_safety.py -k oldest`: 1 passed, not skipped.

Base and before-fix probe (worktree checked out at bb5a32e~1, with the new test file copied in):
```
404 passed, 1 skipped in 62.97s (0:01:02)
E       AssertionError: .claude/agents/i1-reviewer.md:18: runs a script with no shell (item 072)
E         .claude/agents/r1-researcher.md:19: runs a script with no shell (item 072)
E         .claude/agents/r2-improver.md:22: runs a script with no shell (item 072)
E         .claude/agents/r3-fact-checker.md:20: runs a script with no shell (item 072)
E         .claude/agents/r3-fact-checker.md:24: runs a script with no shell (item 072)
1 failed, 6 passed in 0.03s
```
The test names exactly the 5 lines 03 counted (r1 1, r2 1, r3 2, i1 1), so it would have caught the original gap.

Mutations (worktree only, each reset with `git checkout -- .`; the final `git status --short` was empty):
```
== m0
7 passed in 0.01s
== m1 old r1 line
E       AssertionError: .claude/agents/r1-researcher.md:19: runs a script with no shell (item 072)
1 failed, 6 passed in 0.02s
== m2 delete r2 tools
E       AssertionError: .claude/agents/r2-improver.md: no tools: line (inherits every tool incl. Bash, item 072)
1 failed, 6 passed in 0.02s
== m3 Bash to i1
E       AssertionError: no-shell agents changed (RULES decision, item 072): ['r1-researcher', 'r2-improver', 'r3-fact-checker']
1 failed, 6 passed in 0.03s
== m4 remove run-item paragraph
E           AssertionError: run-item.md lacks 'the orchestrator runs their commands' (item 072)
1 failed, 6 passed in 0.02s
== m5 disallowedTools Bash on i2
E       AssertionError: .claude/agents/i2-builder.md:26: runs a script with no shell (item 072)
1 failed, 6 passed in 0.02s
== m6 i1 yaml list
7 passed in 0.02s
== x1 i2 inline YAML list [.., Bash]   (I3 probe)
E       AssertionError: .claude/agents/i2-builder.md:25: runs a script with no shell (item 072)
1 failed, 6 passed in 0.02s
== x2 r1 says agent runs it, orchestrator only in other text   (I3 probe)
7 passed in 0.01s
== m5 with disallowedTools reading disabled in the test   (I3 probe, deviation 2)
FAILED tests/test_agent_tools.py::test_agent_tools_parser[e_disallowed_bash]
1 failed, 6 passed in 0.02s
```
- m1-m5 fail as planned, and m6 passes as planned.
- x1: a YAML flow list (`tools: [Read, ..., Bash]`) is not parsed. Bash is missed, but the result is safe: the test goes red and names a line. It is not a silent pass.
- x2: the line rule is a substring check. I rewrote r1 to say "you run `python3 scripts/check_handoff.py <ID>` (not the orchestrator)", and the test still passed. This is a limit of the planned check (04 Files 8 specifies "must hold `orchestrator`"), not a build defect. It is handed to Audit below.

Greps at bb5a32e (from the diff):
- "each step's agent writes its log line" is gone from .claude/.
- "the orchestrator runs their commands" and "never writes to logs/" are in run-item.md.
- "Log fields:" is in r2 and in i1.
- "run by R3, I3, A1" is gone from README.
- "must say PASS before you set READY" is gone from r3.

These match 05.

check_handoff (repo, read-only):
```
$ python3 scripts/check_handoff.py 072
sources count (unique URLs in 01-research.md): 2
fact-check rows: 52
totals line: 52 rows -> 46 as-is, 6 fixed, 0 removed
PASS
exit 0
```

check_pipeline (repo at HEAD 5f3f6bb, before this 06 existed, exit 0):
```
070: complete (FULL)
071: in progress (FULL: next 05)
072: in progress (FULL: next 06)
073: in progress (FULL: next 05)
074: in progress (FULL: next 05)
OPEN BRANCHES (not merged into HEAD):
  origin/claude/project-thread-f64g3k: items none; merges cleanly; last commit 2026-11-18 (0 days)
RULES BRANCH: none
INCOMPLETE: none
LOG TIME: none (not checked: 048: built before 045's --log rule reached main; times typed by hand, not recoverable (item 049))
UNTRACKED CHANGE: none
SKIPPED: none
```

LOG TIME for 071-074 so far (map step 9). I compared each line's stated minute with its adding commit from `git blame --date=iso-strict`. Every line is in its own commit, written per step, and none is late:
```
R1 073 23:22 <= 0b7a5a4 23:22:54 | R1 072 23:22 <= 7b5a2b5 23:22:58 | R1 071 23:23 <= 0200e23 23:23:53 | R1 074 23:24 <= 3bfa60e 23:24:55
R2 072 23:26 <= 414504f 23:26:03 | R2 071 23:26 <= c28b1d4 23:26:55 | R2 073 23:27 <= b90be92 23:27:25 | R2 074 23:27 <= 567788e 23:27:37
R3 072 23:31 <= 00f4fee 23:31:27 | R3 073 23:34 <= ce7f0be 23:34:16 | R3 074 23:38 <= 57a0e9e 23:38:09 | R3 071 23:38 <= bbd48c8 23:38:23
I1 072 23:34 <= ea6ebb9 23:34:29 | I1 073 23:37 <= 21445ed 23:37:29 | I2 072 23:42 <= bb5a32e 23:42:26 | I1 074 23:43 <= 6638526 23:43:19
I1 071 23:45 <= 516c497 23:45:53
```
- 072's own lines run R1 23:22, R2 23:26, R3 23:31, I1 23:34, I2 23:42, in step order.
- The R3 and I1 fields match 03's totals line and Status line, and 04's `Log fields:` line.
- 073's I2 line (from 5f3f6bb) is outside this check, which covers 072.

Which run-item.md 072 is built on (run-item item 034): all four items are on daily-fixes/2026-11-18. 072 (bb5a32e) was built before 073's I2 (5f3f6bb), and 073 was built on top of it. `RULES BRANCH: none`.

## Real-data effect (diff_reports output, pasted)
not required (`git diff --stat bb5a32e~1 bb5a32e`: .claude/agents/i1-reviewer.md, .claude/agents/r1-researcher.md, .claude/agents/r2-improver.md, .claude/agents/r3-fact-checker.md, .claude/commands/run-item.md, README.md, logs/implementation/2026-11-18.md, templates/research-handoff.md, tests/test_agent_tools.py, work/072/05-build-report.md; no ccbot/realtest.py, costs.py, expiries.py, config.py, pricing.py, config/ or data/real/ file)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-002, RI-007, RI-009, RI-010, RI-012, RI-013, RI-008, RI-004, RI-005, RI-006 (RI-003, RI-011 not applicable)
- RI-001 (ESCALATED): the selector count was re-measured, not taken on trust. The before-fix probe names exactly 5 lines, the after-fix run has 0, and the no-Bash set has 4 of 7 files. The feasibility test was re-run, and the numbers in 03/04/05 match it.
- RI-002 (GUARDED): this is not a BUG item and has no removed default to put back. The parser's absent inputs (no frontmatter, no `tools:`, empty `tools:`) each give a named error and are never read as "no Bash". Parser cases a-c and m2 confirm this. There is no ccbot/ change.
- RI-007 (GUARDED): Scope FULL, and all steps 01-05 exist. The code, test and rules changes are committed together with 05 in bb5a32e. `UNTRACKED CHANGE: none`.
- RI-009 (GUARDED): run-item.md is shared with 073. 073 was built on top of 072 on the same branch, and 072's paragraph survives at 5f3f6bb. The test file is separate from 071's test_pipeline_check.py.
- RI-010 (GUARDED): this item's purpose. The text duty now has a script check: the before-fix probe fails, and m1-m5 fail. `LOG TIME: none` and `INCOMPLETE: none`. All 17 lines for 071-074 were checked against their commits (above).
- RI-012 (GUARDED): the item has no error or reply classifier. The drift test does match the substring "orchestrator" on a line, though, and probe x2 shows that a line with "orchestrator" in other text passes. Because this is a lint of rule text and not an error or reply classifier, I do not FAIL the item on item 059. It is handed to Audit as a possible extension.
- RI-013: no realtest change, so no diff_reports run is needed.
- RI-008: stdlib plus pytest only. The python3.11 compile test passed (not skipped). python3.10 is not on PATH.
- RI-004 / RI-005 / RI-006: the example log fields in r2/i1 and 04's last line fit LOG_FORMAT. The counts in 05 and here come from command output.
- 062 picker rule: not applicable (no simulator or replay).

## Pipeline line (step 2)
check_pipeline line: `072: awaiting A1 (FULL)`
(re-run after this file, 07 and the I3 log line `23:48 | I3 | 072 | PASS | sent to audit: yes` existed; exit 0; `INCOMPLETE: none`, `LOG TIME: none (not checked: 048 ...)`, `UNTRACKED CHANGE: none`, `SKIPPED: none`, `RULES BRANCH: none`. Before 06 existed the line was `072: in progress (FULL: next 06)`.)

## Sent back / sent to Audit
Sent back: none. Sent to Audit: yes (work/072/07-audit-task.md).
Notes for Audit (not defects of the build against the plan):
1. Probe x2: the line rule is a substring test, so a contradicting sentence that mentions the orchestrator passes.
2. Probe x1: a YAML flow list `[..]` is not parsed. Bash is missed, which fails loud rather than silently.
3. The I2 log field `tests 411/411` leaves out the 1 skipped test (the suite reports 411 passed, 1 skipped). The format accepts it, but 069/070's and 073's I2 lines count skips in the total (073: `tests 414/415`).
4. The PR is a RULES BRANCH (.claude/, templates/), so the person must approve it.
