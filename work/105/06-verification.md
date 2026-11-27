# 06 Verification - 105
Verdict: PASS (round 1)
Sent back to: none
Scratch dir: /tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad/i3-105-r1-783vtu1p

Made with `python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="i3-105-r1-", dir="/tmp/claude-0/-home-claude/9aa805a6-ba6b-5ce4-bc2b-bc0a977a3e2c/scratchpad"))'`. Inside it, made with `git worktree add --detach`: `head/` at a32037d (I2's build commit), `base/` at 1662121 (05's build base) and `main/` at origin/main 1d0de33 (for the RULES BRANCH check only). Also `tools/` (mutation script, checker outputs) and `pyc/` (a fresh PYTHONPYCACHEPREFIX per run). Every test run used PYTHONDONTWRITEBYTECODE=1. No `git stash` anywhere. No test ran in the main checkout (109 is being built there). Each probe was restored with `git checkout HEAD -- <file>` inside the scratch worktree; `git status --short | wc -l` printed 0 in `head/` and in `base/` afterwards. The clone is full (`git rev-parse --is-shallow-repository` printed `false`).

## I1 audit (plan vs research)
The plan follows 03's map steps 1-6 row by row (04 Rule trace has one row per map step, Missing-inputs row and Self-check row). I checked each:
- Map step 1 (`_person_dated` helper, used by `_build_waived` and `_person_waived_before_i2`, comment update): Files 1, same body and docstring content as 03.
- Map step 2 (classify `dated`, `blocked = ... not dated`, new message, module docstring text, parse_request unchanged): Files 1, word for word from 03 step 2.
- Map step 3(a)-(d): Files 2. The 11 rows of 03 are kept with the same setups and expected statuses; the detail strings are spelled out (C2).
- Map step 4 (M-a to M-g): Tests 4, plus M-h.
- Map step 5 (full-output diff, suite, py_compile 3.11): Tests 2, 3, 5.
- Map step 6 (rule text proposal in the PR, no edit): Rule text section.

Additions beyond 03, each with a source:
- C1 rows R12 (empty group 2) and R13 (second Waived line): both are rows of 03's own Missing inputs table that had no test. Sourced to that table. M-h goes with R13.
- C3 kill-list corrections: re-derived from test code; observed results below confirm most of them (see deviations).
- C4 RULES BRANCH / RULE_PATHS note: sourced to RULE_PATHS in check_pipeline.py and item 049.
- Extra research 1-3: Python `re` docs URL with fetch date (anchor, soft-deprecation of match, dot vs newline, IGNORECASE, Unicode `\d`), and a hand-traced tab edge with no code change. The Unicode-digit gap goes only into a docstring.

No unsourced addition. Two plan expectations were wrong (not unsourced, but mistaken); neither changes code or a test:
1. Tests 5 expected the head run's RULES BRANCH line to name scripts/check_pipeline.py "on this branch". RULES BRANCH reads `git branch -r --no-merged HEAD` (open_branches), so a branch's own rule change is never shown from a checkout of that branch. I checked the line where it does show: in my `main/` worktree at origin/main 1d0de33, `python3 scripts/check_pipeline.py` prints `RULES BRANCH: origin/daily-fixes/2026-11-25 changes scripts/check_pipeline.py; build new items on top of it (item 049)` and `OPEN BRANCHES (not merged into HEAD):` / `origin/daily-fixes/2026-11-25: items 105, 106, 107, 108, 109, 110; merges cleanly; ...`. So the person does see it from main. (108 and 110 also change that file on this branch, so the line does not single out 105.)
2. Tests 4 kill lists: M-a does not kill R12 (plan said so) but also kills N-b and N-d (plan omitted); M-h does not kill `_build_waived` case 6 (`_build_waived` takes its steps from the first line only, `[02]`, so `WAIVE_BUILD <= set(steps)` is False under either reader). Every mutation is still killed by a row of the new test.

## I2 audit (build vs plan)
`git diff --stat 1662121 a32037d -- scripts tests ccbot config templates .claude`: `scripts/check_pipeline.py | 44`, `tests/test_pipeline_check.py | 51`, 2 files changed, 75 insertions(+), 20 deletions(-). Matches 05.

Line by line against 04 Files 1-2 (read in `git diff 1662121 a32037d`):
- `_person_dated(text)` above `_build_waived`: body `m = WAIVED_LINE.search(text)` / `return bool(m and PERSON_DATED.match(m.group(2)))`; docstring has every bullet the plan lists (first line only, anchored RI-012, re.match not prefixmatch RI-008, format check not proof, case-sensitive, date not validated incl. 2026-13-45 and Unicode digits, later line never read). As planned.
- `_build_waived`: `return WAIVE_BUILD <= set(steps) and _person_dated(text)`; docstring names `_person_dated`. As planned.
- `_person_waived_before_i2`: local `m` dropped; condition starts `_person_dated(req_text) and pre and ...`. As planned.
- Item 093 comment: PERSON_DATED used only through `_person_dated` (093, 100, from 105 classify). As planned.
- `classify`: `(waived, waived_line, _)`, `dated = _person_dated(req_text)`, `blocked = [s for s in waived if s in PERSON_ONLY and not dated]`, message `... can be waived only by the person, as (person, <date>: <why>){extra}`; FAST check unchanged. As planned.
- Module docstring sentence replaced with 03 step 2's text. As planned.
- `parse_request`: code unchanged, docstring line added. As planned.
- Tests: `PERSON_ONLY_MSG`, `SETUP_105`, `test_person_only_waiver_needs_dated_form` R1-R13 with exactly the plan table's setups, rows and expected tuples (R13's row contains the `\n` second Waived line, and its expected detail is the first line only); placed right after `test_fact_check_and_verification_waivable_only_by_person`; plan docstring. 107/108 asserts updated to the plan's strings; `SKIPPED: 107, 108` and `code == 1` unchanged. N-b and N-d flipped to True with the item-105 comment; docstring sentence added. As planned.
- Not changed: templates/request.md, .claude/commands/run-item.md (as planned; proposal goes in PR text).

Connectivity, re-done: in `git show a32037d:scripts/check_pipeline.py`, `_person_dated(` has 3 callers (L661 `_build_waived`, L674 `_person_waived_before_i2`, L782 `classify`) plus the def (L641); `PERSON_DATED.` has one code use (L650, inside `_person_dated`). `who` in parse_request (L634, L638) has no reader in scripts/ any more; the only remaining unpack that names it is tests/test_pipeline_check.py L1963 (`scope, _, (waived, line, who) = cp.parse_request(text)`, an existing parse_request test), which is why the 3-tuple is kept. Other `parse_request(` callers (L660, L672, L760, L768, L781, L1323, L2080) use index 0 or unpack 3-tuples, all unaffected. Output: classify's (status, detail) is printed per item and in `SKIPPED:` (exit 1). Every branch ends in a defined result (no Waived line, empty group 2 R12, unreadable request.md, undated/other-who, non-03/06 waiver R11).

05's grep reasons checked: the missing-data grep over ccbot/ has only pre-existing hits and `git diff --stat 1662121 a32037d -- ccbot/` is empty; the diff's only `<=` are set-subset tests. Agreed.

05 deviation note on RULES BRANCH: 05 says the line reads `none` because "this branch is not pushed". That reason is wrong. `git reflog show origin/daily-fixes/2026-11-25` shows pushes at 23:24 (1d0de33), 23:54 (40b2bd2) and 00:10 (a32037d), so the branch was on origin before the build. The real reason is the `--no-merged HEAD` rule above (from 05's `head/`, origin at 40b2bd2 differed from 1662121 only in work/ and logs/, so it had no rule files). 05's conclusion (no code change needed; the line shows on other checkouts) is correct and I confirmed it from origin/main. This is a wrong explanation in 05, not a build defect; not sent back.

Data-hole edges: no data window in this item. The text analogue was checked: before the first value (no Waived line: normal rules; empty group 2: R12), after the last (a second Waived line is never read: R13, M-h).

RI-012 negative text-match test (item 059): present. R3 (dated person form quoted inside an undated waiver) and R4 (`(person) x (person, ...)`) put the pattern inside other text; M-b (`.search`) is killed by R3 and R4. Simulator rule (item 062): N/A, no simulator or replay.

Rule the person follows (001): this does not change a 001 strategy rule. It tightens a process rule. The rule text in scripts/check_pipeline.py's module docstring (a RULE_PATH) changed in this same commit. templates/request.md L5 and run-item.md L10 still say only `<who> = person`; 04 puts the proposed wording in the PR text for the person, and a new item if approved. No request is open for those two edits yet: listed in 07 for Audit.

## Tests re-run (output)
All in `head/` at a32037d (or `base/` where said), Python 3.13.18, `env -u PYTEST_ADDOPTS PY_COLORS=0 python3 -m pytest -q -p no:cacheprovider`.

1. Full suite at head:
```
1027 passed, 1 skipped in 209.63s (0:03:29)
```
Same as 05 (`1027 passed, 1 skipped`). A second full run with `-rs`: `SKIPPED [1] tests/test_calendar.py:110: could not import 'exchange_calendars': No module named 'exchange_calendars'` / `1027 passed, 1 skipped in 207.81s (0:03:27)`. The skip is not the oldest-Python compile test: `tests/test_safety.py` alone gives `9 passed in 2.17s` (python3.11 is on PATH at /usr/bin/python3.11; python3.10 is not).
2. `python3.11 -m py_compile scripts/check_pipeline.py tests/test_pipeline_check.py`: exit 0.
3. Focused group at head (`-k "person_only_waiver_needs_dated_form or fact_check_and_verification_waivable or batch_waiver_not_excused_stays_strict"`): `20 passed, 514 deselected in 5.31s`.
4. Guardrail would have caught the original error: head's tests/test_pipeline_check.py copied onto base code in `base/` (restored afterwards with `git checkout HEAD -- tests/test_pipeline_check.py`), same `-k`:
```
FAILED tests/test_pipeline_check.py::test_fact_check_and_verification_waivable_only_by_person
FAILED tests/test_pipeline_check.py::test_person_only_waiver_needs_dated_form[R1]
FAILED tests/test_pipeline_check.py::test_person_only_waiver_needs_dated_form[R2]
FAILED tests/test_pipeline_check.py::test_person_only_waiver_needs_dated_form[R3]
FAILED tests/test_pipeline_check.py::test_person_only_waiver_needs_dated_form[R4]
FAILED tests/test_pipeline_check.py::test_person_only_waiver_needs_dated_form[R5]
FAILED tests/test_pipeline_check.py::test_person_only_waiver_needs_dated_form[R6]
FAILED tests/test_pipeline_check.py::test_person_only_waiver_needs_dated_form[R7]
FAILED tests/test_pipeline_check.py::test_person_only_waiver_needs_dated_form[R12]
FAILED tests/test_pipeline_check.py::test_person_only_waiver_needs_dated_form[R13]
FAILED tests/test_pipeline_check.py::test_batch_waiver_not_excused_stays_strict[N-b]
FAILED tests/test_pipeline_check.py::test_batch_waiver_not_excused_stays_strict[N-d]
12 failed, 8 passed, 514 deselected in 3.33s
```
The A1 finding (undated `Waived: 03 06 (person)` accepted) is exactly R1, which gives `in progress` on base and fails. Same as 05 and as 04 Tests 1 expects.
5. Mutations, re-run by me in `head/` with `tools/mut.py` (exact-string replace, each target asserted to occur once), one at a time, whole `tests/test_pipeline_check.py` (534 tests), restored with `git checkout HEAD -- scripts/check_pipeline.py` after each. Control, unmutated: `534 passed in 118.36s (0:01:58)` (in my worktree of a32037d the repo test passes, because 05 and its I2 log line exist; so I2's `repo*` artifact is absent below except where a real item is affected).
   - M-a (`who` back, `who != "person"`): 10 failed, 524 passed. R1, R2, R3, R4, R5, R6, R7, R13, N-b, N-d. (R12 passes, as 04 says.)
   - M-b (`PERSON_DATED.search(m.group(2))`): 7 failed, 527 passed. R3, R4, `_build_waived` cases 7, 8, 9, N-c, N-d.
   - M-c (`re.match(PERSON_DATED.pattern, m.group(2), re.I)`): 1 failed, 533 passed. R5.
   - M-d (`not (dated or s == "06")`): 10 failed, 524 passed. R1, R2, R3, R4, R5, R6, R12, R13, `test_fact_check_and_verification_waivable_only_by_person`, `test_research_only_branch_waiver_needs_the_person`.
   - M-e (`not (dated or s == "03")`): 12 failed, 522 passed. R1, R2, R3, R4, R7, R12, R13, `test_fact_check_and_verification_waivable_only_by_person`, N-a, N-b, N-c, N-d.
   - M-f (`PERSON_DATED.match(m.group(0))`): 16 failed, 518 passed. R8, R9, R10, `test_waived_steps_are_excused_and_printed`, `test_repo_pipeline_has_no_skipped_items` (real 024), `_build_waived` cases 1, 2, `test_research_code_rules`, `test_research_only_branch_waiver_needs_the_person`, `test_branch_unchanged_tip_py_not_counted`, `test_batch_no_line_before_i2_strict_from_090[990-INCOMPLETE: none]`, `test_batch_person_waiver_before_i2_excused[FULL]`, `[FAST]`, `test_excused_reason_not_strict`, `test_person_waiver_helper_on_item_024`, N-f.
   - M-g (`blocked = list(waived) if not dated else []`): 3 failed, 531 passed. R11, `test_waived_steps_are_excused_and_printed`, `test_repo_pipeline_has_no_skipped_items` (real 023).
   - M-h (`any(PERSON_DATED.match(x.group(2)) for x in WAIVED_LINE.finditer(text))`): 2 failed, 532 passed. R13, N-j.
   - Result: all 8 killed by at least one row of `test_person_only_waiver_needs_dated_form`; M-f also by `test_waived_steps_are_excused_and_printed` and `test_person_waiver_helper_on_item_024`, M-g also by `test_waived_steps_are_excused_and_printed` (04's requirement). Same failing-test sets as 05 once 05's `repo*` artifact is removed (my M-a 10 = 05's 11 - repo*; M-b 7 = 8 - 1; M-c 1 = 2 - 1; M-d 10 = 11 - 1; M-e 12 = 13 - 1; M-f 16 = 16, where repo fails for a real reason in both; M-g 3 = 3; M-h 2 = 3 - 1).
6. RI-002 probe: this change removes no default value, so there is no `else 0` to put back. The nearest equivalent, putting back the removed `who`-only acceptance (M-a), fails 10 tests (above).
7. check_handoff, main checkout (reads work/105 only):
```
sources count (unique URLs in 01-research.md): 1
fact-check rows: 33
totals line: 33 rows -> 28 as-is, 5 fixed, 0 removed
PASS
```
exit 0.
8. Real-repo checker diff (04 Tests 5), full clone. In `head/` (a32037d, clean), `python3 scripts/check_pipeline.py` (head script) and `python3 <scratch copy of base/scripts/check_pipeline.py>` (base script, 1662121) on the same cwd:
```
head exit 0
base exit 0
 132 .../tools/out_base.txt
 132 .../tools/out_head.txt
diff exit 0
```
Identical, including `023: complete (RESEARCH ONLY; Waived: 02 (A1, ...`, `024: complete (FULL; Waived: 01 02 03 04 (person, 2026-10-31: ...`, `105: in progress (FULL: next 06)`, `OPEN BRANCHES (not merged into HEAD):`, `RULES BRANCH: none`, `SKIPPED: none`, `INCOMPLETE: none`, `I3 FAIL: none`. 0 of 2 real Waived items change (RI-001 feasibility count: `grep -rn "^Waived:" work/*/request.md` gives exactly 023 L4 and 024 L4; 024 is the 1 real PERSON_ONLY waiver and it is dated).

## Real-data effect (diff_reports output, pasted)
not required (scripts/check_pipeline.py, tests/test_pipeline_check.py)

## Recurring issues checked (step 0)
Recurring issues checked: RI-001, RI-014, RI-002, RI-008, RI-012 (read logs/recurring-issues.md on 2026-11-26; RI-001 ESCALATED and RI-014 OPEN are the only entries not GUARDED)
- RI-001 (ESCALATED): re-ran each feasibility count. Real Waived lines: 2 (023, 024), the PERSON_ONLY one dated (024); accept branch reached by R8-R10 and the real 024 (`test_person_waiver_helper_on_item_024` green, 024 `complete` in both outputs); block branch by R1, R6, R7. The numbers cited in 03/04/05 (2 Waived, 1 dated PERSON_ONLY, 0 undated, 0 of 2 change) match. Open-branch items: from origin/main the only open branch is this one. No new occurrence.
- RI-014 (OPEN): the change reads no git; the clone is full (`false`), so there are no "not checked" lines; the base/head outputs are identical. No new occurrence.
- RI-002: no absent input becomes a pass: R12 (empty group 2) and R13 (first line undated) give SKIPPED; unreadable request.md still UNREADABLE (`test_unreadable_request` green in the full suite).
- RI-008: python3.11 py_compile exit 0; `test_every_py_compiles_on_oldest_python` ran (python3.11 present) and passed; `.match` kept.
- RI-012: in-text negatives R3, R4 present and kill M-b; M-h killed by R13.

## Pipeline line (step 2)
check_pipeline line: `105: awaiting A1 (FULL)` (main checkout, after 06, 07 and the --log line were written; exit 0)

## Sent back / sent to Audit
PASS, round 1. Sent to Audit: 07-audit-task.md. Nothing sent back. Notes for Audit (no code change needed): 05's stated reason for `RULES BRANCH: none` is wrong (the branch was pushed; the real reason is `--no-merged HEAD`); 04's Tests 5 expectation for RULES BRANCH and two kill-list details were wrong, results otherwise as planned.
