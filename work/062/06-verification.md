# 06 Verification - 062
Verdict: PASS (round 2; earlier rounds: FAIL round 1)
<!-- On every re-verification, update this line first: it must show the latest round. -->
## I1 audit (plan vs research)
04 follows 03's map steps 1-8 and every correction row (01 design D: the waiver regex is replaced by the steps ⊇ {04,05,06} + who + date test; 01 design A: Scope and Waived are read at the tip). The changes from 03 are simplifications with a reason: (a) `parse_request` split, (b) `_walk` shared with 053 (03 called it `_units`), (c) one pure `_research_code`, (d) the edge case where classify already gives SKIPPED for an `(I2, ...)` waiver of 06, (e) a flagged ID with no request.md dir. Nothing is added without a source. The line-number drift 04 notes (`changed()` L318-322, not L316-325) is real and changes nothing.

One error in 04, which is the cause of the FAIL below: the mutation list says "Drop the who check → (2b) and its unit case fail." Both of those inputs have no `(person, <date>:` anywhere, so the date regex rejects them whether or not the who check is there. 04 does not name an input where only the who check decides.

## I2 audit (build vs plan)
I read the 530bd92 diff against 04 steps 1-7, and it matches them line by line:
- Constants and `_build_waived` are in step 1.
- `_research_code` is step 2, using paths only, with the LEGACY skip, the missing request.md flag and gap (g).
- `_walk`, `untracked_changes(walked=)`, `research_code`, the main loop override, the after-loop print and the `RESEARCH CODE:` line are step 3.
- The `requests` cache, the per-ref unit and the merged detail are step 4.
- The docstring with gaps (g)-(j) is step 5.
- `_branch_adds(extra=)`, the new tests and the `RESEARCH CODE: none` assert are step 6.
- The three rule sentences in step 7 match 03 map step 7 word for word.

Merging (2a) and (2b) into one test is a declared deviation that keeps the plan's assertions.

I re-did the connectivity check and agree with 05. Every new function has a caller (`parse_request` ← `read_request`, `_build_waived`, `_research_code`; `_walk` ← `main`, `untracked_changes`, `research_code`). Every branch ends in a named result. 05 gives a reason for the one grep hit (`is not None and`): a missing request.md is flagged, never passed.

## Tests re-run (output)
```
$ python3 -m pytest -q
254 passed, 1 skipped in 24.32s
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars'
$ python3 -m pytest -q tests/test_safety.py
9 passed            (python3.11 is on PATH, so test_every_py_compiles_on_oldest_python ran, not skipped)
$ python3 scripts/check_handoff.py 062
sources count (unique URLs in 01-research.md): 0
fact-check rows: 50
totals line: 50 rows -> 45 as-is, 5 fixed, 0 removed
PASS
$ git fetch origin && python3 scripts/check_pipeline.py      (exit=0)
062: in progress (FULL: next 06)
BRANCH SKIPPED: 061 (origin/claude/project-thread-ltyppm: RESEARCH ONLY: changes ccbot/realtest.py scripts/fetch_real_data.py tests/test_realtest.py with no 04-06; needs Scope FULL or "Waived: 04 05 06 (person, <date>: <why>)" on the item's single Waived: line (item 062))
UNTRACKED CHANGE: none
RESEARCH CODE: none
SKIPPED: none
```
Feasibility (RI-001), re-run: the HEAD flag rule gives 0 (`RESEARCH CODE: none`; 04 expected 0). The branch flag rule gives 1 (`BRANCH SKIPPED: 061`; 04 expected 1). The waiver rule passes 2 of the 6 parametrized strings (the test passes).

Mutation M3 (drop `who == "person"`), run in a scratch copy and deleted afterwards:
- `tests/test_pipeline_check.py` gives **69 passed**, so I reproduce I2's result: the mutation survives.

I2's explanation, "the date regex already requires person", is **wrong**. `WAIVE_BUILD_BY_PERSON.search(waived_line)` searches the whole Waived line, including the why text, while `who` is the text after the first `(`. A probe on the real code:
```
Waived: 04 05 06 (I2, 2026-11-13: copied from 061 "(person, 2026-11-12: ok)")
  parse_request -> who 'i2'
  _build_waived (as built)        -> False
  without the who check (M3)      -> True
```
So the who check is the only guard against a non-person waiver that quotes the person's form. RI-012 and the i3 step 3 rule from item 059 cover exactly this: a match on text needs a negative test with the pattern inside other text. The existing negative test, `(I2, 2026-11-13: person said ok)`, holds the word "person" but not the pattern `(person, <date>:` that the regex matches, so it cannot tell the two checks apart.

Fix shown to work, in the same scratch copy:
- I added the parametrized case `("Waived: 04 05 06 (I2, 2026-11-13: copied \"(person, 2026-11-12: ok)\")", False)`.
- With M3 applied, that case fails: **1 failed, 69 passed**.
- After restoring the code, the suite gives **70 passed**.

## Recurring issues checked (step 0)
Recurring issues checked: RI-001 (feasibility counts re-run: 0 / 1 / 2 of 7 in round 2, 2 of 6 in round 1; they match 04 and 05), RI-007 (this item; 061 is flagged BRANCH SKIPPED on the real ref, HEAD fixture (3) gives SKIPPED exit 1; guardrail in place), RI-011 (branch side uses `changed()` from merge-tree; 061 reported against its merge-tree result, not HEAD...ref), RI-012 (round 1 FAIL: the who check had no negative test with `(person, <date>:` inside another who's text, so M3 survived; round 2: the copied-bracket case is added and M3 fails 1 test); GUARDED ones looked at: RI-002 (missing request.md/git/cutoff each give a named result; the one grep hit has a reason), RI-008 (python3.11 compile ran, no 3.12-only syntax), RI-010 (log lines through `--log`)

## Pipeline line (step 2)
check_pipeline line: `062: in progress (FULL: next 07)` (round 2; in round 1 it was `next 06`, run before this file existed)

## Sent back / sent to Audit
Round 1: sent back. Not sent to Audit, and no 07 is written.
1. **To I2.** In `tests/test_pipeline_check.py::test_build_waiver_needs_person_date_and_all_three`, add the negative case `("Waived: 04 05 06 (I2, 2026-11-13: copied \"(person, 2026-11-12: ok)\")", False)`. Paste in 05 that M3 (drop `who == "person"`) now fails ≥ 1 test. Correct 05's sentence "the date regex ... already requires person ... so the who check is redundant": it is not redundant, because the regex is a search over the whole line.
   - Optional, the builder's choice: also anchor the regex to the first bracket, e.g. `re.match(r"[0-9 ,]*\(\s*person\s*,\s*\d{4}-\d{2}-\d{2}\s*:", line_after_Waived)`, so that both checks guard the same position. The new test is required either way.
2. **To I1, for the record.** 04's mutation line "Drop the who check → (2b) and its unit case fail" is wrong for the reason above. When the fix is in, update it to name the new case.

No other problems found. The rest of the build matches 04, and the full suite, check_handoff (PASS) and check_pipeline (exit 0, `BRANCH SKIPPED: 061`, `RESEARCH CODE: none`) are as expected.

## Round 2 (I2 commit 2343440)
Change checked: `git diff 530bd92 2343440 -- scripts` is empty, so the code is unchanged. The diff adds one parametrized case to `test_build_waiver_needs_person_date_and_all_three`: `('Waived: 04 05 06 (I2, 2026-11-13: copied "(person, 2026-11-12: ok)")', False)`. Both round-1 send-backs are handled:
- 05 replaces the wrong "redundant" sentence and pastes the M3 rerun.
- 04's mutation line now names the new case.
- The waiver feasibility count is 2 of 7 in both 04/05 and the test.

Leaving the regex unanchored is acceptable. 05 shows that with an anchored regex M3 survives again, because the anchored regex alone rejects the copied bracket. As built, each of the two checks has its own failing case.

Mutations re-run by I3 in a scratch copy (deleted afterwards; the repo was not touched), on `tests/test_pipeline_check.py`:
```
M3 drop who == "person"            : 1 failed, 69 passed
M2 drop WAIVE_BUILD <=             : 1 failed, 69 passed
M4 drop the date regex             : 1 failed, 69 passed
M1 drop the RESEARCH ONLY Scope test: 3 failed, 67 passed
restored                           : 70 passed
```
Tests and checks, re-run:
```
$ python3 -m pytest -q
255 passed, 1 skipped in 25.25s
SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars'
(test_safety compile test ran with python3.11; not skipped)
$ python3 scripts/check_handoff.py 062
PASS   (50 rows -> 45 as-is, 5 fixed, 0 removed)
$ git fetch origin && python3 scripts/check_pipeline.py      (exit=0)
062: in progress (FULL: next 07)
BRANCH SKIPPED: 061 (origin/claude/project-thread-ltyppm: RESEARCH ONLY: changes ccbot/realtest.py scripts/fetch_real_data.py tests/test_realtest.py with no 04-06; needs Scope FULL or "Waived: 04 05 06 (person, <date>: <why>)" on the item's single Waived: line (item 062))
INCOMPLETE: none
UNTRACKED CHANGE: none
RESEARCH CODE: none
SKIPPED: none
```
Round 2 recurring issues checked: RI-012 is now met, because the copied `(person, <date>:` bracket inside an I2 waiver is a negative test that kills M3. RI-001 was re-run and gives 0 / 1 / 2 of 7. RI-007 and RI-011 are unchanged from round 1.

Round 2 pipeline line: check_pipeline line: `062: in progress (FULL: next 07)`

Round 2: PASS, sent to Audit (work/062/07-audit-task.md).
