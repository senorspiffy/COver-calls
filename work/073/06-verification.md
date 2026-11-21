# 06 Verification - 073
Verdict: PASS (round 1; earlier rounds: none)
Sent back to: none

Verified head: 5f3f6bb (I2 build), base bb5a32e. All tests and mutations were run by I3 in its own clean detached worktree of 5f3f6bb (`/tmp/claude-0/-home-claude/17414523-55e9-552d-bf38-90b98a4fb4ca/scratchpad/wt-073-i3`, removed afterwards), never in the repo tree. Python 3.13.18.

## I1 audit (plan vs research)
- 03 map step 1 (i3-verifier.md sentence) -> 04 Files 1. The 04 text equals 03's "append exactly" text word for word (checked by script: the 03 quote is a substring of the built file, True).
- 03 map step 2 (run-item.md sentence) -> 04 Files 2, word for word as 03 (same script check, True).
- 03 map step 3 (template sentence) -> 04 Files 3 with change C2 (same `--max-rows`, fallback to 05's pasted lines). C2 is sourced: scripts/diff_reports.py `diff_csv` cuts only the printed row lines to `max_rows` (`... <n> more`) while the counters count every row, and the TOTAL line is built from the counters; default `--max-rows` is 20. I re-read these lines: TOTAL is independent of `--max-rows`, a whole-output `cmp` is not. The sourcing holds.
- C1 (new test t23, +3 ids, files 3 -> 4) is a change against 03 map step 5 ("no test added"). It is sourced to RI-010's root cause ("duties exist only in the agent text ... no script checks them", logs/recurring-issues.md L120) and is disclosed in the plan's Rule trace (step 5 total is base + 3). Not an unsourced addition.
- C3 (text anchors instead of line numbers) is a build method only; no content change.
- 03 map step 4 (no change to i2-builder, build-report, check_pipeline, logs) -> 04 "Not changed" list. Step 6 follow-ups -> 05 `Follow-ups for A1`. D1-D4 each traced; D3 DROPPED with a reason (071 edits check_pipeline.py; name check proves only names differ). Missing inputs rows each traced. No unsourced additions found.

## I2 audit (build vs plan)
`git diff bb5a32e 5f3f6bb --stat -- . ':!work' ':!logs'` (I3 re-run):
```
 .claude/agents/i3-verifier.md |  2 +-
 .claude/commands/run-item.md  |  2 +-
 templates/verification.md     |  2 +-
 tests/test_real_data_field.py | 16 ++++++++++++++++
 4 files changed, 19 insertions(+), 3 deletions(-)
```
Exactly the 4 planned files (04 "Files planned: 4 (4 changed, 0 new)").
- Files 1: sentence appended on the same line directly after "run the base too (item 068)."; rest of step 2 unchanged (diff shows one line changed, old text kept as prefix). Word-for-word match with 04: True (628 chars).
- Files 2: sentence appended after "come only from the full run (item 068)."; 072's text intact. Match: True (364 chars).
- Files 3: only the last sentence of the comment replaced; comment still ends ` -->` and keeps `from item 070 check_pipeline.py requires`. Match with 04's C2 wording: True (441 chars).
- Files 4: t23 is placed after t7d, text identical to 04's code block (diff compared by eye, line by line: parametrize ids i3/run-item/template, must/must_not lists, docstring, asserts).
- Greps (I3 re-run in the worktree):
```
grep -c "item 073" .claude/agents/i3-verifier.md = 1
grep -c "(item 068)" .claude/agents/i3-verifier.md = 1
grep -c "make one full run at the head commit" .claude/agents/i3-verifier.md = 1
grep -c "item 073" .claude/commands/run-item.md = 1
grep -c "counts as the base only if" .claude/commands/run-item.md = 1
grep -c "the orchestrator runs their commands" .claude/commands/run-item.md = 1
grep -c "same dirs" templates/verification.md = 0
grep -c "item 073" templates/verification.md = 1
grep -c "from item 070 check_pipeline.py requires" templates/verification.md = 1
```
All equal 04's expected values.
- Connectivity re-done: t23 is collected (3 ids run below); each new sentence is read by its consumer (I3 reads i3-verifier step 2 and the template comment; the orchestrator reads run-item.md) and is pinned by one t23 id. No TODO, no new file, no ccbot/ change (`git diff --stat bb5a32e 5f3f6bb -- ccbot/` empty), so the missing-data grep has no new hit.
- 05's deviation (built before 071, by the orchestrator's direction) is disclosed; 071's planned edits (i3 step 5, `Sent back to:` line) use other anchors. No conflict at 5f3f6bb.
- Minor (not a FAIL): 05's RI list marks RI-004/RI-005 "not applicable", while 04 did replay the 068 worked example. Nothing in 05 depends on it.

## Tests re-run (output)
```
$ python3 -m pytest -q
414 passed, 1 skipped in 62.24s (0:01:02)
$ python3 -m pytest -q -rs | grep -i skip
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'
```
414 = 05's base 411 + 3 (t23), same as 05. The one skip is the pre-existing calendar test, not the Python-version test.
```
$ python3 -m pytest -q tests/test_safety.py -k oldest -rs
1 passed, 8 deselected in 0.11s
```
`test_every_py_compiles_on_oldest_python` ran (python3.11 on PATH at /usr/bin/python3.11; python3.10 not on PATH). Not skipped.
```
$ python3 -m pytest tests/test_real_data_field.py -k "t7d or t23" -v
tests/test_real_data_field.py::test_t7d_cutoff_constant_matches_template_comment[templates/build-report.md] PASSED
tests/test_real_data_field.py::test_t7d_cutoff_constant_matches_template_comment[templates/verification.md] PASSED
tests/test_real_data_field.py::test_t23_own_head_run_text[i3] PASSED
tests/test_real_data_field.py::test_t23_own_head_run_text[run-item] PASSED
tests/test_real_data_field.py::test_t23_own_head_run_text[template] PASSED
5 passed, 30 deselected
```
check_handoff (I3 re-run, exit 0):
```
$ python3 scripts/check_handoff.py 073
sources count (unique URLs in 01-research.md): 0
fact-check rows: 70
totals line: 70 rows -> 59 as-is, 10 fixed, 1 removed
PASS
```
Mutations m1-m3 (04 Tests and checks; I2 left them to I3). Each in the scratch worktree, each restored from a backup copy before the next; `git status --short` empty afterwards and t23 back to 3 passed:
```
m1: 073 sentence deleted from .claude/agents/i3-verifier.md (grep "item 073" -> 0)
FAILED tests/test_real_data_field.py::test_t23_own_head_run_text[i3] - Assert...
1 failed, 2 passed, 32 deselected

m2: old sentence "I3 re-runs diff_reports.py on the same dirs and compares its TOTAL line with 05's." put back in place of the new one (grep "same dirs" -> 1)
FAILED tests/test_real_data_field.py::test_t23_own_head_run_text[template] - ...
1 failed, 2 passed, 32 deselected
E   AssertionError: templates/verification.md: missing "never 05's head dir (item 073)"

m2b (extra, to test must_not on its own): new sentence kept, old "same dirs" sentence appended after it
E   AssertionError: templates/verification.md: still has 'same dirs'
1 failed, 34 deselected

m3: "never give I3 the head run made for 05, " removed from .claude/commands/run-item.md (grep -> 0)
FAILED tests/test_real_data_field.py::test_t23_own_head_run_text[run-item] - ...
1 failed, 2 passed, 32 deselected
```
m2 as written fails first on the `must` list (the replacement also removes the new text), so m2b shows the `must_not` check also bites by itself.

Step 3 (BUG checks): 073 is an IDEA, not a BUG; no removed default (RI-002 mutation n/a), no feasibility test added (the 9-path scope is pinned by the existing test_t9, which passes in the full suite), no data-hole check, no 001 rule changed, no text classifier (t23 is a fixed-string presence test on rule text), no simulator/replay (item 062 n/a).

## Real-data effect (diff_reports output, pasted)
not required (.claude/agents/i3-verifier.md, .claude/commands/run-item.md, templates/verification.md, tests/test_real_data_field.py). Confirmed: none of these is in TRIGGER (`ccbot/realtest.py`, `ccbot/costs.py`, `ccbot/expiries.py`, `ccbot/config.py`, `ccbot/pricing.py`, `config/default.json`, `config/tickers.json`, `config/holidays.json`) or under TRIGGER_DIRS (`data/real/`), scripts/check_pipeline.py L183-186; `REAL-DATA FIELD: none`. So the new own-head-run rule does not apply to 073 itself: 0 full runs, no head or base run made.

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-002, RI-004, RI-005, RI-006, RI-007, RI-009, RI-010, RI-012, RI-013 (RI-003, RI-008, RI-011: not applicable)
- RI-001 (ESCALATED, the only non-GUARDED entry): the one scope rule cites 9 paths; I re-read TRIGGER (8) + TRIGGER_DIRS (1) in scripts/check_pipeline.py L183-186 = 9, and test_t9 passes. No market filter added.
- RI-002: no value defaulted; every absent I3 input in 04's Missing inputs gets n/a/unknown text, a re-run or FAIL, never a copy of 05's value. No ccbot/ change.
- RI-004/RI-005: replayed the 068 example on the built text: 068's head run `068-after` was "the head run made for 05", so "never use the head run made for 05, whoever made it" fires. Cost numbers in 04 (822.704 s x 2/3/4 = 27.42/41.14/54.85 min) re-derived, match.
- RI-006: file count (4) and suite delta (+3) taken from command output above, not by hand.
- RI-007: rule and test edits are in one commit with 05 (5f3f6bb); `UNTRACKED CHANGE: none`.
- RI-009: shared files (071, 072) edited by text anchor; 072's grep = 1; I did no `git add -A`, stash, reset or checkout in the repo tree.
- RI-010: the new text duty has a check (t23), and m1-m3 show it fails when any text is removed.
- RI-012: no classifier added; t23 matches fixed rule sentences in fixed files, not free-text replies.
- RI-013: the template now asks for I3's own head dir and the same `--max-rows` for the whole-output compare.
- RI-003 (no calendar), RI-008 (test file compiles with python3.11, and the oldest-Python test passed), RI-011 (no branch diff): not applicable.

## Pipeline line (step 2)
check_pipeline line: `073: awaiting A1 (FULL)` (after 06, 07 and the I3 log line; also INCOMPLETE: none, SKIPPED: none, REAL-DATA FIELD: none, LOG TIME: none for 073, UNTRACKED CHANGE: none)

## Sent back / sent to Audit
Sent back to: none. Sent to Audit: yes (work/073/07-audit-task.md). This is a RULES change (.claude/ and templates/ are RULE_PATHS): the person must OK the PR. RULES BRANCH shows `none` only because daily-fixes/2026-11-18 is not pushed yet.
